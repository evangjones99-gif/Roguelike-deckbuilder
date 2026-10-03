# v0.4 engine repair evidence

This is implementation evidence, not an independent review or a claim of commercial quality. The v0.3 development archive retains the inherited legal-action save defect and its original evidence.

## Repaired behavior

Repeated Silence casts on a guarding foe now produce one ` · silenced (armor remains)` status suffix. They retain the original cost, card-copy payment, zero damage, canceled reinforcements, guard identity and eventual armor grant. A valid older double-suffix intent becomes canonical when another Silence is cast. A redundant cast on an already canonical intent spends its normal cost but emits no fabricated control change.

The preserved actual campaign is `reviews/solo-v0.3/silence-overflow-campaign.json`: Initiate seed 1989, 119 accepted legal actions, Ironjaw node ten, turn three. Action 117 casts Silence+ for one energy, action 118 casts Silence for two, and action 119 casts the second base Silence for two. Energy proceeds 6→5→3→1; the deck contains exactly those three copies. Previously labels grew 35→62→89→116 characters, exceeding the validator's 100-character bound. They now remain at 62 after all three casts. Every intermediate state validates.

Only the repeated intent text and its later combat-log observation differ from the archived engine in this campaign. The new regression compares every other field, including RNG, HP, block, attack, intention damage/target/reinforcements, statistics, collection, draw/discard/hand, relics, gold, floor and route. JSON continuation reaches victory with matching mechanics. The next enemy phase grants the existing 14 armor and replaces the status with the normal Iron cleaver intent.

## Narrow old-save recovery

`recoverLegacySilenceSave(value: unknown): GameState | null` returns a detached repaired state only when the original fails validation and an overlong enemy label exactly matches a known generated guard prefix followed entirely by repeated Silence suffixes. It additionally requires that foe's guard turn, its self target, zero damage, and an empty reinforcement array. The canonicalized complete state must pass the existing validator. Valid saves use the normal loader and return null from this helper.

The helper catches malformed inputs, rejects unknown prefixes/trailing junk, mismatched phases or turns, alternate targets, damage/reinforcements, oversized labels, forged definitions, unrelated HP/RNG/copy corruption and unknown schema. It never mutates the input. UI owns preserving the exact original storage text before writing a recovered save and presenting an honest recovery notice. Recovery is not a general corruption migration or a promise to accept arbitrary old saves.

## Verification and provenance

- `npm test`: 54 passing tests, including five new save regressions and the unchanged 120 complete deterministic/random replay comparisons against the archived v0.2 engine.
- `npx tsc --noEmit`: passed.
- `tests/save-validity-v0.4.test.ts` replays all 119 actual actions, checks legal acceptance and input purity, compares archived semantics with the explicit narrow label exception, checks real guard resolution, serialized continuation, recovery detachment and corruption rejection.
- Engine SHA-256: `ee85f1400a9d02142aee1dd66f82722453f35930bbf2c0c229ad38e38a818d0d`.
- Content SHA-256, unchanged: `2f45160b3e577a7cd44381cb361c4407661a68819ff827a24b8ab34ce15c4234`.
- New regression SHA-256: `4e23c3f02c05c8888605f50a11ef8fa826446f8036f94a79bcb587647b3482de`.

Schema remains 2. Shared RNG, encounter sampling, prices, deck rules, and saved fields are unchanged. Production world-stream isolation is a separate future candidate; the virtual cheaper-removal research does not authorize a price patch. Independent review and production-browser migration checks remain separate from these implementation checks.
