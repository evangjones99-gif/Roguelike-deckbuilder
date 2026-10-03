import os,json,hashlib,resource
from pathlib import Path
resource.setrlimit(resource.RLIMIT_DATA,(24*1048576,24*1048576));p=Path(__file__).parent
root=Path('/workspace/scratch/native128-empty-intent-stage-r1')
def read(f):
 fd=os.open(f,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME)
 with os.fdopen(fd,'rb')as h:return h.read()
for n in ['src/coherent-native128.ts','src/arena.ts','src/main.ts','src/art.ts','src/coherent-native128-assets.json']:
 f=root/n
 if f.exists():
  b=read(f);s=b.decode();r={'path':str(f),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'relevantLines':[l.strip()for l in s.splitlines()if any(x in l for x in ['native128','Native128','coherentNative','cardPortrait','portraitFor','starter','assets.json'])][:45]}
  (p/(f.name+'.inspection.json')).write_text(json.dumps(r,indent=2)+'\n')
  print(json.dumps({'file':n,'bytes':len(b),'sha256':r['sha256']}))
 else:print(json.dumps({'file':n,'absent':True}))
print(json.dumps({'srcJSONNames':[str(f.relative_to(root))for f in (root/'src').glob('*.json')]}))
