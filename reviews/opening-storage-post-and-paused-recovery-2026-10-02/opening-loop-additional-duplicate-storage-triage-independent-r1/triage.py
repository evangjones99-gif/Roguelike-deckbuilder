import os,stat,json,hashlib,resource,pathlib,subprocess
P=pathlib.Path(__file__).parent
R=pathlib.Path('/workspace/Roguelike-deckbuilder')
S=pathlib.Path('/workspace/scratch')
SHA='451347c174a3fe78e5f7b6ef22736b7cfbbd33b39fd04ea20556730bb3b15a8b'
scratch=S/'wording-grounded-trials-checkpoint-output-root-r1'/('evidence-'+SHA+'.tar.gz')
canonical=R/'reviews/opening-cue-and-grounded-trial-2026-10-02/archive'/scratch.name
def put(n,j):
 b=(json.dumps(j,indent=2)+'\n').encode();assert len(b)<32768
 with (P/n).open('xb') as f:f.write(b);f.flush();os.fsync(f.fileno())
def meta(p):
 s=p.lstat();assert stat.S_ISREG(s.st_mode)
 return {k:getattr(s,k) for k in ['st_dev','st_ino','st_mode','st_uid','st_gid','st_nlink','st_size','st_blocks','st_mtime_ns','st_ctime_ns','st_atime_ns']}|{'xattrs':{k:os.getxattr(p,k).hex() for k in os.listxattr(p)}}
def nonatime(m):return {k:v for k,v in m.items() if k!='st_atime_ns'}
def pinned(p):
 before=meta(p);fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME)
 try:
  h=hashlib.sha256();n=0
  while b:=os.read(fd,65536):h.update(b);n+=len(b)
 finally:os.close(fd)
 after=meta(p);assert nonatime(before)==nonatime(after);assert n==before['st_size']
 return {'path':str(p),'sha256':h.hexdigest(),'bytes':n,'before':before,'after':after,'readMode':'O_RDONLY|O_NOFOLLOW|O_NOATIME; no fallback'}
a,b=pinned(scratch),pinned(canonical)
assert a['sha256']==b['sha256']==SHA and a['bytes']==b['bytes']==7848992
assert (a['before']['st_dev'],a['before']['st_ino'])!=(b['before']['st_dev'],b['before']['st_ino'])
assert a['before']['st_nlink']==1
fd1=os.open(scratch,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME);fd2=os.open(canonical,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME)
try:
 while True:
  x=os.read(fd1,65536);y=os.read(fd2,65536);assert x==y
  if not x:break
finally:os.close(fd1);os.close(fd2)
assert nonatime(meta(scratch))==nonatime(a['before']) and nonatime(meta(canonical))==nonatime(b['before'])
idxpath=canonical.parent/'INDEX.json';idxpin=pinned(idxpath);idx=json.loads(idxpath.read_bytes())
assert idxpin['sha256']=='64fe0a3ea9e523e6a63c9b7e60cd4ae3df8c88ef15cfba858a86187e21e98d58'
oldidx=pinned(scratch.parent/'INDEX.json');assert oldidx['sha256']==idxpin['sha256']
assert idx['newArchive']['path']==str(scratch) and idx['newArchive']['sha256']==SHA
assert len(idx['rows'])==952 and len({r[2] for r in idx['rows'] if r[5]=='newBlob'})==711
gp=canonical.parent.parent/'archive-complete-independent/GATE.json';gatepin=pinned(gp);gate=json.loads(gp.read_bytes())
assert gatepin['sha256']=='df8ef40e5409409f004d2a2c08d7ca20dfb519f31590c379459c29d2f6983a85'
assert gate['archiveSHA256']==SHA and gate['completePreservationAccepted'] and gate['all952LogicalOriginalBodiesMatched']
receipts=[]
for leaf in ['opening-guidance-checkpoint-push-receipt-root-r2.json','native-checkpoint-ignored-logs-current-push-receipt-root-r1.json']:
 q=S/leaf;receipts.append({'pin':pinned(q),'receipt':json.loads(q.read_bytes())})
roots=[R/'src',R/'docs',R/'reviews/opening-cue-and-grounded-trial-2026-10-02',R/'reviews/opening-native-aftermath-and-starter-art-2026-10-02',S/'native-aftermath-starter-checkpoint-source-author-r1',S/'wording-grounded-trials-checkpoint-source-author-r1',scratch.parent]
needles=[str(scratch).encode(),scratch.parent.name.encode(),SHA.encode()]
matches=[];skipped=[];files=0;bytesread=0
for root in roots:
 for q in sorted(root.rglob('*')):
  if q.is_symlink() or not q.is_file() or q.suffix.lower() not in ['.json','.py','.md','.ts','.css','.txt','.log']:continue
  size=q.stat().st_size
  if size>1536000 or bytesread+size>24000000:skipped.append({'path':str(q),'bytes':size});continue
  raw=q.read_bytes();files+=1;bytesread+=len(raw)
  if any(n in raw for n in needles):
   lines=[{'line':i,'text':t[:240]} for i,t in enumerate(raw.decode('utf-8',errors='replace').splitlines(),1) if any(n.decode() in t for n in needles)]
   matches.append({'path':str(q),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'matchLines':lines[:5],'totalMatchingLines':len(lines)})
cache=[{'pin':b,'purpose':'Known canonical modest reviewed evidence; no protected archive or Gitpack; body pair just freshly verified.'}]
for q in [R/'public/art/adversaries-atlas.png',R/'public/art/companions-atlas.png']:
 cache.append({'pin':pinned(q),'purpose':'Known ordinary canonical atlas; full body newly pinned only, not art approval or frozen-map replay.'})
rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024;assert rss<24*1048576
put('PROOF.json',{'pair':[a,b],'literalFullPairEquality':True,'indexes':[idxpin,oldidx],'completeMemberProof':gatepin,'memberProofInheritedNotNewlyDecoded':True,'logicalRows':952,'newUniqueBodies':711,'historicalNewArchiveRow':idx['newArchive'],'receipts':receipts,'consumerScan':{'roots':list(map(str,roots)),'files':files,'bytes':bytesread,'skipped':skipped,'matches':matches,'scope':'Fixed named roots; filename/SHA/path references only, no global consumer or FD claim.'},'cacheHintCandidates':cache,'ownMaxRSSBytes':rss})
put('FINDING.json',{'decision':'IDENTIFIED_VERIFIED_PRIVATE_SCRATCH_DUPLICATE_TRIAGE_ONLY','candidatePath':str(scratch),'canonicalPath':str(canonical),'sha256':SHA,'bytes':a['bytes'],'grossPrivateAllocatedBytes':a['before']['st_blocks']*512,'authority':'No retirement, cleanup, producer, action, cache-hint or Git authority. Separate fresh proposal/replacement-map publication/current clean push/producer judgment/finite independently reviewed action/POST required.','necessity':'Old INDEX and COMPLETE gate still name scratch path; old readers may require separately reviewed fresh reconstruction or append-only location mapping. Known later checkpoint inheritance uses canonical4513. Bounded reference scan does not prove all current or future consumer absence.','preservation':'Retain canonical container, old scratch metadata/path mapping, all INDEX/read observations/receipts/gates/source/art/versions. Private inode/time is unique metadata; exact container body is replicated.','resource':'Gross blocks are not measured net recovery. Reclaimed filesystem capacity cannot establish browser admission or memory headroom.','cacheHints':'Proposal only: fresh O_NOFOLLOW/O_RDONLY exact device/inode/body pins and before/after metadata, closed actors, advisory POSIX_FADV_DONTNEED limited named ordinary canonical evidence/atlases. Advice may be ignored, does not free disk, and makes no admission promise. No advice executed.','relationship':'Previously independently reviewed earlier cue capsules and gameplay; authored new native checkpoint preservation SOURCE, so this is not acceptance of own COMPLETE archive.','protectedFiles':'No protected ZIP, release, Gitpack, unique old dataset/art/version or unrelated TAR body accessed.','sourceProfile':'Ordinary64MiB+512MiB reserve/disk64MiB, ownRSS below24MiB; cgroup observations nonexclusive.'})
print(json.dumps({'ownRSSBytes':rss,'pairSHA256':SHA,'consumerFiles':files,'matches':len(matches),'candidateGrossBytes':a['before']['st_blocks']*512,'authority':'triage only'}))
