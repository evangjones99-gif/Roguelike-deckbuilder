// SOURCE ONLY. External module and browser execution require Root's exact grant.
import fs from 'node:fs';
import path from 'node:path';
import http from 'node:http';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {performance} from 'node:perf_hooks';
const ROOT=path.dirname(new URL(import.meta.url).pathname), STAGE='/workspace/scratch/starter-static-recovered-stage-r1';
const FREEZE='/workspace/scratch/starter-static-recovered-authority-r1/NEW-RUNTIME-FREEZE.json';
const DEPS='/workspace/scratch/starter-opening-runtime-dependency-evidence-r3/DEPENDENCIES.json';
const SOURCE='65b31b3f21e34a624bdac962e4919c7dc1791e502eb6cfdb1612103b8036fe9c';
const OUTPUT='960e723da3b98d31e99e2b4ce6ee2195dd9fea1bfce9c8254b3cb65c04b7b49d';
const K='hollowpact.run.v2', M=1048576;
const mono=()=>Number(process.hrtime.bigint())/1e6;
let outerEntry,outerDeadline,workDeadline,workTimer,closingPromise;
const workLeft=()=>Math.max(0,workDeadline-mono());
async function bound(promise,label,ms=4000,cleanup=false){const left=cleanup?Math.max(0,outerDeadline-mono()-1500):workLeft();assert(left>0,label+' deadline exhausted');let t;try{return await Promise.race([promise,new Promise((_,reject)=>{t=setTimeout(()=>reject(Error(label+' bounded timeout')),Math.min(ms,left));})]);}finally{clearTimeout(t);}}
const sha=b=>createHash('sha256').update(b).digest('hex');
function regular(p){assert(path.isAbsolute(p));let current='/';for(const part of p.slice(1).split('/')){assert(part&&part!=='.'&&part!=='..');current=path.join(current,part);assert(!fs.lstatSync(current).isSymbolicLink(),'Symlink '+current);}assert(fs.lstatSync(p).isFile());return fs.readFileSync(p);}
function pinned(p,h){const b=regular(p);assert.equal(sha(b),h,'Pin mismatch '+p);return b;}
const grant=JSON.parse(regular(process.argv[2]));
assert(grant.enabled===true&&grant.rootMethodReviewed===true&&grant.independentTechnicalSourceReviewed===true&&grant.bFullBodyReviewed===true,'Root and independent review boundary remains closed');
assert.equal(grant.wholeBudgetSeconds,350);assert.equal(grant.observationSeconds,300);
const manifestBytes=pinned(path.join(ROOT,'MANIFEST.json'),grant.methodManifestSHA256),manifest=JSON.parse(manifestBytes);
for(const [name,pin] of Object.entries(manifest.files))pinned(path.join(ROOT,name),pin.sha256);
for(const review of [grant.rootReview,grant.technicalSourceReview,grant.bAuthority,grant.bFullBodyReview]){assert(review&&review.path&&review.sha256);pinned(review.path,review.sha256);}
const freezeBytes=pinned(FREEZE,grant.freezeSHA256),freeze=JSON.parse(freezeBytes);
assert.equal(freeze.stage,STAGE);assert.equal(freeze.sourceDigest,SOURCE);assert.equal(freeze.outputsDigest,OUTPUT);
assert.equal(freeze.inputCount,104);assert.equal(freeze.outputCount,70);
const depsBytes=pinned(DEPS,grant.dependenciesSHA256),deps=JSON.parse(depsBytes);assert.equal(deps.packageVersion,'1.62.0');assert.equal(deps.files.length,404);
assert.equal(deps.modulePath,'/opt/codex/runtimes/codex-primary-runtime/dependencies/python/lib/python3.12/site-packages/playwright/driver/package/index.mjs');
assert.equal(deps.browserExecutablePath,'/usr/lib/chromium/chromium');
const packet=grant.actualPacket;assert.equal(packet,process.argv[3]);assert(path.isAbsolute(packet)&&packet.startsWith('/workspace/scratch/starter-first300-observer-actual-'));
const admission=JSON.parse(regular(path.join(packet,'ADMISSION.json')));assert.equal(admission.work,896*M);assert.equal(admission.reserve,512*M);assert.equal(admission.admitted,true);assert.equal(admission.wholeBudgetSeconds,350);
assert.equal(sha(regular(process.argv[2])),admission.grantSHA256);
outerEntry=admission.outerEntryMonotonicSeconds*1000;outerDeadline=admission.outerDeadlineMonotonicSeconds*1000;workDeadline=admission.workerCutoffMonotonicSeconds*1000;
assert.equal(outerDeadline-outerEntry,350000);assert.equal(workDeadline-outerEntry,337000);assert(mono()>=outerEntry&&mono()<workDeadline,'Shared Linux monotonic clock/work cutoff mismatch');
const result={classification:'Source-informed 300-second agent observation, not human play or fun approval',sourceDigest:SOURCE,outputsDigest:OUTPUT,actions:0,observations:0,captures:[],completed300:false,mechanicalFailures:[],browser:'NOT_LAUNCHED',server:'NOT_STARTED',passiveIntervals:0};
let browser,server,page,context,launchAt=null,journalBytes=0,shots=0,stopping=false;
const stamp=()=>({utc:new Date().toISOString(),wholeElapsedMs:mono()-outerEntry,launchElapsedMs:launchAt===null?null:performance.now()-launchAt});
const proofBytes=()=>fs.readdirSync(packet).reduce((n,k)=>{const s=fs.statSync(path.join(packet,k));return n+(s.isFile()?s.size:0);},0);
function check(){assert(!stopping,'Stopped');assert(mono()<workDeadline,'337s outer worker cutoff; cleanup reserve');if(page)page.setDefaultTimeout(Math.max(1,Math.min(4000,workLeft())));assert(proofBytes()<=71*M,'71MiB physical proof bound');assert(fs.statfsSync(packet).bavail*fs.statfsSync(packet).bsize>=64*M,'64MiB disk review margin');}
function journal(row){const text=JSON.stringify({...stamp(),...row})+'\n';assert(journalBytes+Buffer.byteLength(text)<=M,'1MiB journal bound');fs.appendFileSync(path.join(packet,'JOURNAL.jsonl'),text);journalBytes+=Buffer.byteLength(text);}
function persist(){fs.writeFileSync(path.join(packet,'RESULT.json'),JSON.stringify({...result,...stamp()},null,2)+'\n');}
async function fileHash(p){regularComponents(p);const h=createHash('sha256');for await(const b of fs.createReadStream(p,{highWaterMark:65536})){check();h.update(b);}return h.digest('hex');}
function regularComponents(p){let cur='/';for(const part of p.slice(1).split('/')){assert(part&&part!=='.'&&part!=='..');cur=path.join(cur,part);assert(!fs.lstatSync(cur).isSymbolicLink());}assert(fs.lstatSync(p).isFile());}
async function audit(label){const receipt={label,...stamp(),files:[]};for(const [rel,h] of Object.entries({...freeze.inputs,...Object.fromEntries(Object.entries(freeze.outputs).map(([p,h])=>['dist/'+p,h]))})){const p=path.join(STAGE,rel);assert.equal(await fileHash(p),h);receipt.files.push({path:rel,sha256:h});}fs.writeFileSync(path.join(packet,'AUDIT-'+label+'.json'),JSON.stringify(receipt)+'\n');}
async function raw(){const s=await bound(page.evaluate(k=>localStorage.getItem(k),K),'raw save',2000);assert(s===null||Buffer.byteLength(s)<=262144,'Raw save cap256KiB');return s;}
function saveRef(raw){if(raw===null)return null;const h=sha(raw),leaf='save-'+h+'.json';if(!fs.existsSync(path.join(packet,leaf)))fs.writeFileSync(path.join(packet,leaf),raw,{flag:'wx'});return {path:leaf,bytes:Buffer.byteLength(raw),sha256:h};}
async function snap(label){check();const before=await raw();const ui=await page.evaluate(()=>({title:document.title,bodyText:document.body.innerText.slice(0,6000),nativeClass:document.documentElement.className,cards:[...document.querySelectorAll('.hand-cards .game-card')].map(e=>({id:e.dataset.card,index:e.dataset.index,disabled:e.getAttribute('aria-disabled'),label:e.getAttribute('aria-label')})),actors:[...document.querySelectorAll('.field-actor:not([hidden])')].map(e=>({uid:e.dataset.actor,text:e.innerText,label:e.querySelector('[data-unit]')?.getAttribute('aria-label')})),preview:document.querySelector('#consequence-preview')?.innerText??null}));assert.equal(await raw(),before,'Read-only observation mutated save');journal({kind:'observation',label,raw:saveRef(before),rawSHA256:before===null?null:sha(before),ui});result.observations++;return before===null?null:JSON.parse(before);}
async function settle(){assert(workLeft()>240);await bound(page.waitForTimeout(240),'settle',500);check();}
async function point(locator){assert.equal(await locator.count(),1);assert(await locator.isVisible());assert(await locator.evaluate(e=>!e.disabled&&e.getAttribute('aria-disabled')!=='true'));let b=await locator.boundingBox();assert(b);await page.mouse.move(b.x+b.width/2,b.y+b.height/2);await settle();b=await locator.boundingBox();assert(b);const p={x:b.x+b.width/2,y:b.y+b.height/2};await page.mouse.move(p.x,p.y);assert(await locator.evaluate((e,p)=>{const hit=document.elementFromPoint(p.x,p.y);return hit===e||e.contains(hit);},p),'Pointer owner absent');return p;}
async function click(locator,label){check();const before=await raw(),p=await point(locator);journal({kind:'action-start',label,before:saveRef(before)});await page.mouse.down();assert(workLeft()>60);await bound(page.waitForTimeout(60),'pointer hold',200);assert(await locator.evaluate((e,p)=>{const hit=document.elementFromPoint(p.x,p.y);return hit===e||e.contains(hit);},p),'Release owner changed');await page.mouse.up();await settle();const after=await raw();journal({kind:'action-complete',label,point:p,before:saveRef(before),after:saveRef(after),beforeSHA256:before===null?null:sha(before),afterSHA256:after===null?null:sha(after)});result.actions++;persist();}
async function capture(label){check();assert(shots<4);const file=path.join(packet,String(++shots).padStart(2,'0')+'-'+label+'.jpg');const before=stamp();await bound(page.screenshot({path:file,type:'jpeg',quality:75,fullPage:false}),'original capture',4000);const bytes=fs.statSync(file).size;result.captures.push({path:file,bytes,sha256:await fileHash(file),requested:before,completed:stamp(),phaseCertified:false,personallyViewed:false});assert(result.captures.reduce((n,c)=>n+c.bytes,0)<=2*M,'Four original JPEG aggregate2MiB bound');persist();}
async function cancel(card){const before=await raw(),p=await point(card);journal({kind:'action-start',label:'ordinary drag Escape cancellation',before:saveRef(before),card:await card.getAttribute('data-card'),index:await card.getAttribute('data-index')});try{await page.mouse.down();await page.mouse.move(p.x,p.y-20,{steps:4});await page.keyboard.press('Escape');}finally{await page.mouse.up();}await settle();const after=await raw();journal({kind:'cancel-complete',before:saveRef(before),after:saveRef(after),byteEqual:before===after});assert.equal(after,before,'Cancellation changed complete save');result.actions++;}
let canceled=false,inspectDone=false,commandDone=false;
async function decision(){
 const s=await snap('decision boundary');
 if(!s){journal({kind:'passive',reason:'No canonical save/unclear UI'});result.passiveIntervals++;return;}
 if(s.phase!=='battle'){journal({kind:'passive',reason:'Conservative method does not choose reward/map/camp/shop/event/terminal controls',phase:s.phase});result.passiveIntervals++;return;}
 const hand=page.locator('.hand-cards .game-card[aria-disabled="false"]:visible');
 if(!canceled&&await hand.count()){await cancel(hand.first());canceled=true;await capture('cancelled');return;}
 const inspectors=page.locator('.field-actor:not([hidden]) .field-inspect:visible');
 if(!inspectDone&&await inspectors.count()){await click(inspectors.first(),'ordinary inspect current creature');await snap('actual creature dossier');await page.keyboard.press('Escape');await settle();inspectDone=true;return;}
 const ready=page.locator('.field-actor:not([hidden]) .field-unit.ally.ready:visible');
 if(await ready.count()){
  const before=await raw();await click(ready.first(),'select first visible READY binding');const targets=page.locator('.field-actor:not([hidden]) .field-unit.enemy.valid-target:visible');
  if(!await targets.count()){await page.keyboard.press('Escape');await settle();journal({kind:'passive',reason:'No visible legal target after READY selection',before:saveRef(before),after:saveRef(await raw())});result.passiveIntervals++;return;}
  // Read current live target labels/previews; no forced target, seed or state.
  for(let i=0;i<Math.min(2,await targets.count());i++){const save=await raw();await point(targets.nth(i));await snap('ordinary target hover alternative '+i);assert.equal(await raw(),save);}
  await click(targets.first(),'free Order into first current highlighted enemy');
  const afterRaw=await raw(),beforeState=JSON.parse(before),after=JSON.parse(afterRaw);
  const refs={before:saveRef(before),after:saveRef(afterRaw)};
  if(after.phase==='battle'){
   journal({kind:'command-mechanics',...refs,beforePhase:beforeState.phase,afterPhase:after.phase,energyEqualityChecked:true,energyEqual:after.energy===beforeState.energy});
   assert.equal(after.energy,beforeState.energy,'Free Order consumed energy while remaining in battle');
  }else if(after.phase==='reward'||after.phase==='victory'){
   const fields=state=>({phase:state.phase,energy:state.energy,hp:state.hp,gold:state.gold,turn:state.turn,floor:state.floor,allies:state.allies,enemies:state.enemies});
   const cleanup={kind:'command-terminal-cleanup',...refs,beforeFields:fields(beforeState),afterFields:fields(after),energyEqualityChecked:false,energyCostInference:null,qualification:'Battle completion resets energy/field; not a command-cost assertion'};
   journal(cleanup);result.terminalCleanups??=[];result.terminalCleanups.push({...stamp(),...cleanup});
  }else{
   journal({kind:'command-unexpected-phase',...refs,beforePhase:beforeState.phase,afterPhase:after.phase,energyEqualityChecked:false});
   throw Error('Unexpected post-command phase '+after.phase);
  }
  if(!commandDone){commandDone=true;await capture('first-order');}return;
 }
 const summon=page.locator('.hand-cards .game-card.summon[aria-disabled="false"]:visible');
 if(await summon.count()&&s.allies.length<2){const id=await summon.first().getAttribute('data-card'),index=await summon.first().getAttribute('data-index');await click(summon.first(),'ordinary naturally drawn binding '+id+' occurrence '+index);return;}
 // Explicit limited tactic: use legal commands and up to two bindings, then end.
 const end=page.locator('[data-action="endTurn"]:visible:not([disabled])');
 if(await end.count()===1){await snap('read enemy intents before End turn');await click(end,'ordinary End turn; observe enemy response');await snap('post End turn enemy response');return;}
 journal({kind:'passive',reason:'No supported unambiguous ordinary control'});result.passiveIntervals++;
}
async function close(){
 if(closingPromise)return closingPromise;
 stopping=true;clearTimeout(workTimer);
 closingPromise=(async()=>{const errors=[];try{if(browser)await bound(browser.close(),'browser close',5000,true);result.browser=browser?'CLOSED':'NOT_LAUNCHED';}catch(e){errors.push(String(e));result.browser='CLOSE_UNCONFIRMED';}try{if(server){server.closeAllConnections();await bound(new Promise((r,j)=>server.close(e=>e?j(e):r())),'server close',2000,true);}result.server=server?'CLOSED':'NOT_STARTED';}catch(e){errors.push(String(e));result.server='CLOSE_UNCONFIRMED';}result.closeErrors=errors;result.workerClosureElapsedMs=mono()-outerEntry;result.workerPayloadCutoffSeconds=337;if(errors.length||mono()>=outerDeadline)process.exitCode=2;persist();})();return closingPromise;
}
process.once('SIGTERM',()=>{result.mechanicalFailures.push('Supervisor cancellation');void close().finally(()=>process.exit(2));});
workTimer=setTimeout(()=>{result.mechanicalFailures.push('337s worker cutoff');process.exitCode=2;void close();},workLeft());
try{
 await audit('before');
 for(const pin of deps.files){assert.equal(fs.statSync(pin.path).size,pin.bytes);assert.equal(await fileHash(pin.path),pin.sha256);}
 const {chromium}=await bound(import(deps.modulePath),'external module import',5000); // AFTER Root grants and full static audits
 server=http.createServer((req,res)=>{try{const key=decodeURIComponent(new URL(req.url,'http://localhost').pathname.slice(1))||'index.html';assert(Object.hasOwn(freeze.outputs,key));const body=regular(path.join(STAGE,'dist',key));assert.equal(sha(body),freeze.outputs[key]);res.setHeader('Content-Type',key.endsWith('.html')?'text/html':key.endsWith('.js')?'text/javascript':key.endsWith('.css')?'text/css':key.endsWith('.png')?'image/png':key.endsWith('.wav')?'audio/wav':'application/octet-stream');res.end(body);}catch{res.writeHead(404);res.end();}});
 await bound(new Promise((r,j)=>{server.once('error',j);server.listen(0,'127.0.0.1',r);}), 'loopback server listen',2000);result.server='OPEN';
 launchAt=performance.now();journal({kind:'browser-launch-request',clockDefinition:'Actual300s begins immediately before fresh browser launch request, includes startup/menu/actions/passive intervals'});
 browser=await bound(chromium.launch({executablePath:deps.browserExecutablePath,headless:true,args:['--no-sandbox','--disable-dev-shm-usage'],timeout:Math.max(1,Math.min(12000,workLeft()))}),'browser launch',12000);result.browser='OPEN';
 context=await bound(browser.newContext({viewport:{width:1440,height:900},deviceScaleFactor:1,reducedMotion:'no-preference'}),'fresh context');page=await bound(context.newPage(),'fresh page');page.setDefaultTimeout(4000);
 page.on('pageerror',e=>{result.mechanicalFailures.push(String(e));});
 const url='http://127.0.0.1:'+server.address().port+'/?targetClearGhost=1&coherentNative128=1';
 await page.route('**/*',route=>{const u=new URL(route.request().url());if(u.origin===new URL(url).origin)void route.continue();else void route.abort();});
 await page.goto(url,{waitUntil:'domcontentloaded',timeout:Math.max(1,Math.min(12000,workLeft()))});await settle();assert.equal(await raw(),null,'Fresh browser save was not empty');await snap('fresh menu');await capture('fresh-menu');
 await click(page.locator('#scene-ui [data-ui="new"]'),'open ordinary contract');assert(await page.locator('input[name="difficulty"][value="0"]').isChecked());
 result.generatedSeedField=await page.locator('#seed').inputValue();journal({kind:'entry',defaultDifficulty:'Initiate',generatedSeedField:result.generatedSeedField,seedEdited:false});
 await click(page.locator('#new-game-form [type="submit"]'),'accept ordinary random Initiate contract');assert(workLeft()>600);await bound(page.waitForTimeout(600),'ordinary entry settle',800);await settle();const initial=await snap('actual entry');assert.equal(initial.difficulty,0);result.actualSeed=initial.seed;
 while(performance.now()-launchAt<300000){check();assert.equal(result.mechanicalFailures.length,0,'Page errors');const intervalStart=performance.now();try{await decision();}catch(e){result.mechanicalFailures.push(String(e));throw e;}await snap('interval after decision');persist();const remain=Math.min(10000-(performance.now()-intervalStart),300000-(performance.now()-launchAt));if(remain>0)await new Promise(resolve=>setTimeout(resolve,Math.min(remain,workLeft())));}
 await snap('actual300 elapsed endpoint');await capture('endpoint');result.completed300=true;result.launchElapsedAtEndpointMs=performance.now()-launchAt;await audit('after');
}catch(e){result.mechanicalFailures.push(String(e));process.exitCode=2;}finally{await close();}
