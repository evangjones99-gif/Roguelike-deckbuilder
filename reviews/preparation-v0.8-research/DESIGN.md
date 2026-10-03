# Optional field kits: v0.8 exterior research proposal

**Keep the shipped default starter unchanged. Do not promote these kits from this experiment alone.** Pursuit and Ash supply distinct tactical preparation hypotheses worth independent review. Iron Vigil is currently a weaker proposal: it often adds turns and hunter damage despite its advertised protection role. All three candidates and negative trajectories are retained without tuning on the declared held-out cohort.

This research used existing original binding/tool definitions, frozen engine/scoring sources and no new dependency or telemetry. It changed only the `deck` property in detached, validated initial diagnostic states before the first legal travel action. These are hypothetical starting loadouts, not earned acquisitions or actual user-selected campaigns. No new campaign, settings, rules, source, public asset, release, save or interface file in the project was written.

## Three coherent twelve-card candidates

| Kit | Binding cards | Tool cards | Decision it asks | Counterpressure |
| --- | --- | --- | --- | --- |
| Pursuit Seal | Cairn Hound×2, Grave Hound, Fen Stalker | Scour×2, Iron Ward×2, Sundering Hex, Kill Command, Forbidden Survey, Pack Edict | Strip armor before hound commands; Ready a spent hound or invest in enduring Edict attack. Spend binding/command tempo to prevent the next dangerous intent. | Only35 printed creature HP across four bindings; no creature healing. Armored retaliation, delayed binding draw and uncontained necromancer pressure punish aggression. |
| Iron Vigil | Briar Colossus×2, Fen Stalker, Cairn Hound | Scour×2, Iron Ward×2, Blood Sutures, Black Aegis, Sundering Hex, Forbidden Survey | Commit three energy to a colossus whose repeated commands ward the hunter, or use that energy to shield/heal immediately. | Setup costs and slower removal allow more enemy turns. Revenants bypass block; repeated Cantor pressure can overwhelm apparent durability. |
| Ash Writ | Ash Widow×2, Cairn Hound, Fen Stalker | Scour×2, Iron Ward×2, Sundering Hex, Witchfire, Silence the Dead, Forbidden Survey | Keep widows alive for targeted spell amplification; decide whether to damage now or deny an announced breath/raising intent. Use Witchfire for multiple weak targets, understanding widows do not enhance it. | Only31 printed creature HP. Silence is temporary and costs two energy; drawing it without a binding or ignoring the next intent can be costly. No Sutures/Aegis recovery. |

All candidates contain twelve cards, four bindings and eight tools; the current default has five bindings/seven tools. These are changes to **role mix**, not extra cards. Identical card count does not isolate role identity from draw density or make power budgets equal. Printed creature HP/attack and total energy are descriptive, not potency ratings. Hypothetical existing shop value is540gold per candidate versus555default, but no gold was charged and this is not a balancing measure. No premium/upgraded starting cards were introduced. `kit-profiles.json` preserves exact unchanged definitions and printed profiles.

If a later independently accepted kit becomes optional, place its role, exact deck and explicit weakness inside the existing new-campaign dialog, after seed/difficulty. The current default stays preselected; acceptance/abandon behavior stays the same; selection does not persist in sound/motion preferences or silently alter a resumed campaign. Deck inspection should be available before committing. Do not call kits difficulty settings or automatically choose one from a seed. Existing seeded boss forecast can help deliberate preparation, but must not become a hidden recommendation system.

Future construction must preserve `createGame(seed,difficulty)` and both supported world generations byte-for-byte when no explicit new kit is chosen. Do not change shared `STARTER_DECK`, prices, card values or continuing saved decks. A transient new-campaign construction option could supply a copied validated deck; it needs a reviewed contract and save/retry behavior before implementation. No such option exists in this research or shipped UI. Kind1/schema2 and kind2/schema3 interpretations stay separate; an existing save cannot be retroactively labeled a kit by fuzzy deck matching.

## Declared bounded experiment

`plan.json` was written before any source snapshot, episode or counterplay probe. SHA2564c493a46bd07983f70893227babb8a9ec2ef8d161a74303f90e74f942bd30b8b. Twelve declared seeds58001–58012 cover each fixed boss identity four times. This is a new cohort relative to inspected active source/tests/docs and frozen0.5ML records, not externally authenticated proof of globally untouched history.

Matrix: four decks × twelve seeds × two supported world generations × two combat policies × two acquisition arms = **384 episodes**, Hunter difficulty1,700 accepted-action cap. The existing heuristic combat score and frozen0.5 learned linear weights ran without modification or training. Both use the same copied ML noncombat decision function; one arm accepts its fixed reward ranking up to19cards, the other overrides only rewards to skip. Route/camp/event decisions use identical functions, not artificially identical health-dependent outcomes. Shops are skipped by the copied policy. The experiment therefore does not test diverse procurement, elites, shops, route planning, novice play or different difficulties.

The existing ML tool writes fixed directories and trains before evaluation. I inspected it and copied its complete hierarchy unchanged into the exterior snapshot. A separate adapter extracts its exact feature/scoring/noncombat functions and adds only imports/reexports, avoiding a second training run or protected dataset overwrite. `adapter-derivation.json` records the section hash and wrapper hash. `simulate.ts` supplies the actual existing heuristic. The frozen source hashes remain enginebfc9e612…, content2f45160b…, world-rngc4ea7b2b…, learn-policyaa1fa0e6…, and learned policybd6c70f5…. Full hashes are in plan/execution metadata.

Generation2 separates world purposes, so matching common node/kind encounters and offers remain equal across kit pairs: **zero differences**. Generation1 intentionally couples deck draws to its legacy RNG schedule: **964 differences** among comparable recorded world observations. Those legacy outcomes are not a pure same-encounter kit comparison and are reported separately. Neither constructor nor RNG code changed to make the experiment look controlled.

Every accepted action checks exact legal membership, incoming-state purity, validated state/JSON save, generation continuity, reducer-versus-resolved-event state equality and JSON-restored reducer equivalence. All384 initial states and57,029 full initial/accepted records are retained in `results/full-state-transitions.jsonl.gz` (about5.2MiB). All episodes terminated; zero invalid transitions, stalls or source-hash failures. A separate implementing-author reaggregation matched every final-state/trajectory hash and action count; it is **not independent reviewer evidence**.

## Results and retained negative outcomes

These48-run-per-kit generation2 pooled rows span both combat policies and both reward arms. They are descriptive correlated seed repeats, not48 independent players. Final HP includes defeats; actions are reducer steps rather than elapsed play time; cumulative received HP loss can exceed final-health differences because camps/victory effects heal the hunter.

| Generation2 kit | Completed victories | Mean final HP | Mean accepted actions | Mean turns | Mean hunter HP damage |
| --- | ---: | ---: | ---: | ---: | ---: |
| Default | 48/48 | 48.42 | 149.65 | 19.92 | 53.90 |
| Pursuit | 48/48 | 44.60 | 139.19 | 18.46 | 53.54 |
| Vigil | 48/48 | 45.88 | 153.60 | 22.08 | 61.73 |
| Ash | 47/48 | 42.02 | 144.50 | 20.67 | 67.40 |

Across both generations, default wins96/96; each candidate wins95/96 and introduces one paired loss, with no rescue because the baseline has no defeats. Pursuit lowers final HP in58/96 pairs while saving11.29actions and1.51turns on average. Vigil lowers HP in58pairs, uses more actions in68pairs and raises hunter damage8.24 on average. Ash lowers HP in56pairs and adds12.60damage despite6.44fewer actions. These tradeoffs reject a blanket claim of improvement or per-seed nonregression.

All introduced losses occur at a Cantor final contract; exact contexts and full states are retained:

- Pursuit:58003,kind1,heuristic/frozen rewards; final fight starts52HP, loses after six turns. Legacy encounters/acquisitions can differ from the default, limiting attribution.
- Vigil:58012,kind1,learned/frozen rewards; final fight starts63HP, loses after eight turns. Protection/setup did not guarantee survival; legacy-world caveat applies.
- Ash:58009,kind2,learned/skip rewards; final fight starts64HP, loses after seven turns. Matched world, but policy treatment of control is a specific confound.

`results/paired-all.json` contains all288 baseline/candidate pairs; `negatives.json` preserves every introduced loss and joint lower-HP/more-actions negative; `negative-context/` contains the final twelve full-state records for each loss. No failed deck/result was deleted or retuned.

## Counterplay and model limits

The frozen learned policy has no feature for reduced future intent/reinforcement pressure. With skip rewards it plays **zero Silence casts** across both generations'24Ash runs, versus64casts from the existing heuristic. This is not evidence that control itself is useless. Learned was trained on the default kind2 starter; custom kits and kind1 are out of that training domain. Its earlier96/96versus95/96 success had26winning pairs with lowerHP and slower average pacing; those original negatives remain immutable and are not outweighed by a new victory percentage.

Four posthoc mechanistic branches were extracted from actual legal diagnostic campaign states. They were declared as exploratory **after** the primary matrix and are not new held-out wins, tuning, equal-resource campaign comparisons or human observations:

- Sunder then hound command spends one extra energy/card, removes armor and avoids the1retaliation HP loss observed in the direct-command comparison.
- Ready makes a formerly illegal second hound command legal; its actual attack ends the fight in the selected case, preventing4hunter damage and allowing the ordinary victory heal. Readying does not automatically attack.
- Aegis before a Cindermaw all-target breath reduces hunter damage8→3 and creature damage29→12 in its selected case, at the cost of two energy/card. It cannot be generalized to block-ignoring attacks.
- Silence before an announced Cantor all-target attack reduces actual hunter damage12→0 and creature damage19→7 in its selected state; other actual attackers still resolve. This demonstrates prospective counterplay omitted from the frozen linear feature vector.

Full before/action/after/events for every branch are in `counterplay/`. The chosen cases spend different resources from immediate end-turn/direct-command baselines; they explain tactical mechanisms, not superior policies. No automatic policy retuning or new rule/value patch follows.

## Recommendation and next gate

Retain the default as the sole shipped starter now. Invite a separately assigned gameplay reviewer to replay the immutable matrix, inspect Cantor failures and actual legal counterplay, and challenge kit identity/readability. Pursuit is the clearest next optional prototype because command tempo meaningfully differs; Ash needs a prospective-intent-aware evaluation and novice control comprehension; reject promoting Vigil as a safer option based on this data.

Do not revise these kits using the same held-out rows and then relabel a second pass as untouched. Any later iteration needs a new declared cohort and preserved first-pass failures. Prospective-player observation must assess whether preparation decisions are understandable, distinct, tempting and replayable. Automatic survival/pacing, content count and stronger model play cannot establish fun, AAA craft or Steam readiness.

## Separate auxiliary hunter annotation clarification

The hunter renderer researcher requested an art-author source-point check while this exterior research ran. `auxiliary-hunter-annotation-review/` is **not kit evidence**. Actual unchangedR3source Canvas overlays show supplied recovery seal(328,232) onbelt/vial rather than the held goldring. Estimated actual ring centers (±3sourcepx) are idle(323,235),anticipation(268,219),command(222,221),recovery(283,172),reaction(250,180),collapse(244,290). Parent/hunter researcher were informed; frozen runtime remained untouched. Independent renderer promotion is separate. Initial connection/view timing failures are recorded; corrected actual captures were inspected. No image pixel edit occurred.
