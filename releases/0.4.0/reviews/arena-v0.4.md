# Arena v0.4 implementation review

Renderer-author evidence, not an independent acceptance verdict, human playtest or AAA/Steam readiness claim. Candidate graphics source is frozen for production build and independent comparison.

## Result and source identity

The floor shadow is now visible and uses the same transformed local origin as its ellipse. All shadows and slot sigils render before depth-sorted creature bodies, so a later shadow cannot paint over a previously painted neighbor. The hound's painted airborne attack has an authored broader/lighter footprint. Hound pose changes use solid cel cuts; this removes the previously observed doubled/translucent anatomy at dissolve midpoints.

- Candidate `src/arena.ts` SHA256:`55ca21caebd76cd078213cd3686d167c7600088bae94bbf7411f423858dfc299`.
- Candidate `src/art.ts` SHA256:`0c6b04e531cb6a9afb5b27305835f61a11157720f5fbff8c56a4af6eb928c5ba`.
- Preserved v0.3 source commit:`1be4f11`; original arena SHA`ec0b44aadc869dbf3903f3c6c3d1d0ef96f2c00caed4c75c444be790250620ea`, art SHA`c8ecd30136abb54d865fa80e27649da0049db3c65f879cbfa2a80d2269a14d1d`.
- Hound pose image remains SHA`0f363fb1a22fc6e8ce730eabcc19af7ce61a1c7fdc71d8e52860b0114efe4968`,1536×1024RGBA. No source imagery, game rules or save schema changed by this renderer work.

Evidence and harnesses are in `arena-v0.4-evidence/`. The original v0.3 source snapshots are preserved under `baseline/`. Earlier v0.4 experiment—including its first visually ineffective attempt—is preserved in `arena-v0.4-depth-prototype/`; its report and evidence were not overwritten.

## Contact and pose choices

The inherited radial gradient used absolute world coordinates before translating/scaling a locally centered ellipse. The prototype's first floor-pass/altitude comparison produced byte-identical pixels even though recorded gradient radii/alpha differed. Creating the radial gradient at local(0,0) after the transform produced measured floor-contact changes. Reviewed prototype idle/contact/full12 frames show restrained darkening under feet. The independent visual reviewer conditionally supported production comparison; production acceptance still belongs to the new frozen-build review.

Each hound pose retains the original crop, anatomical scale and calibrated ground anchor. Attack's feet are28sourcepixels above its anchor, approximately0.080×nominal body size. Metadata records that apparent elevation and uses footprint1.12/contactopacity0.68. The elevation is already painted into the image and is **not added again as body displacement**. Preparation resolves death contact and pose before the floor/body passes; strike endpoints are remapped again afterward. The320ms formation interpolation, UID targets and240ms physical contact timing remain intact.

A controlled three-way comparison used the same floor fix, resolved action, movement and coordinates with70ms dissolves,20ms dissolves and0ms cel cuts. Actual hound source-cell/alpha/position draws are recorded in `blend-comparison.json`. At331ms the20ms candidate drew two different anatomies at0.5alpha each. At356ms the old70ms candidate likewise drew two0.5alpha silhouettes. The cut candidate rendered one pose at1.0alpha, at the exact same world coordinates. Viewed these frames and attack161ms: cel cuts clearly preserve solid anatomy; shorter dissolves only shorten the defect. All captures remain preserved, including the rejected20ms variant.

Chosen hound metadata sets all six pose blends to0ms. Other/future atlases retain70ms default unless their metadata overrides it. **Tradeoff:** six hard painted pose changes replace translucent transitions; this does not add articulated joints, authored in-betweens or establish temporal smoothness. The smooth whole-body trajectory still runs each display frame. The independent reviewer supports cut0 as a candidate from the compared stills and will judge natural production pace separately. This is an intentional limited remedy for sparse paintings, not a finished animation system.

## Affected checks

TypeScript source check passes. Own standalone fixtures use actual renderer/engine/images in Chromium `/usr/bin/chromium --disable-gpu`. Controlled16.67ms RAF gives repeatable pose captures, not real display cadence. Raw evidence:`candidate/qa.json`.

- Reachable early lethal case: only actual e1→hunter hit/death, no following intended attack; busy730ms and settles0.
- Validated weak-binding case: e30 kills a10, then actual e31→hunter fallback; busy1141ms and settles0.
- Synthetic final armored mutual kill: command, enemy death, actual retaliation, hound death, canonical reward. Busy1181ms and presentation promise resolves. Grounded corpse remains at contact; standing adversary fades as before.
- Actual Silence control and Edict attack-buff cues still target the resolved units without fake hit poses. Reaction uses one solid hound pose. No before-state, after-state or event input mutation was observed.
-3→4 hound formation anchor:[198.4,440.1]→[227.2,468.45] at160ms→[256,496.8] at340ms. Maximum12 captures at1280×540 and390×500 were viewed; every creature position fits, though narrow creatures remain very small.
- Manual reduced motion and real Playwright OS reduced-motion emulation settle and remain pixel-identical during500ms controlled advancement. Cancel/dispose resolve waits. Resize settles a pending action. A simulated document.hidden property plus visibilitychange event resolves waits and resumes coherently; this is a lifecycle-handler test, **not a real operating-system background-tab observation**.
- No2D context: arena provides the accessible HTML fallback, busy0, immediate promise, and cleans the notice/restores canvas visibility on disposal. Actual production UI fallback/integration remains independent/root testing.
- No uncaught browser errors in the own affected fixtures.

## Live cadence and draw cost

Unlike pose captures, this benchmark uses natural requestAnimationFrame. It compares original v0.3 source and the current candidate sequentially in one headlessLinux Chromium session, with12 synthetic actors at1280×540,600ms warmup and2200ms sample. The callback includes a forced1pixel readback to flush raster work. Full samples/method are in `performance.json`. It is a scoped same-session draw measurement, **not declared target-hardware budget, packaged-build acceptance or an independent benchmark**.

| Renderer | Actual observedfps | Gap p50/p95 | Mean draw+readback | p95 draw+readback |
| --- | ---: | --- | ---: | ---: |
| Preserved v0.3 |60.0027|16.7/16.8ms|3.176ms|4.70ms|
| v0.4 candidate |60.0037|16.7/16.8ms|3.282ms|4.50ms|

Neither sample skipped a display frame; no uncaught errors. Mean candidate cost rose0.106ms(~3.3%) while p95 fell0.2ms, within the practical variation of this single short sample. Source does one extra floor loop but cel cuts avoid drawing a second hound pose. The small visual improvement carries no observed cadence regression in this sample; longer actual production/target-hardware checks remain necessary.

## Remaining craft work

The floor-shadow change is subtle on the detailed wet dark courtyard. It is a grounding improvement, not new environmental depth or camera parallax. Hard cel changes can pop; more coherent painted in-between frames remain the strongest future route to smoother creature motion. Other creatures still have single paintings, and enemy death still fades a standing body. Hunter impacts still aim at a virtual canvas point rather than a visible hunter body. No landing dust, new artwork or new spell grammar was introduced. Human enjoyment, sound craft, sustained performance and commercial readiness remain unassessed by this implementation report.
