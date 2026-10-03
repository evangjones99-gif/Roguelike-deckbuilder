# Arena v0.5 — bounded caster gesture repair

Phase1 renderer-author QA, frozen for root's production build/review. This does not approve pending warleader artwork, a complete v0.5 release, AAA craft or human enjoyment. Root owns art.ts/images and their later integration; this repair edits only arena.ts. Old releases, images and evidence remain unchanged.

## Confirmed problem and repair

Actual immutable v0.4 production digest`da553781de9d57a2ca3a0c6260082335e7db65ad423c8cfd647e84d4055f5425` reproduced a dragon disappearing during breath against six bindings. The valid diagnostic state executes seven actual hits, one hunter and six bindings. Existing presentation classified each as physical, then summed all seven source-body lunges. The image was wholly outside the457px canvas for17 sampled frames; a captured ground point reachedy1287.95. Before/contact/return pictures were actually viewed. Canonical saved state still matched the expected reducer state: this was a presentation defect, not extra damage. The original timing reference includes pre-Playwright-click latency; it is not an exact240ms action clock. Actual offscreen bounds and images are unaffected by that limitation. Frozen proof remains under`reviews/animation-v0.5/`.

The repaired renderer uses the **actual resolved hit trace** and the source enemy's pre-action stable`intent.target==='all'` to identify a ranged area cast. It does not parse display labels, replay intents or fabricate targets. Every actual hit retains its separate impact; the breath caster stays grounded. One-target enemy bites retain physical movement. Armor retaliation remains a counter rather than a new voluntary attack.

A shared`activeGesture` selects only the source's latest active physical/magic gesture for body movement/pose. This prevents additive displacement from overlapping real actions as well as multi-target casts. Old impact effects remain in flight; the source body never sums their movement. Anticipation/240ms physical contact/recovery coefficients are unchanged.

## Frozen identities and methods

- Repaired arena SHA256:`01bd60015273988470a378e092398938f71f1ac07c4754e04d09e00efbbfcd94`.
- Unedited art.ts at phase1:`0c6b04e531cb6a9afb5b27305835f61a11157720f5fbff8c56a4af6eb928c5ba`.
- Arena baseline from immutable tag`v0.4.0`:`55ca21caebd76cd078213cd3686d167c7600088bae94bbf7411f423858dfc299`; exact source snapshots preserved under`arena-v0.5-evidence/baseline/`.

`arena-v0.5-evidence/fixtures.json` contains before/action/actualstate/events for eight diagnostic cases. Both states validate with the real engine. These are valid diagnostic positions, not claimed naturally reached campaigns. Own A/B harness loads the archived and repaired actual source/images into separate canvases1280×540 sharing a controlled16.67ms RAF. It records source-image transforms, magic impact circles and pending presentation. Exact241ms/351ms captures are repeatable action-clock observations, **not displayFPS or packaged-build acceptance**. Chromium used `/usr/bin/chromium --disable-gpu`; no source-image editing. No uncaught errors.

Own actual UI checks use real rendered controls and naturalRAF in the Vite development application at5173. All serialized commits match canonical engine results exactly, including the legal three-action command→KillCommand→command sequence. This proves source/UI behavior and saves, **not a frozen production-bundle identity**. Root/reviewers must repeat the affected cases on the final build, especially after new artwork integration.

## Affected evidence

| Valid diagnostic | Actual trace | Renderer observation |
| --- | --- | --- |
| Dragon breath /6 bindings |7hits|At241ms old sourcegroundy1556.31 on540px canvas; repairedy302.40. All7distinct actual magic impact circles remain. In actual sourceUI dragon groundy255.92 stays fixed throughout captured action.|
| One-target dragon bite |1hit|Source x302.2286,y481.8031 exactly equal in archived/repaired controlled capture. Physical bite trajectory remains.|
| Fully blocked breath |7hits, allhpLost0|Caster remains grounded and all7real contact cues remain. No extra damage/death is created.|
| Two breath casters |14hits|Both sourcegrounds remainx426.6667/853.3333,y302.40; actual impact circles total14 at351ms. Archived sources instead leave the field.|
| Two ordinary melee casters |2hits|Separate actor gestures/impacts retain prior behavior and780ms remaining initial effect time.|
| Mutual lethal armored counter |Command→enemydeath→retaliation→bindingdeath|1181ms initial presentation bound matches archive. Hound x787.3344,y402.2243 at241ms matches exactly. Counter does not trigger a voluntary source swing.|
| Fully blocked command/counter |Real blockedcommand+retaliation|770ms initial presentation matches archive; the real counter remains.|
| Legal command→ready→command |Two actualcommands+ward|Previous sourcebodyx1123.8464 overshoots by summed lunges; repairedx787.3344 uses the latest single gesture. Both command impact effects remain. All3actual UI action saves match engine states.|

Every A/B before/after/event input snapshot remains unchanged. Every case settles busy0. Manual reduced motion keeps both canvases byte-identical during500ms controlled advancement; cancel/dispose release all pending waits. Shared terminal event staggering and UI cap are unchanged. Canvas fallback, OS-motion, hidden/resize settlement code is unmodified; the prior v0.4 checks remain relevant, with final production regression checks still required.

Viewed actual sourceUI breath contact: dragon remains visible above six reacting bindings, with actual rings on the bindings and hunter impact at its existing virtual location. Viewed archived contact: empty caster space while damage lines continue. This is a concrete repaired defect. Ranged breath still uses generic magic lines/rings, not authored fire; keeping the body grounded does not provide a believable complete dragon breath animation.

## Boundaries and next integration

No rules, damage, RNG, saves or canonical events were changed by this renderer patch. The classifier only uses a resolved enemy hit and stable source intent target; canceled area intents with no hits create no body gesture. Presentation effects stay subordinate to immediate canonical commits and existing bounded terminal transitions.

The body chooses the newest gesture rather than accumulating multiple actions. That intentionally interrupts an earlier actor movement when a new real action begins; earlier impact effects still finish. This is preferable to positional overshoot, but does not author a smooth interrupted recovery. Multi-target casters still have sparse/static paintings. Once-playback frame clocks, target-facing/contact landmarks, more hound in-betweens, supported warleader collapse, visible hunter and distinctive spell art remain future craft work. Root rejected the first uncontained warleader sheet; no rejected image was promoted in this repair. Actual production cadence/load/memory, natural full-run play, and independent v0.5 acceptance remain pending.
