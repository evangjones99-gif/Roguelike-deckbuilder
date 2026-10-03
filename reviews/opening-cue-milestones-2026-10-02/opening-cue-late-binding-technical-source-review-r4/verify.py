"""Independent read-only SOURCE identity/reconstruction/grammar audit; no caller import."""
import ast,base64,gzip,hashlib,json,pathlib,resource,subprocess,time
P=pathlib.Path('/workspace/scratch/opening-cue-late-binding-caller-source-r4')
O=pathlib.Path(__file__).parent
start=time.monotonic()
def sha(b):return hashlib.sha256(b).hexdigest()
def encode(v):return (json.dumps(v,separators=(',',':'))+'\n').encode()
def load(n):return json.loads((P/n).read_bytes())
physical={f.name:f.read_bytes() for f in P.iterdir() if f.is_file()}
assert all(f.is_file() and not f.is_symlink() for f in P.iterdir())
assert sha(physical['SOURCE-SEAL.json'])=='aabc6f5fd7b7c8ebc5c9456c44fbadac532ee27e9c2d260b21395a95df1c231d'
seal=load('SOURCE-SEAL.json')
assert set(physical)=={r['name'] for r in seal['files']}|{'SOURCE-SEAL.json'}
for r in seal['files']:assert len(physical[r['name']])==r['bytes'] and sha(physical[r['name']])==r['sha256']
assert sum(map(len,physical.values()))==seal['familyBytesIncludingSeal']==218693<=seal['sourceFamilyCapBytes']==262144
assert len(physical)==25
def patch(text,hunks,side):
    lines=text.splitlines(keepends=True);out=[];cursor=0
    for h in hunks:
        pos=h[side+'LineStart'];old=h[side].splitlines(keepends=True)
        assert pos>=cursor and ''.join(lines[pos:pos+len(old)])==h[side]
        out.extend(lines[cursor:pos]);out.append(h['after' if side=='before' else 'before']);cursor=pos+len(old)
    return ''.join(out+lines[cursor:])
def resolve(value):
    if isinstance(value,str):return value.encode()
    if 'base64' in value:return base64.b64decode(value['base64'],validate=True)
    b=physical[value['bodyRef']]
    if 'truncateBytes' in value:b=b[:value['truncateBytes']]
    for a,z in value.get('replacements',[]):b=b.replace(a.encode(),z.encode())
    if 'hunks' in value:b=patch(b.decode(),value['hunks'],'before').encode()
    assert len(b)==value['bytes'] and sha(b)==value['sha256']
    return b
origin_encoded=json.loads(gzip.decompress(physical['R1-SNAPSHOT.json.gz']))
origin={n:resolve(v) for n,v in origin_encoded.items()}
old=pathlib.Path('/workspace/scratch/opening-cue-late-binding-caller-source-r1')
assert set(origin)=={f.name for f in old.iterdir() if f.is_file()}
for n,b in origin.items():assert b==(old/n).read_bytes(),n
assert sum(map(len,origin.values()))==100761
oldseal=json.loads(origin['SOURCE-SEAL.json'])
for r in oldseal['files']:assert len(origin[r['name']])==r['bytes'] and sha(origin[r['name']])==r['sha256']

def audit_inverse(name,before):
    inv=json.loads(gzip.decompress(physical[name]))
    assert set(inv['before'])==set(before)
    for n,r in inv['before'].items():assert len(before[n])==r['bytes'] and sha(before[n])==r['sha256']
    after={n:physical[n] for n in inv['after']}
    for n,r in inv['after'].items():assert len(after[n])==r['bytes'] and sha(after[n])==r['sha256']
    fwd=dict(before);rev=dict(after)
    for d in inv['deltas']:
        n=d['name']
        for target,side in [(fwd,'before'),(rev,'after')]:
            other='after' if side=='before' else 'before';body=target.get(n)
            assert (sha(body) if body is not None else None)==d[side+'SHA256']
            if d[other+'SHA256'] is None:target.pop(n,None)
            elif 'hunks' in d:target[n]=patch(body.decode(),d['hunks'],side).encode()
            elif 'losslessOriginCodec' in d:
                codec=d['losslessOriginCodec'];assert codec['compressionLevel']==9 and codec['mtime']==0
                if side=='before':
                    values=json.loads(gzip.decompress(body));values.update(codec['replacementReferences'])
                else:
                    values={key:({'base64':base64.b64encode(resolve(v)).decode()} if isinstance(v,dict) and v.get('originalRepresentation','base64')=='base64' else resolve(v).decode()) for key,v in json.loads(gzip.decompress(body)).items()}
                    assert sha(encode(values))==codec['expandedCanonicalJSONSHA256']
                target[n]=gzip.compress(encode(values),compresslevel=codec['compressionLevel'],mtime=codec['mtime'])
            else:target[n]=resolve(d[other+'Literal'])
            assert (sha(target[n]) if n in target else None)==d[other+'SHA256']
    assert fwd==after and rev==before
    return {'name':name,'beforeLogicalFiles':len(before),'afterLogicalFiles':len(after),'fullForwardExact':True,'fullInverseExact':True,'closureSidecarsExcludedFromRecursiveDomain':sorted(set(physical)-set(after))}
inverses=[audit_inverse('R1-INVERSE.json.gz',origin)]
pins=load('R2-ORIGIN-PINS.json');r2=pathlib.Path(pins['sourceRoot']);before2={r['name']:(r2/r['name']).read_bytes() for r in pins['files']}
for r in pins['files']:assert len(before2[r['name']])==r['bytes'] and sha(before2[r['name']])==r['sha256']
assert set(before2)=={f.name for f in r2.iterdir() if f.is_file()}
inverses.append(audit_inverse('R3-INVERSE.json.gz',before2))
control=json.loads(gzip.decompress(physical['CONTROL-INVERSE.json.gz']))
controls=json.loads(gzip.decompress(physical['ORIGIN-CONTROLS.json.gz']))['files']
for row in control['files']:
    source=next(r for r in controls if r['name']==row['originName']);a=source['literalUTF8'].encode();b=physical[row['name']]
    assert len(a)==source['bytes'] and sha(a)==source['sha256']==row['beforeSHA256']
    assert sha(b)==row['afterSHA256'] and patch(a.decode(),row['hunks'],'before').encode()==b and patch(b.decode(),row['hunks'],'after').encode()==a
expected=load('EXPECTED.json');protocol=load('PROTOCOL.json');manifest=load('MANIFEST.json')
assert not expected['sealed'] and not expected['runtimeEligible'] and not expected['runtimeRecovery']['complete']
assert expected['driverSeconds']==60 and expected['supervisorWholeSeconds']==90
assert protocol['caps']['driverSeconds']==60 and protocol['caps']['wholeSupervisorSeconds']==90
assert protocol['caps']['workMiB']==896 and protocol['caps']['reserveMiB']==512
assert protocol['caps']['sourceKiBInclusive']==256
c=expected['runtimes'][1]
for key in ['stage','outputsDigest','freezePath','freezeSHA256','stageManifestPath','stageManifestSHA256','stageAuthorityPath','stageAuthoritySHA256','stageReviewPath','stageReviewSHA256']:assert c[key] is None
assert not pathlib.Path(expected['rootMethodGrantPath']).exists()
for r in manifest['bodies']:assert len(physical[r['name']])==r['bytes'] and sha(physical[r['name']])==r['sha256']
for key in ['dependenciesExternal','candidateSourceProposal','candidateBuildInputEvidence']:
    r=manifest[key];b=pathlib.Path(r['path']).read_bytes();assert len(b)==r['bytes'] and sha(b)==r['sha256']
reviews=load('R1-REVIEW-COLLECTION.json')
for r in [x for role in reviews['reviews'] for x in role['files']]+reviews['technicalTerminalAddendum']:
    b=pathlib.Path(r['path']).read_bytes();assert len(b)==r['bytes'] and sha(b)==r['sha256']
trace=load('UI-SOURCE-TRACE.json')
for r in trace['bodies']:
    b=pathlib.Path(r['path']).read_bytes();assert len(b)==r['bytes'] and sha(b)==r['sha256']
d=physical['driver-cue.mjs'].decode();s=physical['supervise-cue.py'].decode();j=physical['runtime-guard-cue.mjs'].decode();py=physical['runtime_guard_cue.py'].decode()
assert d.index('qualification=qualify(')<d.index('await import(expected.dependencies.modulePath)')<d.index('fs.writeFileSync(')
assert s.index('method_grant=qualify(')<s.index('stage,freeze,packet,port=')<s.index('p.mkdir(')<s.index('subprocess.Popen(')
assert j.index('assert(expected.sealed===true')<j.index('JSON.parse(regular(expected.rootMethodGrantPath))')
assert py.index("assert expected.get('sealed') is True")<py.index("grant=json.loads(regular(expected['rootMethodGrantPath']))")
assert d==pathlib.Path('/workspace/scratch/opening-cue-late-binding-caller-source-r3/driver-cue.mjs').read_text().replace('opening-cue-late-binding-caller-source-r3','opening-cue-late-binding-caller-source-r4')
assert s==pathlib.Path('/workspace/scratch/opening-cue-late-binding-caller-source-r3/supervise-cue.py').read_text().replace('opening-cue-late-binding-caller-source-r3','opening-cue-late-binding-caller-source-r4')
assert s==origin['supervise-cue.py'].decode().replace('opening-cue-late-binding-caller-source-r1','opening-cue-late-binding-caller-source-r4')
assert physical['runtime-guard-cue.mjs']==origin['runtime-guard-cue.mjs'] and physical['runtime_guard_cue.py']==origin['runtime_guard_cue.py']
for token in ['localStorage.setItem','dispatchEvent','createGame(','applyAction(','.fill(']:assert token not in d
assert "if(phase==='battle'){cueCheck(initial,null);return;}" in d
assert "Math.min(4000,60000-(Date.now()-started)-500)" in d
assert "assert.equal(await raw(),before,'Passive terminal presentation wait changed full save')" in d
assert "assert(settled.cue.visible!==true" in d
assert 'seedInitiallyHidden:true,seedVisibleAfterOrdinaryDisclosure:true' in d
assert 'a.raw===z.raw' in d and 'missing checkpoint' in d and 'result.mechanicalPass=result.protocolPass&&result.focusedLateBindingBranchObserved' in d
node='/opt/codex/runtimes/codex-primary-runtime/dependencies/node/bin/node'
grammar=[]
for n in ['driver-cue.mjs','runtime-guard-cue.mjs']:
    r=subprocess.run([node,'--check',str(P/n)],capture_output=True,text=True,timeout=15)
    grammar.append({'name':n,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr});assert r.returncode==0
for n,b in physical.items():
    if n.endswith('.py'):compile(ast.parse(b.decode()),str(P/n),'exec')
predicate=d.split('await page.waitForFunction(terminalPhase=>{',1)[1].split('},phase,{timeout:waitMs,polling:100})',1)[0]
js="""import assert from 'node:assert/strict';
const predicate=terminalPhase=>{PREDICATE};
let cases=0;
function test(v,want,phase='reward') {
const nodes={'#app':v.app?{classList:{contains:k=>k==='settling-combat'?v.settling:k==='phase-'+v.phase}}:null,'#dock':{hidden:v.hidden},'#scene-ui':{getAttribute:()=>v.busy?'true':null,querySelector:()=>v.heading?{}:null},'#arena-wrap':{getAttribute:()=>v.arenaHidden?'true':'false'}};
globalThis.document={querySelector:k=>nodes[k]};assert.equal(!!predicate(phase),want);cases++;
}
const ready={app:true,phase:'reward',settling:false,busy:false,hidden:true,heading:true,arenaHidden:true};
test(ready,true);test({...ready,retainedCuePresent:true},true);
for(const [k,v] of [['app',false],['settling',true],['busy',true],['hidden',false],['heading',false],['arenaHidden',false],['phase','battle']])test({...ready,[k]:v},false);
for(const phase of ['victory','defeat'])test({...ready,phase},true,phase);
console.log(JSON.stringify({pureExactPredicateCases:cases}));
""".replace('PREDICATE',predicate)
(O/'terminal-predicate-check.mjs').write_text(js)
r=subprocess.run([node,str(O/'terminal-predicate-check.mjs')],capture_output=True,text=True,timeout=15);assert r.returncode==0,r.stderr
assert (O/'terminal-predicate-check.mjs').stat().st_size<8192
result={'verdict':'ACCEPT_EXACT_INELIGIBLE_SOURCE_TEMPLATE_ONLY','sourceSealSHA256':sha(physical['SOURCE-SEAL.json']),'manifestSHA256':sha(physical['MANIFEST.json']),'physicalFiles':len(physical),'inclusivePhysicalBytes':sum(map(len,physical.values())),'sourceCapBytes':262144,'R1FullLogicalOriginBytes':sum(map(len,origin.values())),'R1LogicalOriginBodies':len(origin),'fullR1BodyComparison':True,'inverses':inverses,'threeInheritedControlInversesExact':True,'allPrimaryTraceAndExternalReferenceHashesExact':True,'ExpectedClosedCandidateAuthorityNullRootGrantAbsent':True,'grammar':grammar,'terminalPredicate':json.loads(r.stdout),'runtimeExecuted':False,'ownPeakRSSBytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,'largestSequentialGrammarChildPeakRSSBytes':resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss*1024,'elapsedSeconds':time.monotonic()-start,'qualification':'Pure standard-library reconstruction/static source inspection and Node grammar/exact predicate stub only; no author methods/helpers/caller/app import or runtime. Recursive closure sidecars separately bound by inclusive seal. No build/output, actual cue/gameplay/art/default/fun/platform or runtime approval.'}
assert result['ownPeakRSSBytes']+result['largestSequentialGrammarChildPeakRSSBytes']<=64*1048576
with (O/'CHECKS.json').open('x') as f:json.dump(result,f,indent=2,sort_keys=True);f.write('\n')
print(json.dumps(result))
