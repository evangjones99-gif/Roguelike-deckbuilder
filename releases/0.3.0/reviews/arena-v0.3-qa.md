# Arena v0.3 implementation QA

This is the renderer author's implementation QA, not an independent review, a human fun assessment, or commercial readiness approval. Independent gameplay/visual review and production-package testing are separate.

## Frozen source and artwork

- `src/arena.ts`: `ec0b44aadc869dbf3903f3c6c3d1d0ef96f2c00caed4c75c444be790250620ea`
- `src/art.ts`: `c8ecd30136abb54d865fa80e27649da0049db3c65f879cbfa2a80d2269a14d1d`
- `public/art/hound-poses.png`: `0f363fb1a22fc6e8ce730eabcc19af7ce61a1c7fdc71d8e52860b0114efe4968`, 1536 × 1024 RGBA. Root owns image-generation input preservation and provenance.

Hound sheet: three columns, two rows. Top row idle, anticipation, attack; bottom recovery, reaction, death. Each 512-square cell is sampled with the common 32,96,448,384 source crop, preserving actual cropped-image aspect. All poses use scale1.1 and horizontal center anchor. Ground reference per pose in original cell pixels:446,440,446,400,394,397. Attack feet intentionally clear the ground. No image originals were edited by the renderer.

This is painted multi-pose animation with 70 ms crossfades, not skeletal animation, articulated3D, or a rig. Other creatures still use one painted cutout. A metadata interface supports additional poses and multiple frames per pose.

## Behavior and evidence

Captures, repeatable fixture harness, and raw draw records are in `arena-v0.3-screenshots/`. The harness uses actual local renderer, engine and images in Chromium `/usr/bin/chromium` with `--disable-gpu`, at1280 ×540 canvas and390 ×500 narrow canvas. It substitutes a controlled16.67ms RAF clock to obtain reproducible phase captures. These values are animation-time observations, **not actual display frame-rate or target hardware performance measurements**. Console errors: none.

- Attack:140ms anticipation,180ms attack,260ms recovery, impact at240ms. The physical trajectory now peaks at the impact frame, reaches the painted victim with the jaw/claws, then withdraws. The first contact capture exposed a gap from peaking at320ms; `hound-attack-before-contact-fix.png` and `qa-before-contact-fix.json` preserve that finding. `hound-attack.png` shows the corrected reach at235ms, near contact. Idle/anticipation/attack/recovery captures and draw-source records confirm distinct cells.
- Reaction: actual enemy hit against a surviving hound samples source cell row1/column1; `hound-reaction.png` shows changed limb/body posture, with ground-anchor calibration.
- Death: collapsed hound row1/column2, body holds300ms then fades600ms; separate rising ash particles. A dying lunging attacker retains its contact location rather than teleporting to its original place. `terminal-retaliation.png` shows the grounded collapse beside the enemy.
- Canonical event case, reachable early hunter death: only e1→hunter hit followed by hunter death. The renderer consumes the actual one-hit trace; no following enemy intent is replayed. Busy730ms; settles0.
- Canonical weak-binding case: e30→a10 kills binding; e31→hunter after fallback. The passed event target remains hunter rather than the retained corpse. Busy1141ms; settles0. This own trace/state observation does not replace independent pixel-target verification.
- Terminal retaliation synthetic case: command a10→e30, enemy death, actual retaliation e30→a10, companion death, canonical reward phase. Busy1181ms; presentation promise resolves and remaining busy0. Dying enemy remains visible long enough for the counter effect. Retaliation uses a counter slash and does not invent a new lunging enemy attack. Surviving party members are retained during ordinary winning presentations; actual death events still remove killed companions.
- Formation3→4: first hound anchor moves from[198.4,440.1] through[227.2,468.45] at160ms to[256,496.8] at340ms. Transition uses320ms smoothstep, with interpolated size. Attack endpoints follow UIDs every draw, including during reformation. New units enter a vacant stable slot; death gaps do not immediately shift survivors. `formation-four.png` and maximum12 desktop/narrow captures preserved.
- Nondamage cues: root source audit found Silence/Pack Edict became visually silent with `events=[]`. The engine added actual control/buff events, and the renderer now uses violet/gold rings on their real targets without hit recoil, lunge or fabricated damage. Actual fixture Silence emits hunter→e30 control; Edict emits hunter→a10 attack buff; busy730ms each. `silence-cue.png`/`edict-cue.png` preserved. Prior contact-repair arena hash was`de9e1deffed6541c88e8c0737374f61899bdc8bcf2b035c3b3ad4c2e7bd54bd0`; final hash above includes this narrow cue regression repair.
- Manual reduced motion: pending presentation settles immediately, busy0, and canvas dataURL remains byte-identical after500ms controlled advancement. Cancel and dispose each resolve a pending presentation promise. No state mutation is performed by presentation code. OS reduced motion and hidden-tab/resize behavior retain existing settlement paths; production UI tests remain necessary for integration.

## API contract

`playAction(action,before,after,events?)` schedules resolved presentation and internally calls `render(after)`. UI saves canonical state first; it may retain old battle HTML while awaiting `waitForPresentation()`. `busyMs()` (alias`getPresentationBusyMs`) reports remaining effects. `cancelPresentation()` settles; reduced motion, hidden tabs and disposal release waits. Terminal enemy-source staggering is9ms(max45ms for6sources), normal enemy staggering50ms. Death+maximum terminal stagger fits1185ms, under UI's1200ms cap. A single AOE shares its source delay. The metadata-free fallback does not replay enemy intents; callers should pass canonical resolved events.

## Remaining limits and next work

The hound has six sparse painted poses; 70ms crossfades can show overlapping outlines. Seven other main silhouettes remain static cutouts. Counter sources do not have painted impact/death poses, so humanoids fade standing. Hunter is represented by UI portrait and a virtual canvas impact location rather than an arena body. Effects lack per-attack slash art, distinct spell grammar and layered occlusion from architecture. Pose timing and formation captures support a measurable improvement over v0.2; they do not establish AAA animation craft, full Steam release readiness, or human enjoyment. Actual production-package FPS, natural final-hit UI retention, browser error checks and independent review remain root/reviewer work before acceptance.
