import errno,hashlib,json,os,pathlib,resource,stat,tarfile,time
P=pathlib.Path(__file__).parent;S=P.parent;R=pathlib.Path('/workspace/Roguelike-deckbuilder');CAP=64*1024;fallback=[];began=time.monotonic()
def op(p):
 try:fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME)
 except OSError as e:
  if e.errno!=errno.EPERM:raise
  fallback.append(str(p));fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW)
 assert stat.S_ISREG(os.fstat(fd).st_mode);return os.fdopen(fd,'rb')
def sha(p):
 h=hashlib.sha256()
 with op(p) as f:
  while b:=f.read(32768):h.update(b)
 return h.hexdigest()
def load(p):
 with op(p) as f:return json.load(f)
def meta(p):
 s=os.stat(p,follow_symlinks=False);assert stat.S_ISREG(s.st_mode)
 return {k:getattr(s,k) for k in ['st_dev','st_ino','st_mode','st_uid','st_gid','st_nlink','st_size','st_blocks','st_atime_ns','st_mtime_ns','st_ctime_ns']}|{'xattrs':{k:os.getxattr(p,k,follow_symlinks=False).hex() for k in os.listxattr(p,follow_symlinks=False)}}
def put(n,x):
 b=(json.dumps(x,separators=(',',':'))+'\n').encode();assert sum(p.stat().st_size for p in P.rglob('*') if p.is_file())+len(b)+8192<=CAP
 with (P/n).open('xb') as f:f.write(b);f.flush();os.fsync(f.fileno())
specs=[('f912',S/'opening-turn-payoff-opening-checkpoint-output-root-r1',R/'reviews/opening-turn-payoff-default-2026-10-02/archive','f9121c7b6416398241d1b5a160b4781f17a45dff4813260edaf4c3b6df1761af',3839783,S/'opening-turn-payoff-opening-checkpoint-preservation-independent-r1/GATE.json','940a3ec99f960aea7cbd5c9b942da6f595e0a4d45463ac963979eac03cfd425d'),('ce0f',S/'pixel-cue-evidence-capsule-root-r1',R/'reviews/coherent-native128-actual-trial-2026-10-02','ce0f8f40bcf0f0b22e5e4d93eef3d4660662826e617900aba09ac208c148dc13',8328689,S/'pixel-cue-evidence-preservation-independent-r1/GATE.json','11707477d92cc0a041f3dbbfd77d5ba6ef185a4d5df3bb181f2285d827dfeb05')]
results=[]
for ident,sd,cd,h,length,gate,gh in specs:
 scratch=sd/('evidence-'+h+'.tar.gz');canonical=cd/scratch.name;mb=meta(scratch);cb=meta(canonical);assert mb['st_size']==cb['st_size']==length;assert (mb['st_dev'],mb['st_ino'])!=(cb['st_dev'],cb['st_ino']);a=hashlib.sha256();b=hashlib.sha256();n=0
 with op(scratch) as sf,op(canonical) as cf:
  while x:=sf.read(32768):y=cf.read(len(x));assert x==y;a.update(x);b.update(y);n+=len(x)
  assert cf.read(1)==b''
 assert a.hexdigest()==b.hexdigest()==h and n==length;assert sha(gate)==gh;g=load(gate);assert g['decision'].startswith('ACCEPT') and g['archive']['sha256']==h
 si=sd/'INDEX.json';ci=cd/'INDEX.json';assert sha(si)==sha(ci);index=load(ci);unique={}
 for row in index['rows']:
  if row[5]=='newBlob':
   if row[2] in unique:assert unique[row[2]]==row[3]
   unique[row[2]]=row[3]
 seen=set();decoded=0
 with op(canonical) as f:
  with tarfile.open(fileobj=f,mode='r|gz',bufsize=32768) as tar:
   for member in tar:
    assert member.isfile() and member.name.startswith('blobs/');mh=member.name[6:];assert mh in unique and mh not in seen and member.size==unique[mh];body=tar.extractfile(member);hh=hashlib.sha256();count=0
    while x:=body.read(32768):hh.update(x);count+=len(x)
    assert hh.hexdigest()==mh and count==member.size;seen.add(mh);decoded+=count
 assert seen==set(unique);after=meta(scratch);ca=meta(canonical)
 assert {k:v for k,v in mb.items() if k!='st_atime_ns'}=={k:v for k,v in after.items() if k!='st_atime_ns'} and {k:v for k,v in cb.items() if k!='st_atime_ns'}=={k:v for k,v in ca.items() if k!='st_atime_ns'}
 related=[]
 for name in ['INDEX.json','READ-OBSERVATIONS.json','RESULT.json','README.md']:
  q=sd/name;related.append({'path':str(q),'sha256':sha(q),'bytes':q.stat().st_size,'preserve':'Not retirement scope'})
 results.append({'id':ident,'scratchPath':str(scratch),'canonicalPath':str(canonical),'sha256':h,'bytes':length,'allLiteralContainerBytesEqual':True,'scratchBefore':mb,'scratchAfter':after,'canonicalBefore':cb,'canonicalAfter':ca,'distinctPhysicalInodes':True,'grossOnlyIfPrivateLastLink':mb['st_blocks']*512,'COMPLETE':{'path':str(gate),'sha256':gh,'decision':g['decision']},'freshCanonicalTARMemberSHAAndLengthsMatched':len(seen),'freshDecodedBytes':decoded,'logicalRows':len(index['rows']),'inheritedLogicalReferences':len(index['rows'])-sum(1 for r in index['rows'] if r[5]=='newBlob'),'exactBothIndexSHA256':sha(ci),'indexArchivePointer':index['newArchive'],'relatedScratchControlsKept':related,'originalPhysicalPathLoss':'Removal loses this scratch archive pathname/private inode/times; canonical container/logical body bytes retained. Old index/gates/path readers must be mapped/reconstructed explicitly, not silently rewritten.'})
push=S/'opening-guidance-checkpoint-push-receipt-root-r2.json';assert sha(push)=='15b67770f34b776252a01f30ba172eecbf56cbff754a048c3bd19fa3f54c5f14';ps=load(push);assert ps['confirmedPush'] and ps['clean'] and ps['head']==ps['remote']=='06007e0d81298fa49cedeb46719d03cae9fba04c'
prior=R/'reviews/opening-cue-and-grounded-trial-2026-10-02/archive/INDEX.json';assert sha(prior)=='64fe0a3ea9e523e6a63c9b7e60cd4ae3df8c88ef15cfba858a86187e21e98d58';pi=load(prior);referenceChecks=[]
for c in pi['existingCapsules']:
 expected=next(r for r in results if r['id']==c['id']);assert c['archive']['path']==expected['canonicalPath'] and c['archive']['sha256']==expected['sha256'];referenceChecks.append({'id':c['id'],'current4513CanonicalReferenceExact':True,'completeGateSHA256':c['completeGateSHA256']})
del pi,index
dirs=[R/'src',R/'docs',R/'reviews/opening-turn-payoff-default-2026-10-02',R/'reviews/coherent-native128-actual-trial-2026-10-02',R/'reviews/opening-cue-and-grounded-trial-2026-10-02',S/'opening-turn-payoff-opening-checkpoint-source-author-r1',S/'opening-turn-payoff-opening-checkpoint-source-independent-r1',S/'opening-turn-payoff-opening-checkpoint-preservation-independent-r1',S/'pixel-cue-evidence-preserver-source-author-r3',S/'pixel-cue-evidence-preserver-source-independent-r3',S/'pixel-cue-evidence-preservation-independent-r1',S/'wording-grounded-trials-checkpoint-source-author-r1',S/'native-aftermath-starter-checkpoint-source-author-r1']
files={p for d in dirs for p in d.rglob('*') if p.is_file() and not p.is_symlink() and p.suffix in ['.py','.json','.md','.ts','.css']};files|={S/n for n in ['opening-cue-checkpoint-publication-root-r1.py','pixel-cue-capsule-publication-source-root-r1.py','pixel-cue-capsule-publication-source-root-r2.py','wording-guidance-development-selection-root-r1.py'] if (S/n).exists()}
needle=[str(r['scratchPath']) for r in results]+[str(spec[1]) for spec in specs];matches=[];skipped=[];total=0;scanned=0
for p in sorted(files):
 if p.stat().st_size>1048576:skipped.append({'path':str(p),'reason':'Bounded source scan max1MiB per file'});continue
 if total+p.stat().st_size>24*1048576:skipped.append({'path':str(p),'reason':'Bounded source scan max24MiB total'});continue
 with op(p) as f:data=f.read()
 total+=len(data);scanned+=1;hits=[s for s in needle if s.encode() in data]
 if hits:matches.append({'path':str(p),'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'matchedNeedles':hits,'interpretation':'Literal reference; historical reader/index may require reconstructed old pathname. Presence alone does not establish current operational need.'})
assert resource.getrusage(resource.RUSAGE_SELF).ru_maxrss<=24576
put('PROOF.json',{'phase':'INDEPENDENT_DUPLICATE_CONTAINER_RETIREMENT_PROPOSAL_ONLY','archivePairs':results,'combinedGrossAllocatedCandidateBytes':sum(r['grossOnlyIfPrivateLastLink'] for r in results),'prior06007PushReceipt':{'path':str(push),'sha256':sha(push),'RootConfirmedNotNewGitRead':True},'current4513CanonicalReferences':referenceChecks,'knownConsumerScan':{'roots':[str(d) for d in dirs],'scannedFileCount':scanned,'scannedBytes':total,'matches':matches,'skipped':skipped,'scope':'Finite named history/current code and newpreserver source; not all workspace/future consumers/FD/process inventory'},'NOATIMEFallbackPaths':fallback,'roleDisclosure':'Earlier independent f912/ce0f COMPLETE/copy reviewer and cue gameplay/archive work; current new checkpoint SOURCE author. This fresh review concerns duplicate physical retention only, not own preserver COMPLETE acceptance.','protectedZIPOrOtherArchiveBodyRead':False,'sourceBootstrap':'Exact paths via rg plus small AGENTS/gate/schema reads outside guard; both full container comparisons and canonical member/hash audit under original64+512 guard.','ownRSSKiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'elapsedSeconds':time.monotonic()-began,'noMutationDeletionRecompressionOrTARCopy':True})
print(json.dumps({'normal':True,'logicalPacketBytes':sum(p.stat().st_size for p in P.rglob('*') if p.is_file()),'matchedFiles':len(matches),'ownRSSKiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'elapsedSeconds':time.monotonic()-began}))
