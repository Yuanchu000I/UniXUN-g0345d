#!/usr/bin/env python3
"""Portable host-only v10 ADT adaptation core. BSD-2-Clause-Patent; see LICENSE."""
from pathlib import Path
import argparse,hashlib,json,struct
BUS='/device-tree/arm-io'
EXPECTED_REGS={BUS+'/intc':(0x9bc0000,0x10000,0x9c00000,0x100000),BUS+'/ufshc':(0x624000,0x2500),BUS+'/gpu':(0xb00000,0x3f000),BUS+'/rpm-msg-ram':(0x68000,0x8000),BUS+'/tcsr-mutex':(0x740000,0x40000),BUS+'/blsp2-i2c6':(0x75ba000,0x1000)}
def require(ok,message):
 if not ok: raise ValueError(message)
def parse_adt(blob: bytes) -> tuple[dict, dict]:
    nodes, meta = {}, {}

    def node(at: int, parent: str, depth: int) -> int:
        require(depth < 32 and at + 8 <= len(blob), "invalid ADT node")
        properties, children = struct.unpack_from("<II", blob, at)
        require(properties < 1024 and children < 1024, "invalid ADT node counts")
        at += 8
        values, offsets = {}, {}
        for _ in range(properties):
            require(at + 36 <= len(blob), "truncated ADT property")
            key = blob[at:at + 32].split(b"\0", 1)[0].decode("ascii")
            length = struct.unpack_from("<I", blob, at + 32)[0]
            at += 36
            require(key not in values and length < len(blob) and at + length <= len(blob),
                    "invalid ADT property")
            values[key], offsets[key] = blob[at:at + length], at
            at += (length + 3) & ~3
        name = values.get("name", b"").split(b"\0", 1)[0].decode("ascii")
        require("/" not in name, "invalid ADT node name")
        path = parent + "/" + name if name else parent
        require(path not in nodes, "duplicate ADT node")
        nodes[path], meta[path] = values, offsets
        for _ in range(children):
            at = node(at, path, depth + 1)
        return at

    require(node(0, "", 0) == len(blob), "unparsed ADT tail")
    return nodes, meta

def adapt(before):
 nodes,offsets=parse_adt(before)
 require(struct.unpack('<3Q',nodes[BUS]['ranges'])==(0,0,0xa000000),'unexpected old bus window')
 regs={p:struct.unpack('<'+'Q'*(len(v['reg'])//8),v['reg']) for p,v in nodes.items() if p.startswith(BUS+'/') and 'reg' in v}
 require(regs==EXPECTED_REGS,'unexpected register inventory')
 require(nodes['/device-tree/cpus/cpu0']['timebase-frequency']==struct.pack('<I',19200000),'unexpected CPU timebase')
 after=bytearray(before);count=2
 def put(path,prop,index,value):struct.pack_into('<Q',after,offsets[path][prop]+index*8,value)
 put(BUS,'ranges',1,0x60000);put(BUS,'ranges',2,0x9fa0000)
 for path,values in EXPECTED_REGS.items():
  for index in range(0,len(values),2):
   physical,length=values[index:index+2];relative=physical-0x60000
   require(0<=relative and relative+length<=0x9fa0000,'register outside bus window');put(path,'reg',index,relative);count+=1
 require(count==9,'wrong field count');return bytes(after)
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('input',type=Path);ap.add_argument('output',type=Path);args=ap.parse_args();after=adapt(args.input.read_bytes())
 with args.output.open('xb') as f:f.write(after)
 require(args.output.read_bytes()==after,'output readback differs');print(json.dumps({'state':'adapted','bytes':len(after),'u64_field_changes':9,'sha256':hashlib.sha256(after).hexdigest()}))
if __name__=='__main__':main()
