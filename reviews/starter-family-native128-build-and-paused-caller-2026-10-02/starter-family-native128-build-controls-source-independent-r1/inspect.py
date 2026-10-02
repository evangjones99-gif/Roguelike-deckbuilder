import os,json,gzip,resource
from pathlib import Path
P=Path(__file__).parent;A=Path('/workspace/scratch/starter-family-native128-build-controls-source-author-r1')
def read(p):
 fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME)
 with os.fdopen(fd,'rb') as f:return f.read()
plan=json.loads(read(A/'PLAN.json'))
print(json.dumps({k:('MAP '+str(len(v)) if k in ['expectedInputs','expectedHeldOutputs','expectedAliasKeys'] else v) for k,v in plan.items()},separators=(',',':')))
for n in ['assemble.py','bounded-build.py','finalize.py','strict-build-runner.mjs']:
 print('\nDIFF '+n+'\n'+gzip.decompress(read(A/(n+'.diff.gz'))).decode())
print(json.dumps({'ownMaxRSSKiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}))
