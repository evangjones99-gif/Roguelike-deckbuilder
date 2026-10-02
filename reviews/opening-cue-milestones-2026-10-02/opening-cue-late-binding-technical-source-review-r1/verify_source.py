import pathlib,json,gzip,hashlib,ast,subprocess,resource,os,re,signal,shutil
P=pathlib.Path('/workspace/scratch/opening-cue-late-binding-caller-source-r1');O=pathlib.Path('/workspace/scratch/opening-cue-late-binding-technical-source-review-r1')
signal.alarm(30)
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):b=p.read_bytes();return dict(bytes=len(b),sha256=sha(b))
host=int(next(x.split()[1] for x in pathlib.Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))*1024
cg=pathlib.Path('/sys/fs/cgroup');maximum=(cg/'memory.max').read_text().strip();cur=int((cg/'memory.current').read_text());available=host if maximum=='max' else min(host,int(maximum)-cur)
assert available>=(64+512)*1048576 and shutil.disk_usage(O).free>=24*1048576
before={p.name:pin(p) for p in P.iterdir() if p.is_file()}
assert not any(x.is_symlink() or not x.is_file() for x in P.iterdir())
seal=json.loads((P/'SOURCE-SEAL.json').read_bytes());assert before['SOURCE-SEAL.json']['sha256']=='99e7723d28e71a8e3e840e039268fe76877abd81923976d8d79b6d0f8e2fc813'
assert before=={**{r['name']:{k:r[k] for k in ('bytes','sha256')} for r in seal['files']},'SOURCE-SEAL.json':before['SOURCE-SEAL.json']}
assert sum(r['bytes'] for r in before.values())==seal['familyBytesIncludingSeal']==100761<=196608
assert seal['sourceOnly'] and not seal['runtimeEligible'] and not seal['candidateCBindingsComplete'] and not seal['RootMethodGrantPresent']
expected=json.loads((P/'EXPECTED.json').read_bytes());b,c=expected['runtimes']
assert expected['sealed'] is False and expected['runtimeEligible'] is False and expected['runtimeRecovery']['complete'] is False
pending=['stage','outputsDigest','freezePath','freezeSHA256','stageManifestPath','stageManifestSHA256','stageAuthorityPath','stageAuthoritySHA256','stageReviewPath','stageReviewSHA256']
assert all(c[k] is None for k in pending) and b['role']=='retainedB' and c['role']=='candidateC'
assert [r['case'] for r in expected['runtimes']]==['B-cue','C-cue']
orig=json.loads(gzip.decompress((P/'ORIGIN-CONTROLS.json.gz').read_bytes()));delta=json.loads(gzip.decompress((P/'CONTROL-INVERSE.json.gz').read_bytes()))
def trans(text,hunks,side):
 lines=text.splitlines(keepends=True);out=[];cursor=0
 for q in hunks:
  start=q[side+'LineStart'];old=q[side].splitlines(keepends=True);assert start>=cursor and ''.join(lines[start:start+len(old)])==q[side];out.extend([''.join(lines[cursor:start]),q['after' if side=='before' else 'before']]);cursor=start+len(old)
 out.append(''.join(lines[cursor:]));return ''.join(out)
roundtrips=[]
for row in delta['files']:
 parent=next(x for x in orig['files'] if x['name']==row['originName']);old=parent['literalUTF8'];new=(P/row['name']).read_text()
 assert len(old.encode())==parent['bytes']==row['beforeBytes'] and sha(old.encode())==parent['sha256']==row['beforeSHA256']
 assert sha(new.encode())==row['afterSHA256'] and len(new.encode())==row['afterBytes']
 assert trans(old,row['hunks'],'before')==new and trans(new,row['hunks'],'after')==old
 roundtrips.append({k:v for k,v in row.items() if k!='hunks'})
assert len(roundtrips)==3
driver=(P/'driver-cue.mjs').read_text();sup=(P/'supervise-cue.py').read_text();js=(P/'runtime-guard-cue.mjs').read_text();py=(P/'runtime_guard_cue.py').read_text()
assert driver.index('qualification=qualify(')<driver.index('await import(expected.dependencies.modulePath)')<driver.index('fs.writeFileSync(')<driver.index('http.createServer(')<driver.index('chromium.launch(')
assert sup.index('method_grant=qualify(')<sup.index('stage,freeze,packet,port=')<sup.index('p.mkdir(')<sup.index('subprocess.Popen(')
assert sup.index('entry_start=time.monotonic()')<sup.index('method_grant=qualify(')<sup.index('start=entry_start')
assert driver.index('const started=Date.now()')<driver.index('qualification=qualify(') and '60000-(Date.now()-started)' in driver
assert not any(s in driver for s in ('localStorage.setItem','dispatchEvent','createGame(','applyAction(','.fill('))
assert 'a.raw===z.raw' in driver and 'new Set([...Object.keys(b.checkpoints),...Object.keys(c.checkpoints)])' in driver
assert 'result.mechanicalPass=result.protocolPass&&result.focusedLateBindingBranchObserved' in driver
for s in ['SKIPPED_NO_NATURAL_TURN1_LEGAL_BINDING','SKIPPED_NO_NATURAL_TURN2_LEGAL_BINDING','SKIPPED_TERMINAL_BEFORE_LATE_BINDING','LATE_BINDING_TERMINAL_NO_FIRST_ORDER','if(after.phase===\'battle\')','assert(!currentAlly||currentAlly.acted','350','assert.equal(s.hand[Number(choice.index)],choice.id)','active.boundUID=ally.uid','assert.equal(b.boundUID??null,c.boundUID??null)','assert.equal(b.orderTargetUID??null,c.orderTargetUID??null)']:assert s in driver
assert all(s in sup for s in ['work=896*1048576;reserve=512*1048576','71*1048576','jpg<=2*1048576','storedProofBytesTotal\']<=5*1048576','postLifecycleFullReadbackVerified','terminal-after-every-owned-packet-write'])
for f in P.glob('*.py'):compile(ast.parse(f.read_bytes()),str(f),'exec')
grammar=[]
for name in ['driver-cue.mjs','runtime-guard-cue.mjs']:
 r=subprocess.run(['/opt/codex/runtimes/codex-primary-runtime/dependencies/node/bin/node','--check',str(P/name)],capture_output=True,timeout=10)
 assert r.returncode==0;grammar.append(dict(name=name,exit=r.returncode,stdoutBytes=len(r.stdout),stderrBytes=len(r.stderr)))
# Isolate the exact rejection predicate/function; no canonical helper module or caller executed.
t=ast.parse(py);fn=next(n for n in t.body if isinstance(n,ast.FunctionDef) and n.name=='qualify');access=[]
env={'regular':lambda *a:access.append(a)}
exec(compile(ast.Module(body=[fn],type_ignores=[]),'isolated_ineligible_qualify','exec'),env)
cases=[]
for label,data in [('actual',expected),('unsealed',{'sealed':False,'runtimeEligible':True,'runtimeRecovery':{'complete':True}}),('runtime-ineligible',{'sealed':True,'runtimeEligible':False,'runtimeRecovery':{'complete':True}}),('incomplete-recovery',{'sealed':True,'runtimeEligible':True,'runtimeRecovery':{'complete':False}})]:
 try:env['qualify'](data,b'none','/synthetic')
 except AssertionError as e:assert 'SOURCE_ONLY_UNSEALED' in str(e)
 else:raise AssertionError('ineligible admitted '+label)
 assert not access;cases.append(label)
q=js[js.index('export function qualify('):].replace('export function qualify(','function qualify(',1)
probe="import assert from 'node:assert/strict';\nlet access=0;const regular=()=>{access++;throw Error('unexpected file access')};\n"+q+"\nconst cases=[{sealed:false,runtimeEligible:false,runtimeRecovery:{complete:false}},{sealed:false,runtimeEligible:true,runtimeRecovery:{complete:true}},{sealed:true,runtimeEligible:false,runtimeRecovery:{complete:true}},{sealed:true,runtimeEligible:true,runtimeRecovery:{complete:false}}];for(const c of cases){assert.throws(()=>qualify(c,Buffer.from('none'),'/synthetic'),/SOURCE_ONLY_UNSEALED/);assert.equal(access,0)}console.log(JSON.stringify({cases:4,fileAccesses:access,externalImportOrCallerExecuted:false}));\n"
(O/'isolated_guard_check.mjs').write_text(probe)
r=subprocess.run(['/opt/codex/runtimes/codex-primary-runtime/dependencies/node/bin/node',str(O/'isolated_guard_check.mjs')],capture_output=True,timeout=10);assert r.returncode==0,r.stderr;jsprobe=json.loads(r.stdout)
# Exact B review schema and current regular-file namespace/metadata, no runtime stage execution or historical-restoration claim.
external={}
def rec(path,h):p=pathlib.Path(path);row=pin(p);assert row['sha256']==h;external[path]=row;return json.loads(p.read_bytes())
freeze=rec(b['freezePath'],b['freezeSHA256']);manifest=rec(b['stageManifestPath'],b['stageManifestSHA256']);authority=rec(b['stageAuthorityPath'],b['stageAuthoritySHA256']);review=rec(b['stageReviewPath'],b['stageReviewSHA256'])
assert review['decision']=='ACCEPT_EXACT_NEW_REGULAR_FILE_STATIC_RECONSTRUCTION_ONLY' and review['accepted'] is True
for key,ref in [('newRuntimeFreezeSHA256','freezeSHA256'),('newStageManifestSHA256','stageManifestSHA256'),('newRootAuthoritySHA256','stageAuthoritySHA256')]:assert review[key]==b[ref]
assert review['exactSource104Verified'] and review['exactOutputs70Verified'] and not review['artDefaultGameplayFunApproved'] and not review['actualFreshStrictBuild']
audit=rec(str(pathlib.Path(b['stageReviewPath']).parent/'AUDIT.json'),review['fullAuditSHA256']);assert audit['stage']==b['stage'] and audit['inputCount']==104 and audit['outputCount']==70
rec(str(pathlib.Path(b['stageAuthorityPath']).parent/'BODY-COPY-RECEIPT.json'),authority['bodyCopyReceiptSHA256'])
membership={**freeze['inputs'],**{'dist/'+k:v for k,v in freeze['outputs'].items()}};assert set(membership)==set(manifest['files']) and len(membership)==174
stage=pathlib.Path(b['stage']);assert not stage.is_symlink();actual=[];inodes=set()
for dp,dirs,files in os.walk(stage):
 assert not any(pathlib.Path(dp,n).is_symlink() for n in dirs+files)
 actual.extend(str(pathlib.Path(dp,n).relative_to(stage)) for n in files)
assert set(actual)==set(membership)
for rel,row in manifest['files'].items():
 f=stage/rel;s=f.stat();assert f.is_file() and row['sha256']==membership[rel]
 for key,value in {'bytes':s.st_size,'dev':s.st_dev,'ino':s.st_ino,'mode':s.st_mode,'nlink':s.st_nlink,'mtimeNs':s.st_mtime_ns,'ctimeNs':s.st_ctime_ns}.items():assert str(value)==str(row[key]),(rel,key)
 assert s.st_nlink==1 and (s.st_dev,s.st_ino) not in inodes;inodes.add((s.st_dev,s.st_ino))
dependencies=rec(expected['dependencies']['path'],expected['dependencies']['sha256']);assert dependencies['schema']=='installed-dependency-identities-v1' and dependencies['nodeVersion']=='v24.19.0' and dependencies['packageVersion']=='1.62.0'
assert before=={p.name:pin(p) for p in P.iterdir() if p.is_file()}
rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024;child=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss*1024;assert rss+child<=64*1048576
proof=dict(verdict='PASS_SOURCE_ONLY_INELIGIBLE_TEMPLATE',sourceSealSHA256=before['SOURCE-SEAL.json']['sha256'],sourceInclusiveBytes=100761,sourceFiles=before,threeCopiedControlFullForwardInverse=roundtrips,originAuthority='literal working R4 controls, not a final source seal',sourceIneligibleFlagsFalse=True,candidateNullFields=pending,BActual703SchemaAndCurrent174MetadataVerified=True,stageBodiesHashedByThisReviewer=False,externalMetadataPins=external,dependencyQualification='404 external files646881166B metadata pinned; bodies not hashed here',grammar=grammar,pythonASTCompiled=True,isolatedPythonFalseGuardCases=cases,isolatedJSFalseGuard=jsprobe,ineligibleBeforeRootGrantLookupOrExternalImportOrMkdirPopen=True,elapsedClocksBeginBeforePreflightAndNeverReset=True,resourceDeadlines='sampled cancellation/final elapsed validation, no hard synchronous preflight IO deadline',rawCheckpointFullUnionAndPairedBranches=True,ordinaryUICurrentUIDLegalTargetsAndPurityChecks=True,terminalOrderAssertionsBattleScoped=True,noCallerHelperModuleBrowserServerBuildOrAppExecuted=True,frozenSourceAndOriginalAuthorityBodiesUnchanged=True,atimeMayChange=True,resource=dict(workBytes=64*1048576,reserveBytes=512*1048576,initialAvailable=available,selfPeakRSS=rss,sourceGrammarAndIsolatedChildPeakRSS=child,conservativePeakSum=rss+child,finiteSeconds=30))
(O/'CHECKS.json').write_text(json.dumps(proof,indent=2)+'\n')
print(json.dumps(dict(status='PASS',sourceSealSHA256=proof['sourceSealSHA256'],caseCount=8,Bnamespace=174,resource=proof['resource'],checksSHA256=sha((O/'CHECKS.json').read_bytes()))))
