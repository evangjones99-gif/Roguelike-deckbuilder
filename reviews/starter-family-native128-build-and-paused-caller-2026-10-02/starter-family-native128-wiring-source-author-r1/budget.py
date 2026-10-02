import os
from pathlib import Path
p=Path(__file__).with_name('reconstruct.py');fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME)
with os.fdopen(fd) as f:s=f.read()
s=s.replace("'ready = images.length === 7;','ready = images.length === 13;'","'images.length === 7','images.length === 13'")
a="need(current+sum(map(len,files.values()))+6000<=128*1024,'Upfront entire family128KiB including6000B final/guard reserve')"
b="print(json.dumps({'currentBytes':current,'plannedBodyBytes':sum(map(len,files.values())),'plainHelper':len(files['coherent-native128.ts']),'plainArt':len(files['art.ts']),'helperGzip':len(gzip.compress(files['coherent-native128.ts'],mtime=0)),'artGzip':len(gzip.compress(files['art.ts'],mtime=0)),'plannedPlusFinalReserve':current+sum(map(len,files.values()))+6000,'cap':128*1024}));sys.exit(0)"
assert s.count(a)==1;s=s.replace(a,b);exec(compile(s,str(p)+'+budget-only','exec'))
