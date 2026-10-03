# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: input-v0.6.spec.ts >> composition passes through; synthetic visible blur requires a neutral controller release
- Location: tests/browser/input-v0.6.spec.ts:61:1

# Error details

```
Error: expect(received).toEqual(expected) // deep equality

- Expected  - 4
+ Received  + 3

@@ -1,9 +1,9 @@
  Object {
    "allies": Array [
      Object {
-       "acted": true,
+       "acted": false,
        "attack": 4,
        "block": 0,
        "cardId": "fenstalker",
        "color": "#7f9386",
        "hp": 10,
@@ -45,11 +45,11 @@
        "acted": false,
        "attack": 4,
        "block": 0,
        "cardId": "raider",
        "color": "#a6a59c",
-       "hp": 12,
+       "hp": 16,
        "intent": Object {
          "damage": 0,
          "label": "Raise shield · gain 4 block",
          "target": "e1",
        },
@@ -91,11 +91,10 @@
    "hp": 65,
    "log": Array [
      "A scarred hunter. One final contract. No pact is harmless.",
      "The keep has teeth.",
      "Bound Fen Stalker.",
-     "Fen Stalker strikes Ironjaw Reaver.",
    ],
    "maxHp": 65,
    "nextUid": 4,
    "phase": "battle",
    "relics": Array [],
@@ -107,10 +106,10 @@
    "schema": 3,
    "seed": 121,
    "stats": Object {
      "battles": 1,
      "cardsPlayed": 1,
-     "damageDealt": 4,
+     "damageDealt": 0,
      "turns": 1,
    },
    "turn": 1,
  }
```

# Page snapshot

```yaml
- generic [ref=e1]:
  - generic [ref=e2]:
    - banner [ref=e3]:
      - button "Hollowpact main menu" [ref=e4] [cursor=pointer]:
        - generic [ref=e7]:
          - text: HOLLOWPACT
          - generic [ref=e8]: CONTRACTS · CREATURES · CONSEQUENCES
      - navigation "Game tools" [ref=e9]:
        - button "Deck" [ref=e10] [cursor=pointer]:
          - generic [ref=e13]: Deck 12
        - button "How to play" [ref=e14] [cursor=pointer]:
          - generic [ref=e15]: "?"
        - button "Field report" [ref=e17] [cursor=pointer]
        - button "Settings" [ref=e21] [cursor=pointer]
    - generic [ref=e25]:
      - generic [ref=e26]:
        - 'button "Inspect Marek Voss. Hunter: 65 of 65 health" [ref=e27] [cursor=pointer]'
        - generic [ref=e29]:
          - strong [ref=e30]: Marek Voss
          - generic [ref=e31]: 65 / 65
      - generic [ref=e36]:
        - text: ACTIVE CONTRACT
        - strong [ref=e37]: Contract 1 / 10Turn 1
      - generic [ref=e38]:
        - generic [ref=e39]:
          - strong [ref=e43]: "65"
          - generic [ref=e44]: Gold
        - generic [ref=e45]:
          - strong [ref=e48]: "3"
          - generic [ref=e49]: Energy
    - main [ref=e50]:
      - generic [ref=e52]:
        - generic [ref=e53]:
          - status [ref=e54]: "Fen Stalker · binding 1 → hostile 1: 4 health damage"
          - button "Cancel Esc" [ref=e55] [cursor=pointer]:
            - text: Cancel
            - generic [ref=e56]: Esc
        - region "Bound creatures" [ref=e57]:
          - generic [ref=e58]:
            - generic [ref=e59]: YOUR BINDINGS
            - generic [ref=e60]: 1 / 6
          - generic [ref=e61]:
            - article [ref=e62]:
              - button "Fen Stalker · binding 1. 10 of 10 health, 4 attack. Ready; select, then choose an enemy." [pressed] [ref=e63] [cursor=pointer]:
                - generic [ref=e67]:
                  - strong [ref=e68]:
                    - text: Fen Stalker
                    - generic [aria-hidden] [ref=e69]: B1
                  - generic [ref=e70]:
                    - text: "10"
                    - generic [ref=e73]: /10
                    - generic [ref=e74]: "4"
                - generic [ref=e79]: CHOOSE HOSTILE TARGET
              - button "Inspect Fen Stalker · binding 1" [ref=e80] [cursor=pointer]: i
            - generic "Empty binding slot 2" [ref=e81]:
              - generic [ref=e82]: —
              - generic [ref=e83]: Binding 2 empty
            - generic "Empty binding slot 3" [ref=e84]:
              - generic [ref=e85]: —
              - generic [ref=e86]: Binding 3 empty
            - generic "Empty binding slot 4" [ref=e87]:
              - generic [ref=e88]: —
              - generic [ref=e89]: Binding 4 empty
            - generic "Empty binding slot 5" [ref=e90]:
              - generic [ref=e91]: —
              - generic [ref=e92]: Binding 5 empty
            - generic "Empty binding slot 6" [ref=e93]:
              - generic [ref=e94]: —
              - generic [ref=e95]: Binding 6 empty
          - generic [ref=e96]: One free command per turn.New bindings can act immediately.
        - generic [aria-hidden]:
          - generic: THE BLACK MARCH
          - generic: TARGET ACQUIRED · GIVE THE ORDER
        - region "Enemies" [ref=e97]:
          - generic [ref=e98]:
            - generic [ref=e99]: HOSTILE CONTACTS
            - generic [ref=e100]: 2 / 6
          - generic [ref=e101]:
            - article [ref=e102]:
              - button "Ironjaw Reaver · hostile 1. 16 of 16 health, 4 attack. Raise shield · gain 4 block Select as target." [active] [ref=e103] [cursor=pointer]:
                - generic [ref=e107]:
                  - strong [ref=e108]:
                    - text: Ironjaw Reaver
                    - generic [aria-hidden] [ref=e109]: H1
                  - generic [ref=e110]:
                    - text: "16"
                    - generic [ref=e113]: /16
                    - generic [ref=e114]: "4"
                - generic "Raise shield · gain 4 block" [ref=e122]
              - button "Inspect Ironjaw Reaver · hostile 1" [ref=e123] [cursor=pointer]: i
            - article [ref=e124]:
              - button "Gloam Revenant · hostile 2. 15 of 15 health, 5 attack. 5 damage → hunter · ignores block Select as target." [ref=e125] [cursor=pointer]:
                - generic [ref=e129]:
                  - strong [ref=e130]:
                    - text: Gloam Revenant
                    - generic [aria-hidden] [ref=e131]: H2
                  - generic [ref=e132]:
                    - text: "15"
                    - generic [ref=e135]: /15
                    - generic [ref=e136]: "5"
                - generic "5 damage → hunter · ignores block" [ref=e144]
              - button "Inspect Gloam Revenant · hostile 2" [ref=e145] [cursor=pointer]: i
            - generic "Empty enemy slot 3" [ref=e146]:
              - generic [ref=e147]: —
              - generic [ref=e148]: No contact
            - generic "Empty enemy slot 4" [ref=e149]:
              - generic [ref=e150]: —
              - generic [ref=e151]: No contact
            - generic "Empty enemy slot 5" [ref=e152]:
              - generic [ref=e153]: —
              - generic [ref=e154]: No contact
            - generic "Empty enemy slot 6" [ref=e155]:
              - generic [ref=e156]: —
              - generic [ref=e157]: No contact
          - generic [ref=e158]: Intents resolve in order.A fallen marked creature redirects the hit to the hunter.
    - region "Your hand" [ref=e159]:
      - generic [ref=e160]:
        - generic [ref=e161]:
          - generic [ref=e162]: AVAILABLE CARDS 4
          - generic [ref=e163]:
            - button [ref=e164] [cursor=pointer]:
              - text: Draw
              - strong [ref=e165]: "7"
            - button [ref=e166] [cursor=pointer]:
              - text: Discard
              - strong [ref=e167]: "0"
        - generic [ref=e168]:
          - button "Forbidden Survey, 1 energy. Draw 2 cards." [ref=e169] [cursor=pointer]:
            - generic [ref=e170]: "1"
            - generic [ref=e174]: Forbidden Survey
            - generic [ref=e175]: TOOL
            - generic [ref=e176]: Draw 2 cards.
          - button "Blood Sutures, 1 energy. Heal a creature 6 HP and give it 2 block." [ref=e177] [cursor=pointer]:
            - generic [ref=e178]: "1"
            - generic [ref=e180]: Blood Sutures
            - generic [ref=e181]: TOOL · CHOOSE TARGET
            - generic [ref=e182]: Heal a creature 6 HP and give it 2 block.
          - button "Ash Widow, 2 energy. Your targeted damaging spells deal 2 extra damage while this creature lives." [ref=e183] [cursor=pointer]:
            - generic [ref=e184]: "2"
            - generic [ref=e188]: Ash Widow
            - generic [ref=e189]: BINDING
            - generic [ref=e190]: Your targeted damaging spells deal 2 extra damage while this creature lives.
            - generic [ref=e191]:
              - text: 2 Attack
              - generic [ref=e194]: 7 Health
          - 'button "Cairn Hound, 1 energy. On binding: gain 2 hunter block. Commands deal 2 extra damage to enemies with no block." [ref=e197] [cursor=pointer]':
            - generic [ref=e198]: "1"
            - generic [ref=e202]: Cairn Hound
            - generic [ref=e203]: BINDING
            - generic [ref=e204]: "On binding: gain 2 hunter block. Commands deal 2 extra damage to enemies with no block."
            - generic [ref=e205]:
              - text: 3 Attack
              - generic [ref=e208]: 7 Health
      - generic [ref=e211]:
        - generic [ref=e212]:
          - strong [ref=e215]: "3"
          - generic [ref=e216]: energy
        - button "End turn Enemy intents resolve · draw 5 · refill energy" [ref=e217] [cursor=pointer]:
          - text: End turn
          - generic [ref=e220]: Enemy intents resolve · draw 5 · refill energy
        - generic "Keyboard controls" [ref=e221]:
          - generic [ref=e222]: E End turn · Esc Back
          - generic [ref=e223]: H Hand · B Bindings · T Hostiles
          - generic [ref=e224]: I Inspect · Arrows Move
    - contentinfo [ref=e225]:
      - generic [ref=e226]: v0.6.0 · Playable prototype
      - generic [ref=e227]: Seed 121 · Contract saved locally
      - button "Fullscreen" [ref=e228] [cursor=pointer]
  - status [ref=e229]
```

# Test source

```ts
  1   | import { test, expect, type Page } from '@playwright/test';
  2   | import { applyAction, createGame, legalActions, CARDS, validateState, type GameState } from '../../src/engine';
  3   | import { readFileSync } from 'node:fs';
  4   | const key = 'hollowpact.run.v2';
  5   | function battle(kind: 1 | 2): GameState {
  6   |   let s = applyAction(createGame(121, 0, { engineKind: kind }), { type: 'travel', choice: 'battle' });
  7   |   const summon = legalActions(s).find(a => a.type === 'play' && CARDS[s.hand[a.index]].type === 'summon');
  8   |   if (!summon) throw new Error('Actual starting campaign must offer a binding');
  9   |   return applyAction(s, summon);
  10  | }
  11  | async function load(page: Page, s: GameState, pad = false) {
  12  |   expect(validateState(s)).toBe(true);
  13  |   await page.addInitScript(({ s, pad }) => {
  14  |     localStorage.setItem('hollowpact.run.v2', JSON.stringify(s));
  15  |     localStorage.setItem('hollowpact.settings.v2', JSON.stringify({ motion: false, mute: true, volume: 0 }));
  16  |     if (pad) {
  17  |       const sample = { index: 0, mapping: 'standard', connected: true, axes: [0, 0], buttons: Array.from({ length: 17 }, () => ({ pressed: false, value: 0 })) };
  18  |       (window as any).__testPad = sample;
  19  |       Object.defineProperty(navigator, 'getGamepads', { value: () => [sample] });
  20  |     }
  21  |   }, { s, pad });
  22  |   await page.goto('/'); await page.locator('[data-ui=resume]').click();
  23  | }
  24  | async function saved(page: Page) { return page.evaluate(k => JSON.parse(localStorage.getItem(k)!), key); }
  25  | for (const kind of [1, 2] as const) {
  26  |   for (const activation of ['Enter', 'Space']) test(`kind${kind}: held ${activation} selects without following focus to commit`, async ({ page }) => {
  27  |     const s = battle(kind); await load(page, s);
  28  |     const action = legalActions(s).find(a => a.type === 'attack')!;
  29  |     if (action.type !== 'attack') throw new Error('Command required');
  30  |     await page.locator(`[data-unit="${action.unit}"]`).focus();
  31  |     await page.keyboard.down(activation); await page.keyboard.down(activation);
  32  |     expect(await saved(page)).toEqual(s);
  33  |     await page.keyboard.up(activation);
  34  |     await expect(page.locator(`[data-unit="${action.unit}"]`)).toHaveAttribute('aria-pressed', 'true');
  35  |     await expect(page.locator(`[data-unit="${action.target}"]`)).toBeFocused();
  36  |     expect(await saved(page)).toEqual(s);
  37  |     await page.keyboard.press(activation);
  38  |     expect(await saved(page)).toEqual(applyAction(s, action));
  39  |   });
  40  |   test(`kind${kind}: cancel, nested dossier and nonfinal death retain meaningful focus`, async ({ page }) => {
  41  |     const s = battle(kind);
  42  |     // Structurally valid diagnostic injury; not a naturally earned state.
  43  |     s.enemies[0].hp = 1; s.enemies[0].block = 0;
  44  |     await load(page, s);
  45  |     const action = legalActions(s).find(a => a.type === 'attack' && a.target === s.enemies[0].uid)!;
  46  |     if (action.type !== 'attack') throw new Error('Command required');
  47  |     const source = page.locator(`[data-unit="${action.unit}"]`);
  48  |     await source.focus(); await page.keyboard.press('Enter'); await page.keyboard.press('Escape');
  49  |     await expect(source).toBeFocused(); expect(await saved(page)).toEqual(s);
  50  |     const opener = page.locator('#topbar [data-ui=deck]');
  51  |     await opener.focus(); await page.keyboard.press('Enter');
  52  |     await page.locator('#dialog .game-card').first().focus(); await page.keyboard.press('Enter');
  53  |     await expect(page.locator('#dialog-title')).toBeFocused();
  54  |     await page.keyboard.press('Escape'); await expect(opener).toBeFocused();
  55  |     await source.focus(); await page.keyboard.press('Enter'); await page.keyboard.press('Enter');
  56  |     expect(await saved(page)).toEqual(applyAction(s, action));
  57  |     const focus = await page.evaluate(() => ({ tag: document.activeElement?.tagName, meaningful: document.activeElement?.matches('.ally.ready,.hand-cards button,[data-action=endTurn]') }));
  58  |     expect(focus).toEqual({ tag: 'BUTTON', meaningful: true });
  59  |   });
  60  | }
  61  | test('composition passes through; synthetic visible blur requires a neutral controller release', async ({ page }) => {
  62  |   const s = battle(2); await load(page, s, true);
  63  |   const action = legalActions(s).find(a => a.type === 'attack')!;
  64  |   if (action.type !== 'attack') throw new Error('Command required');
  65  |   await page.locator(`[data-unit="${action.unit}"]`).focus(); await page.keyboard.press('Enter');
  66  |   const target = page.locator(`[data-unit="${action.target}"]`);
  67  |   for (const composingKey of ['i', 'h', 'b', 't', 'ArrowRight']) await target.dispatchEvent('keydown', { key: composingKey, bubbles: true, isComposing: true });
  68  |   await expect(target).toBeFocused(); await expect(page.locator('dialog')).not.toBeVisible();
  69  |   await page.evaluate(() => window.dispatchEvent(new Event('blur')));
  70  |   const button = async (pressed: boolean) => {
  71  |     await page.evaluate(pressed => { (window as any).__testPad.buttons[0] = { pressed, value: pressed ? 1 : 0 }; }, pressed);
  72  |     await page.waitForTimeout(60);
  73  |   };
  74  |   await button(true); expect(await saved(page)).toEqual(s);
  75  |   await page.evaluate(() => window.dispatchEvent(new Event('focus')));
  76  |   await page.waitForTimeout(60); expect(await saved(page)).toEqual(s);
  77  |   await button(false); await button(true);
> 78  |   expect(await saved(page)).toEqual(applyAction(s, action));
      |                             ^ Error: expect(received).toEqual(expected) // deep equality
  79  |   await expect(page.locator('.keyboard-hint')).toContainText('LB/RB Regions');
  80  | });
  81  | test('all twelve intents and complete hand rules fit wide short viewports', async ({ page }) => {
  82  |   const s = JSON.parse(readFileSync('reviews/screenshots-v0.2/full-fixture.json', 'utf8'));
  83  |   await load(page, s);
  84  |   const before = await saved(page);
  85  |   for (const width of [1600, 1920, 2560]) {
  86  |     await page.setViewportSize({ width, height: 720 });
  87  |     const bounds = await page.evaluate(() => ({
  88  |       units: [...document.querySelectorAll('.roster .unit')].map(unit => {
  89  |         const u = unit.getBoundingClientRect(), r = unit.closest('.roster')!.getBoundingClientRect(), i = unit.querySelector('.unit-status')!.getBoundingClientRect();
  90  |         return { contained: u.top >= r.top - 1 && u.bottom <= r.bottom + 1 && i.bottom <= u.bottom + 1, font: parseFloat(getComputedStyle(unit.querySelector('.unit-status')!).fontSize) };
  91  |       }),
  92  |       cards: [...document.querySelectorAll('.hand-cards .game-card')].flatMap(card => {
  93  |         const c = card.getBoundingClientRect();
  94  |         return [...card.querySelectorAll('.card-name,.card-description,.card-stats')].map(part => { const r = part.getBoundingClientRect(); return r.top >= c.top - 1 && r.bottom <= c.bottom + 1 && r.left >= c.left - 1 && r.right <= c.right + 1; });
  95  |       }),
  96  |       hint: (() => { const h = document.querySelector('.keyboard-hint')!.getBoundingClientRect(), p = document.querySelector('.turn-controls')!.getBoundingClientRect(); return h.left >= p.left - 1 && h.right <= p.right + 1 && h.bottom <= p.bottom + 1; })(),
  97  |     }));
  98  |     expect(bounds.units).toHaveLength(12); expect(bounds.units.every(u => u.contained && u.font >= 12)).toBe(true);
  99  |     expect(bounds.cards.every(Boolean)).toBe(true); expect(bounds.hint).toBe(true);
  100 |     expect(await saved(page)).toEqual(before);
  101 |   }
  102 | });
  103 | 
```