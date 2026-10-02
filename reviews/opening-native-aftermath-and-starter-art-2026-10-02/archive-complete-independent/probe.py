import json
from pathlib import Path
S=Path('/workspace/scratch');R=Path('/workspace/Roguelike-deckbuilder/reviews/opening-native-aftermath-and-starter-art-2026-10-02/archive')
def shape(x):
 if isinstance(x,dict):return {k:('dict:'+','.join(v.keys()) if isinstance(v,dict) else 'list:'+str(len(v))+':'+str(type(v[0]).__name__ if v else '') if isinstance(v,list) else str(v)[:160]) for k,v in x.items()}
 return type(x).__name__
for p in [R/'ROOT-ARCHIVE-GRANT.json',R/'RESULT.json',S/'native128-defeat-aftermath-comparison-actual-r2/RESULT.json',S/'native128-floor-perspective-comparison-actual-r1/RESULT.json']:
 print(json.dumps({'path':str(p),'shape':shape(json.loads(p.read_bytes()))},separators=(',',':')))
