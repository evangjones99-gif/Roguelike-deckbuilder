import hashlib,json,pathlib,os,zipfile,time
P=pathlib.Path('/workspace/scratch/archive8cdf-acquired-r1');O=pathlib.Path('/workspace/scratch/archive8cdf-transfer-actual-review-r1')
S='8cdf546a8429e949fe88611d781aca341566f473135fbcbe44b5373beabd7aa8';N='evidence-'+S+'.tar.gz';Z='20f99bef9f8453ab9a40f18c8d5ea46ced1a86f485af902d377bbc2b0e8f9202';G='f768057141601502417dc8e31ba7e9cf678b616b';B=5085419
current=int(pathlib.Path('/sys/fs/cgroup/memory.current').read_text());maximum=int(pathlib.Path('/sys/fs/cgroup/memory.max').read_text());assert maximum-current>= (64+512)*1048576;assert os.statvfs(O).f_bavail*os.statvfs(O).f_frsize>=64*1048576
names=['TRANSPORT.zip',N,'CI-VERIFICATION.json','ROOT-VERIFICATION.json'];before={n:(P/n).stat() for n in names};assert all((P/n).is_file() and not (P/n).is_symlink() for n in names)
def digest(stream,size):
 h=hashlib.sha256();g=hashlib.sha1(b'blob '+str(size).encode()+b'\0');count=0
 while c:=stream.read(65536):count+=len(c);assert count<=size;h.update(c);g.update(c)
 assert count==size;return {'bytes':count,'sha256':h.hexdigest(),'gitFramedSHA1':g.hexdigest()}
with (P/'TRANSPORT.zip').open('rb') as f:z=digest(f,5086847)
assert z['sha256']==Z
with (P/N).open('rb') as f:a=digest(f,B)
assert a['sha256']==S and a['gitFramedSHA1']==G
with zipfile.ZipFile(P/'TRANSPORT.zip') as f:
 rows=f.infolist();assert len(rows)==2 and {r.filename for r in rows}=={N,'VERIFICATION.json'}
 for r in rows:assert not r.is_dir() and not r.flag_bits&1 and not pathlib.PurePosixPath(r.filename).is_absolute() and '..' not in pathlib.PurePosixPath(r.filename).parts
 assert f.getinfo(N).file_size==B and f.getinfo('VERIFICATION.json').file_size<=4096
 with f.open(N) as body:inside=digest(body,B)
 assert inside==a
 receipt=f.read('VERIFICATION.json');assert receipt==(P/'CI-VERIFICATION.json').read_bytes();ci=json.loads(receipt)
 assert ci['repository']=='evangjones99-gif/Roguelike-deckbuilder' and ci['ref']=='refs/heads/codex/lanternbound-production' and ci['workflowCommit']=='ff5ac095f35a605d86e01edf0183b15f2e9c3874'
 assert ci['runID']=='37045153855' and ci['runAttempt']=='1' and ci['blobSHA1']==G and ci['archiveSHA256']==S and ci['archiveBytes']==B
 assert ci['status']=='EXACT_IMMUTABLE_ARCHIVE_BYTES_VERIFIED_ONLY' and ci['fullStoredArchiveSHA256Readback'] is True and ci['extractedOrExecutedArchive'] is False and ci['historicalFilesystemMetadataRestored'] is False
 assert ci['apiJSONBytes']<=ci['apiResponseCapBytes']==8388608 and ci['wholeSecondsBeforeReceipt']<ci['wholeDeadlineSeconds']==60
root=json.loads((P/'ROOT-VERIFICATION.json').read_bytes());assert root['runID']==37045153855 and root['jobID']==110964632125 and root['artifactID']==11244177679 and root['zipSHA256']==Z and root['archiveSHA256']==S and root['gitBlobSHA1']==G
after={n:(P/n).stat() for n in names};metadata=[]
for n in names:
 old,new=before[n],after[n];assert (old.st_dev,old.st_ino,old.st_size,old.st_mode,old.st_mtime_ns,old.st_ctime_ns)==(new.st_dev,new.st_ino,new.st_size,new.st_mode,new.st_mtime_ns,new.st_ctime_ns);metadata.append({'name':n,'size':new.st_size,'atimeBeforeNS':old.st_atime_ns,'atimeAfterNS':new.st_atime_ns,'regularBodyMetadataPreserved':True})
v={'decision':'ACCEPT_EXACT_ACTUAL_CI_ZIP_AND_INNER_8CDF_BYTES_ONLY','runID':37045153855,'jobID':110964632125,'artifactID':11244177679,'headCommit':'ff5ac095f35a605d86e01edf0183b15f2e9c3874','zip':z,'standaloneArchive':a,'zipInnerArchive':inside,'zipReceiptSHA256':hashlib.sha256(receipt).hexdigest(),'CIReceiptByteExactStandalone':True,'ZIPMemberCount':2,'ZIPCRCSuccessfullyRead':True,'metadata':metadata,'wholeSecondsBeforeReceipt':ci['wholeSecondsBeforeReceipt'],'tarExtractedOrExecuted':False,'tarMemberCoverageVerified':False,'sourceWorkBytes':64*1048576,'reserveBytes':512*1048576,'initialCgroupCurrent':current,'initialCgroupMaximum':maximum,'qualification':'ZIP read/decode only; inner TAR container fully hashed without opening/decompressing/extracting TAR. No runtime/media/gameplay/visual/default/fun approval. Artifact metadata/job success independently read through connected tools; expiry remains external.'}
(O/'PROOF.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
