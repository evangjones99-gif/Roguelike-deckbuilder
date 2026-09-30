# v0.5 engine implementation evidence

Implementation checks, not an independent acceptance review or a claim of fun/commercial readiness. Every prior release/report/dataset is preserved. Economy, card catalogue, stats, map choices and combat rules remain unchanged.

## New runs and continuing campaigns

`createGame(seed, difficulty = 0, options = { engineKind: 2 })` now creates schema 3 with explicit `engineKind: 2`. Passing `{ engineKind: 1 }` creates the original schema-2 state without any generation property. Unknown construction kinds throw; validation rejects unknown/conflicting schema/kind combinations. Public actions and transient event shapes are unchanged.

Existing schema-2 saves remain kind 1 for their whole campaign, including the shared RNG sequence, and serialize again as schema 2. They are not upgraded or reshuffled on load. The known 119-action seed-1989 campaign still uses this legacy path, validates at every step after the v0.4 status repair, and continues to victory. New-generation saves likewise retain their current draw RNG position across JSON continuation. UI owns the existing storage key and truthful unsupported-format notice; this engine does not rewrite storage.

## Isolated world schedule

`src/world-rng.ts` implements the exact proposed hash-version-1 UTF-8 JSON tuple → FNV-1a-64 → SplitMix64 finalizer. Generation, seed, purpose, entered node, encounter kind and stable identity form its key. Full 64-bit ranks are transient and never saved. Ties use explicit string code-point ordering for ASCII catalogue IDs, without locale-dependent comparison.

Encounter formations, reward cards, shop cards and relic identities use separate stateless purposes. Encounter IDs describe stable rosters rather than array positions. Relic exclusion cannot change surviving identities' ranks. World sampling never reads or advances battle draw RNG. Battle entry initializes its own nonzero draw seed once; actual drawing and reshuffles then use the original mutable PRNG normally. Preview queries work on detached state and leave the original RNG unchanged. Quarry forecast retains the existing seed-modulo-three mapping.

New-generation same-seed worlds intentionally differ from old releases. Different deck compositions can still change draw order, HP, choices and survival; the guarantee concerns common-node/kind world sampling. No historical coupled-RNG dataset is relabeled as this schedule. No cheaper-removal proposal is applied.

Two small clarifications accompany integration: recovery rejects nonserializable programmatic cyclic/BigInt extras before accepting a detached legacy save; actual JSON recovery remains unchanged. In kind 2 only, Silence against a Revenant says its damage/reinforcements are canceled, without the inherited misleading armor suffix. Legacy kind-1 states and events retain their original wording and exact byte compatibility. This changes no armor or damage rules.

## Checks

- `npm test`: 64 passing tests. The original 54 remain, with explicit legacy construction for archival/save fixtures. The 120 original full-run archival comparisons remain strict (72 informed runs on 7101–7124 × three difficulties, and 48 legal-random runs on 7901–7948); they were not weakened to accommodate new sampling.
- Ten new tests check generation classification, frozen hash goldens, catalogue reversal and owned filtering, actual v0.4 compatibility, earned branch comparisons, complete new-generation JSON/event replays, query purity, recovery rejection and generation-specific Revenant wording.
- The v0.4 engine/content fixtures were copied verbatim from `releases/0.4.0/hollowpact-0.4.0-source.zip`. Their hashes are asserted before 18 full legacy campaign comparisons of states and ordered events on 8101–8118, difficulty `seed % 3`.
- Twelve actual first-reward campaigns on 6501–6512, Initiate, branch into acquisition/skip, then actual shop purchase/removal, then elite contracts. All resulting saves validate; common battle rosters, reward/shop offers and relics match. Eight additional actual battle/event route forks on 6601–6608, Initiate, match later shop offers and elite rosters. These are earned progressions, not injected economy fixtures.
- Thirty-six complete kind-2 informed campaigns on 9101–9136, difficulty `seed % 3`, serialize/replay at each action and compare ordinary/observed reducer results, with more than 200 end-turn/draw boundaries, more than ten actual discard-recycling boundaries, more than ten forecast-matching boss entries and all map/battle/reward/shop/camp/event phases exercised. Thirty-six explicit kind-2 legal-random campaigns on 9301–9336, difficulty `seed % 3`, validate every accepted intermediate/serialized state and compare JSON event replay. Terminal actions remain harmless and schema-3 menu saves are rejected. The original 300 legal-random runs on 1–100 × three difficulties also exercise default kind 2 and validate every intermediate state inside `scripts/simulate.ts`.
- Revenant wording uses explicitly unearned five-card combat fixtures to isolate three legal Silence payments and their ordered observations in both kinds. No armor gain is invented and legacy observations match v0.4 exactly.
- `npx tsc --noEmit`: passed. Independent production-browser/packaged-platform checks and release promotion remain separate gates.

## Frozen source hashes

| File | SHA-256 |
|---|---|
| src/engine.ts | bfc9e61299d73a344569e54e4b3f3348009f4075560dc2f0fb057f5d8a4d296b |
| src/world-rng.ts | c4ea7b2bb7fc3fa3f0497111dae923566159d2b4143f01b646cb688d3223c1da |
| src/content.ts, unchanged | 2f45160b3e577a7cd44381cb361c4407661a68819ff827a24b8ab34ce15c4234 |
| tests/world-rng-v0.5.test.ts | 192eab190525201fb3ef16d710faf0d776c5b4307d18ee0f9f3e2548a3347d3f |

Limit: the production catalogue/generation contract now requires retaining this sampler's identities and algorithm for kind-2 continuations. A future sampler/catalogue revision needs an explicit later generation and compatibility policy. Automated victories do not measure human enjoyment or guarantee every seed improves.
