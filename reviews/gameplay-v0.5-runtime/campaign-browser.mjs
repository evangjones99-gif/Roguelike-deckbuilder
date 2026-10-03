import assert from 'node:assert/strict';
import {chromium} from '/workspace/Roguelike-deckbuilder/node_modules/playwright/index.mjs';
import {readFileSync,writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {gunzipSync} from 'node:zlib';
import {performance} from 'node:perf_hooks';
if(process.argv[2]!=='--go')throw Error('Requires parent final production freeze GO');
const root='/workspace/Roguelike-deckbuilder',out=root+'/reviews/gameplay-v0.5-runtime',endpoint='http://127.0.0.1:4173',digest='9f80af0d0053b992c7f0f39d6de106a8f318619ea92e94c00354933e07ebcf04';
const input=JSON.parse(gunzipSync(readFileSync(out+'/campaign-inputs.json.gz')).toString());
const hash=v=>createHash('sha256').update(v).digest('hex');
const browser=await chromium.launch({headless:true,executablePath:'/usr/bin/chromium',args:['--no-sandbox']});
const legacyOnly=process.argv.includes('--legacy');const results=[];
async function click(page,a){
 if(a.type==='play'){await page.locator(`[data-ui="play-card"][data-index="${a.index}"]`).click();if(a.target)await page.locator(`[data-unit="${a.target}"]`).click();}
 else if(a.type==='attack'){await page.locator(`[data-unit="${a.unit}"]`).click();await page.locator(`[data-unit="${a.target}"]`).click();}
 else if(a.type==='camp'&&a.choice==='train'){await page.locator('[data-ui="train"]').click();await page.locator(`[data-action="camp"][data-choice="train"][data-index="${a.index}"]`).click();}
 else if(['travel','camp','event'].includes(a.type))await page.locator(`[data-action="${a.type}"][data-choice="${a.choice}"]`).click();
 else if(a.type==='reward')await page.locator(`[data-action="reward"][data-card="${a.card??''}"]`).click();
 else if(a.type==='buy')await page.locator(`[data-action="buy"][data-card="${a.card}"]`).click();
 else if(a.type==='remove'){await page.locator('[data-ui="remove"]').click();await page.locator(`[data-action="remove"][data-index="${a.index}"]`).click();}
 else if(a.type==='leave')await page.locator('[data-action="leave"]').click();
 else if(a.type==='endTurn'){await page.locator('[data-action="endTurn"]').click();const confirm=page.locator('[data-ui="confirm-end"]');if(await confirm.isVisible())await confirm.click();}
 else throw Error('Unhandled '+a.type);
}
const canonical=async page=>JSON.stringify(JSON.parse(await page.evaluate(()=>localStorage.getItem('hollowpact.run.v2'))));
try{for(const run of input.runs.filter(r=>!legacyOnly||r.engineKind===1)){
 const context=await browser.newContext({viewport:{width:1440,height:900},reducedMotion:'no-preference',acceptDownloads:true});
 await context.addInitScript(({start,fresh})=>{localStorage.setItem('hollowpact.settings.v2',JSON.stringify({mute:true,volume:0,motion:true}));localStorage.setItem('hollowpact.tutorial.v2','yes');if(!fresh&&localStorage.getItem('hollowpact.run.v2')===null)localStorage.setItem('hollowpact.run.v2',' \n'+JSON.stringify(start)+'\n');},{start:run.start,fresh:run.fresh});
 const page=await context.newPage(),errors=[],requests=[];page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>requests.push(r.url()));
 await page.goto(endpoint);const build=await(await page.request.get(endpoint+'/build-provenance.json')).json();assert.equal(build.sourceDigest,digest);
 let exactResumeRaw=null;
 if(run.fresh){await page.locator('[data-ui="new"]').click();await page.locator('#seed').fill(String(run.seed));await page.locator('input[name="difficulty"][value="2"]').check();await page.locator('button[type="submit"]').click();}
 else {const before=await page.evaluate(()=>localStorage.getItem('hollowpact.run.v2'));await page.locator('[data-ui="resume"]').click();exactResumeRaw=before===await page.evaluate(()=>localStorage.getItem('hollowpact.run.v2'));assert.ok(exactResumeRaw);}
 const settling=[],actionCounts={},screens=[],start=performance.now();let reload=null,accepted=0;
 for(const t of run.trace){
  await page.waitForFunction(()=>!document.querySelector('#app')?.classList.contains('settling-combat'));
  assert.equal(hash(await canonical(page)),t.beforeHash,`Pre-action mismatch ${run.seed}/${accepted}`);
  await click(page,t.action);accepted++;actionCounts[t.action.type]=(actionCounts[t.action.type]??0)+1;
  const raw=await canonical(page);assert.equal(hash(raw),t.afterHash,`Commit mismatch ${run.seed}/${accepted}`);
  const s=JSON.parse(raw);assert.equal(s.schema,run.engineKind===1?2:3);assert.equal(Object.hasOwn(s,'engineKind'),run.engineKind===2);
  const hold=await page.evaluate(()=>({active:document.querySelector('#app').classList.contains('settling-combat'),busy:document.querySelector('#scene-ui').getAttribute('aria-busy'),guidance:document.querySelector('#consequence-preview')?.textContent}));
  if(hold.active){const began=performance.now(),terminal=['victory','defeat'].includes(s.phase);const record={action:accepted,phase:s.phase,hp:s.hp,busy:hold.busy,guidance:hold.guidance,canonicalCommittedImmediately:true};
   if(terminal){await page.keyboard.press('e');await page.keyboard.press('1');assert.equal(await canonical(page),raw);record.staleKeysUnchanged=true;await page.screenshot({path:out+`/campaign-${run.seed}-${s.phase}-impact.png`});}
   await page.waitForFunction(()=>!document.querySelector('#app').classList.contains('settling-combat'));record.observedWaitMs=performance.now()-began;settling.push(record);
   if(terminal){await page.screenshot({path:out+`/campaign-${run.seed}-${s.phase}-recap.png`});screens.push({kind:'terminal',action:accepted});}
  }
  if(!reload&&accepted>=12&&s.phase==='battle'){
   const before=await canonical(page);await page.reload();await page.locator('[data-ui="resume"]').click();assert.equal(await canonical(page),before);reload={action:accepted,phase:s.phase,turn:s.turn,exact:true,generation:run.engineKind};
  }
  if(accepted===25||t.action.type==='remove'||t.action.type==='camp'){
   if(s.phase==='battle'||s.phase==='map'){await page.screenshot({path:out+`/campaign-${run.seed}-action-${accepted}.png`});screens.push({kind:t.action.type,action:accepted});}
  }
  if(accepted%40===0)console.log(JSON.stringify({seed:run.seed,accepted,phase:s.phase,hp:s.hp}));
 }
 const final=JSON.parse(await canonical(page));assert.equal(final.phase,run.phase);assert.equal(final.hp,run.hp);
 await page.locator('[data-ui="feedback"]').click();const questions=await page.locator('#feedback-form label').allTextContents();
 await page.locator('#feedback-confusion').fill('AUTOMATED AGENT QA, NOT HUMAN PLAYTEST DATA: checking a negative local response and exact build/generation context.');
 await page.locator('#feedback-choice').fill('AUTOMATED QA: no meaningful choice claimed by this synthetic response.');await page.locator('#feedback-replay').selectOption('no');
 const storage=await page.evaluate(()=>JSON.stringify(Object.entries(localStorage))),requestIndex=requests.length,download=page.waitForEvent('download');await page.locator('#feedback-form button[type="submit"]').click();const file=await download,feedback=JSON.parse(readFileSync(await file.path(),'utf8'));
 assert.equal(feedback.context.build.sourceDigest,digest);assert.equal(feedback.context.run.saveSchema,run.engineKind===1?2:3);assert.equal(feedback.context.run.rulesGeneration,run.engineKind);assert.equal(feedback.responses.replayIntent,'no');assert.equal(storage,await page.evaluate(()=>JSON.stringify(Object.entries(localStorage))));assert.equal(requests.slice(requestIndex).filter(r=>r.startsWith('http')).length,0);
 await page.getByRole('button',{name:'Close dialog',exact:true}).click();await page.locator('[data-ui="retry"]').click();const retry=JSON.parse(await canonical(page));assert.equal(retry.seed,run.seed);assert.equal(retry.hp,65);assert.equal(retry.phase,'map');assert.equal(retry.floor,0);assert.equal(retry.engineKind,2);
 assert.deepEqual(errors,[]);const result={seed:run.seed,difficulty:2,policy:run.policy,engineKind:run.engineKind,fresh:run.fresh,earnedPrefixActions:run.earnedPrefixActions??0,acceptedActions:accepted,phase:final.phase,hp:final.hp,elapsedMs:performance.now()-start,motion:true,muted:true,actualControls:true,canonicalHashCheckedBeforeAndAfterEveryAction:true,exactResumeRaw,reload,actionCounts,settling,screens,questions,feedback:{qaOnly:true,data:feedback,storageUnchanged:true,newHttpRequests:0},retry:{generation:2,seed:retry.seed,hp:65,phase:'map'},build:build.sourceDigest,errors};results.push(result);writeFileSync(out+(legacyOnly?'/legacy-campaign-results.json':'/campaign-results.json'),JSON.stringify({method:'Actual production DOM controls, motionON, reference legal replay; automation elapsed time is not human pacing or FPS. Legacy prefix is earned simulation, not a human save.',inputSHA256:hash(readFileSync(out+'/campaign-inputs.json.gz')),results},null,2)+'\n');console.log(JSON.stringify({seed:run.seed,phase:final.phase,hp:final.hp,accepted,generation:run.engineKind,errors}));await context.close();
}}finally{await browser.close();}
