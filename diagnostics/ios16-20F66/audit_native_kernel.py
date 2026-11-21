#!/usr/bin/env python3
"""Private v9/v10 native kernel identity/header audit. BSD-2-Clause-Patent; see LICENSE.
Does not compile, repeat every original instruction audit or establish device execution.
"""
import argparse,hashlib,json,struct
from pathlib import Path
EXPECTED='af1550fdd5e219d54cb49e7a4806dcbfb8ef3778c03b381d4c88647355b94ab2'
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('kernel',type=Path);b=p.parse_args().kernel.read_bytes()
 if len(b)!=17961240 or hashlib.sha256(b).hexdigest()!=EXPECTED:raise ValueError('kernel identity differs')
 magic,cpu,sub,kind,ncmds,sizeofcmds,flags,reserved=struct.unpack_from('<8I',b)
 if (magic,cpu,kind)!=(0xfeedfacf,0x100000c,2) or 32+sizeofcmds>len(b):raise ValueError('not ARM64 MH_EXECUTE')
 at=32
 for _ in range(ncmds):
  cmd,size=struct.unpack_from('<II',b,at)
  if size<8 or at+size>32+sizeofcmds:raise ValueError('malformed load command')
  at+=size
 if at!=32+sizeofcmds:raise ValueError('load command extent differs')
 print(json.dumps({'state':'known-native-kernel-identity-confirmed','sha256':EXPECTED,'bytes':len(b),'format':'ARM64 MH_EXECUTE','device_execution_established':False}))
if __name__=='__main__':main()
