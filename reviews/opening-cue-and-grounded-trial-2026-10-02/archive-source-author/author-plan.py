import ast,collections,errno,gzip,hashlib,json,os,pathlib,resource,stat,zlib
P=pathlib.Path('/workspace/scratch/wording-grounded-trials-checkpoint-source-author-r1');S=pathlib.Path('/workspace/scratch');R=pathlib.Path('/workspace/Roguelike-deckbuilder');roots=[];roles=[];rows=[];seen={};fallbacks=[];readObservations=[]
def sha(b):return hashlib.sha256(b).hexdigest()
def idx(seq,x):
 if x not in seq:seq.append(x)
 return seq.index(x)
def op(p):
 p=pathlib.Path(p);q=p.resolve(strict=True);flags=os.O_RDONLY|os.O_NOFOLLOW
 try:fd=os.open(q,flags|os.O_NOATIME)
 except OSError as e:
  if e.errno!=errno.EPERM:raise
  fallbacks.append(str(q));fd=os.open(q,flags)
 return os.fdopen(fd,'rb'),q
def digest(p):
 h=hashlib.sha256();n=0;f,q=op(p)
 with f:
  bstat=os.fstat(f.fileno());assert stat.S_ISREG(bstat.st_mode)
  while b:=f.read(32768):h.update(b);n+=len(b)
  astat=os.fstat(f.fileno());assert bstat==astat and bstat.st_mtime_ns==astat.st_mtime_ns and bstat.st_ctime_ns==astat.st_ctime_ns
 return h.hexdigest(),n
def j(p):return json.loads(pathlib.Path(p).read_bytes())
capsules=[{'id':'ce0f','archive':{'path':str(R/'reviews/coherent-native128-actual-trial-2026-10-02/evidence-ce0f8f40bcf0f0b22e5e4d93eef3d4660662826e617900aba09ac208c148dc13.tar.gz'),'sha256':'ce0f8f40bcf0f0b22e5e4d93eef3d4660662826e617900aba09ac208c148dc13'},'index':{'path':str(R/'reviews/coherent-native128-actual-trial-2026-10-02/INDEX.json'),'sha256':'115bbdb35d9cdff98503a3a5c63ced87e49a48d198194c9caa45268254bec0cf'},'completeGateSHA256':'11707477d92cc0a041f3dbbfd77d5ba6ef185a4d5df3bb181f2285d827dfeb05'},{'id':'f912','archive':{'path':str(R/'reviews/opening-turn-payoff-default-2026-10-02/archive/evidence-f9121c7b6416398241d1b5a160b4781f17a45dff4813260edaf4c3b6df1761af.tar.gz'),'sha256':'f9121c7b6416398241d1b5a160b4781f17a45dff4813260edaf4c3b6df1761af'},'index':{'path':str(R/'reviews/opening-turn-payoff-default-2026-10-02/archive/INDEX.json'),'sha256':'fd6e057da394aa127766f434bd70c9b1045c17f92ab0e94fb70dd77ebb6a9ad2'},'completeGateSHA256':'940a3ec99f960aea7cbd5c9b942da6f595e0a4d45463ac963979eac03cfd425d'}]
members={};historicalMasters=[]
for ci,cap in enumerate(capsules):
 for key in ['archive','index']:assert digest(cap[key]['path'])[0]==cap[key]['sha256']
 if ci==0:
  decoder=json.JSONDecoder();buf='';old=[]
  with pathlib.Path(cap['index']['path']).open('r') as f:
   while '"logicalBodies":[' not in buf:
    b=f.read(32768);assert b;buf=(buf+b)[-131072:]
   buf=buf.split('"logicalBodies":[',1)[1]
   while True:
    buf=buf.lstrip(' \n\r\t,')
    if buf.startswith(']'):break
    try:row,end=decoder.raw_decode(buf)
    except json.JSONDecodeError:
     b=f.read(32768);assert b;buf+=b;assert len(buf)<131072;continue
    assert row['blob']=='blobs/'+row['sha256'];members.setdefault(row['sha256'],(row['bytes'],ci))
    if row['originalPath'].startswith('/workspace/generated_images/'):historicalMasters.append({'path':row['originalPath'],'sha256':row['sha256'],'bytes':row['bytes'],'exactExistingCapsule':'ce0f','bodyNotRereadOrRecopied':True})
    old.append(1);buf=buf[end:]
  assert len(old)==831
 else:
  old=j(cap['index']['path']);assert len(old['rows'])==490
  for ri,rel,h,n,role,storage in old['rows']:
   if storage=='newBlob':members.setdefault(h,(n,ci))
   else:assert h in members and members[h][0]==n
def add(p,role,expected=None):
 p=pathlib.Path(p);key=str(p)
 if key in seen:
  if expected:assert rows[seen[key]][2]==expected
  return
 h,n=digest(p);assert expected is None or expected==h
 storage='newBlob'
 if h in members:assert members[h][0]==n;storage='existingCapsule:'+capsules[members[h][1]]['id']
 seen[key]=len(rows);rows.append([idx(roots,str(p.parent)),p.name,h,n,idx(roles,role),storage])
def folder(name,role):
 base=S/name;assert base.is_dir() and not base.is_symlink(),name
 for p in sorted(base.rglob('*')):
  if p.is_file():assert not p.is_symlink();add(p,role)
scopeFolders={
 'wording actual full originals':['opening-turn-payoff-wording-actual-comparison-root-r1'],
 'wording reviews including failed gameplay r1':['opening-turn-payoff-wording-actual-gameplay-independent-r1','opening-turn-payoff-wording-actual-gameplay-independent-r2','opening-turn-payoff-wording-actual-visual-independent-r1','opening-turn-payoff-wording-actual-technical-independent-r1'],
 'wording source build caller originals and failures':['opening-turn-payoff-wording-source-author-r1','opening-turn-payoff-wording-source-independent-r1','opening-turn-payoff-wording-source-output-root-r1','opening-turn-payoff-wording-reconstruct-guard-root-r1','opening-turn-payoff-wording-build-controls-root-r1','opening-turn-payoff-wording-build-controls-author-guard-root-r1','opening-turn-payoff-wording-build-controls-author-guard-root-r2','opening-turn-payoff-wording-build-controls-independent-r1','opening-turn-payoff-wording-assembly-guard-root-r1','opening-turn-payoff-wording-strict-build-root-r1','opening-turn-payoff-wording-freeze-guard-root-r1','opening-turn-payoff-wording-actual-build-independent-r1','opening-turn-payoff-wording-actual-caller-source-final-r1','opening-turn-payoff-wording-actual-caller-source-final-r2','opening-turn-payoff-wording-caller-source-independent-r1','wording-caller-grammar-guard-root-r1'],
 'grounded pixel actual full compressed originals':['coherent-native128-fallen-ground-comparison-actual-r1'],
 'grounded pixel actual negative qualified reviews':['coherent-native128-fallen-ground-actual-technical-independent-r1','coherent-native128-fallen-ground-actual-visual-independent-r1','coherent-native128-fallen-ground-gameplay-independent-r1'],
 'grounded pixel source build caller all failures':['native128-fallen-ground-applied-source-root-r1','native128-fallen-ground-reconstructed-source-independent-r1','native128-fallen-ground-reconstruction-guard-root-r1','coherent-native128-fallen-ground-build-controls-source-author-r1','coherent-native128-fallen-ground-build-controls-independent-r1','coherent-native128-fallen-ground-assembly-guard-root-r1','coherent-native128-fallen-ground-strict-build-root-r1','coherent-native128-fallen-ground-freeze-guard-root-r1','coherent-native128-fallen-ground-actual-build-independent-r1','coherent-native128-fallen-ground-actual-build-independent-r2','coherent-native128-fallen-ground-caller-source-author-r1','coherent-native128-fallen-ground-caller-source-final-r2','coherent-native128-fallen-ground-caller-source-final-r3','coherent-native128-fallen-ground-caller-source-independent-r1','coherent-native128-fallen-ground-caller-source-final-independent-r3','grounded-pixel-caller-grammar-guard-root-r1'],
 'fallen sprite converter output source and visual provenance':['native128-reaver-fallen-grounded-cleanup-source-author-r1','native128-reaver-fallen-grounded-cleanup-source-independent-r1','native128-reaver-fallen-grounded-output-root-r1','native128-reaver-fallen-grounded-conversion-guard-root-r1','native128-reaver-fallen-grounded-native-visual-independent-r1'],
 'cached courtyard source provenance retained drafts':['standard-sol-pixel-courtyard-assets-author-r1','standard-sol-pixel-courtyard-assets-author-r2','standard-sol-pixel-courtyard-independent-r1','standard-sol-pixel-courtyard-independent-r2','standard-sol-pixel-courtyard-native-verification-independent-r3'],
 'unimplemented starter input converter and negative alpha diagnostic':['starter-family-native128-converter-source-author-r1','starter-family-native128-converter-source-independent-r1','starter-family-master-inspection-guard-root-r1','starter-family-native128-alpha-diagnostic-guard-root-r1'],
 'separate rejected expiry prototype no actual run':['native128-defeat-aftermath-source-author-r1','native128-defeat-aftermath-source-independent-r1']}
for role,names in scopeFolders.items():
 for name in names:folder(name,role)
singleton=['opening-turn-payoff-wording-activation-root-r1.json','opening-turn-payoff-wording-reconstruct-root-r1.py','opening-turn-payoff-wording-build-controls-author-root-r2.py','wording-caller-grammar-root-r1.py','wording-actual-grant-root-r1.py','wording-actual-grant-root-r1.json','wording-actual-terminal-tool-return-root-r1.json','coherent-native128-fallen-ground-activation-root-r1.json','native128-fallen-ground-reconstruction-activation-root-r1.json','grounded-pixel-caller-grammar-root-r1.py','grounded-pixel-actual-grant-root-r1.py','grounded-pixel-actual-grant-root-r1.json','grounded-pixel-actual-root-observations-r1.json','starter-family-master-inspection-root-r1.json','starter-family-master-inspect-root-r1.py','starter-family-alpha-diagnostic-grant-root-r1.json','starter-family-alpha-diagnostic-launch-root-r1.py','opening-cue-checkpoint-push-root-r1.py','opening-cue-checkpoint-push-receipt-root-r1.json']
for name in singleton:add(S/name,'Root grants grammar terminal derivatives and prior confirmed push')
reviewPins={'opening-turn-payoff-wording-actual-gameplay-independent-r2':'cbfcbc0e082c17b663d3bb1fac3f7a415505e0aeb7ca664814ebea36e3cccc52','opening-turn-payoff-wording-actual-visual-independent-r1':'cae95281a0aef122085edb29e68b6e88ff7571d69333ad3c8fdd7162fc9f1e17','opening-turn-payoff-wording-actual-technical-independent-r1':'83eab5f5ed24dfe7d5bf7ae353ce44f20d716493b106175ef119aae79cc19e3e','coherent-native128-fallen-ground-actual-technical-independent-r1':'274b9a998c21806d2cce59fae67c064415dbe214a0302f2fe4f310b19cacb8ce','coherent-native128-fallen-ground-actual-visual-independent-r1':'e25481e9e67146aef7afc13fca212ff3e06f8fe47446f06710a387ce4ca995a9','coherent-native128-fallen-ground-gameplay-independent-r1':'406675d4793c3f679a73095d8367dc3d2894f2f88f390ebe76563df60b4b3332','native128-defeat-aftermath-source-independent-r1':'492084ab8e5adfccf9d17749ea55ed6d10aea8edd016c388f0f989571497cc05'}
gates=[]
for name,h in reviewPins.items():
 path=S/name/'GATE.json';assert digest(path)[0]==h;gates.append({'path':str(path),'sha256':h,'decision':j(path)['decision']})
metadata=[]
for rel in ['AGENTS.md','docs/CONTINUATION.md','docs/PRODUCTION.md','docs/FIRST-FIVE-MINUTES.md']:
 path=R/rel;add(path,'prior pushed d144 metadata snapshot not new-actual status');h,n=digest(path);metadata.append({'path':str(path),'sha256':h,'bytes':n,'RootHoldThroughActualArchiveAndCompleteReview':True})
master=j(S/'starter-family-master-inspection-root-r1.json');assert master['sha256']=='4a08d967ad5752e2ffa71f6370af4debd52dc75419d9ae7a40d8ca0c9f5fbbb4';add(master['path'],'new unimplemented generated starter master negative alpha prototype input',master['sha256']);assert not (S/'starter-family-native128-alpha-diagnostic-root-r1').exists()
authorities=[];dependencies=[]
freezes=[S/'opening-turn-payoff-wording-strict-build-root-r1/final-seal-r1/RUNTIME-FREEZE.json',S/'coherent-native128-fallen-ground-strict-build-root-r1/final-seal-r1/RUNTIME-FREEZE.json',S/'target-clear-default-build-author-r1/RUNTIME-FREEZE.json']
for path in freezes:
 add(path,'exact full candidate and selected rollback runtime maps');f=j(path);base=pathlib.Path(f['stage']);authorities.append({'freezePath':str(path),'freezeSHA256':digest(path)[0],'stage':str(base),'sourceDigest':f['sourceDigest'],'outputsDigest':f['outputsDigest'],'inputCount':len(f['inputs']),'outputCount':len(f['outputs']),'selection':'candidate unselected' if len(authorities)<2 else 'current selected c4 rollback'})
 for field,m in [('inputs',f['inputs']),('outputs',f['outputs'])]:
  assert sha(json.dumps(m,sort_keys=True,separators=(',',':')).encode())==f['sourceDigest' if field=='inputs' else 'outputsDigest']
  for rel,h in m.items():
   q=base/rel if field=='inputs' else base/'dist'/rel
   if q.suffix.lower() in {'.png','.wav','.ogg','.mp3','.jpg','.webp'}:
    assert q.is_file();dependencies.append([idx(roots,str(q.parent)),q.name,h,idx(roles,'held game media dependency body excluded')]);continue
   add(q,'exact runtime code/support or rollback reference',h)
 assert len(f['inputs']) in [88,89,98] and len(f['outputs']) in [56,64]
rollback=j(freezes[-1]);rollbackCode=[]
for rel,h in rollback['outputs'].items():
 if rel.startswith(('art/','audio/')):continue
 q=R/'dist'/rel;add(q,'old five canonical code outputs physical retention required',h);h,n=digest(q);rollbackCode.append({'path':str(q),'sha256':h,'bytes':n,'storage':rows[seen[str(q)]][5]})
assert len(rollbackCode)==5
for rel,h in rollback['inputs'].items():
 if pathlib.Path(rel).suffix.lower() not in {'.png','.wav','.ogg','.mp3','.jpg','.webp'}:add(R/rel,'current selected canonical code baseline',h)
assert not (R/'src/opening-turn-payoff.css').exists()
controls=[];comparisons=[];nestedGzip=[]
for name,labels in [('opening-turn-payoff-wording-actual-comparison-root-r1',['C0','C1','C2','C-cancelled','C-released','C-endTurn']),('coherent-native128-fallen-ground-comparison-actual-r1',['C0','C1','C2','C-firstDrop','C-normalized','C-secondOutcome'])]:
 d=S/name;b=j(d/'BYTE-AUDIT-before.json');a=j(d/'BYTE-AUDIT-after.json');assert b['controls']==a['controls'] and len(b['controls'])==40;scopeControls=[]
 for row in b['controls']:
  path=pathlib.Path(row['root'])/row['name'];add(path,'exact forty actual caller controls per actual',row['sha256']);scopeControls.append({'path':str(path),'sha256':row['sha256'],'bytes':row['bytes']})
 controls.append({'actualRoot':str(d),'count':40,'bodyIdentityAuthority':'Complete original before/after40-control bodies and manifests in logical rows','controls':scopeControls})
 pairs=[]
 for label in labels:
  prefix='cue' if name.startswith('opening') else 'hold-release';raw=[]
  for side in 'AB':raw.append(j(d/(side+'-'+prefix+'-'+label+'-OPAQUE-SAVE.json'))['raw'].encode('utf-8'))
  assert raw[0]==raw[1];pairs.append({'label':label,'rawSHA256':sha(raw[0]),'rawBytes':len(raw[0])})
 assert len(list(d.glob('*.jpg')))==8;comparisons.append({'originalRoot':str(d),'originalJPEGCount':8,'sixCompleteRawPairs':pairs,'opaqueWrapperHashesAreSeparateDomain':True})
 if (d/'EVIDENCE-FORMAT.json').exists():
  fmt=j(d/'EVIDENCE-FORMAT.json')
  for logical,row in fmt['files'].items():
   assert digest(d/row['storedLeaf'])==(row['storedSHA256'],row['storedBytes']);hh=hashlib.sha256();n=0;f,q=op(d/row['storedLeaf'])
   with f,gzip.GzipFile(fileobj=f) as decoded:
    while x:=decoded.read(32768):hh.update(x);n+=len(x)
   assert (hh.hexdigest(),n)==(row['originalSHA256'],row['originalBytes']);nestedGzip.append({'root':str(d),'logicalLeaf':logical,**row,'sourcePhaseFullLogicalSHAAndLengthVerified':True})
unique={}
for ri,rel,h,n,role,storage in rows:
 if storage=='newBlob':unique.setdefault(h,(pathlib.Path(roots[ri])/rel,n))
estimate=0
for h,(path,n) in unique.items():
 encoder=zlib.compressobj(6,zlib.DEFLATED,31);decoder=zlib.decompressobj(31);original=hashlib.sha256();decoded=hashlib.sha256();encodedN=0;decodedN=0;f,q=op(path)
 with f:
  while b:=f.read(32768):
   original.update(b);z=encoder.compress(b);encodedN+=len(z);plain=decoder.decompress(z);decoded.update(plain);decodedN+=len(plain)
  z=encoder.flush();encodedN+=len(z);plain=decoder.decompress(z)+decoder.flush();decoded.update(plain);decodedN+=len(plain)
 assert decoder.eof and decodedN==n and original.hexdigest()==decoded.hexdigest()==h;estimate+=encodedN
method=(P/'preserve-checkpoint.py').read_bytes();ast.parse(method);inverse=j(P/'METHOD-INVERSE.json');assert sha(method)==inverse['methodSHA256']
oldmethod=method.decode()
for entry in reversed(inverse['changes']):assert oldmethod.count(entry['after'])==1;oldmethod=oldmethod.replace(entry['after'],entry['before'])
assert sha(oldmethod.encode())==inverse['predecessorSHA256']
plan={'status':'FINAL_SOURCE_PLAN_REQUIRES_ROOT_ARCHIVE_GRANT','scope':'Exact complete new clearer-wording actual and separate rejected/qualified grounded-pixel actual with immutable failed source/review/control/provenance history. Archive-only; clearer cue selection deferred. Optional new unimplemented master/negative alpha and rejected expiry prototype preserved separately; fresh mutable fix excluded.','roots':roots,'roles':roles,'rowColumns':['rootIndex','relativeLeaf','sha256','originalBytes','roleIndex','storage'],'rows':rows,'existingCapsules':capsules,'existingReferenceRule':'storage existingCapsule:ID means blobs/<row SHA> in exact ID archive; required pinned INDEX plus previous COMPLETE gate; all original logical names remain explicit.','runtimeAuthorities':authorities,'actualComparisons':comparisons,'nestedLogicalGzipDomains':nestedGzip,'originalReviewGatesVerbatim':gates,'scopeRootInventory':scopeFolders,'exactActualControls':controls,'metadataSnapshot':{'status':'Prior pushed d144 metadata; not claiming new actuals reflected','reportedConfirmedHead':'d144368d04b5af55abc7c81927417eb88ee47e16','docs':metadata,'mustRemainUnchangedThroughArchiveAndCompleteReview':True},'externalDependencies':{'gameMediaColumns':['rootIndex','relativeLeaf','sha256','roleIndex'],'gameMediaRows':dependencies,'gameMediaBodyReadOrCopiedByMapWalk':False,'historicalMasters':historicalMasters,'nodeModules':{'path':str(R/'node_modules'),'bodyExcluded':True,'authority':'Exact package-lock.json in full frozen maps; installed tree external'},'selfContainedRelease':False,'uniqueNewNativeOutputAndCourtyardSourcePackagesIncludedInLogicalRows':True,'allOldOriginalPathsRetained':True},'optionalInputDomains':{'starterMaster':{'path':master['path'],'sha256':master['sha256'],'bytes':master['bytes'],'implementationAccepted':False,'qualityAccepted':False,'alphaDiagnostic':'Original guard exit2/zero output; named attempted output absent; silhouette touches border error retained'},'rejectedExpiryPrototypeGateSHA256':reviewPins['native128-defeat-aftermath-source-independent-r1'],'rejectedExpiryPrototypeActualRun':False,'mutableSuccessorIncluded':False},'futureSelectionContract':{'archiveHelperPublishesOrSelects':False,'noPublisherAuthored':True,'requiresCompletePreservationIndependentReviewThenRootJudgmentAndConfirmedCurrentPush':True,'optionalLaterCanonicalSourceChangesOnly':['src/main.ts','src/opening-turn-payoff.css'],'oldMainSHA256':rollback['inputs']['src/main.ts'],'oldCueCSSCurrentlyAbsent':True,'candidateMainSHA256':j(freezes[0])['inputs']['src/main.ts'],'candidateCueCSSSHA256':j(freezes[0])['inputs']['src/opening-turn-payoff.css'],'oldFiveDistCodeBodies':rollbackCode,'oldDistSourceAndOutputRemainPhysical':True,'canonicalDistReplacementNotAuthorizedHere':True,'candidate89SourcesAnd56BuiltOutputsBoundByFreeze':True,'holding51SharedOldMediaNoOverwrite':True,'noRemovalTagVersionPlatformFunClaim':True},'proposedArchive':{'workMiB':128,'reserveMiB':512,'diskMinimumMiB':64,'physicalOutputCapBytes':16*1048576,'logicalOutputCapBytes':16*1048576,'ownRSSCapBytes':24*1048576,'methodWholeCeilingSeconds':60,'freshFreeDiskMinimumBytes':17*1048576,'newUniqueBodyCount':len(unique),'newUniqueOriginalBytes':sum(n for p,n in unique.values()),'perBodyGzipSumEstimateBytes':estimate,'estimateQualification':'Memory-only full-original gzip/readback estimate excludes TAR/index/receipt overhead. Actual archive/full readback/terminal output cap needs separate Root grant and independent COMPLETE review.'},'publicationPlan':{'candidateDestination':str(R/'reviews/wording-grounded-trials-2026-10-02'),'rootMayPublishOnlyAfterActualIndependentCompleteReview':True,'requiredSiblingSupport':['full immutable source author packet','future independent SOURCE review packet','Root archive grant/guard/terminal stdout','future independent COMPLETE preservation review'],'noOriginalRemovalOverwriteOrRuntimeWrites':True,'noCanonicalArchiveCopyAuthorizedInSourcePhase':True},'sourceReadQualifications':{'originalBodiesNOATIMERequested':True,'permissionFallbackPaths':fallbacks,'standardJSONMetadataIndexReadsMayAdvanceAtime':True,'fullStatXattrPreservationClaimed':False,'existingArchiveBodiesHashedCompressedOnlyNoExtraction':True,'protectedZIPBodyRead':False}}
blob=(json.dumps(plan,separators=(',',':'))+'\n').encode();current=sum(x.stat().st_size for x in P.rglob('*') if x.is_file());assert current+len(blob)+32768<=256*1024,(current,len(blob),'STOP_BEFORE_PLAN_WRITE_NEEDS_ROOT_ALLOCATION')
rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss;assert rss<=24576
(P/'PLAN.json').write_bytes(blob)
proof={'status':'SOURCE_ONLY_NO_ARCHIVE_EXECUTION','planSHA256':sha(blob),'planBytes':len(blob),'helperSHA256':sha(method),'exactFullHelperInverse':True,'logicalRows':len(rows),'newUniqueBodies':len(unique),'newUniqueOriginalBytes':sum(n for p,n in unique.values()),'gzipEstimateBytes':estimate,'storageOccurrences':dict(collections.Counter(x[5] for x in rows)),'scopeFolderCount':sum(map(len,scopeFolders.values())),'twoActualJPEGCount':16,'sixRawPairsPerActual':True,'both40ControlsPreserved':True,'allOriginalGateDecisionsPreserved':gates,'optionalNegativeInputAndExpiryPrototypeIncluded':True,'allMetadataFrozenPriorPushed':True,'ownRSSKiB':rss,'sourceFamilyCapBytes':256*1024,'archiveOrPublisherExecuted':False}
(P/'SOURCE-PROOF.json').write_text(json.dumps(proof,indent=2)+'\n')
print(json.dumps({k:v for k,v in proof.items() if k not in ['allOriginalGateDecisionsPreserved']},separators=(',',':')))
