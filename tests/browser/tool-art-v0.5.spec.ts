import { test, expect } from '@playwright/test';
import { readFileSync } from 'node:fs';
import { applyAction, createGame, validateState } from '../../src/engine';

const families = { scour: 'hook', harpoon: 'hook', ironward: 'plate', aegis: 'plate', sutures: 'sewing', edict: 'pack' };
const fixture = JSON.parse(readFileSync('reviews/screenshots-v0.2/full-fixture.json', 'utf8'));
// Valid diagnostic inventory rearrangement, not a naturally reached six-tool hand.
const inventory = [...fixture.hand, ...fixture.draw, ...fixture.discard];
fixture.hand = Object.keys(families).map(id => {
  const index = inventory.indexOf(id);
  if (index < 0) throw new Error(`Missing diagnostic card ${id}`);
  return inventory.splice(index, 1)[0];
});
fixture.draw = inventory; fixture.discard = [];

test('illustrated equipment loads in hand and collection; crops resize without affecting the save', async ({ page }) => {
  const errors: string[] = []; page.on('pageerror', e => errors.push(e.message));
  const raw = JSON.stringify(fixture);
  expect(validateState(fixture)).toBe(true);
  await page.addInitScript(raw => {
    localStorage.setItem('hollowpact.run.v2', raw);
    localStorage.setItem('hollowpact.settings.v2', JSON.stringify({ mute: true, volume: 0, motion: false }));
  }, raw);
  await page.goto('/'); await page.locator('[data-ui=resume]').click();
  await expect(page.locator('#dock .illustration-ready')).toHaveCount(6);
  await page.locator('#dock [data-card="scour"]').focus();
  await page.keyboard.press('Enter');
  await expect(page.locator('#dock [data-card="scour"]')).toHaveClass(/selected/);
  await expect(page.locator('#dock .illustration-ready')).toHaveCount(6);
  await page.keyboard.press('Escape');
  await page.locator('[data-ui=deck]').click();
  for (const [id, family] of Object.entries(families)) {
    const card = page.locator(`dialog [data-card="${id}"]`).first();
    await expect(card.locator(`canvas[data-tool-art="${family}"]`)).toHaveCount(1);
    await expect(card.locator('.card-art')).toHaveClass(/illustration-ready/);
  }
  for (const id of ['bloodprice', 'killcommand', 'witchfire']) {
    await expect(page.locator(`dialog [data-card="${id}"]`)).toHaveCount(1);
    await expect(page.locator(`dialog [data-card="${id}"] canvas[data-tool-art]`)).toHaveCount(0);
  }
  for (const viewport of [{width:1920,height:1080},{width:1440,height:900},{width:1280,height:720},{width:1024,height:768},{width:390,height:900}]) {
    await page.setViewportSize(viewport);
    const canvas = page.locator('dialog [data-card="edict"] canvas');
    await expect.poll(() => canvas.evaluate(c => {
      const canvas = c as HTMLCanvasElement, box = canvas.getBoundingClientRect();
      return Math.abs(canvas.width - Math.round(box.width * Math.min(2, devicePixelRatio))) <= 1;
    })).toBe(true);
    const failures = await page.locator('dialog .game-card').evaluateAll(cards => cards.flatMap(card => {
      const cb = card.getBoundingClientRect(), column = card.parentElement!.getBoundingClientRect();
      const outsideColumn = cb.left < column.left - 1 || cb.right > column.right + 1;
      if (outsideColumn) return [`Card overlaps collection column: ${(card as HTMLElement).dataset.card}`];
      return [...card.querySelectorAll('.card-cost,.card-description,.card-name')].filter(e => {
        const b = e.getBoundingClientRect(); return b.bottom > cb.bottom + 1 || b.right > cb.right + 1 || b.left < cb.left - 1;
      }).map(e => e.textContent);
    }));
    expect(failures).toEqual([]);
  }
  expect(await page.evaluate(() => localStorage.getItem('hollowpact.run.v2'))).toBe(raw);
  expect(errors).toEqual([]);
});

test('missing illustration leaves the original symbol and working card controls', async ({ page }) => {
  await page.route('**/art/tool-vignettes.png', route => route.abort());
  const state = applyAction(createGame(121), {type:'travel',choice:'battle'});
  const raw = JSON.stringify(state);
  await page.addInitScript(raw => {
    localStorage.setItem('hollowpact.run.v2', raw);
    localStorage.setItem('hollowpact.settings.v2', JSON.stringify({ mute: true, volume: 0, motion: false }));
  }, raw);
  await page.goto('/'); await page.locator('[data-ui=resume]').click();
  await page.locator('[data-ui=deck]').click();
  const card = page.locator('dialog [data-card="scour"]').first();
  await expect(card.locator('.card-art')).not.toHaveClass(/illustration-ready/);
  await expect(card.locator('.card-art>.icon')).toBeVisible();
  await expect(card).toHaveAccessibleName(/Scour, 1 energy/);
  await card.click(); await expect(page.locator('#dialog-title')).toHaveText('Scour');
  expect(await page.evaluate(() => localStorage.getItem('hollowpact.run.v2'))).toBe(raw);
});
