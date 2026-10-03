import os,json,hashlib,resource
from pathlib import Path
resource.setrlimit(resource.RLIMIT_DATA,(24*1048576,24*1048576));p=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def r(q):
 f=os.open(q,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME)
 with os.fdopen(f,'rb') as s:return s.read()
plan=json.loads(r(p/'PLAN.json'));rows=[]
for q in sorted(p.rglob('*')):
 if q.is_file() and 'FINAL-GUARD' not in q.parts:
  b=r(q);rows.append([str(q.relative_to(p)),len(b),sha(b)])
x={'scope':'SOURCE_ONLY_UNSELECTED_FRESH_R2_CLOSURE','planSHA256':sha(r(p/'PLAN.json')),'materializeMethodSHA256':sha(r(p/'materialize.py')),'sourceBodyTupleSHA256':sha(json.dumps(rows,separators=(',',':')).encode()),'sourceBodyCount':len(rows),'r1ExactRetainedLogicalBytes':plan['r1LogicalBytes'],'r1FinalReserveRefusalRetained':True,'predictedSourceDigest':plan['predictedSourceDigest'],'inputs':104,'outputsPredictionOnly':70,'cap128KiBIncludesGuardTails':True,'noActualBuildOrOwnArtApproval':True,'rssKiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'closureRequiresFinalGuardNormalReturn':True}
b=(json.dumps(x,separators=(',',':'))+'\n').encode();assert sum(q.stat().st_size for q in p.rglob('*') if q.is_file())+len(b)+3000<=131072
with (p/'FINAL-SEAL.json').open('xb') as f:f.write(b);f.flush();os.fsync(f.fileno())
assert r(p/'FINAL-SEAL.json')==b;print(json.dumps({'finalSHA256':sha(b),'planSHA256':x['planSHA256'],'methodSHA256':x['materializeMethodSHA256'],'rssKiB':x['rssKiB']}))
