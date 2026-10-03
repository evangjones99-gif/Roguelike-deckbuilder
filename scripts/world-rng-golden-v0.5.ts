/** Standalone research only: no game imports or runtime/save integration. */
import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { chromium } from "@playwright/test";

type Key = (string | number)[];
// Self-contained so the exact encoding/integer algorithm runs in both hosts.
function rankAll(keys: Key[]): string[] {
  return keys.map(key => {
    const mask = (1n << 64n) - 1n;
    let h = 14695981039346656037n;
    for (const byte of new TextEncoder().encode(JSON.stringify(key)))
      h = ((h ^ BigInt(byte)) * 1099511628211n) & mask;
    h = ((h ^ (h >> 30n)) * 0xbf58476d1ce4e5b9n) & mask;
    h = ((h ^ (h >> 27n)) * 0x94d049bb133111ebn) & mask;
    h ^= h >> 31n;
    return h.toString(16).padStart(16, "0");
  });
}
function key(seed: number, purpose: string, node: number, kind: string,
  identity: string): Key {
  return ["hollowpact", 2, seed, purpose, node, kind, identity];
}
// ASCII-only catalogue IDs use explicit code-point ordering, never localeCompare.
function compareId(a: string, b: string): number {
  assert.match(a, /^[\x20-\x7e]*$/);
  assert.match(b, /^[\x20-\x7e]*$/);
  return a < b ? -1 : a > b ? 1 : 0;
}
function ranked(ids: string[], seed: number, purpose: string,
  node: number, kind: string) {
  const hashes = rankAll(ids.map(id => key(seed, purpose, node, kind, id)));
  return ids.map((id, index) => ({ id, rank: hashes[index] }))
    .sort((a, b) => a.rank < b.rank ? -1 : a.rank > b.rank ? 1 : compareId(a.id, b.id));
}

const path = "reviews/world-rng-v0.5/golden-vectors-r1.json";
if (existsSync(path)) throw Error("Refusing to overwrite immutable research evidence: " + path);
const golden = [
  { key: key(0, "encounter", 1, "battle", "normal.raider-thrall"), expected: "38227b714820819f" },
  { key: key(1989, "encounter", 1, "battle", "normal.raider-thrall"), expected: "665f451dd24bcd8a" },
  { key: key(1989, "reward", 1, "battle", "silence"), expected: "ff0dae33d92e09df" },
  { key: key(1989, "shop", 1, "battle", "silence"), expected: "573f69031537cc51" },
  { key: key(1989, "relic", 4, "elite", "grave-coin"), expected: "7c178ff49c76723b" },
  { key: key(1989, "battle-deck", 10, "boss", ""), expected: "82c62931bd899fc9" },
  { key: key(4294967295, "battle-deck", 10, "boss", ""), expected: "d05bee1128f7ac8c" },
];
const goldenActual = rankAll(golden.map(g => g.key));
assert.deepEqual(goldenActual, golden.map(g => g.expected));
const samples: Key[] = [];
for (const seed of [0, 1, 1989, 6501, 28001, 4294967295])
  for (const purpose of ["encounter", "reward", "shop", "relic", "battle-deck"])
    for (let node = 1; node <= 10; node++)
      for (const kind of ["battle", "elite", "shop"])
        for (const id of ["silence", "resonance", "cairnhound", "grave-coin"])
          samples.push(key(seed, purpose, node, kind, id));
// Encoding boundaries are algorithm fixtures, not declared valid content IDs.
const encodingFixtures: Key[] = [
  key(1989, "reward", 1, "battle", "unicode-🜏"),
  key(1989, "a|b", 1, "c", "d"),
  key(1989, "a", 1, "b|c", "d"),
  key(1989, "reward", 1, "battle", 'quoted-"-\\'),
];
samples.push(...encodingFixtures);
const actual = rankAll(samples);
assert.equal(new Set(samples.map(k => JSON.stringify(k))).size, samples.length);
assert.equal(new Set(actual).size, actual.length, "observed finite-sample hash collision");
assert.notEqual(JSON.stringify(encodingFixtures[1]), JSON.stringify(encodingFixtures[2]));
assert.notEqual(actual.at(-3), actual.at(-2));

const catalogue = ["silence", "resonance", "cairnhound", "sunder", "witchfire"];
const ordered = ranked(catalogue, 1989, "reward", 4, "elite");
assert.deepEqual(ranked([...catalogue].reverse(), 1989, "reward", 4, "elite"), ordered);
const relics = ["grave-coin", "brass-bell", "fang-charm", "iron-token"];
const allRelics = ranked(relics, 1989, "relic", 4, "elite");
const owned = new Set(allRelics.slice(0, 2).map(r => r.id));
assert.deepEqual(ranked(relics.filter(id => !owned.has(id)), 1989, "relic", 4, "elite"),
  allRelics.filter(r => !owned.has(r.id)));
const forcedTie = ["a", "Z", "z", "A"].sort(compareId);
assert.deepEqual(forcedTie, ["A", "Z", "a", "z"]);
assert.deepEqual(rankAll(samples.map(k => JSON.parse(JSON.stringify(k)))), actual);

const browser = await chromium.launch({
  headless: true,
  executablePath: process.env.HOLLOWPACT_CHROMIUM_EXECUTABLE ?? "/usr/bin/chromium",
  args: ["--no-sandbox"],
});
let browserVersion = "";
try {
  const page = await browser.newPage();
  browserVersion = browser.version();
  const browserGoldens = await page.evaluate(rankAll, golden.map(g => g.key));
  assert.deepEqual(browserGoldens, goldenActual);
  const browserSamples = await page.evaluate(rankAll, samples);
  assert.deepEqual(browserSamples, actual);
} finally {
  await browser.close();
}

const sourceHash = createHash("sha256").update(readFileSync(import.meta.filename)).digest("hex");
const evidence = {
  revision: 1,
  purpose: "Proposed v0.5 hash/identity-order portability research, not production integration",
  runtimeImported: false,
  algorithm: "UTF8 JSON tuple; FNV-1a-64 then SplitMix64 finalizer, hash version1",
  generationProposed: 2,
  sourceHash,
  nodeVersion: process.version,
  browserVersion,
  golden: golden.map((g, index) => ({ ...g, actual: goldenActual[index] })),
  broaderTupleCount: samples.length,
  broaderTupleDigest: createHash("sha256").update(JSON.stringify({ samples, actual })).digest("hex"),
  nodeBrowserExact: true,
  observations: {
    sampleRanksUnique: true,
    catalogueReorderExact: true,
    ownedFilterPreservesRanks: true,
    forcedTieOrder: forcedTie,
    serializedTupleReplayExact: true,
    unicodeAndDelimiterFixturesMatch: true,
  },
  limitations: [
    "Both hosts run the same specified algorithm; this is portability evidence, not an independent hash proof.",
    "Tuple combinations include unearned/unreachable node-purpose/content pairs and test no game progression.",
    "A finite unique sample cannot establish absence of all possible 64-bit collisions.",
    "No saved state, draw-stream continuation, generation migration or game-world schedule was tested.",
  ],
};
mkdirSync("reviews/world-rng-v0.5", { recursive: true });
writeFileSync(path, JSON.stringify(evidence, null, 2) + "\n", { flag: "wx" });
console.log(JSON.stringify({ path, sourceHash, browserVersion,
  exactTupleComparisons: samples.length + golden.length,
  runtimeImported: false }));
