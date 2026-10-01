"""Capture only explicitly hashed file inputs, including declared media references."""
from pathlib import Path,PurePosixPath
import json,hashlib,tarfile,shutil,sys
source=Path('/workspace/scratch')/sys.argv[1];dest=Path('/workspace/Roguelike-deckbuilder/reviews')/sys.argv[2];manifest=sys.argv[3]
def declared(data):
 r=data.get('files',data)
 return {k:(v['sha256'] if isinstance(v,dict) else v) for k,v in r.items()} if isinstance(r,dict) else {v['path']:v['sha256'] for v in r}
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(1024*1024):h.update(b)
 return h.hexdigest()
files=declared(json.loads((source/manifest).read_text()));files[manifest]=sha(source/manifest)
addon=source/'ADDENDUM-MANIFEST-001.json'
if addon.exists():files.update(declared(json.loads(addon.read_text())));files[addon.name]=sha(addon)
records=[]
for name,expected in sorted(files.items()):
 rel=PurePosixPath(name);assert not rel.is_absolute() and '..' not in rel.parts
 p=source/name;assert p.is_file();assert sha(p)==expected
 records.append({'path':name,'bytes':p.stat().st_size,'sha256':expected,'referenceTarget':str(p.resolve()) if p.is_symlink() else None})
dest.mkdir(exist_ok=False);archive=dest/'curated-evidence.tar.gz'
with tarfile.open(archive,'x:gz') as tar:
 for row in records:
  p=source/row['path'];info=tar.gettarinfo(str(p.resolve()),arcname=row['path']);assert info.isfile();info.name=row['path']
  with p.open('rb') as f:tar.addfile(info,f)
with tarfile.open(archive,'r:gz') as tar:
 assert len(tar.getmembers())==len(records)
 for row in records:
  m=tar.getmember(row['path']);assert m.isfile() and m.size==row['bytes'];h=hashlib.sha256()
  with tar.extractfile(m) as f:
   while b:=f.read(1024*1024):h.update(b)
  assert h.hexdigest()==row['sha256']
for row in records:
 if '/' not in row['path'] and (row['path'].endswith('.md') or row['path']==manifest or 'ADDENDUM' in row['path']):shutil.copyfile(source/row['path'],dest/row['path'])
receipt={'sourceDirectory':str(source),'archive':archive.name,'archiveBytes':archive.stat().st_size,'archiveSHA256':sha(archive),'everyDeclaredByteRoundTripVerified':True,'scope':'Only exact manifest/addendum-declared file bytes. Individually hashed media references captured as regular bytes; reference targets recorded. No directory/dependency links followed; source paths and originals remain unchanged.','files':records}
(dest/'PRESERVATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items() if k!='files'}))
