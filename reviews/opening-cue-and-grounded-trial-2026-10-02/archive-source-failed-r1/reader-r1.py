import os,json,hashlib,resource
from pathlib import Path
P=Path(__file__).parent;A=Path('/workspace/scratch/wording-grounded-trials-checkpoint-source-author-r1');R=Path('/workspace/Roguelike-deckbuilder')
def read(p):
 fd=os.open(p,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW)
 try:
  a=os.fstat(fd);b=b''.join(iter(lambda:os.read(fd,65536),b''));assert os.fstat(fd)==a;return b
 finally:os.close(fd)
def pin(p):
 b=read(p);return {'path':str(p),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
print('AGENTS',read(R/'AGENTS.md').decode())
print('FILES',[(x.name,x.stat().st_size)for x in A.iterdir()if x.is_file()])
print('PLAN',read(A/'PLAN.json').decode());print('MANIFEST',read(A/'MANIFEST.json').decode());print('FINAL',read(A/'FINAL-SEAL.json').decode())
rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024;assert rss<24*1024*1024
with (P/'IDENTITIES.json').open('x')as f:json.dump({'agents':pin(R/'AGENTS.md'),'plan':pin(A/'PLAN.json'),'manifest':pin(A/'MANIFEST.json'),'final':pin(A/'FINAL-SEAL.json'),'ownRSSBytes':rss},f,indent=2)
print('OWN_RSS',rss)
