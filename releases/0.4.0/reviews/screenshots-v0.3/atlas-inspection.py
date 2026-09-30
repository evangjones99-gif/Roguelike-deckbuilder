"""Read-only atlas boundary/alpha inspection; does not alter artwork."""
import sys, json, hashlib
from pathlib import Path
from PIL import Image
source=Path(sys.argv[1] if len(sys.argv)>1 else 'public/art/hound-poses.png')
image=Image.open(source).convert('RGBA')
width,height=image.size
alpha=image.getchannel('A')
columns,rows=3,2
vertical=[]
for c in range(1,columns):
 x=round(width*c/columns)
 vertical.append({'x':x,'alphaMaxAtDivider':max(alpha.getpixel((x,y)) for y in range(height)), 'alphaMaxInNinePixelGutter':max(alpha.getpixel((xx,y)) for xx in range(max(0,x-4),min(width,x+5)) for y in range(height))})
horizontal=[]
for r in range(1,rows):
 y=round(height*r/rows)
 horizontal.append({'y':y,'alphaMaxAtDivider':max(alpha.getpixel((x,y)) for x in range(width)), 'alphaMaxInNinePixelGutter':max(alpha.getpixel((x,yy)) for yy in range(max(0,y-4),min(height,y+5)) for x in range(width))})
cells=[]
for r in range(rows):
 for c in range(columns):
  left,top,right,bottom=round(width*c/columns),round(height*r/rows),round(width*(c+1)/columns),round(height*(r+1)/rows)
  cell=alpha.crop((left,top,right,bottom))
  bbox=cell.point(lambda a:255 if a>=16 else 0).getbbox()
  cells.append({'column':c,'row':r,'cellWidth':right-left,'cellHeight':bottom-top,'significantAlphaBBox':bbox,'normalizedBBox':[bbox[0]/(right-left),bbox[1]/(bottom-top),bbox[2]/(right-left),bbox[3]/(bottom-top)] if bbox else None})
result={'source':str(source),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'size':[width,height],'originalMode':Image.open(source).mode,'verticalDividers':vertical,'horizontalDividers':horizontal,'cells':cells,'allDividerAlphaZero':all(d['alphaMaxAtDivider']==0 for d in vertical+horizontal),'scope':'Numerical clipping/spacing check only; anatomy and pose consistency require visual inspection.'}
output=Path('reviews/screenshots-v0.3/atlas-inspection.json')
output.write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
