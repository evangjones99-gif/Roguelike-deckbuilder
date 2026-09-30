# Independent gameplay review — HOLLOWPACT v0.2.0

**Verdict: a materially stronger development prototype, suitable for a preserved v0.2 development milestone after release checks pass. The reported target-identity defect is repaired and independently verified. AAA craft and exceptional human enjoyment remain unproven.** I do not endorse commercial Steam release from this evidence alone. Different boss win rates are not themselves a defect, and I do not recommend blanket damage tuning to equalize them.

## Evidence and limits

Read the frozen engine, content and `docs/ENGINE-v0.2.md`. Authored a separate deterministic policy harness, without importing the existing heuristic or ML policy, and completed **2,412 runs in the final evidence**:

- 2,268 runs: nine policies × three difficulties × 72 new seeds (6501–6572) plus 12 earlier regression seeds (1001–1012).
- 144 additional Nightmare runs: Pack and boss-aware acquisition on untouched follow-up seeds 8001–8072. This tests an exploratory hypothesis raised by the first cohort.

All runs retain outcomes, encounter summaries, card use, progression choices and decks. Complete action/state traces are retained for the first three seeds of every policy/difficulty/cohort: 168 full traces across the final two evidence files. Every action came from `legalActions`, changed the state through `applyAction`, and passed `validateState`. There were zero invalid intermediate states and zero incomplete runs. The initial 5001–5048 exploratory experiment is retained separately; it is not pooled into the final table. Full evidence and recorded action traces are preserved losslessly as [final experiments](/workspace/Roguelike-deckbuilder/reviews/gameplay-v0.2-experiments.json.gz), [pilot experiments](/workspace/Roguelike-deckbuilder/reviews/gameplay-v0.2-pilot.json.gz), and [quarry holdouts](/workspace/Roguelike-deckbuilder/reviews/gameplay-v0.2-quarry-holdout.json.gz). Local raw JSON remains available; compressed copies retain every field and are the archive evidence artifacts. Policies/seed cohorts are not human samples or independent randomized treatments. Earlier choice changes alter future RNG consumption, so identical seed labels do not guarantee identical later formations or hands.

Also completed **two actual browser runs through rendered controls**, with no game-state injection: hard seed 5001 (Ironjaw, 195 actions, victory at 65 HP) and hard seed 6502 (Cantor, 185 actions, victory at 52 HP). At every action, the browser's saved phase/floor/turn/HP/energy/hand/creatures/enemies matched the independent engine trace. Neither browser run generated a page error. They exercised first-time help, three targeted upgrade dialogs, purchases, removals, enemy targeting and reinforcements. Browser evidence and screenshots are retained as `reviews/gameplay-v0.2-browser*.json/png`.

These are automated agent playtests and reviewer judgments. They do not measure human fun, comprehension, replay intention, real play time, controller comfort, sound quality, animation feel or Steam integration. Browser runs used Chromium at 1440×900 with audio muted and motion disabled. A visually coherent still frame is not AAA validation. `npx tsc --noEmit` passed for the final harness.

Reproduce the final simulations with:

```sh
npx tsx scripts/review-playtest-v0.2.ts 72
npx tsx scripts/review-playtest-v0.2.ts 72 quarry
```

Frozen SHA-256:

- Engine: `21bafb33832ec2d3ee1ca4ead9486825510bd380b62e143a8736465f1ad4110b`
- Content: `2f45160b3e577a7cd44381cb361c4407661a68819ff827a24b8ab34ce15c4234`
- Reviewer harness: `70b43ab2c55186b521a759926d2343da0b98cf4b75b904dd098d0d4f7ef4e86e`

The v0.1 script, review and experiments remain untouched. This review does not retrofit the old verdict to make the new version appear successful.

## Fresh-seed outcomes

Pack, widow-spells, starter, front-focused, no-counter and boss-aware use a six-fight route with three elites, one shop and three camps. Rest below 39 HP, otherwise choose an explicit upgrade. Crypt chooses events and health-dependent elite detours. Bare starter takes normal battles, skips all acquisitions and upgrades, and always rests. Solo-attempt never binds a creature, prefers spell acquisition and creature removal, takes normal fights and shops, and pays for healing at crypts.

| Policy | Initiate wins | Hunter wins | Veteran wins | Veteran mean final HP | Veteran mean rests |
|---|---:|---:|---:|---:|---:|
| Pack | 72/72 | 72/72 | 69/72 | 41.15 | 1.11 |
| Widow spells | 72/72 | 72/72 | 69/72 | 31.24 | 1.36 |
| Starter, upgrades/relics retained | 72/72 | 72/72 | 65/72 | 25.58 | 1.42 |
| Front-focused targeting | 72/72 | 63/72 | 53/72 | 26.26 | 1.11 |
| No Silence/Sunder/recoil awareness | 72/72 | 72/72 | 69/72 | 36.44 | 1.08 |
| Bare starter, all rests | 72/72 | 72/72 | 63/72 | 36.89 | 3.00 (forced) |
| Crypt detours | 72/72 | 72/72 | 69/72 | 37.22 | 0.47 |
| Boss-aware acquisition/upgrades | 72/72 | 72/72 | 70/72 | 38.44 | 1.10 |
| Solo-attempt, no creature commands | 61/72 | 47/72 | 19/72 | 8.31 | 0.00 (shop route) |

Mean final health includes defeats at zero HP. The earlier-seed regression cohort also completed cleanly; hard Pack won 11/12 and bare starter 8/12. The unchanged acquisition-free strategy is still viable but has less margin than an assembled pack. Story/normal high wins for these deliberate policies preserve accessibility. These policies know exact engine rules; their win rates are not novice difficulty estimates.

The no-counter policy avoids buying, selecting or upgrading Silence/Sunder and ignores recoil when commanding. Its result shows that these new tools are useful options, rather than mandatory keys for every hard run. It does not isolate the causal value of one card: removing them also changes deck choices, RNG and target sequences. I corrected an exploratory policy confound that previously spent resources on tools it refused to play; the final result uses the corrected policy.

## Are progression decisions consequential?

**Targeted upgrades now change a plan.** On hard Pack's 72 runs, selected upgrades included 55 Surveys, 39 Edicts, 26 Silences and 16 Cairn Hounds. Widow-spells emphasizes Ash Widow and offensive tools instead. The browser upgrade dialog exposed individual duplicate entries and exact before/after effects. This addresses v0.1's automatic first-summon upgrade limitation. Enhanced Silence's lower energy cost and upgraded draw/buff values give credible alternatives to pure creature stats.

**Recovery is a real opportunity cost.** Pack averages 1.11 rests across three camps at hard and widow-spells 1.36. This is materially more active recovery decision-making than the v0.1 review's 0.15 hard Pack rests, though the seed sets, rules and policy are different, so this is a directional comparison rather than an isolated balance experiment. Pack seed 6501 reached 1 HP during its run, spent two camps resting, and still won at 20 HP. Increasing pressure alone is not the objective; choosing how to recover without losing a build opportunity is.

**Crypt choices affect survival and deck shape.** Hard Crypt used 72 oaths, 77 surgeon bargains, 28 purges and 39 gold picks. Purge is conditional on health/deck size in this policy. A health-paid relic, paid recovery and removal compete, and the actual cost is visible. This demonstrates reachable, meaningfully different consequences; it does not prove an optimal event policy. The same crypt still appears repeatedly rather than providing narrative/event diversity.

**Shop acquisition is helpful but still optional.** Hard starter skips every reward, purchase and removal and wins 65/72, with lower final health than Pack. Pack buys support, damage, control and several creature families; widow-spells acquires more spiders/offensive tools and averages 6.65 final binding cards versus Pack's 7.17. Their resource use differs, but both retain starter commands; this is a spell-supported pack, not a demonstrated pure spell archetype. Mean leftover gold is 116.39 for Pack, 257.57 for Starter and 214.58 for Crypt. Crypt deliberately takes no shops. That route choice and terminal pay explain much of the surplus; price inflation is not automatically the right fix.

**Pure solo remains expensive to assemble.** Solo-attempt ends with 2.61 unplayed creature cards on average despite preferring their removal, and loses 53/72 hard runs: 24 in normal fights, 29 in bosses. Seed 6503 does win against Cindermaw on turn 13 after removing four creatures, while 6501 dies at floor 4 and 6502 at floor 8. Resonance/Dead Man's Coin create a useful no-binding opening, but the inherited five-creature deck, three-shop opportunity cost and fragile early combat make this strict strategy difficult. This is a deliberately demanding policy, not proof that every solo strategy fails. Present the effect as an opening payoff unless further testing establishes a full removal archetype; investigate acquisition/removal paths before buffing damage blindly.

## Cantor pressure and preparing for the quarry

The final boss is forecast early and stays fixed by seed. At hard, the 24 Cantor-seed cohorts produced 21 Pack wins, 23 widow-spells wins, 17 starter wins and 15 bare-starter wins. Other Pack/bare cohorts won 24/24. These are **whole-run wins grouped by final quarry**, including any early deaths; they are not conditional boss win rates.

**Cantor is a legitimate build check with readable responses, not demonstrated unfairness.** Reinforcements receive a response window, the source can be killed or silenced, commands can clear thralls, and healing/protection preserve wounded creatures through the area attack. Even starter-only plans win many hard Cantor runs. More pressure than Ironjaw is acceptable. Random offer access and long-term survival may still influence difficulty; no exhaustive search was performed to establish that every losing seed had a winning plan.

The boss-aware policy changes reward/shop/upgrade preferences toward Silence, Witchfire and protection for Cantor; Sunder for Ironjaw; and Aegis/endurance/healing for Cindermaw. It was conceived after the first cohort, so those results are exploratory. On untouched seeds 8001–8072, it won **72/72**, compared with Pack's **70/72**. Its mean final health was slightly lower (38.76 versus 40.86), so this is not universal superiority. The two changed outcomes include one Pack death before the boss. Different rewards change subsequent RNG and formations; this is evidence that deliberate planning can alter a run, not proof of a single counter card's causal effect.

Seed 8023 is a useful example: Pack died to Cantor after entering at 53 HP; the boss-aware deck won at 18 HP, with more readying/protection/Harpoon support and fewer pack buffs. Both had enhanced Silence. That outcome argues for testing known-quarry preparation as a broader deck question rather than simply reducing Cantor's numbers.

Browser seed 6502 further demonstrated the counterplay: Silence canceled Cantor's 13-damage litany on turns 2 and 5; four thralls were raised across the fight and received visible turns before acting. Victory arrived on turn 6. It was possible to plan around the source and its servants rather than requiring every reinforcement to be prevented.

## Reported client defect and craft gate

**Duplicate binding intent identity was ambiguous in the observed build.** The Cantor browser screenshot shows two identical Cairn Hounds at 9/9 HP; both thrall intents say “7 damage → Cairn Hound”, despite targeting one specific UID. The roster, dossier and accessible description omitted binding-slot identity. A player deciding which copy to heal could not confidently identify the announced target. This is a concrete clarity defect in the core tactical promise, not a subjective graphics complaint. Reported to the lead as an archive blocker; the lead repaired it using exact binding numbers. A phase-stale “Contract cleared” toast also appeared over the boss during rapid play; clearing travel feedback was accepted.

Independent repair verification passed against the rebuilt production client at port 4173. I resumed the valid hard-6502 turn-2 state reconstructed solely from legal actions: Cairn Hound copies carry B1/B2 badges, accessible names distinguish binding 1/2, both thrall intents identify binding 1, and the inspection dossier identifies that same copy. I then played a fresh first battle through rendered controls and verified that the real victory notice disappears after reward acceptance and travel. There were zero page errors. This targeted verification uses a legal saved-state fixture and a short fresh fight, rather than another complete run. [Repair evidence](/workspace/Roguelike-deckbuilder/reviews/gameplay-v0.2-target-repair.json) and [screenshot](/workspace/Roguelike-deckbuilder/reviews/gameplay-v0.2-target-repair.png) retain the checks. The client served build provenance `006db8571a5c1697b21bcbe51434161e53bb75580c5b72bed852efdd4da7bee9`, main SHA-256 `9fe8938578533af5896ccfcabef86dff5986a44e8ea6f949417a596d4aa39a7d`, and style SHA-256 `ee165e5cbaf5a8022f271fd61782b026d4d5610d964a965480ac882802d08716`. This closes the identified clarity blocker. Engine results remain valid because these are presentation repairs. The browser artwork and roster organization are coherent and considerably more convincing than primitive placeholders, but disabled-card readability, combat motion, sound, input effort and accessibility still need their own testing. AAA quality cannot be earned by the number of simulated wins or generated assets.

Provisional 1–10 reviewer scores (5 = functional prototype promise, 8 = demonstrated professional strength):

| Area | v0.1 | v0.2 | Evidence |
|---|---:|---:|---|
| Tactical decisions | 6 | 7 | Exposed/armored commands, spell resistance, reinforcement timing and source/servant choices. |
| Enemy counterplay/variety | 5 | 7 | Four elite formations, three distinct forecast bosses, multiple readable answers. |
| Build/progression identity | 4 | 6 | Explicit upgrades and spell/widow/pack preferences; pure solo support still uncertain. |
| Difficulty/recovery decisions | 4 | 6 | Camps and surgeon bargains carry an opportunity cost; strong informed policies retain high success. |
| Pacing potential | 6 | 6 | Hard Pack averages 23.24 actual player turns across six fights; human minutes/click burden unmeasured. |
| Replay potential | 3 | 5 | More final contracts and relic subsets, but fixed ten-node skeleton, one crypt and small card pool. |
| Human fun, AAA craft, Steam readiness | Unassessed | Unassessed | Needs observed humans, motion/audio/controller/platform reviews. |

Maintain the repaired exact target readability; next test the solo transition and known-quarry preparation with observed humans and fresh agent seeds. Expand encounter/event questions where players predict the same answer, rather than adding quantity or equalizing boss win rates by default. Preserve both milestones and these independent findings. v0.2 can be a valuable development release while commercial/AAA promotion remains rejected.
