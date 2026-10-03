import os,json,hashlib,resource
from pathlib import Path
P=Path(__file__).parent;A=Path('/workspace/scratch/wording-grounded-trials-checkpoint-source-author-r1');R=Path('/workspace/Roguelike-deckbuilder');OLD=Path('/workspace/scratch/wording-grounded-trials-checkpoint-source-independent-r1')
def read(p):
 fd=os.open(p,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW)
 try:
  a=os.fstat(fd);b=b''.join(iter(lambda:os.read(fd,65536),b''));assert a==os.fstat(fd);return b
 finally:os.close(fd)
def pin(p):
 b=read(p);return {'path':str(p),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
a=read(R/'AGENTS.md');print('AGENTS_REMAINING',a.decode()[14000:])
v=json.loads(read(A/'PLAN.json'));print('PLAN_KEYS',list(v))
for k,x in v.items():
 print('PLAN_FIELD',k,('DICT '+str(list(x)) if isinstance(x,dict) else 'LIST '+str(len(x)) if isinstance(x,list) else str(x)[:600]))
print('FILES',[(x.name,x.stat().st_size)for x in A.iterdir()if x.is_file()]);print('MANIFEST',read(A/'MANIFEST.json').decode()[:7000])
old=[dict(pin(x),relativePath=str(x.relative_to(OLD))) for x in sorted(OLD.rglob('*')) if x.is_file()]
z={'failedR1NeededPreserved':old,'failedR1Bytes':sum(x['bytes']for x in old),'acceptedR2CapBytes':131072,'failedR1ExcludedFromR2Cap':True,'sourcePlan':pin(A/'PLAN.json'),'sourceManifest':pin(A/'MANIFEST.json'),'sourceFinal':pin(A/'FINAL-SEAL.json'),'agents':pin(R/'AGENTS.md'),'ownRSSBytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024}
assert z['sourcePlan']['sha256']=='0998d948c57e2fb3d1e01f34e61028d5c80db299df308d3b1e83ab902d4281b7' and z['sourceManifest']['sha256']=='aac303e5619efd453671e821f57f111f66e6a95e40e20aec638c27e5b00e47a1' and z['sourceFinal']['sha256']=='390bee76cdfe116f97b0c8df582c6b92b717f853dda01aea34d7ddf87cc99566'
assert z['ownRSSBytes']<24*1024*1024
with(P/'IDENTITIES.json').open('x')as f:json.dump(z,f,indent=2,sort_keys=True);f.write('\n')
print('OWN_RSS',z['ownRSSBytes'])
