import os,stat,json,hashlib,tarfile,gzip,resource,time
from pathlib import Path
P=Path(__file__).parent;S=Path('/workspace/scratch');A=S/'native-aftermath-starter-checkpoint-source-author-r1';C=Path('/workspace/Roguelike-deckbuilder/reviews/opening-native-aftermath-and-starter-art-2026-10-02/archive');beg=time.monotonic();pins={}
def opened(p):
 fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME);assert stat.S_ISREG(os.fstat(fd).st_mode);return os.fdopen(fd,'rb')
def sha(p):
 h=hashlib.sha256()
 with opened(p) as f:
  while b:=f.read(65536):h.update(b)
 return h.hexdigest()
def read(p):
 with opened(p) as f:return f.read()
def load(p,h=None):
 p=Path(p);actual=sha(p);assert h is None or h==actual,str(p);pins[str(p)]=actual;return json.loads(read(p))
manifestSHA='91c82de1139c861da723ad8ec5208eac3791da16a6e67d32659865584b01ddc3';archiveSHA='8cdf546a8429e949fe88611d781aca341566f473135fbcbe44b5373beabd7aa8'
m=load(C/'ROOT-FINAL-INPUT-MANIFEST.json',manifestSHA);assert read(C/'ROOT-FINAL-INPUT-MANIFEST.json')==read(S/'native-checkpoint-final-input-manifest-root-r3.json')
idx=load(C/'INDEX.json','a7b01a97c4185ebd9f82faf084e8f3145ff4bdb40e2b0034f0590269eaa9000f')
for key in ['roots','rows','rowColumns','roles','runtimeAuthorities','existingCapsules','externalDependencies']:assert idx[key]==m[key],key
assert idx['format']=='original-path-sha256-blobs-v1' and idx['allOriginalPathsRetained'] and idx['fullUniqueOriginalByteRoundtrip'] and idx['selfContainedRelease'] is False
arc=C/('evidence-'+archiveSHA+'.tar.gz');assert idx['newArchive']=={'path':str(arc),'sha256':archiveSHA,'bytes':5085419} and arc.stat().st_size==5085419 and sha(arc)==archiveSHA
grant=load(C/'ROOT-ARCHIVE-GRANT.json','3e2a148546534eeecbd8dc8d8595cddca10aa0cbeb28a9303d3510f5293604e2');assert read(C/'ROOT-ARCHIVE-GRANT.json')==read(S/'native-checkpoint-archive-grant-root-r1.json')
for field in ['authorized','archiveOnly','soleCanonicalArchiveWriterConfirmed','allIncludedInputRootsClosedConfirmed','ordinary128Plus512GuardConfirmed','RootVerifiedExactMethodSourceEligibility','RootVerifiedFreshCurrentCleanPush']:assert grant[field] is True
assert grant['currentHEAD']==grant['freshRemoteHEAD']=='06007e0d81298fa49cedeb46719d03cae9fba04c'
sg=load(grant['independentSourceGate']['path'],grant['independentSourceGate']['sha256']);assert grant['independentSourceGate']['sha256']=='698daceaa2775a0934f825fdf20020050937cf7d2450cf962fe7114a8485fd97' and sg['sourceEngineeringEligible']
mg=load(grant['independentRootManifestGate']['path'],grant['independentRootManifestGate']['sha256']);assert grant['independentRootManifestGate']['sha256']=='ea90c86b77554a5da0a848f99d132291b47e43abd9452923f49f10b75937f46f' and mg['accepted'] and mg['inputManifestSHA256']==manifestSHA
assert grant['methodSHA256']==sg['methodSHA256']==sha(A/'preserve-direct-final.py')=='5ad10c515b362ac6434ad6041565a13d74551f53e658c1f65c5ab4a08c10dd0f'
assert sha(A/'preserve-direct-r2.py')==sg['implementationSHA256']=='9818bfbbb52ff3f4ad173c6c29071c77531011c95bda404f61636f9b3fad0568'
patch=load(grant['sourceSpec']['path'],grant['sourceSpec']['sha256']);assert grant['sourceSpec']['sha256']==sg['specSHA256']==m['sourceSpecSHA256']=='13d1c918f57c103929e098a03ce90ba7574161e1e0ae75e598960812e7ec6e0f'
spec=load(patch['inherits']['path'],patch['inherits']['sha256']);spec.update(patch['updates'])
for k,x in [('requiredRoots','appendRequiredRoots'),('fixedSingleFiles','appendFixedSingleFiles'),('requiredControlPins','appendControlPins')]:spec[k]+=patch[x]
assert m['runtimeAuthorities']==spec['runtimeAuthorities'] and m['existingCapsules']==spec['existingCapsules'] and len(m['futurePhaseStates'])==6 and set(m['futurePhaseStates'].values())=={'CLOSED_INCLUDED'}
assert grant['finalInputManifest']=={'path':str(S/'native-checkpoint-final-input-manifest-root-r3.json'),'sha256':manifestSHA}
push=load(grant['confirmedPush']['path'],grant['confirmedPush']['sha256']);assert push['confirmedPush'] and push['clean'] and push['head']==push['remote']==grant['currentHEAD']
roots=idx['roots'];rows=idx['rows'];assert len(roots)==141 and len(rows)==1278
names={};unique={};inherited=0
for i,rel,h,n,role,storage in rows:
 assert type(i)==int and 0<=i<len(roots) and not Path(rel).is_absolute() and '..' not in Path(rel).parts
 q=Path(roots[i])/rel;assert str(q) not in names;names[str(q)]=(h,n,storage);assert q.is_file() and not q.is_symlink() and q.stat().st_size==n
 if storage=='newBlob':
  if h in unique:assert unique[h][1]==n
  else:unique[h]=(q,n)
 else:assert storage=='existing:4513';inherited+=1
assert len(unique)==1116
old=m['existingCapsules'][0];oldstat=Path(old['archive']['path']).lstat();assert stat.S_ISREG(oldstat.st_mode) and oldstat.st_size==old['archive']['bytes']
oldidx=load(old['index']['path'],old['index']['sha256']);oldgate=load(old['complete']['path'],old['complete']['sha256']);assert oldidx['newArchive']['sha256']==old['archive']['sha256']
prior={(str(Path(oldidx['roots'][r[0]])/r[1]),r[2],r[3]) for r in oldidx['rows']};del oldidx
for q,(h,n,storage) in names.items():assert (storage=='existing:4513')==((q,h,n) in prior)
seen=set();bytecount=0;atimechanges=0
with opened(arc) as f:
 with tarfile.open(fileobj=f,mode='r|gz',bufsize=65536) as tar:
  for member in tar:
   assert member.isfile() and member.name.startswith('blobs/') and not member.pax_headers
   h=member.name[6:];assert h in unique and h not in seen and member.size==unique[h][1] and member.mode==0o444 and member.mtime==0
   body=tar.extractfile(member);digest=hashlib.sha256();size=0
   with opened(unique[h][0]) as original:
    before=os.fstat(original.fileno())
    while b:=body.read(65536):
     assert original.read(len(b))==b,'Full original literal comparison mismatch';digest.update(b);size+=len(b)
    assert original.read(1)==b'';after=os.fstat(original.fileno())
    assert (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns)
    atimechanges+=before.st_atime_ns!=after.st_atime_ns
   assert size==member.size and digest.hexdigest()==h;seen.add(h);bytecount+=size
assert seen==set(unique) and Path(old['archive']['path']).lstat()==oldstat
obs=load(C/'READ-OBSERVATIONS.json','febf7ef93ed6a821c8361265f53d3999b9135ab71771840343d9ebcc85be8d99');assert len(obs)==1+2*1116
first={x['sha256']:x for x in obs[1:] if 'sha256' in x};again={x['originalPath'] for x in obs[1:] if x.get('scope')=='full decoded original-byte equality readback'}
assert set(first)==set(unique) and again=={str(q) for q,n in unique.values()}
for h,(q,n) in unique.items():assert first[h]['originalPath']==str(q) and first[h]['bytes']==n and first[h]['checkedInodeSizeMtimeStableAtimeQualified'] and first[h]['timestampResetPerformed'] is False
fallbacks=sum(x.get('permissionFallback',False) for x in obs);del obs
runtime=[]
for authority in m['runtimeAuthorities']:
 freeze=load(authority['freeze']['path'],authority['freeze']['sha256']);assert freeze['sourceDigest']==authority['sourceDigest'] and freeze['outputsDigest']==authority['outputsDigest'] and [freeze['inputCount'],freeze['outputCount']]==authority['mappedCounts']==[98,64]
 mapped={**freeze['inputs'],**{'dist/'+k:v for k,v in freeze['outputs'].items()}};code={k:h for k,h in mapped.items() if not any(x in k for x in ['public/art/','public/audio/','dist/art/','dist/audio/']) and k!='desktop/icon.png'}
 assert len(code)==43 and sorted(code)==m['runtimeCodeAllowedRelativePaths'][authority['stage']]
 for rel,h in code.items():assert names[str(Path(authority['stage'])/rel)][0]==h
 runtime.append({'stage':authority['stage'],'freezeSHA256':authority['freeze']['sha256'],'codeRows':43})
evidence=[];sixgates=[];fullpairs=0;originalshots=0;gzipdomains=0
for leaf in ['native128-defeat-aftermath-comparison-actual-r2','native128-floor-perspective-comparison-actual-r1']:
 q=S/leaf;shots=sorted(q.glob('*.jpg'));assert len(shots)==4
 for z in shots:assert str(z) in names
 pairfacts=[]
 for checkpoint in ['C0','C1','C2','C-normalized','C-firstDrop','C-secondOutcome']:
  pair=[load(q/(prefix+'-hold-release-'+checkpoint+'-OPAQUE-SAVE.json')) for prefix in ['A','B']]
  for prefix,state in zip(['A','B'],pair):
   z=q/(prefix+'-hold-release-'+checkpoint+'-OPAQUE-SAVE.json');assert str(z) in names and state['observedOnly'] is True and isinstance(state['raw'],str) and len(state['raw'])>500
   decoded=json.loads(state['raw']);assert decoded['schema']==3 and decoded['engineKind']==2 and decoded['seed']==937240
  pairfacts.append({'checkpoint':checkpoint,'fullRawPairEqual':pair[0]['raw']==pair[1]['raw'],'rawBytes':len(pair[0]['raw'].encode())});fullpairs+=1
 fmt=load(q/'EVIDENCE-FORMAT.json');assert len(fmt['files'])==2
 for logical,meta in fmt['files'].items():
  z=q/meta['storedLeaf'];assert str(z) in names and sha(z)==meta['storedSHA256'] and z.stat().st_size==meta['storedBytes'] and meta['fullOriginalByteReadbackVerified']
  h=hashlib.sha256();n=0
  with opened(z) as compressed:
   with gzip.GzipFile(fileobj=compressed,mode='rb') as decoded:
    while b:=decoded.read(65536):h.update(b);n+=len(b)
  assert h.hexdigest()==meta['originalSHA256'] and n==meta['originalBytes'];gzipdomains+=1
 originalshots+=len(shots);evidence.append({'root':str(q),'originalJPEGs':4,'fullSavedPairs':pairfacts,'fullLosslessGzipDomains':2,'newVisualDecodeOrGameplayRun':False})
reviewroots=['native128-defeat-aftermath-actual-technical-independent-r2','native128-defeat-aftermath-actual-visual-independent-r1','native128-defeat-aftermath-actual-gameplay-independent-r2','native128-floor-perspective-actual-technical-independent-r1','native128-floor-perspective-actual-visual-independent-r1','native128-floor-perspective-actual-gameplay-independent-r1']
for leaf in reviewroots:
 z=S/leaf/'GATE.json';assert str(z) in names;gate=load(z);sixgates.append({'path':str(z),'sha256':names[str(z)][0],'decision':gate.get('decision')})
artgates=[]
for leaf in ['starter-family-native128-assets-visual-independent-r3','ash-widow-correction-native128-native-visual-independent-r2']:
 z=S/leaf/'GATE.json';assert str(z) in names;gate=load(z);artgates.append({'path':str(z),'sha256':names[str(z)][0],'decision':gate.get('decision'),'accepted':gate.get('accepted')})
assert originalshots==8 and fullpairs==12 and gzipdomains==4
for c in spec['requiredControlPins']:assert names[c['path']][:2]==(c['sha256'],c['bytes'])
guard=S/'native-checkpoint-archive-guard-root-r1';g=load(guard/'RESULT.json');ad=load(guard/'ADMISSION.json');terminal=json.loads(read(guard/'EXECUTION.log'));pins[str(guard/'EXECUTION.log')]=sha(guard/'EXECUTION.log')
assert g['exit_code']==0 and g['failure'] is None and g['memory_events_before']==g['memory_events_after'] and len(g['samples'])==12
assert ad['admitted'] and ad['work']==128*1048576 and ad['reserve']==512*1048576 and ad['initial']['free']>=76*1048576
assert ad['command']==['python3','-B',str(A/'preserve-direct-final.py'),str(S/'native-checkpoint-archive-grant-root-r1.json'),'3e2a148546534eeecbd8dc8d8595cddca10aa0cbeb28a9303d3510f5293604e2']
assert all(r['headroom']>=512*1048576 and r['delta']<=128*1048576 for r in g['samples'])
assert terminal['archiveSHA256']==archiveSHA and terminal['logicalBodies']==1278 and terminal['newUniqueBodies']==1116 and terminal['planSHA256']==manifestSHA
assert terminal['indexSHA256']==pins[str(C/'INDEX.json')] and terminal['readObservationsSHA256']==pins[str(C/'READ-OBSERVATIONS.json')]
result=load(C/'RESULT.json');assert all(terminal[k]==v for k,v in result.items())
assert terminal['terminalElapsedAfterAllWrites']==1.1194373439939227 and terminal['terminalElapsedAfterAllWrites']<60 and terminal['terminalOwnMaxRSSBytesAfterAllWrites']<=24576*1024
leaves={p.name for p in C.iterdir()};assert leaves=={'ROOT-FINAL-INPUT-MANIFEST.json','ROOT-ARCHIVE-GRANT.json','INDEX.json','READ-OBSERVATIONS.json','README.md','RESULT.json',arc.name}
assert all(z.is_file() and not z.is_symlink() for z in C.iterdir())
logical=sum(z.stat().st_size for z in C.iterdir());allocated=sum(z.stat().st_blocks*512 for z in C.iterdir());assert logical==terminal['terminalLogicalOutputBytesAfterAllWrites']==6292888 and allocated==terminal['terminalAllocatedOutputBytesAfterAllWrites']==6311936
outerlogical=sum(z.stat().st_size for z in guard.iterdir());outerallocated=sum(z.stat().st_blocks*512 for z in guard.iterdir());assert logical+outerlogical<12*1048576 and allocated+outerallocated<12*1048576
assert not (C/'FAILURE.json').exists() and not (C/'evidence.partial.tar.gz').exists()
assert resource.getrusage(resource.RUSAGE_SELF).ru_maxrss<=24576
out={'decision':'ACCEPT_COMPLETE_EXACT_NATIVE_AFTERMATH_AND_STARTER_CHECKPOINT_PRESERVATION_ONLY','archiveSHA256':archiveSHA,'archiveBytes':5085419,'logicalRows':1278,'newUniqueBodies':1116,'fullNewUniqueOriginalLiteralByteEquality':True,'newUniqueDecodedBytesCompared':bytecount,'inheritedLogicalRows':inherited,'runtimeCodeRows':86,'runtime':runtime,'eightOriginalJPEGsPreserved':True,'twelveFullSavedPairsPreserved':True,'fourGzipOriginalDomainsFullyDecodedHashed':True,'actualEvidence':evidence,'sixOriginalActualReviewGates':sixgates,'nativeArtGatesRetainedWithoutNewApproval':artgates,'allOriginalFailuresScope':'Complete exact R3 tree memberships inherited from earlier independent Source audit; all listed failure bodies retained in exact archive mappings. No new all-workspace completeness claim.','sourceAuditVsActual':'Earlier Source audit independently hashed every1278 logical row. This actual review renews1116 representative new unique originals by literal byte equality, stats all rows, matches archive index exactly, verifies12 full raw pairs and4 gzip domains. Other duplicate paths/inherited bodies not all rehashed again.','priorArchive':'Exact4513 index/COMPLETE inherited; old archive STAT only, body never opened.','mediaExternal':'Unchanged frozen media and installed dependencies remain explicit external map/catalogue/support/package-metadata pins; preceding Source audit independently checked230 literal alias chains/support60/toolmetadata8; no media byte/decode rerun or dependency Merkle here.','rootGuardNormal':True,'rootMinimumHeadroom':min(r['headroom'] for r in g['samples']),'rootOwnRSSBytes':terminal['terminalOwnMaxRSSBytesAfterAllWrites'],'archiveLogicalBytes':logical,'archiveAllocatedBytes':allocated,'outerGuardLogicalBytes':outerlogical,'outerGuardAllocatedBytes':outerallocated,'readAtimeChangesObserved':atimechanges,'rootNoAtimePermissionFallbacks':fallbacks,'metadataQualification':'O_NOATIME requested; measured inode/size/mtime stable for new unique readbacks; no whole stat/xattr rollback claim.','roleDisclosure':'Reviewer authored older converter/witness/helper work and the independent Root manifest audit, not different-author preserver. Actual archive data verification is separate; no creative/algorithm/art/game/default/fun approval.','noActualRunOrMutation':True,'ownMaxRSSKiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'elapsedSeconds':time.monotonic()-beg,'pins':pins}
(P/'AUDIT.json').open('x').write(json.dumps(out,separators=(',',':'))+'\n');print(json.dumps({k:out[k] for k in ['decision','logicalRows','newUniqueBodies','newUniqueDecodedBytesCompared','inheritedLogicalRows','ownMaxRSSKiB','elapsedSeconds']}))
