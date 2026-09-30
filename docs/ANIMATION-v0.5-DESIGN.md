# Painted combat motion — v0.5 design

Status: isolated design/research only. No runtime, rule, source-image or existing review writes; root owns generation and promotion. The v0.4 arena/art remain frozen. This design is grounded in actual viewed artwork and independent rendered review, not a claim of professional animation approval.

## First generation: Ironjaw warleader, six poses

Root chooses the warleader before hound in-betweens. This broadens both source and victim motion: the existing Reaver and Ironjaw boss share the `warlord` silhouette, and independent v0.4 final-hit captures still show them standing while fading. A matching recoil/collapse directly closes that observed hole. Hound still needs intermediate painting; a six-pose warleader will not eliminate its hard cuts or establish full-roster animation quality.

Reference is **only the top-left character** of `public/art/adversaries-atlas.png`, SHA256`5d0ad1963acce4a93e6456d73a840f34d104e2d5b33c82fb491cfcb873801ea5`. It is a heavy bipedal pale gray scarred warleader: skull-like iron faceguard, angular layered blackened plate, exposed muscular arms, ragged deep-red cape/tabard, skull belt ornaments and the same broad chipped cleaver/axe. It is not the hooded caster, wraith or dragon in the other three reference cells. Keep its imposing, hostile proportions; avoid a small cute goblin, rounded toy armor, enlarged eyes, a new sword, extra arms or changing costume between cells.

### Exact sheet and camera contract

- Transparent RGBA1536×1024, three columns×two rows, six512×512 cells. Root may accept a different actual image size only with equal-grid sampling and aspect-preserving anatomy; do not rescale each pose independently.
- Fixed three-quarter camera matching the reference, whole character oriented to the right. Runtime normally mirrors the enemy; generation must not alternate facing/camera between cells.
- Full body, cape and complete cleaver in every cell. No baked floor, cast shadow, backdrop, glow rectangle, labels, divider lines or grid marks. At least32pixels of genuinely transparent margin around cell edges; no significant silhouette/weapon/cape pixels cross a cell boundary. Draw each weapon pose within the cell rather than clipping an overhead blade.
- Common source sampling crop within each cell:`x32,y32,width448,height448`. Common authored ground origin:`(256,464)` in full-cell coordinates; normalized draw anchor:`(.5,(464-32)/448)`.
- Standing anatomy target: head top near64, boots at464, approximately400pixels tall. Initial uniform renderer scale0.96 makes400/448×0.96≈0.857 of nominal figure size, close to the original536/627≈0.855 significant-alpha height. This is a calibration target, not a measured delivered asset. Measure actual art after generation and choose **one** camera scale; never stretch or individually grow/shrink a corpse to match a box.
- Stable body scale/lighting across all six cells. Same head/armor/cleaver dimensions, same scar/helmet/cape identity. Left courtyard torch gives restrained warm edges; cool overcast upper-right fill and dirty rough metal remain coherent. No new emissive eyes or candy highlights.

| Cell | Pose | Specific readable anatomy/action |
| --- | --- | --- |
|Top-left(0,0)|Idle|Original threatening ready stance. Two complete boots grounded; shoulders heavy; cleaver hanging at the same side as reference; cloak torn but still identifiable.|
|Top-middle(1,0)|Anticipation|Weight shifts into bent rear knee, torso winds back, cleaver drawn diagonally across/behind shoulder within frame. Front boot remains planted; head locks toward opponent. Cape lags the torso, does not grow new strips.|
|Top-right(2,0)|Attack/contact|Torso rotates forward into a heavy cleaver chop; leading boot takes load, rear heel rises. Cleaver cutting edge reaches rightward/forward, within crop; bent joints and hand grip remain anatomically coherent. Blade may angle down through target height rather than becoming a huge extended sword.|
|Bottom-left(0,1)|Recovery|Cleaver finishes low and returns under control; elbows/knees retain weight, hips re-center over boots, cape settles. Recognizably the same body returning from the prior strike, not a fresh idle repaint.|
|Bottom-middle(1,1)|Hit reaction|Armor/shoulder jolts away from incoming contact, ribs/hips counterbalance; knees absorb impact and cleaver remains gripped. Head/eyes stay threatening rather than comedic surprise. Boots support the recoil; no whole rigid body tipped above the floor.|
|Bottom-right(2,1)|Collapsed death|Non-graphic defeated body with bent knees/hips, shoulder/hip/head supported on the same floor line. Cleaver lies beside or beneath the forearm, red cape pooled. Same anatomical scale and intact outfit, no dismemberment or blood spray; no standing figure rotated flat with unsupported limbs. Keep head and weapon visible inside32px margins.|

Ground/landmark positions above are **authored targets**, not measurements. Deliverable QA must distinguish boot/shoulder/weapon contacts from lowest alpha: cape hems or the blade are not automatically feet. Record actual per-cell ground anchors and adjust source offsets at one uniform scale. In death, horizontal body length approaches the usable width; fold the limbs/weapon coherently rather than miniaturizing the entire body. All poses must read at the existing small six-unit battle size.

### Exact generation brief for root

> Use only the top-left armored warleader of the supplied2×2 reference atlas. Create one transparent1536×1024RGBA sprite sheet of the SAME original character in six full-body poses arranged exactly3columns×2rows,512-square cells: top row ready idle, braced cleaver wind-up, heavy cleaver contact strike; bottom row controlled recovery, supported hit recoil, grounded non-graphic collapsed death. Fixed right-facing three-quarter camera and identical anatomical scale, skull-like faceguard, pale scarred exposed arms, angular dirty blackened plate, skull ornaments, ragged deep-red cape/tabard and the same chipped broad cleaver/axe in every pose. The other three creatures in the reference must not appear. Each cell has a common floor origin at horizontal center256 and ground line464, standing head near64. Include the entire cape, all limbs and full weapon with at least32transparent pixels at every cell edge. Corpse shoulder/hip/head must rest on the floor, limbs bent with weight, cleaver beside its forearm; do not shrink it, float it, rotate a rigid standing body, dismember it or add blood spray. Restrained left torch warmth plus cool overcast fill, harsh realistic materials, no cute eyes/toy anatomy. Completely transparent backgrounds: no scenery, floor, shadow, halo rectangle, text, cell lines or labels. Keep the camera/light/gear identity consistent; pose changes must come from convincing shoulders, hips, knees, elbows and weapon grip.

This brief is not tool execution. Root should attach the original atlas, preserve exact prompts/all originals/repairs, and inspect containment and identity before publishing an asset. If the model cannot keep full weapon margins or anatomy, repair/reject rather than asking the renderer to hide the problem.

## Runtime timing and actual resolution

Use existing action timings for the first six single poses: anticipation0–140ms, attack140–320ms with canonical impact240ms, recovery320–580ms; reaction220ms; death900ms from resolved lethal hit. The body stays solid (`blendMs0`) while the physical trajectory advances each display frame. Current death holds opaque through300ms and fades over600ms. A single collapsed cell improves defeat readability but still cuts directly to collapse; a later fall/settle sequence is needed for credible mass transfer.

Only actual resolved events initiate effects. Fully blocked real attacks can still communicate contact; canceled/unexecuted attacks must not animate. Armor retaliation is a counter, not a new voluntary cleaver swing—especially if the source died earlier in the event order. Retain source/targetUIDs, stable slots,320ms formation changes, contact-anchored death and the current≤1200ms terminal presentation cap. Canonical state/save commit remains immediate and presentation never replays damage.

A grounded warleader cleaver is not the hound's airborne pounce: metadata altitude0, grounded contact1; keep floor shadows below bodies. Actual foot placement/weapon contact still need production comparison. Existing whole-body lunges can slide planted feet; six cel poses alone do not fix locomotion or prove weighted continuous animation.

## Required sequence contract before multiple frames

Current `poseFrame` selects multi-frame arrays by age modulo total. With several death frames this would repeatedly fall/get up. Age currently starts when a RAF notices a pose change, so a phase-relative sequence can also lag actual impact. These are concrete source constraints; solve them before promoting multi-frame motion.

Proposed presentation-only metadata:

- Sequences specify`playback:'once'|'loop'`; attack, reaction and death are once, clamp to last frame. Only authored idle cycles loop. Missing/malformed frames fall back to existing idle art.
- Each frame has source atlas/cell, crop, uniform anatomical scale, ground origin, named visible landmarks and optional contacts. Use an optional per-frame atlas reference to reuse preserved hound key poses and a separate supplementary sheet; no destructive repacking of old originals.
- Frame age derives from the authoritative presentation event onset/source action, not from the RAF that first selected a pose. Hit/reaction/death clocks derive from actual queued hit times. Dropped frames advance to the correct cell; they must not delay240ms contact or replay a fall.
- Keep actor actions separate from target impacts. One source action can have many actual resolved target hits. AOE must not sum several full body lunges.
- Attack-facing comes from source→target position with an explicit mirror and transformed landmarks. Current fixed side-facing can point a right-facing hound away from a leftward cross-column target. Do not rotate a flat cutout in3D or flip it repeatedly when targets temporarily move through the source.
- Named source-space markers:`ground`,`hip`,`shoulder`,`muzzle_or_blade`,`near_front_contact`,`rear_contact`. Mirror and transform them through the same camera scale as the image. Markers are delivered-art measurements, not guessed from transparent padding. Planted-foot phases lock the chosen world contact; anticipation leans inside the painting rather than sliding the root3.5% backward. Push-off/contact release or acquire authored foot contacts.

A read-only audit also found dragon breath classified as physical for every hunter/ally hit, while `motionFor` sums all those source lunges. Seven simultaneous target hits can move the caster outside the field. Before broader motion promotion, add an actual AOE fixture and separate one caster action from its impacts/classify executed breath as magic. This is an inherited presentation finding, not a request to change damage or game rules. Root has been notified; frozenv0.4 remains untouched.

## Hound expansion after the warleader

Original hound sheet is preserved unchanged, SHA`0f363fb1a22fc6e8ce730eabcc19af7ce61a1c7fdc71d8e52860b0114efe4968`. Its actual alpha boxes and ground references are in `reviews/animation-v0.5/source-inspection.json`. Keep the same damaged bone shoulder/ribs, scarred flesh, black mane, angular muzzle, limb count, paw/claw anatomy and right-facing camera.

A separate3×2 supplementary sheet (1536×1024,512cells) avoids compressing twelve detailed drawings into one low-resolution image. Use the original common32,96,448,384crop, uniform1.1scale and targetground(256,448); measure delivered markers and retain the old per-pose offsets. No body stretch, mirrored arbitrary poses, copied standing skeleton rotated into death, or dissolve used to conceal mismatched anatomy.

| Supplement cell | Needed in-between | Contact/mass intent |
| --- | --- | --- |
|(0,0)|Weight loads between original idle/crouch|Chest lowers, rear hock compresses, planted fore/hind toes hold ground; head/neck tracks prey.|
|(1,0)|Push-off|Rear toes push on floor, hip extends, forelimbs begin lift; mane/tail lag.|
|(2,0)|Early flight|Chest leads, forelimbs extend toward target, hind limbs tuck; all toes clear floor.|
|(0,1)|Bite/claw contact|Jaw/lead claws meet actual target marker; shoulders compress from load, same skull/teeth scale.|
|(1,1)|Forepaw landing|Forepaw absorbs load with elbow/shoulder bend, rear limbs still completing travel; no rigid belly float.|
|(2,1)|Hindfoot settle|Rear contact joins, hips/shoulders absorb and recover; returns toward the preserved recovery/idle keys.|

Suggested total580ms remains: anticipation140ms (new load70+old crouch70); attack180ms (new push40+new early flight40+old airborne20+new contact80, placing contact exactly240ms); recovery260ms (new forelanding70+new hindsettle90+old recovery100). These are authored targets for once playback, not an implemented animation. Preserve the same canonical impact and bounded terminal deadline. A later reaction/fall supplement should add recoil→knee buckle→shoulder/hip settle before the existing collapsed key, keeping the900ms death budget. Do not claim the locomotion sheet adds death continuity.

## Acceptance before promotion

1. Source alpha inspection:1536×1024RGBA, six equal cells, gutters/outer32px contain no significant body/weapon/cape pixels. Record every original/repair hash and exact prompt. No rootpublic copy before assetQA.
2. Identity/camera: compare delivered keys at actual battle size against original top-left warleader and existing hound. Reject changed mask/weapon/cape, limb number, head/body scale, cute eyes, inconsistent light, hard clipping or hidden anatomy.
3. Frame/contact: actual opaque anticipation,240ms blade/jaw target contact, recovery, nonlethal recoil, final collapse on floor, mutual lethal retaliation, leftward/rightward cross-column attacks,3→4 reformation,12actors,390narrow. Inspect complete sequences at natural pace as well as timed captures; stills alone cannot establish smoothness.
4. Rules/UI: exact canonical event targets/orders remain, no state/RNG mutation, final save immediate, stale input blocked only during bounded presentation. Motion-off/hidden/cancel/resize/dispose settle; missing new art falls back to preserved figures and playable controls.
5. Performance: same frozenbaseline, same actual productionframes and target fixture; report decode/memory/drawcost separately. One1536×1024RGBA sheet is about6MiB decoded before texture/caches. Avoid extra whole-canvas filters and per-frame alpha reads. Compare actual cadence under an uncontended renderer; do not call headless measurements target hardware certification.
6. Independent visual/gameplay reviews may reject the candidate; preserve it and revert a regression. Sparse painted sheets remain2.5D, not skeletal rigs. Repeated variant art, nonanimated remaining species, virtual hunter hit location, sound/controller/platform/human-fun gaps still prevent whole-game AAA/Steam-ready agreement.
