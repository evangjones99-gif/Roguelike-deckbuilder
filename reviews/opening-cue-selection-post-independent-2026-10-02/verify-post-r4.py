import os,json,hashlib,stat,resource,time,tarfile,subprocess
from pathlib import Path,PurePosixPath
P=Path(__file__).parent;R=Path('/workspace/Roguelike-deckbuilder');C=R/'reviews/opening-cue-and-grounded-trial-2026-10-02';S=Path('/workspace/scratch/wording-development-source-selection-actual-root-r1');started=time.monotonic()
def opened(p):
 fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME);assert stat.S_ISREG(os.fstat(fd).st_mode);return os.fdopen(fd,'rb')
def read(p):
 with opened(p)as f:return f.read()
def sha(p):
 with opened(p)as f:
  a=os.fstat(f.fileno());h=hashlib.sha256();n=0
  while b:=f.read(65536):h.update(b);n+=len(b)
  assert a==os.fstat(f.fileno())
 return h.hexdigest(),n
def expect(p,h,n=None):
 got,size=sha(p);assert got==h and(n is None or n==size);return {'path':str(p),'sha256':got,'bytes':size}
def load(p):return json.loads(read(p))
pub=load(C/'PUBLICATION.json');expect(C/'PUBLICATION.json','177ac62256d18bd75a9cf9a71e369bcde8f17ff09c22a4b16f781b353f03fe9e');assert len(pub['records'])==120
dest=set();orig=set();total=0
for x in pub['records']:
 rel=PurePosixPath(x['destination']);assert not rel.is_absolute()and '..'not in rel.parts
 d=R/str(rel);assert d.is_relative_to(C)and str(d)not in dest;dest.add(str(d));orig.add(x['originalPath']);total+=x['bytes']
 expect(Path(x['originalPath']),x['sha256'],x['bytes']);expect(d,x['sha256'],x['bytes'])
 with opened(Path(x['originalPath']))as a,opened(d)as b:
  while v:=a.read(65536):assert b.read(len(v))==v
  assert not b.read(1)
assert total==9298292 and len(orig)==120
assert {str(x)for x in C.rglob('*')if x.is_file()}==dest|{str(C/'README.md'),str(C/'PUBLICATION.json')}
assert not any(x.is_symlink()for x in C.rglob('*'))
assert read(C/'README.md')==(pub['scope']+'\n').encode()
for name,root in [('archive-source-author','wording-grounded-trials-checkpoint-source-author-r1'),('archive-source-failed-r1','wording-grounded-trials-checkpoint-source-independent-r1'),('archive-source-independent','wording-grounded-trials-checkpoint-source-independent-r2'),('archive-complete-independent','wording-grounded-trials-checkpoint-complete-independent-r1')]:
 source=Path('/workspace/scratch')/root;copies={str(x.relative_to(C/name))for x in(C/name).rglob('*')if x.is_file()};assert copies=={str(x.relative_to(source))for x in source.rglob('*')if x.is_file()}
expect(C/'archive-complete-independent/GATE.json','df8ef40e5409409f004d2a2c08d7ca20dfb519f31590c379459c29d2f6983a85');expect(C/'archive-source-independent/GATE.json','8a260e2815faa8e54671b1d4e7c03df61ebaaea2dc6b4958c3798a12cf83e7f4')
assert pub['completePreservationGateSHA256']=='df8ef40e5409409f004d2a2c08d7ca20dfb519f31590c379459c29d2f6983a85'
result=load(S/'RESULT.json');expect(S/'RESULT.json','1e581aa938ccb423dc269a0c5767f4b6633cc0e060d1880655d4fd27375e2ac7');assert pub['sourceSelectionResultSHA256']==sha(S/'RESULT.json')[0]
plan=load(C/'archive-source-author/PLAN.json');idx=load(C/'archive/INDEX.json')
assert idx['rows']==plan['rows'] and idx['runtimeAuthorities']==plan['runtimeAuthorities']
word=load(Path(plan['runtimeAuthorities'][0]['freezePath']));old=load(Path(plan['runtimeAuthorities'][2]['freezePath']))
assert len(word['inputs'])==89 and len(old['outputs'])==56
assert word['sourceDigest']==result['sourceDigest']=='64c2a14ada2b24796535f9bb71d8a6acc534685365bcf4f5665b21bf18595353'
assert old['outputsDigest']==result['retainedDistDigest']=='8bbaea72d9cb3b9757a2b8cb10ead190495ef61e6496e1ace0f942f635e00cf7'
assert word['outputsDigest']==result['reviewedCandidateBuiltOutputDigest']=='82e049c9fee16e4a56d80520a0feb19c54546dc86f83953f27d703d53fec7042'
for rel,h in word['inputs'].items():expect(R/rel,h)
for rel,h in old['outputs'].items():expect(R/'dist'/rel,h)
assert set(word['inputs'])-set(old['inputs'])=={'src/opening-turn-payoff.css'} and not(set(old['inputs'])-set(word['inputs']))
assert [p for p in old['inputs']if old['inputs'][p]!=word['inputs'][p]]==['src/main.ts']
assert {str(x.relative_to(R/'dist'))for x in(R/'dist').rglob('*')if x.is_file()}==set(old['outputs'])
assert not any(x.name.startswith('.wording-source-main-')for x in(R/'src').iterdir())
expect(S/'OLD-main.ts',old['inputs']['src/main.ts'],116568)
assert result['canonicalMainSHA256']==word['inputs']['src/main.ts']=='efecdc20b01faac49a75640268d169409b010dae166f84a135dfe2449bef99bc'
assert result['canonicalCueCSSSHA256']==word['inputs']['src/opening-turn-payoff.css']=='a84a4a47ddc671234aea4ff655357f9205dc123a394be250924df1c201777983'
assert len(read(R/'src/opening-turn-payoff.css'))==163
newmeta=result['newMainMetadata'];live=os.stat(R/'src/main.ts',follow_symlinks=False)
for k,v in newmeta.items():
 if k=='xattrs':assert {n:os.getxattr(R/'src/main.ts',n).hex()for n in os.listxattr(R/'src/main.ts')}==v
 else:assert getattr(live,k)==v
before=load(S/'BEFORE.json');grant=load(C/'ROOT-SELECTION-GRANT.json');assert sha(C/'ROOT-SELECTION-GRANT.json')[0]==before['grantSHA256']
assert before['sourcePaths']==['src/main.ts','src/opening-turn-payoff.css'] and not before['bothSourceFilesAtomicTogether'] and result['oldMainInodeTimeNotRestoredOrPreserved']
method=Path('/workspace/scratch/wording-development-source-selection-author-r1/select-development-source.py');expect(method,grant['methodSHA256']);assert grant['methodSHA256']=='9c3c231b71c03ce23b5515f2cca5dcc3b341af418216000bc1edab0dc2a3b788'
expect(Path(grant['independentSourceGate']['path']),grant['independentSourceGate']['sha256']);assert grant['independentSourceGate']['sha256']=='54dbe0760eb34634e79f6402e5a8dbaba79d8b5a5a91ce6c6a26fc9526320e40'
events=[json.loads(x)for x in read(S/'JOURNAL.jsonl').decode().splitlines()]
assert [x['event']for x in events]==['BEFORE_VALIDATED','OLD_LITERAL_BACKUP_DURABLE','FRESH_MAIN_TEMP_DURABLE','NEW_CSS_EXCLUSIVELY_CREATED_DURABLE','MAIN_ATOMICALLY_REPLACED_DURABLE','FULL89_SOURCE_AND_OLD56_DIST_POST_VERIFIED']
assert [x['utcNs']for x in events]==sorted(x['utcNs']for x in events)
docneeds={x['sha256']:x for x in plan['metadataSnapshot']['docs']};historical={}
archive=Path(idx['newArchive']['path']);expect(archive,'451347c174a3fe78e5f7b6ef22736b7cfbbd33b39fd04ea20556730bb3b15a8b',7848992)
with opened(archive)as f,tarfile.open(fileobj=f,mode='r|gz',bufsize=65536)as tf:
 for m in tf:
  h=m.name[6:]
  if h in docneeds:
   b=tf.extractfile(m).read();assert len(b)==docneeds[h]['bytes']and hashlib.sha256(b).hexdigest()==h;historical[h]=b
assert set(historical)==set(docneeds)
docrecords=[]
for h,x in docneeds.items():
 now=read(Path(x['path']));assert now.endswith(historical[h]);prefix=now[:-len(historical[h])];assert prefix and b'64c2'in prefix and b'8b'in prefix
 docrecords.append({'path':x['path'],'historicalSHA256':h,'currentSHA256':hashlib.sha256(now).hexdigest(),'prependedBytes':len(prefix),'oldFullBodyRetained':True})
head='d144368d04b5af55abc7c81927417eb88ee47e16';g=subprocess.run(['git','-c','gc.auto=0','show',head+':README.md'],cwd=R,capture_output=True,timeout=10);assert g.returncode==0
addition=b' After first-turn commands are spent, the cue explains your remaining card choice and that **End turn lets enemies act**.'
needle=b'Click or drag a BINDING card from the bottom hand into the field, then select its ready creature and an enemy for a free command.'
now=read(R/'README.md');assert g.stdout.count(needle)==1 and now==g.stdout.replace(needle,needle+addition) and now.count(addition)==1
guardrecords=[]
for name in ['wording-grounded-checkpoint-publication-guard-root-r1','wording-development-source-selection-guard-root-r1']:
 gp=Path('/workspace/scratch')/name;v=load(gp/'RESULT.json');assert v['exit_code']==0 and v['failure']is None and v['memory_events_before']==v['memory_events_after'] and 'all child group processes closed'in v['scope']
 guardrecords.append({'path':str(gp),'resultSHA256':sha(gp/'RESULT.json')[0],'samples':len(v['samples']),'minimumHeadroom':min(x['headroom']for x in v['samples']),'recordedChildGroupClosure':True})
terminal=load(Path('/workspace/scratch/wording-development-source-selection-guard-root-r1/EXECUTION.log'))
assert terminal['terminalElapsedSeconds']<60 and terminal['terminalOwnRSSKiB']<24*1024 and terminal['terminalOutputBytes']<192*1024
for k,v in result.items():assert terminal[k]==v
assert not result['canonicalDistNowMatchesNewSource'] and not result['gitBuildGameReleaseTagCleanupExecuted'] and result['NOATIMEFallbackPaths']==[]
rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024;assert rss<24*1048576
out={'decision':'PASS_LITERAL_PUBLICATION_AND_DEVELOPMENT_SOURCE_POST_CHECKS','publication':expect(C/'PUBLICATION.json',sha(C/'PUBLICATION.json')[0]),'literalCopyCount':120,'literalCopyBytes':total,'everyOriginalAndCopyFullSHAAndByteMatched':True,'exact122PublishedFileMembership':True,'fullAuthorFailedR1AcceptedR2CompleteFamiliesCopied':True,'publishedReadmeMatchesPublicationScope':True,'sourceSelectionResult':expect(S/'RESULT.json',sha(S/'RESULT.json')[0]),'currentCanonical89InputsMatchFrozen64c2':True,'canonicalHeldDist56BodiesMatchOld8b':True,'reviewedFrozenCandidate82eRemainsSeparate':True,'sourceMapChangesOnlyMainPlusNew163ByteCSS':True,'oldMainLiteralExact':expect(S/'OLD-main.ts',old['inputs']['src/main.ts']),'oldInodeTimeLossAcceptedNotRestored':True,'newMainRecordedMetadataFreshlyExact':True,'sixJournalEventsExactOrder':True,'sourceFilePairNotAtomic':True,'historicalArchiveDocsNotMisrequiredAsCurrentCanonical':True,'fourDocsPrependOnlyFullHistoricalTextRetained':docrecords,'readmeExactOneInsertionInverseToGitD144':{'oldSHA256':hashlib.sha256(g.stdout).hexdigest(),'currentSHA256':hashlib.sha256(now).hexdigest(),'addedBytes':len(addition)},'rootGuardRecords':guardrecords,'rootTerminal':{k:v for k,v in terminal.items()if k.startswith('terminal')},'noServerBuildGameStartedByReviewer':True,'noCanonicalMutationByReviewer':True,'ownRSSBytes':rss,'elapsedSeconds':time.monotonic()-started,'ownNOATIMEFallback':False,'notCurrentPushVerification':True,'noPixelMotionFunOrReleaseAcceptance':True}
with(P/'POST-CHECKS.json').open('x')as f:json.dump(out,f,indent=2,sort_keys=True);f.write('\n')
print(json.dumps({'check':'PASS','copiedBodies':120,'copiedBytes':total,'sourceInputs':89,'retainedDistOutputs':56,'ownRSSBytes':rss,'elapsedSeconds':out['elapsedSeconds']}))
