import ast,gzip,hashlib,json,pathlib,re
P=pathlib.Path(__file__).parent;D=pathlib.Path('/workspace/scratch/native128-empty-intent-caller-source-author-r2')
def h(b):return hashlib.sha256(b).hexdigest()
def sha(q):return h(pathlib.Path(q).read_bytes())
def put(n,v):(P/n).write_bytes(v if isinstance(v,bytes) else (json.dumps(v,separators=(',',':'))+'\n').encode())
d0=(D/'driver-paired-r2.mjs').read_text();s0=(D/'supervise-paired-r2.py').read_text();e0=json.loads((D/'EXPECTED-CANDIDATE.json').read_bytes())
assert h(d0.encode())=='63b171a4793469723e723f5c88ba66b9bbee620d1476dbe6159e226c0455f3ee';assert h(s0.encode())=='e4be00a1b66a757d7b6aa8b4666066685ce770722ab59330dba6cf6f5873adb6'
ops=[];d=d0
def swap(a,b,count=1):
 global d
 assert d.count(a)==count,(a[:100],d.count(a),count)
 d=d.replace(a,b);ops.append({'before':a,'after':b,'count':count})
def block(a,z,b):
 global d
 start=d.index(a);end=d.index(z,start);swap(d[start:end],b)
swap(str(D),str(P),2)
swap("assert.deepEqual(expected.cases,[{name:'A-hold-release',query:'?targetClearGhost=1&coherentNative128=1',feedbackEnabled:true},{name:'B-hold-release',query:'?targetClearGhost=1&coherentNative128=1',feedbackEnabled:true}]);","assert.deepEqual(expected.cases,[{name:'A-opening',query:'?targetClearGhost=1&coherentNative128=1',feedbackEnabled:true},{name:'B-opening',query:'?targetClearGhost=1&coherentNative128=1',feedbackEnabled:true}]);")
swap("assert.deepEqual(expected.captureCapsByCase,{'A-hold-release':2,'B-hold-release':2})","assert.deepEqual(expected.captureCapsByCase,{'A-opening':2,'B-opening':2})")
swap('assert.equal(freeze.inputCount,98);assert.equal(freeze.outputCount,64);','assert.equal(freeze.inputCount,config.inputCount);assert.equal(freeze.outputCount,config.outputCount);')
swap('Object.keys(policy.leaves).length,115','Object.keys(policy.leaves).length,config.aliasCount')
swap('count:115','count:config.aliasCount',2)
swap('Object.keys(p.leaves).length,115','Object.keys(p.leaves).length,config.aliasCount')
swap('Object.keys(freeze.inputs).length,expected.inputCount','Object.keys(freeze.inputs).length,config.inputCount')
swap('Object.keys(freeze.outputs).length,expected.outputCount','Object.keys(freeze.outputs).length,config.outputCount')
swap('assert.deepEqual(runtimes.map(r=>r.config.port),[4849,4850])','assert.deepEqual(runtimes.map(r=>r.config.port),[4851,4852])')
block('const changedInputs=',"const controlsPath=", "const commonInputs=Object.keys(runtimes[0].freeze.inputs);assert(commonInputs.every(k=>k in runtimes[1].freeze.inputs));const changedInputs=commonInputs.filter(k=>runtimes[0].freeze.inputs[k]!==runtimes[1].freeze.inputs[k]).sort();assert.deepEqual(changedInputs,['public/art/coherent-native128-manual-crop-view-manifest.json','src/art.ts','src/coherent-native128.ts','src/main.ts']);assert.deepEqual(Object.keys(runtimes[1].freeze.inputs).filter(k=>!commonInputs.includes(k)).sort(),expected.newNativeInputPaths);for(const runtime of runtimes)for(const asset of runtime.config.nativeAssets)assert.equal(runtime.freeze.outputs['art/'+asset.filename],asset.sha256);\n")
oldScope=re.search("const result=\\{scope:'([^']*)'",d).group(1)
swap(oldScope,"Native starter opening comparison: frozen76e5/2547 seven assets versus65b31/960e thirteen assets, both same native query, ordinary937240 Initiate. Cairn/freeOrder/heldScourEscape/oneScour/Endturn/enemy response/natural starter hover/one legal second ally; four originals. Native layout capacity2, first300 remaining unobserved. No art/default/animation/fun acceptance.")
swap("emit({kind:'decode',sha256,width:image.naturalWidth,height:image.naturalHeight,complete:image.complete})","emit({kind:'decode',sha256,sourceURL:image.src,width:image.naturalWidth,height:image.naturalHeight,complete:image.complete})")
swap("async function decodedBeforeEntry(){","function currentNativeAssets(){return runtimes.find(r=>r.config.case===activeCase.name).config.nativeAssets;}\nasync function decodedBeforeEntry(){")
swap(".size<7&&Date.now()<until",".size<currentNativeAssets().length&&Date.now()<until")
swap('expected:expected.nativeAssets,records,allRequired:expected.nativeAssets.every','expected:currentNativeAssets(),records,allRequired:currentNativeAssets().every')
swap('Actual seven successful native128 decodes','Actual per-runtime complete successful native128 decodes')
swap("bodyPins=expected.nativeAssets.filter(p=>p.category==='body')","bodyPins=currentNativeAssets().filter(p=>p.category==='body')")
swap('await ownedContext.addInitScript(installPixelObserver,expected.nativeAssets)','await ownedContext.addInitScript(installPixelObserver,runtime.config.nativeAssets)')
swap("classification:'Source-informed native transient diagnostic; not accepted cause/fix or human fun'","classification:'Source-informed opening-prefix native starter diagnostic; not300 or human fun',starterObservations:[],starterGaps:[],enemyResponses:[],sessionStartedWallMs:Date.now()")
swap("await page.goto('http://127.0.0.1:'","row.navigationRequested=stamp();row.sessionStartedWallMs=Date.now();await page.goto('http://127.0.0.1:'")
swap('  await initialCairnCancel();await heldCancelPure();','  row.initialCairnCloneCancel={status:\'NOT_ATTEMPTED\',reason:\'Opening prefix retains ordinary Cairn hover/bind and real Scour Escape instead of duplicate Cairn clone diagnostics\'};')
swap("assert(await ready(row.targetUID,'settled after binding'));await click(unit('Cairn Hound')","row.targetAlternatives=bound.enemies.map(u=>({uid:u.uid,name:u.name,hp:u.hp,block:u.block,intent:u.intent}));row.choiceRationale='Choose currently unarmored Ironjaw Reaver for Cairn bonus; alternate Gloam piercing threat remains observed.';assert(await ready(row.targetUID,'settled after binding'));await click(unit('Cairn Hound')")
block('  const first=await firstDrop();'," }catch(e){row.failure=e.stack",(P/'opening-case.mjs.txt').read_text())
swap('async function runCase(name,query,scenario,feedbackEnabled){',(P/'opening-flow.mjs.txt').read_text()+'\nasync function runCase(name,query,scenario,feedbackEnabled){')
block(' result.canonicalComparisons=[];',"}catch(e){result.failure=e.stack",(P/'opening-comparison.mjs.txt').read_text())
# Remove now-unused corpse/second-card helpers as one explicit source delta.
block('function secondCommitted(', 'async function starterSnapshot(', '// Opening trial deliberately omits second-card kill/normalization/corpse helpers.\n')
swap("await page.waitForTimeout(100);row.after=await receipt(label+' after native release');if(activeCase.firstDrop&&secondCommitted(row.after.raw,activeCase.firstDrop.after.raw))await markCanonicalKill(row.after.raw,row.releaseAtMs,'genuine held mouse-up');", "await page.waitForTimeout(100);row.after=await receipt(label+' after native release');")
restored=d
for op in reversed(ops):assert restored.count(op['after'])==op['count'];restored=restored.replace(op['after'],op['before'])
assert restored==d0
s=s0.replace(str(D)+'/driver-paired-r2.mjs',str(P)+'/driver-opening-r1.mjs');assert s.replace(str(P)+'/driver-opening-r1.mjs',str(D)+'/driver-paired-r2.mjs')==s0;ast.parse(s)
fp=pathlib.Path('/workspace/scratch/starter-family-native128-strict-build-root-r1/final-seal-r1/RUNTIME-FREEZE.json');assert sha(fp)=='6e61e6e42b1c160e899da7888b20daf33264f8dc2f65d5301ac72e70537590fc'
f=json.loads(fp.read_bytes());cat=f['actualAliasCatalogue'];assert sha(cat['path'])==cat['sha256'];policy=json.loads(pathlib.Path(cat['path']).read_bytes());assert len(policy['leaves'])==121
assets=json.loads(pathlib.Path('/workspace/scratch/starter-family-native128-materialized-source-root-r1/coherent-native128-manual-crop-view-manifest.json').read_bytes())['sprites'];assets=[{k:r[k] for k in ['name','filename','sha256','category']} for r in assets]
roles=['cairn','reaver','gloam','hunter','cairn-portrait','hunter-portrait','fallen-reaver','ash','ash-portrait','fen','fen-portrait','briar','briar-portrait']
for a,r in zip(assets,roles):a['role']=r
a=e0['runtimes'][1];a.update({'case':'A-opening','port':4851,'inputCount':98,'outputCount':64,'aliasCount':115,'nativeAssets':e0['nativeAssets']})
b={'case':'B-opening','port':4852,'stage':f['stage'],'freezePath':str(fp),'freezeSHA256':sha(fp),'sourceDigest':f['sourceDigest'],'outputsDigest':f['outputsDigest'],'inputCount':104,'outputCount':70,'aliasCount':121,'aliasPolicyPath':cat['path'],'aliasPolicySHA256':cat['sha256'],'aliasRoots':policy['roots'],'aliasBinding':'freeze-forward-catalogue','nativeAssets':assets,'buildGatePath':None,'buildGateSHA256':None,'buildGateDecision':None}
e=e0;e.update({k:a[k] for k in ['stage','freezePath','freezeSHA256','sourceDigest','outputsDigest','inputCount','outputCount','aliasPolicyPath','aliasPolicySHA256','aliasRoots','buildGatePath','buildGateSHA256','buildGateDecision']})
e.update({'sealed':False,'runtimes':[a,b],'port':4851,'actualPacket':'/workspace/scratch/starter-family-native128-opening-comparison-actual-r1','cases':[{'name':r['case'],'query':'?targetClearGhost=1&coherentNative128=1','feedbackEnabled':True} for r in [a,b]],'captureCapsByCase':{'A-opening':2,'B-opening':2},'scenarios':['opening'],'nativeAssets':assets,'sourceEligibility':'PENDING_EXTERNAL_NEW_BUILD_GATE_INDEPENDENT_SOURCE_GRAMMAR_ROOT_GRANT','newNativeInputPaths':sorted(k for k in f['inputs'] if k not in json.loads(pathlib.Path(a['freezePath']).read_bytes())['inputs']),'comparisonScope':'Exactly four source/manifest replacements and six new PNGs; rules/CSS/arena/tactile unchanged. Baseline7 naturally falls painted with unsupported starter hand; trial13 may retain native only within2ally/2enemy layout.','openingProtocolReference':{'path':'/workspace/scratch/starter-family-native128-first-session-protocol-source-r1/PROTOCOL.json','sha256':'4bbaa810f1afd601982d9b81e5a97fb84b605806eeaac6ba8981bb7aa7ca127a'},'pendingControls':['exact candidate actual-build gate','independent caller SOURCE gate','Root driver-only grammar','Root sole actual grant with fresh admission']})
for k in ['actualCSSSHA256ByCase','intentFieldDiagnostic','emptyIntentComparisonScope','aftermathTiming','ghostPlacementEnabledByCase','finalCSSGate']:e.pop(k,None)
put('driver-opening-r1.mjs',d.encode());put('supervise-opening-r1.py',s.encode());put('EXPECTED-CANDIDATE.json',e)
inverse=(json.dumps({'driverLiteralDeltas':ops,'donorDriverSHA256':h(d0.encode()),'donorSupervisorSHA256':h(s0.encode()),'fullDriverInverse':True,'supervisorOwnedPathOnly':True,'ExpectedDonorSHA256':sha(D/'EXPECTED-CANDIDATE.json')},separators=(',',':'))+'\n').encode();z=gzip.compress(inverse,mtime=0);assert gzip.decompress(z)==inverse;put('INVERSE.json.gz',z)
put('PROOF.json',{'status':'SOURCE_TEMPLATE_PENDING_NEW_BUILD_GATE','sourceProtocolSHA256':e['openingProtocolReference']['sha256'],'driverFullInverse':True,'supervisorFullInverse':True,'inverseLogicalBytes':len(inverse),'inverseStoredBytes':len(z),'inverseSHA256':h(inverse),'inverseStoredSHA256':h(z),'rootLifecycleBoundaryUnchanged':True,'rawSaveAndTrustedOwnedSourceReleaseFunctionsUnchangedExceptRemovedUnusedKillMarker':True,'selected19StylesAndLeafClipsUnchanged':True,'fixedFallenSamplerUnchanged':True,'newObserverField':'decode sourceURL to join actual card img blob source with exact observed decoded SHA; passive only','familyReadiness':'7A/13B, initial3actors+hunter draw evidence; secondAsh sampled separately','coverageLosses':['Corpse/expiry timings and images removed','second Scour/kill/normalization/transient replay removed','Cairn clone/cancel duplicate rich path unused','Fen/Briar body and thirdbinding deliberately notattempted; optionalturn3 may gap'],'runtimeLimitsUnchanged':True,'noRuntimeExecuted':True,'noGameQualityClaim':True})
put('MANIFEST.json',{'bodies':[{'name':n,'bytes':(P/n).stat().st_size,'sha256':sha(P/n)} for n in ['driver-opening-r1.mjs','supervise-opening-r1.py','EXPECTED-CANDIDATE.json']],'sourceOnly':True,'runtimeEligible':False,'buildGatePending':True,'inverseReference':{'path':str(P/'INVERSE.json.gz'),'sha256':sha(P/'INVERSE.json.gz')},'proofSHA256':sha(P/'PROOF.json'),'logicalCapBytes':147456})
status={x.split(':')[0]:x.split(':')[1].strip() for x in pathlib.Path('/proc/self/status').read_text().splitlines() if x.startswith(('VmRSS:','VmHWM:'))};assert all(int(v.split()[0])<24576 for v in status.values())
assert sum(q.stat().st_size for q in P.rglob('*') if q.is_file())+4096<147456
print(json.dumps({'normal':True,'own':status,'logicalBeforeTail':sum(q.stat().st_size for q in P.rglob('*') if q.is_file()),'driverSHA256':h(d.encode()),'supervisorSHA256':h(s.encode()),'buildGatePending':True}))
