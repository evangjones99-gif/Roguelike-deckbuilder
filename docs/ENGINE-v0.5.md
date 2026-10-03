# HOLLOWPACT v0.5 engine and save contract

v0.5 isolates world sampling for new campaigns while continuing existing campaigns with their original rules generation. Prices, card/creature values, route choices, combat timing and reward counts remain unchanged. These notes describe the implemented engine; final presentation, packaging and platform acceptance have separate evidence.

## Save boundary

| Saved format | Interpretation | Construction and continuation |
|---|---|---|
| Schema 2, without an `engineKind` property | Legacy kind 1 | `createGame(seed, difficulty, { engineKind: 1 })`; shared RNG schedule and schema-2 serialization remain byte-compatible with v0.4. |
| Schema 3, explicitly `engineKind: 2` | Kind 2 | Default `createGame(seed, difficulty)`; isolated world purposes and saved battle draw position. |
| Missing/conflicting/unknown schema or generation | Unsupported or invalid | Reject; preserve original saved bytes and show the appropriate notice. |

The loader still uses `hollowpact.run.v2`; the key's historical name does not determine its schema. Loading, resuming, opening settings or exporting optional feedback does not silently convert a campaign. A kind-1 run remains kind 1 through completion. Starting a new campaign deliberately creates kind 2. Older released engines reject schema 3 rather than interpreting its schedule as legacy.

The existing narrow legacy Silence guard-label recovery remains available: only the exact identified repeated suffix is repaired, every other field must validate, and the UI preserves the original text before saving recovery. Cyclic/BigInt programmatic extras now fail recovery. This is structural recovery, not authentication or a general corrupt-save migration. Public action and ordered transient event shapes are unchanged; events are never saved as gameplay fields.

## Kind-2 randomness

`src/world-rng.ts` hash version 1 encodes the UTF-8 JSON tuple `["hollowpact", 2, seed, purpose, node, encounterKind, identity]`, applies FNV-1a-64 followed by the SplitMix64 finalizer, and ranks with the full unsigned 64-bit result. Stable ASCII IDs resolve ties with explicit code-point ordering. Ranks are transient BigInts and never enter JSON saves. Hashing provides deterministic separation, not cryptographic security or a guarantee that finite hashes cannot collide.

| Purpose | Stable identity and behavior |
|---|---|
| `encounter` | Formation ID within the entered normal/elite pool; independent of deck length, purchases, earlier draws and route history. |
| `reward` | Base card ID at the completed node/kind; fixed three-card offer. |
| `shop` | Base card ID at the entered shop; fixed initial five-card offer, with purchases removing their selected offer normally. |
| `relic` | Relic ID at the source node/kind; owned exclusions preserve remaining identities' ranks. A different eligible pool can legitimately yield a different drop. |
| `battle-deck` | Initializes `state.rng` once on battle entry from the hash's low 32 bits, replacing zero with one. |

Only drawing and shuffling advance kind-2 mutable battle RNG. World sampling never reads or advances it. Save/load and detached previews do not reset or consume the actual draw stream. Different decks still produce different draws and outcomes. Alternate routes intentionally select different encounters; later common node/kind keys do not inherit an RNG cursor from that choice. `bossForSeed(seed)` retains its modulo-three quarry forecast in both generations.

Kind 2 also gives a silenced Revenant truthful canceled-damage wording. Kind 1 retains v0.4 wording and exact state/event compatibility. No damage or armor rule changes accompany that clarification.

## Catalogue and future-change policy

Formation, card and relic identities—not array positions—define kind 2. Keep hash version 1 and its catalogue interpretation stable for continuing kind-2 runs; catalogue reordering alone must not reroll offers. Kind 1 likewise retains its legacy catalogue and sampling interpretation.

Both kinds currently share `content.ts` and most combat/economy code. The generation marker alone does not preserve old prices or card values if that shared code is edited. Before changing content, pricing or rules, retain the supported kind-1/kind-2 interpretations with versioned lookups/dispatch, or declare a reviewed later-generation compatibility policy that preserves original saves and historical builds. New-generation construction must not automatically remigrate existing campaigns. Introduce later sampling/catalogue behavior explicitly rather than silently changing kind 2's meaning.

## Evidence and limits

- [Engine implementation evidence](../reviews/engine-v0.5.md): 64 passing rules tests, exact source hashes, legacy replay gates, actual acquired-card/shop/route branches and JSON continuation through discard recycling. Tests verify validation at every accepted intermediate state, generation rejection and harmless terminal actions.
- [Independent engine/world review](../reviews/gameplay-v0.5-engine.md): 120 actual-v0.4 full state/event replays, the 119-action legacy recovery campaign, and 4,608 declared legal campaigns across both kinds, three difficulties, four automatic strategies and two procurement arms. All 668,620 actions validated; kind 2 had zero world discrepancies in 14,355 comparable acquisition records. [Immutable dataset](../reviews/gameplay-v0.5-engine-runs-r2.json.gz) and [summary](../reviews/gameplay-v0.5-engine-summary-r2.json) retain negative outcomes. The changed schedule is not universally easier or stronger.
- [ML experiment](../reviews/ml-policy-0.5-r1/README.md) and [independent audit](../reviews/ml-policy-0.5-independent.md): all 880 training/evaluation records reproduced byte-identically from frozen hierarchical sources. Held-out learned wins were 96/96 versus 95/96, but play was slower and 26 shared winning seeds ended with less health. This narrow rules experiment excludes final-art/native-build provenance and does not authorize policy adoption or balance changes.

Automatic strategies and learned-policy victories do not establish human enjoyment, AAA craft, platform readiness or commercial/Steam acceptance. No price patch follows from these results. Future experiments need new declared cohorts, preserved negatives and independent review; prospective-player observation remains necessary.
