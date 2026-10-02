// SOURCE-ONLY native transient-drag comparison. No execution without exact ROOT grant.
import fs from 'node:fs';
import path from 'node:path';
import http from 'node:http';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {gzipSync,gunzipSync} from 'node:zlib';
import {chromium} from '/workspace/Roguelike-deckbuilder/node_modules/playwright-core/index.mjs';


const [stage,freezePath,packet,portText]=process.argv.slice(2),port=Number(portText),started=Date.now();
const expected=JSON.parse(fs.readFileSync('/workspace/scratch/starter-family-native128-opening-caller-source-author-r1/EXPECTED-CANDIDATE.json'));
assert.equal(stage,expected.stage);assert.equal(freezePath,expected.freezePath);
assert.equal(packet,expected.actualPacket);assert.equal(port,expected.port);
assert.equal(expected.sealed,true);assert.deepEqual(expected.cases,[{name:'A-opening',query:'?targetClearGhost=1&coherentNative128=1',feedbackEnabled:true},{name:'B-opening',query:'?targetClearGhost=1&coherentNative128=1',feedbackEnabled:true}]);assert.equal(expected.captureCap,4);assert.deepEqual(expected.captureCapsByCase,{'A-opening':2,'B-opening':2});assert.equal(expected.captureFormat,'jpeg');assert.equal(expected.captureQuality,80);
const hash=b=>createHash('sha256').update(b).digest('hex');
const runtimes=expected.runtimes.map(config=>{
 const bytes=fs.readFileSync(config.freezePath),freeze=JSON.parse(bytes),policyBytes=fs.readFileSync(config.aliasPolicyPath),policy=JSON.parse(policyBytes);
 assert.equal(hash(bytes),config.freezeSHA256);assert.equal(freeze.stage,config.stage);assert.equal(freeze.sourceDigest,config.sourceDigest);assert.equal(freeze.outputsDigest,config.outputsDigest);assert.equal(freeze.inputCount,config.inputCount);assert.equal(freeze.outputCount,config.outputCount);assert(freeze.inputs&&typeof freeze.inputs==='object'&&!Array.isArray(freeze.inputs));
 assert.equal(hash(policyBytes),config.aliasPolicySHA256);assert.equal(policy.roots[0],config.stage);assert.equal(Object.keys(policy.leaves).length,config.aliasCount);assert.deepEqual(policy.roots,config.aliasRoots);
 if(config.aliasBinding==='catalogue-header-freeze')assert.equal(policy.freezeSHA256,config.freezeSHA256);
 else{assert.equal(config.aliasBinding,'freeze-forward-catalogue');assert.deepEqual(freeze.actualAliasCatalogue,{path:config.aliasPolicyPath,sha256:config.aliasPolicySHA256,count:config.aliasCount});}
 const gateBytes=fs.readFileSync(config.buildGatePath),gate=JSON.parse(gateBytes);assert.equal(hash(gateBytes),config.buildGateSHA256);assert.equal(gate.decision,config.buildGateDecision);assert.equal(gate.stage,config.stage);assert.equal(gate.sourceDigest,config.sourceDigest);assert.equal(gate.outputsDigest,config.outputsDigest);
 return {config,stage:config.stage,freeze,policy};
});
assert.equal(runtimes.length,2);assert.deepEqual(runtimes.map(r=>r.config.port),[4851,4852]);assert.deepEqual(runtimes.map(r=>r.config.case),expected.cases.map(c=>c.name));assert.equal(runtimes[0].stage,stage);assert.equal(runtimes[0].config.freezePath,freezePath);assert.equal(runtimes[0].config.port,port);
const commonInputs=Object.keys(runtimes[0].freeze.inputs);assert(commonInputs.every(k=>k in runtimes[1].freeze.inputs));const changedInputs=commonInputs.filter(k=>runtimes[0].freeze.inputs[k]!==runtimes[1].freeze.inputs[k]).sort();assert.deepEqual(changedInputs,['public/art/coherent-native128-manual-crop-view-manifest.json','src/art.ts','src/coherent-native128.ts','src/main.ts']);assert.deepEqual(Object.keys(runtimes[1].freeze.inputs).filter(k=>!commonInputs.includes(k)).sort(),expected.newNativeInputPaths);for(const runtime of runtimes)for(const asset of runtime.config.nativeAssets)assert.equal(runtime.freeze.outputs['art/'+asset.filename],asset.sha256);
const controlsPath='/workspace/scratch/starter-family-native128-opening-caller-source-author-r1/MANIFEST.json';
const controlsBytes=fs.readFileSync(controlsPath),controls=JSON.parse(controlsBytes);
const compactControlsPath='/workspace/scratch/target-clear-default-compact-caller-author-r2/MANIFEST.json';
const compactControlsBytes=fs.readFileSync(compactControlsPath),compactControls=JSON.parse(compactControlsBytes);assert.equal(hash(compactControlsBytes),'e91d747bef6e88f475aee26d64b69ae9b679526d137c5476ca9d0731d2e6d766');assert.equal(compactControls.bodies.length,3);
const retainedControlsPath='/workspace/scratch/target-clear-default-caller-author-r1/MANIFEST.json',retainedCallerGatePath='/workspace/scratch/target-clear-default-caller-independent-r1/GATE.json';
const retainedControlsBytes=fs.readFileSync(retainedControlsPath),retainedControls=JSON.parse(retainedControlsBytes);
assert.equal(hash(retainedControlsBytes),'5de445351d0849ae37ac3e8b91538219db1e3ad29fee980570a08aa206d5d782');assert.equal(retainedControls.bodies.length,34);assert.equal(controls.bodies.length,3);assert.equal(hash(fs.readFileSync(retainedCallerGatePath)),'36ddead7bcd9647706f33c766952732dc3ff7b42455f2c678b125569bde2c31a');
assert.equal(typeof expected.buildGatePath,'string');assert.equal(typeof expected.buildGateSHA256,'string');
const buildGateBytes=fs.readFileSync(expected.buildGatePath),buildGate=JSON.parse(buildGateBytes);
assert.equal(hash(buildGateBytes),expected.buildGateSHA256);assert.equal(buildGate.decision,expected.buildGateDecision);
const freezeBytes=fs.readFileSync(freezePath),freeze=JSON.parse(freezeBytes);
assert.equal(hash(freezeBytes),expected.freezeSHA256);assert.equal(freeze.stage,stage);
assert.equal(freeze.sourceDigest,expected.sourceDigest);assert.equal(freeze.outputsDigest,expected.outputsDigest);
assert.equal(freeze.inputCount,expected.inputCount);assert.equal(freeze.outputCount,expected.outputCount);
assert.equal(expected.freezeSourceMapKey,'inputs');assert(freeze.inputs&&typeof freeze.inputs==='object'&&!Array.isArray(freeze.inputs));
const admission=JSON.parse(fs.readFileSync(path.join(packet,'ADMISSION.json'))),work=896*1048576,reserve=512*1048576;
const current=Number(fs.readFileSync('/sys/fs/cgroup/memory.current','utf8')),maximum=Number(fs.readFileSync('/sys/fs/cgroup/memory.max','utf8'));
const spent=Math.max(0,current-admission.initial.current);
assert(admission.admitted===true&&admission.stage===stage&&admission.freeze===freezePath&&admission.work===work&&admission.reserve===reserve&&admission.initial.maximum===maximum&&admission.initial.headroom>=work+reserve&&spent<=work&&maximum-current>=reserve+Math.max(0,work-spent),'Same outer896+512 accounting rejected');
assert(admission.initial.free>=expected.estimatedCaptureBytes+expected.estimatedProofBytes+expected.minimumPostCaptureReviewFreeBytes,'Fresh disk admission cannot retain estimated captures plus64MiB review margin');
fs.writeFileSync(path.join(packet,'INSIDE-PHASE-ACCOUNTING.json'),JSON.stringify({work,reserve,current,maximum,spent,remaining:Math.max(0,work-spent),freshAdmission:false,sameOuterAdmission:true})+'\n');
const result={scope:'Native starter opening comparison: frozen76e5/2547 seven assets versus65b31/960e thirteen assets, both same native query, ordinary937240 Initiate. Cairn/freeOrder/heldScourEscape/oneScour/Endturn/enemy response/natural starter hover/one legal second ally; four originals. Native layout capacity2, first300 remaining unobserved. No art/default/animation/fun acceptance.',sourceDigest:freeze.sourceDigest,outputsDigest:freeze.outputsDigest,captureCap:4,perContextCaptureCap:2,captureCapsByCase:expected.captureCapsByCase,actions:[],captures:[],contexts:[],pageErrors:[],browser:'NOT_LAUNCHED',server:'NOT_LAUNCHED',mechanicalPass:false,personallyViewed:false};
result.evidenceSerialization={format:'compact-json-gzip-v1',scope:['VISUAL-PROGRESS.json','VISUAL-RESULT.json'],encoding:'utf8',trailingNewline:'LF',compression:'gzip level6; full serialized UTF8 byte readback verified',rawCheckpointStrings:'unchanged'};
const servers=[];result.servers=[];result.runtimes=expected.runtimes;
let browser,context,page,stopReason=null,timer,auditBefore=false,closingPromise=null,closedBrowser=null,activeCase=null;
const K='hollowpact.run.v2';
const pixelEvents=[];let pixelEventBytes=0;
const pointerEvents=[],observerPrefix='__SETTLE_DRAG_NATIVE__';let pointerEventBytes=0;
const stamp=()=>({utc:new Date().toISOString(),wholeElapsedMs:Date.now()-started});
function log(name,data){fs.appendFileSync(path.join(packet,name),JSON.stringify({...stamp(),...data})+'\n');}
const evidenceFiles={};
function writeEvidence(logicalLeaf,value){
 assert(['VISUAL-PROGRESS.json','VISUAL-RESULT.json'].includes(logicalLeaf));
 const original=Buffer.from(JSON.stringify(value)+'\n'),stored=gzipSync(original,{level:6});
 assert(gunzipSync(stored).equals(original),'Lossless gzip full original-byte readback mismatch');
 const storedLeaf=logicalLeaf+'.gz';fs.writeFileSync(path.join(packet,storedLeaf),stored);
 evidenceFiles[logicalLeaf]={storedLeaf,encoding:'gzip',originalBytes:original.length,originalSHA256:hash(original),storedBytes:stored.length,storedSHA256:hash(stored),fullOriginalByteReadbackVerified:true};
 fs.writeFileSync(path.join(packet,'EVIDENCE-FORMAT.json'),JSON.stringify({format:'lossless-original-compact-json-gzip-v1',scope:'Only progress/final bytes compressed; full R2 selected diagnostic fields/raw strings retained; Cairn duplicate snapshot aliases are explicit stable uiObservations references. Full original R1 fields remain in failed R1 packet. Storage cap is physical; logical bytes reported separately.',files:evidenceFiles})+'\n');
}
function proofMetrics(){
 const files=fs.readdirSync(packet).filter(n=>!n.endsWith('.jpg')&&fs.statSync(path.join(packet,n)).isFile()),stored=files.reduce((n,f)=>n+fs.statSync(path.join(packet,f)).size,0);
 return {stored,logical:stored+Object.values(evidenceFiles).reduce((n,r)=>n+r.originalBytes-r.storedBytes,0)};
}
function persist(){writeEvidence('VISUAL-PROGRESS.json',result);}
function check(){if(stopReason||Date.now()-started>=60000||result.pageErrors.length)throw Error(stopReason||result.pageErrors[0]||'60s paired driver abort');}
// Only exact frozen runtime FINAL leaves may resolve through their pinned chain.
function tracePinnedFile(file){
 assert.equal(file,path.resolve(file),'Noncanonical logical input path');
 const runtime=runtimes.find(r=>file.startsWith(r.stage+path.sep)),policy=runtime?.policy,rel=runtime?path.relative(runtime.stage,file):null,pin=policy?.leaves[rel];
 const decode=p=>{assert(Number.isInteger(p[0])&&typeof p[1]==='string');return policy.roots[p[0]]+p[1];};
 const wanted=pin?policy.chains[pin[2]].map(x=>({path:decode(x[0]),target:decode(x[1]),finalLeaf:x[2]})):[];
 let pending=file.slice(1).split('/'),resolved='/',links=[],nodes=[];
 while(pending.length){
  const part=pending.shift();assert(part&&part!=='.'&&part!=='..');resolved=path.join(resolved,part);
  const st=fs.lstatSync(resolved);nodes.push([resolved,String(st.dev),String(st.ino),st.mode]);
  if(st.isSymbolicLink()){
   assert(links.length<wanted.length,'Unknown or excessive symlink '+resolved);
   const row={path:resolved,target:fs.readlinkSync(resolved),finalLeaf:pending.length===0};assert.deepEqual(row,wanted[links.length],'Changed symlink chain '+resolved);links.push(row);
   const target=path.resolve(path.dirname(resolved),row.target);pending=target.slice(1).split('/').concat(pending);resolved='/';
  }else if(pending.length)assert(st.isDirectory(),'Non-directory parent '+resolved);
  else assert(st.isFile(),'Resolved body must be a regular file '+resolved);
 }
 assert.deepEqual(links,wanted,'Pinned leaf disappeared or chain changed');
 assert.equal(resolved,pin?decode(pin[1]):file,'Unexpected resolved body');
 return {resolved,links,nodes,pinnedSHA256:pin?.[0]??null};
}
function checkAliasPolicy(runtime){
 const {stage,freeze,policy:p,config}=runtime;assert.equal(p.roots[0],stage);assert.equal(Object.keys(p.leaves).length,config.aliasCount);assert.deepEqual(p.roots,config.aliasRoots);
 if(config.aliasBinding==='catalogue-header-freeze')assert.equal(p.freezeSHA256,config.freezeSHA256);
 else assert.deepEqual(freeze.actualAliasCatalogue,{path:config.aliasPolicyPath,sha256:config.aliasPolicySHA256,count:config.aliasCount});
 for(const [rel,pin] of Object.entries(p.leaves)){
  assert(!path.isAbsolute(rel)&&!rel.split('/').some(x=>x==='..'||x==='.'),'Unsafe alias key');
  const body=rel.startsWith('dist/')?freeze.outputs[rel.slice(5)]:freeze.inputs[rel];assert.equal(pin[0],body,'Alias not in exact frozen membership');
  assert(rel.startsWith('desktop/')||rel.startsWith('public/')||rel.startsWith('dist/art/')||rel.startsWith('dist/audio/'),'Source/control alias forbidden');tracePinnedFile(path.join(stage,rel));
 }
}
async function hashFile(file){
 const before=tracePinnedFile(file),h=createHash('sha256');let bytes=0,fd,noAtime=true;
 try{
  try{fd=fs.openSync(before.resolved,fs.constants.O_RDONLY|fs.constants.O_NOATIME|fs.constants.O_NOFOLLOW);}
  catch(e){if(e.code!=='EPERM')throw e;noAtime=false;fd=fs.openSync(before.resolved,fs.constants.O_RDONLY|fs.constants.O_NOFOLLOW);}
  const opened=fs.fstatSync(fd);assert(opened.isFile(),'Opened descriptor is not regular');
  const body=fs.lstatSync(before.resolved);assert(body.isFile()&&body.dev===opened.dev&&body.ino===opened.ino,'Body changed while opening');
  for await(const b of fs.createReadStream(before.resolved,{fd,autoClose:false,highWaterMark:32768})){check();h.update(b);bytes+=b.length;}
  const after=tracePinnedFile(file),finished=fs.fstatSync(fd);assert.deepEqual(after,before,'Runtime alias/parent identity changed during read');
  assert(finished.dev===opened.dev&&finished.ino===opened.ino&&finished.size===bytes&&opened.size===bytes,'Opened body changed during read');
 }finally{if(fd!==undefined)fs.closeSync(fd);}
 const sha256=h.digest('hex');if(before.pinnedSHA256)assert.equal(sha256,before.pinnedSHA256,'Resolved alias full body SHA mismatch');
 return {sha256,bytes,resolvedPath:before.resolved,aliasChain:before.links,noAtime:{requested:true,used:noAtime,permissionFallback:!noAtime}};
}
async function audit(label){
 for(const runtime of runtimes){const {stage,freeze,config}=runtime;const row={label,case:config.case,stage,sourceDigest:freeze.sourceDigest,outputsDigest:freeze.outputsDigest,inputs:[],outputs:[],controls:[]};checkAliasPolicy(runtime);
 row.aliasPolicy=await hashFile(config.aliasPolicyPath);assert.equal(row.aliasPolicy.sha256,config.aliasPolicySHA256,'Full alias policy dependency changed');
 row.freeze=await hashFile(config.freezePath);assert.equal(row.freeze.sha256,config.freezeSHA256);row.buildGate=await hashFile(config.buildGatePath);assert.equal(row.buildGate.sha256,config.buildGateSHA256);
 assert.equal((await hashFile(controlsPath)).sha256,hash(controlsBytes),'Control manifest changed');
 assert.equal((await hashFile(retainedControlsPath)).sha256,hash(retainedControlsBytes));assert.equal((await hashFile(retainedCallerGatePath)).sha256,'36ddead7bcd9647706f33c766952732dc3ff7b42455f2c678b125569bde2c31a');
 assert.equal((await hashFile(compactControlsPath)).sha256,hash(compactControlsBytes));
 for(const [root,bodies] of [[path.dirname(retainedControlsPath),retainedControls.bodies],[path.dirname(compactControlsPath),compactControls.bodies],[path.dirname(controlsPath),controls.bodies]])for(const entry of bodies){const actual=await hashFile(path.join(root,entry.name));assert.equal(actual.sha256,entry.sha256,'Driver/caller control changed '+entry.name);row.controls.push({root,name:entry.name,...actual});}assert.equal(row.controls.length,40);assert.equal(Object.keys(freeze.inputs).length,config.inputCount);assert.equal(Object.keys(freeze.outputs).length,config.outputCount);
 for(const [rel,expected] of Object.entries(freeze.inputs)){check();const actual=await hashFile(path.join(stage,rel));assert.equal(actual.sha256,expected,'Input mismatch '+rel);row.inputs.push({path:rel,...actual});}
 for(const [rel,expected] of Object.entries(freeze.outputs)){check();const actual=await hashFile(path.join(stage,'dist',rel));assert.equal(actual.sha256,expected,'Output mismatch '+rel);row.outputs.push({path:rel,...actual});}
 fs.writeFileSync(path.join(packet,`BYTE-AUDIT-${config.case}-${label}.json`),JSON.stringify(row,null,2)+'\n');
 }
}
async function bounded(promise,ms,label){let t;try{return await Promise.race([promise,new Promise((_,reject)=>{t=setTimeout(()=>reject(Error(label+' timeout')),ms);})]);}finally{clearTimeout(t);}}
async function close(reason){
 if(closingPromise)return closingPromise;
 closingPromise=(async()=>{
  log('LIFECYCLE.jsonl',{event:'close initiated',reason});const errors=[],ownedBrowser=browser;
  try{if(ownedBrowser){await bounded(ownedBrowser.close(),8000,'browser close');closedBrowser=ownedBrowser;result.browser='CLOSED';}}catch(e){errors.push(String(e));result.browser='CLOSE_UNCONFIRMED';}
  for(const owner of servers){if(owner.closed)continue;try{owner.server.closeIdleConnections?.();await bounded(new Promise((resolve,reject)=>owner.server.close(e=>e&&!(e.code==='ERR_SERVER_NOT_RUNNING'&&!owner.server.listening)?reject(e):resolve())),2000,'server close '+owner.receipt.case);owner.closed=true;owner.receipt.status='CLOSED';}catch(e){errors.push(String(e));owner.receipt.status='CLOSE_UNCONFIRMED';}}
  result.server=servers.length===2&&servers.every(o=>o.closed)?'CLOSED':servers.every(o=>o.closed)?'CLOSED_PARTIAL':'CLOSE_UNCONFIRMED';
  if(errors.length){result.closeErrors=errors;result.mechanicalPass=false;process.exitCode=2;}
  log('LIFECYCLE.jsonl',{event:errors.length?'close failures':'normal browser and server close',reason,errors});persist();
 })();return closingPromise;
}
function abort(reason){if(stopReason)return;stopReason=reason;result.abortReason=reason;result.mechanicalPass=false;process.exitCode=2;void close(reason).catch(e=>{result.closeFailure=String(e);process.exitCode=2;});}
process.once('SIGTERM',()=>abort('supervisor SIGTERM'));
timer=setTimeout(()=>abort('60s visual driver abort'),Math.max(0,60000-(Date.now()-started)));
async function owned(locator){
 check();await locator.waitFor();
 // Avoid Playwright's stability-based scroll wait on already visible animated
 // actor bodies. Keep the original scoped scroll path for offscreen controls.
 const existing=await locator.boundingBox(),viewport=page.viewportSize();
 const alreadyFullyVisible=existing&&viewport&&existing.width>0&&existing.height>0&&existing.x>=0&&existing.y>=0&&existing.x+existing.width<=viewport.width&&existing.y+existing.height<=viewport.height;
 if(!alreadyFullyVisible)await locator.scrollIntoViewIfNeeded();await settle();
 let b=await locator.boundingBox();assert(b,'Missing pointer box');await page.mouse.move(b.x+b.width/2,b.y+b.height/2);await settle();
 b=await locator.boundingBox();assert(b,'Owner vanished after hover');const point={x:b.x+b.width/2,y:b.y+b.height/2};
 // Move to the final settled coordinate that will actually be pressed. Do not
 // assert/log a recomputed center while leaving the mouse at the prior center.
 await page.mouse.move(point.x,point.y);await settle();
 assert(await locator.evaluate((e,p)=>{const t=document.elementFromPoint(p.x,p.y);return t===e||e.contains(t);},point),'Fresh actual pointer owner missing');
 assert(await locator.evaluate(e=>!e.disabled&&e.getAttribute('aria-disabled')!=='true'),'Unavailable control');return point;
}

async function rawSave(){check();const raw=await page.evaluate(k=>localStorage.getItem(k),K);assert(raw===null||Buffer.byteLength(raw)<=expected.rawSaveByteCap,'Opaque saved state exceeded declared bound');return raw;}
async function settle(){check();await page.waitForTimeout(220);await page.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));check();}
async function eventsSince(n){return pointerEvents.slice(n);}
const eventRefs=events=>events.map(e=>e.traceIndex);
async function click(locator,label,captureKind=null){
 const p=await owned(locator),before=await rawSave(),n=pointerEvents.length;
 assert(await locator.evaluate((e,p)=>{const t=document.elementFromPoint(p.x,p.y);return t===e||e.contains(t);},p),'Actual press owner changed');
 await page.mouse.down();await page.waitForTimeout(60);check();
 assert(await locator.evaluate((e,p)=>{const t=document.elementFromPoint(p.x,p.y);return t===e||e.contains(t);},p),'Actual release owner changed');
 await page.mouse.up();const release=await page.evaluate(()=>performance.now());
 const action={case:activeCase.name,label,point:p,beforeSHA:before===null?null:hash(before),releaseObservedAtMs:release,assertionsPending:true};result.actions.push(action);persist();
  if(captureKind==='command'){const issued=await observation('immediate post-command issued-result receipt');activeCase.immediateIssuedReceipt={releaseObservedAtMs:release,observedAtMs:issued.observedAtMs,preview:issued.preview};persist();assert.equal(issued.preview.kind,'issued-command','R8 issued result missing after actual command');}
 await settle();const events=await eventsSince(n);action.events=eventRefs(events);action.afterSHA=await rawSave().then(v=>v===null?null:hash(v));persist();
 assert(events.some(e=>e.type==='pointerdown'&&e.trusted&&Math.abs(e.x-p.x)<=1&&Math.abs(e.y-p.y)<=1)&&events.some(e=>e.type==='pointerup'&&e.trusted&&Math.abs(e.x-p.x)<=1&&Math.abs(e.y-p.y)<=1),'Missing trusted native press/release at actual checked coordinates');
 action.assertionsPending=false;persist();
}
async function key(value,label){
 check();const n=pointerEvents.length,before=await rawSave();await page.keyboard.press(value);await settle();
 const events=await eventsSince(n);result.actions.push({case:activeCase.name,label,key:value,events:eventRefs(events),beforeSHA:before===null?null:hash(before),afterSHA:await rawSave().then(v=>v===null?null:hash(v))});persist();
 assert(events.some(e=>e.type==='keydown'&&e.trusted),'Native key event absent');
}
async function shot(label){
 check();assert(result.captures.length<expected.captureCap&&activeCase.captureCount<expected.captureCapsByCase[activeCase.name],'Declared A2/B2 total4 original JPEG capture cap exceeded');
 const entry={case:activeCase.name,label,format:'jpeg',quality:80,path:path.join(packet,`${activeCase.name}-${String(++activeCase.captureCount).padStart(2,'0')}-${label}.jpg`),request:stamp(),requestObservedAtMs:await page.evaluate(()=>performance.now()),phaseCertified:false,pending:true,personallyViewed:false,preCaptureView:await view(activeCase.heldPoint??null,activeCase.targetUID??null)};
 result.captures.push(entry);persist();await page.screenshot({path:entry.path,type:'jpeg',quality:80,fullPage:false});
 entry.completed=stamp();entry.completedObservedAtMs=await page.evaluate(()=>performance.now());Object.assign(entry,await hashFile(entry.path));entry.pending=false;assert(result.captures.reduce((n,c)=>n+(c.bytes??0),0)<=expected.estimatedCaptureBytes,'Actual complete original JPEG bytes exceeded declared2MiB cap');entry.postCaptureView=await view(activeCase.heldPoint??null,activeCase.targetUID??null);entry.phaseMayHaveChanged=JSON.stringify(entry.preCaptureView.fields)!==JSON.stringify(entry.postCaptureView.fields);assert(fs.statfsSync(packet).bavail*fs.statfsSync(packet).bsize>=expected.minimumPostCaptureReviewFreeBytes,'Actual post-capture disk reserve fell below64MiB');persist();
}
async function observation(label){
 check();const row=await page.evaluate(()=>{
  const e=document.querySelector('#consequence-preview');
  return {observedAtMs:performance.now(),viewport:{width:innerWidth,height:innerHeight,dpr:devicePixelRatio},scroll:{width:document.documentElement.scrollWidth,height:document.documentElement.scrollHeight},preview:{kind:e?.dataset.preview,text:e?.innerText??'',fontSize:e?parseFloat(getComputedStyle(e).fontSize):null,rect:e?.getBoundingClientRect().toJSON()??null}};
 });activeCase.observations.push({label,...stamp(),row});persist();assert.equal(row.viewport.width,1440);assert.equal(row.viewport.height,900);assert(row.scroll.width<=1440&&row.scroll.height<=900,'Actual complete1440x900 fit failed '+label);return row;
}
async function checkpoint(label){
 const raw=await rawSave();assert(raw!==null,'Actual run save absent');const file=path.join(packet,`${activeCase.name}-${label}-OPAQUE-SAVE.json`);
 fs.writeFileSync(file,JSON.stringify({observedOnly:true,raw})+'\n');const state=JSON.parse(raw);assert(Number.isFinite(state.rng),'Actual RNG field absent');activeCase.checkpoints[label]={path:file,sha256:hash(raw),rng:state.rng,raw};persist();return state;
}
// Pixel observer wraps native methods only to observe unchanged calls/results.

function installPixelObserver(pins) {
 const prefix='__COHERENT_NATIVE128_OBSERVED__', allowed=new Set(pins.map(p=>p.sha256)), blobs=new Map(), images=new WeakMap(), signatures=new Set();
 const emit=row=>console.debug(prefix+JSON.stringify({atMs:performance.now(),...row}));
 const digest=buffer=>crypto.subtle.digest('SHA-256',buffer).then(b=>Array.from(new Uint8Array(b),n=>n.toString(16).padStart(2,'0')).join(''));
 const originalURL=URL.createObjectURL;
 URL.createObjectURL=function(blob){
  const url=Reflect.apply(originalURL,this,[blob]);
  if(blob instanceof Blob&&blob.type==='image/png'&&blob.size<=65536){
   const identity=blob.arrayBuffer().then(digest);blobs.set(url,identity);
   identity.catch(e=>emit({kind:'observer-error',where:'blob identity',error:String(e)}));
  }
  return url;
 };
 const originalDecode=HTMLImageElement.prototype.decode;
 HTMLImageElement.prototype.decode=function(...args){
  const promise=Reflect.apply(originalDecode,this,args),image=this,identity=blobs.get(image.src);
  if(identity)promise.then(()=>identity.then(sha256=>{
   if(!allowed.has(sha256))return;
   images.set(image,sha256);emit({kind:'decode',sha256,sourceURL:image.src,width:image.naturalWidth,height:image.naturalHeight,complete:image.complete});
  }),e=>emit({kind:'decode-failed',error:String(e)})).catch(e=>emit({kind:'observer-error',where:'decode evidence',error:String(e)}));
  return promise;
 };
 const fallenSHA=pins.find(p=>p.role==='fallen-reaver')?.sha256;let lastFallenSample=-Infinity;
 const originalDraw=CanvasRenderingContext2D.prototype.drawImage;
 CanvasRenderingContext2D.prototype.drawImage=function(...args){
  const returned=Reflect.apply(originalDraw,this,args),image=args[0],sha256=images.get(image);
  if(sha256&&this.canvas.isConnected){
   const transform=this.getTransform(),coords=args.slice(1),mode=document.documentElement.classList.contains('coherent-native128');
   const signature=JSON.stringify([sha256,this.canvas.id,coords,mode]);
   const sampleAtMs=performance.now(),fallen=sha256===fallenSHA;
   if(fallen?sampleAtMs-lastFallenSample>=250:!signatures.has(signature)){
    if(fallen)lastFallenSample=sampleAtMs;signatures.add(signature);emit({kind:'draw',sha256,source:[image.naturalWidth,image.naturalHeight],canvas:{id:this.canvas.id,width:this.canvas.width,height:this.canvas.height,rect:this.canvas.getBoundingClientRect().toJSON()},coords,transform:[transform.a,transform.b,transform.c,transform.d,transform.e,transform.f],smoothing:this.imageSmoothingEnabled,alpha:this.globalAlpha,nativeClass:mode});
   }
  }
  return returned;
 };
}
async function pixelSnapshot(label){
 const at=await page.evaluate(()=>{
  const style=e=>{if(!e)return null;const s=getComputedStyle(e);return {classes:e.className,rect:e.getBoundingClientRect().toJSON(),opacity:s.opacity,transform:s.transform,filter:s.filter,borderColor:s.borderColor,outline:s.outline,outlineOffset:s.outlineOffset,animationName:s.animationName,transition:s.transition,backgroundImage:s.backgroundImage,imageRendering:s.imageRendering,fontSize:s.fontSize,display:s.display,visibility:s.visibility,selected:e.getAttribute('aria-selected'),disabled:e.getAttribute('aria-disabled'),hover:e.matches(':hover'),focusVisible:e.matches(':focus-visible'),text:e.innerText??''};};
  return {observedAtMs:performance.now(),nativeClass:document.documentElement.classList.contains('coherent-native128'),htmlClasses:document.documentElement.className,appClasses:document.querySelector('#app')?.className,reduced:matchMedia('(prefers-reduced-motion: reduce)').matches,cards:[...document.querySelectorAll('.hand-cards .game-card')].map(e=>({card:e.dataset.card,index:e.dataset.index,...style(e)})),ghosts:[...document.querySelectorAll('.tactile-ghost')].map(style),fields:[...document.querySelectorAll('.field-unit')].map(e=>({uid:e.dataset.unit,...style(e)})),hunter:style(document.querySelector('.hunter-icon')),preview:style(document.querySelector('#consequence-preview')),liveUI:[...document.querySelectorAll('.battle-hud,.hud,.intent,.unit-intent,.unit-readout')].map(style)};
 });
 const row={label,...stamp(),...at,eventRefs:pixelEvents.filter(e=>e.case===activeCase.name).map(e=>e.traceIndex)};activeCase.pixelObservations.push(row);persist();return row;
}
function currentNativeAssets(){return runtimes.find(r=>r.config.case===activeCase.name).config.nativeAssets;}
async function decodedBeforeEntry(){
 const until=Math.min(started+55000,Date.now()+6000),own=()=>pixelEvents.filter(e=>e.case===activeCase.name&&e.kind==='decode'&&e.complete&&e.width===128&&e.height===128);
 while(new Set(own().map(e=>e.sha256)).size<currentNativeAssets().length&&Date.now()<until){check();await page.waitForTimeout(60);}
 const records=own();activeCase.decodeBeforeEntry={...stamp(),expected:currentNativeAssets(),records,allRequired:currentNativeAssets().every(p=>records.some(e=>e.sha256===p.sha256))};persist();
 if(!activeCase.decodeBeforeEntry.allRequired){activeCase.pixelAdmissionGap='Actual per-runtime complete successful native128 decodes were not observed before ordinary entry; no synthetic readiness or mode injection';throw Error(activeCase.pixelAdmissionGap);}
}
async function requireActualPixelAdmission(label){
 const row=await pixelSnapshot(label),bodyPins=currentNativeAssets().filter(p=>p.category==='body'),draws=pixelEvents.filter(e=>e.case===activeCase.name&&e.kind==='draw'&&e.nativeClass);
 const valid=e=>e.source[0]===128&&e.source[1]===128&&e.coords.length===8&&JSON.stringify(e.coords.slice(0,4))==='[0,0,128,128]'&&e.coords.every(Number.isInteger)&&e.coords[6]>=128&&e.coords[7]>=128&&e.coords[6]%128===0&&e.coords[7]%128===0&&JSON.stringify(e.transform)==='[1,0,0,1,0,0]'&&!e.smoothing&&e.alpha===1;
 const saved=JSON.parse(await rawSave());const required=bodyPins.filter(p=>p.role==='hunter'||p.role==='reaver'||(saved.enemies.some(u=>u.cardId==='revenant')&&p.role==='gloam')||(saved.allies.some(u=>u.cardId==='cairnhound')&&p.role==='cairn'));
 activeCase.admission={label,nativeClass:row.nativeClass,required,draws:draws.filter(valid),admitted:row.nativeClass&&required.every(p=>draws.some(e=>e.sha256===p.sha256&&valid(e))),continuityCertified:false};persist();
 if(!activeCase.admission.admitted){activeCase.pixelAdmissionGap='Legitimate first entry/binding did not show actual native class and required128 nearest integer draw fingerprint. Prior-layout/phase latch gap possible; no mode forcing.';throw Error(activeCase.pixelAdmissionGap);}
}
async function heldCancelPure(){
 const before=await rawSave(),row=await lift('pure held cancel');
 try{row.hoverAndHeld=await pixelSnapshot('Scour pressed and lifted');await key('Escape','native held Escape cancellation');await page.mouse.up();row.releasePending=false;await settle();assert.equal(await rawSave(),before,'Held Escape cancel altered complete saved state');const v=await view();assert(!activeGhost(v),'Held Escape left active ghost');activeCase.heldCancel={pure:true,beforeSHA:hash(before),afterSHA:hash(await rawSave()),eventRefs:eventRefs(await eventsSince(row.eventsStart)),snapshot:await pixelSnapshot('source restored after pure held cancel')};}
 finally{if(row.releasePending){await page.mouse.up();row.releasePending=false;}}persist();
}


async function uiSnapshot(label){
 const at=await page.evaluate(()=>{
  const rect=e=>e?.getBoundingClientRect().toJSON()??null;
  const intersect=(a,b)=>{if(!a||!b)return null;const left=Math.max(a.left,b.left),top=Math.max(a.top,b.top),right=Math.min(a.right,b.right),bottom=Math.min(a.bottom,b.bottom);return right>left&&bottom>top?{left,top,right,bottom,width:right-left,height:bottom-top}:null;};
  const css=e=>{if(!e)return null;const s=getComputedStyle(e);return {color:s.color,backgroundColor:s.backgroundColor,backgroundImage:s.backgroundImage,borderColor:s.borderColor,opacity:s.opacity,filter:s.filter,fontFamily:s.fontFamily,fontSize:s.fontSize,fontWeight:s.fontWeight,lineHeight:s.lineHeight,whiteSpace:s.whiteSpace,overflowX:s.overflowX,overflowY:s.overflowY,textOverflow:s.textOverflow,lineClamp:s.webkitLineClamp,transform:s.transform,imageRendering:s.imageRendering,visibility:s.visibility,display:s.display};};
  const clip=e=>{if(!e)return null;const r=e.getBoundingClientRect(),s=getComputedStyle(e),left=r.left+parseFloat(s.borderLeftWidth||0),top=r.top+parseFloat(s.borderTopWidth||0);const b={left,top,right:left+e.clientWidth,bottom:top+e.clientHeight,width:e.clientWidth,height:e.clientHeight};let nativeQuad=null;try{nativeQuad=e.getBoxQuads?.({box:'padding'})?.map(q=>[q.p1,q.p2,q.p3,q.p4].map(p=>({x:p.x,y:p.y})))??null;}catch{}return {box:b,quad:nativeQuad??[[{x:b.left,y:b.top},{x:b.right,y:b.top},{x:b.right,y:b.bottom},{x:b.left,y:b.bottom}]],quadSource:nativeQuad?'native CSSOM padding quad':'axis-aligned client clip; only exact if transform none',transform:s.transform,axisAlignedExact:s.transform==='none',overflowX:s.overflowX,overflowY:s.overflowY};};
  const measure=(e,textFragments=true)=>{if(!e)return null;const bounds=rect(e),style=css(e);let fragments=[];if(textFragments){const range=document.createRange();range.selectNodeContents(e);fragments=Array.from(range.getClientRects(),r=>r.toJSON());range.detach();}const clips=[];for(let p=e;p;p=p.parentElement){const c=clip(p);if(c&&(c.overflowX!=='visible'||c.overflowY!=='visible'))clips.push({tag:p.tagName,classes:p.className,...c});}return {tag:e.tagName,classes:e.className,text:e.textContent??'',rect:bounds,style,clientWidth:e.clientWidth,clientHeight:e.clientHeight,scrollWidth:e.scrollWidth,scrollHeight:e.scrollHeight,fragments,textFragmentCoverage:textFragments?'full native Range fragments':'compound container omitted; inner text leaves measured separately',clipChain:clips,fragmentClipIntersections:'derive losslessly from retained fragments and clipChain.box using intersection; not duplicated',solidBackgroundAncestors:(()=>{const a=[];for(let p=e;p&&a.length<8;p=p.parentElement)a.push({classes:p.className,color:getComputedStyle(p).backgroundColor,image:getComputedStyle(p).backgroundImage});return a;})()};};
  const scroller=document.querySelector('#dock .hand-cards'),scrollerClip=clip(scroller);
  const cards=[...document.querySelectorAll('.hand-cards .game-card,.tactile-ghost .game-card')].map(e=>({scope:e.closest('.tactile-ghost')?'clone':'hand',card:e.dataset.card,index:e.dataset.index,selected:e.getAttribute('aria-selected'),ariaDisabled:e.getAttribute('aria-disabled'),hover:e.matches(':hover'),focusVisible:e.matches(':focus-visible'),source:e.classList.contains('tactile-source'),pressed:e.classList.contains('tactile-pressed'),outer:measure(e,false),content:[...e.querySelectorAll('.card-cost,.card-name,.card-kind,.card-description,.card-stats,.card-stats>span,.card-stats .icon,.card-art,.card-art img,.card-art svg')].map(part=>({kind:part.className,...measure(part)})),scrollerClip:e.closest('.hand-cards')?scrollerClip:null}));
  const hunterIcon=document.querySelector('.hunter-icon'),portrait=document.querySelector('.coherent-hunter-portrait'),iconClip=clip(hunterIcon),portraitRect=rect(portrait),visiblePortrait=intersect(portraitRect,iconClip?.box),guidance=document.querySelector('.battle-guidance');
  return {observedAtMs:performance.now(),nativeClass:document.documentElement.classList.contains('coherent-native128'),cards,scroller:{...measure(scroller,false),clip:scrollerClip,scrollLeft:scroller?.scrollLeft,scrollTop:scroller?.scrollTop},hunterIcon:measure(hunterIcon,false),hunterPortrait:{...measure(portrait),naturalWidth:portrait?.naturalWidth??null,naturalHeight:portrait?.naturalHeight??null,complete:portrait?.complete??null,source:portrait?.getAttribute('src')??null,iconClip,visiblePortrait,guidanceOverlap:intersect(visiblePortrait,rect(guidance)),cropIsNotResampledPixelEvidence:true},guidance:measure(guidance),endTurn:[...document.querySelectorAll('.end-turn,.end-turn small')].map(e=>measure(e)),hud:[...document.querySelectorAll('#hud>.hunter-hud,#hud>.journey-hud,#hud>.resources')].map(e=>measure(e,false)),footer:[...document.querySelectorAll('#dock .hand-heading,#dock .turn-controls,.keyboard-hint,footer')].map(e=>measure(e)),fieldActors:[...document.querySelectorAll('#field-controls .field-actor')].map(e=>({uid:e.dataset.actor,...measure(e,false),button:measure(e.querySelector('.field-unit'),false)})),canvas:[...document.querySelectorAll('#arena-wrap canvas')].map(e=>({id:e.id,width:e.width,height:e.height,rect:rect(e)})),viewport:{width:innerWidth,height:innerHeight},scroll:{width:document.documentElement.scrollWidth,height:document.documentElement.scrollHeight}};
 });
 const row={label,...stamp(),...at};activeCase.uiObservations.push(row);persist();assert.equal(row.viewport.width,1440);assert.equal(row.viewport.height,900);assert(row.scroll.width<=1440&&row.scroll.height<=900,'Full1440x900 document fit failed '+label);return row;
}
function uiSnapshotReference(row){const index=activeCase.uiObservations.indexOf(row);assert(index>=0);return {collection:'uiObservations',index,label:row.label};}
async function initialCairnCancel(){
 const card=page.locator('.hand-cards .game-card[data-card="cairnhound"][aria-disabled="false"]').first(),before=await rawSave(),point=await owned(card),eventsStart=pointerEvents.length;
 await page.waitForTimeout(180);assert.equal(await rawSave(),before,'Cairn hover dwell changed complete save');activeCase.cairnHover=uiSnapshotReference(await uiSnapshot('initial Cairn long rules hover'));let held=false;
 try{await page.mouse.down();held=true;await page.waitForTimeout(60);activeCase.cairnPressed=uiSnapshotReference(await uiSnapshot('initial Cairn pressed cost and rules'));await page.mouse.move(point.x,point.y-14,{steps:4});await page.evaluate(()=>new Promise(r=>requestAnimationFrame(r)));activeCase.cairnClone=uiSnapshotReference(await uiSnapshot('initial Cairn held clone before cancellation'));assert(activeGhost(await view()),'Cairn cloned held ghost missing');assert.equal(await rawSave(),before,'Cairn lift mutated complete state');await key('Escape','native initial Cairn held Escape');await page.mouse.up();held=false;await settle();assert.equal(await rawSave(),before,'Cairn cloned cancellation changed full state');assert(!activeGhost(await view()),'Cairn cancellation left active ghost');activeCase.cairnCancelled=uiSnapshotReference(await uiSnapshot('initial Cairn restored after cloned cancel'));activeCase.cairnCancel={pure:true,beforeSHA:hash(before),afterSHA:hash(await rawSave()),eventRefs:eventRefs(await eventsSince(eventsStart))};}
 finally{if(held)await page.mouse.up();}persist();
}

// Observer listeners only read DOM/events and emit local console evidence. No app globals are set.
function installObserver() {
 const read=e=>{
  const target=e.target instanceof Element?e.target:null,under='clientX' in e?document.elementFromPoint(e.clientX,e.clientY):null;
  const info=x=>{const card=x?.closest?.('.game-card'),unit=x?.closest?.('[data-unit]');return {tag:x?.tagName,id:x?.id,classes:x?.className,card:card?.dataset.card,index:card?.dataset.index,unit:unit?.dataset.unit,disabled:unit?.disabled??card?.getAttribute('aria-disabled')??null};};
  const card=target?.closest?.('.game-card'),css=card?getComputedStyle(card):null;
  return {sourceStyle:css?{opacity:css.opacity,transform:css.transform,borderColor:css.borderColor,outline:css.outline,filter:css.filter,classes:card.className}:null,type:e.type,trusted:e.isTrusted,atMs:performance.now(),key:e.key,x:e.clientX,y:e.clientY,buttons:e.buttons,target:info(target),under:info(under),appClasses:document.querySelector('#app')?.className,dragging:!!document.querySelector('[data-tactile-hand].tactile-dragging'),ghosts:[...document.querySelectorAll('.tactile-ghost')].map(g=>({classes:g.className,legal:g.dataset.legal})),ghostLabel:document.querySelector('.tactile-preview')?.innerText??'',previewKind:document.querySelector('#consequence-preview')?.dataset.preview??null,consequence:document.querySelector('#consequence-preview')?.innerText??'',fields:[...document.querySelectorAll('.field-unit')].map(u=>({uid:u.dataset.unit,disabled:u.disabled,classes:u.className}))};
 };
 for(const type of ['pointerdown','pointermove','pointerup','pointercancel','keydown'])addEventListener(type,e=>{if(e.isTrusted)console.debug('__SETTLE_DRAG_NATIVE__'+JSON.stringify(read(e)));},{capture:true,passive:true});
}
async function view(point=null,geometryUID=null){
 check();const measurementRequested=stamp();const value=await page.evaluate(({point,geometryUID,actorCap,controlCap,ghostCap})=>{
  const bounds=e=>e?e.getBoundingClientRect().toJSON():null;const under=point?document.elementFromPoint(point.x,point.y):null,u=under?.closest?.('.field-unit[data-unit]');
  const rect=e=>{if(!e)return null;const r=e.getBoundingClientRect();return {left:r.left,top:r.top,right:r.right,bottom:r.bottom,width:r.width,height:r.height};};
  const intersect=(a,b)=>{
   if(!a||!b)return null;const left=Math.max(a.left,b.left),top=Math.max(a.top,b.top),right=Math.min(a.right,b.right),bottom=Math.min(a.bottom,b.bottom);
   return right>left&&bottom>top?{left,top,right,bottom,width:right-left,height:bottom-top}:null;
  };
  const viewportRect={left:0,top:0,right:innerWidth,bottom:innerHeight,width:innerWidth,height:innerHeight};
  const measured=e=>{
   if(!e)return {present:false,visible:false,rect:null,rawRect:null,text:null,empty:false};
   const rawRect=rect(e),r=intersect(rawRect,viewportRect),css=getComputedStyle(e);
   const visible=e.isConnected&&!e.closest('[hidden]')&&css.display!=='none'&&css.visibility!=='hidden'&&css.visibility!=='collapse'&&Number(css.opacity)>0&&!!r;
   return {present:true,visible,rect:r,rawRect,text:(e.innerText??'').slice(0,300),empty:!e.textContent?.trim()&&e.childElementCount===0};
  };
  const unionArea=rects=>{
   const rs=rects.filter(r=>r&&r.width>0&&r.height>0);if(!rs.length)return 0;
   const xs=[...new Set(rs.flatMap(r=>[r.left,r.right]))].sort((a,b)=>a-b);let area=0;
   for(let i=1;i<xs.length;i++){
    const left=xs[i-1],right=xs[i];let length=0,lastTop=null,lastBottom=null;
    const spans=rs.filter(r=>r.left<right&&r.right>left).map(r=>[r.top,r.bottom]).sort((a,b)=>a[0]-b[0]);
    for(const [top,bottom]of spans){if(lastTop===null){lastTop=top;lastBottom=bottom;}else if(top<=lastBottom)lastBottom=Math.max(lastBottom,bottom);else{length+=lastBottom-lastTop;lastTop=top;lastBottom=bottom;}}
    if(lastTop!==null)length+=lastBottom-lastTop;area+=(right-left)*length;
   }return area;
  };
  const actorParts=actor=>{
   const selectors={button:'.field-unit[data-unit]',nameplate:'.field-nameplate',health:'.health-track',statline:'.field-stat-line',intent:'.field-intent',status:'.field-ready'};
   return Object.entries(selectors).map(([kind,selector])=>{
    const part={key:'actor:'+actor?.dataset.actor+':'+kind,kind,selector,...measured(actor?.querySelector(selector))};
    part.occupied=!((kind==='intent'||kind==='status')&&part.empty);return part;
   });
  };
  let geometry=null;
  if(geometryUID){
   const begunAtMs=performance.now(),saved=JSON.parse(localStorage.getItem('hollowpact.run.v2')??'null');
   const livingUIDs=[...(saved?.allies??[]),...(saved?.enemies??[])].filter(unit=>unit.hp>0).map(unit=>unit.uid);
   const allActors=[...document.querySelectorAll('#field-controls .field-actor')].filter(a=>livingUIDs.includes(a.dataset.actor)&&a.querySelector('.field-unit[data-unit]')?.dataset.unit===a.dataset.actor);
   const actors=allActors.slice(0,actorCap),actor=actors.find(a=>a.dataset.actor===geometryUID),button=actor?.querySelector('.field-unit[data-unit]');
   const allGhosts=[...document.querySelectorAll('.tactile-ghost')],ghosts=allGhosts.slice(0,ghostCap).map((g,index)=>({subject:'ghost-'+index,classes:g.className,legal:g.dataset.legal??null,activeHeld:!!document.querySelector('[data-tactile-hand].tactile-dragging')&&!g.classList.contains('tactile-returning')&&!g.classList.contains('tactile-accepted'),avoidanceDataset:g.dataset.targetAvoidance??null,placementSideDataset:g.dataset.targetSide??null,...measured(g)}));
   const label={subject:'live-label',...measured(document.querySelector('.tactile-preview'))},subjects=[...ghosts,label],parts=actorParts(actor);
   const metric=regions=>{
    const pairs=[],all=[];
    for(const subject of subjects)for(const region of regions){
     const clipped=subject.visible&&region.visible&&region.occupied!==false?intersect(subject.rect,region.rect):null;
     if(clipped)all.push(clipped);
     pairs.push({subject:subject.subject,region:region.key??region.kind,intersectionPx2:clipped?clipped.width*clipped.height:0});
    }
    const perRegion=regions.map(region=>{
     const clips=subjects.map(subject=>subject.visible&&region.visible&&region.occupied!==false?intersect(subject.rect,region.rect):null);
     return {key:region.key??region.kind,kind:region.kind,visible:region.visible,occupied:region.occupied!==false,unionIntersectionPx2:unionArea(clips),rect:region.rect};
    });
    return {pairs,perRegion,bySubject:subjects.map(subject=>({subject:subject.subject,unionIntersectionPx2:unionArea(regions.map(region=>subject.visible&&region.visible&&region.occupied!==false?intersect(subject.rect,region.rect):null))})),combinedUnionIntersectionPx2:unionArea(all),visibleRegionsUnionPx2:unionArea(regions.filter(r=>r.visible&&r.occupied!==false).map(r=>r.rect))};
   };
   const actorDiagnostics=actors.map(a=>{const regions=actorParts(a);return {uid:a.dataset.actor,buttonUID:a.querySelector('.field-unit[data-unit]')?.dataset.unit,regions,overlap:metric(regions)};});
   const neighbors=actorDiagnostics.filter(a=>a.uid!==geometryUID);
   const controlSelectors=['#hud .hunter-icon','#hud .hunter-health','#hud .block-count','#hud .journey-hud > .eyebrow','#hud .journey-hud > strong','#hud .resource','.battle-guidance > span','.battle-guidance > button','#dock .hand-heading > .eyebrow','#dock .first-binding-cue','#dock .pile-buttons > button','#dock .hand-cards > .game-card','#dock .hand-cards > .empty-hand','#dock .energy-orb','#dock [data-action="endTurn"]','#dock .keyboard-hint'];
   const allControls=controlSelectors.flatMap(selector=>[...document.querySelectorAll(selector)].map((e,index)=>({key:'control:'+selector+':'+index,kind:'control',selector,index,occupied:true,...measured(e)})));
   const controls=allControls.slice(0,controlCap),protectedRegions=[...actorDiagnostics.flatMap(a=>a.regions),...controls],protectedOverlap=metric(protectedRegions);
   const missingLivingUIDs=livingUIDs.filter(uid=>!actors.some(a=>a.dataset.actor===uid));
   const duplicateRegionKeys=protectedRegions.map(r=>r.key).filter((key,index,keys)=>keys.indexOf(key)!==index);
   const truncatedActors=allActors.length>actorCap,truncatedControls=allControls.length>controlCap,truncatedGhosts=allGhosts.length>ghostCap;
   const source=document.querySelector('.hand-cards .game-card[data-card="scour"][data-index="1"]');
   geometry={begunAtMs,completedAtMs:performance.now(),actualPoint:point,chosenUID:geometryUID,actorUID:actor?.dataset.actor??null,buttonUID:button?.dataset.unit??null,buttonDisabled:button?.disabled??null,underUID:u?.dataset.unit??null,underActorUID:u?.closest('[data-actor]')?.dataset.actor??null,ownedActorButton:!!button&&button.dataset.unit===geometryUID&&actor.dataset.actor===geometryUID,sourceIdentity:{cardId:source?.dataset.card??null,index:source?.dataset.index??null,revisionAttribute:source?.getAttribute('data-revision')??null},regions:parts,ghosts,label,overlap:metric(parts),actorDiagnostics,controls,protectedOverlap,inventory:{livingUIDs,actorCount:allActors.length,actorCap,truncatedActors,controlCount:allControls.length,controlCap,truncatedControls,missingLivingUIDs,duplicateRegionKeys},neighborDiagnostic:{visibleOtherActorCount:neighbors.length,consideredUIDs:neighbors.map(a=>a.uid),cap:actorCap,truncated:truncatedActors,all:neighbors,intersecting:neighbors.filter(n=>n.overlap.combinedUnionIntersectionPx2>0)},ghostCount:allGhosts.length,ghostCap,truncatedGhosts,measurementComplete:!truncatedActors&&!truncatedControls&&!truncatedGhosts&&!missingLivingUIDs.length&&!duplicateRegionKeys.length,qualification:'Raw and viewport-clipped axis-aligned DOM boxes; per-region union ghost plus label. CSS visibility not paint/alpha/shadow/ancestor occlusion proof. Caps and missing inventory are gaps, never clearance. Living UID ownership uses passive opaque-save read. One synchronous read, not frozen motion. Dataset advisory only.'};
  }
  return {atMs:performance.now(),geometry,actualPoint:point,under:{uid:u?.dataset.unit??null,disabled:u?.disabled??null,actorUID:u?.closest('[data-actor]')?.dataset.actor??null,ownedField:!!u?.closest('#field-controls')},viewport:{width:innerWidth,height:innerHeight,dpr:devicePixelRatio},appClasses:document.querySelector('#app')?.className,dragging:!!document.querySelector('[data-tactile-hand].tactile-dragging'),ghosts:[...document.querySelectorAll('.tactile-ghost')].map(g=>({classes:g.className,legal:g.dataset.legal,rect:bounds(g)})),ghostLabel:document.querySelector('.tactile-preview')?.innerText??'',previewKind:document.querySelector('#consequence-preview')?.dataset.preview??null,consequence:document.querySelector('#consequence-preview')?.innerText??'',dialogOpen:!!document.querySelector('#dialog')?.open,cue:document.querySelector('.first-binding-cue')?.innerText??'',fields:[...document.querySelectorAll('.field-unit')].map(u=>({uid:u.dataset.unit,disabled:u.disabled,classes:u.className,rect:bounds(u)})),cards:[...document.querySelectorAll('.hand-cards .game-card')].map(c=>({card:c.dataset.card,index:c.dataset.index,revision:c.dataset.revision??null,ariaDisabled:c.getAttribute('aria-disabled'),classes:c.className,rect:bounds(c)}))};
 },{point,geometryUID,actorCap:expected.geometryActorCap,controlCap:expected.geometryControlCap,ghostCap:expected.geometryGhostCap});
 if(value.geometry)value.geometry.requestCompletion={requested:measurementRequested,completed:stamp()};return value;
}
async function receipt(label,point=null,geometryUID=null){
 const raw=await rawSave(),row={label,...stamp(),raw,sha256:raw===null?null:hash(raw),view:await view(point,geometryUID)};assert(activeCase.receipts.length<64,'Receipt cap exceeded');activeCase.receipts.push({label,rowAtMs:row.view.atMs,sha256:row.sha256});persist();return row;
}
const stateOf=row=>JSON.parse(row.raw);
const sourceHandles=new WeakMap();
const activeGhost=v=>v.dragging&&v.ghosts.some(g=>!g.classes.includes('tactile-returning')&&!g.classes.includes('tactile-accepted'));
const targetReady=(v,uid)=>v.fields.some(u=>u.uid===uid&&!u.disabled)&&!v.dialogOpen;
async function ready(uid,label,maximumMs=5000){
 const begin=Date.now(),samples=[];let last=null;
 while(Date.now()-begin<maximumMs){check();last=await view(activeCase.heldPoint??null);samples.push({atMs:last.atMs,actualPoint:last.actualPoint,under:last.under,dragging:last.dragging,ghosts:last.ghosts.map(g=>({classes:g.classes,legal:g.legal})),ghostLabel:last.ghostLabel,consequence:last.consequence,dialogOpen:last.dialogOpen,fields:last.fields.filter(u=>u.uid===uid).map(u=>({uid:u.uid,disabled:u.disabled}))});if(targetReady(last,uid)){activeCase.readiness.push({label,samples,ready:true});persist();return last;}await page.waitForTimeout(25);}
 activeCase.readiness.push({label,samples,ready:false});persist();return null;
}
function unit(name){return page.locator('.field-actor:not([hidden])').filter({has:page.locator('.field-nameplate',{hasText:name})}).locator('.field-unit').first();}
function target(uid){return page.locator('.field-unit[data-unit="'+uid+'"]:visible');}
async function lift(label){
 check();const card=page.locator('.hand-cards .game-card[data-card="scour"][data-index="1"][aria-disabled="false"]');assert.equal(await card.count(),1,'Missing actual legal Scour index1');
 const first=await card.boundingBox();assert(first);await page.mouse.move(first.x+first.width/2,first.y+first.height/2);
 const source=await card.boundingBox();assert(source);const p={x:source.x+source.width/2,y:source.y+source.height/2};
 await page.mouse.move(p.x,p.y);
 assert(await card.evaluate((e,p)=>{const u=document.elementFromPoint(p.x,p.y);return u===e||e.contains(u);},p),'Actual Scour press owner absent');
 await pixelSnapshot(label+' source hover before native press');
 const before=await receipt(label+' before native press');assert.equal(stateOf(before).hand[1],'scour');
 const row={label,...stamp(),startWallMs:Date.now(),startAtMs:await page.evaluate(()=>performance.now()),source,point:p,before,eventsStart:pointerEvents.length,releasePending:true};activeCase.gestures.push(row);
 const original=await card.elementHandle();assert(original,'Original owned Scour node missing');sourceHandles.set(row,original);
 row.observedSource=await original.evaluate(e=>({card:e.dataset.card,index:e.dataset.index,revisionAttribute:e.getAttribute('data-revision'),connected:e.isConnected}));
 assert(row.observedSource.connected&&row.observedSource.card==='scour'&&row.observedSource.index==='1');persist();
 await page.mouse.down();
 try{await page.mouse.move(p.x,p.y-14,{steps:4});row.lifted=await receipt(label+' after threshold lift');assert.equal(row.lifted.raw,before.raw,'Lift mutated save');return row;}
 catch(e){await page.mouse.up();row.releasePending=false;throw e;}
}
async function moveToTarget(row,uid,label){
 const box=await target(uid).boundingBox();assert(box,'Actual target bounds absent');const point={x:box.x+box.width/2,y:box.y+box.height/2};
 row.targetGeometries??=[];row.targetGeometries.push({label,...stamp(),box,point});await page.mouse.move(point.x,point.y,{steps:12});
 const observed=await receipt(label,point);row.atTarget=observed;row.currentPoint=point;activeCase.heldPoint=point;assert.equal(observed.raw,row.before.raw,'Holding/moving mutated save before release');return observed;
}
async function release(row,label,{requireLegal=true}={}){
 row.pointerHeldBeforeRelease=row.releasePending===true;
 row.beforeRelease=await receipt(label+' immediately before release',row.currentPoint??null);assert.equal(row.beforeRelease.raw,row.before.raw,'Save changed while pointer held');
 row.preUpSource=await page.evaluate(original=>[...document.querySelectorAll('.hand-cards .game-card.tactile-source')].map(e=>({card:e.dataset.card,index:e.dataset.index,classes:e.className,connected:e.isConnected,sameOriginalNode:e===original,revisionAttribute:e.getAttribute('data-revision')})),sourceHandles.get(row));
 const lastNative=pointerEvents.filter(e=>e.case===activeCase.name&&e.trusted&&['pointerdown','pointermove','pointerup','pointercancel'].includes(e.type)).at(-1),v=row.beforeRelease.view;
 row.preUpOwnedLegalWitness={requireLegal,pointerHeld:row.releasePending===true,lastNative,activeSource:row.preUpSource,actualPoint:row.currentPoint,under:v.under,dragging:v.dragging,ghosts:v.ghosts};persist();
 if(requireLegal){assert(row.releasePending&&lastNative?.trusted&&lastNative.buttons===1&&Math.abs(lastNative.x-row.currentPoint.x)<=1&&Math.abs(lastNative.y-row.currentPoint.y)<=1,'Genuine native pointer-held actual-point witness missing before mouse-up');assert(row.preUpSource.length===1&&row.preUpSource[0].card==='scour'&&row.preUpSource[0].index==='1'&&row.preUpSource[0].connected&&row.preUpSource[0].sameOriginalNode&&row.preUpSource[0].revisionAttribute===row.observedSource.revisionAttribute,'Current original Scour occurrence/nullable DOM revision missing before mouse-up');assert(activeGhost(v)&&v.ghosts.some(g=>g.legal==='true'&&!g.classes.includes('tactile-returning')&&!g.classes.includes('tactile-accepted')),'Active legal held ghost missing before mouse-up');assert(v.under.ownedField&&v.under.uid===activeCase.targetUID&&v.under.actorUID===activeCase.targetUID&&v.under.disabled===false&&targetReady(v,activeCase.targetUID),'Actual sampled under-UID is not the owned legal target before mouse-up');}else assert(!activeGhost(v),'Safe coverage-gap return still has active ghost');

 try{await page.mouse.up();row.releaseAtMs=await page.evaluate(()=>performance.now());row.releasePending=false;}
 finally{if(row.releasePending){await page.mouse.up();row.releasePending=false;}}
 await page.waitForTimeout(100);row.after=await receipt(label+' after native release');const events=await eventsSince(row.eventsStart);row.eventRefs=eventRefs(events);activeCase.heldPoint=null;
 assert(events.some(e=>e.type==='pointerdown'&&e.trusted)&&events.some(e=>e.type==='pointerup'&&e.trusted),'Missing native drag down/up observer receipt');persist();return row.after;
}
async function firstDrop(){
 const row=await lift('first settled Scour drag');try{
  const v=await view();assert(targetReady(v,activeCase.targetUID),'First drag target must be observed ready');
  await moveToTarget(row,activeCase.targetUID,'first drag actual target');await release(row,'first Scour drag');
 }finally{if(row.releasePending){await page.mouse.up();row.releasePending=false;}}
 const before=stateOf(row.before),after=stateOf(row.after),a=after.enemies.find(u=>u.uid===activeCase.targetUID);assert.equal(a?.hp,5);assert.equal(after.energy,before.energy-1);assert.equal(after.stats.damageDealt-before.stats.damageDealt,6);assert.equal(after.hand.filter(id=>id==='scour').length,1);
 activeCase.firstDrop=row;return row;
}
// Opening trial deliberately omits second-card kill/normalization/corpse helpers.
async function starterSnapshot(label){
 const raw=await rawSave(),state=JSON.parse(raw),at=await page.evaluate(()=>{
  const style=e=>{const s=getComputedStyle(e);return {display:s.display,visibility:s.visibility,opacity:s.opacity,imageRendering:s.imageRendering,transform:s.transform,rect:e.getBoundingClientRect().toJSON()};};
  return {atMs:performance.now(),nativeClass:document.documentElement.classList.contains('coherent-native128'),cards:[...document.querySelectorAll('.hand-cards .game-card')].map(e=>({card:e.dataset.card,index:e.dataset.index,ariaLabel:e.getAttribute('aria-label'),ariaDisabled:e.getAttribute('aria-disabled'),hover:e.matches(':hover'),name:e.querySelector('.card-name')?.innerText,cost:e.querySelector('.card-cost')?.innerText,rules:e.querySelector('.card-description')?.innerText,...style(e),images:[...e.querySelectorAll('.coherent-native-art img')].map(i=>({sourceURL:i.src,complete:i.complete,naturalWidth:i.naturalWidth,naturalHeight:i.naturalHeight,...style(i)}))})),actors:[...document.querySelectorAll('#field-controls .field-actor:not([hidden])')].map(e=>({uid:e.dataset.actor,buttonUID:e.querySelector('.field-unit')?.dataset.unit,name:e.querySelector('.field-nameplate')?.innerText,stats:e.querySelector('.field-stat-line')?.innerText,health:e.querySelector('.health-track')?.getAttribute('aria-label'),intent:e.querySelector('.field-intent')?.textContent,...style(e)}))};
 });
 for(const c of at.cards)for(const image of c.images)image.decodeIdentity=pixelEvents.find(e=>e.case===activeCase.name&&e.kind==='decode'&&e.sourceURL===image.sourceURL)?.sha256??null;
 const ownAssets=runtimes.find(r=>r.config.case===activeCase.name).config.nativeAssets,body=ownAssets.find(p=>p.role==='ash'),draws=body?pixelEvents.filter(e=>e.case===activeCase.name&&e.kind==='draw'&&e.sha256===body.sha256):[];
 const row={label,...stamp(),rawSHA256:hash(raw),turn:state.turn,energy:state.energy,allies:state.allies.map(u=>({uid:u.uid,cardId:u.cardId,hp:u.hp})),...at,observedAshBodyDraws:draws,eventRefs:eventRefs(pointerEvents.filter(e=>e.case===activeCase.name)),qualification:'Passive current DOM and exact decoded blob URL identity; source-informed body draw hash is not private UID/continuous pose attribution. Source capacity2 and encounter latch can cause whole fallback; no generated text or hidden art visibility assumption.'};
 activeCase.starterObservations.push(row);assert.equal(await rawSave(),raw,'Read-only family snapshot changed complete save');persist();return row;
}
async function hoverStarter(id,label){
 const state=JSON.parse(await rawSave()),card=page.locator('.hand-cards .game-card[data-card="'+id+'"]');
 if(!state.hand.includes(id)||await card.count()!==1){activeCase.starterGaps.push({label,status:'DRAW_OR_UNIQUE_CARD_NOT_OBSERVED',id,...stamp()});persist();return null;}
 const before=await rawSave(),start=pointerEvents.length;await owned(card);await page.waitForTimeout(180);assert.equal(await rawSave(),before,'Ordinary starter hover changed complete save');
 const row=await starterSnapshot(label);row.hoverEventRefs=eventRefs(await eventsSince(start));assert(row.hoverEventRefs.length&&pointerEvents.some(e=>row.hoverEventRefs.includes(e.traceIndex)&&e.type==='pointermove'&&e.trusted),'Ordinary hover trusted movement absent');persist();return row;
}
async function openingEndTurn(label){
 const before=JSON.parse(await rawSave());assert.equal(before.phase,'battle');
 const intents=before.enemies.map(u=>({uid:u.uid,name:u.name,intent:u.intent}));await click(page.locator('[data-action="endTurn"]:visible'),'ordinary '+label);
 const after=await checkpoint(label),notes=intents.map(u=>u.name+': '+u.intent.label+'.');
 activeCase.enemyResponses.push({label,...stamp(),intents,beforeHP:before.hp,afterHP:after.hp,beforeAllies:before.allies,afterAllies:after.allies,notes,actualLog:after.log,notesMatched:notes.every(n=>after.log.includes(n)),phase:after.phase});
 assert(notes.every(n=>after.log.includes(n)),'Ordinary enemy response source intent notes missing');
 if(after.phase==='battle'){assert.equal(after.turn,before.turn+1);assert.equal(after.stats.turns,before.stats.turns+1);assert(after.allies.every(u=>!u.acted));assert.equal(after.energy,5);assert.equal(after.hand.length,5);}
 persist();return after;
}

async function runCase(name,query,scenario,feedbackEnabled){
 const runtime=runtimes.find(r=>r.config.case===name);assert(runtime,'Unknown runtime case');
 const row={runtime:{stage:runtime.stage,freezeSHA256:runtime.config.freezeSHA256,sourceDigest:runtime.freeze.sourceDigest,outputsDigest:runtime.freeze.outputsDigest,port:runtime.config.port},uiObservations:[],pixelObservations:[],name,query,scenario,feedbackEnabled,seed:937240,classification:'Source-informed opening-prefix native starter diagnostic; not300 or human fun',starterObservations:[],starterGaps:[],enemyResponses:[],sessionStartedWallMs:Date.now(),captureCount:0,checkpoints:{},observations:[],receipts:[],readiness:[],gestures:[],context:'NOT_CREATED',completed:false};result.contexts.push(row);activeCase=row;persist();
 let ownedContext;
 try{
  check();ownedContext=await browser.newContext({viewport:{width:1440,height:900},deviceScaleFactor:1,reducedMotion:'no-preference'});context=ownedContext;row.context='OPEN';
  await ownedContext.addInitScript(installObserver);await ownedContext.addInitScript(installPixelObserver,runtime.config.nativeAssets);page=await ownedContext.newPage();page.setDefaultTimeout(4000);
  page.on('console',m=>{const text=m.text();if(!text.startsWith(observerPrefix))return;try{const event=JSON.parse(text.slice(observerPrefix.length));event.case=name;event.received=stamp();event.traceIndex=pointerEvents.length;pointerEventBytes+=Buffer.byteLength(text);if(pointerEvents.length>=expected.pointerEventCap||pointerEventBytes>expected.pointerEventByteCap){result.traceLimitExceeded=true;abort('native observer declared event/byte cap');return;}pointerEvents.push(event);log('NATIVE-POINTERS.jsonl',event);}catch(e){result.pageErrors.push('observer parse '+String(e));}});
  page.on('console',m=>{const text=m.text(),prefix='__COHERENT_NATIVE128_OBSERVED__';if(!text.startsWith(prefix))return;try{const e=JSON.parse(text.slice(prefix.length));e.case=name;e.received=stamp();e.traceIndex=pixelEvents.length;pixelEventBytes+=Buffer.byteLength(text);if(pixelEvents.length>=expected.pixelEventCap||pixelEventBytes>expected.pixelEventByteCap){abort('passive pixel observer declared event/byte cap');return;}pixelEvents.push(e);log('NATIVE-PIXEL-OBSERVATIONS.jsonl',e);}catch(e){result.pageErrors.push('pixel observer parse '+String(e));}});
  page.on('pageerror',e=>{result.pageErrors.push(String(e));log('ERRORS.jsonl',{case:name,error:String(e)});});
  row.navigationRequested=stamp();row.sessionStartedWallMs=Date.now();await page.goto('http://127.0.0.1:'+runtime.config.port+'/'+query,{waitUntil:'domcontentloaded',timeout:12000});await settle();assert.equal(await rawSave(),null);await decodedBeforeEntry();await pixelSnapshot('ordinary first menu before new contract');
  await click(page.locator('#scene-ui [data-ui="new"]'),'open ordinary new contract');assert(await page.locator('input[name="difficulty"][value="0"]').isChecked());
  await click(page.locator('[data-hunt-disclosure="hunt-seed-panel"]'),'ordinary seed disclosure');await click(page.locator('#seed'),'native seed field');
  const seedEvents=pointerEvents.length;await page.keyboard.press('Control+A');await page.keyboard.type('937240',{delay:25});assert.equal(await page.locator('#seed').inputValue(),'937240');await settle();const seedInputEvents=await eventsSince(seedEvents);row.seedInputEventRefs=eventRefs(seedInputEvents);assert(seedInputEvents.some(e=>e.type==='keydown'&&e.trusted&&e.target.id==='seed'));
  await click(page.locator('#new-game-form [type="submit"]'),'accept typed seed937240 Initiate');await page.waitForTimeout(600);await settle();
  let s=JSON.parse(await rawSave());if(s.phase==='map'){await click(page.locator('[data-action="travel"]:visible').first(),'ordinary first visible travel');await page.waitForTimeout(600);await settle();}
  s=await checkpoint('C0');assert.equal(s.seed,937240);assert.equal(s.difficulty,0);assert.equal(s.phase,'battle');assert.equal(s.floor,1);assert.equal(s.turn,1);assert.equal(s.hand.length,5);const neutralBefore=await rawSave(),neutralStart=pointerEvents.length,neutralRequested=stamp();const neutralClear=await page.evaluate(()=>{const h=document.querySelector('.hand-cards')?.getBoundingClientRect(),under=document.elementFromPoint(10,10);return !!h&&!(10>=h.left&&10<=h.right&&10>=h.top&&10<=h.bottom)&&!under?.closest('.game-card');});assert(neutralClear,'Initial neutral point must be outside actual hand/card');await page.mouse.move(10,10);await page.waitForTimeout(180);await settle();assert.equal(await rawSave(),neutralBefore,'Neutral mouse move/dwell changed complete save');const neutralEvents=await eventsSince(neutralStart);assert(neutralEvents.some(e=>e.type==='pointermove'&&e.trusted&&e.x===10&&e.y===10),'Genuine initial neutral pointer event missing');row.initialNeutral={requested:neutralRequested,completed:stamp(),point:{x:10,y:10},dwellMs:180,pure:true,eventRefs:eventRefs(neutralEvents)};await uiSnapshot('initial full five-card hand before binding');await pixelSnapshot('actual first battle');await requireActualPixelAdmission('ordinary first battle');
  row.initialCairnCloneCancel={status:'NOT_ATTEMPTED',reason:'Opening prefix retains ordinary Cairn hover/bind and real Scour Escape instead of duplicate Cairn clone diagnostics'};
  const cairn=page.locator('.hand-cards .game-card[data-card="cairnhound"][aria-disabled="false"]').first();assert.equal(await cairn.count(),1);row.bindingOccurrence={index:await cairn.getAttribute('data-index'),card:await cairn.getAttribute('data-card')};
  await click(cairn,'bind actual Cairn occurrence');const bound=await checkpoint('C1');row.cairnUID=await unit('Cairn Hound').getAttribute('data-unit');row.targetUID=await unit('Ironjaw Reaver').getAttribute('data-unit');
  await pixelSnapshot('bound rear ally');await requireActualPixelAdmission('bound rear ally');
  row.targetLabel=bound.enemies.find(u=>u.uid===row.targetUID).name+' · hostile '+(bound.enemies.findIndex(u=>u.uid===row.targetUID)+1);
   assert(bound.allies.some(u=>u.uid===row.cairnUID&&u.cardId==='cairnhound'&&!u.acted));assert.equal(bound.enemies.find(u=>u.uid===row.targetUID)?.hp,16);assert.equal(bound.energy,s.energy-1);assert.equal(bound.hand.filter(id=>id==='scour').length,2);
  row.targetAlternatives=bound.enemies.map(u=>({uid:u.uid,name:u.name,hp:u.hp,block:u.block,intent:u.intent}));row.choiceRationale='Choose currently unarmored Ironjaw Reaver for Cairn bonus; alternate Gloam piercing threat remains observed.';assert(await ready(row.targetUID,'settled after binding'));await click(unit('Cairn Hound'),'select observed READY Cairn');await pixelSnapshot('selected READY ally');await click(target(row.targetUID),'free Cairn Order into actual Reaver','command');
  await uiSnapshot('post Order costs Endturn contrast HUD and footer');await pixelSnapshot('post actual free Order command');
  const commanded=await checkpoint('C2');assert(commanded.allies.find(u=>u.uid===row.cairnUID)?.acted);assert.equal(commanded.energy,bound.energy);assert.deepEqual(commanded.hand,bound.hand);assert.equal(commanded.enemies.find(u=>u.uid===row.targetUID)?.hp,11);assert.equal(commanded.stats.damageDealt-bound.stats.damageDealt,5);assert(await ready(row.targetUID,'settled before first Scour'));
  // Deliberate opening-session protocol replacement; no second Scour or corpse waits.
  const beforeCancel=await rawSave();await heldCancelPure();assert.equal(await rawSave(),beforeCancel);await checkpoint('C-cancelled');
  const first=await firstDrop();await checkpoint('C-firstDrop');await page.waitForTimeout(350);assert.equal(await rawSave(),first.after.raw,'Queued or repeated spend after one legal release');row.noQueuedActionAfterRelease=true;
  const turn2=await openingEndTurn('C-endTurn');
  if(turn2.phase!=='battle')throw Error('Opening entered actual terminal phase before starter hand; preserved outcome, no forced turn');
  row.firstStarterHand=await starterSnapshot('first actual turn2 family hand');
  await hoverStarter('ashwidow','first naturally drawn Ash Widow hover');await hoverStarter('fenstalker','first naturally drawn Fen Stalker hover');
  await uiSnapshot('turn2 starter hand live costs rules portraits');await shot('turn2-starter-hand');
  let second=JSON.parse(await rawSave());const chosen=second.hand.includes('ashwidow')?'ashwidow':second.hand.includes('fenstalker')?'fenstalker':null;
  const legalCard=chosen?page.locator('.hand-cards .game-card[data-card="'+chosen+'"][aria-disabled="false"]'):null;
  if(chosen&&second.phase==='battle'&&second.allies.length<2&&second.energy>=2&&await legalCard.count()===1){
   const before=await rawSave(),previous=second.allies.map(u=>u.uid);row.secondBinding={chosen,...stamp(),beforeSHA256:hash(before),occurrence:await legalCard.getAttribute('data-index')};
   await click(legalCard,'ordinary legal second binding '+chosen);second=await checkpoint('C-starterBound');
   const added=second.allies.filter(u=>!previous.includes(u.uid));assert.equal(added.length,1);assert.equal(added[0].cardId,chosen);assert(second.allies.length<=2);assert.equal(second.energy,JSON.parse(before).energy-2);assert.equal(second.stats.cardsPlayed,JSON.parse(before).stats.cardsPlayed+1);
   row.secondBinding.afterUID=added[0].uid;row.secondBinding.afterSHA256=hash(await rawSave());row.secondBinding.observedOnly=true;
  }else{row.starterGaps.push({label:'second binding',status:'LEGAL_SECOND_BINDING_NOT_AVAILABLE',chosen,...stamp()});await checkpoint('C-starterBound');}
  await starterSnapshot('after actual second binding or honest gap');await uiSnapshot('second ally live readouts and hand');await shot('second-starter-field');
  // Keep optional turn3 observable but leave enough finite shared driver budget for B and closure.
  const elapsed=Date.now()-started,limit=name.startsWith('A-')?25000:48000;
  if(elapsed<limit&&second.phase==='battle'&&await page.locator('[data-action="endTurn"]:visible:not([disabled])').count()===1){
   const turn3=await openingEndTurn('C-nextEndTurn');
   if(turn3.phase==='battle')await hoverStarter('briarcolossus','first naturally drawn Briar Colossus hover');
   else row.starterGaps.push({label:'Briar hand',status:'ACTUAL_TERMINAL_PHASE',phase:turn3.phase,...stamp()});
  }else row.starterGaps.push({label:'optional next Endturn and Briar',status:'NOT_ATTEMPTED_FINITE_BUDGET_OR_LEGAL_PHASE',elapsedMs:elapsed,limitMs:limit,...stamp()});
  row.nativeContinuityObserved=row.starterObservations.every(o=>o.nativeClass);row.first300={elapsedPrefixMs:Date.now()-row.sessionStartedWallMs,remainingUnobservedMs:Math.max(0,300000-(Date.now()-row.sessionStartedWallMs)),completed300:false,humanAttentionOrFunObserved:false};
  row.coverage={secondAlly:!!row.secondBinding?.afterUID,FenBody:false,BriarBody:false,thirdBinding:false,continuousPixels:false,transientHeldDisabledToReady:false};row.supplemental={reload:'NOT_ATTEMPTED',reducedMotion:'NOT_ATTEMPTED',corpseExpiry:'NOT_ATTEMPTED',thirdBinding:'NOT_ATTEMPTED_SOURCE_LAYOUT_LIMIT2'};row.completed=true;persist();
 }catch(e){row.failure=e.stack;persist();throw e;}
 finally{if(ownedContext){try{await bounded(ownedContext.close(),4000,'case context close');row.context='CLOSED';}catch(e){row.context='CLOSE_UNCONFIRMED';row.closeFailure=String(e);process.exitCode=2;throw e;}finally{persist();}}}
}

try{
 await audit('before');auditBefore=true;check();
 for(const runtime of runtimes){
  const keys=Object.keys(runtime.freeze.outputs).sort(),receipt={case:runtime.config.case,stage:runtime.stage,port:runtime.config.port,host:'127.0.0.1',status:'CREATED'},owner={receipt,closed:false};
  owner.server=http.createServer((req,res)=>{try{const pathname=new URL(req.url,'http://localhost').pathname,key=pathname==='/'?'index.html':decodeURIComponent(pathname.slice(1));if(!keys.includes(key)){res.writeHead(404);res.end('Not found');return;}res.setHeader('Content-Type',key.endsWith('.html')?'text/html':key.endsWith('.js')?'text/javascript':key.endsWith('.css')?'text/css':key.endsWith('.png')?'image/png':key.endsWith('.wav')?'audio/wav':key.endsWith('.json')?'application/json':'application/octet-stream');const stream=fs.createReadStream(path.join(runtime.stage,'dist',key));stream.on('error',()=>res.destroy());stream.pipe(res);}catch{res.writeHead(400);res.end('Bad request');}});
  servers.push(owner);result.servers.push(receipt);await new Promise((resolve,reject)=>{owner.server.once('error',reject);owner.server.listen(runtime.config.port,'127.0.0.1',resolve);});receipt.status='OPEN';result.server='OPEN';check();
  const served=[];for(const rel of keys){check();const response=await fetch(`http://127.0.0.1:${runtime.config.port}/${rel.split('/').map(encodeURIComponent).join('/')}`,{signal:AbortSignal.timeout(8000)});assert(response.ok,'Serve failed '+rel);const h=createHash('sha256');let bytes=0;for await(const b of response.body){check();h.update(b);bytes+=b.length;}const sha256=h.digest('hex');assert.equal(sha256,runtime.freeze.outputs[rel],'Served mismatch '+rel);served.push({path:rel,bytes,sha256});}
  fs.writeFileSync(path.join(packet,`SERVED-BYTE-AUDIT-${runtime.config.case}.json`),JSON.stringify({stage:runtime.stage,sourceDigest:runtime.freeze.sourceDigest,outputsDigest:runtime.freeze.outputsDigest,served},null,2)+'\n');
 }

 check();browser=await chromium.launch({headless:true,executablePath:'/usr/bin/chromium',args:['--no-sandbox'],timeout:12000});result.browser='OPEN';check();
 for(const scenario of expected.scenarios){for(const entry of expected.cases)await runCase(entry.name,entry.query,scenario,entry.feedbackEnabled);}
 result.canonicalComparisons=[];const a=result.contexts[0],b=result.contexts[1];
 for(const label of ['C0','C1','C2','C-cancelled','C-firstDrop','C-endTurn','C-starterBound']){const x=a.checkpoints[label],y=b.checkpoints[label],equal=!!x&&!!y&&x.raw===y.raw;result.canonicalComparisons.push({label,byteEqual:equal,aSHA:x?.sha256??null,bSHA:y?.sha256??null});assert(equal,'Complete opening raw save mismatch '+label);}
 result.optionalNextTurnComparison={aAttempted:!!a.checkpoints['C-nextEndTurn'],bAttempted:!!b.checkpoints['C-nextEndTurn'],byteEqual:a.checkpoints['C-nextEndTurn']&&b.checkpoints['C-nextEndTurn']?a.checkpoints['C-nextEndTurn'].raw===b.checkpoints['C-nextEndTurn'].raw:null,qualification:'Finite-budget branch may be missing; no normalization or fabricated matching state'};
 if(result.optionalNextTurnComparison.aAttempted&&result.optionalNextTurnComparison.bAttempted)assert(result.optionalNextTurnComparison.byteEqual,'Optional ordinary next-turn full save mismatch');
 assert.equal(result.captures.length,4);assert(result.captures.every(c=>!c.pending&&c.quality===80));
 const initial=c=>c.uiObservations.find(r=>r.label==='initial full five-card hand before binding');
 for(const c of result.contexts){const ui=initial(c),cards=ui?.cards.filter(r=>r.scope==='hand')??[];assert.equal(cards.length,5);for(const card of cards)for(const kind of ['card-cost','card-name','card-description']){const parts=card.content.filter(p=>typeof p.kind==='string'&&p.kind.split(' ').includes(kind));assert.equal(parts.length,1);const part=parts[0];assert(part.rect?.width>0&&part.rect?.height>0&&part.style?.color&&Array.isArray(part.fragments)&&Array.isArray(part.clipChain));}}
 result.nativeContinuity={baseline:a.nativeContinuityObserved,trial:b.nativeContinuityObserved,trialSecondAlly:b.secondBinding??null,observedFamily:a.starterObservations.map(o=>({label:o.label,nativeClass:o.nativeClass})),trialFamily:b.starterObservations.map(o=>({label:o.label,nativeClass:o.nativeClass})),qualityAccepted:false,qualification:'Whole native continuity is measured source-informed class/draw/DOM evidence, not all-actor photograph acceptance or an animation certificate. Third ally layout remains unsupported.'};
 result.completeRawPairs=result.canonicalComparisons.every(r=>r.byteEqual);result.pixelEvents=pixelEvents;result.pixelEventBytes=pixelEventBytes;result.nativeEventBytes=pointerEventBytes;result.transientCoverageComplete=false;result.hypothesisAccepted=false;result.causeEstablished=false;result.uiLegibilityQualityAccepted=false;result.requiresIndependentGameplayVisualTechnicalReview=true;
 result.completed=true;result.mechanicalPass=true;persist();
}catch(e){result.failure=e.stack;result.mechanicalPass=false;process.exitCode=2;log('FAILURE.jsonl',{error:String(e)});}
finally{
 await close(stopReason||'paired actual checks completed or failed');
 if(browser&&browser!==closedBrowser||servers.some(o=>!o.closed)){closingPromise=null;await close('final late-created or unconfirmed resource cleanup');}
 if(auditBefore&&!stopReason){try{await audit('after');}catch(e){result.afterAuditFailure=e.stack;result.mechanicalPass=false;process.exitCode=2;}}
 result.wholeElapsedMs=Date.now()-started;result.elapsedScope='This payload marker precedes final gzip/fsync; DRIVER-FINAL-CLOSURE and terminal elapsed/exit check govern full driver work';if(stopReason){result.mechanicalPass=false;process.exitCode=2;}
 result.pixelEvents=pixelEvents;
 const beforeFinal=proofMetrics();result.actualProofBytesBeforeFinal=beforeFinal.stored;result.actualLogicalProofBytesBeforeFinal=beforeFinal.logical;
 result.proofAccountingScope='actualProofBytes fields measure physical retained storage; actualLogicalProofBytes fields replace gzip lengths with exact original lengths. AfterFinal is measured after first compressed final write; supervisor post-lifecycle FINAL-PACKET-CAPS including all receipts is authoritative.';
 writeEvidence('VISUAL-RESULT.json',result);const afterFirst=proofMetrics();result.actualProofBytesAfterFinal=afterFirst.stored;result.actualLogicalProofBytesAfterFinal=afterFirst.logical;
 if(afterFirst.stored>expected.estimatedProofBytes){result.proofCapExceeded=true;result.mechanicalPass=false;process.exitCode=2;}
 writeEvidence('VISUAL-RESULT.json',result);
 const afterRewrite=proofMetrics();if(afterRewrite.stored>expected.estimatedProofBytes){result.proofCapExceeded=true;result.mechanicalPass=false;process.exitCode=2;writeEvidence('VISUAL-RESULT.json',result);}
 // Only owned proof outputs are fsynced; no source/stage/archive write.
 for(const name of fs.readdirSync(packet)){const file=path.join(packet,name);if(fs.statSync(file).isFile()){const fd=fs.openSync(file,fs.constants.O_RDONLY);try{fs.fsyncSync(fd);}finally{fs.closeSync(fd);}}}
 const dirfd=fs.openSync(packet,fs.constants.O_RDONLY);try{fs.fsyncSync(dirfd);}finally{fs.closeSync(dirfd);}
 const measured=proofMetrics(),closure={phase:'after all gzip roundtrips, proof metrics and owned proof/data fsync',elapsedMs:Date.now()-started,storedProofBytes:measured.stored,logicalProofBytes:measured.logical,allBrowserServerClosed:result.browser==='CLOSED'&&servers.length===2&&servers.every(o=>o.closed),fullLogicalFieldsRetained:true,terminalCheckStillRequired:true};
 const closureBody=Buffer.from(JSON.stringify(closure)+'\n');assert(closureBody.length<=4096);if(measured.stored+closureBody.length>expected.estimatedProofBytes){process.exitCode=2;result.mechanicalPass=false;}
 const cf=fs.openSync(path.join(packet,'DRIVER-FINAL-CLOSURE.json'),'wx');try{fs.writeSync(cf,closureBody);fs.fsyncSync(cf);}finally{fs.closeSync(cf);}
 const cdir=fs.openSync(packet,fs.constants.O_RDONLY);try{fs.fsyncSync(cdir);}finally{fs.closeSync(cdir);}
 const terminalElapsedMs=Date.now()-started;clearTimeout(timer);if(terminalElapsedMs>=60000||stopReason){process.exitCode=2;result.mechanicalPass=false;}
 console.log(JSON.stringify({browser:result.browser,server:result.server,completed:result.completed,mechanicalPass:result.mechanicalPass,captures:result.captures.length,contexts:result.contexts.map(x=>({name:x.name,context:x.context,completed:x.completed})),payloadElapsedMs:result.wholeElapsedMs,wholeElapsedMs:terminalElapsedMs,elapsedIncludesCompressionCapsAndFsync:true,failure:result.failure?.split('\n')[0],abortReason:stopReason}));
}
