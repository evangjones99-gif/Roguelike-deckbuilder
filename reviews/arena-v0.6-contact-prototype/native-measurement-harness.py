import json,math
from pathlib import Path
out=Path('/workspace/scratch/hound-contact-v06/review');rows=[]
for name in ['ui-prototype.json','terminal-ui-prototype.json']:
 for c in json.loads((out/name).read_text())['results']:
  assert c['savedMatch'] and not c['errors'] and not c['badResponses']
  closest=[]
  for variant in ['arena','prototype']:
   ss=[]
   for f in c['records']:
    if f['canvas']!=variant:continue
    hit=next((i for i in f['impacts'] if i['color']=='#f3d3a4'),None)
    if hit is None:continue
    for a in f['actors']:
     if a['url']!='hound-poses.png' or a['source'][:2]!=[1056,96]:continue
     sx,sy,sw,sh=a['source'];dx,dy,dw,dh=a['destination'];x=dx+(1456-sx)/sw*dw;y=dy+(255-sy)/sh*dh;m=a['transform'];tip=[m['a']*x+m['c']*y+m['e'],m['b']*x+m['d']*y+m['f']]
     ss.append({'canvas':variant,'elapsedAfterSaveMs':f['elapsed'],'gapPx':math.dist(tip,[hit['x'],hit['y']]),'tip':tip,'hit':[hit['x'],hit['y']],'dimensions':f['dimensions']})
   if ss:closest.append(min(ss,key=lambda s:s['gapPx']))
  rows.append({'file':name,'case':c['name'],'viewport':c['viewport'],'closest':closest})
report={'method':'Own actual preserved d622 UI/nativeRAF/saves plus isolated candidate diagnostic canvas. Actual source-image nose432,255 projected to actual gold slash centers; minimum observed attack-cel gap. Epoch starts in a microtask after save, not physical hit clock. Different clocks, PNG readbacks and missed frames prohibit FPS or phase-timing claims. Two terminal retests defer PNG reads until400ms to avoid missing the short attack/impact overlap; first empty contact observation remains preserved. No production candidate integration claim.', 'immutableWebZipSHA256':'c8a3210688dde4d6bcbe8229ffbc6ae8b11407aa5e6b396c4dfe79c9b3e51c86','canonicalSaveCases':len(rows),'rows':rows}
(out/'native-measurements.json').write_text(json.dumps(report,indent=2));print(json.dumps([{'file':x['file'],'case':x['case'],'width':x['viewport']['width'],'gaps':[round(s['gapPx'],3)for s in x['closest']]}for x in rows],indent=2))
