import assert from 'node:assert/strict';
import {chromium} from '/workspace/Roguelike-deckbuilder/node_modules/playwright/index.mjs';
import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
const base='/workspace/scratch/gameplay-v06-input',endpoint='http://127.0.0.1:5193',digest=process.argv[2],run=process.argv[3];
assert.match(digest,/^[a-f0-9]{64}$/);assert.match(run,/^[a-z0-9-]+$/);const output=base+'/'+run+'.json';assert.ok(!existsSync(output));
const refs=JSON.parse(gunzipSync(readFileSync(base+'/references.json.gz')));const hash=v=>createHash('sha256').update(v).digest('hex');
const browser=await chromium.launch({headless:true,executablePath:'/usr/bin/chromium',args:['--no-sandbox']});const results=[];
const save=p=>p.evaluate(()=>JSON.stringify(JSON.parse(localStorage.getItem('hollowpact.run.v2'))));
const focus=p=>p.evaluate(()=>({tag:document.activeElement.tagName,unit:document.activeElement.dataset.unit,ui:document.activeElement.dataset.ui,action:document.activeElement.dataset.action,index:document.activeElement.dataset.index,id:document.activeElement.id,text:document.activeElement.textContent.slice(0,80)}));
const pause=(p,ms=85)=>p.waitForTimeout(ms);
async function pad(p,idx,hold=100){await p.evaluate(i=>window.__qaPad.buttons[i]={pressed:true,touched:true,value:1},idx);await pause(p,hold);}
async function release(p,idx){await p.evaluate(i=>window.__qaPad.buttons[i]={pressed:false,touched:false,value:0},idx);await pause(p);}
async function press(p,idx){await pad(p,idx);await release(p,idx);}
async function context(state,{motion=false,api='pad'}={}){const c=await browser.newContext({viewport:{width:1440,height:900},reducedMotion:motion?'no-preference':'reduce'});await c.addInitScript(({state,motion,api})=>{
 if(!localStorage.getItem('hollowpact.run.v2'))localStorage.setItem('hollowpact.run.v2',JSON.stringify(state));if(!localStorage.getItem('hollowpact.settings.v2'))localStorage.setItem('hollowpact.settings.v2',JSON.stringify({mute:true,volume:0.5,motion}));localStorage.setItem('hollowpact.tutorial.v2','yes');
 window.__qaReads=0;window.__qaPad={connected:true,index:0,mapping:'standard',axes:[0,0,0,0],buttons:Array.from({length:17},()=>({pressed:false,touched:false,value:0}))};
 Object.defineProperty(window.__qaPad,'id',{get(){throw Error('Reviewer: device ID must not be accessed');}});
 Object.defineProperty(navigator,'getGamepads',{configurable:true,value:api==='absent'?undefined:()=>{window.__qaReads++;if(api==='refused')throw new DOMException('Reviewer denied','SecurityError');return window.__qaPad.connected?[window.__qaPad]:[];}});
 },{state,motion,api});const p=await c.newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));await p.goto(endpoint);const b=await(await p.request.get(endpoint+'/build-provenance.json')).json();assert.equal(b.sourceDigest,digest);await p.locator('[data-ui="resume"]').click();assert.equal(await save(p),JSON.stringify(state));await pause(p,130);return{c,p,errors,build:b};}
async function test(name,fixture,fn,options={}){if(process.argv[4]&&!name.includes(process.argv[4]))return;let ctx;const item={name,fixture:fixture.name,kind:fixture.kind};try{ctx=await context(fixture.state,options);Object.assign(item,await fn(ctx.p,fixture));assert.deepEqual(ctx.errors,[]);item.pass=true;}catch(e){item.pass=false;item.error=String(e.stack||e);console.log(JSON.stringify({name,pass:false,error:e.message}));}finally{if(ctx){item.finalFocus=await focus(ctx.p).catch(()=>null);item.finalSaveHash=hash(await save(ctx.p).catch(()=>''));item.errors=ctx.errors;await ctx.c.close();}results.push(item);writeFileSync(output,JSON.stringify({scope:'Actual production handlers; only navigator.getGamepads samples emulated. No injected host or adapter. Diagnostic fixtures are unearned validated saves; no physical hardware claim.',digest,referenceSHA:hash(readFileSync(base+'/references.json.gz')),harnessSHA:hash(readFileSync(import.meta.filename)),results},null,2)+'\n');console.log(JSON.stringify({name,pass:item.pass}));}}
const f=(n,k)=>refs.fixtures.find(x=>x.name===n&&x.kind===k);

try{for(const k of [1,2]){
await test('archive-baseline-held-enter-'+k,f('nonfinal-kill',k),async(p,r)=>{await p.locator(`[data-unit="${r.state.allies[0].uid}"]`).focus();await p.keyboard.down('Enter');assert.equal(await save(p),JSON.stringify(r.state));await p.keyboard.down('Enter');assert.equal(await save(p),JSON.stringify(r.steps[0].after));await p.keyboard.up('Enter');const focused=await focus(p);assert.equal(focused.tag,'BODY');return{observedHeldRepeatCommittedCommand:true,observedRemovedEnemyFocusBODY:true,exactActionReducer:true};});
}}finally{await browser.close();}
