# Final-strike readout — exterior author R1

**A main-only presentation proposal ready for separate independent review. Not shipped; no AAA, fun, native or Steam approval.** Root source remains untouched. This packet starts from frozen runtime23477 and does not contain the separately reviewed scene-coherence or hound-jaw changes.

## Problem and resulting behavior

The genuine UI-only campaign review, `agent-ui-playtest-v08-seed242113/REVIEW.md`, reports an elite's4/21HP beside “Quarry down” after450ms, a dragon's9/35 and a final Thrall's2/11. Original unedited evidence remains at its prior paths. The held buttons also keep old threat/readiness aria labels. This author did not conduct that campaign or borrow its independence.

During the existing final-strike hold, this proposal shows the actual post-resolution unit HP, attack and remaining visible block, accurate health bars and current disabled-control labels. A0HP enemy says “Quarry down”; a0HP ally says “Binding lost”; living allies say “Survived”; living enemies on defeat say “Still standing.” Hunter HP/maxHP/block reflect the canonical result, including contract-clear healing and unspent armor on piercing self-damage defeat. Ready/selected/target markers no longer invite held input.

Ordered actual engine events reconstruct presentation-only clones of the before roster. Death is inferred only from actual HP/death observations; absence from the after roster alone never means death. Winning clears surviving bindings from canonical state, while the dramatic field still holds those figures. Canonical surviving actors reconcile silent turn resets, including enemy block. A real on-binding entry attack can clear the fight before its new creature's ordinary UI render; only that affected roster is constructed with the actual summoned unit. Other roster controls retain their nodes. No new save fields, local storage keys, rules, RNG, economy, input bridges, telemetry, art pixels or animation timings are introduced.

## Exact identities

- Baseline: `23477f68c99d6d60b0b3f82b286a8d33bb6da6f2ca92c103fbecf5663634959f`,76inputs/55outputs.
- Candidate: `5952c4cc5d96b74af3946282da0d6f700ecb60aecc839ce09b2e195c906fdd44`,76inputs/55outputs.
- Only changed runtime input: `src/main.ts`, `4a3926b392ae6f21d981af6e8b5d44e7e9a664fdf8ab3212771380128cce5c03`.
- Original main: `acce54d9bb6b568c6c30089c8b9a8cf6e4d80cc136151777a69aefd20964dfcc`.

`SOURCE-BUILD-IDENTITY.json` records every source/output hash and explicit immutable-media prerequisite. Mutable source/config/package text is copied into `prototype`; original PNG/WAV inputs are declared external immutable references with assembled aliases. `prototype/dist` retains the actual tested build. These references are not standalone media backups. Dependencies are the installed root node_modules with the pinned lockfile. `main-only-r1.patch` is the semantic integration proposal; root must merge it separately with other main changes. No version bump was made for this unaccepted development proposal.

## Verification and acceptance criteria

Strict build and all87 existing rules pass. Fourteen real engine transitions across both save schemas exercise the exact extracted projection, plus one nonfinite/negative/unknown-target guard context; no before/result/event mutation occurs. This is author testing, not an independent gate.

`VERIFICATION-SUMMARY.json` counts56 completed actual production-browser contexts/actions/reloads:28 baseline and28 candidate. Four guard contexts intentionally repeat earlier scenarios with additional visible block instrumentation. Primary observations are the30 completed rows in `actual-ui-failure-r5.json`,18 in `actual-ui-results-r6.json` and8 in `actual-ui-results-r7.json`. The failed R5 active context is excluded from successes.

The natural-clock tests use schema-valid, **unearned diagnostic saves**, actual ordinary actionable UI controls, headless muted software Chromium, and exact engine results as a diagnostic oracle. They are not a human/independent strategic playtest. Core cases cover elite recovery, lethal armor retaliation, self-healing command, ward command, boss victory, area-hit defeat and lethal entry summon in both schemas. Supplements cover six-enemy entry kills with sixth binding, surviving enemy guard, piercing self-damage defeat, missing/delayed original pose media, active1280→390 resize, initial reduced motion, a verified simulated hidden-document value and denied arena2D context. The latter two prove controlled presentation fallback, not operating-system background/native behavior.

Acceptance requires matching numeric HP and aria labels during the natural450ms hold; zero HP/bar for actual deaths; actual positive HP/block for survivors; truthful hunter recovery/block; disabled stale controls; immediate and settled canonical save equality; unchanged settings/tutorial/storage keys; actual reload preservation without a held battle; and no page errors. All those candidate assertions pass in their applicable contexts. Original arena source and75 other runtime inputs are byte-identical. Natural screenshots retain the actual death field; no frame-perfect Canvas pixel comparison, listening or hardware performance claim is made.

## Preserved failures and limits

First strict-build staging lacked copied test-only simulation/legacy imports; the original failed log remains, followed by corrected build/rules logs. Early browser harness attempts accidentally reinitialized their own save on reload, used an invalid unquoted numeric CSS selector, and checked a literal-backslash regex. These failures and all successful partial rows remain. The R5 hidden-document mock became an out-of-scope TSX `__name` helper; exact serialized-source evidence is retained, and R6 used a verified literal value override. None required changing candidate production source.

Screenshot filenames are unique for each attempt. Earlier probes lacked an explicit exclusive screenshot write, but reused no names; R6/R7 write returned screenshot bytes with `wx`. No old screenshot was overwritten. Future outputs must remain exclusive.

Other held resources and the previous hand remain the existing battle context until settlement; this proposal specifically repairs actor health/stat/label consistency. The separate ten-route-stages versus “Contracts faced” wording finding is not folded into this packet. Independent reviewers may reject presentation timing, labels, layout, scope or craft. Fresh combined production/native checks remain required after an accepted semantic merge.
