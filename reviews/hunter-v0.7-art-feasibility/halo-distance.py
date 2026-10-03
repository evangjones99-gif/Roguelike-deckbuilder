from PIL import Image
from scipy.ndimage import distance_transform_edt
import numpy as np,json,pathlib
p=pathlib.Path('/workspace/Roguelike-deckbuilder/assets/art-sources/v0.7/hunter-sheet-edit-r3.png');a=np.array(Image.open(p))[:,:,3];out=[]
for k,name in enumerate(['idle','anticipation','command','recovery','reaction','collapse']):
 c=a[k//3*512:(k//3+1)*512,k%3*512:(k%3+1)*512];d=distance_transform_edt(c<=128);r={'pose':name,'reference':'nearest alpha>128 pixel Euclidean sourcepx'}
 for n in [2,4,8,16,32]:
  fringe=c[d>n];r[str(n)]={'alphaMax':int(fringe.max()),'countsOver':{str(t):int((fringe>t).sum()) for t in [1,8,32,64]},'pixels':int(fringe.size)}
 out.append(r)
pathlib.Path('/workspace/scratch/art-review-v07/halo-distance.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
