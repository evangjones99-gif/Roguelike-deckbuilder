"""Finite, exact two scratch-encoding retirement after published mapping and fresh confirmed clean push."""
from pathlib import Path
import os,sys,json,stat,hashlib,subprocess,time,resource
STARTED=time.monotonic()
def check():
 if time.monotonic()-STARTED>40:raise RuntimeError("Finite40s action deadline exceeded; any earlier per-path progress remains recorded")
 if resource.getrusage(resource.RUSAGE_SELF).ru_maxrss>24576:raise RuntimeError("Own24MiB action ceiling exceeded")
R=Path('/workspace/Roguelike-deckbuilder');D=R/'reviews/reviewed-opening-capsule-duplicate-retirement-2026-10-02';S=Path('/workspace/scratch')
PAIRS=[('f912',S/'opening-turn-payoff-opening-checkpoint-output-root-r1/evidence-f9121c7b6416398241d1b5a160b4781f17a45dff4813260edaf4c3b6df1761af.tar.gz',R/'reviews/opening-turn-payoff-default-2026-10-02/archive/evidence-f9121c7b6416398241d1b5a160b4781f17a45dff4813260edaf4c3b6df1761af.tar.gz','f9121c7b6416398241d1b5a160b4781f17a45dff4813260edaf4c3b6df1761af',3839783),('ce0f',S/'pixel-cue-evidence-capsule-root-r1/evidence-ce0f8f40bcf0f0b22e5e4d93eef3d4660662826e617900aba09ac208c148dc13.tar.gz',R/'reviews/coherent-native128-actual-trial-2026-10-02/evidence-ce0f8f40bcf0f0b22e5e4d93eef3d4660662826e617900aba09ac208c148dc13.tar.gz','ce0f8f40bcf0f0b22e5e4d93eef3d4660662826e617900aba09ac208c148dc13',8328689)]
def digest(p):
 h=hashlib.sha256();fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME)
 with os.fdopen(fd,'rb') as f:
  assert stat.S_ISREG(os.fstat(f.fileno()).st_mode)
  while b:=f.read(65536):check();h.update(b)
 return h.hexdigest()
def met(p):
 t=p.lstat();return {k:getattr(t,k) for k in ['st_dev','st_ino','st_mode','st_uid','st_gid','st_nlink','st_size','st_blocks','st_atime_ns','st_mtime_ns','st_ctime_ns']}|{'xattrs':{k:os.getxattr(p,k,follow_symlinks=False).hex() for k in os.listxattr(p,follow_symlinks=False)}}
def sync(p):
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
 try:os.fsync(fd)
 finally:os.close(fd)
def pinned(path,h):assert digest(path)==h;return json.loads(path.read_bytes())
def write(p,v):
 check()
 with p.open('x') as f:json.dump(v,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 sync(p.parent)
if __name__=='__main__':
 if not __debug__:raise RuntimeError('Optimized Python erases safety assertions; action refused')
 check()
 assert len(sys.argv)==7,'GATE GATE_SHA PUSH_RECEIPT PUSH_SHA ACTION_GRANT GRANT_SHA'
 gatepath=Path(sys.argv[1]);g=pinned(gatepath,sys.argv[2]);push=pinned(Path(sys.argv[3]),sys.argv[4]);grant=pinned(Path(sys.argv[5]),sys.argv[6]);methodSHA=digest(Path(__file__))
 assert g['exactTwoPathActionMethodEligible'] is True and g['methodSHA256']==methodSHA
 assert grant['authorized'] is True and grant['soleWriterConfirmed'] is True and grant['allSourceActorsPausedConfirmed'] is True and grant['methodSHA256']==methodSHA and grant['independentMethodGateSHA256']==sys.argv[2]
 assert push['confirmedPush'] is True and push['clean'] is True and push['localHEAD']==push['remoteHEAD']
 head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True,timeout=10).strip();assert head==push['localHEAD'];assert not subprocess.check_output(['git','status','--porcelain'],cwd=R,timeout=10)
 age=time.time_ns()-push['remoteVerifiedAtNs'];assert 0<=age<=120*1000000000;assert grant['confirmedPushSHA256']==sys.argv[4]
 check()
 location=pinned(D/'LOCATION-MAP.json','7aa54ca2c8ab29604d5d334e5cac825b2bd6145fecbe90a656e255f771cdafb4');proposal=pinned(D/'proposal-r2/GATE.json','596577259f0b2455c03b3b3d160700f4c7f1f6a90c049e1ba2347752976ddd8c');producer=json.loads((D/'PRODUCER-DECISION.json').read_bytes());assert producer['preferCanonicalAndRetireTwoPrivateEncodingsAfterPush'] is True and grant['producerDecisionSHA256']==digest(D/'PRODUCER-DECISION.json')
 records=[]
 for ident,old,new,h,n in PAIRS:
  check()
  for p in [old,new]:
   assert not p.is_symlink()
   for parent in p.parents:assert not parent.is_symlink()
  oldmeta=met(old);newmeta=met(new);entry=next(x for x in location['entries'] if x['sha256']==h)
  assert entry['oldScratchLogicalPath']==str(old) and entry['preferredCanonicalPhysicalPath']==str(new) and entry['bytes']==n
  assert oldmeta==entry['originalScratchMetadata'] and oldmeta['st_nlink']==1 and stat.S_ISREG(oldmeta['st_mode']) and stat.S_ISREG(newmeta['st_mode']) and oldmeta['st_size']==newmeta['st_size']==n
  assert (oldmeta['st_dev'],oldmeta['st_ino'])!=(newmeta['st_dev'],newmeta['st_ino'])
  assert digest(old)==digest(new)==h and met(old)==oldmeta and met(new)==newmeta
  subprocess.run(['git','ls-files','--error-unmatch',str(new.relative_to(R)),str((D/'LOCATION-MAP.json').relative_to(R)),str((D/'PRODUCER-DECISION.json').relative_to(R))],cwd=R,check=True,stdout=subprocess.DEVNULL,timeout=10)
  records.append({'id':ident,'oldPath':str(old),'canonicalPath':str(new),'sha256':h,'bytes':n,'oldMetadata':oldmeta,'canonicalMetadata':newmeta})
 out=S/'opening-capsule-duplicate-retirement-action-root-r2';out.mkdir(exist_ok=False);beforeFree=os.statvfs(R).f_bavail*os.statvfs(R).f_frsize
 write(out/'PRE.json',{'records':records,'freshConfirmedHEAD':head,'methodSHA256':methodSHA,'sourceGateSHA256':sys.argv[2],'grantSHA256':sys.argv[6],'freeBytes':beforeFree,'scope':'Exactly two private encodings only; originals of source/art/reviews and canonical archive bodies stay. Historical direct scratch readers need published mapping or separately reviewed reconstruction; no global FD/consumer absence or old inode/time reconstruction claimed.'})
 for row in records:
  check()
  old=Path(row['oldPath']);new=Path(row['canonicalPath']);assert met(old)==row['oldMetadata'] and met(new)==row['canonicalMetadata'];check();old.unlink();sync(old.parent)
  assert not os.path.lexists(old) and digest(new)==row['sha256'] and met(new)==row['canonicalMetadata'];write(out/(row['id']+'-POST.json'),{'oldPathAbsent':True,'canonicalBodyAndMetadataUnchanged':True,'record':row,'utcNs':time.time_ns()})
 afterFree=os.statvfs(R).f_bavail*os.statvfs(R).f_frsize;write(out/'RESULT.json',{'completed':True,'exactRetiredScratchPaths':[x['oldPath'] for x in records],'allCanonicalBodiesAndMetadataUnchanged':True,'confirmedHEADBeforeDeletion':head,'freeBefore':beforeFree,'freeAfter':afterFree,'netObservedFreeChange':afterFree-beforeFree,'grossPrivateBlocks':sum(x['oldMetadata']['st_blocks']*512 for x in records),'allOtherMaterialsRetained':True,'qualification':'Shared filesystem free delta is nonexclusive; each private nlink1 body absent and exact canonical replacement remains. No symlink/auto-restore/old review rewrite; no new playable version or quality approval.'})
 print(json.dumps({'completed':True,'resultPath':str(out/'RESULT.json'),'resultSHA256':digest(out/'RESULT.json'),'freeBefore':beforeFree,'freeAfter':afterFree}))
