# v0.6 authored hound contact — isolated candidate

2026-09-30. Arena owner's implementation evidence; **not independent acceptance, a production integration, an AAA/fun certificate or a Steam release**. Arena/art runtime source remains unchanged while root reviews this candidate. All active research is outside Git at `/workspace/scratch/hound-contact-v06/review`.

## Candidate and scope

Candidate arena SHA-256 `4cfa90a38f10b270867683940400cfb1ca954a3aaf773b6c469e5cca1bab13e1`; candidate art metadata SHA `26b515016ecf52996acf91ae704da608224d2d1475a883f9675aa0079abbfb1c`. Baseline source is byte-identical to accepted v0.5/d622 arena `2e2a5d65a58db91d09ef0e8746a98264fca129520a988ccbb3b5233569f32b79` and art `379e6b60f78cafd20170bcbcc4168a490cd2663388131957ad9766df852430b7`. Only candidate `arena.ts` and `art.ts` are eligible for later promotion. The isolated `candidate/engine.ts` is a **type-only QA bridge** and must never replace the actual engine.

An optional `CreaturePoseFrame.contactTip` records fractions of a whole source cell. The current hound attack cell uses the independent reviewer's approximate nose landmark `(432,255)` in its 512×512 cell, i.e. `(432/512,255/512)`. The source cell, crop `(32,96,448,384)`, floor anchor446, anchorX0.5, scale1.1, facing and actual decoded aspect give the nose's painted offset from body ground. This is an authored visual landmark, not a skeletal hitbox. No source image pixels or visible opacity change.

Only a loaded authored physical attack cell opts in. Other creatures, magic/AOE, counters, missing pose sheets and the first140ms anticipation retain existing movement. The original `.74` curve is not globally increased. Instead, for the active hound command:

- Compute the baseline nose at the240ms peak and its distance from the actual resolved target combat point.
- Leave convincing contact unchanged when that distance is ≤max(3 logical pixels, 3% of creature size). Smoothly ramp the correction to full strength over the same margin.
- Derive the desired body root as target minus the mirrored painted nose offset, compensating the actual subtle breath scale.
- Bound that root so the entire sampled attack quad remains in the canvas with a2px margin; preserve a small residual gap when an edge prevents exact reach.
- Add the body-root correction with the existing positive movement amount divided by.74. It peaks at240ms and withdraws on the existing attack/recovery schedule. The source's anticipation coefficients, phase clocks and580ms gesture duration stay unchanged.

Current authored metadata applies only to the existing symmetric-anchor hound cell. Further species/multiple attack frames require their own calibrated points and independent comparisons; this is not certification of a general anatomical animation system. Existing target UID reconciliation, facing/death retention, rendered death anchoring, final presentation bounds and reduced-motion behavior are retained. Counter impact centers correctly follow the altered hound body; actual enemy-target slash and magic-ring centers stay unchanged.

## Paired evidence

`fixture-harness.ts` recreates nineteen valid before/action/after/resolved-event cases with the actual pure engine: far/near left and right, neutral vertical, blocked hit, blocked and partly blocked retaliation, terminal and full-field mutual death, full6×6, ordinary bite, warleader controls and7/14-target breath. Inputs/outputs validate and the reducer does not mutate its input. Diagnostic intents are not claimed naturally generated encounters. The first eleven cases are attributed to preserved independent final v0.5 fixtures.

`compare-harness.mjs`, `narrow-harness.mjs` and `formation-harness.mjs` run the actual two Canvas2D sources on one controlled16.67ms RAF clock. Seventy-six cases cover758×270,1280×540,390×525 and actual narrow390×220. Three further comparisons use a legal command followed100ms later by a fourth binding, changing the formation while the command is in flight. The three before/after states validate and both actual resolved traces are preserved in `formation-fixture.json`.

**All79 comparisons pass** (`measurements.json`): input objects remain unchanged; all busy times remain equal; maximum busy1191ms; draw counts, sampled source/destination rectangles, opacity, mirrors and breath scales remain equal; all non-hound actor draw records remain equal; actual gold target slash and magic-ring records remain equal; no retaliation cue is dropped. Every sampled candidate attack quad checked at240–260ms fits the canvas. The two-caster case retains all14 simultaneous target rings. `comparison.json`, `narrow-comparison.json` and `formation-comparison.json` retain raw timed records and original/candidate identity hashes. Samples include100,140,180,240,241,260,320,401,580,641,741,1000 and1200ms. This clock proves phase/contact geometry, not production FPS.

At the controlled peak, far left/right758×270 gaps fall from91.55/91.58px to approximately zero. At241ms the far partly blocked/counter/death probes remain within0.76px. Near left/right improve from approximately25px to0.16px at241ms. Full-quadrant edge protection leaves the neutral vertical case around7.93px instead of52px; narrow390×220 leaves around5.05px. The accepted narrow duel is unchanged: its measured best gap1.629px is identical, and all source body world coordinates are exactly equal throughout the sampled phases. Dynamic fourth-binding formation contact improves from31/34/24px to0.45/0.73/approximately0px across the three larger/tall dimensions. Projection uses actual draw transforms and actual drawn slash centers, including breath/mirror; no virtual replacement impact is used.

## Actual preserved-app observations

The original web ZIP is independently SHA-verified against the v0.5 manifest: `c8a3210688dde4d6bcbe8229ffbc6ae8b11407aa5e6b396c4dfe79c9b3e51c86`. It is unpacked and served from scratch on5187; every tested page verifies frozen digest `d6221bf764bad593b04981e87bead7ba6868b72cf361d70671af5c91aac39416`.

`ui-prototype-harness.mjs` uses actual immutable d622 UI controls and localStorage, plus a **separate isolated candidate diagnostic canvas**, forwarding the exact accepted action and resolved events after the real canonical save. Original runtime/canvas stays untouched; this is not a newly built production candidate. Fourteen desktop1280×720/narrow390×844 actions save exactly the expected canonical state, with no page/asset errors. Two additional terminal retests also preserve the expected save. Actual field sizes are758×277 and390×220; the first controlled desktop270px fixture is intentionally a nearby geometry comparison, not mislabeled as the exact native field.

The actual inherited desktop far bite defect is reproduced at97.80/97.81px, matching the independent approximately98px finding. The candidate's closest sampled native gaps are7.59px in both directions, near bites about1.6px, narrow far bites about4px, and vertical about8.6/5.4px. Native frame sampling can miss the exact240ms peak; after-save epochs can differ from action/renderer clocks and PNG readback costs time. These records do not establish cadence/performance or claim an impact-timing change. Controlled exact-phase evidence above supplies the timing proof. Native source-sheet/body/death images were directly inspected: jaw meets the quarry instead of an air bite, creatures remain opaque and intact, and the mutual-lethal hound/warleader actually collapse on the floor.

The first terminal capture sometimes missed its short attack/impact overlap due PNG readbacks. Separate terminal retests defer PNG capture until400ms, preserve actual draw observations before then, and show retained real attack/impact and later death. `native-measurements.json` documents the distinction rather than inventing a missing frame. Actual narrow near-contact poses retain the legacy body path; natural per-frame distance differences between two independent canvases are not evidence of a changed trajectory when the controlled source paths are identical.

## Failure modes, prior attempts and limits

Strict installed TypeScript7 CLI passes with project compiler options and the explicit type-only bridge. Manual reduced-motion frames are byte-stable500ms later; OS browser media emulation settles active waits and produces stable frames. Cancel, resize and synthetic hidden-document events settle waits with busy0. Missing Canvas2D gives the existing honest playable-panel notice. Aborting the hound pose sheet falls back to the original static portrait/trajectory with baseline/candidate draw records exactly identical (`extra-checks.json`). No OS suspension/consumer GPU/platform certification is implied.

Earlier experiments are retained under `pass1` and `pass2`: initial fixture labelled mutual death actually had a fully blocked strike and only hound death, corrected by validating the emitted death events; the unsupported TypeScript7 JavaScript API attempt was replaced by the native CLI; a shared preview identity changed before capture, so the strict digest guard aborted and the immutable web ZIP replaced it. Pass2 improved distant contact but needlessly altered a mobile duel already within approximately1px; the arena owner rejected that unnecessary shift, added the soft margin and repeated all79 source comparisons and16 actual-save observations. No runtime code was changed to pass a fixture, and no failed evidence was deleted.

This is a bounded painted-contact repair. Six cel keys, abrupt turn/pose changes, a rapid long-distance pounce, absent intermediate articulation/fall frames and approximate landmarks remain below premium animation craft. Near-vertical edge clamps deliberately leave a small gap. Sparse pose direction cannot perfectly represent every depth angle. Broader creature motion, believable breath, audio/human fun and target-machine draw performance remain separate gates. Require root inspection, actual combined-build integration and independent visual/gameplay/technical review before promotion; no automatic acceptance follows from these owner tests.

## Representative viewed images

- `native-captures/1280-hound-leftward-arena-240.png` / `1280-hound-leftward-prototype-240.png`: preserved-app baseline/candidate combat window, clock caveat above.
- `captures/actual-desktop-field-hound-rightward-241-baseline.png` / `...-candidate.png`: precise controlled rightward contact.
- `captures/actual-narrow-field-hound-duel-short-range-241-baseline.png` / `...-candidate.png`: unchanged close-contact path.
- `captures/tall-narrow-field-hound-vertical-241-candidate.png`: intact edge-protected body.
- `captures/actual-desktop-field-hound-far-left-mutual-death-641-candidate.png`: both real corpses, unchanged cue timing.
- `formation-captures/actual-desktop-field-legal-command-then-fourth-bind-241-candidate.png`: target alignment through moving formation.

`MANIFEST.json` and `HASHES.sha256` will freeze source/assets/evidence identities for review. Only the two candidate source files may later be copied into the project after root GO; active fixtures, the QA bridge and the development servers are not shipping runtime features.
