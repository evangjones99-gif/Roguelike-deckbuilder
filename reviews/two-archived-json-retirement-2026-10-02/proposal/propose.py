import os,stat,pathlib,json,hashlib,tarfile,resource,time
resource.setrlimit(resource.RLIMIT_DATA,(24*1048576,24*1048576))
R=pathlib.Path(__file__).parent;CG=pathlib.Path('/sys/fs/cgroup');BASE=int((CG/'memory.current').read_text());EVENTS=(CG/'memory.events').read_text();START=time.monotonic();ROWS=[]
CAPROOT='/workspace/Roguelike-deckbuilder/reviews/opening-ready-and-rapid-drop-2026-10-01'
RAWROOT='/workspace/scratch/settle-drag-comparison-actual-r1'
EXPECTED={'VISUAL-RESULT.json':('b7713194f75462873cf59193251203f0cfebfd65c0f32b6732c2a1bac4354d74',3013464),'VISUAL-PROGRESS.json':('76c5d89a05d73e0fb9e0c17559c900be4515668fbfd3ec9e919e9bc2adda34b2',3013437)}
ASHA='27c7d4e2a117c5fa2625146a5ca78e7965705f8f809e44b6c2d7b9efb52817af';MSHA='005225286c6784598181a46bd0ad25cc99d4ee54b3c2394d58d5ea915b41155b'
def guard(label):
 c=int((CG/'memory.current').read_text());m=int((CG/'memory.max').read_text());v=os.statvfs(R);rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024;row={'label':label,'elapsed':time.monotonic()-START,'sharedDelta':c-BASE,'headroom':m-c,'free':v.f_bavail*v.f_frsize,'ownMaxRSS':rss};ROWS.append(row)
 assert row['sharedDelta']<=64*1048576 and row['headroom']>=512*1048576 and row['free']>=64*1048576 and rss<=24*1048576 and row['elapsed']<60 and EVENTS==(CG/'memory.events').read_text();return row
def meta(s):return {k:getattr(s,k) for k in ['st_dev','st_ino','st_mode','st_nlink','st_uid','st_gid','st_size','st_blocks','st_atime_ns','st_mtime_ns','st_ctime_ns']}
def parent(path):
 fd=os.open('/',os.O_PATH|os.O_DIRECTORY|os.O_NOFOLLOW)
 try:
  for n in pathlib.Path(path).parts[1:]:
   nxt=os.open(n,os.O_PATH|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd);os.close(fd);fd=nxt
  return fd
 except BaseException:os.close(fd);raise
def pin(path,decode=False):
 p,n=os.path.split(path);d=parent(p);fd=None
 try:
  ls=meta(os.stat(n,dir_fd=d,follow_symlinks=False));fd=os.open(n,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME,dir_fd=d);fs=meta(os.fstat(fd));assert ls==fs and stat.S_ISREG(fs['st_mode'])
  xs={k:os.getxattr(fd,k).hex() for k in os.listxattr(fd)};h=hashlib.sha256();body=b''
  while True:
   b=os.read(fd,65536)
   if not b:break
   h.update(b)
   if decode:body+=b;assert len(body)<256*1024
  assert fs==meta(os.fstat(fd))==meta(os.stat(n,dir_fd=d,follow_symlinks=False)) and xs=={k:os.getxattr(fd,k).hex() for k in os.listxattr(fd)};guard('stream-closed')
  return {'path':path,'sha256':h.hexdigest(),'bytes':fs['st_size'],'lstat':ls,'fstat':fs,'xattrs':xs,'nofollowHeldParents':True,'O_NOATIME':True,'duringReadMetadataExact':True},body
 finally:
  if fd is not None:os.close(fd)
  os.close(d)
initial=guard('initial');raw=[]
for name,(sha,size) in EXPECTED.items():
 p,_=pin(RAWROOT+'/'+name);assert p['sha256']==sha and p['bytes']==size and p['fstat']['st_nlink']==1 and p['fstat']['st_dev']==27;raw.append(p)
assert raw[0]['fstat']['st_ino']!=raw[1]['fstat']['st_ino']
capsule,_=pin(CAPROOT+'/evidence.tar.gz');assert capsule['sha256']==ASHA and capsule['bytes']==3303630
gatepin,gatebody=pin(CAPROOT+'/independent-capsule-review/GATE.json',True);gate=json.loads(gatebody)
assert gate['decision']=='ACCEPT_EXACT_BOUNDED_EVIDENCE_CAPSULE_WITH_DECLARED_FOOTPRINT_DEVIATION' and gate['archive']['sha256']==ASHA and gate['archiveManifestSHA256']==MSHA
reviewpin,reviewbody=pin(CAPROOT+'/independent-capsule-review/REVIEW.md',True);assert 'Every661 archive blob roundtrips' in reviewbody.decode()
archivefd=os.open(capsule['path'],os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME);mapping=[];blobs=[];manifest=None;memberCount=0
try:
 assert meta(os.fstat(archivefd))==capsule['fstat']
 with os.fdopen(os.dup(archivefd),'rb') as stream:
  with tarfile.open(fileobj=stream,mode='r|gz') as archive:
   for member in archive:
    memberCount+=1;assert memberCount<=1000
    if member.name=='MANIFEST.json':
     assert member.isfile() and member.size<2*1048576
     with archive.extractfile(member) as f:body=f.read(2*1048576)
     assert len(body)==member.size and hashlib.sha256(body).hexdigest()==MSHA;manifest=json.loads(body)
     for rawfile in raw:
      entries=[e for e in manifest['entries'] if e.get('originalPath')==rawfile['path']];assert len(entries)==1
      entry=entries[0];assert entry['sha256']==rawfile['sha256'] and entry['bytes']==rawfile['bytes']
      mapping.append({'originalPath':rawfile['path'],'logicalPath':entry['path'],'blobMember':'blobs/'+entry['sha256'],'sha256':entry['sha256'],'bytes':entry['bytes']})
    elif member.name in ['blobs/'+v[0] for v in EXPECTED.values()]:
     assert member.isfile();h=hashlib.sha256();count=0
     with archive.extractfile(member) as f:
      while True:
       b=f.read(65536)
       if not b:break
       h.update(b);count+=len(b)
     blobs.append({'member':member.name,'sha256':h.hexdigest(),'bytes':count,'tarMode':member.mode,'tarUID':member.uid,'tarGID':member.gid,'tarMtime':member.mtime})
    if memberCount%128==0:guard('archive128members')
 assert meta(os.fstat(archivefd))==capsule['fstat']
finally:os.close(archivefd)
assert len(mapping)==len(blobs)==2
for m in mapping:assert any(b['member']==m['blobMember'] and b['sha256']==m['sha256'] and b['bytes']==m['bytes'] for b in blobs)
controlPaths=[CAPROOT+'/SUMMARY.json',CAPROOT+'/README.md','/workspace/scratch/settle-drag-caller-author-r2/driver-paired-r1.mjs','/workspace/scratch/settle-drag-caller-author-r2/supervise-paired-r1.py','/workspace/scratch/settle-drag-actual-gameplay-independent-r1/review_evidence.py','/workspace/scratch/ready-default-300-caller-root-r1/driver.mjs','/workspace/scratch/ready-default-300-caller-root-r1/supervise.py','/workspace/scratch/ready-default-first300-grant-root-r1.json','/workspace/scratch/target-clear-ghost-caller-author-r2/driver.mjs','/workspace/scratch/target-clear-ghost-caller-author-r2/supervise.py']
consumers=[]
for path in controlPaths:
 p,b=pin(path,True);t=b.decode();hits=[line[:400] for line in t.splitlines() if any(k in line for k in ['settle-drag-comparison-actual-r1','VISUAL-RESULT.json','VISUAL-PROGRESS.json'])][:12]
 consumers.append({'pin':{'path':p['path'],'sha256':p['sha256'],'bytes':p['bytes']},'exactHistoricalRootMentioned':RAWROOT in t,'resultNameMentioned':'VISUAL-RESULT.json' in t,'progressNameMentioned':'VISUAL-PROGRESS.json' in t,'referenceLines':hits})
driver=next(x for x in consumers if x['pin']['path'].endswith('ready-default-300-caller-root-r1/driver.mjs'));supervisor=next(x for x in consumers if x['pin']['path'].endswith('ready-default-300-caller-root-r1/supervise.py'))
assert driver['pin']['sha256']=='badafdeae12140fd4ac3beb0e441a7dec37b5d3747a81e65c0d6272c946170c4' and supervisor['pin']['sha256']=='48b3935b60dbb348129c8ebe534e0e5724feac2680d4fc8d4516a42ad87bbab3'
assert not driver['exactHistoricalRootMentioned'] and not supervisor['exactHistoricalRootMentioned']
parents=[]
for path in [RAWROOT,CAPROOT]:
 fd=parent(path)
 try:parents.append({'path':path,'fstat':meta(os.fstat(fd)),'xattrs':{n:os.getxattr('/proc/self/fd/'+str(fd),n).hex() for n in os.listxattr('/proc/self/fd/'+str(fd))}})
 finally:os.close(fd)
proposal={'decision':'PREFER selective retirement of ONLY two redundant physical scratch JSON encodings after independent replacement/no-longer-needed review, producer judgment and fresh confirmed push. NO ACTION AUTHORITY.','rawFiles':raw,'capsule':capsule,'manifestSHA256':MSHA,'exactLogicalMapping':mapping,'freshBlobRoundtrip':blobs,'archiveMemberCount':memberCount,'independentPreservationGate':gatepin,'independentPreservationReview':reviewpin,'originalGateFacts':{'decision':gate['decision'],'logicalBodies':gate['logicalBodies'],'uniqueBlobs':gate['uniqueBlobs'],'footprintDeviationPreserved':True,'noRetirementAuthorityInGate':gate['noReleasePromotionRetirementOrRuntimeAuthorization']},'preservedParentRights':parents,'consumerPins':consumers,'grossRawAllocationBytes':sum(p['fstat']['st_blocks']*512 for p in raw),'rawLogicalBytes':sum(p['bytes'] for p in raw),'whySuccessorBetter':'The already published, independently roundtrip-reviewed capsule retains both distinct full bodies, exact logical/original mappings and surrounding provenance, raw saves/events/reviews. Its immutable content-addressed encoding is reproducible and avoids retaining another6.0MB loose allocation. It improves storage for the current opening work, not gameplay or archival semantics.','whyLooseCopiesNoLongerNeeded':'Closed historical actual/readers have preserved findings and all bodies in the capsule. The exact current300 caller neither reads nor names the historical packet root; generic same result/progress basenames are separate current packet outputs. Old reviewer source directly addresses this old root and therefore needs explicit reconstruction for a future rerun. Keeping bytes/methods/rights/provenance in the verified published capsule suffices under a documented reconstruction workflow; old physical scratch inode/time isolation is conditionally unnecessary. Independent reviewer may reject this judgment.','rawPathLoss':'Retirement removes BOTH original raw JSON directory entries; do not claim paths stay readable. Historical links and hardcoded old review inputs require reconstructing exact bodies to a fresh owned path and intentionally directing a new review to that reconstruction. No rewriting old reviews/reference claims.','metadataLoss':'Original raw inode identities/current kernel ctime disappear and old per-path atime/mtime cease to be live. Full original stat/xattrs/parent rights recorded here. Reconstructed copies receive fresh inode/time/ownership/mode; body SHA/length are exact. No mandatory metadata restoration or exact full-metadata rollback is claimed.','restoreProcedure':'Pin immutable capsule SHA/manifestSHA, stream MANIFEST to choose exact logical mapping, stream specified blob into an explicitly fresh destination with exclusive nofollow creation, verify full SHA/length, and preserve new restore receipts. Provided helper is source-only and unexecuted. No giant duplicate extraction or writes into original frozen packets now.','immutableWorkflow':'Keep capsule/GATE/review and this proposal immutable; never re-encode archive or mutate existing historical bodies. Future reproductions/reviews use fresh stages/outputs. Obtain independent review, producer judgment and current push before a separate finite two-path retirement method. Root reports current90d128 push; this source review does not invoke Git/remote or certify a later push.','preservationScope':'ONLY VISUAL-RESULT.json and VISUAL-PROGRESS.json loose encodings. All JPEGs, checkpoints/saves, NATIVE-POINTERS, lifecycle/resource/build/caller/review/failure bodies, source/art/rights/provenance, other archives and unique inputs remain untouched. This is no broad cleanup.','coverageLimits':'Scoped static source references, declared closed historical contexts and exact current caller pins; no global FD/mmap/queued/future-consumer inventory. Generic names do not prove historical consumption. Any live need for these original paths blocks retirement until resolved.','resourceQualification':'Normal64+512 source guard, ownRSS/RLIMIT_DATA24MiB; earlier tiny control discovery was outside this guard but all relied-on controls are fully reread here. No body extraction output, Node/imported app/Git/build/browser/native/action.'}
with (R/'PROPOSAL.json').open('x') as f:json.dump(proposal,f,indent=2);f.write('\n')
final=guard('final')
with (R/'RESOURCE.json').open('x') as f:json.dump({'initial':initial,'rows':ROWS,'final':final,'eventsBefore':EVENTS,'eventsAfter':(CG/'memory.events').read_text(),'allFDsClosed':True,'scope':'Observed shared64MiB work plus512reserve; own24MiB. Not exclusive cgroup attribution or global actor proof.'},f,indent=2);f.write('\n')
print(json.dumps({'rawPaths':[p['path'] for p in raw],'logicalMapping':mapping,'grossAllocation':proposal['grossRawAllocationBytes'],'final':final,'allFDsClosed':True}))
