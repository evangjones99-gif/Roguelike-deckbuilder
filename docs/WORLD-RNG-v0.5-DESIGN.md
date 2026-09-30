# v0.5 proposal: reproducible world streams

This document proposes a future engine generation. It does not change v0.4 rules, save schema, prices, content or runtime RNG. v0.4 first repairs the inherited Silence label defect. Independent review must approve the subsequent implementation on its actual source and playable build.

## Problem and evidence

The released engine uses one mutable RNG for deck shuffles and world sampling. In nine reachable first-reward states, taking a card instead of skipping changed the next enemy formation in six pairs despite equal seed, HP, node and route. Thus same-seed procurement comparisons also change the world encountered.

The separately labeled research sampler produced 1,728 terminal holdout records on fresh seeds 28001–28072. Strict-solo wins with normal versus proposed cheaper creature release were 53→62, 33→57 and 12→38 across the three difficulties. Ordinary pack pairs were identical. Widow-hybrid Veteran wins fell 22→21. The independent reviewer checked all rows, rescue/new-loss lists and all 4,510 common-node encounter rosters. These observations support isolating the comparison environment, while withholding a general release-price patch. Whole-policy wins remain balance measurements rather than player enjoyment.

The research sampler is not the production algorithm. Its arithmetic purpose tags and array-index ranks overlap between shop/reward pools, and filtering owned relics reranks other identities. Keep that source, prespecification and results unchanged. Production keys should encode purpose and stable identities explicitly.

## Compatibility decision

Keep valid schema-2 saves in their original format through the entire run. Classify them as engine kind 1 internally, and retain their shared RNG schedule. Do not switch a continuing campaign into the new world generator, shuffle its current hand, reroll its visible intentions, or change its advertised quarry. v0.4's narrow label normalization remains the declared text-only compatibility repair.

New campaigns use schema 3 with explicit `engineKind: 2`. A discriminated state union can retain the existing common gameplay fields. Schema 3 without kind 2, or unknown kinds, must fail validation. Schema 2 with a conflicting generation field must fail classification rather than silently becoming kind 2. The loader first validates/classifies; the reducer cannot guess a mode from deck composition or a missing new field midway through play.

Use the existing `hollowpact.run.v2` storage location with automatic classification. Saving a continuing kind-1 run writes schema 2 again, so archived v0.2/v0.3 builds can still read it. Starting a genuinely new run replaces the current campaign with schema 3 under the normal existing new-run flow; archived engines will truthfully reject that newer format. No automatic destructive conversion is required. Preserve raw text before any recovery; an exported save can identify both schema and engine kind. This avoids inventing an irreversible migration merely to introduce a generator.

The existing storage key's name is historical, not a claim about the save's schema. UI must report an unsupported newer/unknown format honestly, retain its bytes, and offer new-run controls without silently overwriting the unrecognized campaign. A loader must not treat an unsupported schema-3 save as an absent save.

## Stream design

World values are stateless functions of normalized run seed, engine generation, purpose, actual entered node, encounter identity, and optional stable content identity. Battle draw randomness alone uses mutable `state.rng`. No world function reads or advances that field.

Use an unambiguous key encoded as UTF-8 `JSON.stringify(["hollowpact", 2, seed, purpose, node, encounterKind, identity])`, with fixed numeric/string field types. Proposed exact hash version 1: FNV-1a-64 (offset 14695981039346656037, prime 1099511628211, mask to 64 bits after each multiplication), followed by the SplitMix64 finalizer (xor right-shift 30, multiply 0xbf58476d1ce4e5b9; xor right-shift 27, multiply 0x94d049bb133111eb; xor right-shift 31; mask after multiplications). Use the full unsigned 64-bit result for ranks; battle PRNG initialization uses its low 32 bits, replacing zero with one. Kind 2 always uses hash version 1; changing that algorithm requires an explicit later generation. Review the implementation and freeze browser/Node golden vectors before use. BigInt is supported by the declared browser target. Hashing provides deterministic separation, not cryptographic guarantees. Resolve a rank collision using explicit ASCII code-point comparison of stable IDs, never `localeCompare`; do not depend on source object/array iteration order.

| Purpose | Inputs and behavior |
|---|---|
| encounter | Seed, kind 2, actual node, route kind. Rank stable formation IDs within that node's normal/elite pool; no card count, prior actions, gold, HP, rewards or relics. Difficulty retains its declared stat scaling. |
| reward | Seed, kind 2, node, completed encounter kind, stable base card ID. Rank the unchanged reward catalogue and select its usual count. No previous draws or acquisitions. |
| shop | Seed, kind 2, node, stable base card ID. Independent shop key, usual offer count; purchases do not regenerate offers. |
| relic | Seed, kind 2, node, source kind, stable relic ID. Compute identity ranks before excluding owned relics; filter owned entries without reranking surviving identities. A changed eligible pool can legitimately change which drop remains. |
| battle deck | Seed, kind 2, node, encounter kind, purpose `battle-deck`. Initialize `rng` once when entering a new battle, then use the existing shuffle/draw PRNG and save its current position exactly. |

Formation IDs must describe stable rosters, not array indices. Content additions/removals constitute a generation decision: a release must not silently alter kind-2 catalogue interpretation midway through an old kind-2 run. Either keep that generation's catalogue or introduce a later explicit kind. Catalogue provenance belongs in evidence and release manifests.

Map progression stays unchanged. Node is the entered encounter's floor, not the number of RNG calls or cards played. Choosing an elite intentionally selects its elite pool; choosing camp instead intentionally means that combat does not occur. Neither branch advances a shared world cursor, so later common node/kind keys match. No route is implicitly rerolled. Quarry forecasting remains `bossForSeed(seed)` with the existing modulo-three mapping for both kinds.

Preliminary vectors computed with a standalone Node implementation of the specified tuple/hash, before any runtime implementation:

| Seed | Purpose | Node/kind | Identity | Unsigned 64-bit rank, hexadecimal |
|---|---|---|---|---|
| 0 | encounter | 1/battle | normal.raider-thrall | 38227b714820819f |
| 1989 | encounter | 1/battle | normal.raider-thrall | 665f451dd24bcd8a |
| 1989 | reward | 1/battle | silence | ff0dae33d92e09df |
| 1989 | shop | 1/battle | silence | 573f69031537cc51 |
| 1989 | relic | 4/elite | grave-coin | 7c178ff49c76723b |
| 1989 | battle-deck | 10/boss | empty string | 82c62931bd899fc9 |
| 4294967295 | battle-deck | 10/boss | empty string | d05bee1128f7ac8c |

All seven vectors matched in a standalone Playwright page using the project's `/usr/bin/chromium` executable, Chromium 151.0.7922.173, and Node v24.19.0. This portability check imported no game runtime. The eventual production implementation still needs its own tests against these vectors. The two battle-deck vectors initialize the existing draw PRNG to 3179913161 and 687320204 respectively. These define algorithm checks, not a shipped encounter catalogue or evidence that every finite hash is unique.

The reproducible standalone `scripts/world-rng-golden-v0.5.ts` additionally passed 3,604 broader tuple comparisons and identity reorder/filter/forced-tie checks, writing immutable evidence under `reviews/world-rng-v0.5/`. Its source and host versions are recorded there. These remain algorithm fixtures and do not substitute for reachable campaign/save tests of the future runtime.

Initial order and later reshuffles may differ between deck interventions because their real cards differ. The guarantee concerns world sampling, not identical card availability. Gold/HP/resources may cause different legal choices or survival. Visible intentions can change with actual allied targets; their timing and stable targeting remain existing combat rules.

## Replay and validation requirements

1. Retain strict archive byte comparisons for ordinary kind-1 runs, plus the explicit v0.4 repeated-status-text exception in the known legal campaign. No historical research dataset is rerun and relabeled as the new production schedule.
2. Replay new kind-2 runs from their action list and from JSON save checkpoints at map, battle before/after reshuffle, reward, shop, camp, event and terminal phases. Compare state and ordered transient events exactly. Never reset or advance the real draw RNG on save load, preview query or an ordinary non-draw action. A preview reducer operates on a detached state only.
3. Compare reachable reward/skip, purchase/no purchase, removal/no removal and earlier draw choices. At a common later node/kind, initial enemy family formation and fixed shop/reward offers must match. Eligible relic identity ranks must match; owned exclusions must be explained. Validate each state and preserve card-copy/UID conservation.
4. Verify old campaign saves at every phase continue as kind 1 and are written back as schema 2. Verify unknown/conflicting schema/kind combinations and forged generation fields fail; malformed saves cannot exploit recovery to switch modes.
5. Freeze hash golden vectors and representative seed/node/purpose fixtures, including repeated serialization, source-array reorder and content-identity reorder. Verify purpose separation without promising that finite hashes never collide.
6. Confirm each formation is in its intended pool, all three quarries remain forecastable, and target/death/reinforcement event ordering remains exact. Run independent technical review before a new balance holdout.

## Release risks and next experiment

New-generation same-seed runs deliberately have a different world schedule. Report that change; do not market differences from old historical seeds as a pure balance improvement. Resampling can improve or worsen individual routes even when global mechanics are unchanged. Retaining legacy code paths creates maintenance cost; remove them only through an explicit supported end-of-run/export policy in a future major migration.

After implementation and review, precommit untouched seeds for several legal policies and realistic procurement arms, with pack negative controls. Repeat price comparisons only against matched kind-2 worlds and keep all negative outcomes. No price change is part of this generator patch. Human observation remains necessary to evaluate acquisition meaning, cost comprehension and replay motivation.

Small API backlog, separate from the actual JSON loader: the v0.4 recovery helper can preserve a cyclic unknown extra field on a programmatically supplied object, returning a state that cannot be serialized. Such an object cannot come from `JSON.parse(localStorageText)`. A read-only probe using the preserved overflow fixture plus `extra = self` confirmed the API-only limitation; production scope stays frozen. A future migration hardening pass can require serializability after detached cloning and reject cycles/BigInt, with focused regressions, without broadening accepted real saves. A separate presentation clarification should replace inherited Silence wording on Revenant's `ignores block` attack, which currently receives the guard-oriented armor suffix despite being canceled damage.
