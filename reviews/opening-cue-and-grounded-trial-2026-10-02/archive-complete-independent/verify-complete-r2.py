import os,json,hashlib,stat,tarfile,re,resource,time,collections
from pathlib import Path,PurePosixPath
P=Path(__file__).parent;A=Path('/workspace/scratch/wording-grounded-trials-checkpoint-source-author-r1');O=Path('/workspace/scratch/wording-grounded-trials-checkpoint-output-root-r1');started=time.monotonic()
def opened(p):
 fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME);assert stat.S_ISREG(os.fstat(fd).st_mode);return os.fdopen(fd,'rb')
def sha(p):
 with opened(p)as f:
  before=os.fstat(f.fileno());h=hashlib.sha256();n=0
  while b:=f.read(65536):h.update(b);n+=len(b)
  assert before==os.fstat(f.fileno())
 return h.hexdigest(),n
def read(p):
 with opened(p)as f:return f.read()
def load(p):return json.loads(read(p))
def expect(p,h,n=None):
 got,size=sha(p);assert got==h and (n is None or n==size);return {'path':str(p),'sha256':got,'bytes':size}
plan=load(A/'PLAN.json');idx=load(O/'INDEX.json');result=load(O/'RESULT.json');obs=load(O/'READ-OBSERVATIONS.json')
expected={'INDEX.json':('64fe0a3ea9e523e6a63c9b7e60cd4ae3df8c88ef15cfba858a86187e21e98d58',157256),'READ-OBSERVATIONS.json':('e3b4a36b6c2c01b98d3fef9b7fa19711b2577ffdef4b51c5899284298faac142',401008),'RESULT.json':('b992737cecaebdf8c5b62a168607a25258608bcdec27c293844909bccecd6f36',588)}
pins=[expect(O/n,h,s)for n,(h,s)in expected.items()];expect(A/'PLAN.json','0998d948c57e2fb3d1e01f34e61028d5c80db299df308d3b1e83ab902d4281b7');expect(A/'preserve-checkpoint.py','5ee7a0a37946e3afcdf1d355cdfbc929ccf37b39edb1b4654e61e14250fb3f1a')
for k in ['roots','rows','roles','rowColumns','existingCapsules','externalDependencies','runtimeAuthorities']:assert idx[k]==plan[k]
assert idx['allOriginalPathsRetained'] and idx['fullUniqueOriginalByteRoundtrip'] and not idx['selfContainedRelease']
arc=idx['newArchive'];archive=Path(arc['path']);pins.append(expect(archive,'451347c174a3fe78e5f7b6ef22736b7cfbbd33b39fd04ea20556730bb3b15a8b',7848992));assert arc['sha256']==pins[-1]['sha256'] and arc['bytes']==7848992
prior={};priorpins=[]
for c in plan['existingCapsules']:
 for k in ['archive','index']:priorpins.append(expect(Path(c[k]['path']),c[k]['sha256']))
 v=load(Path(c['index']['path']))
 members={(x['sha256'],x['bytes'])for x in v['logicalBodies']}if 'logicalBodies'in v else {(x[2],x[3])for x in v['rows']if x[5]=='newBlob'}
 prior['existingCapsule:'+c['id']]=members
gatepaths=['/workspace/Roguelike-deckbuilder/reviews/coherent-native128-actual-trial-2026-10-02/preservation-independent/GATE.json','/workspace/Roguelike-deckbuilder/reviews/opening-turn-payoff-default-2026-10-02/preservation-independent/GATE.json']
for c,p in zip(plan['existingCapsules'],gatepaths):expect(Path(p),c['completeGateSHA256']);assert load(Path(p))['decision'].startswith('ACCEPT')
paths={};unique={};counts=collections.Counter();allsourcebytes=0
for root,rel,h,size,role,storage in idx['rows']:
 assert 0<=root<len(idx['roots']) and 0<=role<len(idx['roles']);r=PurePosixPath(rel)
 assert not r.is_absolute() and '..' not in r.parts and str(r)==rel and re.fullmatch('[0-9a-f]{64}',h)
 p=Path(idx['roots'][root])/rel;assert str(p)not in paths
 expect(p,h,size);paths[str(p)]=(h,size,storage);counts[storage]+=1;allsourcebytes+=size
 if storage=='newBlob':
  if h in unique:assert unique[h][1]==size
  else:unique[h]=(p,size)
 else:assert (h,size)in prior[storage]
seen=set();tarbytes=0
with opened(archive)as compressed:
 before=os.fstat(compressed.fileno())
 with tarfile.open(fileobj=compressed,mode='r|gz',bufsize=65536)as tf:
  for member in tf:
   assert member.isfile() and re.fullmatch('blobs/[0-9a-f]{64}',member.name) and member.name[6:] in unique
   h=member.name[6:];assert h not in seen;seen.add(h);original,size=unique[h];assert member.size==size and member.mode==0o444 and member.mtime==0
   with opened(original)as f:
    a=os.fstat(f.fileno());decoded=tf.extractfile(member);assert decoded is not None;hasher=hashlib.sha256();n=0
    while b:=decoded.read(65536):assert f.read(len(b))==b;hasher.update(b);n+=len(b)
    assert not f.read(1) and n==size and hasher.hexdigest()==h;assert a==os.fstat(f.fileno());tarbytes+=n
   assert time.monotonic()-started<45
 assert before==os.fstat(compressed.fileno())
assert seen==set(unique) and len(seen)==711 and tarbytes==14555377 and len(paths)==952
assert counts=={'newBlob':722,'existingCapsule:ce0f':227,'existingCapsule:f912':3}
assert len(obs)==4+711*2==1426 and all(x['noAtimeRequested'] and not x['permissionFallback'] for x in obs)
assert collections.Counter(x['originalPath']for x in obs[4:])==collections.Counter({str(p):2 for p,s in unique.values()})
for x in obs[4:]:
 assert x.get('checkedInodeSizeMtimeStableAtimeQualified') is True and x.get('fullStatXattrPreservationClaimed')is False
for x in plan['metadataSnapshot']['docs']:expect(Path(x['path']),x['sha256'],x['bytes'])
gates=[]
for x in plan['originalReviewGatesVerbatim']:
 expect(Path(x['path']),x['sha256']);assert load(Path(x['path']))['decision']==x['decision'];assert x['path']in paths;gates.append(x)
external={str(Path(plan['roots'][r])/rel):h for r,rel,h,role in plan['externalDependencies']['gameMediaRows']}
maps=[]
for x in plan['runtimeAuthorities']:
 expect(Path(x['freezePath']),x['freezeSHA256']);f=load(Path(x['freezePath']));assert f['sourceDigest']==x['sourceDigest'] and f['outputsDigest']==x['outputsDigest']
 assert len(f['inputs'])==x['inputCount']==f['inputCount'] and len(f['outputs'])==x['outputCount']==f['outputCount']
 extcount=0
 for key,base in [('inputs',Path(x['stage'])),('outputs',Path(x['stage'])/'dist')]:
  for rel,h in f[key].items():
   p=str(base/rel)
   if p in paths:assert paths[p][0]==h
   else:assert external.get(p)==h;extcount+=1
 maps.append({'stage':x['stage'],'sourceDigest':x['sourceDigest'],'outputsDigest':x['outputsDigest'],'inputs':x['inputCount'],'outputs':x['outputCount'],'externalPinnedMediaEntries':extcount})
for actual in plan['actualComparisons']:
 assert sum(Path(p).parent==Path(actual['originalRoot'])and p.endswith('.jpg')for p in paths)==8
 assert len(actual['sixCompleteRawPairs'])==6 and actual['opaqueWrapperHashesAreSeparateDomain']
for actual in plan['exactActualControls']:
 assert len(actual['controls'])==actual['count']==40
 for x in actual['controls']:assert paths[x['path']][:2]==(x['sha256'],x['bytes'])
guardpath=Path('/workspace/scratch/wording-grounded-trials-checkpoint-archive-guard-root-r1');guard=load(guardpath/'RESULT.json');terminal=load(guardpath/'EXECUTION.log');grantpath=Path('/workspace/scratch/wording-grounded-trials-checkpoint-archive-grant-root-r1.json');grant=load(grantpath)
assert guard['exit_code']==0 and guard['failure']is None and guard['memory_events_before']==guard['memory_events_after'] and len(guard['samples'])==6
assert grant['workMiB']==128 and grant['reserveMiB']==512 and grant['freshHeadroomBytes']>=640*1048576 and grant['freshFreeDiskBytes']>=64*1048576
expect(Path(grant['sourceGatePath']),grant['sourceGateSHA256']);assert grant['planSHA256']==result['planSHA256'] and grant['helperSHA256']=='5ee7a0a37946e3afcdf1d355cdfbc929ccf37b39edb1b4654e61e14250fb3f1a'
for k,v in result.items():assert terminal[k]==v
logical=sum(x.stat().st_size for x in O.iterdir()if x.is_file());allocated=sum(x.stat().st_blocks*512 for x in O.iterdir()if x.is_file())
assert logical==terminal['terminalLogicalOutputBytesAfterAllWrites']==8408132 and allocated==terminal['terminalAllocatedOutputBytesAfterAllWrites']==8421376 and max(logical,allocated)<16*1048576
assert terminal['terminalOwnMaxRSSBytesAfterAllWrites']==15855616<24*1048576 and terminal['terminalElapsedAfterAllWrites']<60
assert set(x.name for x in O.iterdir())=={'README.md','RESULT.json','INDEX.json','READ-OBSERVATIONS.json',archive.name}
rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024;assert rss<24*1048576
out={'decision':'PASS_COMPLETE_BYTE_AND_LOGICAL_PRESERVATION_CHECKS','sourceOnlyReview':True,'archiveCreatedByReviewer':False,'newArchiveAndReceipts':pins,'allLogicalOriginalPathsFullSHAAndLengthMatched':952,'allLogicalOriginalBytes':allsourcebytes,'storageOccurrenceCounts':dict(counts),'uniqueNewMembersFullDecodedByteCompare':711,'duplicateNewLogicalIdentities':722-711,'decodedNewOriginalBytes':tarbytes,'safeRegularSHA256MemberNamesOnly':True,'duplicateOrUnexpectedMembers':0,'priorCapsuleCompressedBodiesFreshFullSHA':priorpins,'prior230ReferenceRowsExactIndexesAndCurrentOriginalBodies':True,'priorDecodedByteReadbackInheritedFromExactAcceptedCompleteGates':True,'readObservationRows':len(obs),'rootNoAtimeFallback':False,'ownNoAtimeFallback':False,'ownAllOriginalReadFDStatsUnchanged':True,'fourHeldMetadataDocsExact':True,'sevenOriginalReviewDecisionsVerbatim':gates,'threeCompleteRuntimeMapBindings':maps,'twoActualsAll16OriginalJPEGsAndBoth40ControlsPreserved':True,'sixSavedStringPairDomainsEachRetainedNotReinterpretedAsWrapperSHA':True,'nestedLogicalGzipDomainDecodeInheritedWithStoredBodiesFreshSHA':True,'rootActualGuard':{'resultSHA256':sha(guardpath/'RESULT.json')[0],'terminalSHA256':sha(guardpath/'EXECUTION.log')[0],'exitCode':0,'samples':6,'minimumHeadroom':min(x['headroom']for x in guard['samples']),'eventsUnchanged':True,'childGroupClosureScope':guard['scope']},'rootGrant':expect(grantpath,sha(grantpath)[0]),'rootTerminalElapsed':terminal['terminalElapsedAfterAllWrites'],'rootTerminalOwnRSS':terminal['terminalOwnMaxRSSBytesAfterAllWrites'],'outputLogicalBytes':logical,'outputAllocatedBytes':allocated,'ownRSSBytes':rss,'reviewElapsedSeconds':time.monotonic()-started,'notSelfContainedRelease':True,'noSelectionPublicationCleanupAuthority':True,'parentDirectoriesWorkflowHeldNotOSRaceProof':True}
with(P/'COMPLETE-CHECKS.json').open('x')as f:json.dump(out,f,indent=2,sort_keys=True);f.write('\n')
print(json.dumps({'check':'PASS','logicalPaths':len(paths),'uniqueNewMembers':len(seen),'newLogicalDuplicates':11,'oldLogicalReferences':230,'ownRSSBytes':rss,'elapsedSeconds':out['reviewElapsedSeconds']}))
