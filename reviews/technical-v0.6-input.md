# Independent v0.6 input integration — initial gate

Decision: **withhold promotion of this initial integration pending the agreed composition/lifecycle repair and final affected-build recheck.** The held-key, focus recovery and safe terminal-pause changes work in the exercised actual production cases. A new adapter composition boundary is incomplete. Visible-window suspension needs hardening, but a real native background-command failure was not established. This is a provisional development source gate, not a commercial/AAA/controller hardware approval. No implementation was changed by this reviewer.

## Inspected identity

Actual production digest `d33ce538e38d98eba6ec06f90660252d53d3f3fc0122c7316b229f043489b52c`, version0.6.0, server4173. All **27** provenance entries match their current source files, and independently recalculated compact ordered-map digest matches. Compared with preserved v0.5 web provenance, only package/lock versions, main integration and new input module differ; engine/content/world, arena/art/tool renderer, CSS, public images/provenance, desktop shell and credits are unchanged.

- Main SHA256: `dba47ae29bca37d099d04fd0d3d2bcb05948d4d7426b5ab7a331448206d46496`.
- Input SHA256: `4ae4ca1a2dadb41f3a51b8eba35dd41efed5ececb00d912edfbec2e346f9f69d`.
- Decoder tests SHA256: `6bf30c09d86f60b681c0c308cecc8c3d6ea9b2d3df5c34c8d17d3c80c35d06e8`.

The owner disclosed an initial strict-TypeScript integration failure because the engine's declared phase union includes menu; the corrected readonly context maps title/menu to the adapter's title phase. The inspected code contains that mapping and the owner-built production candidate exists. This review does not hide the earlier compile failure or call it a rules defect. Full owner77-rule/27-browser results and later native version0.6 evidence are separate.

## Personally executed behavior

`node --import tsx --test tests/input.test.ts`: **13/13 pass**. The pure decoder covers edge-only activation, neutral rearming, button/axis hysteresis, directional repeats, simultaneous priority, gated pause, disconnect/index/time handling, nonfinite input and device-identity non-access.

Own actual production harness, `technical-v0.6-input-evidence/harness.mjs`, uses the shipped adapter/host, actual controls/native keyboard events, saved data and a synthetic navigator standard gamepad. Valid full-roster diagnostics are deliberately unearned positions. Every load guards the exact production digest; no scratch controller replaces the shipped host.

Seven of nine initial browser cases pass:

1. Held Enter selects a binding once and cannot follow focus into a command; a fresh intentional Enter produces the exact canonical attack.
2. Held Space selects once; a fresh Space produces the exact canonical attack.
3. Killing a focused nonfinal enemy saves the exact expected state and recovers focus to connected ready bindinga11.
4. Escape cancels targeting, restores the source binding and preserves exact saved state.
5. Collection→card modal replacement keeps focus inside its new contents; attempted outside End Turn is blocked; close restores external Deck origin without a save change.
6. Textarea E/I repeats and native arrows retain editing and do not trigger gameplay.
7. Integrated virtual-pad A is edge-only through target focus changes, and fresh confirmation saves the exact canonical action.

Additional actual motion-on terminal diagnostic passes in `terminal-pause.json`: canonical reward state saved before animation; Escape while settling opens safe pause and clears the presentation epoch; after1350ms the old wait/deadline does not override the modal or save; closing pause focuses the outcome heading. No uncaught errors or external renderer requests in these probes.

## Findings and precise scope

**P2 composition guard gap, new adapter — `src/input.ts:onKey`.** Main's capture handler returns for `event.isComposing`; the adapter handler does not. On actual d33 with a focused binding, a synthetic bubbling/cancelable `keydown` for I with `isComposing:true` opens its inspector despite the intended composition guard. The save remains unchanged, but focus/modal state changes during an event that should remain native. H/B/T/arrows have the same missing guard in source. This is a reproduced event-contract/UI boundary, not a claim of tested physical IME composition. Add the adapter composition guard and test that composing inspection/navigation stays inert while ordinary shortcuts continue; then recheck the actual combined production build.

**P2 lifecycle hardening, synthetic evidence only — pad polling.** The adapter resets for hidden document and device changes, but has no blur/focus suspension. A deliberately dispatched window blur with the document still visible allows virtual A→release→A to select/commit an attack. This demonstrates lack of a blur boundary in the adapter; it does **not** establish behavior of a real hardware pad while a native application is unfocused.

An additional setup tried separate browser contexts/windows and bringToFront. Its raw timeline in `visible-window-blur.json` shows `document.hasFocus()` remained true throughout. Consequently that attempt never actually induced focus loss: its later save change is ordinary focused virtual input, not independent evidence of real background input. Do not relabel this failed setup as native focus-loss proof. A narrow blur/focus reset and neutral rearming is the agreed conservative repair; its recheck must distinguish simulated event/adapter semantics from physical/native tests.

Both failed initial check records remain in `checks.json`, including their exact assertions. They are not deleted or recast as full passes. Earlier v0.5 keyboard defects and reviews likewise remain preserved.

## Boundary assessment and next gate

The adapter has no engine import, save mutation, network operation, privileged Node/preload access or device-identity read. It returns intents through limited current-host callbacks and public DOM controls; main still routes canonical accepted actions through its existing reducer/save-before-presentation path. Semantic references use escaped identifiers, not names or detached controls. Dialog guards prevent outside activations; unplayable/illegal gameplay still fails existing host legality checks. Input callbacks cannot manufacture damage, private future previews or new save generation.

Polling is bounded to eight candidate pads and17 buttons, idle retries500ms, with disposable RAF/timer/listener ownership. Hidden/device resets neutralize held input; controller movement repeats while activation does not. Read-only phase/selection/presentation context is not serialized. Existing local voluntary feedback remains independent and no physical-controller identity enters its report.

The separate visual reviewer is investigating inherited short-height1920×720 roster clipping; this review neither certifies that geometry nor closes the existing long-distance contact limitation. After narrow repairs, require actual final digest correspondence and composition/focus-loss/held-key/modal/terminal/target-preview/save regressions. Preserve all current negatives. Native version0.6 Linux/Windows packages and physical controller/Deck/IME/consumer hardware evidence are not yet verified; earlier v0.5 native acceptance must not be borrowed as version0.6 hardware approval. Human enjoyment, authored combat craft, accessibility completeness, rights and Steam publication/install gates remain unearned.

