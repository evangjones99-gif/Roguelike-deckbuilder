import gzip,hashlib,json,os,pathlib,resource,stat,tarfile
resource.setrlimit(resource.RLIMIT_DATA,(24*1048576,24*1048576))
S=pathlib.Path('/workspace/scratch');A=S/'pixel-cue-evidence-capsule-root-r1';H=S/'pixel-cue-evidence-preserver-source-author-r3';P=pathlib.Path(__file__).parent
PROTECTED='/workspace/scratch/retained-original-archives/';ZIP=pathlib.Path(PROTECTED+'preflight-bdf273-original-r4.zip')
def sm(s):return {k:getattr(s,'st_'+k) for k in ['dev','ino','mode','uid','gid','nlink','size','blocks','atime_ns','mtime_ns','ctime_ns']}
def nonat(x):return {k:v for k,v in x.items() if k!='atime_ns'}
def attrs(p):return {n:os.getxattr(p,n,follow_symlinks=False).hex() for n in os.listxattr(p,follow_symlinks=False)}
zipBefore=sm(ZIP.lstat());zipAttrs=attrs(ZIP)
def fdro(p):
 p=pathlib.Path(p);assert p.is_absolute() and '..' not in p.parts and not str(p).startswith(PROTECTED)
 parent=os.open('/',os.O_PATH|os.O_DIRECTORY)
 try:
  for part in p.parts[1:-1]:
   nxt=os.open(part,os.O_PATH|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=parent);os.close(parent);parent=nxt
  fd=os.open(p.name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME,dir_fd=parent)
 finally:os.close(parent)
 assert stat.S_ISREG(os.fstat(fd).st_mode);return fd
def hashfile(p):
 fd=fdro(p);h=hashlib.sha256();n=0
 try:
  s=sm(os.fstat(fd))
  while True:
   b=os.read(fd,32768)
   if not b:break
   h.update(b);n+=len(b)
  t=sm(os.fstat(fd));assert nonat(s)==nonat(t) and n==s['size']
 finally:os.close(fd)
 return {'sha256':h.hexdigest(),'bytes':n}
def small(p):
 fd=fdro(p)
 with os.fdopen(fd,'rb') as f:
  assert os.fstat(fd).st_size<=2*1048576;return f.read()
def load(p):return json.loads(small(p))
def encoded(x):return (json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode()
def inventory(root):
 root=pathlib.Path(root);assert root.is_dir() and not root.is_symlink();rows=[]
 for base,ds,fs in os.walk(root,followlinks=False):
  ds[:]=sorted(x for x in ds if x not in ['__pycache__','node_modules','.git'])
  for d in ds:assert not pathlib.Path(base,d).is_symlink()
  for name in sorted(fs):
   p=pathlib.Path(base,name);assert stat.S_ISREG(p.lstat().st_mode);rows.append({'relative':str(p.relative_to(root)),'stat':sm(p.lstat())})
 return sorted(rows,key=lambda x:x['relative'])
def invhash(root):return hashlib.sha256(encoded([{'relative':r['relative'],'stat':nonat(r['stat'])} for r in inventory(root)])).hexdigest()
result=load(A/'RESULT.json');indexPin=hashfile(A/'INDEX.json');obsPin=hashfile(A/'READ-OBSERVATIONS.json');index=load(A/'INDEX.json')
assert indexPin['sha256']==result['indexSHA256']=='115bbdb35d9cdff98503a3a5c63ced87e49a48d198194c9caa45268254bec0cf'
assert obsPin['sha256']==result['readObservationsSHA256']=='3487b20a345604e8e46b9810586ba57f6ddb9798cfb69cbc18659bcb274356fd'
archive=pathlib.Path(result['archive']);archivePin=hashfile(archive);assert archivePin=={'sha256':'ce0f8f40bcf0f0b22e5e4d93eef3d4660662826e617900aba09ac208c148dc13','bytes':8328689}
assert result['logicalBodyCount']==len(index['logicalBodies'])==831 and result['uniqueBodyCount']==index['uniqueBodyCount']==697 and result['preservedDependencies']==len(index['retainedDependencies'])==312
assert not result['selfContainedRelease'] and not index['selfContainedRelease'] and result['allOriginalPathsRetained']
logical={r['originalPath']:r for r in index['logicalBodies']};assert len(logical)==831
unique={}
for row in logical.values():
 assert row['blob']=='blobs/'+row['sha256'] and row['bytes']==row['stat']['size'] and not row['originalPath'].startswith(PROTECTED)
 if row['sha256'] in unique:assert unique[row['sha256']]==row['bytes']
 unique[row['sha256']]=row['bytes']
assert len(unique)==697
seen=set();archiveIndex=None
with os.fdopen(fdro(archive),'rb') as src,tarfile.open(fileobj=src,mode='r|gz') as tar:
 for member in tar:
  assert member.isfile() and member.name not in seen;seen.add(member.name);stream=tar.extractfile(member);h=hashlib.sha256();n=0
  while True:
   b=stream.read(32768)
   if not b:break
   h.update(b);n+=len(b)
  stream.close();assert n==member.size
  if member.name=='INDEX.json':assert {'sha256':h.hexdigest(),'bytes':n}==indexPin;archiveIndex=h.hexdigest()
  else:assert member.name.startswith('blobs/') and h.hexdigest()==member.name[6:] and n==unique[member.name[6:]]
assert seen=={'INDEX.json'}|{'blobs/'+h for h in unique} and archiveIndex
planPath=S/'pixel-cue-evidence-preserver-source-author-r2/PLAN.json';plan=load(planPath);supp=load(H/'SUPPLEMENT.json');meta=json.loads(gzip.decompress(small(H/'EXPECTED-INVENTORIES.json.gz')))
assert hashfile(planPath)['sha256']==index['planSHA256']==supp['originalPlanSHA256']=='56c1615aa9c7afb2b0f77e41825ba95f43fb0140e06b632fee1451441506661f'
assert hashfile(H/'build-capsule.py')['sha256']=='e9568f2af3ac8248a5758eca90dc195200a1a7f78d16955d95fae29f4c072960' and hashfile(H/'SUPPLEMENT.json')['sha256']=='999efb99ca48498754ef58543137fedcf0271c80543d34437f14a5d42dbd57ed'
assert hashfile(H/'EXPECTED-INVENTORIES.json.gz')['sha256']==supp['metadataSHA256']=='e780cce6990d2034d9959c77ea5c33ca96b56dea557da3c750327f4ca871a451'
sourceGate=S/'pixel-cue-evidence-preserver-source-independent-r3/GATE.json';assert hashfile(sourceGate)['sha256']=='eeaf921455563897b141ecf7a05ac639151b798e5d32bb56b75a4cd0e371597b' and load(sourceGate)['decision'].startswith('ACCEPT')
activationPath=S/'pixel-cue-capsule-activation-root-r1.json';activation=load(activationPath);assert hashfile(activationPath)['sha256']==index['activationSHA256']=='ff925b1f7790c0b2c49381cea547ed6f28bd4e11f3b51f8d8599f97d6e5696f9'
expected=set();expectedStats={};expectedAttrs={};originalRoots=[]
for group in meta['roots']:
 assert invhash(group['path'])==group['nonAtimeInventorySHA256'];originalRoots.append(group['path'])
 for row in group['rows']:
  path=str(pathlib.Path(group['path'])/row['relative']);expected.add(path);expectedStats[path]=row['stat'];expectedAttrs[path]=row['xattrs']
assert len(originalRoots)==39
for row in plan['files']:expected.add(row['path'])
for row in meta['files']:expectedStats[row['path']]=row['expectedOriginalStat'];expectedAttrs[row['path']]=row['xattrs']
for path,pin in plan['auditedCallerControls'].items():expected.add(path);assert logical[path]['sha256']==pin['sha256']
for row in plan['actualAuditedControls']:expected.add(row['resolvedPath']);assert logical[row['resolvedPath']]['sha256']==row['sha256'] and logical[row['resolvedPath']]['bytes']==row['bytes']
assert len(plan['actualAuditedControls'])==40 and len(plan['auditedCallerControls'])==59
newControls=[r for r in plan['actualAuditedControls'] if r['resolvedPath'] not in plan['auditedCallerControls']];assert len(newControls)==37 and sum(r['bytes'] for r in newControls)==234807
assert sorted(r['path'] for r in activation['reviewRoots'])==sorted(plan['pendingActivation']['requiredReviewRoots']) and sorted(r['path'] for r in activation['metadata'])==sorted(plan['pendingActivation']['metadata'])
reviewPins=[]
for group in activation['reviewRoots']:
 assert invhash(group['path'])==group['inventorySHA256'];g=pathlib.Path(group['path'])/'GATE.json';assert hashfile(g)['sha256']==group['gateSHA256']==logical[str(g)]['sha256'];reviewPins.append({'path':str(g),'sha256':group['gateSHA256'],'decision':load(g)['decision']})
 for row in inventory(group['path']):expected.add(str(pathlib.Path(group['path'])/row['relative']))
assert next(r['decision'] for r in reviewPins if 'actual-gameplay-' in r['path']).startswith('REJECT')
for row in activation['metadata']:expected.add(row['path']);expectedStats[row['path']]=row['stat'];expectedAttrs[row['path']]=row['xattrs'];assert logical[row['path']]['sha256']==row['sha256']
for row in inventory(H):expected.add(str(H/row['relative']))
expected.update([str(activationPath),str(H/'SUPPLEMENT.json'),supp['metadataPath']])
dependencies=[];freezeProof=[];newArtBodies=set();mapCount=0
for desc in plan['freezes']:
 assert hashfile(desc['path'])['sha256']==desc['sha256']==logical[desc['path']]['sha256'];expected.add(desc['path']);f=load(desc['path']);freezeProof.append({'path':desc['path'],'sha256':desc['sha256'],'counts':desc['counts'],'sourceDigest':f['sourceDigest'],'outputsDigest':f['outputsDigest']});assert [len(f['inputs']),len(f['outputs'])]==desc['counts']
 for family in ['inputs','outputs']:
  assert hashlib.sha256(encoded(f[family]).rstrip(b'\n')).hexdigest()==desc[family+'MapSHA256']
  for rel,digest in f[family].items():
   mapCount+=1;p=pathlib.Path(f['stage'])/('dist/'+rel if family=='outputs' else rel);new=pathlib.Path(rel).name in plan['newArtNames'];binary=p.suffix.lower() in ['.png','.jpg','.jpeg','.wav','.ogg','.mp3','.ico','.woff','.woff2'];target=p.resolve(strict=True)
   if binary and not new:dependencies.append({'logicalPath':str(p),'sha256':digest,'retainedBodyPath':str(target),'bodyReadInThisCapsulePhase':False,'from':desc['path']})
   else:
    expected.add(str(target));assert logical[str(target)]['sha256']==digest
    if new:newArtBodies.add(str(target))
    if target!=p:dependencies.append({'logicalPath':str(p),'sha256':digest,'includedBodyPath':str(target),'symlink':os.readlink(p) if p.is_symlink() else None})
 for rel,digest in f.get('support30Bodies',{}).items():expected.add(str(pathlib.Path(f['stage'])/rel));assert logical[str(pathlib.Path(f['stage'])/rel)]['sha256']==digest
assert dependencies==index['retainedDependencies'] and len(dependencies)==312 and len(newArtBodies)==6 and mapCount==449
support=load(plan['supportMap']['path']);mapping=support.get('supportBodies',support.get('support30Bodies',{}));assert len(mapping)==30;stage=pathlib.Path(load(plan['freezes'][0]['path'])['stage'])
for rel,value in mapping.items():path=str(stage/rel);expected.add(path);assert logical[path]['sha256']==(value if isinstance(value,str) else value['sha256'])
assert expected==set(logical),{'missing':list(expected-set(logical))[:5],'extra':list(set(logical)-expected)[:5]}
masterPaths=[x['path'] for x in plan['files'] if x['path'].startswith('/workspace/generated_images/')];assert len(masterPaths)==2 and set(masterPaths)<=set(logical)
# Full archive bodies independently match all831 retained originals using bounded
# hashing only: no extracted/copy files, image decoding, or protected ZIP access.
atimeDiffs=[]
for path,row in logical.items():
 current=sm(os.lstat(path));assert nonat(current)==nonat(row['stat']);assert hashfile(path)=={'sha256':row['sha256'],'bytes':row['bytes']}
 if path in expectedStats:assert row['expectedOriginalStat']==expectedStats[path] and nonat(row['stat'])==nonat(expectedStats[path]) and attrs(path)==expectedAttrs[path]
 if current['atime_ns']!=row['stat']['atime_ns']:atimeDiffs.append({'path':path,'archiveAtimeNs':row['stat']['atime_ns'],'freshAtimeNs':current['atime_ns'],'otherFieldsExact':True})
pixel=S/'coherent-native128-pixel-comparison-actual-r6';pairProof=[]
for label in ['C0','C1','C2','C-firstDrop','C-secondOutcome','C-normalized']:
 paths=[pixel/('A-hold-release-'+label+'-OPAQUE-SAVE.json'),pixel/('B-hold-release-'+label+'-OPAQUE-SAVE.json')];a,b=[load(p) for p in paths];assert a['raw']==b['raw'] and all(str(p) in logical for p in paths);pairProof.append({'label':label,'rawUTF8SHA256':hashlib.sha256(a['raw'].encode()).hexdigest(),'bytes':len(a['raw'].encode()),'equal':True})
prefix=index['readObservationsBeforeArchiveWrite'];observations=load(A/'READ-OBSERVATIONS.json');obs=observations['observations'];assert obs[:len(prefix)]==prefix and observations['ordinaryReadPolicy']==index['ordinaryReadPolicy']
archiveReads=[r for r in obs if r['kind']=='archive source body read'];finalStats=[r for r in obs if r['kind']=='final retained path stat'];assert len(archiveReads)==697 and len(finalStats)==831 and set(r['path'] for r in finalStats)==set(logical)
assert all(r['allNonAtimeFieldsStrict'] and r['readMode']=='O_NOATIME|O_NOFOLLOW' for r in obs)
for r in obs:
 assert r['readAtimeChanged']==(r['beforeReadAtimeNs']!=r['postReadAtimeNs']) and r['atimeDiffersFromExpected']==(r['expectedOriginalAtimeNs'] is not None and r['expectedOriginalAtimeNs']!=r['beforeReadAtimeNs'])
assert all(r['expectedOriginalAtimeNs']==logical[r['path']]['expectedOriginalStat']['atime_ns'] for r in finalStats if logical[r['path']]['expectedOriginalStat'])
rootGuard=S/'pixel-cue-capsule-archive-guard-root-r1';rg=load(rootGuard/'RESULT.json');ad=load(rootGuard/'ADMISSION.json');assert rg['exit_code']==0 and rg['failure'] is None and rg['memory_events_before']==rg['memory_events_after'] and ad['work']==256*1048576 and ad['reserve']==512*1048576
assert ad['command'][1]==str(H/'build-capsule.py') and ad['command'][-1]==str(A) and '--supplement-sha256' in ad['command']
assert sm(ZIP.lstat())==zipBefore and attrs(ZIP)==zipAttrs
allocated=sum(p.stat().st_blocks*512 for p in A.iterdir());assert allocated==10145792 and allocated<=16*1048576
rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss;assert rss<=24576
proof={'decision':'ACCEPT_COMPLETE_PIXEL_AND_EARLIER_CUE_EVIDENCE_PRESERVATION_ONLY','archive':{'path':str(archive),**archivePin},'index':indexPin,'readObservations':obsPin,'rootResult':hashfile(A/'RESULT.json'),'rootGuard':{'path':str(rootGuard),'sha256':hashfile(rootGuard/'RESULT.json')['sha256'],'exitCode':0,'samples':len(rg['samples'])},'sourceGate':{'path':str(sourceGate),'sha256':'eeaf921455563897b141ecf7a05ac639151b798e5d32bb56b75a4cd0e371597b'},'activationSHA256':index['activationSHA256'],'logicalBodies':831,'uniqueFullArchiveBodies':697,'all831FullOriginalStreamHashesMatch':True,'exactLogicalPathSetReconstructed':True,'threeFrozenFullMaps':freezeProof,'mapOccurrences':449,'newArtOriginalBodies':sorted(newArtBodies),'masters':[{ 'path':p,'sha256':logical[p]['sha256'],'bytes':logical[p]['bytes']} for p in masterPaths],'sixCompleteUTF8SavePairs':pairProof,'actualControlDomain':40,'sourceControlDomain':59,'formerlyMissing37Bytes':234807,'oldReviewPins':reviewPins,'archiveReadObservations':697,'finalPathObservations':831,'atimeReadChangesRecorded':sum(r['readAtimeChanged'] for r in obs),'expectedAtimeDifferencesRecorded':sum(r['atimeDiffersFromExpected'] for r in obs),'freshAtimeOnlyDifferences':atimeDiffs,'protectedZIPFullStatUnchanged':zipBefore,'protectedZIPBodyRead':False,'dependencyOccurrences':312,'externalBodyDependencies':sum('retainedBodyPath' in r for r in dependencies),'selfContainedRelease':False,'outputAllocatedBytes':allocated,'ownMaxRSSKiB':rss,'limits':['Preservation ACCEPT only; oldpixelREJECT remains verbatim, no art/default/fun/animation/platform acceptance','NewUI12.89MiB actual/newcueactual/newdefault/newcorpse bodies and reviews outside exact scope, metadata references do not supply them','Held312dependencies explicit;303external media bodies not included or freshly replayed here','Ordinary atime-only policy recorded, no reset; content/stat/xattrs strict, finite snapshots notOS protection','Archivefile fsync only; no wholepowerloss atomic/directory durability or cleanup authority','Originals retained; stream hashing produces no extraction/recompression/copy files']}
(P/'PROOF.json').write_text(json.dumps(proof,separators=(',',':'))+'\n');print(json.dumps({'decision':proof['decision'],'logical':831,'unique':697,'originalBodiesIndependentlyMatched':831,'dependencyOccurrences':312,'ownMaxRSSKiB':rss,'proofSHA256':hashfile(P/'PROOF.json')['sha256']}))
