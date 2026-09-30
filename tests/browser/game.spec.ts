import { test, expect } from '@playwright/test';
import {readFileSync} from 'node:fs';
import { createGame, applyAction, legalActions, validateState, CARDS, type Action, type GameState } from '../../src/engine';

const key = 'hollowpact.run.v2';
test('first-time tutorial, summon/command, save/resume and settings', async ({page}) => {
  test.setTimeout(90000);
  await page.addInitScript(()=>localStorage.setItem('hollowpact.settings.v2',JSON.stringify({mute:true,volume:0,motion:false})));
  const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto('/');
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
  await page.screenshot({path:'reviews/browser-v0.2-battle.png'});
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
