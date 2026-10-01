"""Preserve frozen fixture bytes and link metadata without following dependencies."""
import hashlib,json,os,pathlib,shutil,sys,tarfile
base=pathlib.Path('/workspace/scratch')
dest=pathlib.Path('/workspace/Roguelike-deckbuilder/reviews')
def sha(stream):
 h=hashlib.sha256()
 for c in iter(lambda:stream.read(1024*1024),b''):h.update(c)
 return h.hexdigest()
def capture(name,target,manifest):
 root=base/name; data=json.loads((root/manifest).read_text());rows=data['files']
 out=dest/target;out.mkdir(exist_ok=False)
 paths=set();records=[]
 for row in rows:
  rel=pathlib.PurePosixPath(row['path']);assert not rel.is_absolute() and '..' not in rel.parts
  assert row['path'] not in paths;paths.add(row['path']);f=root/rel
  kind=row.get('type',row.get('kind','file'))
  if kind=='symlink':
   assert f.is_symlink() and os.readlink(f)==row['target']
   linksha=hashlib.sha256(os.readlink(f).encode()).hexdigest()
   if 'sha256TargetText' in row:assert linksha==row['sha256TargetText']
   records.append({'path':row['path'],'kind':'symlink','target':os.readlink(f),'sha256TargetText':linksha})
  else:
   assert kind=='file' and f.is_file() and not f.is_symlink()
   with f.open('rb') as stream:digest=sha(stream)
   assert digest==row['sha256'] and f.stat().st_size==row['bytes']
   records.append({'path':row['path'],'kind':'file','sha256':digest,'bytes':f.stat().st_size})
 if manifest not in paths:
  with (root/manifest).open('rb') as stream:digest=sha(stream)
  records.append({'path':manifest,'kind':'file','sha256':digest,'bytes':(root/manifest).stat().st_size})
 archive=out/'complete-frozen-evidence.tar.gz'
 with tarfile.open(archive,'x:gz',dereference=False) as tar:
  for row in records:
   tar.inodes.clear()
   tar.add(root/row['path'],arcname=row['path'],recursive=False)
 with tarfile.open(archive,'r:gz') as tar:
  members=tar.getmembers();assert len(members)==len(records)
  assert {x.name for x in members}=={x['path'] for x in records}
  for row in records:
   member=tar.getmember(row['path'])
   if row['kind']=='symlink':assert member.issym() and member.linkname==row['target']
   else:
    assert member.isfile() and member.size==row['bytes']
    with tar.extractfile(member) as stream:assert sha(stream)==row['sha256']
 for row in records:
  if row['kind']=='file' and '/' not in row['path'] and (row['path'].endswith('.md') or row['path']==manifest):shutil.copyfile(root/row['path'],out/row['path'])
 with archive.open('rb') as stream:archive_sha=sha(stream)
 receipt={'sourceDirectory':str(root),'archive':archive.name,'bytes':archive.stat().st_size,'sha256':archive_sha,'verifiedRecords':len(records),'regularFiles':sum(r['kind']=='file' for r in records),'linkMetadata':sum(r['kind']=='symlink' for r in records),'scope':'All frozen manifest-listed regular bytes and symlink target metadata round-trip verified; links are never followed and dependency bytes are not claimed copied. Embedded synthetic Git directories are inert archive evidence, never gitlinks. Original frozen files remain untouched.','records':records}
 (out/'PRESERVATION.json').write_text(json.dumps(receipt,indent=2)+'\n')
 print(json.dumps({k:v for k,v in receipt.items() if k!='records'}))
if __name__=='__main__':capture(*sys.argv[1:])
