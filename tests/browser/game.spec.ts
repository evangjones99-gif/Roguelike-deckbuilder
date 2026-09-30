import { test, expect } from '@playwright/test';
import {readFileSync} from 'node:fs';
import { createGame, applyAction, legalActions, validateState, CARDS, type Action, type GameState } from '../../src/engine';

const key = 'hollowpact.run.v2';
const version=JSON.parse(readFileSync('package.json','utf8')).version;
test('first-time tutorial, summon/command, save/resume and settings', async ({page}) => {
  test.setTimeout(90000);
  await page.addInitScript(()=>localStorage.setItem('hollowpact.settings.v2',JSON.stringify({mute:true,volume:0,motion:false})));
  const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto('/');
  const portrait=await page.locator('.title-hunter').evaluate(async element=>{
    const url=getComputedStyle(element).backgroundImage.slice(5,-2);
    const image=new Image();image.src=url;await image.decode();
    return {path:new URL(url).pathname,width:image.naturalWidth,height:image.naturalHeight};
  });
  expect(portrait).toEqual({path:'/art/hunter-portrait.png',width:1199,height:1312});
  await page.getByRole('button',{name:/Begin a new contract/}).click();
  await page.locator('#seed').fill('121');
  await page.getByRole('button',{name:/Accept the warrant/}).click();
  await expect(page.getByRole('heading',{name:'Know your tools. Read your quarry.'})).toBeVisible();
  await page.getByRole('button',{name:/Accept field orders/}).click();
  await page.locator('[data-action="travel"]').first().click();
  let saved = await page.evaluate(k=>JSON.parse(localStorage.getItem(k)!),key) as GameState;
  const summon=legalActions(saved).find(a=>a.type==='play'&&CARDS[saved.hand[a.index]].type==='summon');
  expect(summon).toBeTruthy();
  await clickAction(page,summon!);
  saved = await page.evaluate(k=>JSON.parse(localStorage.getItem(k)!),key) as GameState;
  const command=legalActions(saved).find(a=>a.type==='attack')!;
  await clickAction(page,command);
  const before = await page.evaluate(k=>localStorage.getItem(k),key);
  await page.reload();
  await page.getByRole('button',{name:/Resume contract/}).click();
  expect(await page.evaluate(k=>localStorage.getItem(k),key)).toBe(before);
  await page.getByRole('button',{name:'Settings',exact:true}).click();
  await page.locator('#motion').uncheck();
  await expect(page.locator('html')).toHaveAttribute('data-reduced-motion','true');
  await page.getByRole('button',{name:'Close dialog',exact:true}).click();
  await page.screenshot({path:`reviews/browser-${version}-battle.png`});
  expect(errors).toEqual([]);
});

test('complete seeded run through actual controls matches rules and reaches victory', async ({page}) => {
  test.setTimeout(180000);
  await page.addInitScript(()=>{
    localStorage.setItem('hollowpact.tutorial.v2','yes');
    localStorage.setItem('hollowpact.settings.v2',JSON.stringify({mute:true,volume:0,motion:false}));

  });
  await page.goto('/');
  await page.getByRole('button',{name:/Begin a new contract/}).click();
  await page.locator('#seed').fill('121');
  await page.getByRole('button',{name:/Accept the warrant/}).click();
  let s=createGame(121);
  for(let steps=0;s.phase!=='victory'&&s.phase!=='defeat'&&steps<400;steps++) {
    const a=choose(s); await clickAction(page,a); s=applyAction(s,a);
    const stored=await page.evaluate(k=>JSON.parse(localStorage.getItem(k)!),key);
    expect(stored).toEqual(s);
    if(steps===8) {await page.reload();await page.getByRole('button',{name:/Resume contract/}).click();}
  }
  expect(s.phase).toBe('victory');
  await expect(page.getByRole('heading',{name:'The last mark is dead.'})).toBeVisible();
});

test('corrupt save gives a usable fresh-start path',async ({page})=>{
  await page.addInitScript(()=>localStorage.setItem('hollowpact.run.v2','{"phase":"battle"}'));
  await page.goto('/');
  await expect(page.getByRole('status').filter({hasText:/incompatible save/})).toBeVisible();
  await expect(page.getByRole('button',{name:/Begin a new contract/})).toBeVisible();
});

test('loaded names render as text in the inspection dossier', async ({page})=>{
  let s=applyAction(createGame(121),{type:'travel',choice:'battle'});
  const summon=legalActions(s).find(a=>a.type==='play'&&CARDS[s.hand[a.index]].type==='summon')!;
  s=applyAction(s,summon);
  const payload='<img src=x onerror="document.body.dataset.audit=1">';
  s.allies[0].name=payload;
  expect(validateState(s)).toBe(true);
  await page.addInitScript(({key,state})=>{localStorage.setItem(key,JSON.stringify(state));localStorage.setItem('hollowpact.tutorial.v2','yes');},{key,state:s});
  await page.goto('/');await page.locator('[data-ui="resume"]').click();
  await page.locator(`[data-ui="inspect-unit"][data-uid="${s.allies[0].uid}"]`).click();
  await expect(page.locator('#dialog-title')).toContainText(payload);
  await expect(page.locator('#dialog-title img')).toHaveCount(0);
  expect(await page.evaluate(()=>document.body.dataset.audit)).toBeUndefined();
});

test('full rosters expose every intent and identify duplicate binding targets',async({page})=>{
  await page.setViewportSize({width:1280,height:720});
  const s=JSON.parse(readFileSync('reviews/screenshots-v0.2/full-fixture.json','utf8')) as GameState;
  s.allies[1].name=s.allies[0].name;
  s.enemies[0].intent!.target=s.allies[0].uid;s.enemies[1].intent!.target=s.allies[1].uid;
  expect(validateState(s)).toBe(true);
  await page.addInitScript(s=>{localStorage.setItem('hollowpact.run.v2',JSON.stringify(s));localStorage.setItem('hollowpact.settings.v2',JSON.stringify({motion:false,mute:true,volume:0}));},s);
  await page.goto('/');await page.locator('[data-ui="resume"]').click();
  expect(await page.locator('.unit').count()).toBe(12);
  const hidden=await page.locator('.roster').evaluateAll(rosters=>rosters.flatMap(roster=>{
    const r=roster.getBoundingClientRect();
    return [...roster.querySelectorAll('.unit')].filter(unit=>{const u=unit.getBoundingClientRect();return u.top<r.top-1||u.bottom>r.bottom+1||u.top<0||u.bottom>innerHeight;}).map(unit=>unit.getAttribute('aria-label'));
  }));
  expect(hidden).toEqual([]);
  const intents=await page.locator('.enemy .unit-status').allTextContents();
  expect(intents[0]).toMatch(/binding\s*1/i);expect(intents[1]).toMatch(/binding\s*2/i);
});

function terminalFixture():GameState {
  const s=applyAction(createGame(121),{type:'travel',choice:'battle'});
  s.enemies=s.enemies.slice(0,1);s.enemies[0].hp=1;s.enemies[0].block=0;
  const pile=[...s.hand,...s.draw,...s.discard];const scour=pile.indexOf('scour');
  if(scour<0)throw new Error('Starter deck must contain Scour');
  s.hand=[pile.splice(scour,1)[0]];s.draw=pile;s.discard=[];
  if(!validateState(s))throw new Error('Terminal presentation fixture must be valid');
  return s;
}
async function loadFixture(page:import('@playwright/test').Page,s:GameState,motion:boolean){
  await page.addInitScript(({s,motion})=>{if(!localStorage.getItem('hollowpact.run.v2'))localStorage.setItem('hollowpact.run.v2',JSON.stringify(s));localStorage.setItem('hollowpact.settings.v2',JSON.stringify({motion,mute:true,volume:0}));localStorage.setItem('hollowpact.tutorial.v2','yes');},{s,motion});
  await page.goto('/');await page.locator('[data-ui="resume"]').click();
  await expect(page.locator('.enemy')).toHaveCount(s.enemies.length);
}
test('final strike saves outcome immediately, blocks stale commands and resumes canonical result',async({page})=>{
  await loadFixture(page,terminalFixture(),true);
  await page.locator('[data-ui="play-card"]').click();await page.locator('.enemy.valid-target').click();
  const saved=await page.evaluate(k=>localStorage.getItem(k),key);
  expect(JSON.parse(saved!).phase).toBe('reward');
  await expect(page.locator('#app')).toHaveClass(/settling-combat/);
  await expect(page.locator('[data-action="reward"]')).toHaveCount(0);
  await expect(page.locator('[data-action="endTurn"]')).toBeDisabled();
  await page.keyboard.press('e');expect(await page.evaluate(k=>localStorage.getItem(k),key)).toBe(saved);
  await page.reload();await page.locator('[data-ui="resume"]').click();
  await expect(page.locator('[data-action="reward"]').first()).toBeVisible();
  await expect(page.locator('#app')).not.toHaveClass(/settling-combat/);
  expect(await page.evaluate(k=>localStorage.getItem(k),key)).toBe(saved);
});
test('reduced motion reaches salvage without a presentation hold',async({page})=>{
  await loadFixture(page,terminalFixture(),false);
  await page.locator('[data-ui="play-card"]').click();await page.locator('.enemy.valid-target').click();
  await expect(page.locator('[data-action="reward"]').first()).toBeVisible();
  await expect(page.locator('#app')).not.toHaveClass(/settling-combat/);
});
test('voluntary field report exports exact build context and negative feedback locally without changing save',async({page})=>{
  const external:string[]=[];page.on('request',r=>{if(/^https?:/.test(r.url())&&!r.url().startsWith('http://127.0.0.1:4173/'))external.push(r.url());});
  await loadFixture(page,terminalFixture(),false);
  const before=await page.evaluate(()=>({...localStorage}));
  await page.locator('[data-ui="feedback"]').click();
  await page.locator('#feedback-confusion').fill('[Automated QA, not human feedback] <script>window.qa=1</script> Target unclear.');
  await page.locator('#feedback-choice').fill('None in this synthetic fixture.');
  await page.locator('#feedback-replay').selectOption('no');
  const [download]=await Promise.all([page.waitForEvent('download'),page.locator('#feedback-form button[type="submit"]').click()]);
  const file=await download.path();expect(file).toBeTruthy();const report=JSON.parse(readFileSync(file!,'utf8'));
  expect(report.kind).toBe('voluntary-player-feedback');expect(report.source).toBe('local-export');
  expect(report.responses.replayIntent).toBe('no');expect(report.responses.confusion).toContain('<script>');
  expect(report.context.build.version).toBe(version);
  expect(report.context.build.sourceDigest).toBe(JSON.parse(readFileSync('dist/build-provenance.json','utf8')).sourceDigest);
  expect(report.context.run.seed).toBe(121);expect(report.context.run.phase).toBe('battle');
  expect(await page.evaluate(()=>({...localStorage}))).toEqual(before);
  await expect(page.locator('#dialog script')).toHaveCount(0);expect(external).toEqual([]);
});

async function clickAction(page:import('@playwright/test').Page,a:Action) {
  if(a.type==='play') {await page.locator(`[data-ui="play-card"][data-index="${a.index}"]`).click();if(a.target)await page.locator(`[data-unit="${a.target}"]`).click();}
  else if(a.type==='attack') {await page.locator(`[data-unit="${a.unit}"]`).click();await page.locator(`[data-unit="${a.target}"]`).click();}
  else if(a.type==='camp'&&a.choice==='train') {await page.locator('[data-ui="train"]').click();await page.locator(`[data-action="camp"][data-choice="train"][data-index="${a.index}"]`).click();}
  else if(a.type==='travel'||a.type==='camp'||a.type==='event') await page.locator(`[data-action="${a.type}"][data-choice="${a.choice}"]`).click();
  else if(a.type==='reward') await page.locator(`[data-action="reward"][data-card="${a.card??''}"]`).click();
  else if(a.type==='leave') await page.locator('[data-action="leave"]').click();
  else if(a.type==='endTurn') {await page.locator('[data-action="endTurn"]').click();const confirm=page.locator('[data-ui="confirm-end"]');if(await confirm.isVisible())await confirm.click();}
  else throw new Error(`Unsupported test action ${a.type}`);
}
function choose(s:GameState):Action {
  const aa=legalActions(s);
  if(s.phase==='map') return aa.find(a=>a.type==='travel'&&a.choice==='camp')??aa.find(a=>a.type==='travel'&&a.choice==='battle')??aa[0];
  if(s.phase==='reward')return aa.find(a=>a.type==='reward'&&a.card===null)!;
  if(s.phase==='shop')return aa.find(a=>a.type==='leave')!;
  if(s.phase==='event')return aa.find(a=>a.type==='event'&&a.choice==='forage')!;
  if(s.phase==='camp')return aa.find(a=>a.type==='camp'&&a.choice===(s.hp<45?'rest':'train'))!;
  let best=aa[0],score=-Infinity;
  for(const a of aa) {
    const n=applyAction(s,a);
    if(n.phase==='victory'||n.phase==='reward')return a;
    if(n.phase==='defeat')continue;
    const damage=s.enemies.reduce((v,u)=>v+u.hp,0)-n.enemies.reduce((v,u)=>v+u.hp,0);
    const attack=n.allies.reduce((v,u)=>v+u.attack,0)-s.allies.reduce((v,u)=>v+u.attack,0);
    const value=damage*2+attack*3+(n.hp-s.hp)*2+(n.block-s.block)*0.2+(a.type==='endTurn'?-10:0)+(a.type==='attack'?0.3:0);
    if(value>score){score=value;best=a;}
  }
  return best;
}
