# Independent gameplay review — Lanternbound v0.1.0

**Decision: accept as a playable prototype for continued iteration; reject promotion as a very high quality, fun, Steam-ready game.** This is an independent agent judgment. It is not a human enjoyment result. The combat has a coherent identity and meaningful targeting, but the current content and progression do not sustain the requested quality claim.

## Scope and reproducibility

Reviewed the frozen renderer-independent engine/content and integration notes. Created `scripts/review-playtest.ts` without importing the existing heuristic, learning script or learned policy, and completed **864 actual seeded engine runs** through `legalActions` and `applyAction`: seeds 1001–1048, six policies, difficulties 0/1/2. Every accepted action changed the state and passed `validateState`. All runs terminated in victory or defeat within 3,000 actions. I inspected complete action traces for seeds 1001 and 1002 across policies and the hardest difficulty. These are deterministic agent simulations, not browser play sessions or human playtests.

Evidence: `reviews/gameplay-v0.1-experiments.json` contains outcomes, encounter summaries, decks, economy, rests, upgrades, source hashes, and full action/state traces for the first two seeds of every policy/difficulty pair. Reproduce with `npx tsx scripts/review-playtest.ts 48`. The review script passed `npx tsc --noEmit` at the time of review. Implementation files were not edited.

Frozen SHA-256:

- `src/engine.ts`: `ed14d3e3394d760284694a56d50f4303ad320ecd65cfe25b14e23d1279c74fe5`
- `src/content.ts`: `c64b68b7813ca4e923faf7b23ca36f871522772efc713fa1134bcbcfe06a9a71`
- Reviewer harness: `86e381b45e20aedcae2b97dba8b69d05da703ddf831ffcba4241bd6be3e79b26`

This review does not evaluate graphics, animation, audio, controller support, onboarding comprehension, real play duration, or desktop/Steam integration. Those require the finished client and separate reviews. No assertion here constitutes Steam approval.

## Method and outcomes

Each policy ranks currently legal actions, without future-state search. Combat usually deploys companions, commands them at no energy cost, prefers lethal attacks, buffs an existing pack, and uses defense when announced damage makes it useful. Threat-aware policies prioritize piercing Wisps and dangerous Witches. Policies differ in progression and target priorities:

| Policy | Progression and combat variation |
|---|---|
| Pack | Prefer pack scaling/healing rewards; take all three available elites; one shop; rest below 35 HP, otherwise train. |
| Spells | Same route/combat; prefer offensive/support spells and more removal; this still uses starter companions eagerly. |
| Starter | Same elite route; skip every reward, purchase and removal; camp upgrades/rests and automatic elite relics remain. |
| Front focused | Same progression preferences as Pack; prioritize front enemies instead of species threat. It is a policy comparison, not an isolated action replay. |
| Safe route | Choose the early event and normal fights instead of elites; keep one shop and three camps. |
| Bare starter | Normal fights, one ignored shop, skip every reward, always rest; no purchases, removals, upgrades or relics. |

All policies use the same fixed deck-management and combat rules except the stated differences. Different choices consume RNG differently, so a common initial seed does not guarantee identical later encounters. Runs are paired by seed, not independent human samples; no statistical population claim is appropriate.

| Policy | Story wins | Normal wins | Hard wins | Hard mean final HP / 65 | Hard lowest HP seen | Hard mean rests |
|---|---:|---:|---:|---:|---:|---:|
| Pack | 48/48 | 48/48 | 48/48 | 45.40 | 6 | 0.15 |
| Spells | 48/48 | 48/48 | 48/48 | 44.85 | 7 | 0.15 |
| Starter | 48/48 | 48/48 | 48/48 | 40.06 | 13 | 0.08 |
| Front focused | 48/48 | 45/48 | 38/48 | 22.79 | 0 | 0.67 |
| Safe route | 48/48 | 48/48 | 48/48 | 37.04 | 8 | 0.27 |
| Bare starter | 48/48 | 48/48 | 48/48 | 42.19 | 25 | 3.00 (forced by policy) |

The high win rate alone does **not** establish poor gameplay: there is genuine HP pressure, and correct targeting has a substantial benefit. More telling is that five reward skips, zero purchases, and zero removal are sufficient on the elite route at every difficulty. Even the completely unenhanced starter deck wins all hard seeds on the normal route without relics. The latter comparison also changes encounter difficulty and forces rests; it does not prove that upgrades/relics have no value.

Pack on hard averages 18.33 player turns across six battles. Its boss ends on turn 4 in 18 runs, turn 5 in 28, and turn 6 in 2. The engine's `stats.turns` only counts completed nonterminal end turns, so it understates actual player-turn count; I used encounter `maxTurn` for these pacing observations. This says nothing about minutes of human play.

## Concrete play records

**Seed 1001, hard, Pack: victory at 65 HP, lowest HP 36, no rests, three upgrades.** All three elites awarded the three available relics. In boss turn 1, deploy Lantern Owl and Brook Otter, cast Spark at the Wisp, command both companions at it, then finish it with Briar Lance. This avoids its seven unblockable damage. The Crown's turn 2 quake leaves several companions badly wounded, making shelter/healing attractive, but immediate summons and card draw also compete for energy. On turn 4, six companions make Communion capable of healing 18 HP (15 actually restored to the cap), alongside Rally strengthening subsequent commands. Victory arrives on turn 5 before another quake resolves. This is a satisfying, legible engine-level sequence with multiple synergies, though enjoyment remains unmeasured.

**Seed 1002, hard, Pack: victory at 32 HP, lowest HP 29, no rests, three upgrades.** The boss opening hand contains only Ward/Ward/Rally/Rally/Rally with no companions, producing a dead opening turn against piercing Wisp damage. Turn 2 summons Cinder Fox+, Mossling+ and Cinder Fox, and directs their commands at the Wisp; turn 3 finishes it, deploys the remaining companions, and protects against the Crown's heavy attack. Three Rallies on turn 5 plus six commands end the battle. Draw order creates real risk, but the pack ramp overcomes it.

**Seed 1002, hard, Front focused: defeat on boss turn 3.** Its deck and six encounter compositions match the Pack run, making this a useful concrete comparison despite different earlier HP and action histories. It reaches the boss at 39 HP, keeps hitting the Crown while the Wisp remains at 19 HP, and takes repeated piercing hits. Turn 3 spends energy on two Sparks at the Crown rather than Ward, then dies to the heavy attack plus Wisp. Target/defense mistakes matter. This should not be described as a single-variable causal experiment.

**Seed 1001, hard, Starter: victory at 44 HP, lowest HP 41, five skipped rewards, zero purchases/removals, three upgrades.** It finishes with the original twelve-card composition, two enhanced Mosslings and enhanced Cinder Fox, and all three elite relics. Six battles complete in 2/2/3/3/3/5 turns. The prototype can be solved comfortably without engaging with deck acquisition.

## Strengths and limitations

**Combat decisions and counterplay:** Summon-now versus defense-now, attack allocation, avoiding overkill, buff-before-command, and recovering wounded allies are meaningful. Fixed announced targets make turn planning reliable. Wisp piercing gives an immediate reason to change target order. Sentinel armor and the Crown's guard/quake/heavy cycle create recognizable windows. Front-focused losses confirm that careless play can fail, even though threat-aware play is forgiving. The first-turn summon rules also matter: newly deployed companions do not retroactively attract announced attacks, so a summon is not a substitute for immediate hunter defense.

**Dominant structure:** Free repeatable commands, companions leaving the card cycle while alive, and permanent-in-battle Rally buffs make a stable pack plus rapidly recycling support spells the obvious engine. Starter Rally and Insight already provide this. Spells versus Pack primarily alters supporting cards; it does not demonstrate two fundamentally different winning archetypes. I did not run exhaustive optimal search or every possible card composition, so no individual card is proven globally dominant.

**Progression and economy:** The original twelve-card deck already performs well enough that acquisitions are optional. Hard Starter exits with 260 unspent gold on average; Pack exits with 118.54 despite 2.46 purchases and 0.75 removals. This is partly the route's single shop before three further combat payouts, not proof that prices alone are wrong. Choose upgrades currently means enhance the first eligible summon in deck order: it offers no targeted build decision. Successful Pack/Spell runs rest only 0.15 times per run at hard, so three camps mostly become automatic upgrades. High pressure often arrives in the boss after the last camp; that pressure cannot create an earlier recovery decision without forecasting it.

**Replay:** Twenty-four base cards have coherent fantasy and useful interactions, but there is only one event, two elite formations, three relics and one boss. Three elite visits necessarily repeat an elite formation and always grant every relic if all are won. The ten-node route choices are identical across seeds. Card/draw/encounter shuffling provides variation; the strategic skeleton changes little. An agent can identify promising tactical moments, but cannot infer long-term human replay motivation from these runs.

## Rubric and promotion gate

Scores are provisional reviewer judgments on a 1–10 scale: 5 means functional prototype promise, 8 means demonstrated professional strength with substantial validation. Unassessed areas are not given invented scores.

| Area | Score | Grounding |
|---|---:|---|
| Tactical decision quality | 6 | Threat/defense choices affect losses; command timing and pack support interact. |
| Enemy counterplay and variety | 5 | Distinct readable behaviors, but very few formations and one boss. |
| Build identity and progression | 4 | Coherent pack identity; growth is unnecessary and camp upgrades are untargeted. |
| Difficulty and recovery decisions | 4 | Hard can reach single-digit HP, but every threat-aware policy wins all sampled seeds and rests are rare. |
| Pacing potential | 6 | Short fights and a decisive 4–6 turn boss; browser input effort and human minutes unmeasured. |
| Replay motivation potential | 3 | Fixed route skeleton, tiny event/relic/boss pools, same pack ramp. |
| Human fun, visual/audio quality, accessibility, Steam readiness | Unassessed | No relevant human/client/platform testing in this review. |

Priorities for the next release:

1. **Make deck choices change the plan.** Add targeted upgrades and a few genuinely distinct archetype payoffs before indiscriminate card quantity. Test enemy mechanics that reward alternate plans, not merely more HP. Preserve forgiving Story difficulty.
2. **Broaden encounter questions.** Add an enemy or boss mechanic that changes the pack/Rally default and has an explicit, readable response. Expand elite formations and event outcomes; three elites should not guarantee the complete relic catalogue.
3. **Retune progression pressure as a whole.** Compare camps, shop timing, income, innate healing, scaling and draw reliability together. Do not use these win rates alone as justification for blanket damage inflation. Maintain a small number of intentional recovery decisions and viable reward-skip choices.
4. **Run human sessions before a fun claim.** Observe first-run comprehension, mistakes, unnecessary clicks, preferred rewards, remembered encounters and willingness to replay. Keep those results separate from agents and ML. The next version should retain these baseline artifacts and use fresh holdout seeds in addition to these regressions.

A reasonable next promotion gate is an independently reviewed client with no critical clarity failures, demonstrably different build plans on fresh seeds, explicit difficulty goals, and observed human replay interest. Until then, publish milestone builds as prototypes and preserve this review as the v0.1.0 baseline.
