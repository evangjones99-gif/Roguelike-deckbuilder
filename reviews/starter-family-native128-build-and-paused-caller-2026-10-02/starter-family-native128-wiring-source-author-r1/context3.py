import os,json,resource
from pathlib import Path
resource.setrlimit(resource.RLIMIT_DATA,(24*1048576,24*1048576))
def r(p):
 f=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME)
 with os.fdopen(f,'r') as s:return s.read()
b=Path('/workspace/scratch/native128-empty-intent-stage-r1')
s=r(b/'src/coherent-native128.ts');print(json.dumps({'keyFor':s[s.index('const keyFor'):s.index('export function createCoherentNative128')]}))
s=r(b/'src/content.ts');print(json.dumps({'cards':s[s.index('fenstalker:'):s.index('fenstalker:')+160] if 'fenstalker:' in s else s[1000:3500]}))
s=r(b/'src/main.ts');a=s.index('const nativeArt =');print(json.dumps({'nativeArt':s[a:a+480]}))
f=json.loads(r('/workspace/scratch/native128-empty-intent-strict-build-root-r1/final-seal-r1/RUNTIME-FREEZE.json'));print(json.dumps({'freezeKeys':list(f),'inputKeys':list(f.get('inputs',{}))[:3]}))
for n in ['ash-widow-correction-native128-final-output-root-r2','starter-family-native128-final-output-root-r3']:
 x=json.loads(r('/workspace/scratch/'+n+'/VIEW-MANIFEST.json'));print(json.dumps({'root':n,'viewKeys':list(x),'sprites':x.get('sprites')}))
print(json.dumps({'rssKiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}))
