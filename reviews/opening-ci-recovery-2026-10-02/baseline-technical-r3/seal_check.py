import pathlib,json,hashlib,ast,re,yaml,resource
P=pathlib.Path('/workspace/scratch/empty-intent-fresh-ci-source-r3');R2=pathlib.Path('/workspace/scratch/empty-intent-fresh-ci-source-r2');T2=pathlib.Path('/workspace/scratch/empty-intent-fresh-ci-technical-r2');O=pathlib.Path('/workspace/scratch/empty-intent-fresh-ci-technical-r3')
def sha(b):return hashlib.sha256(b).hexdigest()
sb=(P/'SOURCE-SEAL.json').read_bytes();s=json.loads(sb);assert sha(sb)=='03a79c3c83060e69775bbc7cf13692034920a5ec63ce4c34a65e43aa9362f071'
mb=(P/'MANIFEST.json').read_bytes();m=json.loads(mb);assert sha(mb)==s['manifestSHA256']=='a060e483ae571df407a96f4a740de43832975afdfc03b138cafea42fbec612d0' and len(mb)==s['manifestBytes']
for f in P.rglob('*'):assert not f.is_symlink()
observed={f.relative_to(P).as_posix() for f in P.rglob('*') if f.is_file()};assert observed==set(m['files'])|{'MANIFEST.json','SOURCE-SEAL.json'}
for name,(h,n) in m['files'].items():
 b=(P/name).read_bytes();assert len(b)==n and sha(b)==h
total=sum(f.stat().st_size for f in P.rglob('*') if f.is_file());assert total==s['inclusiveFamilyBytes']==m['inclusiveFamilyBytes']==196446<=s['sourceCapBytes']==196608
prov=json.loads((P/'PROVENANCE.json').read_bytes());assert sha((R2/'SOURCE-SEAL.json').read_bytes())==prov['parentSealSHA256']=='617c0a6007c8ae9734fe0f547645745558a6cdc1666a1b46dad12bb37f0e0629'
assert sha((R2/'MANIFEST.json').read_bytes())==prov['parentManifestSHA256']
assert sha((T2/'GATE.json').read_bytes())=='a171b1c18153df20a8e7efa9e479901adb790e474fd31b1eb7143b13eadfdfeb'
for name in prov['unchangedPayloads']:assert (P/name).read_bytes()==(R2/name).read_bytes()
for name,h in prov['actualFailurePins'].items():assert sha((pathlib.Path(prov['actualFailureDirectory'])/name).read_bytes())==h
a=ast.parse((R2/'runner.py').read_bytes());b=ast.parse((P/'runner.py').read_bytes());assert len(a.body)==len(b.body)
changed=[]
for x,y in zip(a.body,b.body):
 if ast.dump(x,include_attributes=False)!=ast.dump(y,include_attributes=False):
  assert isinstance(x,ast.FunctionDef) and isinstance(y,ast.FunctionDef) and x.name==y.name=='child_env';changed.append(x.name)
assert changed==['child_env']
old=(R2/'runner.py').read_text();new=(P/'runner.py').read_text();h1=sha(old.encode());h2=sha(new.encode())
w2=yaml.load((R2/'rebuild-opening-baseline.yml').read_bytes(),Loader=yaml.BaseLoader);w3=yaml.load((P/'rebuild-opening-baseline.yml').read_bytes(),Loader=yaml.BaseLoader)
r2=w2['jobs']['fresh-baseline']['steps'][0]['run'];r3=w3['jobs']['fresh-baseline']['steps'][0]['run'];w3['jobs']['fresh-baseline']['steps'][0]['run']=r2;assert w3==w2
def initializer(run):return ast.parse(run.split("python3 -I -B - <<'PY'\n",1)[1].rsplit('\nPY',1)[0])
i2=initializer(r2);i3=initializer(r3);removed=[]
for n in list(i3.body):
 if isinstance(n,ast.For) and isinstance(n.target,ast.Name) and n.target.id=='config_name':
  assert ast.literal_eval(n.iter)==('npm-user.npmrc','npm-global.npmrc');i3.body.remove(n);removed.append('exclusive config loop')
 elif isinstance(n,ast.Assert) and 'st_ino' in ast.unparse(n):
  i3.body.remove(n);removed.append('distinct inode check')
for n in ast.walk(i3):
 if isinstance(n,ast.Constant) and n.value==new:n.value=old
 elif isinstance(n,ast.Constant) and n.value==h2:n.value=h1
 elif isinstance(n,ast.Dict):
  extras={'ownedEmptyNpmConfigFiles','npmConfigBytes','npmConfigSHA256','distinctConfigInodes'}
  pairs=[(k,v) for k,v in zip(n.keys,n.values) if not (isinstance(k,ast.Constant) and k.value in extras)]
  n.keys=[k for k,v in pairs];n.values=[v for k,v in pairs]
assert len(removed)==2 and ast.dump(i3,include_attributes=False)==ast.dump(i2,include_attributes=False)
tree=ast.parse((pathlib.Path('/workspace/scratch/empty-intent-fresh-ci-technical-r1')/'final_seal_check.py').read_bytes());f=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='unified');env={'re':re};exec(compile(ast.Module(body=[f],type_ignores=[]),'offline_exact_inverse_decoder','exec'),env)
inverse=json.loads((P/'INVERSE.json').read_bytes());roundtrips=[]
for name,v in inverse['files'].items():
 r3=(P/name).read_text();r2=(R2/name).read_text();assert sha(r3.encode())==v['R3SHA256'] and sha(r2.encode())==v['R2SHA256']
 assert env['unified'](r3,v['inverseUnifiedDiff'])==r2 and env['unified'](r2,v['inverseUnifiedDiff'],True)==r3;roundtrips.append(name)
assert set(roundtrips)=={'runner.py','rebuild-opening-baseline.yml','source_checks.py'}
current=int(pathlib.Path('/sys/fs/cgroup/memory.current').read_text());maximum=int(pathlib.Path('/sys/fs/cgroup/memory.max').read_text());assert maximum-current>=(64+512)*1048576
proof={'sourceOnly':True,'sourceSealSHA256':sha(sb),'manifestSHA256':sha(mb),'recursiveFamilyBytes':total,'allRecursiveManifestBodiesVerified':True,'parentR2SealAndAcceptedGateVerified':True,'parentAcceptedGateSHA256':'a171b1c18153df20a8e7efa9e479901adb790e474fd31b1eb7143b13eadfdfeb','actualFailureExternalPinsVerified':True,'onlyChangedRunnerAST':'child_env','onlyChangedWorkflowRun':'initialize','initializationChangesOnly':'two exclusive regular empty npm configs, distinct inode check, matching proof metadata and new exact method literal/hash','allOtherWorkflowFieldsRunsAndRunnerFunctionsByteExact':True,'completeInverseForwardRoundtrips':roundtrips,'methodSHA256':h2,'workflowSHA256':sha((P/'rebuild-opening-baseline.yml').read_bytes()),'source98Support30Blob53PinsUnchanged':True,'independentPathHeaderStreamCases':32,'independentConfigEnvironmentCases':4,'allNineShellGrammarPassed':True,'candidateMainNetworkArchiveNpmBuildTestsExecutedByReviewer':False,'authorAuthorizedOfflineNpmVersionOnlyReproVerified':True,'actualR3CIResultAccepted':False,'ordinaryWorkBytes':64*1048576,'reserveBytes':512*1048576,'initialCgroupCurrent':current,'cgroupMaximum':maximum,'thisVerifierPeakRSSBytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,'qualification':'Source-only configuration repair after verified preflight failure. No game bug claim; acquisition/assembly receipts in failed run do not supply downloaded runner-stage bodies. Actual installed/build/test/browser behavior remains pending.'}
(O/'FINAL-SEAL-PROOF.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof))
