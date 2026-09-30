import { test, expect } from '@playwright/test';
import { applyAction, createGame, validateState } from '../../src/engine';

const key = 'hollowpact.run.v2';
for (const engineKind of [1, 2] as const) {
  test(`generation ${engineKind} resumes unchanged and persists its own schema`, async ({ page }) => {
    const state = applyAction(createGame(321, 0, { engineKind }), { type: 'travel', choice: 'battle' });
    const raw = ` \n${JSON.stringify(state)}\n`;
    await page.addInitScript(raw => {
      localStorage.setItem('hollowpact.run.v2', raw);
      localStorage.setItem('hollowpact.settings.v2', JSON.stringify({ motion: false, mute: true, volume: 0 }));
      localStorage.setItem('hollowpact.tutorial.v2', 'yes');
    }, raw);
    await page.goto('/');
    await page.locator('[data-ui="resume"]').click();
    expect(await page.evaluate(k => localStorage.getItem(k), key)).toBe(raw);
    await page.locator('[data-action="endTurn"]').click();
    const saved = await page.evaluate(k => JSON.parse(localStorage.getItem(k)!), key);
    expect(saved).toEqual(applyAction(state, { type: 'endTurn' }));
    expect(validateState(saved)).toBe(true);
    expect(saved.schema).toBe(engineKind === 1 ? 2 : 3);
    expect(saved.engineKind).toBe(engineKind === 1 ? undefined : 2);
    const downloadPromise = page.waitForEvent('download');
    await page.locator('[data-ui="feedback"]').click();
    await page.locator('#feedback-form button[type="submit"]').click();
    const download = await downloadPromise;
    const stream = await download.createReadStream();
    const chunks: Buffer[] = [];
    for await (const chunk of stream!) chunks.push(Buffer.from(chunk));
    const report = JSON.parse(Buffer.concat(chunks).toString());
    expect(report.context.run.saveSchema).toBe(saved.schema);
    expect(report.context.run.rulesGeneration).toBe(engineKind);
    expect(report.responses.replayIntent).toBe('unanswered');
    expect(await page.evaluate(k => JSON.parse(localStorage.getItem(k)!), key)).toEqual(saved);
  });
}

test('unsupported generations retain exact raw data through title inspection', async ({ browser }) => {
  for (const generation of [{ schema: 4, engineKind: 3 }, { schema: 3, engineKind: 9 }, { schema: 3 }]) {
    const candidate = { ...createGame(321, 0, { engineKind: 1 }), ...generation };
    expect(validateState(candidate)).toBe(false);
    const raw = ` \n${JSON.stringify(candidate)}\n`;
    const context = await browser.newContext();
    const page = await context.newPage();
    await page.addInitScript(raw => localStorage.setItem('hollowpact.run.v2', raw), raw);
    await page.goto('/');
    await expect(page.locator('[data-ui="resume"]')).toHaveCount(0);
    await expect(page.locator('.save-notice')).toContainText('unsupported rules version');
    await page.locator('[data-ui="settings"]').click();
    await page.locator('[data-ui="close"]').first().click();
    await page.locator('[data-ui="feedback"]').click();
    expect(await page.evaluate(k => localStorage.getItem(k), key)).toBe(raw);
    expect(await page.evaluate(() => Object.keys(localStorage).some(k => k.startsWith('hollowpact.run.v2.backup.')))).toBe(false);
    await context.close();
  }
});
