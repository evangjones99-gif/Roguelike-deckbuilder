# Independent visual and accessibility review — Hollowpact v0.2.0 candidate

Status: complete on the repaired frozen production candidate. Accept development-prototype preservation; reject commercial/AAA/Steam-ready promotion. Independent reviewer may reject promotion. No human fun endorsement or AAA claim is made.

## Target and method

The requested target is a grim, realistic monster hunter game with craft comparable to strong commercial releases. Detailed illustrations alone cannot establish that standard. Review covers consistent character identity, anatomy/materials, lighting, action feedback, animation, readable tactics, accessibility and measured rendering behavior.

Independently used system Chromium on Linux through Playwright against the production preview at localhost:4173. No WebGL flags are needed by the new Canvas 2D renderer. Executed `screenshots-v0.2/review.mjs` with Node/tsx: actual seed 121 UI play, tutorial/map, first battle, keyboard summon/command, inspection/deck dialogs, settings, four viewport sizes and battle completion. Captured and actually viewed title, initial/summoned battle, targeting, four sequential attack captures, death/settled captures, desktop 1280/1440/1920 and narrow 390 layouts, deck and dossier.

The first battle reached reward in two turns after the first summon/command and twelve further accepted actions. No uncaught page errors or failed HTTP responses appeared. Source hashes were identical before/after that review. That is a short real UI battle, not a complete campaign playtest or a fun rating.

A second independent script, `stress-review.mjs`, loaded a constructed save accepted by `validateState` with six allies, six enemies, enhanced hand cards and all 48 base/enhanced card definitions. This is deliberate visual stress, not a naturally reached player state. Captured/viewed full occupancy at 1280×720,1440×900,1920×1080 and390×844; all-card deck modal and disabled-canvas fallback. The fixture and JSON observations are retained.

Video capture was attempted, but Playwright's ffmpeg helper is absent; no video-quality or full-motion playback claim is made. Sequential screenshots and renderer/source observations support the narrower animation findings below. Attack captures were obtained about247,536,922 and1594ms after keyboard activation, not exact nominal animation keyframes. Audio source was inspected but not heard; sound quality is unrated.

## What improved

The richly detailed wet abbey courtyard, broken architecture, cold distance and localized brazier warmth support the requested grim tone. Creature silhouettes and material treatments now convey plated flesh, bone, torn cloth, chitin and bark instead of the former friendly geometry. At 1080p the enemy and companion art reads clearly against the environment; it is a meaningful visual direction improvement.

The same atlas cells supply battlefield figures, side portraits and binding cards. This repairs v0.1's cross-surface identity mismatch. Four companion family illustrations and four adversary illustrations are shared across variant cards/foes; the game does not contain an independently illustrated model for every named variant. The inspected registry and art-direction document accurately describe that reuse.

Commands have a directed trace, translation lunge and received-hit recoil; removed enemies fade/leave particles rather than disappearing immediately. In the four sequential captures the hound shifts toward the opposing side and returns. Death/settled captures show the defeated spectral foe disappear while its surviving enemy stays in position. These effects are an improvement over v0.1, with the craft limitations below.

Desktop tactical effects/intents remain12px; narrow effects/intents are11px. Tested card text boxes and all48 deck entries had no detected vertical overflow. The inspected small dossier gives readable traits/binding rules. Keyboard Enter selected a ready creature, focused a named valid enemy and commanded it. Native Escape closed dialogs; mobile tools retain Deck/How to play/Settings names. Forced Canvas2D failure displayed a notice while all six companions/enemies remained available in HTML; a keyboard command still marked the companion acted.

Motion off yielded byte-identical canvas captures250ms apart and zero actual arena draws during an additional idle250ms. This suppresses effects without losing rule outcomes.

## Remaining findings

1. **Commercial blocker: animation and action craft.** Each creature has one illustrated pose. The renderer translates/scales the entire image, with no limb, jaw, weapon, cloth or locomotion articulation. Attack bodies glide rather than execute grounded strikes; received hits shake the cutout; death rises/fades. These are transformed illustration effects, not convincing creature animation. A professional illustrated game can use limited animation, but this implementation does not yet supply its needed pose variety, anticipation, contact, impact and recovery. Do not describe it as rigged3D, realistic movement or AAA quality.
2. **P2: initial rendering cadence defect, repair authorized.** Instrumented actual arena `drawImage(backplate)` calls over1500ms measured32draws,21.62fps,median49.9ms andp95~50.2ms gaps. The source's strict `dt>=1/30` gate reset its timestamp every draw, plausibly quantizing60Hz callbacks into50ms intervals. The observed cadence is below the intended30fps and visibly limits short effects. Parent authorized a repair; original evidence is preserved in `inspection.json`. Final remeasurement pending. This Linux browser sample is not a minimum-spec, GPU, Steam Deck or hardware certification.
3. **P2: high-occupancy tactical information hides in scrolling rails.** At1280×720 each roster was278px high with686/701px content; only about2.5 of six occupied panels were initially visible. At1920×1080 the larger rails still hid later creatures/intents. The last creature can be reached with keyboard focus, so commands are accessible, but assessing all enemy plans now requires scrolling each side. Compared with v0.1's all-six visible roster, this is a tactical presentation regression. Add a compact high-occupancy layout or complete visible intent summary. The narrow three-column/two-row layout does show all six.
4. **P2: formation and outcome transition coherence.** Summoning a fourth unit instantly switches both parties from staggered positions to horizontal rows. This makes bodies jump to new locations during a tactical action. Source schedules strike endpoints using pre-action positions before the formation change, so effects already queued can remain aimed at earlier positions. This endpoint concern is source-derived; I did not isolate a single wrong-target impact in slow-motion playback. On the final kill the UI switches immediately to the reward panel, concealing the terminal death animation. Sequence the visual outcome while keeping rule state deterministic.
5. **Commercial craft gap: contact, lighting and identity variation.** Detailed single images retain their baked highlights. They do not react to the abbey lights, occlusion, damage or motion; whole-image contact shadows remain generic. Named family variants and regular enemies/bosses share art. These choices are honest prototype shortcuts, but they limit embodied realism and roster memorability. A defined character/animation pipeline and human art direction are needed before the requested quality claim.
6. **Accessibility/product gaps.** No in-game text scale, contrast mode or controller path was tested or found. The mobile battle is about1255px tall on an844px display, separating cards from enemy plans through page scrolling. Narrow support is functional, but not a polished single-screen handheld combat layout. Screen-reader speech,200%browser zoom, alternate-color perception and real Steam Deck operation remain untested. Settings still describes the new gritty effects as "Soft, synthesized notes"; update the wording to match the product.
7. **Feedback/aesthetic limitations.** Tool cards still use generic symbols rather than individual art. The menu is a clean typographic panel without a character/world hero presentation. These can suit a restrained direction, but they do not demonstrate a complete commercial identity. The audio implementation layers tones/noise and ends its sources, but without listening or player observation it cannot be judged tactile, well mixed or enjoyable.

## Preliminary verdict

Acceptable as a clearly labelled development prototype if the final repair/build checks pass. Reject promotion as a high-quality commercial, AAA or fully Steam-ready release. The visual direction is substantially closer to the requested grim setting; satisfying that preference is not proof of the requested craft level or human fun. The most valuable next work is grounded multi-pose/rigged action, coherent formations/terminal feedback, full visible tactics at high occupancy, and independent prospective-player sessions.

Do not average away these findings or replace this report with praise when later versions improve. Preserve v0.1 and each candidate's evidence.


## Initial frozen evidence identities

Source and build below identify the initial reviewed candidate, before the subsequently authorized repairs. Final repaired identities will be appended separately.

| Source | SHA-256 |
|---|---|
| src/main.ts | 8a7700763ad6872d6fedade008330e28bae22da29611bf6226422746e285a324 |
| src/style.css | 166105cdd658b8d6fa331d90af9b13777c522fe2c4a9c4fa0dd2b4f3131478de |
| src/arena.ts | 61e8e03ddbd02ed139ac05d95aa191bc66f8a4d09fc445d041397b36fcf77f91 |
| src/art.ts | 3127ed46b8ec4aecbcc8218c8a78ded3e3f57c922d04b330c7f8fe0c51be1e85 |
| src/content.ts | 2f45160b3e577a7cd44381cb361c4407661a68819ff827a24b8ab34ce15c4234 |
| src/engine.ts | 21bafb33832ec2d3ee1ca4ead9486825510bd380b62e143a8736465f1ad4110b |
| index.html | fa9d21cc9c38a02bb08485df2303ada2880648a5e62c363784a97e8f8532764c |

| Production build | SHA-256 |
|---|---|
| dist/index.html | 956e4c94d506d95d41e3625b080d32d753b2c69c195015d47565cc9321faa82b |
| dist/assets/index-BRMqMSVy.css | 28f87cdb0f3ceed742e2c32310345b259753a30ef4547f7467e1b9a835064293 |
| dist/assets/index-CZGG71EA.js | 855e7f6e1d0fe8c2552fa802f3c339ec6e7fbb64ee964a404fdd999b5233b9e8 |

All local generated images have per-file records and hashes in `public/art/PROVENANCE.json`. I inspected that file and the rendered artwork. It correctly labels the presentation as illustrated2.5D and marks commercial rights review pending. I did not independently inspect the full generation conversation or complete a legal review.


## Independent repaired-candidate recheck

Ran `node --import tsx reviews/screenshots-v0.2/final-recheck.mjs` against the refreshed production preview. Source and build hashes were identical before/after this session. JSON is `screenshots-v0.2/final-recheck.json`; final screenshots use the new `final-full-` prefix so the rejected initial rail presentation remains preserved.

I actually viewed the final full-occupancy captures at1024×720,1280×720,1920×1080 and390×844. All twelve occupied panels now fit inside their respective desktop rails at1024,1280,1440 and1920 widths. Intent text remains12px, and the tested fixture has no measured horizontal or vertical intent overflow. Compact rows expose name, slot identifier, health, attack and intent. Keyboard commanding the last ally still works; its last-slot enemy inspection opened `Ironjaw Warlord · hostile6`. This resolves the specific desktop tactical regression. The initial scroll-hiding finding is historical, not an outstanding desktop blocker.

Rendering cadence materially improved:236 actual arena draws over4000ms,58.99fps,median16.7ms,p95 32.6ms,max39.3ms. This six-versus-six sample supports smoother presentation than the initial21.62fps sample, but it is not a hardware performance guarantee and the observed long gaps still warrant profiling on declared targets. Motion off remained byte-identical across captures250ms apart. No uncaught page errors occurred.

At390px, lower rows extend several pixels beyond their roster section bounds. The final screenshot visibly retains the panels, rather than hiding them in the former desktop scroll rails. Some narrow titles/slot badges wrap, and scrolling still separates cards from enemy information. Treat this as unresolved portrait-layout polish; it does not invalidate the minimum1024×720 desktop verification.

I inspected the repaired arena source: pending strike origins/targets are now recomputed by unit ID after formation reconciliation. That addresses the stale-coordinate code path reported above. The arena author also records a dedicated fixture for it; this review does not claim an independent slow-motion target-coordinate measurement. Instant formation rearrangement itself and the immediate final-kill reward overlay remain unresolved animation polish.

### Final identities

| Source | SHA-256 |
|---|---|
| src/main.ts | 9fe8938578533af5896ccfcabef86dff5986a44e8ea6f949417a596d4aa39a7d |
| src/style.css | ee165e5cbaf5a8022f271fd61782b026d4d5610d964a965480ac882802d08716 |
| src/arena.ts | bff20f7b8e91ae17316142ac9185bfebe9c9de2b994a102570726e5a4734046b |
| src/art.ts | 3127ed46b8ec4aecbcc8218c8a78ded3e3f57c922d04b330c7f8fe0c51be1e85 |
| src/content.ts | 2f45160b3e577a7cd44381cb361c4407661a68819ff827a24b8ab34ce15c4234 |
| src/engine.ts | 21bafb33832ec2d3ee1ca4ead9486825510bd380b62e143a8736465f1ad4110b |
| index.html | 897357d797f5bd82b62dd5fcc37f3be04700f5091cd5f8c430daecc5102bdfc8 |

| Production build | SHA-256 |
|---|---|
| dist/index.html | 0570a856abe24dd2255ea89ad3d3334e42ec7471d799f65445911d27c1ec2c6c |
| dist/assets/index-C4TLZn37.js | 43b79a82e7b14f93cb670f1e9a8aaa6a5bb0973ab69bac0302e1b2e81c3e4260 |
| dist/assets/index-D74h-cbs.css | 5a1672d8a51273e8fcb1239b954899b1e3189ab300661ccb9e425ac0b62fbb89 |


### Independent craft judgment

| Dimension | Finding |
|---|---|
| Grim tone and environmental illustration | Strong prototype direction; substantial improvement toward the requested setting. |
| Character identity | Consistent card/portrait/arena families, but single poses and shared variant art limit differentiation. |
| Tactical readability | Desktop high-occupancy regression repaired and independently verified. Portrait/scale/contrast coverage remains incomplete. |
| Animation and combat outcome craft | Below requested commercial standard: transformed cutouts, abrupt formation changes and terminal feedback hidden by rewards. |
| Performance | Specific cadence defect repaired; roughly59fps measured in one headless six-versus-six sample. Broader platform budgets unverified. |
| Audio | Source inspected; not heard. No professional sound-quality endorsement. |
| Human enjoyment/purchase appeal | Unrated. No prospective-player evidence. |

**Final verdict: accept v0.2.0 as a preserved, clearly labelled development prototype. Reject high-quality commercial, AAA or fully Steam-ready promotion.** The practical readability and cadence repairs are meaningful, and the detailed grim art is a substantial stylistic advance. They do not supply convincing articulated action, grounded contact/recovery, complete audio direction, polish across declared platforms or human fun evidence. Highest next priorities are a real pose/animation pipeline, sequenced final-kill feedback, coherent formation transitions, distinct family variants and observed prospective-player sessions. Preserve this report and both pre-repair/repaired evidence with the release.
