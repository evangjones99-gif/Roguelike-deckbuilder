# Independent v0.7 held-combat hint comparison

Verdict: the isolated two-part hint repair passes the observed behavior gate. It corrects a real v0.6.1 misleading-controls defect without changing the reducer, persistence, presentation lock, or allowed pause action. This is a prototype review, not a shipped-version or native-controller acceptance. Readability should improve before promotion: the brief hint is still 10px at 1280×720; use at least 12px and a consistent visible key treatment for Start.

## Attribution and independence

Reviewer: game_ui, independently exercising the root-authored repair. No repository or root-prototype files were edited by this reviewer. All new evidence resides in `/workspace/scratch/ui-v07-independent`.

Baseline: actual production browser on 4173, version 0.6.1, advertised source digest `8720a38701aa78ccae894ba4ca7cb8656cc3072d5b023cdd9cc3d9d2b3d4c22d`; main source SHA256 `75f4dad531b0eef0d990607695f5a1b87645b92beac7f2e2d7eea6b79b754d44`, served JS SHA256 `8e70022b6c20950f691ace9ec3b9fdf3920296056fe15d22d9c7bc65db8f27dd`.

Candidate: Vite development server on 4189 at `/workspace/scratch/ui-v07-root`, main source SHA256 `69b1b25f391d77978c01ede281e523620b6e3d61b3af79b480ee4e79bcbf1e7a`. It serves transformed source modules, not its copied dist. The copied dist provenance remains identical to baseline and does not identify the prototype. `prototype-served-modules-after.json` records served transformed modules; no new release digest is claimed.

Both reviewed source snapshots used CSS SHA256 `7489c4689cd3c3f6da9c79fdd62d2df788d67e420eacc8395709e9d5d3753483`. Fingerprints before and after all 12 trials match. Root subsequently appended a separate decorative arena-caption hiding rule; current CSS SHA256 `7f6d5b164630c98d04ff9ab3be5783224ec51164252d084700fa96f66ebe6c5d`. That next-stage delta is outside this review and is not covered by screenshots or the unchanged-source assertion.

## Actual comparison

A structurally valid diagnostic state uses one 1-HP hostile and a conserved real Scour card. The fixture is disclosed as diagnostic, not an earned campaign. The expected full terminal state is computed independently with the actual pure reducer before the browser test.

Six paths were run against each server, 12 trials total:

- Keyboard final kill: canonical reward save commits immediately while battle HTML remains held. E is blocked. The old hint still advertises Choose, Cancel, Targets, Move, Inspect and End turn; the repair shows only “Final impact resolving” and “Esc Pause.”
- Synthetic standard-controller final kill: genuine runtime adapter polling, fresh A selection and command, neutral releases. The old hint advertises A/B/X/Y/D-pad actions during hold; the repair shows only resolving status and “Start Pause.” B is blocked, no pause or state change. Fresh Start opens the real pause dialog and settles presentation.
- Input mode change during hold: trusted keyboard E switches to keyboard mode without accepting an engine action. Fresh synthetic Start switches the hint back to controller mode while the hold is still active, then safely pauses. Synchronous instrumentation of actual hint updates records resolving/Start → resolving/Esc → resolving/Start. No host callback or input-context shim is used.
- Motion disabled before kill: no hold; rewards appear immediately and the battle dock/hint is not visible.
- Live system reduced-motion change: after the actual matchMedia change event, the hold snaps to rewards; saved state is unchanged.
- Explicitly emulated hidden document: presentation settles and pad reads stop. Held A on visibility return does not claim a reward; neutral release re-arms. This is a synthetic visibility boundary, not an OS background-window certification.

For every path, full saved state equals the independently computed outcome and all localStorage keys equal their prior values apart from the one accepted killing action's campaign update. No future cards or rewards are claimed from user input during the hold. No browser page errors occurred. Screenshot bounds place the hint inside its parent.

## Craft finding

The viewed `baseline-keyboard-hold.png` clearly shows unavailable E/Cancel/region/inspect/navigation controls during “Contract cleared.” The viewed `prototype-keyboard-hold.png` removes that conflict and explains the brief delay. Its 10px pause hint is small at 1280×720. The 12px top resolving banner provides redundant status, but it does not name the safe pause key. Raise the hint to 12px rather than relying on that banner. This report does not assess other layouts, all-six rosters, broader animation craft, enjoyment, or commercial readiness.

## Failed first harness and preservation

The first attempt failed on the baseline live reduced-motion test after four completed trials: CDP emulateMedia returned before its JavaScript matchMedia change event dispatched. The immediate held=false assertion failed. `results-r1.json` and `review-first-attempt.mjs` preserve that raw failure. The revised probe observes the actual event with a 500ms bound, shorter than the ordinary presentation deadline, then retains the same held=false assertion. Both baseline and candidate pass it. This synchronization repair does not wait out the normal animation and does not establish a runtime defect in the first attempt.

The first baseline screenshot filename was reused by the revised attempt before the independent evidence set was frozen. The retained screenshot is explicitly the successful second-run capture; first-run source and failure JSON remain preserved. No published baseline or root evidence was overwritten. A separate initial post-run provenance collection assumed `src/world.ts`; that uncommitted collection attempt found no file and wrote no output. The corrected collector fingerprints the actual `src/world-rng.ts` dependency.

## Evidence and limits

`review.mjs`, `results-r2.json`, fixture, both screenshots, source fingerprints and served-module records form the successful evidence. `results-r1.json` and its first-attempt source retain the failed harness. Reproduction should copy the probe to a new exterior evidence directory and change its out variable: existing result files use exclusive creation and are intended to remain immutable.

The controller is injected through Gamepad API polling with a throwing device-ID getter. No device ID access occurred. No physical gamepad, native Windows, Steam Deck, human listening or human fun assessment occurred. The input mode/history instrumentation delegates to the real DOM setter unchanged. Browser tests ran in isolated contexts with muted audio and no runtime/source modifications. This behavior review supports proceeding to a properly attributed candidate build and independent release checks; it does not itself promote code.
