# Proposed world-hash research

This is standalone algorithm research prepared while the v0.4 runtime remains frozen. It imports no engine or content and implements no migration, card/economy change, world encounter schedule or saved draw stream.

`golden-vectors-r1.json` records 3,611 exact Node/Chromium comparisons: seven prespecified golden vectors and 3,604 broader boundary-seed, node, purpose, identity and encoding tuples. Catalogue reversal, owned-relic filtering, forced equal-rank ASCII ordering and serialized tuple replay checks passed. Both hosts run the same specified code, so this verifies portability rather than serving as independent algorithm certification. The sample includes unreachable purpose/node combinations and hypothetical identity strings; it is not a gameplay simulation. Observed unique ranks do not prove that finite hashes cannot collide.

Source: `scripts/world-rng-golden-v0.5.ts`, SHA-256 `b7943cc0f72606ff9fea63aaee7132df2c54c2b7f8a89fb49476fbfc165455d8`. Hosts: Node v24.19.0 and Chromium 151.0.7922.173 through the project's installed Playwright and `/usr/bin/chromium`. TypeScript validation passed.

The harness refuses to overwrite an evidence file. To reproduce without changing these records, run its absolute path from a fresh working directory using the project's installed tsx entry point. For this checkout, an example is:

```sh
research_dir=$(mktemp -d)
cd "$research_dir"
node /workspace/Roguelike-deckbuilder/node_modules/tsx/dist/cli.mjs /workspace/Roguelike-deckbuilder/scripts/world-rng-golden-v0.5.ts
```

The independent output is written beneath that fresh directory. `HOLLOWPACT_CHROMIUM_EXECUTABLE` may specify a different installed browser path. This test launches a blank page, without a production preview server or game runtime. Production integration needs separate actual legacy continuation, schema classification, stream purity, reachable branch comparisons and replay checks as specified in `docs/WORLD-RNG-v0.5-DESIGN.md`.
