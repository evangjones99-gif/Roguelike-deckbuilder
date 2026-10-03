# v0.3 balance investigation — proposal, not an applied gameplay change

The frozen v0.2 engine and content remain unchanged. This investigation addresses the independent review's weak strict-solo transition and tests whether known-quarry preparation has measurable value in matched boss states. It recommends an experiment with cheaper creature removal, not a Cantor damage nerf or an immediate claim that a complete solo archetype is supported.

## Methods and precommitted holdout

The new harness uses its own deterministic action policy, without importing the game's heuristic, learned policy or reviewer policy. It validates every accepted state and aborts on rejection/incomplete runs. Engine and content hashes are checked against the reviewed v0.2 versions before execution. Evidence is preserved under `reviews/solo-v0.3/`; no previous review or release is overwritten.

Three distinct experiments avoid treating a seed label as a guarantee of identical encounters:

1. Complete progression runs compare two actual legal strict-solo policies (purchase-first versus removal-first), a clearly labeled proposal wrapper charging 15 gold instead of 35 for creature removal, and a diagnostic starting-deck replacement. The wrapper funds the 20-gold difference before the unchanged reducer charges its normal fee. Spell removal still costs 35. Those virtual treatments are not production rules. Whole-run purchases and removals change later RNG consumption; these comparisons evaluate the entire policy/proposal and cannot isolate one card.
2. A removal/acquisition factorial uses frozen single-encounter rosters, hunter HP, first intentions and RNG. Starter, remove-five-bindings, add-five-spells, and both treatments share deterministic card-slot ranks for their initial shuffle. Added cards are two Resonances, Silence, Witchfire and Draught. All states pass structural validation, but they are explicitly counterfactual fixtures, not collections earned through real progression. Normal nodes 1, 4 and 8, all three bosses at node 10, hunter HP 45/65, and difficulties 0/2 are tested. Later deck reshuffles consume RNG according to their different deck shapes; enemy formation remains fixed throughout the comparison.
3. Actual legal pack runs supply boss-entry health, relics and decks. One Scour slot becomes either the forecast quarry's counter (Sunder/Ironjaw, Silence/Cantor, Aegis/Cindermaw) or general-purpose Grave Tithe. Every arm shares the entire starting enemy state, health, RNG and card-slot shuffle. This isolates the selected slot intervention for this policy and draw fixture; it is not proof that a counter is mandatory or that the full progression route improves.

Pilot seeds are 12001–12024. Before executing untouched seeds 16001–16072, `holdout-prespecification.json` records the selected 15-gold creature-removal proposal, fixed harness/source hashes and success criteria. The proposal must improve Veteran strict-solo removal-first completion by at least 8/72, reduce stranded creature cards by at least one on average, and complete every simulation without invalid states. Residual Cantor weakness and negative counter-card outcomes must be reported.

## Pilot diagnosis

In 24 Veteran whole runs, purchase-first and removal-first each won 6. Cheap creature removal won 15, removed 4.96 of five starting bindings on average, and left 0.04 unplayed creature cards. Standard removal-first removed 2.71 and left 2.29. It lost 14 runs before the boss, compared with five under the price proposal. Those later paths are different, so the matched experiments carry the sharper causal evidence.

At node eight, Veteran, and 65 starting HP, strict-solo starter fixtures won 7/24 and ended at 8.25 HP on average including defeats. Removal alone won 24/24 at 47.13 HP; adding the spell packet without removal won 24/24 at 54.13; doing both won 24/24 at 60.38. The inherited dead-card density and affordable access to useful damage/control both influence survival.

At matched Veteran bosses with 65 HP, removal alone won 16/24: all Ironjaw/Cindermaw cases, zero Cantor cases. Adding the packet without removal won 20/24, including five of eight Cantors. Both interventions won 24/24, including all Cantors. A thinner inherited spell deck is not sufficient to clear servants while damaging their source. This supports separate transition access and quarry preparation questions; it does not establish an unfair Cantor.

Nineteen of 24 pilot pack routes reached their boss. In six matched Cantor entries, swapping an extra Silence into one Scour slot raised wins from five to six and mean final HP from 32.33 to 42.17. General Grave Tithe did not rescue that loss. Ironjaw's extra Sunder produced equal outcomes in all five entries. Cindermaw's extra Aegis reduced mean final HP from 34 to 32.25 without changing eight wins; generic sustain slightly helped. A named counter is an option, not an automatic best reward. This policy is less successful than the independent reviewer policy; selection of reachable entries and policy limitations are reported rather than hidden.

## Targeted proposal and player-facing promise

The next balance candidate is a **15-gold price for releasing a creature card**, while releasing a spell remains 35. This reduces the five-binding transition from 175 to 75 gold before any spell acquisition and keeps the normal five-card minimum. It uses an existing understandable transaction, avoids free starting power or global enemy inflation, and preserves the player's option to keep a pack. This proposal has not changed engine exports or shop UI. An implementation would need a per-card removal-price helper used consistently by legal actions, reducer, UI, save-independent tests and policy harnesses; the constant generic price must not disagree with the visible transaction.

Retain current Cantor damage/reinforcement timing pending separate review. Test whether actual reward/shop access can reliably offer Silence or area damage for a declared solo plan, without guaranteeing the best card or flattening all build decisions. The diagnostic five-spell packet is deliberately generous and is not proposed as a free reward bundle.

For the current release, describe Resonance and Dead Man's Coin as rewards for an **unbound opening**. A complete solo contract should remain an advanced experiment until humans can assemble it, understand removal costs, and prepare for the advertised quarry. A suitable observed session asks a player to forecast which card helps against the Cantor, explain their sacrifice at the shop, and decide whether the resulting run feels worth replaying. Agent wins cannot answer those questions.

## Prespecified holdout results

Untouched seeds 16001–16072 completed 864 full solo progression cases, 4,608 matched encounter fixtures, 72 actual legal pack preparation routes and 150 boss-intervention arms. Every accepted state validated and every simulation terminated. The prespecified proposal thresholds passed.

| Difficulty | Actual buy-first | Actual remove-first | Proposal removal 15 | Diagnostic prepared opening |
|---|---:|---:|---:|---:|
| Initiate | 62/72 | 56/72 | 64/72 | 72/72 |
| Hunter | 40/72 | 32/72 | 53/72 | 72/72 |
| Veteran | 16/72 | 16/72 | 45/72 | 72/72 |

Veteran removal-first left 2.26 unplayed bindings on average; the proposal left 0.03. Before-boss losses fell from 45 to 15. The whole-run proposal rescued 32 formerly losing seeds and newly lost three formerly winning seeds (16009, 16024, 16031), a net 29-win increase. Hunter rescued 26 and newly lost five; Initiate rescued 15 and newly lost seven. These negative outcomes are retained in `holdout-paired-analysis.json`. Different procurement changes future formations/draws, so this is not a promise that every seed or player improves.

The matched-factorial diagnosis replicated. At Veteran node eight with 65 HP, the inherited no-binding starter won 21/72, removal alone 72/72, acquisition alone 72/72 and both 72/72. Mean final HP including defeats was respectively 9.14, 47.33, 52.74 and 60.53. At Veteran bosses, the same arms won 0/72, 48/72, 66/72 and 72/72. Removal alone still won zero of 24 Cantor fixtures; adding the packet without removal won 18/24; both won 24/24. The generous prepared opening is a diagnostic upper bound and is not proposed as a free starting deck.

Fifty actual pack routes reached their quarry. In every heldout matched entry, original Scour, quarry-counter and general-sustain arms all won. Additional Silence improved Cantor mean final HP from 35.14 to 41.36 across fourteen entries; Grave Tithe reached 37.86. Extra Sunder reduced Ironjaw mean HP from 46.05 to 44.32 while modestly shortening mean combat from 6 to 5.64 turns. Extra Aegis raised Cindermaw mean HP from 39.79 to 41.14 but lengthened mean combat from 6.43 to 6.64. These are tradeoffs for one policy and collection state. The pilot's rescued Cantor loss did not repeat as a heldout win difference, so a universal best-counter or survival-superiority claim is rejected.

## Transparent secondary metric repair and economy controls

The independent gameplay reviewer identified a secondary metric defect in the prespecified harness: `fight()` counted creature cards in the existing terminal hand again when an end-turn action caused defeat before a new hand was drawn. Wins, HP, removal spending and remaining deck bindings were unaffected. Original pilot/holdout evidence and the exact r1 harness are preserved. Revision two fixes `drawDead` only when the state remains in battle after end-turn and writes separately named `*-r2-*` artifacts with its own source hash. A paired rerun checks unchanged primary outcomes; the original prespecified result remains the basis for the table above.

Before any price patch, revision two adds fresh seeds 20001–20072 for ordinary-pack, widow-hybrid and lean-pack procurement controls at all three difficulties. The ordinary pack never removes a creature, so both prices must produce identical relevant records; any discrepancy would be a harness defect. Widow hybrid removes nonspiders and retains spider spell support; lean pack removes spiders while retaining creature commands. The policies, seeds and reporting criteria were fixed in `controls-prespecification-r2.json` before execution. The 1,296 full control runs completed without invalid or incomplete states. All 216 ordinary-pack price pairs had identical phase, health, collection and gold, satisfying the negative control. Widow-hybrid wins changed 67→68 Initiate, 44→55 Hunter and 26→28 Veteran. Four creature removals cost 140→60 gold, allowing about 1.75 additional purchases per run. Lean-pack wins changed 72→72, 66→65 and 47→49; the Hunter result is a small negative outcome that must not be hidden. Both active sculpture policies had gains and newly losing seeds, retained in `controls-r2-summary.json`. The experiment does not show a runaway completion increase, but cheaper sculpture does change economy pressure and does not establish universal nonregression. A broad cheaper-removal patch remains withheld pending independent review and a repeat with decoupled encounter sampling. Revision-two replay verification confirms all 4,608 heldout fixture outcomes and the complete primary summary are identical to r1; 489 secondary rows lost 1,271 duplicate terminal-hand counts. `drawDead` counts creature cards drawn; they are dead cards only for the strict no-binding policy, not for binding-capable control policies.

No gameplay patch or human enjoyment claim is authorized by this proposal document alone.


## Next mechanics candidate: separate encounter sampling from deck actions

The independent reviewer tested nine real first-reward states across seeds 6501–6503 and all difficulties. Reward-versus-skip changed the immediately following enemy formation in six of nine pairs despite equal HP, node and route. In Initiate seed 6502, skipping gave Reaver/Thrall while taking any of Witchfire, Scour or Silence gave Reaver/Revenant. Thirty-six valid legal branches are retained in `reviews/gameplay-v0.3-evidence.json`. The cause is concrete: battle setup consumes deck-shuffle RNG before sampling its enemy formation. A reward changes deck length and therefore the world sampling point.

The full-policy price outcomes above remain legitimate complete-run observations, but newly losing seeds can partly reflect environmental sampling changes rather than an intrinsically harmful card choice. The matched encounter fixtures were designed to prevent that confound. Before interpreting price/reward changes as causal progression improvements, the next runtime candidate should sample formations from an independent deterministic run-seed/node/encounter-kind stream. Reward/shop offers should likewise have their own identified stream if their fair comparison is required. Keep draw randomness within the battle stream so different card use still changes card cycling naturally. Do not silently reroll the named final quarry.

Acceptance criteria for a future, separately versioned patch:

- Same normalized run seed, actual node, difficulty and route choice must produce the same initial enemy family formation after different legal reward purchases, removals or earlier draw actions.
- The same seed and map-node shop/reward identity must produce an unchanged offer if deck composition changes; the offer's selection itself can still alter subsequent play.
- Different seeds should retain encounter variety, every actual formation remains in its intended normal/elite pool, and all three final quarries stay forecastable.
- Serialized replay remains exact, enemy intentions preserve their readable timing, corruption checks retain card-copy conservation, and old released engines/data stay archived.
- Run fresh matched whole-run acquisition/removal comparisons after decoupling; preserve this coupled-stream evidence and report that changed world sampling invalidates a direct historical same-seed victory claim.

This is a proposal informed by a reproducible observed mechanism. It has not changed runtime RNG, content, save schema or v0.3 balance.


## Current decision and next experiment

The prespecified strict-solo proposal passed its heldout criteria, while the fresh controls exposed broader economy effects and a small negative Hunter lean-pack result. The recommended order is now: (1) prototype and review independent world sampling; (2) repeat price/collection comparisons with the same encounter schedule; (3) decide whether to ship a removal-price change, a narrower explicit conversion option, or retain the current economy. v0.3 runtime should remain frozen through its presentation milestone. No full-solo marketing promise or blanket enemy nerf follows from this evidence.

Reproduction: the current revision-two harness supports `npx tsx scripts/solo-investigation-v0.3.ts holdout 72` and `npx tsx scripts/solo-investigation-v0.3.ts controls 72`. It writes new r2 artifacts; original prespecified r1 artifacts and source snapshot remain immutable. `reviews/solo-v0.3/metric-repair-verification-r2.json` verifies unchanged primary results. All automated evidence remains separate from human judgment about choice quality, cost readability and replay motivation.
