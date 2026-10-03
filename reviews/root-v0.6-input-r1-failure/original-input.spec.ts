import { test, expect, type Page } from '@playwright/test';
import { applyAction, createGame, legalActions, CARDS, validateState, type GameState } from '../../src/engine';
import { readFileSync } from 'node:fs';
const key = 'hollowpact.run.v2';
function battle(kind: 1 | 2): GameState {
  let s = applyAction(createGame(121, 0, { engineKind: kind }), { type: 'travel', choice: 'battle' });
  const summon = legalActions(s).find(a => a.type === 'play' && CARDS[s.hand[a.index]].type === 'summon');
  if (!summon) throw new Error('Actual starting campaign must offer a binding');
  return applyAction(s, summon);
}
async function load(page: Page, s: GameState, pad = false) {
  expect(validateState(s)).toBe(true);
  await page.addInitScript(({ s, pad }) => {
    localStorage.setItem('hollowpact.run.v2', JSON.stringify(s));
    localStorage.setItem('hollowpact.settings.v2', JSON.stringify({ motion: false, mute: true, volume: 0 }));
    if (pad) {
      const sample = { index: 0, mapping: 'standard', connected: true, axes: [0, 0], buttons: Array.from({ length: 17 }, () => ({ pressed: false, value: 0 })) };
      (window as any).__testPad = sample;
      Object.defineProperty(navigator, 'getGamepads', { value: () => [sample] });
    }
  }, { s, pad });
  await page.goto('/'); await page.locator('[data-ui=resume]').click();
}
async function saved(page: Page) { return page.evaluate(k => JSON.parse(localStorage.getItem(k)!), key); }
for (const kind of [1, 2] as const) {
  for (const activation of ['Enter', 'Space']) test(`kind${kind}: held ${activation} selects without following focus to commit`, async ({ page }) => {
    const s = battle(kind); await load(page, s);
    const action = legalActions(s).find(a => a.type === 'attack')!;
    if (action.type !== 'attack') throw new Error('Command required');
    await page.locator(`[data-unit="${action.unit}"]`).focus();
    await page.keyboard.down(activation); await page.keyboard.down(activation);
    expect(await saved(page)).toEqual(s);
    await page.keyboard.up(activation);
    await expect(page.locator(`[data-unit="${action.unit}"]`)).toHaveAttribute('aria-pressed', 'true');
    await expect(page.locator(`[data-unit="${action.target}"]`)).toBeFocused();
    expect(await saved(page)).toEqual(s);
    await page.keyboard.press(activation);
    expect(await saved(page)).toEqual(applyAction(s, action));
  });
  test(`kind${kind}: cancel, nested dossier and nonfinal death retain meaningful focus`, async ({ page }) => {
    const s = battle(kind);
    // Structurally valid diagnostic injury; not a naturally earned state.
    s.enemies[0].hp = 1; s.enemies[0].block = 0;
    await load(page, s);
    const action = legalActions(s).find(a => a.type === 'attack' && a.target === s.enemies[0].uid)!;
    if (action.type !== 'attack') throw new Error('Command required');
    const source = page.locator(`[data-unit="${action.unit}"]`);
    await source.focus(); await page.keyboard.press('Enter'); await page.keyboard.press('Escape');
    await expect(source).toBeFocused(); expect(await saved(page)).toEqual(s);
    const opener = page.locator('#topbar [data-ui=deck]');
    await opener.focus(); await page.keyboard.press('Enter');
    await page.locator('#dialog .game-card').first().focus(); await page.keyboard.press('Enter');
    await expect(page.locator('#dialog-title')).toBeFocused();
    await page.keyboard.press('Escape'); await expect(opener).toBeFocused();
    await source.focus(); await page.keyboard.press('Enter'); await page.keyboard.press('Enter');
    expect(await saved(page)).toEqual(applyAction(s, action));
    const focus = await page.evaluate(() => ({ tag: document.activeElement?.tagName, meaningful: document.activeElement?.matches('.ally.ready,.hand-cards button,[data-action=endTurn]') }));
    expect(focus).toEqual({ tag: 'BUTTON', meaningful: true });
  });
}
test('composition passes through; synthetic visible blur requires a neutral controller release', async ({ page }) => {
  const s = battle(2); await load(page, s, true);
  const action = legalActions(s).find(a => a.type === 'attack')!;
  if (action.type !== 'attack') throw new Error('Command required');
  await page.locator(`[data-unit="${action.unit}"]`).focus(); await page.keyboard.press('Enter');
  const target = page.locator(`[data-unit="${action.target}"]`);
  for (const composingKey of ['i', 'h', 'b', 't', 'ArrowRight']) await target.dispatchEvent('keydown', { key: composingKey, bubbles: true, isComposing: true });
  await expect(target).toBeFocused(); await expect(page.locator('dialog')).not.toBeVisible();
  await page.evaluate(() => window.dispatchEvent(new Event('blur')));
  const button = async (pressed: boolean) => {
    await page.evaluate(pressed => { (window as any).__testPad.buttons[0] = { pressed, value: pressed ? 1 : 0 }; }, pressed);
    await page.waitForTimeout(60);
  };
  await button(true); expect(await saved(page)).toEqual(s);
  await page.evaluate(() => window.dispatchEvent(new Event('focus')));
  await page.waitForTimeout(60); expect(await saved(page)).toEqual(s);
  await button(false); await button(true);
  expect(await saved(page)).toEqual(applyAction(s, action));
  await expect(page.locator('.keyboard-hint')).toContainText('LB/RB Regions');
});
test('all twelve intents and complete hand rules fit wide short viewports', async ({ page }) => {
  const s = JSON.parse(readFileSync('reviews/screenshots-v0.2/full-fixture.json', 'utf8'));
  await load(page, s);
  const before = await saved(page);
  for (const width of [1600, 1920, 2560]) {
    await page.setViewportSize({ width, height: 720 });
    const bounds = await page.evaluate(() => ({
      units: [...document.querySelectorAll('.roster .unit')].map(unit => {
        const u = unit.getBoundingClientRect(), r = unit.closest('.roster')!.getBoundingClientRect(), i = unit.querySelector('.unit-status')!.getBoundingClientRect();
        return { contained: u.top >= r.top - 1 && u.bottom <= r.bottom + 1 && i.bottom <= u.bottom + 1, font: parseFloat(getComputedStyle(unit.querySelector('.unit-status')!).fontSize) };
      }),
      cards: [...document.querySelectorAll('.hand-cards .game-card')].flatMap(card => {
        const c = card.getBoundingClientRect();
        return [...card.querySelectorAll('.card-name,.card-description,.card-stats')].map(part => { const r = part.getBoundingClientRect(); return r.top >= c.top - 1 && r.bottom <= c.bottom + 1 && r.left >= c.left - 1 && r.right <= c.right + 1; });
      }),
      hint: (() => { const h = document.querySelector('.keyboard-hint')!.getBoundingClientRect(), p = document.querySelector('.turn-controls')!.getBoundingClientRect(); return h.left >= p.left - 1 && h.right <= p.right + 1 && h.bottom <= p.bottom + 1; })(),
    }));
    expect(bounds.units).toHaveLength(12); expect(bounds.units.every(u => u.contained && u.font >= 12)).toBe(true);
    expect(bounds.cards.every(Boolean)).toBe(true); expect(bounds.hint).toBe(true);
    expect(await saved(page)).toEqual(before);
  }
});
