import os,json,pathlib,hashlib,stat,resource,subprocess
resource.setrlimit(resource.RLIMIT_AS,(48*1048576,48*1048576))
Q=pathlib.Path(__file__).parent;S=pathlib.Path('/workspace/scratch');R=pathlib.Path('/workspace/Roguelike-deckbuilder')
A=S/'opening-capsule-duplicate-retirement-action-root-r2';D=R/'reviews/reviewed-opening-capsule-duplicate-retirement-2026-10-02';N=R/'reviews/opening-native-aftermath-and-starter-art-2026-10-02'
def pin(p):
 p=pathlib.Path(p);fd=os.open(p,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW);h=hashlib.sha256();n=0
 try:
  assert stat.S_ISREG(os.fstat(fd).st_mode)
  while True:
   b=os.read(fd,32768)
   if not b:break
   n+=len(b);h.update(b)
 finally:os.close(fd)
 return {'path':str(p),'bytes':n,'sha256':h.hexdigest()}
def load(p):
 fd=os.open(p,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW)
 with os.fdopen(fd) as f:return json.load(f)
def meta(p):
 t=p.lstat();return {k:getattr(t,k) for k in ['st_dev','st_ino','st_mode','st_uid','st_gid','st_nlink','st_size','st_blocks','st_atime_ns','st_mtime_ns','st_ctime_ns']}|{'xattrs':{k:os.getxattr(p,k,follow_symlinks=False).hex() for k in os.listxattr(p,follow_symlinks=False)}}
def git(*args):return subprocess.check_output(['git','--no-optional-locks',*args],cwd=R,env={**os.environ,'GIT_OPTIONAL_LOCKS':'0'},timeout=10)
def tree(head,roots):
 out={}
 for b in git('ls-tree','-r','-z',head,'--',*roots).split(b'\0'):
  if b:
   desc,p=b.split(b'\t');mode,kind,h=desc.decode().split();assert kind=='blob' and mode in ['100644','100755'];out[p.decode()]=h
 return out
def guard(p,work):
 d=load(p/'RESULT.json');adm=load(p/'ADMISSION.json');assert d['exit_code']==0 and d['failure'] is None and adm['admitted']
 assert adm['work']==work*1048576 and adm['reserve']==512*1048576 and d['initial']['headroom']>=(work+512)*1048576 and d['initial']['free']>=64*1048576
 assert d['memory_events_before']==d['memory_events_after']
 for row in [d['initial'],d['final']]+d['samples']:assert row['headroom']>=512*1048576
 for row in d['samples']:assert row['delta']<=work*1048576
 return {'result':pin(p/'RESULT.json'),'samples':len(d['samples']),'initialFree':d['initial']['free'],'maximumObservedDelta':max(x['delta'] for x in d['samples']),'minimumObservedHeadroom':min(x['headroom'] for x in d['samples'])}
pre=load(A/'PRE.json');result=load(A/'RESULT.json');loc=load(D/'LOCATION-MAP.json');assert len(pre['records'])==len(loc['entries'])==2
assert result['completed'] and result['allCanonicalBodiesAndMetadataUnchanged']
first=load(S/'native-checkpoint-current-push-receipt-root-r1.json');repair=load(S/'native-checkpoint-ignored-logs-current-push-receipt-root-r1.json');grant=load(S/'opening-capsule-duplicate-retirement-action-grant-root-r2.json')
assert pin(S/'native-checkpoint-current-push-receipt-root-r1.json')['sha256']==grant['confirmedPushSHA256']=='f96339f3fb9e67559cb53d515735e21f8ad6b71ca17be47940875a757441eec5'
assert pin(S/'native-checkpoint-ignored-logs-current-push-receipt-root-r1.json')['sha256']=='b0d31b31fa964452f4fcb8cae74dd8d40d741a8b86149b28d3a37c56b6fd8342'
assert pin(S/'opening-capsule-duplicate-retirement-action-grant-root-r2.json')['sha256']==pre['grantSHA256']
assert grant['authorized'] and grant['soleWriterConfirmed'] and grant['allSourceActorsPausedConfirmed']
assert grant['methodSHA256']==pre['methodSHA256']==pin(S/'retire-opening-capsule-duplicates-root-r2.py')['sha256']=='b1131f6cede49fceb01fcdfb87a251c95519561355acddd03045fba8e4fe7d71'
assert grant['independentMethodGateSHA256']==pre['sourceGateSHA256']=='4408a05e44ebe6f6c678920b6359653aa0b154aa03b818b1288c6e2a767c00d8'
assert grant['producerDecisionSHA256']==pin(D/'PRODUCER-DECISION.json')['sha256']=='67ee3cc4693359db655f1914a6507a0ae956afd497b6f70aec0f9dece5de2f61'
for d in [first,repair]:assert d['confirmedPush'] and d['clean'] and d['localHEAD']==d['remoteHEAD']
assert first['localHEAD']==result['confirmedHEADBeforeDeletion']==pre['freshConfirmedHEAD']=='8a19a23d7dbfc65ff9b4475d72cee3d661687b44'
assert repair['localHEAD']=='9726c5fd285bbaca7d5a7c656217d5b70b78ccfe' and git('rev-parse','HEAD').decode().strip()==repair['localHEAD']
assert not git('status','--porcelain=v1')
assert git('rev-parse',repair['localHEAD']+'^').decode().strip()==first['localHEAD']
postpins=[];canonical=[];related=[];times=[]
oldproof=load(S/'opening-cue-duplicate-retirement-independent-r1/PROOF.json')
for row,e,authority in zip(pre['records'],loc['entries'],oldproof['archivePairs']):
 assert row['oldPath']==e['oldScratchLogicalPath'] and row['canonicalPath']==e['preferredCanonicalPhysicalPath'] and row['sha256']==e['sha256'] and row['bytes']==e['bytes']
 assert row['oldMetadata']==e['originalScratchMetadata']==authority['scratchAfter'] and row['canonicalMetadata']==authority['canonicalAfter']
 assert row['oldMetadata']['st_nlink']==1 and not os.path.lexists(row['oldPath'])
 p=pathlib.Path(row['canonicalPath']);before=meta(p);body=pin(p);after=meta(p)
 assert before==after==row['canonicalMetadata'] and body['sha256']==row['sha256'] and body['bytes']==row['bytes']
 post=load(A/(row['id']+'-POST.json'));assert post['record']==row and post['oldPathAbsent'] and post['canonicalBodyAndMetadataUnchanged']
 assert (A/'PRE.json').stat().st_mtime_ns<=post['utcNs']
 age=post['utcNs']-first['remoteVerifiedAtNs'];assert 0<=age<=120*1000000000
 assert repair['remoteVerifiedAtNs']>post['utcNs'];times.append({'id':row['id'],'postUtcNs':post['utcNs'],'secondsAfterFirstPush':age/1e9})
 canonical.append(body|{'currentFullMetadataMatchesPRE':True,'oldPathAbsent':True});postpins.append(pin(A/(row['id']+'-POST.json')))
 for name in ['INDEX.json','RESULT.json','READ-OBSERVATIONS.json','README.md']:
  related.append(pin(pathlib.Path(row['oldPath']).parent/name))
assert times[0]['postUtcNs']<times[1]['postUtcNs']
assert result['exactRetiredScratchPaths']==[r['oldPath'] for r in pre['records']]
assert result['grossPrivateBlocks']==12173312==sum(r['oldMetadata']['st_blocks']*512 for r in pre['records'])
assert result['netObservedFreeChange']==result['freeAfter']-result['freeBefore']==12161024
roots=[str(N.relative_to(R)),str(D.relative_to(R))];oldtree=tree(first['localHEAD'],roots);newtree=tree(repair['localHEAD'],roots)
current={str(p.relative_to(R)) for root in [N,D] for p in root.rglob('*') if p.is_file()};assert set(newtree)==current and len(current)==164
assert sum(p.startswith(roots[0]+'/') for p in current)==87 and sum(p.startswith(roots[1]+'/') for p in current)==77
missing=set(newtree)-set(oldtree);fixed=repair['exactNewForcedRows'];assert len(missing)==len(fixed)==25 and {x['path'] for x in fixed}==missing
assert all(p.endswith('.log') for p in missing) and sum(x['bytes'] for x in fixed)==14460
for p,h in oldtree.items():assert newtree[p]==h
for x in fixed:
 currentpin=pin(R/x['path']);assert currentpin['sha256']==x['sha256'] and currentpin['bytes']==x['bytes']
 blob=git('show',repair['localHEAD']+':'+x['path']);assert hashlib.sha256(blob).hexdigest()==x['sha256'] and len(blob)==x['bytes']
for row in pre['records']:
 p=str(pathlib.Path(row['canonicalPath']).relative_to(R));a=tree(first['localHEAD'],[p]);b=tree(repair['localHEAD'],[p]);assert a==b and set(a)=={p}
prior=load(S/'retirement-publication-independent-r1/PROOF.json')
for x in prior['literalCopyPins']:
 h=pin(D/x['relativePath']);assert (h['sha256'],h['bytes'])==(x['sha256'],x['bytes'])
for x in prior['threeDocumentBodiesAndCompleteSuffixesUnchanged']:assert pin(x['path'])==x
for x in prior['runtimeBindings']:assert x['digest'] in ['64c2a14ada2b24796535f9bb71d8a6acc534685365bcf4f5665b21bf18595353','8bbaea72d9cb3b9757a2b8cb10ead190495ef61e6496e1ace0f942f635e00cf7']
rootguards=[guard(S/'native-checkpoint-push-retirement-guard-root-r3',128),guard(S/'native-checkpoint-ignored-logs-push-guard-root-r1',128)]
outer=load(S/'native-checkpoint-push-retirement-guard-root-r3/RESULT.json');assert first['remoteVerifiedAtNs']>outer['initial']['time_ns'] and times[-1]['postUtcNs']<outer['final']['time_ns']
stdout=load(S/'native-checkpoint-push-retirement-guard-root-r3/EXECUTION.log');assert stdout['phaseElapsed']<40 and stdout['confirmedHEAD']==first['localHEAD']
inner=json.loads(stdout['actionResult']);assert inner['resultSHA256']==pin(A/'RESULT.json')['sha256']
proof={'decision':'ACCEPT_EXACT_TWO_ENCODING_RETIREMENT_POST_STATE_AND_REPAIRED_DURABILITY_REJECT_COMPLETE_PRE_ACTION_PUBLICATION_PROCESS','actualTwoEncodingCoverageAccepted':True,'canonicalFullCompressedSHAAndMetadataAccepted':True,'fullProceduralAcceptance':False,'allPublicationPushedBeforeDeletion':False,'laterSupportingLogPublicationRepaired':True,'priorPublicationGateUnchanged':pin(S/'retirement-publication-independent-r1/GATE.json'),'methodSHA256':pre['methodSHA256'],'producerDecisionSHA256':grant['producerDecisionSHA256'],'PRE':pin(A/'PRE.json'),'POSTs':postpins,'RESULT':pin(A/'RESULT.json'),'canonicalBodies':canonical,'relatedScratchControlsStillPresent':related,'freshOriginalPushReceipt':pin(S/'native-checkpoint-current-push-receipt-root-r1.json'),'laterRepairPushReceipt':pin(S/'native-checkpoint-ignored-logs-current-push-receipt-root-r1.json'),'grant':pin(S/'opening-capsule-duplicate-retirement-action-grant-root-r2.json'),'observedOrdering':times,'firstHEAD':first['localHEAD'],'repairHEAD':repair['localHEAD'],'initialTrackedNativeAndRetirementFiles':len(oldtree),'currentTrackedNativeFiles':87,'currentTrackedRetirementFiles':77,'unpublishedBeforeActionLogCount':25,'unpublishedBeforeActionLogBytes':14460,'repairedLogs':fixed,'grossPrivateBlocks':12173312,'observedNetFreeDelta':12161024,'RootResourceGuards':rootguards,'ownRSSBytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,'limits':['Reject claim all reviewed publication controls were pushed before cleanup:25 ignored execution logs were added only after both unlinks. Clean8a19 receipt and method checks did not prove full publication membership. Later repair does not retroactively satisfy mandatory precondition.','Exact two current canonical container bodies fully SHA/size/full metadata/xattrs verified without extraction; old two names absent, eight related controls present, method has only two explicit unlink targets. No global all-material/FD/consumer absence certificate.','Old literal scratch readers require explicit append-only mapping or separately reviewed missing-path reconstruction; old inode/time/write-isolation rollback lost as recorded.','Git ls-tree/show of25 small logs only; no oldpack/ZIP/full other TAR replay/network call. Remote confirmation inherited from Root actual receipts, independently local commit membership/ancestry/HEAD/clean inspected.','Shared net free delta nonexclusive; original combined initial disk admission70,217,728B passed64MiB, PRE free63,762,432B is recorded, not a new64MiB admission. No future browser resource guarantee.','Root group cleanup/normal sampled guards are observed closure only, no full external actor attribution; earlier cue author provides engineering/storage review, no gameplay/art/selection approval.']}
assert proof['ownRSSBytes']<24*1048576
(Q/'PROOF.json').write_text(json.dumps(proof,indent=2)+'\n')
print(json.dumps({'exactCanonicalBytes':sum(x['bytes'] for x in canonical),'retired':2,'logsMissingBefore':25,'logsRepaired':25,'proceduralAcceptance':False,'ownRSS':proof['ownRSSBytes']}))
