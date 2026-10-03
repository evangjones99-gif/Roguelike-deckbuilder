import os,json,tarfile,resource
resource.setrlimit(resource.RLIMIT_DATA,(24*1048576,24*1048576))
p='/workspace/Roguelike-deckbuilder/reviews/opening-target-wait-cue-2026-10-02/evidence.tar.gz'
with os.fdopen(os.open(p,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW),'rb') as f:
 with tarfile.open(fileobj=f,mode='r|gz') as t:
  m=next(iter(t));print(m.name,m.size)
  with t.extractfile(m) as b:data=json.load(b)
  for k,v in data.items():print(k,repr(v[:2] if isinstance(v,list) else list(v.items())[:2] if isinstance(v,dict) else v))
