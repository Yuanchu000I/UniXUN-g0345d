#!/usr/bin/env python3
"""Independent offline source-export and ADT audit. BSD-2-Clause-Patent; see LICENSE."""
from pathlib import Path
import hashlib,importlib.util,json,re,struct,sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
def need(ok,message):
 if not ok:raise ValueError(message)
def parse(blob):
 # Independent iterative parser; the adapter uses a recursive parser.
 at=0;pending=[('',1)];out={}
 while pending:
  parent,remaining=pending.pop()
  if not remaining:continue
  pending.append((parent,remaining-1));need(at+8<=len(blob),'truncated node');n,k=struct.unpack_from('<II',blob,at);at+=8;props={};need(n<1024 and k<1024,'oversized node')
  for _ in range(n):
   need(at+36<=len(blob),'truncated property');key=blob[at:at+32].split(b'\0',1)[0].decode('ascii');size=struct.unpack_from('<I',blob,at+32)[0];at+=36
   need(key not in props and at+size<=len(blob),'invalid property');props[key]=blob[at:at+size];at+=(size+3)&~3
  name=props.get('name',b'').split(b'\0',1)[0].decode('ascii');path=parent+'/'+name if name else parent
  need(path not in out and '/' not in name,'invalid node identity');out[path]=props
  if k:pending.append((path,k))
 need(at==len(blob),'unparsed tail');return out

def audit(before,after):
 a,b=parse(before),parse(after);need(len(before)==len(after) and a.keys()==b.keys(),'structure changed');bus='/device-tree/arm-io'
 need(struct.unpack('<3Q',a[bus]['ranges'])==(0,0,0xa000000),'old window differs');need(struct.unpack('<3Q',b[bus]['ranges'])==(0,0x60000,0x9fa0000),'new window differs')
 expected={bus+'/intc':(0x9bc0000,0x10000,0x9c00000,0x100000),bus+'/ufshc':(0x624000,0x2500),bus+'/gpu':(0xb00000,0x3f000),bus+'/rpm-msg-ram':(0x68000,0x8000),bus+'/tcsr-mutex':(0x740000,0x40000),bus+'/blsp2-i2c6':(0x75ba000,0x1000)}
 need({p for p,v in a.items() if p.startswith(bus+'/') and 'reg' in v}==set(expected),'register inventory differs');changes=0;pairs=0
 for p,props in a.items():
  need(props.keys()==b[p].keys(),'property set changed')
  for key,v in props.items():
   w=b[p][key]
   if p==bus and key=='ranges':
    x,y=struct.unpack('<3Q',v),struct.unpack('<3Q',w);changes+=sum(i!=j for i,j in zip(x,y))
   elif p in expected and key=='reg':
    x=struct.unpack('<'+'Q'*(len(v)//8),v);y=struct.unpack('<'+'Q'*(len(w)//8),w);need(x==expected[p],'old register differs')
    for j in range(0,len(x),2):
     need(y[j]+0x60000==x[j] and y[j+1]==x[j+1],'physical address/length changed');need(0<=y[j] and y[j]+y[j+1]<=0x9fa0000,'register outside window');pairs+=1
    changes+=sum(i!=j for i,j in zip(x,y))
   else:need(v==w,'unrelated property changed')
 need(changes==9 and pairs==7,'wrong field/range count');need(a['/device-tree/cpus/cpu0']['timebase-frequency']==struct.pack('<I',19200000),'timebase differs')
 # Parse-level semantic equality alone would miss padding corruption.
 # Allow only bytes belonging to the nine expected scalar changes.
 changed=sum(x!=y for x,y in zip(before,after));need(changed==10,'unexpected changed byte count')
 return {'u64_fields_changed':changes,'physical_ranges_preserved':pairs,'changed_bytes':changed}

def fixture():
 def node(name,props=(),children=()):
  props=[('name',name.encode()+b'\0')]+list(props);out=struct.pack('<II',len(props),len(children))
  for key,value in props:out+=key.encode().ljust(32,b'\0')+struct.pack('<I',len(value))+value+b'\0'*((-len(value))%4)
  return out+b''.join(children)
 regs=[('intc',(0x9bc0000,0x10000,0x9c00000,0x100000)),('ufshc',(0x624000,0x2500)),('gpu',(0xb00000,0x3f000)),('rpm-msg-ram',(0x68000,0x8000)),('tcsr-mutex',(0x740000,0x40000)),('blsp2-i2c6',(0x75ba000,0x1000))]
 children=[node(n,[('reg',struct.pack('<'+'Q'*len(v),*v))]) for n,v in regs]
 return node('device-tree',[('audit-sentinel',b'public synthetic fixture')],[node('arm-io',[('ranges',struct.pack('<3Q',0,0,0xa000000))],children),node('cpus',children=[node('cpu0',[('timebase-frequency',struct.pack('<I',19200000))])])])

def main():
 if len(sys.argv)==4 and sys.argv[1]=='--adt-pair':print(json.dumps(audit(Path(sys.argv[2]).read_bytes(),Path(sys.argv[3]).read_bytes())));return
 need(len(sys.argv)==1,'usage: check_export.py [--adt-pair BEFORE AFTER]');m=json.loads((ROOT/'manifest.json').read_bytes());names=set(m['files']);actual={p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file()}
 need(actual==names|{'manifest.json'},'file inventory differs');forbidden=re.compile(rb'/(?:home|mnt)/|[A-Za-z]:[\\/]Users[\\/]',re.I)
 for name,entry in m['files'].items():
  p=ROOT/name;need(p.is_file() and not p.is_symlink(),'missing/linked file');data=p.read_bytes();need(len(data)==entry['bytes'] and hashlib.sha256(data).hexdigest()==entry['sha256'],'file identity differs: '+name)
  need(b'\0' not in data and not forbidden.search(data),'binary/private path: '+name);need(p.suffix.lower() not in {'.img','.bin','.fd','.dtb','.macho','.jpg','.png'},'forbidden artifact')
 order=m['patch_order'];need(len(order)==len(set(order))==m['patch_count']==46,'invalid patch count');need([Path(p).name for p in order]==(ROOT/'patches/xnu/series').read_text().splitlines(),'series order differs');need({p for p in names if p.startswith('patches/xnu/') and p.endswith('.patch')}==set(order),'patch inventory differs')
 spec=importlib.util.spec_from_file_location('portable_adapter',ROOT/'adapt_adt_window.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);before=fixture();after=mod.adapt(before);result=audit(before,after)
 for bad in [after.replace(b'public synthetic fixture',b'PUBLIC synthetic fixture'),after[:-1]]:
  try:audit(before,bad)
  except (ValueError,struct.error,KeyError):pass
  else:raise ValueError('negative audit control accepted')
 try:mod.adapt(after)
 except (ValueError,struct.error,KeyError):pass
 else:raise ValueError('adapter accepted already-adapted tree')
 sem=json.loads((ROOT/'adt-window-semantics.json').read_bytes());need(sem['field_change_count']==9 and len(sem['fields'])==9 and len(sem['physical_invariance'])==7,'reported semantics differ')
 need(sem['ranges_before_u64']==[0,0,0xa000000] and sem['ranges_after_u64']==[0,0x60000,0x9fa0000],'reported bus window differs')
 for f in sem['physical_invariance']:need(f['physical_before']==f['physical_after']==f['after_bus_parent_base']+f['after_reg_offset'] and f['length_before']==f['length_after'],'reported invariance fails')
 print(json.dumps({'state':'export-check-passed','files_checked':len(names),'patch_count':46,'synthetic_positive_and_negative_checks':True,**result}))
if __name__=='__main__':main()
