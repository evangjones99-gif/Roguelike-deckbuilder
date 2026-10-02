"""SOURCE offline method: grammar, exact copied-control inverse, static fail-closed checks."""
import pathlib,json,gzip,hashlib,difflib,ast,subprocess,time,resource
P=pathlib.Path(__file__).parent;O=pathlib.Path('/workspace/scratch/starter-opening-runtime-caller-source-r4')
def sha(b):return hashlib.sha256(b).hexdigest()
def body(name,value):(P/name).write_bytes((json.dumps(value,separators=(',',':'))+'\n').encode())
origins=[];deltas=[]
pairs=[('runtime-guard-cue.mjs','runtime-guard-r4.mjs'),('runtime_guard_cue.py','runtime_guard_r4.py'),('supervise-cue.py','supervise-opening-r4.py')]
origin_file=P/'ORIGIN-CONTROLS.json.gz'
if origin_file.exists():origins=json.loads(gzip.decompress(origin_file.read_bytes()))['files']
else:
 for new,old in pairs:
  b=(O/old).read_bytes();origins.append({'name':old,'originalPath':str(O/old),'bytes':len(b),'sha256':sha(b),'literalUTF8':b.decode()})
 origin_file.write_bytes(gzip.compress((json.dumps({'schema':'literal-source-origin-v1','qualification':'Exact sampled working R4 source bytes preserved locally; no later R4 final authority is claimed','files':origins},separators=(',',':'))+'\n').encode(),compresslevel=6,mtime=0))
def transform(text,hunks,side):
 lines=text.splitlines(keepends=True);out=[];cursor=0
 for q in hunks:
  start=q[side+'LineStart'];old=q[side].splitlines(keepends=True);assert start>=cursor and ''.join(lines[start:start+len(old)])==q[side];out.extend([''.join(lines[cursor:start]),q['after' if side=='before' else 'before']]);cursor=start+len(old)
 out.append(''.join(lines[cursor:]));return ''.join(out)
for new,old in pairs:
 origin=next(r for r in origins if r['name']==old);before=origin['literalUTF8'];assert sha(before.encode())==origin['sha256'];after=(P/new).read_text();a=before.splitlines(keepends=True);b=after.splitlines(keepends=True);hunks=[]
 for tag,i,j,k,l in difflib.SequenceMatcher(None,a,b,autojunk=False).get_opcodes():
  if tag!='equal':hunks.append({'beforeLineStart':i,'afterLineStart':k,'before':''.join(a[i:j]),'after':''.join(b[k:l])})
 assert transform(before,hunks,'before')==after and transform(after,hunks,'after')==before
 deltas.append({'name':new,'originName':old,'beforeBytes':len(before.encode()),'afterBytes':len(after.encode()),'beforeSHA256':sha(before.encode()),'afterSHA256':sha(after.encode()),'hunks':hunks})
(P/'CONTROL-INVERSE.json.gz').write_bytes(gzip.compress((json.dumps({'schema':'exact-line-hunks-v1','origin':'ORIGIN-CONTROLS.json.gz','files':deltas},separators=(',',':'))+'\n').encode(),compresslevel=6,mtime=0))
start=time.monotonic();grammar=[]
for name in ['driver-cue.mjs','runtime-guard-cue.mjs']:
 r=subprocess.run(['/opt/codex/runtimes/codex-primary-runtime/dependencies/node/bin/node','--check',str(P/name)],capture_output=True,text=True,timeout=15);assert r.returncode==0;grammar.append({'name':name,'exitCode':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
python=[]
for f in sorted(P.glob('*.py')):compile(ast.parse(f.read_text()),str(f),'exec');python.append(f.name)
d=(P/'driver-cue.mjs').read_text();s=(P/'supervise-cue.py').read_text();j=(P/'runtime-guard-cue.mjs').read_text();p=(P/'runtime_guard_cue.py').read_text();e=json.loads((P/'EXPECTED.json').read_text());b,c=e['runtimes']
assert d.index('qualification=qualify(')<d.index('await import(expected.dependencies.modulePath)')<d.index('fs.writeFileSync(')<d.index('http.createServer(')<d.index('chromium.launch(')
assert s.index('method_grant=qualify(')<s.index('stage,freeze,packet,port=')<s.index('p.mkdir(')<s.index('subprocess.Popen(')
assert j.index('assert(expected.sealed===true')<j.index('JSON.parse(regular(expected.rootMethodGrantPath))')
assert p.index("assert expected.get('sealed') is True")<p.index("grant=json.loads(regular(expected['rootMethodGrantPath']))")
assert e['sealed'] is False and e['runtimeEligible'] is False and e['runtimeRecovery']['complete'] is False
for key in ['stage','outputsDigest','freezePath','freezeSHA256','stageManifestPath','stageManifestSHA256','stageAuthorityPath','stageAuthoritySHA256','stageReviewPath','stageReviewSHA256']:assert c[key] is None
assert c['sourceDigest']=='993aa3681596c2488d4d394744e5beda2778ffcba3e1649736612304d20b50c5' and b['sourceDigest']=='65b31b3f21e34a624bdac962e4919c7dc1791e502eb6cfdb1612103b8036fe9c'
assert 'localStorage.setItem' not in d and 'dispatchEvent' not in d and 'createGame(' not in d and 'applyAction(' not in d and '.fill(' not in d
assert "SKIPPED_NO_NATURAL_TURN2_LEGAL_BINDING" in d and "focusedLateBindingBranchObserved" in d and "missing checkpoint" in d
assert all(x in d for x in ["assert.equal(await raw(),before,'Binding drag cancellation",'350',"assert.equal(await raw(),choiceRaw,'Pure target hover",'a.raw===z.raw'])
receipt={'sourceOnly':True,'callerOrHelperExecuted':False,'browserServerBuildExecuted':False,'grammar':grammar,'pythonASTCompileOnly':python,'failClosedStaticOrdering':True,'COutputAuthorityUninventedAndPending':True,'UIOnlyNoSavedStateInjection':True,'skipCoverageExplicit':True,'completeRawUnionPairComparison':True,'threeControlForwardInverseExact':[{'name':r['name'],'beforeSHA256':r['beforeSHA256'],'afterSHA256':r['afterSHA256'],'hunks':len(r['hunks'])} for r in deltas],'sourceOwnPeakRSSKiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'sourceChildPeakRSSKiB':resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,'wholeSeconds':time.monotonic()-start,'qualification':'Grammar and pure offline reconstruction/static source checks only. No caller/helper/app import or execution; no gameplay/visual/resource runtime acceptance.'}
receipt['ownAndLargestSequentialGrammarChildRSSUpperBoundKiB']=receipt['sourceOwnPeakRSSKiB']+receipt['sourceChildPeakRSSKiB'];assert receipt['ownAndLargestSequentialGrammarChildRSSUpperBoundKiB']<=64*1024;body('GRAMMAR-INVERSE-RECEIPT.json',receipt);print(json.dumps(receipt))
