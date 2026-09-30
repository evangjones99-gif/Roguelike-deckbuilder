import { test, expect } from '@playwright/test';
import { applyAction, createGame, validateState } from '../../src/engine';

test('draw inspection reveals counts but no category order from the hidden pile', async ({ browser }) => {
  const original = applyAction(createGame(121, 0, { engineKind: 1 }), { type: 'travel', choice: 'battle' });
  const reversed = structuredClone(original);
  reversed.draw.reverse();
  expect(validateState(original)).toBe(true);
  expect(validateState(reversed)).toBe(true);
  expect(original.draw).not.toEqual(reversed.draw);
  const views: string[][] = [];
  for (const state of [original, reversed]) {
    const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    const page = await context.newPage();
    const errors: string[] = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.addInitScript(s => {
      localStorage.setItem('hollowpact.run.v2', JSON.stringify(s));
      localStorage.setItem('hollowpact.settings.v2', JSON.stringify({ motion: false, mute: true, volume: 0 }));
      localStorage.setItem('hollowpact.tutorial.v2', 'yes');
    }, state);
    await page.goto('/');
    await page.locator('[data-ui="resume"]').click();
    const before = await page.evaluate(() => localStorage.getItem('hollowpact.run.v2'));
    await page.locator('[data-ui="draw"]').click();
    await expect(page.locator('.dialog-copy')).toContainText('without revealing draw order');
    const view = await page.locator('.deck-entry').allTextContents();
    expect(view).toHaveLength(new Set(state.draw).size);
    views.push(view);
    expect(await page.evaluate(() => localStorage.getItem('hollowpact.run.v2'))).toBe(before);
    expect(errors).toEqual([]);
    await context.close();
  }
  expect(views[0]).toEqual(views[1]);
});
