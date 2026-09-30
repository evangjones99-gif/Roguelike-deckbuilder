import assert from 'node:assert/strict';
import {chromium} from '/workspace/Roguelike-deckbuilder/node_modules/playwright/index.mjs';
import {readFileSync,writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
if(process.argv[2]!=='--go')throw Error('Parent final production freeze GO required');
const root='/workspace/Roguelike-deckbuilder',out=root+'/reviews/gameplay-v0.5-runtime',endpoint='http://127.0.0.1:4173',digest='d6221bf764bad593b04981e87bead7ba6868b72cf361d70671af5c91aac39416';
const input=JSON.parse(readFileSync(out+'/diagnostic-inputs.json','utf8')),results={arena:[],previews:[],privacy:[],draw:[],schema:[],tools:[]};
const browser=await chromium.launch({headless:true,executablePath:'/usr/bin/chromium',args:['--no-sandbox']});
const save=async p=>JSON.parse(await p.evaluate(()=>localStorage.getItem('hollowpact.run.v2')));
const snapshot=async p=>p.evaluate(()=>JSON.stringify(Object.entries(localStorage)));
function checkpoint(){writeFileSync(out+'/diagnostic-results-d622.json',JSON.stringify({method:'Actual final production DOM controls on disclosed structurally valid diagnostic saves, natural RAF, motionON. Renderer transforms and screenshot probes are not FPS.',build:digest,inputSHA256:createHash('sha256').update(readFileSync(out+'/diagnostic-inputs.json')).digest('hex'),results},null,2)+'\n');}
async function load(state,{fallback=false,resume=true,raw=null}={}){
 const context=await browser.newContext({viewport:{width:1440,height:900},reducedMotion:'no-preference'});
 if(fallback)await context.route('**/art/tool-vignettes.png',r=>r.abort());
 await context.addInitScript(({state,raw})=>{
  localStorage.setItem('hollowpact.run.v2',raw??JSON.stringify(state));localStorage.setItem('hollowpact.settings.v2',JSON.stringify({motion:true,mute:true,volume:0}));localStorage.setItem('hollowpact.tutorial.v2','yes');
  window.qaDraws=[];const original=CanvasRenderingContext2D.prototype.drawImage;
  CanvasRenderingContext2D.prototype.drawImage=function(...args){const result=original.apply(this,args),image=args[0];
   if(this.canvas.id==='arena'&&image instanceof HTMLImageElement&&args.length===9){
    const dragon=image.src.endsWith('adversaries-atlas.png')&&args[1]>=image.naturalWidth/2&&args[2]>=image.naturalHeight/2;
    const warleader=image.src.endsWith('warleader-poses.png');if(dragon||warleader){const m=this.getTransform(),[x,y,w,h]=args.slice(5),corners=[[x,y],[x+w,y],[x,y+h],[x+w,y+h]].map(([px,py])=>({x:m.a*px+m.c*py+m.e,y:m.b*px+m.d*py+m.f}));qaDraws.push({t:performance.now(),kind:dragon?'dragon':'warleader',sx:args[1],sy:args[2],ground:{x:m.e,y:m.f},bounds:{left:Math.min(...corners.map(p=>p.x)),right:Math.max(...corners.map(p=>p.x)),top:Math.min(...corners.map(p=>p.y)),bottom:Math.max(...corners.map(p=>p.y))},canvas:{width:this.canvas.width,height:this.canvas.height}});}
   }return result;};
 },{state,raw});
 const page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));await page.goto(endpoint);assert.equal((await(await page.request.get(endpoint+'/build-provenance.json')).json()).sourceDigest,digest);
 if(resume){await page.locator('[data-ui="resume"]').click();assert.deepEqual(await save(page),state);}return{context,page,errors};
}
async function action(page,a){
 if(a.type==='endTurn'){await page.locator('[data-action="endTurn"]').click();const c=page.locator('[data-ui="confirm-end"]');if(await c.isVisible())await c.click();}
 else if(a.type==='attack'){await page.locator(`[data-unit="${a.unit}"]`).click();await page.locator(`[data-unit="${a.target}"]`).click();}
 else if(a.type==='play'){await page.locator(`[data-ui="play-card"][data-index="${a.index}"]`).click();if(a.target)await page.locator(`[data-unit="${a.target}"]`).click();}
 else throw Error('Unsupported action');
}
try{
 for(const f of input.arena){const{context,page,errors}=await load(f.before);await page.waitForTimeout(100);await page.evaluate(()=>qaDraws=[]);const checks=[];
  for(const t of f.transitions??[f]){await action(page,t.action);assert.deepEqual(await save(page),t.state);checks.push({action:t.action,canonicalMatch:true,expectedActualHits:t.events.filter(e=>e.type==='hit').length});}
  if((f.transitions??[f]).at(-1).state.phase!=='battle'){const before=JSON.stringify(await save(page));await page.keyboard.press('e');assert.equal(JSON.stringify(await save(page)),before);}
  await page.waitForTimeout(250);await page.locator('#arena').screenshot({path:out+'/d622-diagnostic-'+f.name+'-contact.png'});await page.waitForTimeout(1150);
  const draws=await page.evaluate(()=>qaDraws),dragons=draws.filter(d=>d.kind==='dragon');
  const offscreen=dragons.filter(d=>d.bounds.bottom<0||d.bounds.top>d.canvas.height||d.bounds.right<0||d.bounds.left>d.canvas.width);
  if(f.name.includes('area')||f.name.includes('fourteen')){assert.ok(dragons.length);assert.equal(offscreen.length,0);}
  await page.waitForFunction(()=>!document.querySelector('#app').classList.contains('settling-combat'));
  assert.deepEqual(errors,[]);results.arena.push({name:f.name,checks,errors,dragonDrawCount:dragons.length,offscreenDragonDraws:offscreen.length,dragonGroundY:dragons.length?[Math.min(...dragons.map(d=>d.ground.y)),Math.max(...dragons.map(d=>d.ground.y))]:null,warleaderPoseCrops:[...new Set(draws.filter(d=>d.kind==='warleader').map(d=>`${d.sx},${d.sy}`))],draws});checkpoint();await context.close();
 }
 for(const f of input.previews){const{context,page,errors}=await load(f.state),before=await snapshot(page),a=f.action;
  if(a.type==='attack')await page.locator(`[data-unit="${a.unit}"]`).click();else if(a.target)await page.locator(`[data-ui="play-card"][data-index="${a.index}"]`).click();else await page.locator(`[data-ui="play-card"][data-index="${a.index}"]`).focus();
  if(a.target)await page.locator(`[data-unit="${a.target}"]`).focus();const text=await page.locator('#consequence-preview').innerText();for(const expected of f.expected)assert.ok(text.includes(expected),f.name+' '+text);assert.equal(await snapshot(page),before);assert.deepEqual(await save(page),f.state);
  if(a.target){await page.keyboard.press('Escape');assert.notEqual(await page.locator('#consequence-preview').innerText(),text);assert.equal(await snapshot(page),before);}
  await action(page,a);assert.deepEqual(await save(page),f.after);await page.keyboard.press('e');
  if(['reward','defeat','victory'].includes(f.after.phase))assert.deepEqual(await save(page),f.after);
  await page.waitForFunction(()=>!document.querySelector('#app').classList.contains('settling-combat'));assert.deepEqual(errors,[]);results.previews.push({name:f.name,text,inputStateAndRngUnchanged:true,actualSaveMatches:true,errors});checkpoint();await context.close();
 }
 for(const pair of input.privacy){const texts=[];for(const state of pair.states){const{context,page,errors}=await load(state),before=await snapshot(page),a=pair.action;
   if(a.type==='attack'){await page.locator(`[data-unit="${a.unit}"]`).click();await page.locator(`[data-unit="${a.target}"]`).focus();}else await page.locator(`[data-ui="play-card"][data-index="${a.index}"]`).focus();texts.push(await page.locator('#consequence-preview').innerText());assert.equal(await snapshot(page),before);assert.deepEqual(await save(page),state);assert.deepEqual(errors,[]);await context.close();}
  assert.equal(texts[0],texts[1]);results.privacy.push({name:pair.name,engineKind:pair.engineKind,texts,actualHiddenFutureDiffers:JSON.stringify(pair.future[0])!==JSON.stringify(pair.future[1]),futureField:pair.futureField,unchanged:true});checkpoint();
 }
 for(const engineKind of [1,2]){const original=structuredClone(input.privacy.find(p=>p.name==='hidden-draw-order'&&p.engineKind===engineKind).states[0]);const reversed=structuredClone(original);reversed.draw.reverse();const views=[];
  for(const s of [original,reversed]){const{context,page,errors}=await load(s),before=await snapshot(page);await page.locator('[data-ui="draw"]').click();const copy=await page.locator('.dialog-copy').innerText();assert.ok(copy.includes('without revealing draw order'));views.push(await page.locator('.deck-entry').allTextContents());assert.equal(await snapshot(page),before);assert.deepEqual(errors,[]);await context.close();}
  assert.deepEqual(views[0],views[1]);results.draw.push({engineKind,hiddenPileOrderDiffers:JSON.stringify(original.draw)!==JSON.stringify(reversed.draw),identicalGroupedView:true,views});checkpoint();
 }
 for(const s of input.schema){const raw=' \n'+JSON.stringify(s)+'\n', {context,page,errors}=await load(s,{resume:false,raw});assert.equal(await page.locator('[data-ui="resume"]').count(),0);const notice=await page.locator('.save-notice').innerText();
  await page.locator('[data-ui="settings"]').click();await page.getByRole('button',{name:'Close dialog',exact:true}).click();await page.locator('[data-ui="feedback"]').click();assert.equal(await page.evaluate(()=>localStorage.getItem('hollowpact.run.v2')),raw);assert.equal(await page.evaluate(()=>Object.keys(localStorage).some(k=>k.startsWith('hollowpact.run.v2.backup.'))),false);assert.deepEqual(errors,[]);results.schema.push({schema:s.schema,generation:s.engineKind??'absent',notice,exactRawRetained:true,noRecoveryBackup:true,errors});checkpoint();await context.close();
 }
 const keyboard=JSON.parse(readFileSync(out+'/tool-keyboard.json','utf8'));
 for(const fallback of [false,true]){const{context,page,errors}=await load(input.tools,{fallback});await page.waitForTimeout(250);
  const cards=await page.locator('[data-ui="play-card"]').evaluateAll(cards=>cards.map(c=>({id:c.dataset.card,aria:c.getAttribute('aria-label'),name:c.querySelector('.card-name').textContent,rules:c.querySelector('.card-description').textContent,artReady:c.querySelector('.card-art').classList.contains('illustration-ready'),canvasHidden:c.querySelector('canvas').getAttribute('aria-hidden'),symbolVisible:getComputedStyle(c.querySelector('svg')).visibility!=='hidden'&&getComputedStyle(c.querySelector('svg')).display!=='none'})));
  assert.equal(cards.length,6);for(const c of cards){assert.ok(c.aria.includes(c.name));assert.ok(c.rules.length);assert.equal(c.canvasHidden,'true');assert.equal(c.artReady,!fallback);if(fallback)assert.ok(c.symbolVisible);}
  const before=await snapshot(page);await page.locator('[data-ui="play-card"][data-index="0"]').focus();await page.keyboard.press('Enter');assert.equal(await snapshot(page),before);await page.locator(`[data-unit="${keyboard.action.target}"]`).focus();const preview=await page.locator('#consequence-preview').innerText();await page.keyboard.press('Enter');assert.deepEqual(await save(page),keyboard.after);assert.deepEqual(errors,[]);
  await page.screenshot({path:out+`/d622-tool-art-${fallback?'fallback':'loaded'}-keyboard.png`});results.tools.push({fallback,cards,keyboardSelectedWithoutCommit:true,keyboardTargetCommittedExact:true,preview,errors});checkpoint();await context.close();
 }
 console.log(JSON.stringify({arena:results.arena.map(r=>({name:r.name,checks:r.checks,offscreen:r.offscreenDragonDraws,groundY:r.dragonGroundY})),previews:results.previews.length,privacy:results.privacy.length,draw:results.draw.length,schema:results.schema.length,tools:results.tools.map(t=>({fallback:t.fallback,exact:t.keyboardTargetCommittedExact}))}));
}finally{await browser.close();}
