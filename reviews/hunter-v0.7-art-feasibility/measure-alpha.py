from PIL import Image
import numpy as np,json,hashlib,pathlib
root=pathlib.Path('/workspace/Roguelike-deckbuilder');dest=pathlib.Path('/workspace/scratch/art-review-v07')
paths=['hunter-sheet-original-r1.png','hunter-sheet-edit-r2.png','hunter-sheet-edit-r3.png'];names=['idle','anticipation','command','recovery','reaction','collapse']
out={'method':'Read-only Pillow RGBA; inclusive source-cell bbox coordinates; no PNG pixels written. Edge alpha stats include hidden RGB only when alpha>threshold.','attempts':[]}
def stats(a):
 return {'max':int(a.max()),'counts':{str(t):int((a>t).sum()) for t in [0,1,8,64,128,200]},'pixels':int(a.size)}
for p in paths:
 path=root/'assets/art-sources/v0.7'/p;rgba=np.array(Image.open(path));a=rgba[:,:,3];cells=[]
 for k,name in enumerate(names):
  c=a[k//3*512:(k//3+1)*512,k%3*512:(k%3+1)*512];boxes={}
  for t in [1,8,32,64,128,200,250]:
   yy,xx=np.where(c>t);boxes[str(t)]=[int(xx.min()),int(yy.min()),int(xx.max()),int(yy.max())] if len(xx) else None
  edge={}
  for n in [1,8,16,32,48]:
   mask=np.zeros(c.shape,dtype=bool);mask[:n]=True;mask[-n:]=True;mask[:,:n]=True;mask[:,-n:]=True;edge[str(n)]=stats(c[mask])
  bb=boxes['128'];outside=np.ones(c.shape,dtype=bool);outside[bb[1]:bb[3]+1,bb[0]:bb[2]+1]=False
  cells.append({'name':name,'bboxInclusiveByAlpha':boxes,'edgeBands':edge,'outsideOpaqueBBox':stats(c[outside]),'alpha':stats(c)})
 dividers={}
 for n in [1,4,8,16]:
  dividers[str(n)]={'v512':stats(a[:,512-n:512+n]),'v1024':stats(a[:,1024-n:1024+n]),'h512':stats(a[512-n:512+n,:])}
 out['attempts'].append({'file':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'dimensions':[rgba.shape[1],rgba.shape[0]],'mode':'RGBA','cells':cells,'gridBoundaryHalfBands':dividers,'alpha':stats(a)})
(dest/'alpha-measurements.json').write_text(json.dumps(out,indent=2)+'\n')
for r in out['attempts']:
 print(pathlib.Path(r['file']).name, r['sha256'])
 print('boundary4',r['gridBoundaryHalfBands']['4'])
 for c in r['cells']: print(c['name'],c['bboxInclusiveByAlpha']['128'],'edge8',c['edgeBands']['8'],'outside',c['outsideOpaqueBBox'])
