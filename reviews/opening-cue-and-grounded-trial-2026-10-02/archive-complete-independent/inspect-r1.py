import os,json,resource
from pathlib import Path
P=Path(__file__).parent;O=Path('/workspace/scratch/wording-grounded-trials-checkpoint-output-root-r1');A=Path('/workspace/scratch/wording-grounded-trials-checkpoint-source-author-r1')
def read(p):
 fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME)
 try:return b''.join(iter(lambda:os.read(fd,65536),b''))
 finally:os.close(fd)
j=json.loads(read(A/'PLAN.json'))
print('FILES',[(x.name,x.stat().st_size)for x in O.iterdir()if x.is_file()])
for n in ['RESULT.json','README.md']:
 p=O/n
 if p.exists():print(n,read(p).decode()[:4500])
v=json.loads(read(O/'READ-OBSERVATIONS.json'));print('OBS',type(v).__name__,len(v),str(v[:2]if isinstance(v,list)else list(v))[:2600])
i=json.loads(read(O/'INDEX.json'));print('INDEXKEYS',list(i));print('NEWARCHIVE',i.get('newArchive'))
for x in j['runtimeAuthorities']:
 f=json.loads(read(Path(x['freezePath'])));print('FREEZE',list(f),{k:(len(z) if isinstance(z,(dict,list))else str(z)[:100])for k,z in f.items()});print('FREEZE_SAMPLE',str(f.get('inputs',f.get('sources')))[:450])
g=Path('/workspace/scratch/wording-grounded-trials-checkpoint-archive-guard-root-r1');print('ACTUALGUARD',read(g/'RESULT.json').decode()[:4500]);print('TERMINAL_TAIL',read(g/'EXECUTION.log').decode()[-2000:]);print('RSS',resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024)
