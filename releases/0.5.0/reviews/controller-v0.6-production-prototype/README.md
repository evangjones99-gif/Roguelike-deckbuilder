# Unshipped v0.6 input candidate

Frozen preparatory artifact from final v0.5 digest d6221bf764bad593b04981e87bead7ba6868b72cf361d70671af5c91aac39416. The adapter is not part of that runtime. Parent root must authorize promotion to src/input.ts and integrate real main callbacks. See ../controller-v0.6-implementation-plan.md for contract and limits.

13 decoder tests, eight battle/form/dialog browser checks, nine menu checks and lifecycle checks passed. Browser tests inject an unshipped adapter and borrowed callbacks into real controls. Synthetic standard gamepad state and emulated visibility are not physical controller, native background-tab, Windows or Steam Deck evidence. No human fun evidence follows. Terminal menus were not reached by these probes.

Original workspace: /workspace/scratch/controller-v06-production-input/. These Linux author probe tools preserve that original fixture directory and installed Playwright path intentionally. To reproduce the same probes, place these files there without overwriting existing evidence, run from /workspace/Roguelike-deckbuilder, and serve the stated frozen digest on127.0.0.1:4173:

```sh
npx tsc --ignoreConfig --strict --target ES2022 --module ESNext --lib ES2022,DOM --moduleResolution bundler --outDir /workspace/scratch/controller-v06-production-input/emitted /workspace/scratch/controller-v06-production-input/adapter.ts
npx tsx --test /workspace/scratch/controller-v06-production-input/adapter.test.ts
node /workspace/scratch/controller-v06-production-input/browser-probe.mjs
node /workspace/scratch/controller-v06-production-input/lifecycle-probe.mjs
node /workspace/scratch/controller-v06-production-input/menus-probe.mjs
```

Timestamped evidence writes use exclusive creation. Native pipeline tests should use the actual promoted module, its built digest, real settling state and main callbacks, rather than this shim. Original fixture generator source is retained; runtime RNG/save semantics are unchanged.
