# Independent v0.5 engine and strategy review

**Verdict: accept the engine/RNG development milestone on this frozen source.** New campaigns remove the demonstrated acquisition/world-randomness confound, while existing campaigns retain their exact saved generation. This is an independently verified engineering improvement. It is not an AAA, commercial-release, universal balance improvement or human-fun endorsement. Final graphics and production browser acceptance remain a separate review after the parent issues its final freeze.

Reviewed source: engine `bfc9e61299d73a344569e54e4b3f3348009f4075560dc2f0fb057f5d8a4d296b`; world RNG `c4ea7b2bb7fc3fa3f0497111dae923566159d2b4143f01b646cb688d3223c1da`; content `2f45160b3e577a7cd44381cb361c4407661a68819ff827a24b8ab34ce15c4234`. The content is byte-identical to the actual archived v0.4 source ZIP. Interim production digest supplied by the parent was `4eae7cbc0aae7ddf41f15eb6610c6a93a942e99461ef7c04187c3590a63f75ad`; this report does not claim a browser visit or final-art verification against that build.

## What was independently checked

- Extracted actual engine/content from [the preserved v0.4 source archive](../releases/0.4.0/hollowpact-0.4.0-source.zip), rather than trusting an implementation-owner fixture. All **120 complete legacy campaigns**, comprising **15,851 accepted actions**, matched complete states and ordered resolved events exactly after every action. Cohorts: informed7101–7124 on all three difficulties, legal-random7901–7948 on seed modulo3 difficulty. These are reused compatibility cohorts, not fresh strategic holdout seeds. Continuing saves remain schema2 without a generation property.
- Replayed the actual seed1989 Initiate **119-action Silence campaign** against that archive: every state/event matched, every repaired intermediate save validated, and the exact inherited overflow save recovered to the same canonical campaign. Cyclic and BigInt programmatic extras now fail recovery, closing the previously documented API limitation.
- Checked **56 schema/generation combinations**; only unmarked schema2 and explicitly kind2 schema3 classify as valid. Unknown construction kinds throw. This is engine validation evidence; final UI handling of unsupported raw saves still needs its browser check.
- Twelve actual earned first-reward states6501–6512 each produced **four branches**: every offered card and skip. After legal fights, actual purchase/removal and common elite entry, their fixed formations, reward/shop offers and first eligible relic matched. Purchase/removal preserved draw RNG. These branches are real engine progression, without editing decks, HP, RNG or money.
- Twelve additional actual paths6701–6712 included an extra legal early end turn, producing different draw positions in **all12 pairs**, then different combat/event routes into common shop/elite nodes. Their common offers and formations matched. Diagnostics include **2,849 input-purity and serialized event-query checks**.
- Actual runtime ranks matched seven explicit preserved research vectors plus the digest of all **3,604 broader tuples**. The prior research ran these on Node and Chromium; this review recomputed runtime outputs in Node and does not claim new browser portability execution. Catalogue reorder and owned-relic filtering preserved surviving identity order. Some algorithm tuples are deliberately unreachable encoding fixtures.
- A separate **48-campaign JSON/event replay** of both held-out endpoint seeds across all policies, difficulties and acquisition arms matched the primary dataset's action hashes, terminal phases, HP and accepted-action counts. All **7,003 actions** preserved source inputs and exact resumed states/events, including **461 actual discard recycling/draw boundaries**. Save checkpoints covered map, battle, reward, shop, event and camp. Terminal stale end-turn actions returned the original state with no events.
- Read the engine diff against actual v0.4. Costs, health/damage values, combat timing, routes and reward counts were unchanged. Creature release still costs35 gold. The kind2 Revenant Silence text corrects the inherited armor implication; legacy text/events remain exact.

The [r2 acceptance evidence](gameplay-v0.5-engine-checks-r2.json), [serialization evidence](gameplay-v0.5-engine-serialization.json) and [derived cross-policy checks](gameplay-v0.5-engine-derived.json) preserve details and provenance. TypeScript checking passed independently. No implementation or implementation-owner evidence was edited.

## Declared holdout and results

The [plan](gameplay-v0.5-engine-plan.json) was written before collection: untouched44101–44196, all three difficulties, four deterministic policies, two actual acquisition arms, both engine kinds; **4,608 campaigns**. All reached valid victory/defeat within the1500-action limit, comprising **668,620 accepted actions**. No outcome-based policy changes followed collection.

Combat/progression evaluators are explicitly copied from the earlier research source and qualified accordingly. `pack` retains all creature families; `strictsolo` never summons and prioritizes removing bindings; `spellhybrid` retains spiders, releases other creatures and favors spells; `lean` releases spiders while retaining other bindings and command cards. All use the same deterministic legal-remove-first evaluator, with legal-action order breaking ties. No virtual sampler, cheap-release wrapper, artificial starting deck or money subsidy is used. These are four automatic strategies, not four independent human playtesters or newly trained ML agents.

`procure` follows that policy's offered-card and shop choices. `skip-acquisition` skips every reward and excludes buying, while keeping the same legal removals, routes, combat scoring, events and camp choices. Differences therefore include money retained, draw distribution, deck size and additional affordable removals. This is a whole-policy procurement comparison, not a causal estimate for one card.

New kind2 victories out of96 per cell; each entry is **procure / skip-acquisition**:

| Policy | Initiate0 | Hunter1 | Veteran2 |
|---|---:|---:|---:|
| Pack |95 /95|90 /85|66 /55|
| Strict solo |82 /35|52 /15|23 /4|
| Spell hybrid |89 /90|71 /44|41 /12|
| Lean bindings |95 /95|89 /84|68 /46|

Legacy kind1, using the same real policies and arms:

| Policy | Initiate0 | Hunter1 | Veteran2 |
|---|---:|---:|---:|
| Pack |96 /92|87 /82|61 /51|
| Strict solo |72 /38|51 /9|26 /2|
| Spell hybrid |88 /78|68 /40|33 /17|
| Lean bindings |96 /96|87 /85|67 /51|

For matched acquisition arms at reached common node/kind, **kind2 had0 mismatches in14,355 comparable world records**. Kind1 had **7,574 mismatches in12,866 records**, confirming that taking cards previously changed the comparison environment. The broader kind2 cross-policy check found **23,524 repeated world records** across6,276 distinct world keys, again with0 discrepancies. Relic comparisons require identical eligible sets; a genuinely different owned set may legitimately produce a different remaining drop. Comparisons condition on reaching the same node/kind; they do not pretend defeated arms reached later offers.

All seed-level results, deck/card usage, economy, action hashes and world traces are in the [lossless compressed dataset](gameplay-v0.5-engine-runs-r2.json.gz). [Summary](gameplay-v0.5-engine-summary-r2.json) lists every procurement rescue/new-loss seed and both generations. Raw JSON SHA256 `b29ccff0d2454442f557a6fe67aa0ea023c4f13a6ea4477eb8b300e8ffdbcac9`; gzip SHA256 `0ade50cd1c5941986faf13b6ca6db26818dff269417db7db271c35099b7533e4`. It deliberately contains concise complete campaign records rather than giant intermediate state dumps. Deterministic policy source and action hashes support reproduction.

## What the evidence means for play quality

**Procurement can matter, and it can be wrong.** Veteran pack procurement rescues16 otherwise-losing seeds but creates5 new losses:44110,44128,44177,44178,44188. Hunter pack has8 rescues and3 new losses. Initiate spell hybrid procurement wins89 instead of90, with4 rescues and5 new losses. Veteran spell hybrid gains29 wins net while still introducing losses44180 and44184. Lean's equal95/96 Initiate totals conceal one rescue and one new loss. A larger deck or automatic acquisition is not universally dominant, and matching worlds now lets later investigations examine those decisions without rerolled enemies obscuring the result.

**The new schedule itself is not universally stronger.** Veteran strict-solo procurement wins fall from26 in legacy to23 in kind2. Initiate pack/lean procurement falls from96 to95. Individual old/new world paths differ in both directions. This is expected from the declared generation change and is not a reason to rewrite historical campaigns or claim a balance buff.

**The binding identity remains the strongest strategic base in this policy family.** Veteran pack and lean procurement reach the boss in69 and72 campaigns and win66 and68. Strict solo reaches it in40 and wins23; its73 losses include20 at floor4,19 at6,17 at8 and17 at10. Its weakness therefore cannot fairly be reduced to Cantor alone. Spell hybrid loses36 campaigns at floor6,12 at8 and7 at10. Investigate actual transition procurement and threat responses before either a blanket boss nerf or broad release-price change. A monster-binding game need not give a self-imposed creature-free policy equal wins, but viable advertised alternative builds should earn their supporting tools.

**Friendly difficulty permits a mostly starter-deck route.** Pack's skip-acquisition campaign wins95/96 Initiate and85/96 Hunter, while Veteran falls to55/96. This establishes challenge differences and a strong starting creature engine. It does not establish that reward screens feel consequential to people or that high win rates alone make the difficulty bad. Strict solo and Veteran hybrid show large procurement effects; familiar pack progression still needs human observation for skip-versus-take comprehension, satisfying tactics and replay motivation.

No fresh human feedback was collected. Existing v0.2/v0.3/v0.4 presentation and playtester evidence remains preserved with its original build qualifications. A numeric human-fun score would exceed the evidence here. The frozen engine milestone passes correctness and provides a much better balance experiment environment; AAA strategic depth, content variety and commercial completeness remain unearned.

## Next priorities and preservation

1. Complete final-build motion-on browser acceptance, including the inherited many-target breath displacement repair, new art and generation-aware save/export handling. This engine review does not substitute for it.
2. Use fixed kind2 world comparisons for a narrowly declared transition/procurement investigation, retain pack/hybrid controls and inspect new losses before changing any economy rule. This holdout authorizes no price patch.
3. Observe actual people choosing cards, removing bindings and preparing contracts; distinguish enjoyable difficult decisions from opaque traps. Keep negative and “none” feedback equally valid.
4. Preserve both generations' interpretation in future work. Adding or removing shared catalogue entries or changing shared prices must not silently change continuing kind1/kind2 campaigns; retain their catalogue/rules or declare a supported later generation.

Reproduction: `npx tsx scripts/review-world-v0.5.ts` in a fresh source copy containing the archived baseline, with these reviewer output paths absent. The harness intentionally refuses to overwrite evidence. Final harness SHA256 `47003e36b07c79a2800202ac19d6836eecae7df050b948bddbf753bc17b10e3a`; plan SHA256 `fe640a1c43a045fce09c9809fea7b68ceb48edfbe12c8b5e027a0bbe86686f60`.

Audit correction: the initial reviewer harness omitted the copied evaluator's `bossForSeed` import. It failed before producing any complete holdout record. [Original diagnostic evidence](gameplay-v0.5-engine-checks.json), [failed harness snapshot](gameplay-v0.5-engine-harness-r1.ts.gz) and [repair metadata](gameplay-v0.5-engine-harness-repair.json) remain preserved. R2 added that import and rechecked broader runtime vectors, keeping the previously declared seeds, evaluators and arms unchanged. This was a reviewer tooling error, not an engine defect; it is not hidden by replacing original outputs.
