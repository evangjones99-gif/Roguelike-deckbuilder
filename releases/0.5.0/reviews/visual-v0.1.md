# Independent visual and accessibility review — v0.1.0 candidate

Reviewer: independent visual/accessibility agent. Status: completed on frozen candidate source. Accept as a development prototype; reject commercial-quality/Steam-ready promotion. This is not a human fun endorsement.

## Scope and method

30 September 2026, system Chromium on Linux via Playwright with SwiftShader software WebGL. Independently ran `reviews/screenshots-v0.1/arena-review.mjs` against Vite on localhost:5173. Inspected generated screenshots at 1440×900 and 390×844, with canvas regions 1440×680 and 390×300. Fixtures deliberately cover twelve art categories, not legal engine play. Inspected `arena.ts`, content definitions, integration contract and production plan. Additional integrated checks at 1440×900,1280×720 and narrow widths will follow. Arena-owner supplied screenshots are context only; the evidence in this folder was captured independently.

## Preliminary arena findings

- Consistent woodland palette, tangible stone slab, carved summoning positions and lanterns establish a clear scene. Owl, fox, stag, moth, drake and spider silhouettes are recognizable at desktop size. The characters have authored parts rather than interchangeable sphere bodies.
- Selection changes the chosen base ring to light gold. This remains a subtle cue; essential selection and target status must also be explicit in HTML.
- At 390px, all twelve figures remain in view without cropping. They become too small for tactical details, so the separate HTML roster must remain the reliable interaction surface. Canvas is decorative and carries an accessible illustration label.
- Independent reduced-motion captures 250ms apart are byte-identical. This confirms the fixture stopped visible animation under the browser preference, rather than merely reducing its amplitude.
- Forcing WebGL context creation to fail produced the promised visible fallback status and hid the canvas. No uncaught page errors appeared in the independent standard fixture. Full fallback combat remains pending the UI.
- Source inspection shows idle, summon pop-in and received-hit motion, but no command lunge/projectile or death exit. The combat remains visually underexpressed compared with a finished commercial deckbuilder. Removal also compacts remaining figures instantly. These are polish priorities, not a claim that a frame was observed during an actual battle.

## Preliminary verdict before integration

Do not promote as a Steam-ready or high-quality/fun release on this evidence. This is an appealing procedural prototype direction, with integrated readability, navigation and real combat still to review. AI image inspection does not establish human enjoyment.

## Integrated first pass (before final source freeze)

Ran `ui-review.mjs` through the actual UI using seed 117: new run, tutorial, map, first battle, Mossling summon, keyboard Enter companion selection and Enter enemy targeting. Opened settings, toggled ambient motion off, checked native dialog Tab and Escape, and tested graphics fallback by forcing WebGL context creation to fail in a separate browser context. Fallback battle displayed five hand cards/two enemies and `E` advanced to turn 2. No uncaught page errors in the completed pass. A second redundant capture timed out in software-rendered Chromium during `page.screenshot`; it did not report a game exception. Do not interpret screenshot timeout as gameplay stability evidence.

Screenshots actually viewed: title, tutorial, battle 1440/1280/390, targeting and graphics fallback. JSON records computed font sizes and focus observations. One screenshot pass began while CSS was being written and caught a Vite CSS import error; preserved as `pre-repair-css-error-1440.png`. UI owner removed the import; fresh title and subsequent UI screenshots render normally.

### Findings sent to implementation owners

1. **P1, accessibility setting:** Ambient motion off initially left the arena moving. The UI wrote a document attribute which the arena did not observe. Actual successive canvas screenshots differed. Arena owner reports adding observation; independent fresh-source verification pending.
2. **P2, readability:** At 1280×720 enemy intent/status is 8px and hand effects 9px. At 390px intent/status is 7px and effects 9px. Vital tactical information requires effort to read despite attractive surrounding composition. A finished game needs larger text and layouts that make space for it. No UI text-scale setting exists in this pass.
3. **P2, accessible names:** Narrow layout hides the Deck button's text with `display:none`, while its icon is `aria-hidden`. The visual book icon remains, but the button needs an explicit accessible name. How-to-play similarly collapses to the question mark; give both controls stable labels.
4. **P2, portrait art framing:** Integrated 390px portrait screenshot crops the outer arena positions. The standalone shallower fixture did not expose this. HTML controls remain in view; fix the camera's width fit using the actual tall scene dimensions.
5. **P2, visual feedback and identity:** The summon appearance and hit wobble are preliminary feedback. Command impacts have no directed motion; death simply removes and compacts pieces. Card glyphs are generic and do not consistently match the 3D identities: Mossling is drawn as a mushroom on the card but as a leafy creature on the table, and several species share a generic spirit outline. Create a consistent illustration/rig registry before commercial promotion.

### Positive evidence, with limits

The title has clear hierarchy and a recognizable warm gold/forest palette. Parchment cards are visually separated from the dark battlefield. The tutorial explains energy, cycling, six summon positions, free commands including summon turns, intention reading and persistent hunter health. Enemy intent is present in HTML; new targeting supplies explicit instructions and valid-target states. Keyboard Tab showed visible gold focus outlines. Native modal focus stayed inside the dialog and Escape closed it. The tested summon-command action worked using Enter. No color-only knowledge is required for the tested battle because names, damage, readiness and selected-target wording exist in accessible button labels. Screen reader operation, controller input, high-contrast mode and real GPU performance remain untested. Audio synthesis was inspected in source but not listened to; no sound-quality score is claimed.

The art is a promising prototype and the UI is thoughtfully composed. It does not yet reach a high-quality commercial presentation because tactical text is too small, card/table identities diverge, and combat lacks directed impact/death motion. Human fun and purchase appeal cannot be established by this visual review.


## Frozen candidate verification and final verdict

Final independent command: `node reviews/screenshots-v0.1/recheck.mjs`. Source hashes before and after the session were identical, so screenshots and observed interactions correspond to the same assembled candidate. This session used the development server, without HMR edits during review; it does not independently certify the packaged executable or Steam installation. JSON evidence: `screenshots-v0.1/recheck.json`; final viewed screenshots: `recheck-battle-1440.png`, `recheck-battle-1280.png`, `recheck-battle-390.png`.

| Source | SHA-256 |
|---|---|
| src/main.ts | f4439d20d4f8eb4d2dd46d5e366672853727302fea4d1ee3b5c0b1df1e17acac |
| src/style.css | 2ed6aaa7569617c5d3bfeec1253697c4548ae25459a44a388e1c56f40a69c2db |
| src/arena.ts | 066222b25bed964f3931a98fa503a43faadd7bc42a118350cb15584f04e5d3aa |
| src/engine.ts | ed14d3e3394d760284694a56d50f4303ad320ecd65cfe25b14e23d1279c74fe5 |
| src/content.ts | c64b68b7813ca4e923faf7b23ca36f871522772efc713fa1134bcbcfe06a9a71 |
| index.html | c6d5b1d90b5f4a93fc94a0d0303bf55c46f52776a13d76e2f128190a093fe25e |

The four actionable usability defects were repaired and verified:

- Motion on produced differing canvas captures; motion off produced byte-identical captures 250ms apart. An earlier locator screenshot waited indefinitely for element stability with motion enabled. The final method clips full-page screenshots to the canvas bounds, avoiding Playwright element-stability waits while accurately observing canvas pixels.
- Desktop intent and effects are now 12px; narrow intent and effects are 11px. Inspected text boxes had equal client/scroll heights in the tested seed-117 battle; wrapped intents remained readable. There is no document horizontal overflow at 1280 or 390px. Narrow hand cards intentionally scroll horizontally. Only the tested hand was checked for overflow, not every possible enhanced-card string or six-unit battle.
- The narrow accessibility snapshot now names the controls Deck, How to play and Settings. Keyboard Enter on Mossling selected it and moved focus to a named valid enemy; another Enter commanded the attack. Deck opened with nine distinct starter card entries and Escape closed it.
- All six summoning columns fit the actual 390×525px integrated canvas. The 3D creatures remain small on portrait layouts; the HTML controls are the reliable interaction surface.

No uncaught page errors appeared during the final session. These checks resolve the reported prototype blockers. The graphics fallback had already allowed a real keyboard end-turn in the first integrated pass; the final session did not repeat the fallback after the motion/camera-only arena repair. The unchanged reducer hashes support that narrow check, without proving every battle action.

### Rubric

Scores are qualitative reviewer judgments on a five-point scale: 1 unusable; 2 weak; 3 adequate prototype; 4 strong; 5 commercial exemplar. They are not player survey ratings, and averaging them cannot remove a blocker.

| Dimension | Score | Reason |
|---|---:|---|
| Composition and visual coherence | 4/5 | Distinct woodland palette, tangible arena and calm title hierarchy. |
| Creature identity across surfaces | 3/5 | 3D silhouettes are recognizable; generic card glyphs often diverge from their companions. |
| Tactical readability | 3/5 | Repaired effects/intents are readable in tested desktop/narrow states; text scaling and complete six-unit/enhanced-string coverage remain absent. |
| Combat feedback | 2/5 | Brief appearance/hit motion exists, but attacks have no direction and deaths/slot compaction are abrupt. |
| Keyboard and motion accessibility | 3/5 | Tested keyboard selection, dialogs, names and motion toggle work. Actual screen-reader use, gamepad input and comprehensive zoom/contrast coverage were not tested. |
| Human enjoyment | Unrated | No prospective-player testing; automated inspection cannot establish fun. |

**Final decision: accept preservation/release as v0.1.0 development prototype with this report included. Reject promotion as a high-quality commercial or Steam-ready release.** The core presentation is coherent and the tested interaction is usable, but the current card/table identity and combat feedback fall below that claim. Next visual milestone should align each card illustration with its creature model and add directed command/hit/death feedback, then repeat independent comparative captures and obtain prospective-player observations. Avoid replacing this historical evidence when later versions improve.

### Independent production-build spot check

After final source freeze, independently navigated the built web preview on localhost:4173 using `screenshots-v0.1/production-check.mjs`. Began seed 117, closed onboarding, entered the first battle, summoned Mossling, and used Enter to select/command it against Briar Imp. The saved state recorded Mossling acted and Briar Imp reduced from 13 to 10 HP. No uncaught page errors appeared. Viewed `production-battle-1280.png`; its card effects and intents remain readable and the expected woodland composition is present. This supplements the full frozen-source development-server review; it is a short production-build check, not a full replay of every setting/fallback.

Build SHA-256 evidence in `production-check.json`:

| Build artifact | SHA-256 |
|---|---|
| dist/index.html | 849f93fffa4c17a07448385359b6b31eef95e39744c1fb688bd3f78a7facdf95 |
| dist/assets/index-CLt3UKLq.js | 8c5f7a86536099bb600739c3ae1582b6b19f48fa3e7e2a0961ddba3549cd0d16 |
| dist/assets/index-CmSrDZUw.css | 27070034313b53dbcfaaf254ac5101e7f2a7cd02ebec4cbc01fe6d1c1eaafd94 |

The final decision above remains unchanged: accepted development prototype; commercial/Steam-quality promotion rejected.
