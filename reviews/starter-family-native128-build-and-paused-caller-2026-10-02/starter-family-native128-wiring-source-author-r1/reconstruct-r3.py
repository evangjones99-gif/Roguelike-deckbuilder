"""Lossless helper storage successor; retained original and r2 failures unchanged."""
import os,hashlib
from pathlib import Path
p=Path(__file__).with_name('reconstruct.py');fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME)
with os.fdopen(fd) as f:original=f.read()
changes=[
("s=swap(s,'ready = images.length === 7;','ready = images.length === 13;',ops['coherent-native128.ts'])","s=swap(s,'images.length === 7','images.length === 13',ops['coherent-native128.ts'])\ns=swap(s,'Native seven-image contract','Native thirteen-image contract',ops['coherent-native128.ts'])"),
("'coherent-native128.ts':sourceNew['coherent-native128.ts']","'coherent-native128.ts.gz':gzip.compress(sourceNew['coherent-native128.ts'],mtime=0)"),
("proof.update({'mainStoredSHA256'","proof.update({'helperStoredSHA256':SHA(files['coherent-native128.ts.gz']),'helperStoredBytes':len(files['coherent-native128.ts.gz']),'helperFormat':'gzip mtime0; full decoded source hash/bytes in coherent-native128.ts proof','methodOriginalSHA256':SHA(original.encode()),'methodPatchFullInverse':True,'mainStoredSHA256'"),
("need(gzip.decompress(read(out/'main.ts.gz'))==sourceNew['main.ts'],'Literal full decoded main readback')","need(gzip.decompress(read(out/'coherent-native128.ts.gz'))==sourceNew['coherent-native128.ts'],'Literal full decoded helper readback')\nneed(gzip.decompress(read(out/'main.ts.gz'))==sourceNew['main.ts'],'Literal full decoded main readback')")]
s=original
for a,b in changes:assert s.count(a)==1;s=s.replace(a,b)
inverse=s
for a,b in reversed(changes):assert inverse.count(b)==1;inverse=inverse.replace(b,a)
assert inverse==original
exec(compile(s,str(p)+'+r3-lossless-helper-storage','exec'))
