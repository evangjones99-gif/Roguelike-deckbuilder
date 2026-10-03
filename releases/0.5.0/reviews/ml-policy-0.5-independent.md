# Independent audit: v0.5 policy experiment r1

**Decision: accept the preserved experiment as reproducible synthetic policy evidence. Reject claims of per-seed nonregression, proven superior general play, human enjoyment, AAA quality or a reason to adopt rules changes.** This is a separate reviewer audit, not the implementing agent's `verification.json`. No runtime, policy script, original source snapshot or experiment record was edited by this reviewer.

## Scope and actual work

Inspected `scripts/learn-policy.ts` and the preserved plan, source snapshot, execution marker, policy, report, README, failure log and datasets under `reviews/ml-policy-0.5-r1/`. Independently reaggregated **all 592 training rows and all 288 held-out rows**, reconstructed all 36 mutation vectors and generation selections, and checked every summary, seed/generation label, objective value, weight-vector hash and dataset hash.

Copied the frozen `source` hierarchy into `/tmp/ml-v05-independent-j35nrwxr/source` and ran its unmodified script with the installed tsx CLI and Node v24.19.0 into a new output directory `/tmp/ml-v05-independent-j35nrwxr/replica`. The complete independent run exited successfully. Its plan, execution marker, policy, 592 training records, 288 evaluation records, report and empty failure log are **byte-identical** to the original. Thus all 880 trajectory hashes and recorded outcomes reproduce, not merely the aggregate win counts. The first launcher invocation used an unavailable `/usr/bin/node` path and started no episodes; the subsequent invocation used the actual installed Node path. This was one completed independent replication, separate from the original experiment.

On the completed replica, independently attempted both `--plan-only` and `--execute-plan`. Both refused before episodes, and a recursive before/after hash comparison found no record changes. The original experiment was never targeted by these refusal tests. Temporary replica outputs are audit working files; preserved original snapshots and hashes below remain the reproducible source of truth.

## Reproducibility identity

Every working source file and its original/replica snapshot matched the plan's hash at audit completion:

| Frozen input | SHA256 |
| --- | --- |
| `scripts/learn-policy.ts` | `aa1fa0e68b942e19b75b3f7dfe6a2036d5edc26e96f3976ad1f1688e9388a77d` |
| `src/engine.ts` | `bfc9e61299d73a344569e54e4b3f3348009f4075560dc2f0fb057f5d8a4d296b` |
| `src/content.ts` | `2f45160b3e577a7cd44381cb361c4407661a68819ff827a24b8ab34ce15c4234` |
| `src/world-rng.ts` | `c4ea7b2bb7fc3fa3f0497111dae923566159d2b4143f01b646cb688d3223c1da` |

The following original and independent-replica files matched exactly:

| Evidence | SHA256 |
| --- | --- |
| `plan.json` | `b3fef4ba27698f87677740a58d1a2c7e9615d8f07f2adae4e17ae8b4710bbb60` |
| `execution-started.json` | `bd242385b772a2964110e24dc3d4194cb5e02624ea36aede43bf7ed735d88f61` |
| `policy.json` | `bd6c70f5bdf5f04d8edcb49f32737a485a62d364665a3c834759ad4c6368ddc6` |
| `training-episodes.jsonl` | `64314820b0916d887f54c54cf883f58d319af8f5bfcd23ad57511415d78db64c` |
| `episodes.json` | `6f8d0be9f80bc73ab170d62cee7ed16c18cbaf73ea7ebbbb5fb6c5d9ae9d4fac` |
| `report.json` | `0cf53815455fe28e51cfafc6516b4f2ac523ebc324617d4cd6fad019f8e6611f` |
| Empty `failures.jsonl` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

These identify the rules experiment, **not** the evolving graphical/runtime release build. No native platform, rendered frame, controller or audio acceptance follows from these hashes.

## Plan, selection and held-out separation

The preserved plan fixes schema 3 / rules generation 2, difficulty 1, training seeds 46101–46116 and evaluation seeds 47101–47196. Both lists are complete, ordered, unique and disjoint. Training has 37 candidate cohorts of 16 seeds: the base vector plus six generations of six mutants. It contains 588 victories and four defeats; all failures of weaker mutants are retained. All 880 episodes terminate without stalls or invalid-state failures; the largest recorded action count is 178, below the 700-action ceiling.

The eight-feature linear policy uses the preregistered objective `(win ? 100 : 0) + floor*3 + hp*0.1 - acceptedActions*0.002`. Independent reconstruction of the separate xorshift32 mutation stream, generation-center rule, clamping, strict-greater selection and all candidate weight hashes reproduces the history and final vector. The best training score rises from 134.474125 to 134.87775. Mutants are selected only using the 16 training seeds; no held-out result appears in that selection loop. The random baseline has a separate episode-local action RNG, and every stored random-action seed matches its prescribed derivation.

The source writes and hashes the learned policy before beginning any evaluation, verifies that hash before each held-out episode and after evaluation, and guards frozen source hashes. Accepted transitions check reducer purity, legal acceptance, state validation and generation labels; each linear-policy action preview is validated. The independent replay reproduced these checks without failures. File modification times are consistent with the plan preceding execution and the policy preceding the evaluation dataset. The lead's earlier receipt of the frozen script hash is reported in the README; this reviewer did not independently observe that historical exchange. Filesystem times and in-repository hashes are not externally authenticated preregistration. The inspected code/data support separation within this experiment, but cannot rule out undisclosed earlier experimentation or prove that every future cohort is untouched.

## Independently recomputed held-out results

| Policy | Victories | Mean final HP, including defeats | Mean accepted actions | Mean turns |
| --- | ---: | ---: | ---: | ---: |
| Legal random | 0/96 | 0 | 80.833333 | 16.125000 |
| Base linear | 95/96 | 45.218750 | 145.270833 | 20.229167 |
| Frozen learned linear | 96/96 | 48.000000 | 148.718750 | 20.406250 |

All reported summary fields match the raw records. The learned policy rescues **seed 47179** and introduces no additional defeat in this cohort. At that seed, base loses on contract 10 after 132 actions / 20 turns; learned wins with 19 HP after 168 actions / 25 turns. Completion improves by one seed out of 96 near an already high ceiling. This is a small descriptive advantage in the specified cohort, not robust evidence of broader superior skill.

Paired tradeoffs matter:

- Learned final HP is higher on 43 seeds, lower on **26**, equal on 27. The largest decrease is seed 47173: **59 HP to 42 HP**, with actions rising 143 to 151 and turns 20 to 22.
- Learned uses more actions on **66** seeds, fewer on 20, equal on 10; turns increase on 28, decrease on 15, remain equal on 53.
- Across all 96 pairs, learned gains 2.78125 mean HP while adding 3.447917 mean actions and 0.177083 mean turns. Across the 95 joint victories alone, it adds **3.105263 actions and 0.126316 turns**, while gaining 2.610526 HP. Slower play therefore remains after excluding the rescued campaign.
- Every base/learned trajectory hash differs. This establishes different simulated trajectories, not necessarily meaningful or enjoyable player choices. The random baseline's shorter episodes reflect earlier defeat and cannot be interpreted as better pacing.

The implementing agent later added `paired-tradeoffs.json` and corresponding README detail during the review window. The protected source, plan, policy, training/evaluation datasets and report hashes remained unchanged. The paired numbers above were computed independently from `episodes.json`, without relying on that added derivative.

## Limits and follow-on use

The experiment exercises one starting collection, one difficulty, consecutive fixed seed cohorts and a fixed noncombat acquisition/route heuristic. That heuristic prefers camps then ordinary battles, skips purchases at shops, uses a simple camp/event rule and stops accepting rewards once the deck reaches nineteen cards. The learned features govern battle action scoring; procurement, alternative build plans, elite routing, prices and difficulty balance were not learned or compared. The scorer uses exact detached engine transitions, not a player interpreting the rendered interface. Legal random is deliberately weak and is not a prospective-player benchmark.

The action penalty did not prevent the learned result from taking more actions. Do not quietly retune it on the evaluated seeds or relabel these outcomes as nonregression. Preserve this revision. Any stronger search, changed objective, additional difficulty, procurement policy or rules revision needs a new declared experiment and untouched evaluation cohort. This audit authorizes no automatic balance/economy change and no policy adoption into the game. Human first-run observation, strategic-choice feedback and graphical/interaction review remain separate requirements.
