import { test, expect } from '@playwright/test';
import { applyAction, createGame, validateState } from '../../src/engine';

for (const engineKind of [1, 2] as const) {
  for (const preferences of ['null', '{broken']) {
    test(`invalid preferences ${preferences} do not hide generation ${engineKind} campaign`, async ({ page }) => {
      const state = applyAction(createGame(321, 0, {engineKind}), {type:'travel',choice:'battle'});
      const raw = ` \n${JSON.stringify(state)}\n`;
      const errors: string[] = []; page.on('pageerror', e => errors.push(e.message));
      await page.addInitScript(({raw,preferences}) => {
        // Retain a later accepted action across reload instead of reinjecting the fixture.
        if (localStorage.getItem('hollowpact.run.v2') === null) localStorage.setItem('hollowpact.run.v2', raw);
        localStorage.setItem('hollowpact.settings.v2', preferences);
        localStorage.setItem('hollowpact.tutorial.v2', 'yes');
      }, {raw,preferences});
      await page.goto('/');
      await expect(page.locator('.save-notice')).toHaveCount(0);
      await page.locator('[data-ui=resume]').click();
      expect(await page.evaluate(() => localStorage.getItem('hollowpact.run.v2'))).toBe(raw);
      await page.locator('[data-action=endTurn]').click();
      const expected = applyAction(state, {type:'endTurn'});
      const saved = await page.evaluate(() => localStorage.getItem('hollowpact.run.v2'));
      expect(JSON.parse(saved!)).toEqual(expected); expect(validateState(expected)).toBe(true);
      await page.reload(); await page.locator('[data-ui=resume]').click();
      expect(await page.evaluate(() => localStorage.getItem('hollowpact.run.v2'))).toBe(saved);
      expect(await page.evaluate(() => localStorage.getItem('hollowpact.settings.v2'))).toBe(preferences);
      expect(errors).toEqual([]);
    });
  }
}
