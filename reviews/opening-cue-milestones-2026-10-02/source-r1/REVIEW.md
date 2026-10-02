# Opening cue milestones — proposed source candidate R1

This is a presentation-only candidate for review, not an accepted build or a claim of five minutes of fun. The only changed game source is `src/main.ts`; the full candidate file is included. Apply `FORWARD.patch` to the exact recovered parent. `INVERSE.patch` fully restores that parent file. No canonical or remote files were changed.

## Evidence and hypothesis

Before editing, read the recovered `src/main.ts` (all 1,432 lines), `src/engine.ts` (all 1,333 lines), `src/content.ts` (all 450 lines), and `/workspace/scratch/starter-first300-gameplay-review-r1/REVIEW.md` completely. The parent's main source SHA256 is `d1e71626b4c70679f4ba692b62ccb2aea0dbe5ce74e9a1426b6208fc26a45fe2`.

The gameplay review accepts narrow first-turn binding, READY/free-Order, consequence and intent evidence from private query seed 6743589. Its observer failed at normal reward cleanup after 135.7 seconds; it establishes neither full 300-second completion nor active human enjoyment nor general/native art acceptance. Its explicit next hypothesis is that guidance should survive a natural first summon after turn 1. The existing main.ts798–806 gates both cues to floor 1 / turn 1.

## Implementation

Add one in-memory `openingMilestones` record, outside GameState: binding is pending, unknown, or done; orderDone records an observed committed Order. Keep the existing floor-1 scope and existing cue markup, class, action availability checks and text style. Remove the turn-1 limits and replace the living `acted` inference during play with the committed Order milestone.

Only `dispatch()` after its unchanged-state early return and successful canonical state replacement advances the record. An actual ally summon event marks binding done; an accepted attack marks order done. This includes a lethal Order and a summon whose arrival effect ends combat, even though battle cleanup clears living units. Preview reducer calls do not enter this update. Selection, hover, Inspect, drag cancellation and failed/unavailable actions leave it alone.

`start()` clears the record for every fresh run and same-seed retry. A successful reducer start also clears it. Returning to title and resuming within the same window preserves the current record; no seed-based identity cache can confuse a replay with the previous run.

Loaded validated or recovered saves initialize conservatively: living allies prove a binding occurred; zero cardsPlayed with no allies proves no card was bound; otherwise historical binding is unknown and the cue says “Bind a creature.” instead of “Bind your first creature.” A living acted ally proves an Order was committed. Other historical Order states remain uncertain; the existing generic READY/free-Order text states the current legal affordance without claiming it is the player's first Order. The cue still requires a currently legal attack. No history is guessed from truncated log text or draw/discard identities.

## Stateful review cases (source-traced, not executed gameplay)

| Case | Expected cue behavior |
| --- | --- |
| Fresh first contract has no summon in turn 1; natural turn 2 draw offers a legal summon | First-binding text appears on turn 2; rules/draw remain unchanged. |
| Summon available but currently unaffordable; later energy permits it | Cue waits for legal play, then appears; lack of availability does not complete it. |
| Hover/Inspect; select targeted tool; cancel ordinary selection; cancel drag; invalid dispatch | No milestone changes. Order cue can temporarily hide while a tool is selected and returns after cancellation. |
| Successful summon after turn 1 | Binding marked done; existing READY/free-Order text appears if an attack is legal. |
| Select READY binding, hover target, cancel; end turn without issuing Order | Order remains pending; guidance returns when an attack is available, including later turns. |
| Committed Order does zero health damage, or retaliation kills the acting binding | Order done because it was issued; neither damage nor survival is a completion requirement. |
| Committed Order clears contract | Order done before presentation holds the final strike; reward energy cleanup is irrelevant. |
| Binding lost before any Order; a replacement is summoned | First-binding lesson does not repeat; pending free-Order lesson can appear for the replacement. |
| Order committed; creature readied by spell or next turn; all allies later lost/replaced | Both completed lessons remain retired. |
| Next floor | Both opening cues stay suppressed by floor-1 scope, whether milestones completed or not. |
| Title return/resume in the same window | Observed milestones preserved. |
| Fresh campaign or retry, including the identical seed | Both milestones reset. |
| Reloaded save has an existing ally | Never calls it the first binding; an acted ally also suppresses Order guidance. |
| Reloaded floor-1 save has no allies and cardsPlayed > 0 | Binding history unknown: generic “Bind a creature.” only when a summon is legal. |
| Reloaded save has ready allies but an Order may have happened on a prior turn | Generic READY/free-Order reminder can recur; no reliable historic Order record exists without changing save persistence. This is an explicit limitation. |

## Verification and limits

`GRAMMAR.json` records Node v24.19.0 built-in TypeScript stripping plus `--check` for both exact parent and candidate. Both exit 0; imports and game code were not executed. This proves syntax parsing only, not TypeScript type correctness. Child peak RSS was 26,748 KiB; `/usr/bin/time` was unavailable, so Python resource.getrusage supplied the peak. Strict in-memory forward/inverse application and exact SHA256 restoration are recorded in `MANIFEST.json`.

No npm, network, build, browser, server or gameplay run. No balance, reducer, save schema, localStorage key, telemetry, CSS, audio, source art, hand mechanics, input/focus or reduced-motion edits. The existing live DOM remains authoritative; no overlay or animation was added. Inherited private query paths and assets remain unchanged, with no new Fast toggle or user-facing development control.

Actual exact-source build, A/B comparison, independent gameplay, visual and technical reviews remain necessary and may reject this candidate. This packet does not prove natural late-summon coverage, legibility at every viewport, accessibility with assistive technology, human enjoyment, full 300 seconds, default/native art acceptance, or platform behavior. Reload forgets observed transient history by design; persistent tutorial history would need a separately authorized persistence design.
