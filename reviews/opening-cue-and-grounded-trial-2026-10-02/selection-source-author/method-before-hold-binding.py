"""Root-only future two-file development-source selection. Never runs Git/build/game or writes dist."""
import errno,hashlib,json,os,pathlib,resource,stat,sys,time,uuid
R=pathlib.Path('/workspace/Roguelike-deckbuilder');S=pathlib.Path('/workspace/scratch');STAGE=S/'opening-turn-payoff-wording-stage-r1'
OLD_FREEZE=S/'target-clear-default-build-author-r1/RUNTIME-FREEZE.json';NEW_FREEZE=S/'opening-turn-payoff-wording-strict-build-root-r1/final-seal-r1/RUNTIME-FREEZE.json'
OLD_FREEZE_SHA='739f5e87f95f2ca2ad4e60f7b90ea00aa6384d74c1ae2fc8a4e60266e705ce62';NEW_FREEZE_SHA='d6c225d5408c8e60433aed54655e922a44af224621fc8c48cb6aca8cd3c5883a'
CHECKPOINT_PLAN='0998d948c57e2fb3d1e01f34e61028d5c80db299df308d3b1e83ab902d4281b7'
ACTUAL_GATES=[(S/'opening-turn-payoff-wording-actual-gameplay-independent-r2/GATE.json','cbfcbc0e082c17b663d3bb1fac3f7a415505e0aeb7ca664814ebea36e3cccc52'),(S/'opening-turn-payoff-wording-actual-visual-independent-r1/GATE.json','cae95281a0aef122085edb29e68b6e88ff7571d69333ad3c8fdd7162fc9f1e17'),(S/'opening-turn-payoff-wording-actual-technical-independent-r1/GATE.json','83eab5f5ed24dfe7d5bf7ae353ce44f20d716493b106175ef119aae79cc19e3e')]
FALLBACK=[]
def open_read(p):
 flags=os.O_RDONLY|os.O_NOFOLLOW
 try:fd=os.open(p,flags|os.O_NOATIME)
 except OSError as e:
  if e.errno!=errno.EPERM:raise
  FALLBACK.append(str(p));fd=os.open(p,flags)
 f=os.fdopen(fd,'rb');assert stat.S_ISREG(os.fstat(fd).st_mode);return f
def digest(p):
 h=hashlib.sha256();n=0
 with open_read(p) as f:
  a=os.fstat(f.fileno())
  while b:=f.read(32768):h.update(b);n+=len(b)
  z=os.fstat(f.fileno());assert a.st_dev==z.st_dev and a.st_ino==z.st_ino and a.st_size==z.st_size and a.st_mtime_ns==z.st_mtime_ns
 return h.hexdigest(),n
def read_json(p):
 with open_read(p) as f:return json.load(f)
def pinned(ref):assert digest(ref['path'])[0]==ref['sha256'];return read_json(ref['path'])
def fullmeta(p):
 x=os.stat(p,follow_symlinks=False);assert stat.S_ISREG(x.st_mode)
 return {k:getattr(x,k) for k in ['st_dev','st_ino','st_mode','st_uid','st_gid','st_nlink','st_size','st_mtime_ns','st_ctime_ns','st_blocks']}|{'xattrs':{n:os.getxattr(p,n,follow_symlinks=False).hex() for n in os.listxattr(p,follow_symlinks=False)}}
def sync_dir(p):
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
 try:os.fsync(fd)
 finally:os.close(fd)
def write_new(p,data,mode=0o600):
 fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,mode)
 with os.fdopen(fd,'wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
def canonical_body(p):
 with open_read(p) as f:return f.read()
def run(grant_path,grant_sha,out_path):
 if not __debug__:raise RuntimeError('Optimized Python disables required validation; refused before writes')
 started=time.monotonic()
 assert digest(grant_path)[0]==grant_sha;grant=read_json(grant_path)
 assert grant['authorized'] is True and grant['developmentSourceSelectionOnly'] is True and grant['soleCanonicalWriterConfirmed'] is True and grant['noDevServerOrOtherCanonicalSourceWriterConfirmed'] is True
 assert grant['canonicalPaths']==['src/main.ts','src/opening-turn-payoff.css']
 assert grant['methodSHA256']==digest(__file__)[0] and grant['checkpointSourcePlanSHA256']==CHECKPOINT_PLAN
 independent=pinned(grant['independentSourceGate']);assert independent['decision'].startswith('ACCEPT') and grant['independentSourceGate']['RootVerifiedExactMethodSourceEligibility'] is True
 preservation=grant['completePreservation'];assert preservation['RootVerifiedCompleteScopeAndSourcePlan'] is True and preservation['sourcePlanSHA256']==CHECKPOINT_PLAN
 complete=pinned(preservation['gate']);assert complete['decision'].startswith('ACCEPT')
 assert digest(preservation['archive']['path'])[0]==preservation['archive']['sha256']
 index=pinned(preservation['index']);assert index['allOriginalPathsRetained'] is True and index['newArchive']['sha256']==preservation['archive']['sha256']
 assert grant['confirmedPush']['RootVerifiedCurrentCleanAndPushed'] is True
 assert digest(grant['confirmedPush']['receipt']['path'])[0]==grant['confirmedPush']['receipt']['sha256']
 assert len(grant['confirmedPush']['head'])==40 and all(c in '0123456789abcdef' for c in grant['confirmedPush']['head'])
 for path,h in ACTUAL_GATES:assert digest(path)[0]==h and read_json(path)['decision'].startswith('ACCEPT')
 assert digest(OLD_FREEZE)[0]==OLD_FREEZE_SHA and digest(NEW_FREEZE)[0]==NEW_FREEZE_SHA
 old=read_json(OLD_FREEZE);new=read_json(NEW_FREEZE);assert len(old['inputs'])==88 and len(new['inputs'])==89 and len(old['outputs'])==len(new['outputs'])==56
 delta={k:(old['inputs'].get(k),new['inputs'].get(k)) for k in set(old['inputs'])|set(new['inputs']) if old['inputs'].get(k)!=new['inputs'].get(k)}
 assert delta=={'src/main.ts':('e7568a5a672cac8cf11d98a4fa8a1bfa9784f9087c8de62f59905b018e44845c','efecdc20b01faac49a75640268d169409b010dae166f84a135dfe2449bef99bc'),'src/opening-turn-payoff.css':(None,'a84a4a47ddc671234aea4ff655357f9205dc123a394be250924df1c201777983')}
 assert hashlib.sha256(json.dumps(new['inputs'],sort_keys=True,separators=(',',':')).encode()).hexdigest()=='64c2a14ada2b24796535f9bb71d8a6acc534685365bcf4f5665b21bf18595353'
 for parent in [R,R/'src',R/'dist',S]:assert parent.is_dir() and not parent.is_symlink()
 main=R/'src/main.ts';css=R/'src/opening-turn-payoff.css';assert not css.exists() and not css.is_symlink()
 main_before=fullmeta(main);dist_before={}
 for rel,h in old['inputs'].items():assert digest((R/rel).resolve(strict=True))[0]==h
 for rel,h in old['outputs'].items():
  p=R/'dist'/rel;assert digest(p.resolve(strict=True))[0]==h;dist_before[rel]=fullmeta(p)
 for rel,h in new['inputs'].items():assert digest((STAGE/rel).resolve(strict=True))[0]==h
 for rel,h in new['outputs'].items():assert digest((STAGE/'dist'/rel).resolve(strict=True))[0]==h
 # The exact new preservation INDEX must retain the old canonical main logical name/body.
 assert any(pathlib.Path(index['roots'][r[0]])/r[1]==main and r[2]==old['inputs']['src/main.ts'] for r in index['rows'])
 assert os.statvfs(R).f_bavail*os.statvfs(R).f_frsize>=64*1048576+512*1024
 out=pathlib.Path(out_path);assert out.parent==S and out.name.startswith('wording-development-source-selection-actual-root-') and not out.exists() and not out.is_symlink()
 assert resource.getrusage(resource.RUSAGE_SELF).ru_maxrss<=24576 and time.monotonic()-started<=60
 out.mkdir(mode=0o700);sync_dir(S);token=uuid.uuid4().hex;temporary=R/'src'/('.wording-source-main-'+token+'.ts');restore=R/'src'/('.wording-source-restore-'+token+'.ts');written=False;owned=None
 old_bytes=canonical_body(main);candidate=canonical_body(STAGE/'src/main.ts');css_bytes=canonical_body(STAGE/'src/opening-turn-payoff.css')
 assert hashlib.sha256(old_bytes).hexdigest()==old['inputs']['src/main.ts'] and hashlib.sha256(candidate).hexdigest()==new['inputs']['src/main.ts'] and hashlib.sha256(css_bytes).hexdigest()==new['inputs']['src/opening-turn-payoff.css'] and len(css_bytes)==163
 def record(name,value):write_new(out/name,(json.dumps(value,indent=2)+'\n').encode());sync_dir(out)
 def journal(event,extra=None):
  data=(json.dumps({'event':event,'utcNs':time.time_ns(),'extra':extra},separators=(',',':'))+'\n').encode()
  with (out/'JOURNAL.jsonl').open('ab') as f:f.write(data);f.flush();os.fsync(f.fileno())
  sync_dir(out)
 def check():
  assert resource.getrusage(resource.RUSAGE_SELF).ru_maxrss<=24576 and time.monotonic()-started<=60
  assert sum(p.stat().st_size for p in out.iterdir() if p.is_file())<=512*1024
 def ours():
  if not written or not owned:return False
  try:return fullmeta(main)==owned and digest(main)[0]==new['inputs']['src/main.ts']
  except (FileNotFoundError,AssertionError):return False
 record('BEFORE.json',{'grantSHA256':grant_sha,'RootConfirmedCleanPushedHead':grant['confirmedPush']['head'],'currentGitReadByHelper':False,'oldSourceDigest':old['sourceDigest'],'oldDistDigest':old['outputsDigest'],'candidateSourceDigest':new['sourceDigest'],'candidateBuiltOutputDigest':new['outputsDigest'],'mainMetadata':main_before,'sourcePaths':['src/main.ts','src/opening-turn-payoff.css'],'bothSourceFilesAtomicTogether':False});journal('BEFORE_VALIDATED')
 try:
  write_new(out/'OLD-main.ts',old_bytes);assert digest(out/'OLD-main.ts')[0]==old['inputs']['src/main.ts'];sync_dir(out);journal('OLD_LITERAL_BACKUP_DURABLE')
  check();write_new(temporary,candidate,main_before['st_mode']&0o777);tempmeta=fullmeta(temporary);sync_dir(R/'src');journal('FRESH_MAIN_TEMP_DURABLE',{'path':str(temporary),'sha256':new['inputs']['src/main.ts']})
  assert fullmeta(main)==main_before and digest(main)[0]==old['inputs']['src/main.ts']
  write_new(css,css_bytes,0o644);assert digest(css)[0]==new['inputs']['src/opening-turn-payoff.css'];sync_dir(R/'src');journal('NEW_CSS_EXCLUSIVELY_CREATED_DURABLE')
  check();assert fullmeta(main)==main_before and digest(main)[0]==old['inputs']['src/main.ts'];os.replace(temporary,main);written=True;sync_dir(R/'src');now=fullmeta(main);assert (now['st_dev'],now['st_ino'])==(tempmeta['st_dev'],tempmeta['st_ino']);owned=now;journal('MAIN_ATOMICALLY_REPLACED_DURABLE')
  actual={rel:digest((R/rel).resolve(strict=True))[0] for rel in new['inputs']};assert actual==new['inputs'];assert hashlib.sha256(json.dumps(actual,sort_keys=True,separators=(',',':')).encode()).hexdigest()==new['sourceDigest']
  for rel,h in old['outputs'].items():assert digest((R/'dist'/rel).resolve(strict=True))[0]==h and fullmeta(R/'dist'/rel)==dist_before[rel]
  check();journal('FULL89_SOURCE_AND_OLD56_DIST_POST_VERIFIED')
  record('RESULT.json',{'decision':'SELECTED_DEVELOPMENT_SOURCE_ONLY_DIST_RETAINED_OLD','sourceDigest':new['sourceDigest'],'mappedInputCount':89,'canonicalMainSHA256':new['inputs']['src/main.ts'],'canonicalCueCSSSHA256':new['inputs']['src/opening-turn-payoff.css'],'newMainMetadata':owned,'oldMainLiteralBackup':str(out/'OLD-main.ts'),'oldMainInodeTimeNotRestoredOrPreserved':True,'retainedDistDigest':old['outputsDigest'],'retainedDistOutputCount':56,'reviewedCandidateBuiltOutputDigest':new['outputsDigest'],'canonicalDistNowMatchesNewSource':False,'runtimeInterpretation':'npm development reads selected source if subsequently started; retained preview/desktop dist remains old8b artifact. Neither server nor preview/desktop was launched here.','metadataDocsWritten':False,'gitBuildGameReleaseTagCleanupExecuted':False,'allOtherMappedSourceAndDistBodiesExact':True,'sourceFilesPairAtomic':False,'sameOuter64GuardRequired':True,'NOATIMEFallbackPaths':FALLBACK,'ownRSSKiBBeforeResult':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'elapsedBeforeResultSeconds':time.monotonic()-started,'terminalMeasurementsRequireGuardStdout':True});check()
  print(json.dumps({'normal':True,'result':str(out/'RESULT.json'),'terminalElapsedSeconds':time.monotonic()-started,'terminalOwnRSSKiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'terminalLogicalOutputBytes':sum(p.stat().st_size for p in out.iterdir() if p.is_file()),'qualification':'Two source files not globally atomic; observed preconditions plus Root sole-writer contract, not OS CAS or universal protection. Terminal stdout cost not independently metered.'}))
 except BaseException as error:
  recovery={'mainWritten':written,'attempted':False,'restoredOldMain':False,'CSSPrefixPreserved':css.exists(),'temporaryRetainedIfPresent':str(temporary),'noFileDeletion':True,'originalError':repr(error),'fullOld88SourceSetRestored':False,'qualification':'A retained new CSS prefix means restoring old main alone is not complete88-source rollback. CSS/user edits are not deleted.'}
  try:
   if ours():
    recovery['attempted']=True;write_new(out/'FAILED-OWNED-main.ts',candidate);assert digest(out/'OLD-main.ts')[0]==old['inputs']['src/main.ts'];write_new(restore,old_bytes,main_before['st_mode']&0o777);sync_dir(R/'src')
    if ours():os.replace(restore,main);sync_dir(R/'src');assert digest(main)[0]==old['inputs']['src/main.ts'];recovery['restoredOldMain']=True;journal('OLD_MAIN_ONLY_RECOVERED_OWN_WRITE_STILL_MATCHED')
    else:recovery['skipReason']='Concurrent source metadata/body change observed; restore temporary retained; user changes not overwritten'
   elif written:recovery['skipReason']='Current main is not exact owned inode/metadata/hash; user changes not overwritten'
  except BaseException as failure:recovery['recoveryError']=repr(failure)
  record('FAILURE.json',recovery);raise
if __name__=='__main__':
 assert len(sys.argv)==4,'ROOT_GRANT_JSON ROOT_GRANT_SHA256 NEW_RESULT_DIRECTORY';run(*sys.argv[1:])
