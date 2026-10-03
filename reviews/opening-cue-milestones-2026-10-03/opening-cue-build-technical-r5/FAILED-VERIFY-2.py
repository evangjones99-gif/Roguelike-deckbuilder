"""Independent read-only fixed C build SOURCE audit. Never import runner or execute phases."""
import ast,base64,gzip,hashlib,json,pathlib,re,resource,subprocess,time
import yaml
P=pathlib.Path('/workspace/scratch/opening-cue-build-source-r5')
B=pathlib.Path('/workspace/scratch/empty-intent-fresh-ci-source-r10')
O=pathlib.Path(__file__).parent
start=time.monotonic()
def sha(b):return hashlib.sha256(b).hexdigest()
def read(p):return p.read_bytes()
def load(p):return json.loads(read(p))
def identity(p):
    size=p.stat().st_size;h=hashlib.sha256();g=hashlib.sha1(f'blob {size}\0'.encode());n=0
    with p.open('rb') as f:
        for b in iter(lambda:f.read(65536),b''):h.update(b);g.update(b);n+=len(b)
    assert n==size
    return {'bytes':n,'sha256':h.hexdigest(),'gitBlobSHA1':g.hexdigest()}
physical={f.relative_to(P).as_posix():identity(f) for f in P.rglob('*') if f.is_file()}
assert not any(f.is_symlink() for f in P.rglob('*'))
seal=load(P/'SOURCE-SEAL.json');manifest=load(P/'MANIFEST.json')
assert set(physical)==set(seal['sealedFiles'])|{'SOURCE-SEAL.json'}
for n,r in seal['sealedFiles'].items():assert all(physical[n][k]==v for k,v in r.items()),n
assert physical['MANIFEST.json']['sha256']==seal['manifestSHA256']
assert sum(physical[n]['bytes'] for n in manifest['filesExcludingManifestAndSeal'])==manifest['bytesExcludingManifestAndSeal']
assert set(manifest['filesExcludingManifestAndSeal'])==set(physical)-{'MANIFEST.json','SOURCE-SEAL.json'}
assert sum(x['bytes'] for x in physical.values())<=manifest['sourceCapBytes']==2097152
adapt=load(P/'ADAPTATION.json');shared=adapt['sharedMethod']
assert identity(B/'SOURCE-SEAL.json')['sha256']==shared['sourceSealSHA256']
assert identity(B/'MANIFEST.json')['sha256']==shared['manifestSHA256']
base_seal=load(B/'SOURCE-SEAL.json');base_manifest=load(B/'MANIFEST.json')
# Reuse the exact independently reviewed base by its complete identity.
basegate_path=pathlib.Path('/workspace/scratch/empty-intent-fresh-ci-technical-r10/GATE.json')
basegate=load(basegate_path)
assert basegate['verdict']=='ACCEPT_SOURCE_ONLY' and basegate['sourceSeal']['sha256']==shared['sourceSealSHA256']
for n,r in shared['files'].items():assert all(identity(B/n)[k]==v for k,v in r.items())
for key,n in [('sourceChecker','verify_source.py'),('checks','SOURCE-CHECKS.json'),('review','REVIEW.md'),('fixtureClosureChecker','verify_fixture_closure.py'),('fixtureClosureChecks','FIXTURE-CLOSURE-CHECKS.json')]:
    r=basegate[key];assert all(identity(basegate_path.parent/n)[k]==v for k,v in r.items())
old={}
for n,r in adapt['predecessorFiles'].items():
    b=read(P/r['inverseBody'])
    if r.get('inverseEncoding','').startswith('gzip'):b=gzip.decompress(b)
    if r['inverseEncoding']=='gzip-workflow-template-plus-exact-parent-runner':
        assert b.count(b'{{EXACT_PARENT_RUNNER}}')==1
        b=b.replace(b'{{EXACT_PARENT_RUNNER}}',old['runner.py'].decode().replace('\n','\n          ')[:-10].encode())
    assert len(b)==r['bytes'] and sha(b)==r['sha256'] and b==read(pathlib.Path(adapt['predecessorDirectory'])/n)
    old[n]=b
assert identity(pathlib.Path(adapt['predecessorDirectory'])/'SOURCE-SEAL.json')['sha256']==adapt['predecessorSourceSealSHA256']
assert identity(pathlib.Path(adapt['predecessorDirectory'])/'MANIFEST.json')['sha256']==adapt['predecessorManifestSHA256']
source=read(P/'runner.py').decode();base=read(B/'runner.py').decode();tree=ast.parse(source);prior=ast.parse(base)
const={}
for n in tree.body:
    if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name):
        try:const[n.targets[0].id]=ast.literal_eval(n.value)
        except ValueError:pass
literal=gzip.decompress(base64.b64decode(const['META_LITERAL'],validate=True))
assert literal==read(P/'METADATA.json') and sha(literal)==const['META_SHA']
transformed=re.sub(r'^META_LITERAL = ".*"$', 'META_LITERAL = '+json.dumps(base64.b64encode(gzip.compress(literal,mtime=0)).decode()),base,count=1,flags=re.M)
for r in adapt['replacementsExceptMetadataLiteral']:
    assert transformed.count(r['before'])==r['count'];transformed=transformed.replace(r['before'],r['after'])
assert transformed==source
def functions(t,s):return {x.name:ast.get_source_segment(s,x) for x in t.body if isinstance(x,(ast.FunctionDef,ast.ClassDef))}
current=functions(tree,source);oldfunctions=functions(prior,base);assert set(current)==set(oldfunctions)
changed=[n for n in oldfunctions if oldfunctions[n]!=current[n]]
assert changed==['metadata','context','fetch_blob','acquire','assemble','membership','seal_output']
unchanged=sorted(set(current)-set(changed))
for key in ['run_phase','sampled_inventory','supervisor_fault','mutation_roots','provision_audit','phase','diagnostic','main']:
    assert current[key]==oldfunctions[key]
meta=json.loads(literal);parent=json.loads(gzip.decompress(read(P/'PARENT-SOURCE.json.gz')))
digest=lambda rows:sha(json.dumps(dict(sorted((r['path'],r['sha256']) for r in rows)),separators=(',',':')).encode())
assert len(meta['source'])==104 and len(meta['support'])==32 and len(meta['blobPins'])==59
assert len({r['path'] for r in meta['source']+meta['support']})==136
assert digest(meta['source'])==meta['sourceDigest']==manifest['candidateSourceDigest']=='993aa3681596c2488d4d394744e5beda2778ffcba3e1649736612304d20b50c5'
assert digest(parent['source'])==parent['sourceDigest']=='65b31b3f21e34a624bdac962e4919c7dc1791e502eb6cfdb1612103b8036fe9c'
cm={r['path']:r['sha256'] for r in meta['source']};bm={r['path']:r['sha256'] for r in parent['source']}
assert set(cm)==set(bm) and [n for n in cm if cm[n]!=bm[n]]==['src/main.ts']
assert cm['src/main.ts']=='87a9bd7c2319522f77db7ea9e2edc306bb6124b019306dc220087f6b9b7762f4'
oldmeta=json.loads(old['METADATA.json']);fixture_path=pathlib.Path('/workspace/scratch/opening-ci-original-test-fixtures-root-r1/FIXTURE-PINS.json')
fixtures=load(fixture_path)['files'];assert len(fixtures)==2
fixture_map={r['path']:r for r in fixtures}
assert meta['source']==oldmeta['source']
assert [r for r in meta['support'] if r['path'] not in fixture_map]==oldmeta['support']
assert [r for r in meta['blobPins'] if r['sha256'] not in {r['sha256'] for r in fixtures}]==oldmeta['blobPins']
assert digest([r for r in meta['support'] if r['path'] not in fixture_map])=='b21a0766a30f581221ad009e448f4f9c103efe017682e462ce1548263ada327e'
assert meta['tools']==oldmeta['tools'] and meta['scripts']==oldmeta['scripts'] and meta['expectedNodeVersion']=='v24.19.0'
assert sum(r['path'].startswith('public/') for r in meta['source'])==65 and meta['expectedOutputCount']==70
tests=[r['path'] for r in meta['support'] if re.fullmatch(r'tests/[^/]+\.test\.ts',r['path'])];assert len(tests)==8
blobmap={r['sha256']:r for r in meta['blobPins']};assert len(blobmap)==59
local={};direct={}
for collection,rows in [('source',meta['source']),('support',meta['support'])]:
    for r in rows:
        assert not pathlib.PurePosixPath(r['path']).is_absolute() and '..' not in pathlib.PurePosixPath(r['path']).parts
        p=pathlib.Path('/workspace/scratch/starter-static-recovered-stage-r1')/r['path'] if collection=='source' else pathlib.Path('/workspace/scratch/empty-intent-source-recovered-stage-r1')/r['path']
        if collection=='source' and r['path']=='src/main.ts':p=pathlib.Path('/workspace/scratch/opening-cue-milestones-source-r1/src/main.ts')
        if r['path'] in fixture_map:
            fp=fixture_map[r['path']];p=pathlib.Path(fp['bodyPath']);assert fp['sourceRef']=='fbb617eff4b6ed04ea866ed57751ba23d8b6097d'
            assert all(identity(p)[k]==fp[k] for k in ('bytes','sha256','gitBlobSHA1'))
        actual=identity(p);assert actual['bytes']==r['bytes'] and actual['sha256']==r['sha256']
        local[r['path']]=actual
        if 'blob' in r:
            pin=blobmap[r['blob']];assert r['blob']==r['sha256']
            assert all(actual[k]==pin[k] for k in ('bytes','sha256','gitBlobSHA1'));direct[r['blob']]=actual
        else:assert r['archive'] in ('8cdf','4513','ce0f')
archives=[pathlib.Path('/workspace/scratch/archive8cdf-acquired-r1/evidence-8cdf546a8429e949fe88611d781aca341566f473135fbcbe44b5373beabd7aa8.tar.gz'),pathlib.Path('/workspace/scratch/opening-runtime-bytes-acquired-r2/containers/bodies/evidence-451347c174a3fe78e5f7b6ef22736b7cfbbd33b39fd04ea20556730bb3b15a8b.tar.gz'),pathlib.Path('/workspace/scratch/opening-runtime-bytes-acquired-r2/containers/bodies/evidence-ce0f8f40bcf0f0b22e5e4d93eef3d4660662826e617900aba09ac208c148dc13.tar.gz')]
assert [r['id'] for r in meta['blobPins'][-3:]]==['8cdf','4513','ce0f'] and len(direct)==56
for p,pin in zip(archives,meta['blobPins'][-3:]):
    actual=identity(p);assert all(actual[k]==pin[k] for k in ('bytes','sha256','gitBlobSHA1'));direct[pin['sha256']]=actual
assert set(direct)==set(blobmap)
closure=load(basegate_path.parent/'FIXTURE-CLOSURE-CHECKS.json')
assert closure['status']=='PASS_EXACT_TWO_PRIMARY_FIXTURES_STATIC_TEST_IMPORT_CLOSURE'
assert 'src/main.ts' not in closure['closureBodies']
for name,pin in closure['closureBodies'].items():
    if name!='src/art.ts':assert all(local[name][k]==v for k,v in pin.items())
art_a=read(pathlib.Path('/workspace/scratch/empty-intent-source-recovered-stage-r1/src/art.ts')).decode()
art_c=read(pathlib.Path('/workspace/scratch/starter-static-recovered-stage-r1/src/art.ts')).decode()
marker='export const COHERENT_NATIVE128 = '
assert art_a.count(marker)==art_c.count(marker)==1
assert art_a.split(marker)[0]==art_c.split(marker)[0]
for body in [art_a,art_c]:
    tail=body.split(marker)[1];assert tail.endswith(' as const;\n');assert isinstance(json.loads(tail[:-len(' as const;\n')]),dict)
assert set(closure['fixtures'])==set(fixture_map)
assert set(closure['originalTests'])==set(tests)
assert sorted({r['path'] for r in closure['literalURLReads'] if r['isMissingFixture']})==sorted(fixture_map)
indent=lambda text:text.replace('\n','\n          ')[:-10]
w=read(P/'rebuild-opening-cue-candidate.yml').decode();bw=read(B/'rebuild-opening-baseline.yml').decode()
assert bw.count(indent(base))==1
ew=bw.replace(indent(base),indent(source))
for a,z in [(sha(base.encode()),sha(source.encode())),(sha(read(B/'METADATA.json')),sha(literal)),('Rebuild exact empty-intent opening baseline','Build exact opening cue candidate C'),('rebuild-opening-baseline.yml','rebuild-opening-cue-candidate.yml'),('fresh-baseline:','fresh-cue-candidate:'),('empty-intent-fresh-baseline-','opening-cue-fresh-candidate-'),('empty-intent-fresh-','opening-cue-fresh-'),('empty-intent-diagnostic-','opening-cue-diagnostic-'),('Acquire exactly fifty canonical bodies and three original containers','Acquire fifty-six fixed direct bodies and three original containers'),('runtime98 and support32','candidate source104 and original support32')]:ew=ew.replace(a,z)
assert ew==w
workflow=yaml.safe_load(w);trigger=workflow.get('on',workflow.get(True));assert trigger=={'push':{'branches':['codex/lanternbound-production'],'paths':['.github/workflows/rebuild-opening-cue-candidate.yml']},'workflow_dispatch':{}}
assert workflow['permissions']=={};job=workflow['jobs']['fresh-cue-candidate'];assert job['permissions']=={'contents':'read'} and job['runs-on']=='ubuntu-24.04' and job['timeout-minutes']==15
prior_steps=yaml.safe_load(bw)['jobs']['fresh-baseline']['steps'];assert len(job['steps'])==len(prior_steps)
embedded=False;shell=0;heredocs=0
for step,oldstep in zip(job['steps'],prior_steps):
    assert step.get('uses')==oldstep.get('uses') and step['timeout-minutes']==oldstep['timeout-minutes']
    if 'run' not in step:continue
    r=subprocess.run(['bash','-n'],input=step['run'],text=True,capture_output=True,timeout=10);assert r.returncode==0,r.stderr;shell+=1
    m=re.search(r"<<'PY'\n(.*?)\nPY(?:\n|$)",step['run'],re.S)
    if m:
        t=ast.parse(m.group(1));compile(t,'embedded-workflow','exec');heredocs+=1
        for n in t.body:
            if isinstance(n,ast.Assign) and any(isinstance(v,ast.Name) and v.id=='source' for v in n.targets):assert ast.literal_eval(n.value)==source;embedded=True
assert embedded and sha(source.encode()) in w and sha(literal) in w
for f in P.glob('*.py'):compile(ast.parse(f.read_text()),str(f),'exec')
fail=load(P/'ACTUAL-FAILURES.json');references=[fail['rootReceipt']]+[dict(path=k,**v) for k,v in fail['pins'].items()]
for r in references:assert all(identity(pathlib.Path(r['path']))[k]==v for k,v in r.items() if k!='path')
actual=load(pathlib.Path(next(path for path in fail['pins'] if path.endswith('/C/members/acquisition-progress.json'))))
assert [(r['bytes'],r['sha256'],r['gitBlobSHA1']) for r in actual['verified']]==[(r['bytes'],r['sha256'],r['gitBlobSHA1']) for r in oldmeta['blobPins']]
result={'verdict':'ACCEPT_C_ADAPTATION_SOURCE_ONLY','sourceRoot':str(P),'sourceSeal':physical['SOURCE-SEAL.json'],'manifest':physical['MANIFEST.json'],'runner':physical['runner.py'],'workflow':physical['rebuild-opening-cue-candidate.yml'],'sourceInclusiveFiles':len(physical),'sourceInclusiveBytes':sum(r['bytes'] for r in physical.values()),'sourceCapBytes':2097152,'sealedFiles':physical,'sharedGate':identity(basegate_path),'sharedSourceSealSHA256':shared['sourceSealSHA256'],'sharedRuntimeFunctionsExact':unchanged,'candidateChangedFunctions':changed,'fullSharedRunnerTransformationExact':True,'fullWorkflowTransformationExact':True,'oldCFourFullInverseBodiesExact':True,'candidateOnlyMainDelta':True,'candidateInputs104Support32LocalFullBodyHashesExact':local,'all59BlobPinsFullLocalSizeSHA256GitSHA1Exact':True,'metadataLiteralAndActualAcquisitionExact':True,'shellGrammarRuns':shell,'embeddedPythonGrammarRuns':heredocs,'allPythonASTCompileOnly':True,'actualFailureReferencesHashed':len(references),'yamlVersion':yaml.__version__,'methodSeconds':time.monotonic()-start,'selfPeakRSSBytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,'largestSequentialGrammarChildPeakRSSBytes':resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss*1024,'noMethodPhaseRuntimeInstallBuildTestBrowserNetwork':True,'qualification':'Reuse shared independent guard/race assessment by exact complete function bytes; no helper race fixtures rerun. No new output identity or restored freeze/alias, source selection, gameplay/art/default/fun/platform approval. Prior completed suites with three fixture failures remain failed; source acceptance is not new suite/build/output/caller authority.'}
assert result['selfPeakRSSBytes']+result['largestSequentialGrammarChildPeakRSSBytes']<64*1048576
assert current['phase']==functions(ast.parse(old['runner.py'].decode()),old['runner.py'].decode())['phase']
oldroot=pathlib.Path(adapt['predecessorDirectory']); domain={f.relative_to(oldroot).as_posix():identity(f) for f in oldroot.rglob('*') if f.is_file()}
for name, pin in domain.items():assert identity(P/'INVERSE-FULL-C4'/name)==pin
assert {f.relative_to(P/'INVERSE-FULL-C4').as_posix() for f in (P/'INVERSE-FULL-C4').rglob('*') if f.is_file()}==set(domain)
result['fullOriginalC4PacketFiles']=domain
result['onlyTwoOriginalDataFixturesAdded']=True
result['fixturePrimaryPins']=identity(fixture_path)
result['staticTestDataClosure25ExactBodiesAndArtJSONOnlyDifference']=identity(basegate_path.parent/'FIXTURE-CLOSURE-CHECKS.json')
result['fixtureBodies']={r['path']:identity(pathlib.Path(r['bodyPath'])) for r in fixtures}
with (O/'CHECKS.json').open('x') as f:json.dump(result,f,indent=2,sort_keys=True);f.write('\n')
print(json.dumps({k:result[k] for k in ['verdict','sourceSeal','sourceInclusiveFiles','sourceInclusiveBytes','methodSeconds','selfPeakRSSBytes','largestSequentialGrammarChildPeakRSSBytes']}))
