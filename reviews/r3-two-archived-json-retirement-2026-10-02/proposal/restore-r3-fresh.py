import os,sys,tarfile,json,hashlib
from pathlib import Path
assert len(sys.argv)==3
name,dest=sys.argv[1:];assert name in ['VISUAL-RESULT.json','VISUAL-PROGRESS.json']
P=Path(__file__).parent;plan=json.loads((P/'PROPOSAL.json').read_text());mapping=next(x for x in plan['exactLogicalMapping'] if x['originalPath'].endswith('/'+name));dest=Path(dest)
assert dest.is_absolute() and not dest.exists() and str(dest) not in {x['path'] for x in plan['rawFiles']}
def parent(p):
 f=os.open('/',os.O_PATH|os.O_DIRECTORY|os.O_NOFOLLOW)
 try:
  for part in p.parent.parts[1:]:
   assert part not in ['.','..'];q=os.open(part,os.O_PATH|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=f);os.close(f);f=q
  return f
 except BaseException:os.close(f);raise
cp=Path(plan['capsule']['path']);f=os.open(cp,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW);h=hashlib.sha256()
with os.fdopen(f,'rb') as s:
 for b in iter(lambda:s.read(65536),b''):h.update(b)
assert h.hexdigest()==plan['capsule']['sha256']
fd=os.open(cp,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW);count=0;matched=False;manifestChecked=False
with os.fdopen(fd,'rb') as s,tarfile.open(fileobj=s,mode='r|gz') as tar:
 for m in tar:
  if m.name=='MANIFEST.json':
   b=tar.extractfile(m).read();assert hashlib.sha256(b).hexdigest()==plan['manifestSHA256'];j=json.loads(b);assert any(str(Path(j['roots'][r[0]])/r[1])==mapping['originalPath'] and r[2]==mapping['bytes'] and r[3]==mapping['sha256'] for r in j['rows']);manifestChecked=True
  if m.name==mapping['blobMember']:
   assert manifestChecked and not matched;pf=parent(dest);out=os.open(dest.name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=pf);os.close(pf);h=hashlib.sha256()
   with tar.extractfile(m) as b,os.fdopen(out,'wb') as d:
    for chunk in iter(lambda:b.read(65536),b''):d.write(chunk);h.update(chunk);count+=len(chunk)
    d.flush();os.fsync(d.fileno())
   assert count==mapping['bytes'] and h.hexdigest()==mapping['sha256'];matched=True
assert matched # Source only; never executed in proposal. Failure leaves fresh partial body for diagnosis.
