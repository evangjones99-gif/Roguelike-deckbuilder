import os,json,re,resource
from pathlib import Path
resource.setrlimit(resource.RLIMIT_DATA,(24*1048576,24*1048576));p=Path(__file__).parent;root=Path('/workspace/scratch/native128-empty-intent-stage-r1')
def read(f):
 fd=os.open(f,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME)
 with os.fdopen(fd)as h:return h.read()
s=read(root/'src/coherent-native128.ts');start=s.index('export function createCoherentNative128');end=s.index('export type CoherentNative128',start);(p/'LOADER-R1.txt').write_text(s[start:end])
s=read(root/'src/art.ts');start=s.index('/** Unselected static native128');(p/'ART-NATIVE-R1.txt').write_text(s[start:])
print(json.dumps({'loaderBytes':end-start,'nativeManifest':re.findall(r'"manifest":\s*"([^"]+)"',s),'dataSourceFiles':[f.name for f in (root/'src').iterdir()if f.name in ['data.ts','cards.ts','content.ts','engine.ts','game.ts']]}))
for f in (root/'src').glob('*.ts'):
 if f.name in ['main.ts','arena.ts','coherent-native128.ts']:continue
 s=read(f)
 if any(v in s for v in ['Ash Widow','Fen Stalker','Briar Colossus']):
  lines=[l.strip()for l in s.splitlines()if any(v in l for v in ['Ash Widow','Fen Stalker','Briar Colossus'])]
  print(json.dumps({'file':f.name,'starterRows':lines[:8]}))
print(json.dumps({'freezeCandidateDirs':[str(d)for d in Path('/workspace/scratch').iterdir()if d.is_dir()and d.name.startswith('native128-empty-intent') and any(x in d.name for x in ['build','freeze'])]}))
