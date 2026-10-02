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
