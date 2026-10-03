# Independent visual and accessibility review — v0.3 candidate

**Verdict: accept v0.3 as an improved development prerelease; reject commercial/AAA/Steam-ready promotion.** The hound attack, final-hit retention, hunter identity and repaired collection readability improve the preserved v0.2 baseline. The whole game still falls short of the requested craft standard. This is an independent agent assessment with actual browser evidence, not a human enjoyment claim. The owner now supports2.5D; articulated3D is optional, and polished painted animation can meet the intended direction.

## Preserved comparison baseline

v0.2.0 development prerelease is preserved at `releases/0.2.0`, source commit `d7604f220c3c6e242ef63ac526c1f493d542db26`, runtime source digest `006db8571a5c1697b21bcbe51434161e53bb75580c5b72bed852efdd4da7bee9`. Web archive SHA-256: `712a8717beb6a17a076c74ef82cc556152c00cf0f92a972a0c42e31516f1cca7`. Its independent visual report accepts a development prototype and rejects commercial/AAA promotion.

Baseline strengths to protect: grim courtyard/creature identity, matching card/arena portraits, all twelve occupied desktop combat panels visible at1024×720 and larger, readable12px intents, keyboard commands/dossiers, reduced-motion stability, no clipping of tested48 base/enhanced deck cards, and approximately59fps measured during a headless six-versus-six sample. These are scoped test observations, not a guarantee on hardware.

Baseline weaknesses under review: single-pose cutout actions, abrupt fourth-unit formation switch, immediate reward overlay concealing final death, incomplete actor identity, shared variant art and unassessed professional sound/human enjoyment. Archived files and previous reviews remain unchanged.

## Candidate acceptance checks

1. **Anatomy and identity across attack poses.** Examine actual original atlas cells and rendered wind-up, contact and recovery. The hound must keep the same head, bone armor, limb count and proportions. Look for regenerated anatomy, conflicting accessories, doubled limbs from crossfade, stretched joints, clipping, or changing scale. A pose sheet is not a skeletal rig; report the actual technique and coverage. A single improved creature cannot establish full-roster commercial animation.
2. **Grounded action readability.** Activate attacks through keyboard and mouse. Observe which figure prepares, where its body/feet/shadow move, which target reacts, and whether contact/feedback matches the damage. Record actual pose-cell changes and timings when feasible. Crossfaded standees or sliding body images should not be labelled articulated movement.
3. **Final hit and death before reward.** Trigger a final kill in a real battle. Verify that source, target and outcome remain visible before rewards replace the battlefield; capture actual user-visible frames and phase timing. Check repeated clicks, `E`, pause/resume and reduced-motion behavior during the transition. Rule/save state must remain consistent, and the presentation delay must not block reward progression or accept stale actions.
4. **Stable formations and removal.** Follow one, three, four and six-unit situations. Compare source/target positions before and after a fourth summon, death, replacement summon and layout change. Verify pending effects remain aimed at the matching units. Retained death images must not cause survivor teleportation or cover another target.
5. **Hunter identity and UI readability.** Inspect the scarred hunter portrait, framing and accessible health/energy information. Repeat full-occupancy desktop panels at1024/1280/1440/1920 widths and narrow390px. Inspect all base/enhanced card strings and slot identifiers. A portrait asset cannot replace clear targets or accessible text.
6. **Motion and rendering.** Measure actual canvas draw cadence in an uninstrumented-for-images window, including six-versus-six. Check motion-off/OS reduced motion, foreground/background behavior, asset failures and canvas fallback. Compare with preserved baseline using the same method, while qualifying headless/platform limitations.
7. **Evidence and claim boundaries.** Preserve source/build/asset hashes, methods, seed, recordings/captures and unassessed areas. No art-quality or fun consensus is manufactured. Audio that was not heard stays unrated; human enjoyment requires prospective players. Development milestone acceptance remains separate from commercial/AAA/Steam-ready promotion.

The commercial craft criteria in `docs/AAA-CRAFT-REVIEW.md` provide review expectations; they are not evidence that a teardown of named commercial titles or target-hardware benchmark has occurred. Relevant regressions or unresolved high-quality blockers will be reported plainly.

### Independent archived-baseline recapture

Before candidate inspection, extracted the immutable v0.2 web archive into a temporary directory and served that archived build separately atlocalhost:5182. Its archive hash matched the manifest. `screenshots-v0.3/baseline-capture.mjs` loaded the existing validated six-versus-six fixture, measured actual arena draws for four seconds, and captured1280×720 and1440×900 screenshots. Viewed the1280 capture: all twelve compact combat rows remain visible, matching the prior verified baseline. No uncaught page errors appeared. This does not inspect a stale candidate server.

Baseline recapture measured239 draws,59.75fps,median16.7ms,p95 17.1ms,max43.8ms gaps in this headlessLinux session. The difference from the prior~59fps sample is normal environmental variation; use the same capture method for v0.3 and qualify comparisons. Exact baseline build hashes and method are recorded in `screenshots-v0.3/baseline.json`.

### Preliminary standalone hunter art inspection

Viewed `public/art/hunter-portrait.png` before runtime freeze (SHA-256 `28d4bdc56c434590ade5c9d69d650c35e284713fb14f45f37bad54190ea4e988`). The scarred face, worn cloak, mail and layered iron fit the established grim setting; wet/material detail is coherent with the courtyard. This is a standalone illustrated portrait assessment, not a runtime framing/accessibility or commercial-quality endorsement. The small HUD crop still needs inspection after the build freezes. An identifiable portrait does not establish a present, animated battlefield actor.


## Independent isolated rig-lab assessment (outside runtime)

**Reject promotion of the current rig-lab hound into the game.** This assessment concerns a separate experimental asset and does not reject the uninspected v0.3 runtime candidate. It is a useful skinning/export study, but replacing the preserved illustrated hound with this model would visibly weaken the established grim art direction.

Method: read `docs/RIG-LAB.md`, viewed the actual full-resolution hero/PBR render, white pre-repair import, repaired import, lunge and death articulation renders, opposite/rear turntable views, and reduced-budget hero render. Compared them directly with the top-left hound in the existing companion atlas. Read the imported structure/contact and budget reports; those are author-generated measurements, not independently reproduced Blender execution. Exact inspected-file hashes are in `screenshots-v0.3/rig-lab-inspection-hashes.json`. No heavy Blender render was launched, and no runtime asset was changed. A few still poses do not verify temporal animation quality; the orbital turntable is not a gait/contact test.

The before/after imported images establish a visible, narrow improvement: the original white export lost material identity; the repaired import visibly restores dark hide, pale armor, colored eye and flesh jaw. The reference still has a much richer and more threatening silhouette: ragged mane, broken bone integrated with wounded musculature, irregular skull/cheek planes, articulated digitigrade limbs and narrow hostile expression. The lab render has smooth capsule-like shoulders/thighs, tube forelegs, rounded detached paw pads, a broad simplified muzzle, regular tooth rows and white eyebrow plates. Its orange eye and open mouth read like a stylized toy creature rather than the reference's harsh predator. Darkening the material does not resolve those anatomical differences.

Armor and skin remain visibly separate layers. Four evenly spaced pale rib strips resemble bands laid over the torso; the spine is a repeated row of clean spikes. The reference's exposed ribs grow from a broken, asymmetric skeletal structure. The lab lacks that attachment logic and coherent transitions between bone, flesh and coarse fur. Scar slivers and scattered mane triangles do not supply the reference's surface hierarchy; material roughness is broadly uniform. The back/rear turntable confirms these are whole-form issues rather than a single camera angle.

The lunge still shows the jaw opening downwards, which is clearer than a twisted hinge, but much of the silhouette remains an upright whole-body translation. The death still is a more serious presentation failure: the torso floats horizontally above the ground with curled feet and the near forelimb hanging down like a support. It does not read as weight transferring into a collapsed body. Author-reported minimum geometry Z near0.01m means no floor penetration in that fixture; it does not establish credible contact, planted feet or mass. No skeletal asset should replace the illustration until actual anticipation→push-off→contact→recovery and fall→ground-settle sequences demonstrate those behaviors.

The reduced-budget hero appears close to the original at this inspected view, and the author reports49,328→22,196 triangles with28bones retained. That is a useful budget experiment, not sufficient approval: deformation, silhouettes from other angles, UV seams and runtime draw cost were not independently measured. Neither triangle count confers visual quality. The current detailed illustration remains the stronger presentation baseline.

Priorities before another promotion request:

1. Rebuild major anatomy and silhouette against consistent side/front/three-quarter references: scapula/chest relationship, angular skull and jaw, digitigrade hocks, tendon flow, integrated paws and asymmetric exposed skeleton. Judge clay renders before adding material complexity.
2. Establish weight and contacts in animated sequences. Author planted-foot push-off and recovery; support the collapsed thorax/hip/head on the ground and settle the limbs. Whole-actor minimum-Z projection cannot substitute for that work.
3. Integrate bone/flesh/fur boundaries and authored roughness/surface variation; replace evenly repeated armor decorations with structurally motivated damage. Preserve legible macro forms at actual battle size.
4. Verify imported deformation, seam/texture fidelity and a defensible geometry budget after the artistic issues improve. Retain every rejected lab variant; obtain an independent runtime comparison before any switch.


### Preliminary pose-sheet inspection (before runtime freeze)

Viewed the actual repaired1536×1024 RGBA sheet (SHA-256 `0f363fb1a22fc6e8ce730eabcc19af7ce61a1c7fdc71d8e52860b0114efe4968`). `screenshots-v0.3/atlas-inspection.py` independently measured cell boundaries: divider/gutter alpha never exceeded1/255; meaningful creature pixels remain well inside all six cells. This resolves obvious hard cell clipping at this asset hash. The sheet retains the reference's broken shoulder armor, exposed ribs, dark mane, damaged flesh and threatening muzzle across its painted poses. Recovery/reaction/death differ in within-cell height, so the renderer's per-pose crop/anchor calibration is material to grounded presentation; inspected source contains that calibration. No runtime grounding or temporal continuity claim follows from this standalone inspection. The sheet has six distinct painted poses, not an articulated skeletal model or a full frame-by-frame attack cycle.


### Authorized provisional static runtime check

Root explicitly authorized static art/UI checks on production4173 at provisional digest `0956d1d9706f80da541fc073a3d225f076d87cfd09d1581c2c31c62032e97661` while its event-cue audit continued. This is not the final animation/performance candidate. Ran `screenshots-v0.3/provisional-static.mjs`; title, hunter HUD, all twelve occupied rows and48 unique base/enhanced deck cards were captured. Viewed title1440, battle1280 and390, and deck1280. No uncaught page errors or failed HTTP responses occurred. The scarred face is recognizable in the actual title/HUD crop and fits the grim identity. Desktop compact rows retain readable12px intents; deck cards show no measured text overflow. Narrow390 preserves named controls and all panels but still requires substantial vertical/horizontal scrolling, and its full-occupancy figures are small. This remains a usability limitation relative to desktop. All evidence and exact provisional build hashes are saved in `screenshots-v0.3/provisional-static.json`; final freeze checks still required.


## Final production runtime evidence

Reviewed localhost4173 in Linux headless Chromium (`/usr/bin/chromium --no-sandbox`). Natural seed121 ran on frozen digest `936821d5bf112eea14d4b4c526f6b054eb3c6ed93752f9ad1eb0a254c5222f74`; the only subsequent authorized runtime change was the collection-card height repair. Final clean cadence, layout, terminal, fallback, descendant-containment and supplemental checks ran on digest **`1ef47ce481c3f8722e624fe6df1540d2957462c20c8ba7213c77ed4583a7f258`**. Source and build hashes stayed unchanged through the final cadence/layout/keyboard capture. Screenshots were actually viewed; raw scripts and JSON preserve methods and fixture boundaries.

| Area | Independent result | Remaining craft limit |
| --- | --- | --- |
| Hound action | Natural seed121 keyboard command drew distinct idle→crouch→airborne attack→recovery cells. Viewed actual completed canvas captures `pose-rendered-0..3.png`; attacker approaches the matching enemy. Anatomy/armor identity stays coherent and sampling preserves aspect. | Six single painted poses crossfade over70ms and translate; this is not continuous joint articulation. Other species still use single-pose images. |
| Final strike | Natural play reached salvage on turn2 after12 further actions. Constructed one-hit terminal trace retained the field until1138.5ms and showed salvage at1155.2ms. Canonical phase was already saved as reward. Repeated `E` and stale clicks left the save unchanged. | Single-pose adversaries remain standing while fading. They need authored recoil/collapse rather than a fade-only death. The hold retains pre-hit panel numbers temporarily; outcome text clarifies it. |
| Motion-off / pause | Motion-off showed salvage at7.8ms with no sampled retained battle frame. Pause/close completed salvage at1186.4ms. All tested terminal modes could skip reward and reach map. Manual motion-off arena screenshots were identical; OS reduced-motion screenshots also identical. | Tested on one browser/platform. Real assistive technology and target hardware remain untested. |
| Actual event target | Validated two-thrall fixture killed the sole binding then damaged hunter65→62. Actual slash-curve reconstruction produced27 sampled impacts at the exact virtual hunter aim; first impact remained on the fallen binding. Viewed the hound death pose and both targets. | Hunter has a portrait and virtual battlefield hit point, rather than a visible acting figure; impact on an empty point remains less clear than a visible hunter response. |
| Control / rally cues | Actual Silence made the chosen enemy's intent damage0; Pack Edict raised hound attack3→5. Rendered hound source cells remained idle, with no fake attack/reaction pose. Cue screenshots preserved. | Vague generic rings still offer less distinctive feedback than a fully authored control/rally effect. |
| Desktop density | All twelve unit panels remain inside roster bounds at1024×720,1280×720,1440×900 and1920×1080, with12px intents. Last binding keyboard command and hostile6 dossier worked. | Minimum-width occupied battlefield becomes small. Different named variants still reuse artwork. |
| Narrow layout | All panels/control names remain available at390×844. No document horizontal overflow in static metrics. | Page is long, hand scrolls horizontally, and full-occupancy figures are very small. Some narrow frame bounds extend beyond their roster, as in baseline. This is not polished phone play. |
| Art / canvas failure | Forced Canvas2D unavailable hid the illustration, displayed honest fallback text, kept6+6 controls and accepted a command. Aborted hound pose-sheet request fell back to the original companion image and still accepted a command. | Missing optional animation reduces presentation quality; no claim of complete asset/hardware failure coverage. |
| Hunter identity | Actual title/HUD portrait loads with no404s and remains recognizable; keyboard inspection opens Marek Voss dossier. | Naming and portrait do not complete character animation, narrative or audio production. |

### Cadence comparison

Clean final six-versus-six sample measured241 backdrop draws over4seconds, **60.06fps**, median16.7ms, p95 18.0ms, maximum20.2ms. Archived v0.2 comparison measured59.75fps, median16.7ms,p95 17.1ms,maximum43.8ms. This is consistent cadence with no observed degradation in this session; differences this small are not a meaningful optimization claim. Both used the same actual Canvas2D backdrop-draw method. The final window had no PNG probe, and the rig author/parent kept heavy Blender rendering idle. Headless measurements do not certify Steam Deck, minimum spec, VRAM, sustained frame pacing or native desktop behavior.

### Card treatment and the repaired finding

The dark text on parchment, separated cost and rules, and creature art crops support legibility. The card finish still feels generic next to the detailed wet abbey: clean flat beige areas, broad empty lower halves, and tool icons with little individual identity. Scour and Pack Edict both use the generic bolt despite different roles. Variant creature cards repeat the same portrait, reducing at-a-glance identity. Next polish should add distinct original tool vignettes and restrained aged ink/metal/edge treatment while preserving dark text and12px rules. Avoid decorative texture behind essential text.

An independent1440×900 inspection exposed Ember Widow/base+ attack/health stats clipped6.91px below the collection card. Archived v0.2 reproduced the exact same defect, so this is an inherited limitation discovered during v0.3 review, not an invented new regression. Parent authorized a narrow collection-only auto-height repair. Final measured name/rules/stats descendant bounds across all48 cards at1024/1280/1440/1920/390 show no bottom overflow. Viewed repaired1440 screenshot: Ember Widow's full stat line is visible. Preserve `card-containment.json`, `baseline-card-containment.json`, and `repaired-card-containment.json` to distinguish original finding and repair. The fixed collection uses variable card height, trading stricter uniformity for complete readable content; combat hand remains the existing size.

### Evidence limits and next review priorities

No human player session or enjoyment score was obtained. Audio was not independently heard and remains unrated. Automated model play and synthetic fixtures verify behaviors; they do not establish fun or sustained replay appeal. Native Steam publication, platform compliance, commercial readiness and full accessibility were not assessed here. One early terminal attempt overlapped the authorized CSS rebuild and failed navigation; it was discarded as a completed result and re-run against the frozen build. Its method note is preserved, rather than reporting a false gameplay bug.

For the next2.5D milestone, prioritize coherent floor/shadow depth and source-target contact, eliminate perceptible double silhouettes during pose blending, add authored adversary recoil/death poses, and bring the rest of the roster to the hound's action coverage. Distinct tool/variant art and tactile card/audio feedback should follow without weakening text or cadence. Verify formation transitions and retained death/replacement positions with direct actor-coordinate evidence; source inspection shows320ms layout interpolation and UID endpoint reconciliation, but this review did not independently reproduce every1/3/4/6 occupancy/contact case. These shortcomings prevent a whole-game AAA quality agreement. The isolated procedural rig is also rejected for runtime replacement above; adopting3D is not necessary for the accepted2.5D direction.

### Exact final hashes

Detailed before/after source and dist hashes are preserved in `screenshots-v0.3/candidate-recheck.json`. Final runtime identities:

- `src/main.ts` — `e39ff4c16dc8dcb164d42dad4e84f1190354876f27b220628dc7150b16531371`
- `src/style.css` — `18660c579ee97fe83570ba0e9c9e5deac7fb702fe7fe8c0be158f921d9855b6f`
- `src/arena.ts` — `ec0b44aadc869dbf3903f3c6c3d1d0ef96f2c00caed4c75c444be790250620ea`
- `src/art.ts` — `c8ecd30136abb54d865fa80e27649da0049db3c65f879cbfa2a80d2269a14d1d`
- `src/content.ts` — `2f45160b3e577a7cd44381cb361c4407661a68819ff827a24b8ab34ce15c4234`
- `src/engine.ts` — `4b24a1bd90a05326ec76db361001bf034af6f6ed0e5f86bcab295e9ae0a5f5af`
- `index.html` — `897357d797f5bd82b62dd5fcc37f3be04700f5091cd5f8c430daecc5102bdfc8`
- `public/art/hunter-portrait.png` — `28d4bdc56c434590ade5c9d69d650c35e284713fb14f45f37bad54190ea4e988`
- `public/art/hound-poses.png` — `0f363fb1a22fc6e8ce730eabcc19af7ce61a1c7fdc71d8e52860b0114efe4968`

Final distribution identities:

- `dist/index.html` — `5f71704b89a6e0045f33404223f63b78ac16293cf6c96bc90085cd8a85d02dd9`
- `dist/assets/index-B6l6m9CW.js` — `2d2d1fc5fdb101b62adb10e939fc5c3e404241e0ae16c751ae77ae1268cc8008`
- `dist/assets/index-C43KhXyK.css` — `51075876c82f03cd2f4e330428ecdc1cf4acbd03ef19b396e56cfdf266220faa`


### Observed mid-blend craft defect and report freeze

A separate read-only draw probe captured halfway transitions after the clean cadence sample. Viewed `blend-2.png`, `blend-3.png` and `blend-4.png`: at roughly47.6% current-pose alpha, both head/limb silhouettes remain visible and the creature looks briefly translucent. The70ms dissolve avoids a hard pose cut but weakens its physical presence. This is an observed craft defect, not a speculative skeletal-animation requirement. Dominant crouch/attack/recovery poses improve action direction over v0.2; those improved frames do not establish that every transition frame is superior. Preserve the captures and make solid silhouettes/intermediate painted motion a focused next comparison. `blend-review.json` records exact source cell/alpha and the constructed fixture's resulting state; PNG instrumentation was never used in the clean60fps sample.

Final independent report freeze is on runtime digest1ef47ce481c3f8722e624fe6df1540d2957462c20c8ba7213c77ed4583a7f258. Parent also disclosed an inherited Silence guard-label/save defect from a separate seed1989 investigation; this reviewer did not reproduce that case, and development acceptance here does not conceal or override that known rule/UI limitation. The next review should verify its repair before advancing contact/shadow depth and target previews. This review checkpoint is not a declaration that the game is complete. Commercial/AAA/Steam-ready promotion remains rejected; ongoing2.5D development continues through the parent-led next milestone.
