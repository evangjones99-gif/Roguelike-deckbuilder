import os,json,hashlib,resource,stat,ast,re,time
from pathlib import Path,PurePosixPath
P=Path(__file__).parent; A=Path('/workspace/scratch/wording-grounded-trials-checkpoint-source-author-r1')
started=time.monotonic()
def read(p):
 fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME)
 try:
  a=os.fstat(fd);assert stat.S_ISREG(a.st_mode)
  b=b''.join(iter(lambda:os.read(fd,65536),b''));assert a==os.fstat(fd);return b
 finally:os.close(fd)
def sha(p):return hashlib.sha256(read(p)).hexdigest()
def load(p):return json.loads(read(p))
j=load(A/'PLAN.json'); m=load(A/'MANIFEST.json'); inv=load(A/'METHOD-INVERSE.json')
for x in m['bodies']:assert len(read(A/x['name']))==x['bytes'] and sha(A/x['name'])==x['sha256']
for key,name in [('methodInverseSHA256','METHOD-INVERSE.json'),('proofSHA256','SOURCE-PROOF.json')]:assert sha(A/name)==m[key]
current=read(A/'preserve-checkpoint.py').decode();ast.parse(current)
base=read(Path(inv['predecessorPath'])).decode();assert hashlib.sha256(base.encode()).hexdigest()==inv['predecessorSHA256']
forward=base;inverse=current
for x in inv['changes']:
 assert forward.count(x['before'])==1 and inverse.count(x['after'])==1
 forward=forward.replace(x['before'],x['after']);inverse=inverse.replace(x['after'],x['before'])
assert forward==current and inverse==base
support=m['baselineRequiredPublishedSupport'];assert sha(Path(support['path']))==support['sha256']==inv['predecessorSHA256']
prior={};indexPins=[]
for c in j['existingCapsules']:
 idx=Path(c['index']['path']);assert sha(idx)==c['index']['sha256'];z=load(idx)
 if 'logicalBodies' in z: members={(x['sha256'],x['bytes']) for x in z['logicalBodies']}
 else:members={(x[2],x[3]) for x in z['rows'] if x[5]=='newBlob'}
 prior['existingCapsule:'+c['id']]=members;indexPins.append({'id':c['id'],'indexSHA256':c['index']['sha256'],'referencedMembers':len(members),'completeGateSHA256':c['completeGateSHA256'],'compressedArchiveBodyNotReread':True})
roots=j['roots'];roles=j['roles'];seen=set();unique={};counts={};total=0;paths={};media=[]
for root,rel,h,size,role,storage in j['rows']:
 assert isinstance(root,int) and 0<=root<len(roots) and isinstance(role,int) and 0<=role<len(roles)
 r=PurePosixPath(rel);assert rel and not r.is_absolute() and '..' not in r.parts and str(r)==rel and '\\' not in rel
 assert re.fullmatch('[0-9a-f]{64}',h) and isinstance(size,int) and size>=0
 rp=Path(roots[root]);assert rp.is_absolute() and str(rp).startswith('/workspace/')
 p=rp/rel;assert str(p) not in seen;seen.add(str(p));paths[str(p)]=(h,size,storage)
 counts[storage]=counts.get(storage,0)+1
 if storage=='newBlob':
  b=read(p);assert len(b)==size and hashlib.sha256(b).hexdigest()==h
  if h in unique:assert unique[h]==size
  unique[h]=size;total+=size
 else:assert storage in prior and (h,size) in prior[storage]
for x in j['metadataSnapshot']['docs']:assert sha(Path(x['path']))==x['sha256'] and len(read(Path(x['path'])))==x['bytes']
for x in j['originalReviewGatesVerbatim']:
 assert sha(Path(x['path']))==x['sha256'];assert load(Path(x['path']))['decision']==x['decision'];assert str(x['path']) in paths
for x in j['runtimeAuthorities']:assert sha(Path(x['freezePath']))==x['freezeSHA256']
for domain in j['actualComparisons']:
 ps=[p for p in paths if Path(p).parent==Path(domain['originalRoot']) and p.endswith('.jpg')];assert len(ps)==domain['originalJPEGCount']==8
 assert len(domain['sixCompleteRawPairs'])==6 and domain['opaqueWrapperHashesAreSeparateDomain']
for domain in j['exactActualControls']:
 assert domain['count']==len(domain['controls'])==40
 for x in domain['controls']:assert paths[x['path']][:2]==(x['sha256'],x['bytes'])
for x in j['nestedLogicalGzipDomains']:
 assert paths[str(Path(x['root'])/x['storedLeaf'])][:2]==(x['storedSHA256'],x['storedBytes'])
 assert x['fullOriginalByteReadbackVerified'] and x['sourcePhaseFullLogicalSHAAndLengthVerified']
assert len(unique)==j['proposedArchive']['newUniqueBodyCount']==711 and sum(unique.values())==j['proposedArchive']['newUniqueOriginalBytes']==14555377
assert j['proposedArchive']['workMiB']==128 and j['proposedArchive']['reserveMiB']==512 and j['proposedArchive']['diskMinimumMiB']==64
assert j['proposedArchive']['physicalOutputCapBytes']==j['proposedArchive']['logicalOutputCapBytes']==16777216
assert j['proposedArchive']['ownRSSCapBytes']==25165824 and j['proposedArchive']['methodWholeCeilingSeconds']==60
rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024;assert rss<25165824
out={'sourceOnly':True,'archiveExecuted':False,'planSHA256':sha(A/'PLAN.json'),'helperSHA256':sha(A/'preserve-checkpoint.py'),'fullFourReplacementInverse':True,'publishedBaselineExact':True,'all952SafeLogicalRowsChecked':len(seen)==952,'storageOccurrenceCounts':counts,'newUniqueBodyCount':len(unique),'newUniqueOriginalBytes':sum(unique.values()),'allNewBlobSourcesFullSHAAndLengthMatched':True,'priorIndexReferencesMatchedBySHAAndLength':True,'priorCapsules':indexPins,'priorCompleteProofInheritedNotReexecuted':True,'fourHeldDocsExact':True,'sevenOriginalDecisionBodiesExact':True,'threeFreezeBodiesExact':True,'twoActualsEightJPEGsEach':True,'bothFortyControlsMapped':True,'nestedStoredGzipBodiesExactLogicalDecodeNotRepeated':True,'futureRootProfileMiB':[128,512,64],'helperOwnRSSLimitBytes':25165824,'ownRSSBytes':rss,'elapsedSeconds':time.monotonic()-started,'currentParentDirectoriesNotOSLocked':True}
with (P/'SOURCE-CHECKS.json').open('x')as f:json.dump(out,f,indent=2,sort_keys=True);f.write('\n')
print(json.dumps({'checks':'PASS','rows':len(seen),'counts':counts,'newUnique':len(unique),'ownRSSBytes':rss,'elapsedSeconds':out['elapsedSeconds']},sort_keys=True))
