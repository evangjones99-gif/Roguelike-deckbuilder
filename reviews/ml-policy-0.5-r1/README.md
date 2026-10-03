# v0.5 prespecified policy experiment

This experiment ran once against frozen rules. The implementing agent's checks below are not an independent gameplay review. No human feedback, synthetic enjoyment label, price change or automatic balance patch follows from these results.

Before any episode, `plan.json` fixed training seeds 46101–46116, held-out seeds 47101–47196, difficulty 1, schema 3/kind 2, six generations with six mutants each, and the inherited completion/progress/HP objective with a small action-count penalty. The lead received the frozen script hash before the plan-only checkpoint and data execution. The mutation RNG is separate from each random baseline episode's seed-derived action RNG. The learned policy was written and hashed before evaluation.

The run produced 592 training episodes and 288 held-out episodes. Every accepted state and every linear-policy legal preview validated; accepted transitions also checked incoming-state purity. All training and evaluation episodes terminated, with no stalls, invalid-state failures or source changes. Complete training rows, held-out rows, trajectory hashes, source snapshots, plan/policy hashes and the empty failure log are preserved here.

| Held-out policy | Wins | Mean HP including defeats | Mean actions | Mean turns |
|---|---:|---:|---:|---:|
| Legal random | 0/96 | 0 | 80.83 | 16.13 |
| Base linear | 95/96 | 45.22 | 145.27 | 20.23 |
| Learned linear | 96/96 | 48.00 | 148.72 | 20.41 |

The learned policy rescues seed 47179 and newly loses none in this cohort. It takes 3.45 more actions and 0.18 more turns on average, so the survival/health result is accompanied by slower play. This is a small held-out advantage near a completion ceiling, not evidence of exceptional general skill, meaningful acquisition choices or enjoyment. The fixed noncombat policy favors camps/ordinary fights, skips shops, and stops taking rewards at nineteen cards; other builds, elites, procurement plans and difficulties remain outside this experiment. Legal random is deliberately weak and is not a human benchmark.

Among the 95 pairs where both policies win, learned final HP is lower in 26 seeds, higher in 42 and equal in 27; the largest HP decrease is 17. It uses more actions in 65 of those pairs and more turns in 27, with a maximum eighteen extra actions. `paired-tradeoffs.json` preserves every paired delta and the seed lists. Better cohort completion and mean health do not establish nonregression for each run or better pacing.

`verification.json` is a separate reaggregation and mutation reconstruction by the same implementing agent, with zero episodes rerun. Its word “Independent” refers to computation separate from the episode writer, not a separate reviewer. It confirms all summary rows, hashes, snapshots, disjoint seed sets, all 36 generated mutant vectors, frozen final policy and paired rescue/loss lists. External independent review remains a separate gate. Both plan creation and reexecution against this completed output were tested and refused before episodes; no protected record was replaced.

| Artifact | SHA-256 |
|---|---|
| Frozen scripts/learn-policy.ts | aa1fa0e68b942e19b75b3f7dfe6a2036d5edc26e96f3976ad1f1688e9388a77d |
| plan.json | b3fef4ba27698f87677740a58d1a2c7e9615d8f07f2adae4e17ae8b4710bbb60 |
| policy.json | bd6c70f5bdf5f04d8edcb49f32737a485a62d364665a3c834759ad4c6368ddc6 |
| episodes.json | 6f8d0be9f80bc73ab170d62cee7ed16c18cbaf73ea7ebbbb5fb6c5d9ae9d4fac |
| training-episodes.jsonl | 64314820b0916d887f54c54cf883f58d319af8f5bfcd23ad57511415d78db64c |

The source snapshot preserves `source/src/{engine,content,world-rng}.ts` and `source/scripts/learn-policy.ts` with a minimal module package. These are rules provenance, not a hash of the final graphical build. Exact runtime source hashes are in the plan and report. Node v24.19.0 executed the run; TypeScript validation passed.

To independently replicate without overwriting history, copy the preserved `source` hierarchy into a fresh temporary directory, run the copied script from that copied source root using an installed tsx entry point, and choose a nonexistent output directory outside the preserved snapshot. Default run mode writes its plan before episodes; `--plan-only OUTPUT` followed by `--execute-plan OUTPUT` makes the same checkpoint explicit. Execution accepts only its pristine, source-matching plan once; completed or partial outputs are refused. An independent replication is a new experiment, not an overwrite of this one.
