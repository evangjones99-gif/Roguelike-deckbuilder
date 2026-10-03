import {chromium} from '/workspace/Roguelike-deckbuilder/node_modules/playwright/index.mjs';
import {readFileSync,writeFileSync} from 'node:fs';
import {performance} from 'node:perf_hooks';
import {gunzipSync} from 'node:zlib';
const root='/workspace/Roguelike-deckbuilder';
if(process.argv[2]!=='--go') throw Error('Only run after root freeze GO');
const endpoint=process.argv[3]||'http://127.0.0.1:4173';
const runs=JSON.parse(gunzipSync(readFileSync(root+'/reviews/gameplay-v0.4-browser-inputs.json.gz')).toString());
const browser=await chromium.launch({headless:true,executablePath:'/usr/bin/chromium',args:['--no-sandbox']});
const results=[];
async function click(page,a) {
 if(a.type==='play'){await page.locator(`[data-ui="play-card"][data-index="${a.index}"]`).click();if(a.target)await page.locator(`[data-unit="${a.target}"]`).click();}
 else if(a.type==='attack'){await page.locator(`[data-unit="${a.unit}"]`).click();await page.locator(`[data-unit="${a.target}"]`).click();}
 else if(a.type==='camp'&&a.choice==='train'){await page.locator('[data-ui="train"]').click();await page.locator(`[data-action="camp"][data-choice="train"][data-index="${a.index}"]`).click();}
 else if(['travel','camp','event'].includes(a.type))await page.locator(`[data-action="${a.type}"][data-choice="${a.choice}"]`).click();
 else if(a.type==='reward')await page.locator(`[data-action="reward"][data-card="${a.card??''}"]`).click();
 else if(a.type==='buy')await page.locator(`[data-action="buy"][data-card="${a.card}"]`).click();
 else if(a.type==='remove'){await page.locator('[data-ui="remove"]').click();await page.locator(`[data-action="remove"][data-index="${a.index}"]`).click();}
 else if(a.type==='leave')await page.locator('[data-action="leave"]').click();
 else if(a.type==='endTurn'){await page.locator('[data-action="endTurn"]').click();const c=page.locator('[data-ui="confirm-end"]');if(await c.isVisible())await c.click();}
 else throw Error('Unrecognized action '+a.type);
}
try {
 for(const run of runs) {
  const context=await browser.newContext({viewport:{width:1440,height:900},reducedMotion:'no-preference',acceptDownloads:true});
  const page=await context.newPage(),errors=[],requests=[];page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>requests.push({url:r.url(),method:r.method()}));
  await page.addInitScript(()=>{localStorage.setItem('hollowpact.settings.v2',JSON.stringify({mute:true,volume:0,motion:true}));localStorage.setItem('hollowpact.tutorial.v2','yes');});
  await page.goto(endpoint);await page.locator('[data-ui="new"]').click();await page.locator('#seed').fill(String(run.seed));await page.locator(`input[name="difficulty"][value="${run.difficulty}"]`).check();await page.locator('button[type="submit"]').click();
  const actionTimes=[],settling=[];let accepted=0;const started=performance.now();
  for(const t of run.trace) {
   await page.waitForFunction(()=>!document.querySelector('#app')?.classList.contains('settling-combat'));
   const saved=await page.evaluate(()=>JSON.parse(localStorage.getItem('hollowpact.run.v2')));
   for(const k of ['phase','floor','turn','hp','energy','hand','allies','enemies'])if(JSON.stringify(saved[k])!==JSON.stringify(t[k]))throw Error(`Mismatch seed${run.seed} step${accepted} ${k}`);
   const start=performance.now();await click(page,t.action);actionTimes.push(performance.now()-start);accepted++;
   const after=await page.evaluate(()=>({saved:JSON.parse(localStorage.getItem('hollowpact.run.v2')),settling:document.querySelector('#app').classList.contains('settling-combat'),busy:document.querySelector('#scene-ui').getAttribute('aria-busy'),guidance:document.querySelector('.battle-guidance>span')?.textContent}));
   if(after.settling) {
    const at=performance.now();const terminal=['victory','defeat'].includes(after.saved.phase);
    const held={step:accepted,phase:after.saved.phase,hp:after.saved.hp,busy:after.busy,guidance:after.guidance};
    if(terminal) {
     held.beforeLateKey=await page.evaluate(()=>localStorage.getItem('hollowpact.run.v2'));
     await page.keyboard.press('e');held.lateKeyUnchanged=held.beforeLateKey===await page.evaluate(()=>localStorage.getItem('hollowpact.run.v2'));delete held.beforeLateKey;
     await page.screenshot({path:`${root}/reviews/gameplay-v0.4-${after.saved.phase}-impact.png`});
    }
    await page.waitForFunction(()=>!document.querySelector('#app').classList.contains('settling-combat'));held.observedHoldMs=performance.now()-at;settling.push(held);
    if(terminal) await page.screenshot({path:`${root}/reviews/gameplay-v0.4-${after.saved.phase}-recap.png`});
   }
  }
  const final=await page.evaluate(()=>JSON.parse(localStorage.getItem('hollowpact.run.v2')));
  if(final.phase!==run.phase||final.hp!==run.hp)throw Error('Outcome changed');
  let campaignReload=null;if(run.knownCampaign){await click(page,{type:'endTurn'});const beforeReload=await page.evaluate(()=>localStorage.getItem('hollowpact.run.v2'));if(JSON.stringify(JSON.parse(beforeReload))!==JSON.stringify(run.continued))throw Error('Campaign continuation mismatch');await page.reload();await page.locator('[data-ui=resume]').click();if(beforeReload!==await page.evaluate(()=>localStorage.getItem('hollowpact.run.v2')))throw Error('Valid repaired save reload changed');campaignReload={continuedTurn:run.continued.turn,armor:run.continued.enemies[0].block,unchangedAcrossReload:true};}const reportTests=[];
  for(const negative of [false,true]) {
   await page.locator('[data-ui="feedback"]').click();const copy=await page.locator('#dialog .dialog-copy').innerText();const questions=await page.locator('#feedback-form label').allTextContents();
   if(negative){await page.locator('#feedback-confusion').fill('AUTOMATED AGENT QA SAMPLE, NOT HUMAN PLAYTEST DATA: testing a negative response and local-only export.');await page.locator('#feedback-choice').fill('AUTOMATED QA: none of the choices felt meaningful in this synthetic response.');await page.locator('#feedback-replay').selectOption('no');}
   const storage=await page.evaluate(()=>JSON.stringify(Object.entries(localStorage)));const requestIndex=requests.length;
   const download=page.waitForEvent('download');await page.locator('#feedback-form button[type="submit"]').click();const file=await download;
   const feedback=JSON.parse(readFileSync(await file.path(),'utf8'));
   const unchanged=storage===await page.evaluate(()=>JSON.stringify(Object.entries(localStorage)));
   const newRequests=requests.slice(requestIndex).filter(r=>r.url.startsWith('http'));
   if(!unchanged||newRequests.length)throw Error('Feedback changed storage or made network request');
   if(feedback.responses.replayIntent!==(negative?'no':'unanswered'))throw Error('Replay response changed');
   reportTests.push({qaOnly:true,negative,disclosure:copy,questions,filename:file.suggestedFilename(),storageUnchanged:unchanged,newHttpRequests:newRequests,feedback});
   await page.getByRole('button',{name:'Close dialog',exact:true}).click();
  }
  let retry=null;if(!run.knownCampaign){await page.locator('[data-ui="retry"]').click();retry=await page.evaluate(()=>JSON.parse(localStorage.getItem('hollowpact.run.v2')));if(retry.phase!=='map'||retry.floor!==0||retry.hp!==65||retry.seed!==run.seed)throw Error('Replay failed to recover');}
  const result={seed:run.seed,difficulty:run.difficulty,policy:run.policy,motion:true,audioMuted:true,acceptedActions:accepted,phase:final.phase,hp:final.hp,browserElapsedMs:performance.now()-started,errors,settling,reportTests,campaignReload,retry:retry?{phase:retry.phase,floor:retry.floor,hp:retry.hp,seed:retry.seed}:null,actionClickTimingMs:{mean:actionTimes.reduce((a,b)=>a+b,0)/actionTimes.length,max:Math.max(...actionTimes)},method:'Complete actual rendered-control replay of preserved independent legal actions; every pre-action browser state matches reference. Timing is automation latency, not human pace.'};
  results.push(result);const p=root+'/reviews/gameplay-v0.4-evidence.json';const evidence=JSON.parse(readFileSync(p,'utf8'));evidence.motionRuns=results;evidence.servedBuild=await(await page.request.get(endpoint+'/build-provenance.json')).json();writeFileSync(p,JSON.stringify(evidence,null,2));console.log(JSON.stringify({seed:run.seed,phase:final.phase,hp:final.hp,acceptedActions:accepted,errors,settling:result.settling,feedback:reportTests.map(t=>({negative:t.negative,storageUnchanged:t.storageUnchanged,newHttpRequests:t.newHttpRequests})),retry:result.retry}));await context.close();
 }
} finally {await browser.close();}
