"""Future finite body capsule only. Never publishes, edits, deletes, or imports game code."""
import errno,gzip,hashlib,io,json,os,pathlib,resource,stat,sys,tarfile,time
def digest_path(path):
 h=hashlib.sha256()
 with pathlib.Path(path).open('rb') as f:
  while b:=f.read(65536):h.update(b)
 return h.hexdigest()
def open_original(path):
 flags=os.O_RDONLY|os.O_NOFOLLOW;fallback=False
 try:fd=os.open(path,flags|getattr(os,'O_NOATIME',0))
 except OSError as e:
  if e.errno!=errno.EPERM:raise
  fd=os.open(path,flags);fallback=True
 f=os.fdopen(fd,'rb');assert stat.S_ISREG(os.fstat(fd).st_mode);return f,fallback
class HashedReader:
 def __init__(self,body,check):self.body=body;self.hash=hashlib.sha256();self.bytes=0;self.check=check
 def read(self,n=-1):
  assert 0<=n<=65536;self.check();b=self.body.read(n);self.hash.update(b);self.bytes+=len(b);return b
def run(plan_path,expected_sha,out_path):
 plan_bytes=pathlib.Path(plan_path).read_bytes();assert hashlib.sha256(plan_bytes).hexdigest()==expected_sha;plan=json.loads(plan_bytes);assert plan['status']=='FINAL_SOURCE_PLAN_REQUIRES_ROOT_ARCHIVE_GRANT';started=time.monotonic();out=pathlib.Path(out_path);out.mkdir(exist_ok=False);limit=plan['proposedArchive']['physicalOutputCapBytes'];observations=[]
 def check():
  assert time.monotonic()-started<=60,'Finite archive60s method ceiling exceeded';assert resource.getrusage(resource.RUSAGE_SELF).ru_maxrss<=24576,'Own24MiB source-method limit exceeded';assert sum(p.stat().st_size for p in out.iterdir() if p.is_file())<=limit,'Output cap exceeded; failed originals retained'
 for x in [entry[k] for entry in plan['existingCapsules'] for k in ['archive','index']]:
  body,fallback=open_original(x['path']);h=hashlib.sha256()
  with body:
   before=os.fstat(body.fileno())
   while b:=body.read(65536):h.update(b);check()
   after=os.fstat(body.fileno());assert (before.st_ino,before.st_size,before.st_mtime_ns)==(after.st_ino,after.st_size,after.st_mtime_ns)
  assert h.hexdigest()==x['sha256'];observations.append({'originalPath':x['path'],'scope':'existing canonical capsule/index reference only','noAtimeRequested':True,'permissionFallback':fallback})
 unique={}
 for row in plan['rows']:
  root,rel,h,size,role,storage=row
  if storage=='newBlob':unique.setdefault(h,(pathlib.Path(plan['roots'][root])/rel,size))
 partial=out/'evidence.partial.tar.gz'
 with partial.open('xb') as compressed:
  with gzip.GzipFile(fileobj=compressed,mode='wb',filename='',mtime=0,compresslevel=6) as zipped:
   with tarfile.open(fileobj=zipped,mode='w|',bufsize=65536) as archive:
    for h,(path,size) in sorted(unique.items()):
     check();body,fallback=open_original(path)
     with body:
      before=os.fstat(body.fileno());assert before.st_size==size;reader=HashedReader(body,check);member=tarfile.TarInfo('blobs/'+h);member.size=size;member.mode=0o444;member.mtime=0;archive.addfile(member,reader);after=os.fstat(body.fileno());assert reader.bytes==size and reader.hash.hexdigest()==h;assert (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns)
     observations.append({'originalPath':str(path),'sha256':h,'bytes':size,'noAtimeRequested':True,'permissionFallback':fallback,'checkedInodeSizeMtimeStableAtimeQualified':True,'fullStatXattrPreservationClaimed':False})
  compressed.flush();os.fsync(compressed.fileno())
 seen=set()
 with tarfile.open(partial,mode='r|gz',bufsize=65536) as archive:
  for member in archive:
   check();assert member.isfile() and member.name.startswith('blobs/');h=member.name[6:];assert h in unique and h not in seen and member.size==unique[h][1];body=archive.extractfile(member);actual=hashlib.sha256();n=0
   original,fallback=open_original(unique[h][0])
   with original:
    before=os.fstat(original.fileno())
    while b:=body.read(65536):check();assert original.read(len(b))==b,'Full original byte comparison failed';actual.update(b);n+=len(b)
    assert original.read(1)==b'';after=os.fstat(original.fileno());assert (before.st_ino,before.st_size,before.st_mtime_ns)==(after.st_ino,after.st_size,after.st_mtime_ns)
   assert n==member.size and actual.hexdigest()==h;seen.add(h);observations.append({'originalPath':str(unique[h][0]),'scope':'full decoded original-byte equality readback','noAtimeRequested':True,'permissionFallback':fallback})
 assert seen==set(unique);archive_sha=digest_path(partial);check();archive=out/('evidence-'+archive_sha+'.tar.gz');partial.rename(archive)
 index={'format':'original-path-sha256-blobs-v1','roots':plan['roots'],'rowColumns':plan['rowColumns'],'rows':plan['rows'],'roles':plan['roles'],'newArchive':{'path':str(archive),'sha256':archive_sha,'bytes':archive.stat().st_size},'existingCapsules':plan['existingCapsules'],'externalDependencies':plan['externalDependencies'],'runtimeAuthorities':plan['runtimeAuthorities'],'allOriginalPathsRetained':True,'fullUniqueOriginalByteRoundtrip':True,'selfContainedRelease':False}
 (out/'INDEX.json').write_text(json.dumps(index,separators=(',',':'))+'\n');(out/'READ-OBSERVATIONS.json').write_text(json.dumps(observations,separators=(',',':'))+'\n')
 (out/'README.md').write_text('Original bytes only; logical paths map to blobs/SHA256 in the new archive or exact ce0f/f912 capsules. Game media and installed dependencies remain external and pinned. No game/default/art selection authority. Originals, failed reviews, source drafts, and prior capsules remain in place.\n')
 result={'archiveSHA256':archive_sha,'archiveBytes':archive.stat().st_size,'logicalBodies':len(plan['rows']),'newUniqueBodies':len(unique),'fullUniqueOriginalByteRoundtrip':True,'planSHA256':expected_sha,'indexSHA256':digest_path(out/'INDEX.json'),'readObservationsSHA256':digest_path(out/'READ-OBSERVATIONS.json'),'allOriginalPathsRetained':True,'noPublicationOrSelectionAuthority':True,'ownMaxRSSBytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,'elapsedBeforeFinalReceipt':time.monotonic()-started}
 (out/'RESULT.json').write_text(json.dumps(result,separators=(',',':'))+'\n')
 for p in out.iterdir():
  if p.is_file():
   fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW)
   try:os.fsync(fd)
   finally:os.close(fd)
 check();result['terminalElapsedAfterAllWrites']=time.monotonic()-started;result['terminalLogicalOutputBytesAfterAllWrites']=sum(p.stat().st_size for p in out.iterdir() if p.is_file());result['terminalAllocatedOutputBytesAfterAllWrites']=sum(p.stat().st_blocks*512 for p in out.iterdir() if p.is_file());result['terminalOwnMaxRSSBytesAfterAllWrites']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024;assert result['terminalAllocatedOutputBytesAfterAllWrites']<=limit;print(json.dumps(result,separators=(',',':')))
if __name__=='__main__':
 assert len(sys.argv)==4,'Usage: preserve-checkpoint.py PLAN EXPECTED_PLAN_SHA NEW_OUTPUT_DIRECTORY';run(*sys.argv[1:])
