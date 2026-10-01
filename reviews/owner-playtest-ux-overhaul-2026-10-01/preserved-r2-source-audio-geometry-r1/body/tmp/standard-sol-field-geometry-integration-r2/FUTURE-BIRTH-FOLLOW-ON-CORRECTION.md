# Freeze v4 — event-targeted lead for pre-existing future newborns

Source-only correction in R2 src/arena.ts. Exact v3 source files, API.md, MANIFEST.json and BIRTH-AUDIO-CORRECTION.md are preserved in freeze-v3/. Layout/hunter files are unchanged. No rules, saves, CSS, main, audio, native, Node, compiler, build, or browser changes/tests were made.

## Reachable sequence confirmed by source inspection

The v3 same-action argument remains limited to an arrival killing and replacing its own side within that one action. It does not prevent a later accepted action from touching an earlier canonical arrival before its painter birth.

Current engine.ts legalActions admits cards using canonical hand/energy/target arrays; it has no renderer-born timestamp. content.ts defines Witchfire as a cost2 target-none aoe spell dealing4 to every enemy. play()'s aoe branch emits actual hit/death events against every current canonical hostile, including raised enemies. endTurn() can raise an enemy into a free canonical slot after an earlier player kill, then refresh energy to5 (or the existing relic adjustment), draw5 and publish the next canonical intents. Thus, in a legal battle/deck draw that includes Witchfire, a corpse-slot reinforcement can be canonical and future-born while the unchanged held formation has layoutPending=false. Immediate Witchfire is legal and actually hits that newborn. This is a source-supported sequence, not an executed seed or browser fixture.

Likewise legalActions admits unacted canonical allies as attack sources; they may still have future painter births after a bind. A later traced command, end-turn hostile action, heal, ward, buff or control may therefore reference a future-born source/target. Waiting only when an action itself emits a summon misses those follow-on references. The old v3 state is preserved for review rather than reinterpreted as correct.

## Targeted implementation

referencedFutureBirthHold(events) reads the pre-existing figure map before prepareActionAllocation or any current-action cue scheduling. It examines event.source and event.target for every actual accepted TransitionEvent, takes the latest known figure.born deadline that is later than renderer time, and returns only that remaining hold.

The common action lead is now max(allocationLead, reusedArrivalHold, referencedFutureBirthHold). getActionPresentationDelayMs reports the whole lead, rounded upward by at most1ms without a hard clamp. Existing strike, contact, reaction, death and hunter phase offsets remain relative to the same common anchor. Audio receives that exact reported anchor through root-owned integration. Existing newborn birth deadlines are preserved; the follow-on action does not reset or extend them.

An unrelated ordinary attack whose events touch only already-present figures retains lead0 even when another figure has a future birth or other optional cues are active. A target-none action with no emitted contact events does not wait merely because a future newborn exists. No global cue/input lock or canonical reducer change was added. The narrow scan uses actual accepted events rather than guesses from selected cards, intent labels, layout slots or all canonical actors.

The optional no-trace fallback remains a fallback; this event-targeted protection is for actual canonical traces supplied by the root integration. It does not fabricate missing hits or a predicted event list.

## Death, terminal and interruption reasoning

If Witchfire kills the future newborn, its old born deadline remains intact and the hit/death presentation is shifted to that deadline plus the original240ms impact. The corpse can therefore first paint before its observed collapse instead of dying invisibly before birth. If the action clears combat, the held terminal figures/cues remain disabled and busy through the full lead/impact/death hold; main's actual busy deadline must remain authoritative.

A future-born attacker or retaliation source likewise does not gesture before its known born deadline. All area targets/contact cues in the same action share the latest touched newborn's anchor, avoiding per-contact unreported delay. This briefly defers already-visible co-targets in that action; it is the deliberate common-anchor tradeoff.

V3's reduced/hidden accepted-action branch still clears pending presentation, renders accepted state, and settles births/cues/lead immediately. Cancellation, optional error fallback and resize retain their existing behavior and absolute birth/cue timestamps. This correction adds no new wait timer or clock and does not alter those lifecycle branches.

## Source arithmetic illustrations, not runtime tests

At time4.1s, a raised hostile has born4.6s and is hit by immediate Witchfire. Allocation/reused-new-arrival holds are0, but event-reference hold is500ms: common anchor4.6s, hit/audio contact4.84s, and lethal death begins4.84s. The old v3 lead0 would contact4.34s before first paint4.6s.

An attack with source4.7s birth and target4.6s birth at time4.1s takes600ms, so its source is available by anchor4.7s and contact4.94s. An unrelated attack at4.1s touching no future-born UID takes0 even though those other births exist. A larger allocation lead wins the max; holds are not added together.

## Required independent matched checks

Compile/typecheck after the final renderer freeze. Exercise the actual canonical kill → raising endTurn → immediate Witchfire sequence with the newborn held beyond the follow-on call; record getter delay, born, first paint, hit/death, busy/terminal hold and host audio anchor/offset. Also exercise a future-born command source and enemy source, unrelated immediate attacks, multi-target/multiple-birth maximum, non-damaging future target effects, reduced motion, hidden/restore, cancellation, and active resize. Source arithmetic is not rendered/audible acceptance and no animation-polish claim is made.
