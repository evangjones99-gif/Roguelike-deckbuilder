# Freeze v3 — one reported action anchor for held-slot summons

Source-only correction in R2 src/arena.ts. The v2 three-file freeze is preserved byte-exact in freeze-v2/. battlefield-layout.ts and hunter-presence.ts are unchanged. No Node, browser, build, compiler, Git, main.ts, audio-host.ts, CSS, rules, save, or native edits were made.

## Rejected v2 timing

V2 reported the allocation lead, but birth used max(time+allocationLead, heldCorpse.dead+900ms). Its summon ward cue was moved separately, while the host received only allocationLead. A summon into an unchanged dense formation could therefore have allocationLead=0, a later birth, and audio before visible arrival. V2's later event-order birth adjustment had the same unreported-offset problem.

## Rule-source reasoning

engine.ts play() emits an allied summon with source hunter, then its effect may ward/heal/draw or burn enemies. It does not kill another ally to make that ally's slot available. engine.ts endTurn() damages allies/hunter, cleans those results, then emits enemy reinforcements after the fixed hostile roster acts. It does not kill enemy slots in that phase. Thus the current legal arrival traces can reuse a previously scheduled corpse on their own side, with an already-known absolute death/hold timestamp. Those traces do not require a newly caused same-action death followed by same-side reuse.

The original 900 ms CREATURE_DEATH_MS, per-source enemy phase offsets, retaliation offset, 240 ms impact, complete source windows, and death resize basis stay unchanged. Canonical reducer application/save still occurs before optional presentation as owned by main.

## Implemented contract

prepareActionAllocation still establishes exact UID slots and any geometry lead. Before any current-action strike/gesture is queued, reusedArrivalHold scans the action's summon events plus newly present canonical UIDs and their allocated same-side slots. It finds the maximum previously scheduled old corpse hold remaining. The action lead is max(allocationLead, reusedArrivalHold). getActionPresentationDelayMs returns its upward-rounded integer ms with at most 1 ms quantization and no hard clamp.

lastActionCueStart stores the absolute renderer timestamp. All new figures for the action begin at that anchor, including the no-trace canonical-render fallback. Existing per-source phase delays are added to strikes/hunter gestures exactly as before, relative to the new common anchor. Summon effects no longer add an unreported per-arrival offset. Host audio already adds the reported lead to its anchor and retains its authoritative contact offsets; no audio file was edited here.

Ordinary attacks with no allocation change and no new arrival have lead0 even if other optional cues are active. There is no blanket animation/cue input lock added. Existing root layoutPending dispatch policy remains separately owned. A reinforcement-containing end-turn action can now wait as a whole behind an earlier enemy corpse hold; this is a pacing tradeoff of the single-anchor contract and requires actual comparison.

After scheduling the trace, a defensive check rejects optional presentation if a future/custom same-side victim requires a hold beyond the new figure's common birth anchor. The existing presentation-failure reset clears cues/pending geometry, snaps to accepted canonical state, and rethrows for the host's optional-effects fallback. It does not secretly move that birth beyond the reported audio lead. If future rules intentionally kill and replace the same side in one action, they require an explicit multi-phase/per-cue audio contract rather than stretching a single anchor circularly.

Hidden/reduced accepted actions explicitly clear old pending cues, render the accepted state, then settle canonical figures and lead immediately; they do not retain stale delayed births on restore. Existing resize keeps the absolute cue/birth/hold timestamps and original death-size basis.

## Arithmetic illustrations, not runtime tests

At renderer time4.0s, a prior corpse dead3.7s ends its900ms hold at4.6s. With allocationLead0, the corrected action lead is600ms, figure birth4.6s, and the host's ordinary240ms contact cue4.84s. The old lead0 would have placed that cue4.24s before the4.6s birth.

With allocationLead1.1s and the same600ms hold, lead remains1.1s rather than adding the two: birth5.1s and ordinary contact5.34s. A normal unchanged attack with no arrivals remains lead0 and contact4.24s. Enemy source-order offsets remain on top of the shared anchor; the correction does not invent new enemy actions or independently defer only an arrival sound.

## Remaining gates

Compile/typecheck the matched integration; observe actual allied summons into held full-formations, later binds while an earlier arrival is held, enemy reinforcement phase with old hostile corpses, on-bind burn/ward/heal and terminal results, unchanged ordinary attacks, motion off, hidden/restore, cancellation, and resize during delayed birth. Measure the getter, first visible newborn frame, visual bind/impact, and host cue anchor/offset together. Source arithmetic alone does not establish audible or rendered alignment. No runtime acceptance or animation-polish claim is made.
