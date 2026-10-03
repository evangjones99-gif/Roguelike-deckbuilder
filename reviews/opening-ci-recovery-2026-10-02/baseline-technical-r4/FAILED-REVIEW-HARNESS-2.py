import pathlib,json,hashlib,ast,re,yaml,resource,signal,subprocess,shutil,time,zipfile
P=pathlib.Path('/workspace/scratch/empty-intent-fresh-ci-source-r4');OLD=pathlib.Path('/workspace/scratch/empty-intent-fresh-ci-source-r3');O=pathlib.Path('/workspace/scratch/empty-intent-fresh-ci-technical-r4')
signal.alarm(45)
def sha(b):return hashlib.sha256(b).hexdigest()
def pins(root):return {f.relative_to(root).as_posix():[sha(f.read_bytes()),f.stat().st_size] for f in root.rglob('*') if f.is_file()}
host=int(next(l.split()[1] for l in pathlib.Path('/proc/meminfo').read_text().splitlines() if l.startswith('MemAvailable:')))*1024
cg=pathlib.Path('/sys/fs/cgroup');maximum=(cg/'memory.max').read_text().strip();current=int((cg/'memory.current').read_text());headroom=host if maximum=='max' else min(host,int(maximum)-current)
assert headroom>=(64+512)*1048576 and shutil.disk_usage(O).free>=24*1048576
before=pins(P);oldpins=pins(OLD)
sb=(P/'SOURCE-SEAL.json').read_bytes();s=json.loads(sb);assert sha(sb)=='51f4e42e9ca6d846ad6edd93cb0445936becdf07a7230204c9b9e4ebb71a1080'
mb=(P/'MANIFEST.json').read_bytes();m=json.loads(mb);assert sha(mb)==s['manifestSHA256']=='1c8b2dea0a033a26abf203598f321b32bb61a79959a7da94bdbef4f9378dad70' and len(mb)==s['manifestBytes']
assert not any(f.is_symlink() for f in P.rglob('*'))
assert set(before)==set(m['files'])|{'MANIFEST.json','SOURCE-SEAL.json'}
assert {k:v for k,v in before.items() if k not in ('MANIFEST.json','SOURCE-SEAL.json')}==m['files']
total=sum(x[1] for x in before.values());assert total==s['inclusiveFamilyBytes']==m['inclusiveFamilyBytes']==230709<=s['sourceCapBytes']==262144
prov=json.loads((P/'PROVENANCE.json').read_bytes());assert sha((OLD/'SOURCE-SEAL.json').read_bytes())==prov['parentSealSHA256']=='03a79c3c83060e69775bbc7cf13692034920a5ec63ce4c34a65e43aa9362f071'
assert sha((OLD/'MANIFEST.json').read_bytes())==prov['parentManifestSHA256']
assert sha(pathlib.Path('/workspace/scratch/empty-intent-fresh-ci-technical-r3/GATE.json').read_bytes())=='2656f60240a9b5e067a3a216bb61a1bea4cf265dd2541b8a8d20faad35f7d9ed'
for name in prov['unchangedPayloads']:assert (P/name).read_bytes()==(OLD/name).read_bytes()
failure=pathlib.Path(prov['actualFailureDirectory']);fpins=pins(failure)
for name,h in prov['actualFailurePins'].items():assert sha((failure/name).read_bytes())==h
text=(P/'runner.py').read_text();old=(OLD/'runner.py').read_text();a=ast.parse(old);b=ast.parse(text);compile(b,'candidate_grammar_only','exec')
am={n.name:ast.dump(n,include_attributes=False) for n in a.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))};bm={n.name:ast.dump(n,include_attributes=False) for n in b.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
assert set(bm)-set(am)=={'canonical_bin_map','observed_bin'} and not(set(am)-set(bm))
assert [n for n in am if am[n]!=bm[n]]==['provision_audit']
astother=lambda t:ast.dump(ast.Module(body=[n for n in t.body if not isinstance(n,(ast.FunctionDef,ast.ClassDef))],type_ignores=[]),include_attributes=False)
assert astother(a)==astother(b)
wold=yaml.load((OLD/'rebuild-opening-baseline.yml').read_bytes(),Loader=yaml.BaseLoader);w=yaml.load((P/'rebuild-opening-baseline.yml').read_bytes(),Loader=yaml.BaseLoader)
init=w['jobs']['fresh-baseline']['steps'][0]['run'];oldinit=wold['jobs']['fresh-baseline']['steps'][0]['run']
assert init.replace(text,old).replace(sha(text.encode()),sha(old.encode()))==oldinit
w['jobs']['fresh-baseline']['steps'][0]['run']=oldinit;assert w==wold
tree=ast.parse(pathlib.Path('/workspace/scratch/empty-intent-fresh-ci-technical-r1/final_seal_check.py').read_bytes());fun=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='unified');env={'re':re};exec(compile(ast.Module(body=[fun],type_ignores=[]),'exact_delta_decoder','exec'),env)
roundtrips=[]
for direction,starting,ending in [('INVERSE.json',P,OLD),('FORWARD.json',OLD,P)]:
    d=json.loads((P/direction).read_bytes());assert set(d['files'])=={'runner.py','rebuild-opening-baseline.yml','shared_shim_checks.py'}
    for name,v in d['files'].items():
        new=(P/name).read_text();prev=(OLD/name).read_text();assert sha(new.encode())==v['R4SHA256'] and sha(prev.encode())==v['R3SHA256']
        start=(starting/name).read_text();end=(ending/name).read_text()
        assert env['unified'](start,v['unifiedDiff'])==end and env['unified'](end,v['unifiedDiff'],True)==start
        roundtrips.append(dict(direction=direction,file=name))
harness=json.loads((P/'FAILED-BIN-CASE-HARNESS-1.json').read_bytes());fixed=(P/'shared_shim_checks.py').read_text();assert sha(fixed.encode())==harness['correctedHarnessSHA256'];newstr,oldstr=harness['reverseLiteralReplacement'];assert fixed.count(newstr)==1;assert sha(fixed.replace(newstr,oldstr).encode())==harness['failedHarnessSHA256']
# Run only retained pure synthetic helpers; delete top-level receipt writers before compilation.
pure=[]
for name,resultvar in [('source_checks.py','receipt'),('shared_shim_checks.py','result')]:
    t=ast.parse((P/name).read_bytes())
    kept=[]
    for n in t.body:
        if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='ROOT' for x in n.targets):
            n.value=ast.Call(func=ast.Name(id='Path',ctx=ast.Load()),args=[ast.Constant(str(P))],keywords=[]);ast.fix_missing_locations(n)
        if isinstance(n,ast.With) and any(isinstance(item.context_expr,ast.Call) and isinstance(item.context_expr.func,ast.Attribute) and item.context_expr.func.attr=='open' for item in n.items):continue
        if isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Name) and n.value.func.id=='print':continue
        kept.append(n)
    ns={'__name__':'review_pure_synthetic','__file__':str(O/name)}
    run=subprocess.run
    def finite_run(*args,**kwargs):
        kwargs['timeout']=min(kwargs.get('timeout',10),10)
        return run(*args,**kwargs)
    subprocess.run=finite_run
    try:exec(compile(ast.Module(body=kept,type_ignores=[]),name+'_pure_only','exec'),ns)
    finally:subprocess.run=run
    val=ns[resultvar]
    pure.append(dict(name=name,methodSHA256=val['methodSHA256'],caseCount=val.get('caseCount',len(val['cases'])),cases=val['cases'],sourceReceiptWriterRemoved=True))
    if name=='shared_shim_checks.py':audit_ns=ns
# Independent extra probes: exact helpers from candidate, synthetic filesystem only.
extra=[]
for key in ['node','npm','tsc','vite','tsx']:
    audit_ns['actual_bin_overrides'].clear()
    audit_ns['actual_bin_overrides']['vite' if key!='vite' else 'tsx']={'vite':'bin/vite.js',key:'bin/shadow'} if key!='vite' else {'tsx':'dist/cli.mjs','vite':'bin/shadow'}
    prev=len(audit_ns['receipts'])
    try:audit_ns['env']['provision_audit'](audit_ns['FakePath']('/owned'),{'tools':audit_ns['pins'],'expectedNodeVersion':'v24.19.0'})
    except ValueError as e:assert str(e)=='unused bin command conflicts with fixed execution scope'
    else:raise AssertionError('shadow admission '+key)
    assert len(audit_ns['receipts'])>prev and audit_ns['receipts'][-1]['diagnosticOnlyNotAdmission']
    extra.append('reject_extra_'+key+'_shadow_before_admission')
cn=audit_ns['env']['canonical_bin_map']
for value in [{'':'bin/vite.js'},{'bad/name':'bin/vite.js'},{'vite':'bin//vite.js'},{'vite':'./'},{'vite':'C:\\outside'},{'vite':'bin/./vite.js'},{'vite':'bin/vite.js','unused':'/outside'}]:
    try:cn(value,'vite')
    except ValueError:pass
    else:raise AssertionError('unsafe mapping passed')
    extra.append('reject_'+repr(value))
assert cn({'vite':'././bin/vite.js'},'vite')=={'vite':'bin/vite.js'}
extra.append('leading_dot_components_only_normalize')
ov=audit_ns['env']['observed_bin']({'unused':'x'*20000})
assert ov['complete'] is False and ov['serializedBytes']>8192 and len(ov['prefix'].encode())<=1024 and re.fullmatch('[0-9a-f]{64}',ov['serializedSHA256'])
extra.append('oversized_diagnostic_retains_qualified_hash_prefix')
# Verify actual failure transport metadata and opaque members, no extraction.
rootproof=json.loads((failure/'ROOT-TRANSFER-VERIFICATION.json').read_bytes());expect={x['path']:x for x in rootproof['entries']}
h=hashlib.sha256()
with (failure/'TRANSPORT.zip').open('rb') as f:
    for chunk in iter(lambda:f.read(65536),b''):h.update(chunk)
assert h.hexdigest()==rootproof['zipSHA256']=='5fc4c60c21b4b7c6b5e321c14a595bf8f4ce5ebdf12ae3b2729d3d5822161db2'
members=[]
with zipfile.ZipFile(failure/'TRANSPORT.zip') as z:
    assert len(z.infolist())==17 and set(z.namelist())==set(expect)
    for name in z.namelist():
        hh=hashlib.sha256();n=0
        with z.open(name) as f:
            for chunk in iter(lambda:f.read(65536),b''):hh.update(chunk);n+=len(chunk)
        v=dict(path=name,sha256=hh.hexdigest(),bytes=n);assert v==expect[name]
        assert sha((failure/name).read_bytes())==v['sha256'];members.append(v)
closure=json.loads((failure/'install-closure.json').read_bytes());refusal=json.loads((failure/'install-failure.json').read_bytes())
assert closure['status']=='PASS' and closure['exit']==0 and closure['closureObserved'] and closure['liveAtClosure']==[]
assert refusal=={'exceptionType':'ValueError','message':'actual executable bin metadata','phase':'install','status':'FAILED'}
job=json.loads((O/'CONNECTED-FAILURE-JOBS.json').read_bytes())['jobs'][0];assert job['id']==111000067291 and job['run_id']==37055795326 and job['conclusion']=='failure'
assert all(x['conclusion']=='skipped' for x in job['steps'] if x['name'] in ['Build the original source under independent observed limits','Run the eight original top level unit files separately'])
assert before==pins(P) and oldpins==pins(OLD) and fpins==pins(failure)
rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024;child=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss*1024;assert rss+child<=64*1048576
proof=dict(verdict='PASS_SOURCE_ONLY',sourceSealSHA256=sha(sb),manifestSHA256=sha(mb),sourceInclusiveBytes=total,sourceCap=262144,methodSHA256=sha(text.encode()),workflowSHA256=sha((P/'rebuild-opening-baseline.yml').read_bytes()),sourceFiles=before,parentR3SealAndAcceptedGateVerified=True,onlyRunnerChangedFunctions=['provision_audit'],onlyAddedFunctions=['canonical_bin_map','observed_bin'],allOtherRunnerASTExact=True,allOtherWorkflowFieldsAndRunBlocksByteExact=True,completeInverseForwardRoundtrips=roundtrips,failedAuthorSyntheticHarnessExactInverseVerified=True,pureAuthorCasesReexecutedWithoutSourceWrites=pure,independentAdditionalCases=extra,actualFailure=dict(run=37055795326,job=111000067291,artifact=11248582221,zipSHA256=rootproof['zipSHA256'],members=members,installClosure=closure,refusal=refusal,installedBinCause='UNOBSERVED: no installed package metadata in artifact',buildTests='SKIPPED'),ordinaryResource=dict(workBytes=64*1048576,reserveBytes=512*1048576,initialMinimumHeadroom=headroom,selfPeakRSS=rss,grammarChildPeakRSS=child,conservativePeakSum=rss+child,finiteSeconds=45),allFrozenPacketsAndActualFailureUnchanged=True,noMainNetworkInstallBuildTestBrowserExecution=True,atimeMayChange=True,grammarChildOnly=True)
(O/'CHECKS.json').write_text(json.dumps(proof,indent=2)+'\n')
print(json.dumps(dict(status='PASS',caseCount=sum(x['caseCount'] for x in pure)+len(extra),ordinary=proof['ordinaryResource'],checkSHA256=sha((O/'CHECKS.json').read_bytes()))))
