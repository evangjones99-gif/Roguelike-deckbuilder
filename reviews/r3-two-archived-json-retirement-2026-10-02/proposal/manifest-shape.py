import os,tarfile,json,resource
resource.setrlimit(resource.RLIMIT_DATA,(24*1048576,24*1048576))
p='/workspace/Roguelike-deckbuilder/reviews/opening-target-clear-ghost-opt-in-2026-10-02/evidence-0f6cec73b283cffd830f57d60a37edde43d1670e814d18a33eeb54d05afc37fa.tar.gz'
fd=os.open(p,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW)
with os.fdopen(fd,'rb') as f:
 before=os.fstat(f.fileno())
 with tarfile.open(fileobj=f,mode='r|gz') as t:
  for m in t:
   if m.name=='MANIFEST.json':
    j=json.loads(t.extractfile(m).read(1048576));print('top',[(k,type(v).__name__) for k,v in j.items()])
    for k,v in j.items():
     if isinstance(v,(dict,list)):print(k,str(v)[:1800])
    break
 assert before==os.fstat(f.fileno())
