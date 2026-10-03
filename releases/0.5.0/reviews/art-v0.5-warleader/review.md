# Independent warleader source-art gate

**Accept for a limited integrated runtime test. Do not treat this as final animation, AAA, commercial or whole-game approval.** No runtime source was changed by this review. The next production review must still assess genuine contact, death timing, full formations, missing-art fallback, reduced motion and frame cadence.

## Actual source and reference

Exact supplied image `/workspace/generated_images/exec-89b6ca1f-8b80-42b9-89ef-664d4bcfeaa5.png` is 1536×1024 RGBA, SHA256 `3f8c88d72c4efafbba75e7dfa61ba10f04ec4fa11384008e2381edfbce02353b`. `source.png` here is an unchanged byte-for-byte evidence copy. The requested `public/art/adversaries.png` filename does not exist; I compared the intended top-left figure in actual `public/art/adversaries-atlas.png`, SHA256 `5d0ad1963acce4a93e6456d73a840f34d104e2d5b33c82fb491cfcb873801ea5`, and read `docs/ANIMATION-v0.5-DESIGN.md`.

I viewed the entire actual sheet, reference atlas, all six source-sized cells composited over the abbey, matched nominal-size comparisons, and explicit stationary attack/death/recovery samples. Chromium/Playwright rendered `prototype.html`; no original art pixel was edited. Read-only Pillow alpha/bounding-box inspection is recorded in `source-inspection.json`. This is anatomical/crop review, not an independently tested game animation. A six-key sequence cannot establish smooth articulated motion.

## Identity and threat

The skull-like metal mask, pale scarred arms, angular plate, skull belt, ragged red cape and broad chopped axe remain recognizably the original warleader. The figure stays heavy and hostile rather than a cute goblin or rounded toy. The overhead wind-up, forward low chop and chest/head recoil are distinct readable poses. A prone torso, bent legs and dropped/grounded weapon are a materially better death source than rotating or fading the standing picture.

Armor highlights and scarlet cloth are brighter than the original muted weathered art; tiny armor/scar details also shift between keys. At composited game size I did not see a dominant baked background rectangle or halo, but this does not certify every blend, lighting setting or scaling filter. Recovery is close to the idle silhouette rather than a rich controlled follow-through. Death is one collapsed key, without an authored fall. Integration must retain those limits honestly.

## Crop, scale and grounded landmarks

Use the same full-cell source crop in all six poses: **x0,y32,width512,height448**. Use **one uniform scale1.10**, preserving the crop's 512:448 aspect; no horizontal stretching or per-pose growth. A standing head-to-nearest-boot span of roughly347px gives `347/448 × 1.10 ≈ .852` of nominal figure height, close to original `536/627 ≈ .855`. This checks broad scale, not anatomical exactness.

Common full-cell anchorX256; normalized cropped anchorX0.5. Recommended ground planes are manually judged from body/boot contact, not alpha-box bottom:

| Pose | Full-cell groundY | Cropped normalized anchorY | Inspected support |
|---|---:|---:|---|
| Idle | 474 | 0.986607 | Nearer boot sole around(190,472); far boot around(352,466) |
| Anticipation | 473 | 0.984375 | Bent loaded stance; nearer boot around(156,469), far boot(361,468) |
| Attack | 476 | 0.991071 | Leading boot around(100–125,472); far boot(353,464), torso and cleaver lower forward |
| Recovery | 406 | 0.834821 | Nearer sole(192,401–404); far sole(351,398–400) |
| Reaction | 405 | 0.832589 | Nearer sole(175,400–403); far sole(362,397–400) |
| Death | 406 | 0.834821 | Side/forearm/gauntlet/body plane around399–405; rear boot is higher in depth around384–393 |

Coordinates are approximate authored landmarks; foot contact spans a surface rather than one mathematically exact pixel. `capture.json` retains inspected point markers and source rectangles. Recovery/reaction are painted about70px higher in their cells; their own anchors correct the source translation while preserving common scale. These are grounded attack keys, so don't invent an airborne altitude solely because the cleaver is raised.

For death, alpha≥200 reachesY415 primarily at the dropped blade. **Reject the tentative groundY416 as an automatic body anchor.** It leaves extra empty space beneath the forearm and body. Y406 produces a stronger apparent body-floor relationship in the actual composited sample. The blade can project slightly below the main body plane as a nearer item; it is not the body's support point. A future posed shadow should cover the laid-out body footprint, not a standing-body ellipse.

## Gutters and clipping caveats

Clean equal-grid separators do not fulfill the requested32/64px safety margins. At alpha≥200 the corpse starts at localX7; faint alpha startsX1. This misses the requested left gutter even though the viewed body is not visibly chopped at the cell edge. The full-width crop preserves this cape/boot extension; an x32,width448 crop would visibly cut the corpse and other wide shapes. Keep the exact delivered pixels and document the exception. Source alpha thresholds and outer-edge maxima are retained rather than describing the sheet as universally clean.

The chosen vertical crop endsY480. Significant solid body/weapon pixels fit within it; some faint haze outside the crop is excluded. Final rendering still needs explicit no-neighbor-bleed checks under actual mirroring/scaling, especially the corpse's small left margin. This exception is acceptable only for a limited test, not a reason to skip runtime QA.

## Evidence integrity and reproduction

Serve project root on local5185 and run `node reviews/art-v0.5-warleader/capture.mjs`. The source-sized cells include manual contact markers and source-relative blue ground lines. The battle comparison puts original and candidate at the same175 nominal figure size; no runtime camera/formation simulation is implied. Explicit key screenshots record the actual selected pose in `capture.json`, with no page/request errors.

An initial wall-clock screenshot sequence captured after its intended key because screenshot calls consumed time. Those three files remain clearly labeled `timed-probe-unreliable-label-*` and are excluded as timed pose evidence. The valid `key-*` images use an explicit stationary pose selection. No source-gate image or HTML proves a240ms runtime contact or natural-paced smoothness. Those remain next production-review gates.
