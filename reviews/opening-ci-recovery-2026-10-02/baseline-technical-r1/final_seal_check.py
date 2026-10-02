import pathlib,json,hashlib,re,ast,types,os,resource
P=pathlib.Path('/workspace/scratch/empty-intent-fresh-ci-source-r1');O=pathlib.Path('/workspace/scratch/empty-intent-fresh-ci-technical-r1')
def sha(b):return hashlib.sha256(b).hexdigest()
seal=(P/'SOURCE-SEAL.json').read_bytes();s=json.loads(seal);assert sha(seal)=='4fbe486e3042d4df7e2f30d082bf5f8ce9449defea62f7db409d8453fdab61bc'
mb=(P/'MANIFEST.json').read_bytes();m=json.loads(mb);assert sha(mb)==s['manifestSHA256']=='bf734b58262196a0e17ce271acf471e15dbde5be9473e9819d12cd902d5b2a38' and len(mb)==s['manifestBytes']
assert set(f.name for f in P.iterdir())==set(m['files'])|{'MANIFEST.json','SOURCE-SEAL.json'}
for name,(h,n) in m['files'].items():
 p=P/name;assert p.is_file() and not p.is_symlink();b=p.read_bytes();assert len(b)==n and sha(b)==h
total=sum(f.stat().st_size for f in P.iterdir());assert total==s['inclusiveFamilyBytes']==m['inclusiveFamilyBytes']==196014<=s['sourceCapBytes']==196608
chain=json.loads((P/'FAILED-DRAFT-INVERSE-CHAIN.json').read_bytes());final=(P/'rebuild-opening-baseline.yml').read_text();assert sha(final.encode())==chain['finalWorkflowSHA256']
previous=final
for new,old in chain['reverseLiteralReplacements']:
 assert new in previous;previous=previous.replace(new,old)
assert sha(previous.encode())==chain['previousCorrectedWorkflowSHA256']
delta=json.loads((P/'FAILED-DRAFT-GRAMMAR-DELTA.json').read_bytes());assert sha(previous.encode())==delta['correctedWorkflowSHA256']
def unified(source,diff,reverse=False):
 lines=source.splitlines(keepends=True);d=diff.splitlines(keepends=True);out=[];cursor=0;i=2
 while i<len(d):
  h=re.fullmatch(r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@.*\n',d[i]);assert h;index=int(h.group(3) if reverse else h.group(1))-1
  assert index>=cursor;out.extend(lines[cursor:index]);cursor=index;i+=1
  while i<len(d) and not d[i].startswith('@@ '):
   l=d[i];kind=l[0];text=l[1:];i+=1
   if reverse and kind in '+-':kind='-' if kind=='+' else '+'
   if kind in ' -':assert lines[cursor]==text;cursor+=1
   if kind in ' +':out.append(text)
 out.extend(lines[cursor:]);return ''.join(out)
failed=unified(previous,delta['inverseUnifiedDiff']);assert sha(failed.encode())==delta['failedWorkflowSHA256']==chain['verifiedFailedWorkflowSHA256']=='ad7eec8597f4a07fcecb62501affe536f01a962969a1bfbc3def6d2e87fa6877'
assert unified(failed,delta['inverseUnifiedDiff'],True)==previous
roundtrip=previous
for new,old in reversed(chain['reverseLiteralReplacements']):roundtrip=roundtrip.replace(old,new)
assert roundtrip==final
ownfailed=json.loads((O/'FAILED-DRAFT-DIAGNOSTIC-GRAMMAR.json').read_bytes());assert ownfailed['workflowSHA256ObservedAtFailure']==sha(failed.encode())
source=(P/'runner.py').read_bytes();t=ast.parse(source);nodes=[n for n in t.body if isinstance(n,ast.FunctionDef) and n.name in {'child_env','effective_available'}]
env={'os':types.SimpleNamespace(environ={'PATH':'/selected-node/bin:/usr/bin','HOME':'/synthetic-home','GITHUB_TOKEN':'secret','ACTIONS_RUNTIME_TOKEN':'secret','NODE_OPTIONS':'--require malicious','NODE_AUTH_TOKEN':'secret'}),'MIB':1048576}
exec(compile(ast.fix_missing_locations(ast.Module(body=nodes,type_ignores=[])),'offline_credential_and_headroom_guards','exec'),env)
e=env['child_env'](pathlib.Path('/synthetic-owned'));assert not any(k in e for k in ['GITHUB_TOKEN','ACTIONS_RUNTIME_TOKEN','NODE_AUTH_TOKEN']) and e['NODE_OPTIONS']=='--max-old-space-size=256' and e['npm_config_userconfig']==e['npm_config_globalconfig']=='/dev/null'
env['mem_available']=lambda:1000;env['cgroup_observation']=lambda:{'available':True,'max':'900','current':800};assert env['effective_available']()==100
env['cgroup_observation']=lambda:{'available':True,'max':'max','current':800};assert env['effective_available']()==1000
env['cgroup_observation']=lambda:{'available':False};assert env['effective_available']()==1000
official={}
for name,expected in [('OFFICIAL-SETUP-ACTION.yml','ef58e69919a94e6a823d333159fad95e2720c896'),('OFFICIAL-SETUP-README.md','92804e94eafa5f43c4856e93c808220b08929a15'),('OFFICIAL-SETUP-MAIN.ts','c36d8ec5af7d3c738de3dd7e5ac5faf281942d83'),('OFFICIAL-SETUP-DISTRIBUTION.ts','62999c3348624ee96ace2239fd4082eb69d56270')]:
 b=(O/name).read_bytes();assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==expected;official[name]={'gitBlobSHA1':expected,'sha256':sha(b),'bytes':len(b)}
current=int(pathlib.Path('/sys/fs/cgroup/memory.current').read_text());maximum=int(pathlib.Path('/sys/fs/cgroup/memory.max').read_text());assert maximum-current>=(64+512)*1048576
proof={'finalSourceOnly':True,'sourceSealSHA256':sha(seal),'manifestSHA256':sha(mb),'inclusiveSourceFamilyBytes':total,'all15ManifestMemberBytesHashesVerified':True,'noExtraOrSymlinkFiles':True,'methodSHA256':sha(source),'workflowSHA256':sha(final.encode()),'exactFailedWorkflowInverseAndForwardRoundtrip':True,'failedWorkflowSHA256':sha(failed.encode()),'extraPureCredentialHeadroomCases':4,'credentialFreeChildEnvironmentPass':True,'finiteCgroupAndHostMinHeadroomPass':True,'officialSetupNodeCommit':'49933ea5288caeca8642d1e84afbd3f7d6820020','officialPrimaryFiles':official,'ordinarySourceWorkBytes':64*1048576,'reserveBytes':512*1048576,'currentCgroupBytes':current,'cgroupMaximumBytes':maximum,'verifierPeakRSSBytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,'candidateMainNetworkArchiveNpmBuildTestExecuted':False,'qualification':'Final seal binds earlier final-hash grammar/metadata/path receipts despite their draft field labels. Inverse reconstructs the observed failed workflow exactly, without writing or executing it.'}
(O/'FINAL-SEAL-PROOF.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({k:v for k,v in proof.items() if k!='officialPrimaryFiles'}))
