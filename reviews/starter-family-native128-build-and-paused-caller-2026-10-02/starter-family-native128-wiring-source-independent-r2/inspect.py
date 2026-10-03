import os,gzip,json,difflib,hashlib,resource
from pathlib import Path
P=Path(__file__).parent;A=Path('/workspace/scratch/starter-family-native128-wiring-source-author-r2')
def read(p):
 fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME)
 with os.fdopen(fd,'rb') as f:return f.read()
plan=json.loads(read(A/'PLAN.json'));proof=json.loads(read(Path(plan['full104MapPath']).parent/'PROOF.json'));f=json.loads(read(plan['baseFreeze']['path']));base=Path('/workspace/scratch/native128-empty-intent-stage-r1')
for name in ['coherent-native128.ts','main.ts','art.ts']:
 x=plan['candidateSources'][name];b=read(x['path']);d=gzip.decompress(b) if x['format']=='gzip-mtime0' else b
 assert len(d)==x['decodedBytes'] and hashlib.sha256(d).hexdigest()==x['decodedSHA256']
 print('\n'+name+' SOURCE DIFF\n'+''.join(difflib.unified_diff(read(base/'src'/name).decode().splitlines(True),d.decode().splitlines(True))))
 if name=='coherent-native128.ts':print('\nFULL HELPER\n'+d.decode())
 if name=='main.ts':
  lines=d.decode().splitlines();i=next(i for i,x in enumerate(lines) if 'const nativePortrait' in x);print('\nMAIN CARD CONTEXT\n'+'\n'.join(lines[i-25:i+32]))
print(json.dumps({'ownRSS':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'manifest':json.loads(read(plan['candidateSources']['coherent-native128-manual-crop-view-manifest.json']['path']))},separators=(',',':')))
