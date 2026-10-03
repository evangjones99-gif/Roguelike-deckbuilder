import { test, expect, type Page } from '@playwright/test';
import { readFileSync } from 'node:fs';
import { applyAction, applyActionWithEvents, createGame, validateState, type GameState } from '../../src/engine';
import { ENEMIES } from '../../src/content';
const key = 'hollowpact.run.v2';
function battle(): GameState { return applyAction(createGame(121), {type:'travel',choice:'battle'}); }
function hand(s: GameState, id: string) {
  const pile = [...s.hand,...s.draw,...s.discard];
  const index = pile.indexOf(id);
  if (index < 0) s.deck.push(id); else pile.splice(index,1);
  s.hand=[id];s.draw=pile;s.discard=[];
}
function bind(s: GameState, id: string): GameState {
  hand(s,id); return applyAction(s,{type:'play',index:0});
}
async function load(page: Page, s: GameState) {
  expect(validateState(s)).toBe(true);
  await page.addInitScript(s=>{
    localStorage.setItem('hollowpact.run.v2',JSON.stringify(s));
    localStorage.setItem('hollowpact.settings.v2',JSON.stringify({motion:false,mute:true,volume:0}));
    localStorage.setItem('hollowpact.tutorial.v2','yes');
  },s);
  await page.goto('/');await page.locator('[data-ui="resume"]').click();
}

test('focused spell preview includes actual widow/relic/resistance/block and preserves RNG/save',async({page})=>{
  let s=bind(battle(),'ashwidow');hand(s,'scour');s.relics=['moon-charm'];
  s.enemies[0]={...s.enemies[0],...ENEMIES.revenant,cardId:'revenant',hp:15,maxHp:15,block:3};
  const target=s.enemies[0].uid;
  const resolved=applyActionWithEvents(s,{type:'play',index:0,target});
  const hit=resolved.events.find(e=>e.type==='hit'&&e.target===target);
  if(!hit||hit.type!=='hit')throw Error('Fixture must resolve a targeted hit');
  await load(page,s);const before=await page.evaluate(k=>localStorage.getItem(k),key);
  await page.locator('[data-ui="play-card"]').click();
  await page.locator(`[data-unit="${target}"]`).focus();
  await expect(page.locator('#consequence-preview')).toContainText(`${hit.hpLost} health damage`);
  await expect(page.locator('#consequence-preview')).toContainText(`${hit.blocked} blocked`);
  expect(await page.evaluate(k=>localStorage.getItem(k),key)).toBe(before);
  await page.locator(`[data-unit="${target}"]`).click();
  expect(await page.evaluate(k=>JSON.parse(localStorage.getItem(k)!),key)).toEqual(resolved.state);
});

test('terminal command preview warns of actual lethal retaliation before committing',async({page})=>{
  let s=bind(battle(),'cairnhound');s.allies[0].hp=2;s.allies[0].attack=7;
  s.enemies=[{...s.enemies[0],...ENEMIES.ironjaw,cardId:'ironjaw',hp:2,maxHp:112,block:3}];
  await load(page,s);const before=await page.evaluate(k=>localStorage.getItem(k),key);
  await page.locator('.ally').click();
  await expect(page.locator('#consequence-preview')).toContainText('2 health damage (lethal)');
  await expect(page.locator('#consequence-preview')).toContainText('binding 1 takes 2 retaliation (lethal)');
  await expect(page.locator('#consequence-preview')).toContainText('contract cleared');
  expect(await page.evaluate(k=>localStorage.getItem(k),key)).toBe(before);
  await page.locator('.enemy.valid-target').click();
  expect((await page.evaluate(k=>JSON.parse(localStorage.getItem(k)!),key)).phase).toBe('reward');
});

test('immediate Blood Price hover/focus warns that hunter dies without changing campaign',async({page})=>{
  const s=battle();hand(s,'bloodprice');s.hp=3;await load(page,s);
  const before=await page.evaluate(k=>localStorage.getItem(k),key);
  await page.locator('[data-ui="play-card"]').hover();
  await expect(page.locator('#consequence-preview')).toContainText('HUNTER DIES · campaign ends');
  await page.locator('[data-ui="play-card"]').focus();
  await expect(page.locator('.battle-guidance')).toHaveClass(/danger-preview/);
  expect(await page.evaluate(k=>localStorage.getItem(k),key)).toBe(before);
  await page.locator('[data-ui="play-card"]').click();
  expect((await page.evaluate(k=>JSON.parse(localStorage.getItem(k)!),key)).phase).toBe('defeat');
});

test('ally healing preview shows capped health restoration and actual block',async({page})=>{
  let s=bind(battle(),'cairnhound');s.allies[0].hp=5;hand(s,'sutures');await load(page,s);
  await page.locator('[data-ui="play-card"]').click();
  await expect(page.locator('#consequence-preview')).toContainText('restores 2 health');
  await expect(page.locator('#consequence-preview')).toContainText('gains 2 block');
});

test('all twelve intent panels fit at1024x720 while showing lethal command consequence',async({page})=>{
  await page.setViewportSize({width:1024,height:720});
  const s=JSON.parse(readFileSync('reviews/screenshots-v0.2/full-fixture.json','utf8')) as GameState;
  s.allies[0].hp=1;s.allies[0].attack=30;s.enemies[0].block=3;
  await load(page,s);await page.locator('.ally').first().click();
  await expect(page.locator('#consequence-preview')).toContainText('retaliation (lethal)');
  const layout=await page.locator('.unit').evaluateAll(units=>units.map(unit=>{
    const r=unit.getBoundingClientRect(),p=unit.closest('.roster')!.getBoundingClientRect();
    return {inside:r.top>=p.top&&r.bottom<=p.bottom,px:parseFloat(getComputedStyle(unit.querySelector('.unit-status')!).fontSize)};
  }));
  expect(layout).toHaveLength(12);expect(layout.every(x=>x.inside&&x.px>=12)).toBe(true);
});

test('only known inherited Silence overflow is recovered with exact original backup and neutral notice',async({page})=>{
  const fixture=JSON.parse(readFileSync('reviews/solo-v0.3/silence-overflow-campaign.json','utf8'));
  const original=JSON.stringify(fixture.afterState);
  await page.addInitScript(({key,original})=>localStorage.setItem(key,original),{key,original});
  await page.goto('/');
  await expect(page.locator('.save-notice')).toContainText('Recovered a repeated Silence status label. Your run is preserved.');
  const stored=await page.evaluate(k=>({run:JSON.parse(localStorage.getItem(k)!),backup:localStorage.getItem(`${k}.backup.silence`)}),key);
  expect(stored.backup).toBe(original);expect(validateState(stored.run)).toBe(true);
  await page.locator('[data-ui="resume"]').click();await expect(page.locator('.enemy').first()).toBeVisible();
});

test('unrelated corruption is rejected and original primary text is preserved',async({page})=>{
  const fixture=JSON.parse(readFileSync('reviews/solo-v0.3/silence-overflow-campaign.json','utf8'));
  fixture.afterState.hp=-1;const original=JSON.stringify(fixture.afterState);
  await page.addInitScript(({key,original})=>localStorage.setItem(key,original),{key,original});
  await page.goto('/');await expect(page.locator('.save-notice')).toContainText('incompatible save');
  await expect(page.locator('[data-ui="resume"]')).toHaveCount(0);
  expect(await page.evaluate(k=>localStorage.getItem(k),key)).toBe(original);
});

test('recovery preserves an existing different backup and creates a separate exact raw backup',async({page})=>{
  const fixture=JSON.parse(readFileSync('reviews/solo-v0.3/silence-overflow-campaign.json','utf8'));
  const original=JSON.stringify(fixture.afterState);
  await page.addInitScript(({key,original})=>{
    localStorage.setItem(key,original);localStorage.setItem(`${key}.backup.silence`,'older preserved save');
  },{key,original});
  await page.goto('/');
  const stored=await page.evaluate(k=>({prior:localStorage.getItem(`${k}.backup.silence`),others:Object.keys(localStorage).filter(key=>key.startsWith(`${k}.backup.silence.`)).map(key=>localStorage.getItem(key)),run:JSON.parse(localStorage.getItem(k)!)}),key);
  expect(stored.prior).toBe('older preserved save');expect(stored.others).toContain(original);expect(validateState(stored.run)).toBe(true);
});

test('failed backup storage never overwrites the inherited original while recovered play remains available',async({page})=>{
  const fixture=JSON.parse(readFileSync('reviews/solo-v0.3/silence-overflow-campaign.json','utf8'));
  const original=JSON.stringify(fixture.afterState);
  await page.addInitScript(({key,original})=>{
    localStorage.setItem(key,original);localStorage.setItem('hollowpact.settings.v2',JSON.stringify({motion:false,mute:true,volume:0}));
    const normal=Storage.prototype.setItem;
    Storage.prototype.setItem=function(k,v){if(k.startsWith(`${key}.backup.silence`))throw new DOMException('Synthetic QA backup failure','QuotaExceededError');normal.call(this,k,v);};
  },{key,original});
  await page.goto('/');await expect(page.locator('.save-notice')).toContainText('original save is unchanged');
  await page.locator('[data-ui="resume"]').click();await page.locator('[data-action="endTurn"]').click();
  const confirm=page.locator('[data-ui="confirm-end"]');if(await confirm.isVisible())await confirm.click();
  expect(await page.evaluate(k=>localStorage.getItem(k),key)).toBe(original);
});
