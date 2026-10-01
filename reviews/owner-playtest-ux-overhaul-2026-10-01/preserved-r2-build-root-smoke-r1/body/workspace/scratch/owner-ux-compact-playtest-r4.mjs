import fs from 'node:fs';
import { chromium } from '/workspace/Roguelike-deckbuilder/node_modules/playwright-core/index.mjs';
import { applyActionWithEvents,legalActions,createGame } from '/dev/shm/hollowpact-owner-ux-overhaul-root-r2/src/engine.ts';
const out=`/tmp/hollowpact-owner-ux-compact-playtest-r4-${Date.now()}`;fs.mkdirSync(out,{recursive:false});
const max=Number(fs.readFileSync('/sys/fs/cgroup/memory.max','utf8')),current=Number(fs.readFileSync('/sys/fs/cgroup/memory.current','utf8'));
if(max-current<1152*1024**2)throw Error('640MiB work +512MiB reserve refused');
const report={build:JSON.parse(fs.readFileSync('/dev/shm/hollowpact-owner-ux-overhaul-root-r2/dist/build-provenance.json','utf8')).sourceDigest,contexts:[],errors:[],kind:'ROOT agent playtest, not human enjoyment',browserBackend:'default Chromium 2D; unnecessary forced SwiftShader flags removed after resource stop; guards unchanged',harnessRevision:'Compact R3 adapts preserved root R3 to frozen5d2c; native wheel reveals offscreen body controls, fresh hit ownership remains mandatory. Tutorial preference setup is diagnostic, not earned independent play.'};
async function fieldPoint(page,uid,click=true){
 await page.waitForFunction(id=>{const e=[...document.querySelectorAll('[data-unit]')].find(v=>v.dataset.unit===id);return e&&!e.disabled;},uid);
 let box=await page.locator(`[data-unit="${uid}"]`).boundingBox();if(!box)throw Error('No field bounds');
 for(let attempt=0;attempt<3&&(box.y<0||box.y+box.height>page.viewportSize().height);attempt++){await page.mouse.move(12,200);await page.mouse.wheel(0,box.y+box.height/2-page.viewportSize().height/2);await page.waitForTimeout(150);box=await page.locator(`[data-unit="${uid}"]`).boundingBox();}
 const x=box.x+box.width/2,y=box.y+box.height/2;
 const hit=await page.evaluate(({x,y})=>document.elementFromPoint(x,y)?.closest('[data-unit]')?.dataset.unit,{x,y});if(hit!==uid)throw Error(`Wrong field hit owner ${hit}, expected ${uid}`);
 await page.mouse.move(x,y);if(click)await page.mouse.click(x,y);
}
const browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox']});let currentPage;process.once('SIGTERM',()=>{report.interrupted=true;void browser.close().finally(()=>{fs.writeFileSync(`${out}/INTERRUPTED.json`,JSON.stringify(report,null,2));process.exit(143);});});
try{
 for(const width of [390]){
  const c=await browser.newContext({viewport:{width,height:900}});const page=await c.newPage();currentPage=page;page.setDefaultTimeout(12000);page.on('pageerror',e=>report.errors.push(String(e)));
  await page.addInitScript(()=>localStorage.setItem('hollowpact.tutorial.v2','yes'));
  await page.goto('http://127.0.0.1:4779');await page.screenshot({path:`${out}/${width}-title.jpg`,fullPage:true});
  const entry={width,actions:[],captures:[`${out}/${width}-title.jpg`,`${out}/${width}-contract.jpg`,`${out}/${width}-field.jpg`]};report.contexts.push(entry);
  if(await page.locator('#topbar').isVisible()||await page.locator('#footer').isVisible())throw Error('Duplicate title tools visible');
  await page.locator('#scene-ui [data-ui="new"]').click();entry.initialContract=await page.locator('#new-game-form').innerText();await page.screenshot({path:entry.captures[1],fullPage:true});
  if(await page.locator('#seed').isVisible())throw Error('Optional seed unexpectedly exposed on initial screen');
  await page.locator('[data-hunt-disclosure="hunt-seed-panel"]').click();if(!await page.locator('#seed').evaluate(e=>e===document.activeElement))throw Error('Seed disclosure did not focus seed');await page.locator('#seed').fill('44');await page.locator('#new-game-form [type="submit"]').click();await page.waitForTimeout(850);
  const metrics=()=>page.evaluate(()=>({scene:document.querySelector('#scene').getBoundingClientRect().toJSON(),canvas:{width:document.querySelector('#arena').width,height:document.querySelector('#arena').height,box:document.querySelector('#arena').getBoundingClientRect().toJSON()},labels:[...document.querySelectorAll('.field-actor')].map(e=>({text:e.innerText,box:e.getBoundingClientRect().toJSON()})),heap:performance.memory?.usedJSHeapSize,docWidth:document.documentElement.scrollWidth}));entry.timeline=[];entry.timeline.push(await metrics());
  const save=()=>page.evaluate(()=>JSON.parse(localStorage.getItem('hollowpact.run.v2')));
  const initial=createGame(44,0);const first=applyActionWithEvents(initial,{type:'travel',choice:initial.route[0]}).state;
  if(JSON.stringify(await save())!==JSON.stringify(first))throw Error('Streamlined start differs from actual first travel reducer');entry.forcedFirstTravelSkipped=true;
  for(let i=0;i<2;i++){
   const before=await save(),summon=page.locator('.hand-cards .summon:not(.unplayable)').first();if(!await summon.count())break;
   const index=Number(await summon.getAttribute('data-index'));const expected=applyActionWithEvents(before,{type:'play',index}).state;
   await summon.click();entry.timeline.push(await metrics());await page.waitForTimeout(900);entry.timeline.push(await metrics());if(JSON.stringify(expected)!==JSON.stringify(await save()))throw Error('Summon save differs from pure reducer');entry.actions.push({type:'summon',index,exactReducerSave:true});
  }
  const before=await save(),attack=legalActions(before).find(a=>a.type==='attack');
  if(attack){
   await fieldPoint(page,attack.unit);await fieldPoint(page,attack.target,false);entry.preview=await page.locator('#consequence-preview').innerText();
   const targetFill=await page.locator(`[data-unit="${attack.target}"]`).evaluate(e=>getComputedStyle(e).backgroundColor);if(targetFill!=='rgba(0, 0, 0, 0)')throw Error(`Opaque creature target fill ${targetFill}`);entry.targetFill=targetFill;
   await page.screenshot({path:entry.captures[2],fullPage:true});await fieldPoint(page,attack.target);await page.waitForTimeout(1000);
   const after=await save();if(JSON.stringify(after)!==JSON.stringify(applyActionWithEvents(before,attack).state))throw Error('Direct command save differs from pure reducer');entry.actions.push({type:'direct-command',exactReducerSave:true});
   await page.reload();await page.locator('#scene-ui [data-ui="resume"]').click();await page.waitForTimeout(650);if(JSON.stringify(await save())!==JSON.stringify(after))throw Error('Reload modified saved result');entry.reloadExact=true;
  }
  entry.dom=await page.evaluate(()=>({fieldButtons:document.querySelectorAll('#field-controls [data-unit]').length,sidePanelDuplicates:document.querySelectorAll('#scene-ui .roster').length,documentWidth:document.documentElement.scrollWidth,viewport:innerWidth,cardTextColor:getComputedStyle(document.querySelector('.hand-cards .card-description')).color,controlBounds:[...document.querySelectorAll('#field-controls [data-unit]')].map(e=>({uid:e.dataset.unit,rect:e.getBoundingClientRect().toJSON(),disabled:e.disabled}))}));
  if(entry.dom.documentWidth!==width)throw Error('Horizontal document overflow');
  const rawBefore=await page.evaluate(()=>localStorage.getItem('hollowpact.run.v2'));
  await page.locator('[data-ui="home"]').click();await page.locator('[data-ui="menu"]').click();await page.locator('#scene-ui [data-ui="new"]').click();
  if(!await page.locator('[name="replaceSaved"]').count())throw Error('Saved replacement consent absent');
  // Labelled DOM-malformation diagnostic: validator must preserve the exact original save.
  await page.locator('#new-game-form').evaluate(form=>{const duplicate=document.createElement('input');duplicate.name='difficulty';duplicate.value='2';duplicate.dataset.diagnostic='duplicate';form.append(duplicate);form.dispatchEvent(new Event('submit',{bubbles:true,cancelable:true}));});
  if(await page.evaluate(()=>localStorage.getItem('hollowpact.run.v2'))!==rawBefore)throw Error('Malformed form changed save');entry.duplicateFieldRefused=true;
  await page.locator('[data-diagnostic="duplicate"]').evaluate(e=>e.remove());await page.locator('#new-game-form [data-ui="close"]').click();if(await page.evaluate(()=>localStorage.getItem('hollowpact.run.v2'))!==rawBefore)throw Error('Cancel changed save');entry.cancelExact=true;
  await c.close();console.log(JSON.stringify({completedWidth:width}));
 }
}catch(e){report.failure=String(e);if(currentPage&&!currentPage.isClosed()){await currentPage.screenshot({path:`${out}/failure.jpg`,fullPage:true}).catch(()=>{});report.failureDOM=await currentPage.locator('body').innerText().catch(()=>null);}throw e;}
finally{await browser.close();fs.writeFileSync(`${out}/RESULT.json`,JSON.stringify(report,null,2));}
if(report.errors.length)throw Error('Page errors recorded');console.log(JSON.stringify(report));
