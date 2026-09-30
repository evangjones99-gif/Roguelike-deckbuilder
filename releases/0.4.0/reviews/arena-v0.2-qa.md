# Arena v0.2 implementation QA

This report is the arena implementer's own verification, not an independent review or an approval of commercial/AAA readiness. The independent visual reviewer separately evaluates the integrated game. All fixtures below are synthetic visual states; they do not test combat balance or a complete run.

## Candidate and artwork identity before cadence repair

- `src/arena.ts`: SHA-256 `61e8e03ddbd02ed139ac05d95aa191bc66f8a4d09fc445d041397b36fcf77f91`.
- `src/art.ts`: SHA-256 `3127ed46b8ec4aecbcc8218c8a78ded3e3f57c922d04b330c7f8fe0c51be1e85`.
- Abbey: `92230fee18818b49a813a50085ecb604b93f157173b994ffe53c520b726e99b3`.
- Companion atlas: `1a59f11b0d3829921beeea823b6b148b9308f94d29cb4956c43d2bf9798290c5`.
- Adversary atlas: `5d0ad1963acce4a93e6456d73a840f34d104e2d5b33c82fb491cfcb873801ea5`.

Runtime rendering samples the original local atlases through source rectangles. It does not edit the image files. The arena is illustrated 2.5D: painted full-body cutouts, ground shadows, small scale changes, directed translations, spell/slash effects, and fade/ash effects. It has no articulated creature rigs.

## Method and observed results

Initial implementation QA used system Chromium through Playwright with `--no-sandbox --disable-gpu`. A twelve-figure fixture at 1280×540 CSS pixels, device scale factor 1, exercised the canvas independently of the game UI. Sixty draws, each followed by `getImageData(0,0,1,1)` to force raster readback, took 98 ms in the earlier run: **1.63 ms average**. That earlier measurement preceded the stable-death-slot correction.

The repeat on the candidate hash above used Chromium **151.0.7922.173**, the same GPU-disabled flags and dimensions, and ran on 30 September 2026 at 18:29:29 UTC. Sixty forced-readback draws took **134.8 ms**, or **2.25 ms average**. These are local synthetic measurements, not a target hardware frame budget, minimum hardware certification, full-game frame rate, or evidence of 60 fps.

The frozen-source repeat verified:

- Manual reduced-motion snapshots, taken 200 ms apart, were byte-identical.
- Motion-on snapshots differed.
- Calling `dispose()` stopped arena RAF callbacks.
- Calling `playAction()` and then `render()` plus an unchanged-size `resize()` retained directed attack presentation.
- Deaths retained survivor slots, leaving the victim's fade visible instead of sliding another unit over it.
- Twelve full-body figures could be displayed without overlapping party members completely.
- Browser exception list was empty.

Raw repeat results: [fixture-checks.json](arena-v0.2-screenshots/fixture-checks.json).

Earlier browser fixtures exercised mobile 390×300 rendering. The final formation-repair check below adds a current mobile image and a missing-2D-context fallback fixture. These are implementation checks, not broad device compatibility coverage or a complete-game graphics-failure playthrough.

## Preserved screenshots

| Artifact | Dimensions | SHA-256 | Scope |
| --- | --- | --- | --- |
| [duel-original-qa.png](arena-v0.2-screenshots/duel-original-qa.png) | 1100×480 | `a3afc1b88ddbfb7f2d226e0f28ad5afaa3a4b27fa43ed4b8cd4c891a617ca32b` | Earlier corrected four-body opposing-side fixture; captured before stable death slots. |
| [twelve-original-qa.png](arena-v0.2-screenshots/twelve-original-qa.png) | 1100×480 | `dd23ee272e7656755e779f9ac5ccce41c9fe4653b9b3b1b2198328d1ee200499` | Earlier corrected crowded formation fixture; captured before stable death slots. |
| [reduced-a.png](arena-v0.2-screenshots/reduced-a.png) | 1280×540 | `8da5cf2e882d2d6ff016b7b387716e5d98adf477cd9e5579d525533f5ba708d6` | Candidate hash above, twelve figures and selected binding. |
| [reduced-b.png](arena-v0.2-screenshots/reduced-b.png) | 1280×540 | `8da5cf2e882d2d6ff016b7b387716e5d98adf477cd9e5579d525533f5ba708d6` | Same scene, 200 ms later. |
| [directed-impact.png](arena-v0.2-screenshots/directed-impact.png) | 1280×540 | `c354c86f1b2bbac83c88af12e0d1f3b36033a468a48091504473fb9b0ca0f954` | Candidate hash above, command from UID 0 to UID 6. |
| [death-fade.png](arena-v0.2-screenshots/death-fade.png) | 1280×540 | `b5f768ab5c45dcee91f02fdc3e720f2a805f27b06c6e99488dcfa18f224c983d` | Candidate hash above, UID 6 removed from the rule state. |

These canvas fixtures do not prove integrated roster alignment, controller support, Electron/file URL behavior, or release package provenance. Separate browser/native/package reviews cover those areas.

## Independent finding and authorized repair

The independent visual reviewer reported **32 integrated draws over 1500 ms, approximately 21.62 fps**, with p50 gaps 49.9 ms and p95 gaps 50.2 ms. The `dt >= 1/30` gate reset its timestamp on each draw; ordinary RAF timing could therefore quantize the intended 30 Hz loop to approximately 20 Hz. This finding belongs to the independent reviewer, not the implementer benchmark above.

The lead explicitly authorized a cadence repair within the unreleased v0.2 candidate and will rebuild and recheck affected packages. The pre-repair evidence and hashes above remain intact. Repair measurements will be appended below.

## Remaining production limits

The art direction is a significant change from v0.1's cute low-poly look. That aesthetic judgement does not certify fun, release readiness, or AAA craft. Painted bodies still translate as flat cutouts; multiple attack poses, articulated animation, richer hit readability, animation transitions, and broader hardware testing remain future work. Synthetic average draw costs omit UI work, asset-loading spikes, other system load, display refresh variation, and target-device differences.

## Cadence repair verification

The authorized repair removed the strict 1/30-second gate. The arena draws on every RAF and advances its presentation clock with a time step bounded to 50 ms. Reduced-motion and document-visibility guards still cancel scheduling; disposal still disconnects observers and stops callbacks.

Post-repair `src/arena.ts` SHA-256: **`31b388d6ce05d29f9a11fd1fa0bbeb3ce43d137dad148ecbac061226f7194c97`**. Shared `src/art.ts` and all source artwork hashes above remain unchanged.

Own verification at 18:32:38 UTC on 30 September 2026 used the same Chromium version, GPU-disabled flags, twelve-figure fixture, 1280×540 viewport and device scale factor 1. Instrumentation counted the actual `ctx.drawImage(backplate)` calls, rather than counting scheduled callbacks. Over 1500.1 ms it observed **90 draws, 60.00 fps**, p50 gaps **16.7 ms**, and p95 gaps **17.1 ms**. This fixes the measured quantization in the synthetic fixture; the independent reviewer must separately check the integrated production UI.

The same repeat verified:

- Reduced-motion screenshots taken 180 ms apart remained byte-identical.
- Motion-on screenshots differed.
- The hidden-document control flow produced zero draws during a 150 ms window. This was a simulated `document.hidden` getter plus `visibilitychange`, not an actual background-tab or OS suspend test.
- `dispose()` stopped draws.
- Sixty forced-readback draws took **109.3 ms**, averaging **1.82 ms**. Variation against the earlier 1.63 ms and 2.25 ms runs is retained; these averages still are not target-hardware budgets.
- No browser exceptions occurred.

Raw repair results: [cadence-repair-checks.json](arena-v0.2-screenshots/cadence-repair-checks.json).

The [repaired first snapshot](arena-v0.2-screenshots/repaired-reduced-a.png) and [repaired second snapshot](arena-v0.2-screenshots/repaired-reduced-b.png) are both 1280×540 PNGs with SHA-256 `4f49faede951d16480c27a7697d7f2dba0496e9d6096ad58e14a3da237037850`.

The repaired hash is handed to the lead for package rebuild and affected independent browser/native checks. This report does not attest to the earlier package digest or claim those packages contain the cadence repair.

## Formation endpoint repair and final arena hash

The independent reviewer found that adding a fourth companion could switch the formation while a pending strike retained its former screen coordinates. The lead authorized a repair before freezing the candidate. After each layout reconciliation the renderer now resolves every pending strike's source and target through their unit UIDs again. Retained death figures remain valid visual targets. No reducer timing or game state changes were introduced.

Final arena SHA-256: **`bff20f7b8e91ae17316142ac9185bfebe9c9de2b994a102570726e5a4734046b`**. This supersedes the cadence-only arena hash above; the earlier findings and measurements are intentionally preserved. Shared art and source artwork remain unchanged. TypeScript compilation passed.

Own verification at 18:36:49 UTC instrumented the actual canvas path commands in a synthetic sequence: command UID `a0` against UID `e0`, retain that pending presentation, then add a fourth companion through `playAction()`/`render()`. At 1100×480, the observed post-formation attack source matched **(220, 363.168)**. The subsequent physical impact curve resolved to the new target center **(366.6667, 180.048)**. Both checks passed against the expected updated formation positions; the strike was not canceled merely to hide the mismatch. This is geometric fixture evidence, not a full game interaction test.

- [Formation repair raw results](arena-v0.2-screenshots/formation-repair-checks.json).
- [Remapped impact fixture](arena-v0.2-screenshots/formation-remapped-impact.png): 1100×480, SHA-256 `48815f3249b4e257284513bbdfdfa6664e45782246dfd938c9dea3c46fea2bfa`.
- [Current mobile fixture](arena-v0.2-screenshots/repaired-mobile.png): 390×300, SHA-256 `4492cab2f0f64e565e7e4d551b773a25140810e9962c43cb0ad97d3e1ee8f343`.

A separate forced-null `getContext()` fixture verified the fallback status appeared, the canvas hid, an existing HTML button continued to respond, and `dispose()` removed the status. That button fixture does not certify a complete playable run after real graphics failure.

One independent presentation finding remains: the final killing action moves the UI immediately to its reward overlay, which can mask the arena's death effect. The lead accepted this as documented follow-up work for this candidate. Any future transition should preserve immediate reducer/save correctness and reduced-motion behavior while allowing the impact to be seen. The other stated production limits, especially flat cutout motion and the lack of articulated rigs, still apply.
