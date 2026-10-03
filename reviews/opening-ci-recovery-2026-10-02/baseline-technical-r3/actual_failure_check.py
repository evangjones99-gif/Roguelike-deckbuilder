import pathlib,json,hashlib,zipfile,resource
P=pathlib.Path('/workspace/scratch/empty-intent-fresh-ci-actual-failure-r1');O=pathlib.Path('/workspace/scratch/empty-intent-fresh-ci-technical-r3')
def sha(b):return hashlib.sha256(b).hexdigest()
connected=json.loads((O/'CONNECTED-FAILURE-METADATA.json').read_bytes());a=connected['artifacts'];j=connected['jobs'];assert len(a)==len(j)==1
a=a[0];j=j[0];assert a['id']==11247522978 and a['size_in_bytes']==14214 and a['digest']=='sha256:e2ade41d097c2b622b7633c53259e0fe946b04fca8ba0efc1df4f7f0792b6e0a' and not a['expired']
assert a['workflow_run']['id']==37053530852 and a['workflow_run']['head_sha']=='265eb047cd041d79a56edfa5b0a6d270e020b8f0' and a['workflow_run']['head_branch']=='codex/lanternbound-production'
assert j['id']==110992495401 and j['run_id']==37053530852 and j['status']=='completed' and j['conclusion']=='failure'
for number in [2,3,4,5,12,13]:assert next(s for s in j['steps'] if s['number']==number)['conclusion']=='success'
assert next(s for s in j['steps'] if s['number']==6)['conclusion']=='failure'
for number in [7,8,9,10,11]:assert next(s for s in j['steps'] if s['number']==number)['conclusion']=='skipped'
rootbytes=(P/'ROOT-TRANSFER-VERIFICATION.json').read_bytes();root=json.loads(rootbytes);assert root['artifact']==a['id'] and root['run']==37053530852 and root['actualBuildExecuted'] is False
expected={r['path']:r for r in root['entries']};assert len(expected)==10
before={p.name:p.stat() for p in P.iterdir() if p.is_file()};assert all(not (P/n).is_symlink() for n in before)
zb=(P/'TRANSPORT.zip').read_bytes();assert len(zb)==14214 and sha(zb)==root['zipSHA256']==a['digest'].split(':')[1]
verified={}
with zipfile.ZipFile(P/'TRANSPORT.zip') as archive:
 infos=archive.infolist();assert len(infos)==10 and {i.filename for i in infos}==set(expected)
 for i in infos:
  assert not i.is_dir() and not i.flag_bits&1 and i.compress_type==zipfile.ZIP_STORED and i.file_size<65536
  assert pathlib.PurePosixPath(i.filename).name==i.filename
  b=archive.read(i);assert b==(P/i.filename).read_bytes() and len(b)==expected[i.filename]['bytes'] and sha(b)==expected[i.filename]['sha256']
  verified[i.filename]={'bytes':len(b),'sha256':sha(b),'ZIPCRCPassed':True}
diag=json.loads((P/'diagnostic-index.json').read_bytes());assert diag['allProofBytesUploaded'] is True and diag['status']=='FAILED_OR_INCOMPLETE' and diag['runtimeBuildGameplayApproval'] is False
assert set(diag['proofInventory'])==set(expected)-{'diagnostic-index.json'}
for name,pin in diag['proofInventory'].items():assert all(pin[k]==verified[name][k] for k in ['bytes','sha256'])
assert sum(v['bytes'] for v in verified.values())<=1048576
node=json.loads((P/'node-version-closure.json').read_bytes());npm=json.loads((P/'npm-version-closure.json').read_bytes())
assert node['status']=='PASS' and node['exit']==0 and node['closureObserved'] is True and node['liveAtClosure']==[] and (P/'node-version.log').read_bytes()==b'v24.19.0\n'
assert npm['status']=='FAILED' and npm['exit']==1 and npm['closureObserved'] is True and npm['liveAtClosure']==[] and npm['rawLogComplete'] is True and npm['rawLogBytes']==117
log=(P/'npm-version.log').read_bytes();assert log==b'Exit prior to config file resolving\ncause\ndouble-loading config "/dev/null" as "global", previously loaded as "user"\n'
for x in [node,npm]:assert x['elapsedSeconds']<x['wholeSeconds']==10 and x['sampledAggregatePeakRSS']<=x['workCapBytes']==384*1048576 and x['reserveBytes']==512*1048576
failed=json.loads((P/'preflight-failure.json').read_bytes());assert failed=={'exceptionType':'ValueError','message':'npm-version failed; retained closure/log','phase':'preflight','status':'FAILED'}
m=json.loads(pathlib.Path('/workspace/scratch/empty-intent-fresh-ci-source-r2/METADATA.json').read_bytes());acq=json.loads((P/'acquisition-progress.json').read_bytes())
assert acq['complete'] is True and acq['expected']==53 and len(acq['verified'])==53
assert acq['verified']==[{k:r[k] for k in ['sha256','gitBlobSHA1','bytes']} for r in m['blobPins']]
asm=json.loads((P/'assembled-membership.json').read_bytes());assert asm['sourceCount']==98 and asm['supportCount']==30 and asm['sourceDigest']==m['sourceDigest']
supporthash=sha(json.dumps(dict(sorted((r['path'],r['sha256']) for r in m['support'])),separators=(',',':')).encode());assert asm['supportDigest']==supporthash
init=json.loads((P/'initialization.json').read_bytes());assert init['methodSHA256']=='2c1607de78b67f40d748fa632b67842cf995b48d492707b549c51a24b9ecb117' and init['metadataSHA256']=='b2f13179f14ccebecbc4452fa4e6b3cc88623dc629ff0009c1118401123ca46d' and init['run']=='37053530852'
wf=pathlib.Path('/workspace/scratch/empty-intent-fresh-ci-source-r2/rebuild-opening-baseline.yml').read_bytes();pub=json.loads((O/'PUBLISHED-FAILURE-WORKFLOW.json').read_bytes());assert hashlib.sha1(b'blob '+str(len(wf)).encode()+b'\0'+wf).hexdigest()==pub['gitBlobSHA1']=='508c6242c9704bd4e992908285e7510abbdcc802' and pub['returnedCodeUnits']==len(wf)
for n,old in before.items():
 new=(P/n).stat();assert (old.st_dev,old.st_ino,old.st_size,old.st_mtime_ns,old.st_ctime_ns,old.st_mode)==(new.st_dev,new.st_ino,new.st_size,new.st_mtime_ns,new.st_ctime_ns,new.st_mode)
current=int(pathlib.Path('/sys/fs/cgroup/memory.current').read_text());maximum=int(pathlib.Path('/sys/fs/cgroup/memory.max').read_text());assert maximum-current>=(64+512)*1048576
proof={'actualFailureVerified':True,'runID':37053530852,'jobID':110992495401,'artifactID':11247522978,'headCommit':'265eb047cd041d79a56edfa5b0a6d270e020b8f0','ZIPBytes':len(zb),'ZIPSHA256':sha(zb),'all10MembersStandaloneByteExact':verified,'diagnosticAllProofInventoryVerified':True,'failure':'npm --version refuses double-loading /dev/null for global/user config','nodeVersion':'v24.19.0','actualInstallBuildTestsSkipped':True,'acquisitionAndAssemblyReportedSuccess':True,'source98MapDigestReported':asm['sourceDigest'],'assembledBodiesNotDownloadedOrIndependentlyVerified':True,'noGameBugClaim':True,'retainedMetadataPreservedExceptPermittedAtime':True,'expiresAt':a['expires_at'],'ownVerifierPeakRSSBytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,'ordinaryWorkBytes':64*1048576,'reserveBytes':512*1048576,'initialCgroupCurrent':current,'cgroupMaximum':maximum,'candidateMainArchiveNpmBuildBrowserExecuted':False,'qualification':'Verified actual diagnostic transport and exact logs/receipts, not game/build runtime. CI assembly success/source identity are receipts bound to reviewed published method; this reviewer did not obtain or open runner-stage bodies or TARs.'}
(O/'ACTUAL-FAILURE-PROOF.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({k:v for k,v in proof.items() if k!='all10MembersStandaloneByteExact'}))
