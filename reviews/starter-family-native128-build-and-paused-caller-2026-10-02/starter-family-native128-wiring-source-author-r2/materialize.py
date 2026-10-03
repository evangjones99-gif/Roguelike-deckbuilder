"""ROOT-only future source materialization, not assembly/build; exact external R1 pins."""
import os,sys,json,gzip,hashlib
from pathlib import Path
p=Path(__file__).resolve().parent
def r(q):
 fd=os.open(q,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME)
 with os.fdopen(fd,'rb') as f:return f.read()
plan=json.loads(r(p/'PLAN.json'));out=Path(sys.argv[1]);assert not out.exists()
bodies={}
for name,x in plan['candidateSources'].items():
 b=r(x['path']);assert len(b)==x['storedBytes'] and hashlib.sha256(b).hexdigest()==x['storedSHA256']
 d=gzip.decompress(b) if x['format']=='gzip-mtime0' else b
 assert len(d)==x['decodedBytes']<=128*1024 and hashlib.sha256(d).hexdigest()==x['decodedSHA256'];bodies[name]=d
out.mkdir(mode=0o700)
for n,b in bodies.items():
 with (out/n).open('xb') as f:f.write(b);f.flush();os.fsync(f.fileno())
 assert r(out/n)==b
print(json.dumps({'materializedExactSources':len(bodies),'actualBuild':False}))
