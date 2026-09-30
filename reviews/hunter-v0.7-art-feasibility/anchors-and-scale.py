import json,pathlib,numpy as np
from PIL import Image
root=pathlib.Path('/workspace/Roguelike-deckbuilder/assets/art-sources/v0.7');dest=pathlib.Path('/workspace/scratch/art-review-v07')
a=np.array(Image.open(root/'hunter-sheet-edit-r3.png'))[:,:,3]
names=['idle','anticipation','command','recovery','reaction','collapse'];ground=[502,502,500,450,447,441];data=[]
for k,name in enumerate(names):
 c=a[k//3*512:(k//3+1)*512,k%3*512:(k%3+1)*512];y,x=np.where(c>128);top=int(y.min());ys,xs=np.where(c[top:top+20,:]>128);height=int(y.max()-y.min()+1);width=int(x.max()-x.min()+1)
 data.append({'pose':name,'cell':[k%3,k//3],'anchorX':.5,'anchorY':ground[k]/512,'groundBottomEdgeSourcePx':ground[k],'alpha128BBoxInclusive':[int(x.min()),top,int(x.max()),int(y.max())],'standingHeightProxyPx':height,'heightRatioToIdle':round(height/418,6),'headTop20pxOpaqueSpanPx':int(xs.max()-xs.min()+1),'headTop20pxOpaqueSpanX':[int(xs.min()),int(xs.max())],'common448GroundErrorSourcePx':ground[k]-448,'uniform100pxIdleBody':{'cellSizePx':100*512/418,'meaningfulHeightPx':height*100/418,'meaningfulWidthPx':width*100/418,'common448GroundErrorPx':(ground[k]-448)*100/418}})
out={'status':'Unshipped scratch feasible metadata proposal; not runtime or independent gate','sourceCrop':[0,0,512,512],'scaleRule':'One same cell size for all six poses: target idle height *512/418. Never renormalize pose bbox heights individually.','anchorDefinition':'x=.5 fixed sourcecellmidpoint provisional; y=bottomedge of supported boot including alpha>128; seatedpose anchors nearer boot contact, glove support is farther back on perspective floor.','limits':'An opaque-bbox height is pose compression proxy, not actual skeletal scale. Top20px hair span is appearance proxy, confounded by head turn/tilt. These do not establish a rig, exact physical human height, or motion quality.','poses':data}
(dest/'anchors-and-scale.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
