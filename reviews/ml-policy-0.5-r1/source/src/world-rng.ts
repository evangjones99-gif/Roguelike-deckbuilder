/** Generation-2 world sampling. Ranks are transient; never store BigInt in saves. */
export type WorldPurpose = "encounter" | "reward" | "shop" | "relic" | "battle-deck";
export interface WorldContext { seed: number; node: number; kind: string }
/** Hash version 1 is permanently part of engine kind 2. */
export function worldRank(purpose: WorldPurpose, context: WorldContext,
  identity = ""): bigint {
  const key = ["hollowpact", 2, context.seed, purpose, context.node, context.kind, identity];
  const mask = (1n << 64n) - 1n;
  let h = 14695981039346656037n;
  for (const byte of new TextEncoder().encode(JSON.stringify(key)))
    h = ((h ^ BigInt(byte)) * 1099511628211n) & mask;
  h = ((h ^ (h >> 30n)) * 0xbf58476d1ce4e5b9n) & mask;
  h = ((h ^ (h >> 27n)) * 0x94d049bb133111ebn) & mask;
  return h ^ (h >> 31n);
}
export function worldOrder(ids: readonly string[], purpose: WorldPurpose,
  context: WorldContext): string[] {
  return ids.map(id => ({ id, rank: worldRank(purpose, context, id) }))
    .sort((a, b) => a.rank < b.rank ? -1 : a.rank > b.rank ? 1
      : a.id < b.id ? -1 : a.id > b.id ? 1 : 0)
    .map(entry => entry.id);
}
export function worldDrawSeed(context: WorldContext): number {
  return Number(worldRank("battle-deck", context) & 0xffffffffn) || 1;
}
/** Stable IDs, not source-array positions, define generation-2 formations. */
const EARLY = {
  "normal.raider-revenant": ["raider", "revenant"],
  "normal.raider-thrall": ["raider", "thrall"],
} as const;
const NORMAL = {
  "normal.brood-thrall": ["brood", "thrall"],
  "normal.raider-revenant": ["raider", "revenant"],
  "normal.acolyte-thrall": ["acolyte", "thrall"],
  "normal.revenant-thrall-thrall": ["revenant", "thrall", "thrall"],
} as const;
const ELITE = {
  "elite.raider-revenant-acolyte": ["raider", "revenant", "acolyte"],
  "elite.brood-acolyte": ["brood", "acolyte"],
  "elite.raider-raider-revenant": ["raider", "raider", "revenant"],
  "elite.acolyte-revenant-revenant": ["acolyte", "revenant", "revenant"],
} as const;
export function worldFormation(context: WorldContext): string[] {
  if (context.kind !== "battle" && context.kind !== "elite")
    throw new RangeError("Only battle and elite nodes sample a world formation");
  const pool: Readonly<Record<string, readonly string[]>> = context.kind === "elite"
    ? ELITE : context.node <= 2 ? EARLY : NORMAL;
  const id = worldOrder(Object.keys(pool), "encounter", context)[0];
  return [...pool[id]];
}
