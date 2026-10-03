import os,json,hashlib,resource
from pathlib import Path
P=Path(__file__).parent;A=Path('/workspace/scratch/git-immutable-pack-cache-hint-opening-root-r1');B=Path('/workspace/scratch/git-immutable-pack-cache-hint-ROOT-author-r3')
def read(p):
 fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME)
 try:
  size=os.fstat(fd).st_size;assert size<65536
  return b''.join(iter(lambda:os.read(fd,65536),b''))
 finally:os.close(fd)
def pin(p):
 b=read(p);return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
source=pin(A/'immutable_pack_hint.py');assert source['sha256']=='e93abffe3e8f9260eaa45b4088f2fbe7f005eb480bead7c0bcc962e506aeeda2'
old=pin(B/'immutable_pack_hint.py');s=read(A/'immutable_pack_hint.py').decode();o=read(B/'immutable_pack_hint.py').decode()
props={n:json.loads(read(A/n))for n in ['PROPOSAL.json','METADATA-INTAKE.json']}
out=dict(source=source,oldSource=old,controlPins=[pin(A/n)for n in props],controls=props,AGENTS=pin(Path('/workspace/Roguelike-deckbuilder/AGENTS.md')),ownRSSBytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,packBodyNeverRead=True)
assert out['ownRSSBytes']<24*1048576
with(P/'SOURCE-INTAKE.json').open('x')as f:json.dump(out,f,indent=2,sort_keys=True);f.write('\n');f.flush();os.fsync(f.fileno())
print('NEW_SOURCE_BEGIN\n'+s+'NEW_SOURCE_END')
print('OLD_PATH_LINES',json.dumps([l for l in o.splitlines()if 'BASE' in l or 'OUTPUT' in l]))
print('CONTROLS',json.dumps(props))
print('PINS',json.dumps(dict(source=source,oldSource=old,ownRSSBytes=out['ownRSSBytes'])))
