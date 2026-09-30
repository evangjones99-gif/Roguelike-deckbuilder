import json, math
from pathlib import Path
root=Path('reviews/arena-v0.6-contact-prototype'); out=Path('reviews/technical-v0.6-final-evidence')
problems=[]; count=0; bounded=0; metrics=[]
def project(a,x,y,mkey='transform'):
 sx,sy,sw,sh=a['source']; dx,dy,dw,dh=a['destination']; m=a[mkey]; xx=dx+(x-sx)/sw*dw; yy=dy+(y-sy)/sh*dh
 return m['a']*xx+m['c']*yy+m['e'],m['b']*xx+m['d']*yy+m['f']
def bounds(a,mkey='transform'):
 dx,dy,w,h=a['destination'];m=a[mkey]; p=[(m['a']*x+m['c']*y+m['e'],m['b']*x+m['d']*y+m['f']) for x,y in [(dx,dy),(dx+w,dy),(dx,dy+h),(dx+w,dy+h)]]
 return [min(x for x,y in p),min(y for x,y in p),max(x for x,y in p),max(y for x,y in p)]
def sortedjson(xs): return sorted(json.dumps(x,sort_keys=True) for x in xs)
for path in ['comparison.json','narrow-comparison.json','formation-comparison.json']:
 d=json.loads((root/path).read_text()); assert not d['errors']
 for case in d['results']:
  count+=1; distances={'baseline':[],'candidate':[]}
  if not case['inputsUnchanged'] or case['busy'][0]!=case['busy'][1]: problems.append([case['name'],'canonical/busy'])
  for sample in case['samples']:
   bf=sample['frames']['baseline']; cf=sample['frames']['candidate']
   def crop(a): return {k:a[k] for k in ['url','source','destination','alpha']}|{'facing':a['transform']['a'],'breath':a['transform']['d']}
   if sortedjson(map(crop,bf['actors']))!=sortedjson(map(crop,cf['actors'])):problems.append([case['name'],sample['elapsed'],'crop/mirror/alpha'])
   if sortedjson(a for a in bf['actors'] if a['url']!='hound-poses.png')!=sortedjson(a for a in cf['actors'] if a['url']!='hound-poses.png'):problems.append([case['name'],sample['elapsed'],'other actor'])
   for frame in [bf,cf]:
    assert all(math.isfinite(v) for a in frame['actors'] for v in a['transform'].values())
   static=lambda a:a['kind']=='magic' or a['color']=='#f3d3a4'
   if sortedjson(filter(static,bf['impacts']))!=sortedjson(filter(static,cf['impacts'])):problems.append([case['name'],sample['elapsed'],'enemy slash/magic'])
   if sum(i['color']=='#c7d0d6' for i in bf['impacts'])!=sum(i['color']=='#c7d0d6' for i in cf['impacts']):problems.append([case['name'],sample['elapsed'],'counter count'])
   for key,frame in [('baseline',bf),('candidate',cf)]:
    for a in frame['actors']:
     if a['url']!='hound-poses.png' or a['source'][:2]!=[1056,96]:continue
     tip=project(a,1456,255);hit=next((i for i in frame['impacts'] if i['color']=='#f3d3a4'),None)
     if hit:distances[key].append(math.hypot(tip[0]-hit['x'],tip[1]-hit['y']))
     if key=='candidate' and 240<=sample['elapsed']<=260:
      bounded+=1;b=bounds(a)
      if b[0]<-.001 or b[1]<-.001 or b[2]>case['dimensions']['width']+.001 or b[3]>case['dimensions']['height']+.001:problems.append([case['name'],sample['elapsed'],'peak quad'])
  if any(distances.values()):metrics.append({'name':case['name'],'dimensions':case['dimensions'],'closest':{k:min(v) if v else None for k,v in distances.items()}})
report={'scope':'Independent reanalysis of author-executed controlled comparisons, not reviewer rerun or human play','cases':count,'peakAttackQuadsChecked':bounded,'problems':problems,'contact':metrics}
(out/'author-comparison-reanalysis.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='contact'}));assert not problems
if (out/'production-contact.json').exists():
 data=json.loads((out/'production-contact.json').read_text());rows=[]
 for case in data['results']:
  hits=[];counter=0;magic=0;attack=0
  for frame in case['frames']:
   counter+=sum(i['color']=='#c7d0d6' for i in frame['impacts']);magic=max(magic,sum(i['kind']=='magic' for i in frame['impacts']))
   for a in frame['actors']:
    if a['url']!='hound-poses.png' or a['source'][:2]!=[1056,96]:continue
    attack+=1;tip=project(a,1456,255,'matrix');hit=next((i for i in frame['impacts'] if i['color']=='#f3d3a4'),None)
    if hit:hits.append({'gap':math.hypot(tip[0]-hit['x'],tip[1]-hit['y']),'elapsed':frame['elapsed'],'tip':tip,'slash':hit,'quad':bounds(a,'matrix'),'canvas':[frame['width'],frame['height']]})
  rows.append({'name':case['name'],'viewport':case['viewport'],'version':case['version'],'canonicalSaveExact':case['canonicalSaveExact'],'attackDrawSamples':attack,'closest':min(hits,key=lambda r:r['gap']) if hits else None,'counterDraws':counter,'maximumMagicRingsPerFrame':magic})
 (out/'production-measurements.json').write_text(json.dumps({'scope':'Actual browser-native RAF elapsed approximate includes UI-click delay; closest sampled anatomical landmark gap, no exact impact-frame or hardware/FPS claim','cases':rows},indent=2)+'\n');print(json.dumps(rows,indent=2))
