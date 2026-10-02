# Independent gameplay protocol SOURCE review — focused caller R4

Decision: **ACCEPT SOURCE, narrowly**. The sole gameplay blocker in my retained R1 review is repaired. The frozen R4 protocol is coherent for a controlled later-turn binding and one free Order, with full saved-string purity and paired checkpoint equality. It is still an ineligible source template: candidate C bindings remain null/incomplete, no Root method grant is present, and no caller, browser, server, game, build, or actual comparison was executed for this review. Acceptance is not runtime authorization or evidence that the branch occurs.

Reviewed source root: `/workspace/scratch/opening-cue-late-binding-caller-source-r4`.

## Exact evidence and closure

I independently read the driver, protocol, expected conditions, manifest, README, source trace, preservation receipts, and relevant B/inherited hunt-entry and proposed C presentation source. I rehashed all 24 bodies listed by `SOURCE-SEAL.json`; every byte count and SHA matched. The complete family including its seal is 218,693 bytes, equal to the declared count and below the newly authorized 262,144-byte source cap.

Relevant exact pins:

| Body | SHA-256 |
| --- | --- |
| R4 `SOURCE-SEAL.json` | `aabc6f5fd7b7c8ebc5c9456c44fbadac532ee27e9c2d260b21395a95df1c231d` |
| R4 `driver-cue.mjs` | `37b64437b6e4661f5679cda730a48f45ef2e1590a21f54cda4c0b7285147f3dd` |
| R4 `PROTOCOL.json` | `daaf73607d492039042cf5336c664d7d8815598febdddf78b54078c5d1fa7e61` |
| R4 `EXPECTED.json` | `d5f8a9cddebc3197260ad5da94709401c72a6b6b4fc41d345edf2d736bd2a742` |
| R4 `UI-SOURCE-TRACE.json` | `6d46f79cab104a51707416f12d73094606376d9b7ebcee41b27b8670e45c0643` |
| B `src/main.ts` | `d1e71626b4c70679f4ba692b62ccb2aea0dbe5ce74e9a1426b6208fc26a45fe2` |
| B/inherited `src/hunt-entry.ts` | `7c53defb4db9f68fc2bfb47de6a64302b8915cdf077fb84b6df69af3142f80fb` |
| Proposed C `src/main.ts` | `87a9bd7c2319522f77db7ea9e2edc306bb6124b019306dc220087f6b9b7762f4` |

The three bodies in the UI source trace independently match their recorded lengths and hashes. B is the exact private reconstructed runtime source; the proposed C source is presentation-only and is not an observed C build. Canonical selected/held versions are outside this comparison.

## Terminal blocker repaired

My R1 report rejected unconditional cue DOM removal after an Order. Proposed C `src/main.ts:360` can hold the final strike while saves already reflect the terminal result; it retains the old dock and cue, marks the app settling and scene busy, and disables commands. `render()` at line 468 eventually sets the actual phase class, hides the dock, marks the arena hidden, and renders the terminal heading. It does not erase the old dock innerHTML. A cue node retained inside that hidden dock is consistent with this presentation.

R4 `driver-cue.mjs:53` now distinguishes the saved phase captured after the actual Order:

- In battle it still requires the consumed C cue to be absent. Thus the terminal exception does not allow a stale actionable battle cue.
- Outside battle it retains a real initial sample, then waits for the app class matching the saved phase, no `settling-combat`, scene `aria-busy` other than `true`, `dock.hidden === true`, arena `aria-hidden === true`, and an actual scene heading.
- It rechecks those conditions in the saved settled sample and requires the cue not to be visible. Retained hidden markup is explicitly allowed. Hidden dock ancestry removes its buttons from ordinary actionable UI; the protocol does not falsely require the disabled attributes to be cleared or every descendant to carry its own hidden flag.
- It requires full raw-save equality across the passive presentation wait. The earlier 350 ms post-Order window also checks full equality against the committed checkpoint, followed by a `settled-first-order` checkpoint.

The terminal allowance is `min(4000, 60000 - elapsed - 500)` on the original `started` clock, guarded before and after. It does not reset the 60-second driver budget, enlarge the enclosing 90-second supervisor budget, or create terminal observations before they are sampled. Timeout or a missing condition fails. An initial sample may already be settled; that is valid observed completion rather than an invented impact hold.

I additionally extracted only the exact pure `waitForFunction` predicate into an offline fixture, without importing the caller. Ten checks passed: settled reward/defeat/victory with retained hidden cue markup pass; wrong phase, settling, busy scene, exposed dock, exposed arena, missing heading, and missing app fail. Fixture and receipt are retained in this review directory. This is source predicate checking with mock DOM nodes, not browser/game evidence. Its measured peak RSS was 27,236 KiB, below the authorized 64 MiB ordinary allowance.

## Controlled entry and later-turn branch

`enterFreshContract()` at driver line 52 follows the real inherited UI. It checks null save and title/dialog state; clicks the actual title contract button; verifies default difficulty 0 and no replacement-save field; observes the seed panel initially hidden; clicks `[data-hunt-disclosure="hunt-seed-panel"]`; verifies both expanded state and visibility; focuses the seed input and types 121 with trusted keyboard evidence; then submits the normal form. B `hunt-entry.ts:138` implements that disclosure and focuses the seed field; proposed C `main.ts:1368` handles ordinary submission through `readHuntContractForm` and `start(parseSeed(...))`. No state/save injection or alternate UI donor is involved. The earlier preliminary visual concern about missing disclosure was retracted and is not a remaining blocker.

The protocol deliberately ends turn 1 before any available legal first binding. It checks turn, floor, difficulty, empty allies, and zero cards played; uses the ordinary End turn control; then reads the actual naturally drawn turn-2 hand and current legal DOM occurrences. It prefers a naturally present Cairn Hound, otherwise the first legal summon, and checks the hand index against the raw save. This is an intentional source-informed delayed-binding experiment with typed seed 121. It does not establish naturally unprompted late binding, ordinary random-seed frequency, novice choice, or opening pacing.

If the actual path reaches turn 2 with a legal binding, current candidate cue text and visibility must persist beyond turn 1. The protocol then checks the actual bound card ID, newly observed current UID, READY class, and unspent actor before selecting that same UID. It does not reuse a guessed or stale actor identity.

## Purity, previews, Order, and paired coverage

Driver lines 44–54 retain full raw saved strings at named checkpoints and require purity around samples, binding hover, actual held binding cancellation with Escape/native release, both hostile hovers, and Order cancellation. Held lift requires an active ghost plus a trusted pressed native pointer witness. Cancellation includes the finite 350 ms no-delayed-play window, unchanged full save, no active ghost, and restored cue. Selected Order cancellation preserves the full save and restores the READY cue before reselection of the same current UID.

Both actual enemy UIDs must have current `valid-target` affordances, trusted native pointer movement, retained preview samples, and unchanged full saves. The two-target count is asserted; this protocol cannot silently claim two-target coverage when only one target exists. Preview content is retained for actual review, but semantic preview kind/damage accuracy is not independently asserted by the driver. An actual reviewer must inspect those retained previews before accepting that stronger claim.

The ordinary first Order must change the saved string without increasing cards played. Continuing battle requires equal energy, equal hand, and a surviving actor with its command spent. A terminal transition is qualified by its actual phase rather than wrongly treating combat energy cleanup as Order cost. Post-Order purity and presentation retirement are then checked before the second original capture.

Driver line 56 compares the union of both contexts' checkpoint labels. Every union label must exist on both sides and match as a complete saved string; a missing checkpoint is a failure. Status, binding choice, bound UID, and selected hostile UID must also match. `protocolPass` alone may describe paired explicit skip branches, but `mechanicalPass` requires both actual late bindings and both actual first Orders. `skippedCoverage` preserves lack of that branch. The protocol therefore does not turn skipped terminal/no-binding paths into demonstrated late-binding mechanics. Cue acceptance remains marked for independent actual review.

These finite purity checks do not establish the absence of every possible future repeat. Only two original screenshots per context are authorized; first-binding/cancellation checkpoints rely on raw/DOM/pointer receipts rather than extra images. No full 300-second endpoint is part of this focused caller.

## Preserved failures and remaining gates

The rejected R1 review remains unchanged at SHA `95b812959a6e1430cee946a7c9f7e2f3ad31d1763ccce23503a06ea88dad7c94`. R2 and R3 remain failed, unsealed source closures; I confirmed neither old directory contains `SOURCE-SEAL.json`. The R4 preservation receipts retain their sizing failures. The new R4 cap and acceptance do not retrospectively approve either failed family. Earlier actual first-300 observer failures and the qualified completed private-B run also remain separate evidence.

No additional gameplay source blocker was found in this frozen R4 template. Candidate C is still unbound/ineligible, with runtime outputs/current metadata/engineering authority absent. A later exact rebound source revision needs its own review and Root grant before any runtime. If the actual terminal branch does not occur, it cannot be reported as observed terminal coverage simply because this predicate is corrected.

This review accepts only source protocol behavior. It does not accept human fun, five minutes of active human play, novice pacing, default-query behavior, art coherence, general native-128 rendering, Windows/platform behavior, or actual B/C cue effectiveness.
