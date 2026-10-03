"""Unexecuted restoration source. Requires a separately authorized fresh output."""
import os,sys,json,hashlib,tarfile,pathlib,resource
resource.setrlimit(resource.RLIMIT_DATA,(24*1048576,24*1048576))
CAP='/workspace/Roguelike-deckbuilder/reviews/opening-ready-and-rapid-drop-2026-10-01/evidence.tar.gz'
ASHA='27c7d4e2a117c5fa2625146a5ca78e7965705f8f809e44b6c2d7b9efb52817af';MSHA='005225286c6784598181a46bd0ad25cc99d4ee54b3c2394d58d5ea915b41155b'
RAW='/workspace/scratch/settle-drag-comparison-actual-r1/'
EXPECTED={'VISUAL-RESULT.json':('b7713194f75462873cf59193251203f0cfebfd65c0f32b6732c2a1bac4354d74',3013464),'VISUAL-PROGRESS.json':('76c5d89a05d73e0fb9e0c17559c900be4515668fbfd3ec9e919e9bc2adda34b2',3013437)}
assert len(sys.argv)==3,'Specify raw basename and an explicitly fresh absolute scratch destination.'
name,dest=sys.argv[1:];assert name in EXPECTED
path=pathlib.Path(dest);assert path.is_absolute() and '..' not in path.parts and str(path).startswith('/workspace/scratch/') and not str(path).startswith(RAW)
parent=os.open('/',os.O_PATH|os.O_DIRECTORY|os.O_NOFOLLOW)
try:
 for part in path.parent.parts[1:]:
  nxt=os.open(part,os.O_PATH|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=parent);os.close(parent);parent=nxt
 fd=os.open(CAP,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME)
 try:
  before=os.fstat(fd);h=hashlib.sha256()
  while True:
   b=os.read(fd,65536)
   if not b:break
   h.update(b)
  assert h.hexdigest()==ASHA and before==os.fstat(fd);os.lseek(fd,0,os.SEEK_SET);entry=None;done=False
  with os.fdopen(os.dup(fd),'rb') as stream:
   with tarfile.open(fileobj=stream,mode='r|gz') as archive:
    for member in archive:
     if member.name=='MANIFEST.json':
      assert member.isfile() and member.size<2*1048576
      with archive.extractfile(member) as f:body=f.read(2*1048576)
      assert len(body)==member.size and hashlib.sha256(body).hexdigest()==MSHA
      entries=[e for e in json.loads(body)['entries'] if e.get('originalPath')==RAW+name];assert len(entries)==1;entry=entries[0]
      assert (entry['sha256'],entry['bytes'])==EXPECTED[name]
     elif entry and member.name=='blobs/'+entry['sha256']:
      assert member.isfile() and member.size==entry['bytes'];out=os.open(path.name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=parent)
      try:
       h=hashlib.sha256();count=0
       with archive.extractfile(member) as f:
        while True:
         b=f.read(65536)
         if not b:break
         h.update(b);count+=len(b);v=memoryview(b)
         while v:v=v[os.write(out,v):]
       assert h.hexdigest()==entry['sha256'] and count==entry['bytes'];os.fsync(out);done=True
      finally:os.close(out)
      break
  assert done and before==os.fstat(fd)
  print(json.dumps({'freshPath':dest,'sha256':entry['sha256'],'bytes':entry['bytes'],'logicalPath':entry['path'],'capsuleSHA256':ASHA,'metadata':'Fresh inode/time/current-user ownership; original metadata not restored.'}))
 finally:os.close(fd)
finally:os.close(parent)
