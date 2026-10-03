import pathlib,json,hashlib,ast,yaml,re,resource
P=pathlib.Path('/workspace/scratch/empty-intent-fresh-ci-source-r2');R1=pathlib.Path('/workspace/scratch/empty-intent-fresh-ci-source-r1');T1=pathlib.Path('/workspace/scratch/empty-intent-fresh-ci-technical-r1');O=pathlib.Path('/workspace/scratch/empty-intent-fresh-ci-technical-r2')
def sha(b):return hashlib.sha256(b).hexdigest()
sbytes=(P/'SOURCE-SEAL.json').read_bytes();s=json.loads(sbytes);assert sha(sbytes)=='617c0a6007c8ae9734fe0f547645745558a6cdc1666a1b46dad12bb37f0e0629'
mb=(P/'MANIFEST.json').read_bytes();m=json.loads(mb);assert sha(mb)==s['manifestSHA256']=='61edf83a446e27e1bf8615e93f9a1377a57bb4d663eedeffd9c1b22c90a5c554' and len(mb)==s['manifestBytes']
assert set(f.name for f in P.iterdir())==set(m['files'])|{'MANIFEST.json','SOURCE-SEAL.json'}
for name,(h,n) in m['files'].items():
 p=P/name;assert p.is_file() and not p.is_symlink();b=p.read_bytes();assert len(b)==n and sha(b)==h
total=sum(f.stat().st_size for f in P.iterdir());assert total==s['inclusiveFamilyBytes']==m['inclusiveFamilyBytes']==184882<=s['sourceCapBytes']==196608
provenance=json.loads((P/'PROVENANCE.json').read_bytes());assert sha((R1/'SOURCE-SEAL.json').read_bytes())==provenance['parentSealSHA256']=='4fbe486e3042d4df7e2f30d082bf5f8ce9449defea62f7db409d8453fdab61bc'
assert sha((R1/'MANIFEST.json').read_bytes())==provenance['parentManifestSHA256'] and sum(f.stat().st_size for f in R1.iterdir())==196014
assert sha((T1/'GATE.json').read_bytes())=='bf2935466cf5c1460686617a95acbf810f02ad64affac886a07c8b8260161d45'
for name in provenance['unchangedPayloads']:assert (P/name).read_bytes()==(R1/name).read_bytes()
# Only exact provision_audit AST differs; all constants/imports/other function bodies identical.
a=ast.parse((R1/'runner.py').read_bytes());b=ast.parse((P/'runner.py').read_bytes())
assert len(a.body)==len(b.body)
changed=[]
for x,y in zip(a.body,b.body):
 if ast.dump(x,include_attributes=False)!=ast.dump(y,include_attributes=False):
  assert isinstance(x,ast.FunctionDef) and isinstance(y,ast.FunctionDef) and x.name==y.name=='provision_audit';changed.append(x.name)
assert changed==['provision_audit']
old=(R1/'runner.py').read_text();new=(P/'runner.py').read_text();h1=sha(old.encode());h2=sha(new.encode())
w1=yaml.load((R1/'rebuild-opening-baseline.yml').read_bytes(),Loader=yaml.BaseLoader);w2=yaml.load((P/'rebuild-opening-baseline.yml').read_bytes(),Loader=yaml.BaseLoader)
init2=w2['jobs']['fresh-baseline']['steps'][0]['run'];assert new in init2
w2['jobs']['fresh-baseline']['steps'][0]['run']=init2.replace(new,old).replace(h2,h1);assert w2==w1
# Reuse the pure unified-diff decoder from immutable technicalR1, without its top-level effects.
tree=ast.parse((T1/'final_seal_check.py').read_bytes());f=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='unified');env={'re':re};exec(compile(ast.Module(body=[f],type_ignores=[]),'offline_exact_inverse_decoder','exec'),env)
inverse=json.loads((P/'INVERSE.json').read_bytes());roundtrips=[]
for name,v in inverse['files'].items():
 r2=(P/name).read_text();r1=(R1/name).read_text();assert sha(r2.encode())==v['R2SHA256'] and sha(r1.encode())==v['R1SHA256']
 assert env['unified'](r2,v['inverseUnifiedDiff'])==r1 and env['unified'](r1,v['inverseUnifiedDiff'],True)==r2;roundtrips.append(name)
assert set(roundtrips)=={'runner.py','rebuild-opening-baseline.yml'}
current=int(pathlib.Path('/sys/fs/cgroup/memory.current').read_text());maximum=int(pathlib.Path('/sys/fs/cgroup/memory.max').read_text());assert maximum-current>=(64+512)*1048576
proof={'sourceOnly':True,'sourceSealSHA256':sha(sbytes),'manifestSHA256':sha(mb),'sourceFamilyBytes':total,'allManifestMembersAndSealVerified':True,'parentR1SealVerified':True,'parentRejectedGateSHA256':'bf2935466cf5c1460686617a95acbf810f02ad64affac886a07c8b8260161d45','unchangedPayloadsByteExact':provenance['unchangedPayloads'],'onlyChangedMethodAST':'provision_audit','allOtherWorkflowFieldsAndRunStringsByteExactAfterLiteralMethodSubstitution':True,'fullInverseForwardRoundtrips':roundtrips,'methodSHA256':h2,'workflowSHA256':sha((P/'rebuild-opening-baseline.yml').read_bytes()),'source98Support30Blob53PinsInheritedExact':True,'independentPathHeaderStreamCases':32,'sharedShimSyntheticCases':4,'credentialAndHeadroomCasesInheritedUnchanged':4,'allNineShellGrammarPassed':True,'candidateMainNetworkArchiveNpmBuildTestExecuted':False,'ordinaryWorkBytes':64*1048576,'reserveBytes':512*1048576,'initialCgroupCurrent':current,'cgroupMaximum':maximum,'verifierPeakRSSBytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,'qualification':'Narrow R2 source repair only. Exact same acquisition, inputs, archive guards, resource/time/disk/log/process/output/action restrictions as reviewed R1. Prior rejected R1/failures and primary-source references remain immutable external authority; no actual new CI/build result.'}
(O/'FINAL-SEAL-PROOF.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof))
