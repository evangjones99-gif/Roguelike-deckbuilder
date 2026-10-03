# Marek six-pose sheet: unshipped v0.7 art feasibility

**Recommendation: R3 is usable for a separately reviewed placement/animation prototype with full512-cell sampling, one uniform body scale and measured per-pose ground anchors. It is not accepted runtime art or an independent commercial/AAA gate.** R1 and R2 remain rejected framing attempts. R3 still fails the requested48px safe margin/common y448 groundline and the requested80% scale reduction. Do not describe those requests as achieved.

This implementation-side feasibility author inspected actual R1/R2/R3 and the existing hunter portrait, measured unchanged RGBA pixels with Pillow/NumPy/SciPy, and viewed actual Chromium Canvas2D captures. No runtime/public/source-art pixels were changed. All new files are scratch-only. Root owns generation/provenance and any future promotion. The separate hunter-placement researcher owns collision/event architecture; these artificial six-panel art boards do not establish production field fit.

## Provenance and rejected iterations

Inputs remain in `assets/art-sources/v0.7/`, including all three original image outputs, requests and root QC files. `hunter-sheet-inputs.json` records the portrait reference SHA28d4bdc56c434590ade5c9d69d650c35e284713fb14f45f37bad54190ea4e988 and courtyard SHA92230fee18818b49a813a50085ecb604b93f157173b994ffe53c520b726e99b3. The file explicitly marks generated rights review pending. This report does not establish clearance, human approval or release readiness.

| Attempt | SHA256 | Finding |
| --- | --- | --- |
| R1 original | 71d6a14abcc2ac97ae694d87110f94857f2508ecda0ebc8e9361b313b9094d46 | Head/boots insufficient cell margins; actual opaque pixels at horizontal cell border; idle head direction differs from the command poses. Retained rejected input. |
| R2 edit | 71bedf595a24b98a9bc1971150affe09f584aa9e35eaf4adaf6b19e3ecad65bc | Top-row boots still at y509/509/507 inclusive; ±4px horizontal boundary alphaMAX254. Requested448/48 geometry failed. Retained rejected input. |
| R3 edit | 4492577d3bacc868e9b66da0abf25915bdeaf68bc8f5c31ae8a1d8db485f3c53 | Fullcell containment repaired enough for sampled prototype. Requested48px margins/common448 and exact80% reduction still fail. |

All three are1536×1024 RGBA, alpha0..254. My bbox values are **inclusive** pixel indices. Root's earlier QC uses max+1 bounds; the apparent one-pixel difference is a coordinate convention, not altered PNG bytes.

## Actual containment and alpha

R3 boundary ±4px bands have alphaMAX1/0/1 at vertical512/vertical1024/horizontal512. All six cell outer8px bands have alphaMAX≤4 and zero pixels alpha>8. Meaningful bodies remain contained with full512 source rectangles, with no observed hand, hair, cloak, knee or boot cut at a cell boundary. No assertion is made that every alpha>0 pixel is artwork or that48px margins exist.

| Pose | Alpha>128 bbox inclusive [x0,y0,x1,y1] | Proposed boot/support bottom-edge y | Fixed anchorX |
| --- | --- | --- | --- |
| Idle | [106,84,379,501] | 502 | 256/512 |
| Anticipation | [69,97,433,501] | 502 | 256/512 |
| Command | [68,90,409,499] | 500 | 256/512 |
| Recovery | [78,45,389,449] | 450 | 256/512 |
| Reaction | [71,76,436,446] | 447 | 256/512 |
| Exhausted collapse | [48,173,463,440] | 441 | 256/512 |

The source>8 bounds are wider: recovery head reaches y42, collapse x46..464; top boots reach y502. Do not crop the proposed sheet to48..464 or align all frames at448. That would cut top-row boots or produce roughly13px foot-plane error at a100px standing-body height. The measured top-to-recovery offset52sourcepx becomes12.44px at100px or27.37px at220px if ignored.

The image tool's dark smoky backdrop was misleading: sample hidden RGB at[256,60] is[32,24,24] with alpha0; it disappears in real Canvas2D. `r3-full.png`, `r3-white.png` and abbey captures show no opaque rectangular background or broad dark haze. Distance-to-alpha>128 analysis finds no alpha>8 pixels more than8sourcepx from any opaque silhouette, and alphaMAX≤1 beyond16px. There are a few soft-edge pixels several pixels outside opaque hair/cloth; I did not erase them. Warm light at the material edge is painted illumination, not established as a removable halo defect.

## Uniform scale, body and identity assessment

Use the same sourcecell scale for every frame: **cell size = target idle body height ×512/418**. Do not separately normalize shorter pose bboxes: that would enlarge bent/collapsed anatomy. At100px idle height, fullcell size is122.49px; actual meaningful widths range65.55px idle to99.52px seated collapse. At160px the collapse is159.23px wide. This matters for formation occlusion even when a neutral placement marker fits.

Opaque bbox heights idle/anticipation/command/recovery/reaction/collapse are418/405/410/405/371/268sourcepx. Recovery/anticipation are3.11% shorter than idle; reaction is11.24% lower from bent knees/spine and collapse35.89% lower. These are projected stance differences, not proven skeletal scale factors. R3 height proxies fell only2.4–3.9% from R2, rather than the requested20% reduction. A20px band below each head's first opaque pixel spans63/67/66/64/69/62px of hair/face silhouette. This11.3% range is also confounded by head turn/tilt; it does not prove exact anatomical consistency or justify per-pose resizing.

Viewed at fullsize and common3× sourcepx head inspection:

- The six cells retain recognizable dark tousled hair, short beard, stern weathered face, ragged charcoal cloak, shoulder-side layered iron pauldron, knee plates, leather belts, knife/vials and held pact seal. Idle/recovery head shape is especially close. Anticipation's cheek/jaw looks slightly fuller, command slightly leaner, but no visibly different person appears. The portrait's precise cheek scar is not reliably legible at100px fullbody; do not claim pixel-exact portrait identity.
- Idle head now turns rightward and matches the action profile. Command's head/torso shifts left within the wide stance while its arm points right. The top20px head center shifts approximately59sourcepx from idle to command (~14.1screenpx at100px). Foot anchors alone do not make that instantaneous cel transition smooth; this is a visible motion risk for the animation gate.
- Armor/material direction remains coherent: dark layered leather, worn segmented pauldron on the same rendered shoulder, chainmail neckline, warm edge light compatible with the courtyard. Small belt/seal details vary under hand/angle changes, so these are generated painted poses rather than a shared modeled body/equipment topology.
- Reaction uses a lower defended crouch with knees apart, hand/forearm guarding the face and the seal retained. It reads as impact protection; no apparent stretched limbs or amputated boots. Without intermediate frames it cannot demonstrate weight transfer or physical hit contact.
- The seated pose preserves both footwear silhouettes and an intact bent body. Lowered head, grounded glove and bent legs read as exhaustion/incapacitation rather than an unambiguous lifeless collapse. That is usable for a non-graphic defeat tableau if presentation communicates it, but unsuitable as proof of a convincing fall/death sequence. The nearer boot defines y441; glove/hip supports are further back on a perspective plane, not necessarily at identical image-y.
- At100px, pointing versus recoil versus seated defeat remains distinguishable and silhouette/metal warm edge remains readable. Fine scar, hand digits and small equipment become impressionistic; photographic close-up clarity is not retained.

## Observed rendering and limits

`capture-evidence.json` records8 Chromium151.0.7922.173 actual Canvas captures, zero page errors: R3checker fullcell, white, abbey220/160/100px, incorrect common448 comparison, and retained R1/R2 abbey boards. Figures use unchanged sourcecells, ordinary Canvas source-over and one shared scale. Artificial local radial floor shadows and a gold ground reference are diagnostic presentation layers, not baked source artwork. `r3-head-details.png` samples heads at common3× source scale for inspection only; `failed-head-inspection-crop.png` retains my initial wrongly framed command-head inspection, superseded by corrected head sampling. Neither crop is a proposed runtime atlas crop.

The hunter-placement agent separately measured substantial opaque overlap in its **uncapped** actual12-creature field prototype (reported41.5% of one stalker during command in1024 scene). Those production-layout negatives must be resolved and independently checked before promotion. My100px artificial board is not acceptance of that placement or scale. Wide/short/mobile, ranged/physical event anchors, painter-depth occlusion, supported floor perspective, temporal continuity, reduced motion, terminal defeat and fallback all remain runtime gates. No cadence, battery, target hardware or gameplay/save-equivalence claim follows from this art-only fixture.

This assessment supports continuing an isolated prototype with measured metadata. It does not require approving R3 if independent runtime review finds weight, identity, readability or occlusion inadequate. Higher craft still requires better motion inbetweens/authored contact, temporal staging and independent actual-production review.

## Preservation

Frozen runtime hashes observed during this scratch work: arena4cfa90a38f10b270867683940400cfb1ca954a3aaf773b6c469e5cca1bab13e1; art26b515016ecf52996acf91ae704da608224d2d1475a883f9675aa0079abbfb1c; enginebfc9e61299d73a344569e54e4b3f3348009f4075560dc2f0fb057f5d8a4d296b. This task did not write those files. `HASHES.sha256` freezes all review outputs and `sources-hashes.json` records unchanged source/provenance/reference bytes; manifest itself is excluded from its own list.
