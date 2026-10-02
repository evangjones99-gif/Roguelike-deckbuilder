import ast,collections,errno,hashlib,json,os,pathlib,resource,stat
P=pathlib.Path('/workspace/scratch/opening-turn-payoff-opening-checkpoint-preservation-independent-r1')
A=pathlib.Path('/workspace/scratch/opening-turn-payoff-opening-checkpoint-source-author-r1')
fallbacks=[];aliases=[]
def h(b):return hashlib.sha256(b).hexdigest()
def body(p):
 p=pathlib.Path(p);chain=[];q=p
 while q.is_symlink():
  chain.append((str(q),q.lstat(),os.readlink(q)));q=q.resolve(strict=True)
 flags=os.O_RDONLY|os.O_NOFOLLOW
 try:fd=os.open(q,flags|os.O_NOATIME)
 except OSError as e:
  if e.errno!=errno.EPERM:raise
  fallbacks.append(str(q));fd=os.open(q,flags)
 hh=hashlib.sha256();n=0
 with os.fdopen(fd,'rb') as f:
  before=os.fstat(f.fileno());assert stat.S_ISREG(before.st_mode)
  while b:=f.read(32768):hh.update(b);n+=len(b)
  after=os.fstat(f.fileno())
 assert tuple(before)==tuple(after)
 for name,s,t in chain:assert pathlib.Path(name).lstat()==s and os.readlink(name)==t
 if chain:aliases.append({'logical':str(p),'resolved':str(q)})
 return hh.hexdigest(),n
def j(p):return json.loads(pathlib.Path(p).read_bytes())
pins={'PLAN.json':'6b190d0efba84bf1b5c69fdfd3aa097bfd1bdd84ab65f2665f3df4a722524cce','preserve-checkpoint.py':'367ea7aeeb38186cc546c0bf52ee5e0e65e7705f9dda6d7ccf27c4097c441a69','MANIFEST.json':'5230066863357218bacd7e52e375b9fab4a08bd975c0329b959bf7e1de21792c','CLOSURE.json':'dc77f1a14a3bed45cd432fa236b005fdfee5c5d6750d75f163d4e2b0fa689854'}
for n,v in pins.items():assert body(A/n)[0]==v,(n,'pin')
method=(A/'preserve-checkpoint.py').read_text();ast.parse(method)
assert 'out.mkdir(exist_ok=False)' in method and 'original.read(len(b))==b' in method and 'os.O_NOFOLLOW' in method
assert 'unlink' not in method and 'subprocess' not in method and 'shutil' not in method
a=j(A/'PLAN.json');m=j(A/'MANIFEST.json');assert m['sealed']
# Stream the existing INDEX metadata; do not open the existing TAR or protected ZIP body.
ip=pathlib.Path(a['existingCapsule']['index']['path']);assert body(ip)[0]==a['existingCapsule']['index']['sha256']
decoder=json.JSONDecoder();buf='';members={};oldpaths={};count=0
with ip.open('r') as f:
 while '"logicalBodies":[' not in buf:
  b=f.read(32768);assert b;buf=(buf+b)[-131072:]
 buf=buf.split('"logicalBodies":[',1)[1]
 while True:
  buf=buf.lstrip(' \r\n\t,')
  if buf.startswith(']'):break
  try:row,end=decoder.raw_decode(buf)
  except json.JSONDecodeError:
   b=f.read(32768);assert b;buf+=b;assert len(buf)<131072;continue
  assert row['blob']=='blobs/'+row['sha256'];members[row['sha256']]=row['bytes'];oldpaths[row['originalPath']]=(row['sha256'],row['bytes']);count+=1;buf=buf[end:]
assert count==831 and len(members)==697
rows={};new={};storage=collections.Counter();roles=collections.Counter();oldlogicalsame=0
for ri,rel,sha,n,role,where in a['rows']:
 assert pathlib.Path(rel).name==rel and rel not in ['.','..']
 root=pathlib.Path(a['roots'][ri]);assert root.is_absolute();path=root/rel;key=str(path)
 assert key not in rows;rows[key]=(sha,n,where);storage[where]+=1;roles[a['roles'][role]]+=1
 assert body(path)==(sha,n),(key,'full original identity')
 if where=='existingCapsule':
  assert members[sha]==n
  if oldpaths.get(key)==(sha,n):oldlogicalsame+=1
 elif where=='newBlob':
  assert sha not in new or new[sha]==n;new[sha]=n
 else:raise AssertionError(where)
assert len(rows)==490 and len(new)==298 and sum(new.values())==9934592
assert storage=={'newBlob':303,'existingCapsule':187}
reviewNames=['opening-turn-payoff-actual-technical-independent-r1','opening-turn-payoff-actual-gameplay-independent-r1','opening-turn-payoff-actual-visual-independent-r1','opening-turn-payoff-actual-visual-independent-r2','opening-turn-payoff-on-actual-technical-independent-r1','opening-turn-payoff-on-actual-gameplay-independent-r1','opening-turn-payoff-on-actual-visual-independent-r1']
treeCounts={}
for root in [pathlib.Path(x['originalRoot']) for x in a['actualComparisons']]+[pathlib.Path('/workspace/scratch')/n for n in reviewNames]:
 files={str(p) for p in root.rglob('*') if p.is_file()};assert files<=rows.keys(),(str(root),sorted(files-rows.keys()));treeCounts[str(root)]=len(files)
rawPairs=[]
for comparison in a['actualComparisons']:
 root=pathlib.Path(comparison['originalRoot']);assert len(list(root.glob('*.jpg')))==8
 for expected in comparison['sixCompleteRawPairs']:
  raw=[]
  for side in 'AB':
   path=root/(side+'-cue-'+expected['label']+'-OPAQUE-SAVE.json');v=j(path);raw.append(v['raw'].encode('utf-8'));assert str(path) in rows
  assert raw[0]==raw[1] and (h(raw[0]),len(raw[0]))==(expected['rawSHA256'],expected['rawBytes'])
 rawPairs.append(comparison['sixCompleteRawPairs'])
assert rawPairs[0]==rawPairs[1]
controls=[]
for control in a['exact40Controls']['manifests']:
 path=pathlib.Path(control['path']);assert body(path)[0]==control['sha256'];v=j(path);assert len(v['bodies'])==control['bodies']
 for b in v['bodies']:
  q=path.parent/b['name'];assert str(q) in rows and rows[str(q)][0]==b['sha256'];controls.append(str(q))
assert len(controls)==40
deps={str(pathlib.Path(a['roots'][ri])/rel):sha for ri,rel,sha,role in a['externalDependencies']['gameMediaRows']};assert len(deps)==303
mapCounts=[]
for authority in a['runtimeAuthorities']:
 path=pathlib.Path(authority['freezePath']);assert body(path)[0]==authority['freezeSHA256'];v=j(path);stage=pathlib.Path(authority['stage'])
 assert v['stage']==str(stage)
 for field,countkey,digestkey,base in [('inputs','inputCount','sourceDigest',stage),('outputs','outputCount','outputsDigest',stage/'dist')]:
  mp=v[field];assert len(mp)==authority[countkey]
  digest=h(json.dumps(mp,sort_keys=True,separators=(',',':')).encode());assert digest==authority[digestkey]==v[digestkey]
  for rel,sha in mp.items():
   q=str(base/rel)
   if pathlib.Path(rel).suffix.lower() in {'.png','.wav','.ogg','.mp3','.jpg','.webp'}:assert deps[q]==sha and pathlib.Path(q).is_file()
   else:assert q in rows and rows[q][0]==sha
 mapCounts.append([len(v['inputs']),len(v['outputs'])])
assert mapCounts==[[89,56],[89,56],[88,56]]
gates=[]
for item in a['independentGateIdentities']:
 assert body(item['path'])[0]==item['sha256'] and str(item['path']) in rows
 g=j(item['path']);gates.append({'path':item['path'],'sha256':item['sha256'],'decision':g.get('decision',g.get('status'))})
for n,sha in a['finalDefaultVisualPins'].items():assert rows['/workspace/scratch/opening-turn-payoff-on-actual-visual-independent-r1/'+n][0]==sha
archive=pathlib.Path(a['existingCapsule']['archive']['path']);archiveStat=archive.stat();assert archiveStat.st_size==8328689
zipPath=pathlib.Path('/workspace/scratch/retained-original-archives/preflight-bdf273-original-r4.zip');zipBefore=zipPath.stat();zipAttrs={n:os.getxattr(zipPath,n).hex() for n in os.listxattr(zipPath)}
holdPath=pathlib.Path('/workspace/Roguelike-deckbuilder/AGENTS.md');hold=holdPath.read_bytes();assert b'opening-turn-payoff-on-stage-r1' in hold and b'opening-turn-payoff-default-stage-r3' in hold
proposal=a['proposedArchive'];assert [proposal[x] for x in ['workMiB','reserveMiB','ownRSSCapBytes','methodWholeCeilingSeconds','logicalOutputCapBytes','physicalOutputCapBytes','freshFreeDiskMinimumBytes']]==[128,512,24*1048576,60,16*1048576,16*1048576,17*1048576]
assert zipPath.stat()==zipBefore and {n:os.getxattr(zipPath,n).hex() for n in os.listxattr(zipPath)}==zipAttrs
assert archive.stat()==archiveStat
rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss;assert rss<=24576
proof={'status':'SOURCE_FULL_FINITE_AUDIT_PASS_NOT_ARCHIVE_EXECUTED','pins':pins,'logicalRows':len(rows),'newUniqueBodies':len(new),'newUniqueBytes':sum(new.values()),'storage':dict(storage),'roles':dict(roles),'existingIndexLogicalRows':count,'existingIndexUniqueBodies':len(members),'existingLogicalSamePathCount':oldlogicalsame,'all187ReferenceSHAAndLengthBound':True,'full490OriginalSHAAndLengthMatched':True,'reviewAndActualCompleteTreeCounts':treeCounts,'actualJPEGCount':16,'rawPairCount':12,'rawDomain':'complete UTF8 saved strings separately from opaque wrapper SHA','all40CallerBodies':len(controls),'runtimeMaps':mapCounts,'externalGameMediaIdentityRowsNoBodyRead':len(deps),'gates':gates,'protectedZipStatAndXattrsUnchangedNoBodyRead':True,'AGENTSSHA256':h(hold),'ordinaryNOATIMEFallbackPaths':fallbacks,'aliasBodiesResolvedCount':len(aliases),'ownMaxRSSKiB':rss,'qualification':'Source eligibility only. Existing TAR not body read; exact INDEX and earlier COMPLETE697-body gate retained. Future Root actual must full-hash references, copy/readback298, retain terminal stdout and undergo independent COMPLETE review. No runtime selection or cleanup.'}
# Included as source before final proof write in the retained predecessor reader.
import tarfile
O=pathlib.Path('/workspace/scratch/opening-turn-payoff-opening-checkpoint-output-root-r1')
RG=pathlib.Path('/workspace/scratch/opening-turn-payoff-opening-checkpoint-archive-guard-root-r1')
grantPath=pathlib.Path('/workspace/scratch/opening-turn-payoff-opening-checkpoint-archive-grant-root-r1.json')
assert body(grantPath)[0]=='f10c78099e4e4fc9598eba7b99e5318382ed46050707ae82292ea56eb6b97a62'
grant=j(grantPath);assert grant['rootArchiveAuthorized'] and grant['plan']['sha256']==pins['PLAN.json'] and grant['method']['sha256']==pins['preserve-checkpoint.py']
sg=pathlib.Path(grant['sourceGate']['path']);assert body(sg)[0]==grant['sourceGate']['sha256']=='4bfbc6ee637d79b98831fcf0dfe72233e3fec55309695b137956753920e097aa'
assert h(hold)==grant['currentHold']['sha256']
for n,expected in {'INDEX.json':'fd6e057da394aa127766f434bd70c9b1045c17f92ab0e94fb70dd77ebb6a9ad2','READ-OBSERVATIONS.json':'4b9fecb9012a5970ef0323826de09b2f081e71a2dcdef0691a41dfcb40e8987f','RESULT.json':'91ccaa2007614c70b10cdfbcdb7950ade02309c003fac033aca003c14300dc50'}.items():assert body(O/n)[0]==expected
index=j(O/'INDEX.json');result=j(O/'RESULT.json');observations=j(O/'READ-OBSERVATIONS.json')
for field in ['roots','rowColumns','rows','roles','existingCapsule','externalDependencies','runtimeAuthorities']:assert index[field]==a[field],field
assert index['allOriginalPathsRetained'] and index['fullUniqueOriginalByteRoundtrip'] and index['selfContainedRelease'] is False
assert result['archiveSHA256']=='f9121c7b6416398241d1b5a160b4781f17a45dff4813260edaf4c3b6df1761af' and result['archiveBytes']==3839783
archivePath=O/('evidence-'+result['archiveSHA256']+'.tar.gz')
assert body(archivePath)==(result['archiveSHA256'],result['archiveBytes'])
assert body(archive)==(a['existingCapsule']['archive']['sha256'],8328689)
assert body(ip)[0]==a['existingCapsule']['index']['sha256']
unique={}
for ri,rel,sha,n,role,where in a['rows']:
 if where=='newBlob':unique.setdefault(sha,(pathlib.Path(a['roots'][ri])/rel,n))
seen=set();literalComparedBytes=0
def original_open(path):
 fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME);return os.fdopen(fd,'rb')
with original_open(archivePath) as stream:
 before=os.fstat(stream.fileno())
 with tarfile.open(fileobj=stream,mode='r|gz',bufsize=32768) as tf:
  for member in tf:
   assert member.isfile() and member.name.startswith('blobs/') and member.name.count('/')==1
   sha=member.name.split('/')[1];assert sha in unique and sha not in seen
   original,n=unique[sha];assert member.size==n;hh=hashlib.sha256();read=0
   with tf.extractfile(member) as blob,original_open(original) as raw:
    statBefore=os.fstat(raw.fileno())
    while block:=blob.read(32768):assert raw.read(len(block))==block;hh.update(block);read+=len(block)
    assert raw.read(1)==b'' and os.fstat(raw.fileno())==statBefore
   assert read==n and hh.hexdigest()==sha;literalComparedBytes+=read;seen.add(sha)
 assert os.fstat(stream.fileno())==before
assert seen==set(unique) and literalComparedBytes==9934592
assert len(observations)==598 and all(x['noAtimeRequested'] and not x['permissionFallback'] for x in observations)
assert {x['originalPath'] for x in observations[:2]}=={str(archive),str(ip)}
copies=[x for x in observations if 'sha256' in x];readbacks=[x for x in observations if x.get('scope')=='full decoded original-byte equality readback']
assert len(copies)==len(readbacks)==298
for row in copies:
 assert row['sha256'] in unique and row['bytes']==unique[row['sha256']][1] and pathlib.Path(row['originalPath'])==unique[row['sha256']][0]
assert {x['originalPath'] for x in readbacks}=={str(x[0]) for x in unique.values()}
rootGuard=j(RG/'RESULT.json');admission=j(RG/'ADMISSION.json');terminal=j(RG/'EXECUTION.log')
assert rootGuard['exit_code']==0 and rootGuard['failure'] is None and rootGuard['memory_events_before']==rootGuard['memory_events_after']
assert admission['admitted'] and admission['work']==128*1048576 and admission['reserve']==512*1048576
assert admission['command']==['python','-B',str(A/'preserve-checkpoint.py'),str(A/'PLAN.json'),pins['PLAN.json'],str(O)]
assert admission['initial']['free']>=64*1048576 and admission['initial']['headroom']>=640*1048576
for key in result:assert result[key]==terminal[key]
logical=sum(p.stat().st_size for p in O.rglob('*') if p.is_file());allocated=sum(p.stat().st_blocks*512 for p in O.rglob('*') if p.is_file())
assert terminal['terminalLogicalOutputBytesAfterAllWrites']==logical==4084419 and terminal['terminalAllocatedOutputBytesAfterAllWrites']==allocated==4096000
assert logical<=16*1048576 and allocated<=16*1048576 and terminal['terminalElapsedAfterAllWrites']<=60 and terminal['terminalOwnMaxRSSBytesAfterAllWrites']<=24*1048576
assert zipPath.stat()==zipBefore and {n:os.getxattr(zipPath,n).hex() for n in os.listxattr(zipPath)}==zipAttrs
rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss;assert rss<=24576
proof['status']='ACCEPT_COMPLETE_BYTE_PRESERVATION_NOT_RUNTIME_SELECTION'
proof['completeArchive']={'path':str(archivePath),'sha256':result['archiveSHA256'],'compressedBytes':3839783,'allMembersSHAAndLiteralOriginalByteEquality':True,'memberCount':len(seen),'fullDecodedOriginalBytesCompared':literalComparedBytes,'indexSHA256':body(O/'INDEX.json')[0],'observationsSHA256':body(O/'READ-OBSERVATIONS.json')[0],'resultSHA256':body(O/'RESULT.json')[0],'existingArchiveFreshFullCompressedSHA':a['existingCapsule']['archive']['sha256'],'existing831LogicalIndexFreshFullSHA':a['existingCapsule']['index']['sha256'],'newReferenceCount':187,'old697DecodedBodiesNotReread':'Exact full compressed SHA plus exact INDEX and retained prior COMPLETE117074 verify immutable authority; no old master body read.'}
proof['rootActual']={'grantSHA256':body(grantPath)[0],'guardResultSHA256':body(RG/'RESULT.json')[0],'guardAdmissionSHA256':body(RG/'ADMISSION.json')[0],'terminalStdoutSHA256':body(RG/'EXECUTION.log')[0],'normalExit':0,'samples':len(rootGuard['samples']),'terminalElapsedSeconds':terminal['terminalElapsedAfterAllWrites'],'terminalOwnRSSBytes':terminal['terminalOwnMaxRSSBytesAfterAllWrites'],'logicalOutputBytes':logical,'allocatedOutputBytes':allocated,'observationCount':len(observations),'zeroPermissionFallback':True}
proof['ownMaxRSSKiB']=rss
proof['qualification']='Complete byte-preservation evidence only. No extraction, image decode, protected ZIP body read, original removal, runtime/defaultwording/art selection or platform/enjoyment claim. Shared cgroup guard samples are nonexclusive; Root observed own child closure. Existing archive 697 body authority verified via exact compressed SHA/INDEX plus previous COMPLETE, not replayed old master bodies. Helper metadata subset remains qualified; originals retained.'

(P/'PROOF.json').write_text(json.dumps(proof,indent=2)+'\n')
print(json.dumps({'status':proof['status'],'logicalRows':490,'newBodies':298,'existingRefs':187,'ownMaxRSSKiB':rss,'proofSHA256':h((P/'PROOF.json').read_bytes())}))
