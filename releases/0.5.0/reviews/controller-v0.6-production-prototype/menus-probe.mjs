// Unshipped adapter + borrowed UI host callbacks; all saves are synthetic fixtures.
import {chromium} from '/workspace/Roguelike-deckbuilder/node_modules/playwright/index.mjs';
import {readFileSync,writeFileSync} from 'node:fs';

import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
const scratch='/workspace/scratch/controller-v06-production-input/';
const root='/workspace/Roguelike-deckbuilder/';
const fixtures=JSON.parse(readFileSync(scratch+'probe-fixtures.json','utf8'));
const menus=JSON.parse(readFileSync(scratch+'menu-fixtures.json','utf8'));
const source=readFileSync(scratch+'emitted/adapter.js','utf8');
const expected='d6221bf764bad593b04981e87bead7ba6868b72cf361d70671af5c91aac39416';
const hash=path=>createHash('sha256').update(readFileSync(root+path)).digest('hex');
const runtimeFiles=['src/main.ts','src/style.css','index.html','src/engine.ts','src/arena.ts'];
const before=Object.fromEntries(runtimeFiles.map(path=>[path,hash(path)]));
const browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox','--disable-dev-shm-usage']});
const report={syntheticBrowserQA:true,adapterShipped:false,hostContextBorrowed:true,physicalController:false,checks:[],errors:[],beforeRuntimeHashes:before};
async function load(fixture=fixtures.full){const page=await browser.newPage({viewport:{width:1280,height:720}});page.on('pageerror',e=>report.errors.push(e.message));await page.addInitScript(s=>{localStorage.setItem('hollowpact.run.v2',JSON.stringify(s));localStorage.setItem('hollowpact.settings.v2',JSON.stringify({motion:false,mute:true,volume:0}));localStorage.setItem('hollowpact.tutorial.v2','true');},fixture);await page.goto('http://127.0.0.1:4173');const build=await page.evaluate(async()=>await(await fetch('./build-provenance.json')).json());assert.equal(build.sourceDigest,expected);report.build={version:build.version,digest:build.sourceDigest};await page.locator('[data-ui="resume"]').click();await page.evaluate(async source=>{
const url=URL.createObjectURL(new Blob([source],{type:'text/javascript'}));const module=await import(url);URL.revokeObjectURL(url);
window.__pad={index:0,connected:true,mapping:'standard',axes:[0,0,0,0],buttons:Array.from({length:17},()=>({pressed:false,value:0}))};Object.defineProperty(navigator,'getGamepads',{configurable:true,value:()=>{if(window.__padThrows)throw new DOMException('Synthetic API refusal','SecurityError');return [window.__pad];}});
window.__hostLock=false;window.__hostThrows=false;window.__activations=0;window.__modes=[];
const host={getContext(){if(window.__hostThrows)throw Error('Synthetic host refusal');return {phase:document.querySelector('#app').classList.contains('on-title')?'title':JSON.parse(localStorage.getItem('hollowpact.run.v2')).phase,settling:window.__hostLock,dialog:document.querySelector('#dialog').open?document.querySelector('#dialog'):null,targeting:!!document.querySelector('.battle-guidance.targeting')};},activate(element){window.__activations++;element.click();},back(){const close=document.querySelector('#dialog[open] [data-ui="close"]');const cancel=document.querySelector('[data-ui="cancel"]');if(close)close.click();else if(cancel)cancel.click();else document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true}));},inspect(element){if(element.dataset.unit)document.querySelector(`[data-ui="inspect-unit"][data-uid="${CSS.escape(element.dataset.unit)}"]`)?.click();else if(element.dataset.card){document.querySelector('[data-ui="deck"]').click();document.querySelector(`#dialog [data-ui="inspect"][data-card="${CSS.escape(element.dataset.card)}"]`)?.click();}},endTurn(){document.querySelector('[data-action="endTurn"]:not(:disabled)')?.click();},pause(){document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true}));},onInputMode(mode){window.__modes.push(mode);}};
window.__input=module.createInputAdapter(host,{autoPoll:false});window.__input.pollOnce(0);
},source);return page;}
async function step(page,now,{button,pressed,axes}={}){await page.evaluate(({now,button,pressed,axes})=>{if(button!==undefined)window.__pad.buttons[button]={pressed:!!pressed,value:pressed?1:0};if(axes)window.__pad.axes=axes;window.__input.pollOnce(now);},{now,button,pressed,axes});}
async function snap(page){return page.evaluate(()=>({save:localStorage.getItem('hollowpact.run.v2'),unit:document.activeElement.dataset.unit||null,card:document.activeElement.dataset.focus||null,tag:document.activeElement.tagName,selected:document.querySelectorAll('.unit.selected').length,dialog:document.querySelector('#dialog').open,activations:window.__activations}));}
try{
 report.unexercisedTerminalPhases={phases:['victory','defeat'],reason:'Current title intentionally hides Resume for terminal saved phases; the first harness attempt timed out at victory. Main integration tests must reach an outcome normally.'};
 for(const [phase,fixture] of Object.entries(menus.states).filter(([phase])=>!['victory','defeat'].includes(phase))){
  const page=await load(fixture);const initial=await snap(page);
  const first=page.locator('#scene-ui button:not(:disabled)').first();await first.focus();
  const firstUi=await page.evaluate(()=>({ui:document.activeElement.dataset.ui,action:document.activeElement.dataset.action}));
  await step(page,20,{button:5,pressed:true});assert.equal(await page.evaluate(()=>document.activeElement.closest('#topbar,#hud,#footer')!==null),true);
  await step(page,40,{button:5,pressed:false});await step(page,60,{button:5,pressed:true});assert.equal(await page.evaluate(()=>document.activeElement.closest('#scene-ui')!==null),true);
  const restored=await page.evaluate(()=>({ui:document.activeElement.dataset.ui,action:document.activeElement.dataset.action}));assert.deepEqual(restored,firstUi);
  await step(page,80,{button:5,pressed:false});await step(page,100,{button:15,pressed:true});assert.equal(await page.evaluate(()=>document.activeElement.closest('#scene-ui')!==null),true);
  await step(page,120,{button:15,pressed:false});assert.equal((await snap(page)).save,initial.save);
  report.checks.push({name:phase+'-menu-regions-and-direction',canonicalUnchanged:true,regionFocusRestored:true});
  if(menus.actions[phase]){
   const selectors={camp:'[data-action="camp"][data-choice="rest"]',shop:'[data-action="buy"]:not(:disabled)',event:'[data-action="event"][data-choice="forage"]',reward:'[data-action="reward"][data-card=""]'};
   await page.locator(selectors[phase]).first().focus();await step(page,140,{button:0,pressed:true});const committed=await snap(page);assert.deepEqual(JSON.parse(committed.save),menus.expected[phase]);await step(page,1000);assert.equal((await snap(page)).save,committed.save);
   report.checks.push({name:phase+'-activation-exact-reducer',heldDoesNotRepeat:true,canonicalEqualsReducer:true});
  }
  await page.close();
 }
 report.afterRuntimeHashes=Object.fromEntries(runtimeFiles.map(path=>[path,hash(path)]));assert.deepEqual(report.afterRuntimeHashes,before);report.runtimeUnchanged=true;assert.deepEqual(report.errors,[]);report.passed=report.checks.length;writeFileSync(scratch+`menu-evidence-${Date.now()}.json`,JSON.stringify(report,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify(report,null,2));
}finally{await browser.close();}
