# Independent v0.7 hold-hint R2 review

Verdict: accept the root-authored isolated readability repair for the reviewed prototype gate. The 10px finding is repaired: resolving labels, Esc, and Start are all 12px; keyboard and controller share the visible key treatment. Actual containment, canonical persistence, pause, and blocked-action checks pass at all six requested viewport sizes. This does not promote runtime or establish native/physical-controller acceptance.

## Candidate and preserved comparison

Actual candidate is the Vite development server on 4189 at `/workspace/scratch/ui-v07-root`. R2 main SHA256: `a7890d0ba20b2ce501e6d8cda189b97ceb246eff13ac59884fa016529b342290`; R2 style SHA256: `adcb097532528d44383896c03987061831d8fe79e25d644d0b1b6088402b3bef`. Input and arena are unchanged. All four before/after hashes match. Readonly source snapshots and transformed served-module fingerprints are included; the copied dist provenance still describes the older baseline, and is not presented as an R2 release digest.

Original independent R1 evidence remains untouched: manifest SHA256 `92ed3ea6ebd070c185812200aff99f3b0df5342c8f3fc4f3cce6cf5708b33113`, all ten entries reverified. `r1-main-reconstructed.ts` is a byte-exact R1 source reconstruction made by reversing only R2's Start kbd treatment; its SHA256 is the recorded R1 main hash `69b1b25f391d77978c01ede281e523620b6e3d61b3af79b480ee4e79bcbf1e7a`. This reconstructed copy is stored only in the new exterior review directory, and the method is disclosed rather than representing it as an untouched historical file.

The style also contains the separate root decorative arena-caption hide. The viewed R2 screenshots show that caption absent, so it does not cross the battlefield. This report does not assess any subsequently planned central hunter or audio prototype.

## Actual tests

Twelve independent Chromium cases cover keyboard and synthetic standard-controller input at 1024×720, 1024×1080, 1280×720, 1280×1080, 1920×720, and 1920×1080. Each uses the previously disclosed structurally valid diagnostic final-kill fixture; the unchanged actual reducer from the prototype independently computes the full canonical expected state.

Every case proves:

- The real accepted Scour final kill saves canonical reward state immediately while retaining battle presentation.
- The visible resolving hint has 12px computed font on all spans and key glyphs, includes only the safe Esc/Start Pause action, and fits inside its parent and viewport. It is 126.05×34 pixels in each tested case.
- Keyboard E/I/ArrowDown and a programmatic stale End turn click, or fresh synthetic controller B/X/Y edges with neutral releases, cannot alter state or open a dialog while held. This explicitly exercises the real application gate, not only CSS disabling.
- Trusted keyboard Escape or a fresh synthetic Start edge opens the real Campaign paused dialog, settles the hold, and leaves full serialized canonical save unchanged. Closing it reveals rewards and hides the battle dock.
- No other localStorage key changes. The accepted killing action is the only campaign write represented by the stored outcome. No page errors occurred.

Four screenshots retain keyboard and controller captures at the minimum 1024×720 and largest 1920×1080 viewport. The reviewer actually viewed the 1024 controller and 1920 keyboard screenshots; the short status and key treatment are legible and unclipped. Other sizes have actual computed-font and bounds evidence, not claimed screenshot inspection.

## Limits and reproduction

The synthetic pad is polled by the actual shipped input adapter and actual application callbacks. A throwing device-ID getter detects access; no device ID access occurred. There is no physical gamepad, native packaged Windows/Steam Deck test, accessibility assistive-technology test, audible listening, or human enjoyment assessment in this evidence.

The live reduced-motion, hidden-boundary, and mode-change checks were already independently exercised in R1. R2 does not claim a new repeat of those boundary trials; the current source change adds key markup and CSS font sizing, and the 12 new cases focus on the requested readability/containment and preserved canonical/pause/stale-action behavior. A final integrated release still needs correctly attributed build provenance and its independent regression checks.

`review.mjs`, `results.json`, source snapshots, fixture, transformed-module fingerprints and four screenshots are the new immutable evidence. No repository or root-prototype files were edited. Reproduce into a new exterior output directory: this probe exclusively creates result/fixture evidence and should not be run against a frozen directory.
