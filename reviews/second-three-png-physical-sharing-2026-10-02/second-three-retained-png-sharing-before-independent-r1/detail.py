import pathlib,os,json,resource,sys,hashlib
p=pathlib.Path('/workspace/scratch/media-loose-png-recovery-proposal-author-r2')
def read(path):
 fd=os.open(path,os.O_RDONLY|os.O_NOATIME)
 with os.fdopen(fd,'rb') as f:return f.read()
v=json.loads(read(p/'PROPOSAL.json'))
if sys.argv[1]=='method':
 for n,line in enumerate(read('/workspace/scratch/share-second-three-retained-pngs-root-r1.py').decode().splitlines(),1):print(str(n)+': '+line)
else:
 print('PROPOSAL SHAPE',json.dumps({k:(list(x.keys()) if isinstance(x,dict) else ('list:'+str(len(x)) if isinstance(x,list) else x)) for k,x in v.items()}))
 for k,x in v.items():
  if k not in ('pairs',):print(k,json.dumps(x) if not isinstance(x,list) else json.dumps([{key:val for key,val in r.items() if key not in ['ancestorsNoSymlink','lstat','fstat']} if isinstance(r,dict) else r for r in x]))
 print('HISTORICAL CONSUMER',read(p/'HISTORICAL-CONSUMER.json').decode())
 agents=read('/workspace/Roguelike-deckbuilder/AGENTS.md');print('CURRENT AGENTS SHA',hashlib.sha256(agents).hexdigest())
 for line in agents.decode().splitlines():
  if 'rebuilt-dist' in line:print('CURRENT HOLD',line)
print('OWN_RSS_KIB',resource.getrusage(resource.RUSAGE_SELF).ru_maxrss);assert resource.getrusage(resource.RUSAGE_SELF).ru_maxrss<24*1024
