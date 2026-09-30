/** Investigation only. Imports frozen gameplay; does not patch gameplay files.
 * Proposal wrappers and matched fixtures are labeled counterfactual evidence.
 */
import { createHash } from "node:crypto";
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { gzipSync } from "node:zlib";
import {
  applyAction,
  createGame,
  legalActions,
  validateState,
  CARDS,
  type GameState,
  type Action,
  type Unit,
} from "../src/engine";
import { bossForSeed, STARTER_DECK } from "../src/content";
type Mode = "solo" | "pack";
type Progression =
  | "legal-buy-first"
  | "legal-remove-first"
  | "proposal-removal-15"
  | "counterfactual-ready-opening";
type Entry = { id: string; key: number };
const packet = ["resonance", "resonance", "silence", "witchfire", "draught"];
const digest = (file: string) =>
  createHash("sha256").update(readFileSync(file)).digest("hex");
const sourceHashes = Object.fromEntries(
  ["src/engine.ts", "src/content.ts", "scripts/solo-investigation-v0.3.ts"].map(
    (f) => [f, digest(f)],
  ),
);
const expected = {
  engine: "21bafb33832ec2d3ee1ca4ead9486825510bd380b62e143a8736465f1ad4110b",
  content: "2f45160b3e577a7cd44381cb361c4407661a68819ff827a24b8ab34ce15c4234",
};
if (
  sourceHashes["src/engine.ts"] !== expected.engine ||
  sourceHashes["src/content.ts"] !== expected.content
)
  throw Error(
    "Frozen v0.2 source changed; investigation must be explicitly rebased.",
  );
const base = (id: string) => id.replace("+", "");
function mix(seed: number, key: number) {
  let x = (seed ^ Math.imul(key + 1, 0x9e3779b1)) >>> 0;
  x ^= x >>> 16;
  x = Math.imul(x, 0x85ebca6b);
  x ^= x >>> 13;
  x = Math.imul(x, 0xc2b2ae35);
  return (x ^ (x >>> 16)) >>> 0;
}
function threat(s: GameState, e: Unit) {
  const i = e.intent!;
  const target = s.allies.find((u) => u.uid === i.target);
  return (
    (i.target === "hunter" ||
    i.target === "all" ||
    (!target && i.target !== e.uid)
      ? i.damage
      : 0) *
      5 +
    (i.summon?.length ?? 0) * 22 +
    (i.target === "all"
      ? s.allies.length * i.damage
      : target
        ? Math.min(target.hp, i.damage)
        : 0) *
      2
  );
}
function anticipated(s: GameState) {
  let block = s.block,
    total = 0;
  const alive = new Set(s.allies.map((u) => u.uid));
  for (const e of s.enemies) {
    const i = e.intent!;
    if (
      i.target === "all" ||
      i.target === "hunter" ||
      (i.target !== e.uid && !alive.has(i.target))
    ) {
      if (e.cardId === "revenant") total += i.damage;
      else {
        total += Math.max(0, i.damage - block);
        block = Math.max(0, block - i.damage);
      }
    }
  }
  return total;
}
const soloValues: Record<string, number> = {
  resonance: 120,
  gravetithe: 110,
  silence: 100,
  survey: 95,
  draught: 100,
  witchfire: 90,
  sunder: 75,
  ironward: 72,
  scour: 65,
  bloodprice: 35,
};
const packValues: Record<string, number> = {
  edict: 110,
  silence: 105,
  survey: 100,
  killcommand: 90,
  harpoon: 95,
  covenant: 90,
  aegis: 85,
  gravetithe: 85,
  gravehound: 85,
  fenraker: 85,
  ossuarycolossus: 80,
  emberwidow: 80,
  cairnhound: 70,
  ashwidow: 65,
  fenstalker: 60,
  briarcolossus: 55,
  sunder: 75,
  draught: 60,
  witchfire: 50,
};
function value(s: GameState, id: string, mode: Mode) {
  const c = CARDS[id];
  if (mode === "solo" && c.type === "summon") return -100;
  let v = (mode === "solo" ? soloValues : packValues)[base(id)] ?? 20;
  if (
    bossForSeed(s.seed) === "cantor" &&
    ["silence", "witchfire"].includes(base(id))
  )
    v += 12;
  return v;
}
function combatScore(s: GameState, a: Action, mode: Mode) {
  if (a.type === "endTurn") return 0;
  if (a.type !== "play" && a.type !== "attack") return -1000;
  const c = a.type === "play" ? CARDS[s.hand[a.index]] : undefined;
  if (c?.type === "summon")
    return mode === "solo" ? -1000 : 125 + (c.attack ?? 0) * 3 - c.cost * 4;
  const next = applyAction(s, a);
  if (next.phase === "victory" || next.phase === "reward") return 10000;
  if (next.phase === "defeat") return -10000;
  const dealt = s.enemies.reduce(
    (sum, e) =>
      sum +
      Math.max(0, e.hp - (next.enemies.find((u) => u.uid === e.uid)?.hp ?? 0)),
    0,
  );
  const killed = s.enemies.filter(
    (e) => !next.enemies.some((u) => u.uid === e.uid),
  );
  let score =
    dealt * 5 +
    killed.reduce((n, e) => n + 80 + threat(s, e), 0) +
    (next.hp - s.hp) * 8;
  score +=
    (anticipated(s) - anticipated(next)) * (anticipated(s) >= s.hp ? 25 : 7);
  if (a.type === "attack") {
    const u = s.allies.find((u) => u.uid === a.unit)!;
    const after = next.allies.find((a) => a.uid === u.uid);
    score += 10 + (after ? after.hp - u.hp : -u.hp - 8) * 8;
    return score;
  }
  const effect = c!.effect,
    v = c!.value ?? 0;
  if (effect === "draw")
    return s.energy > c!.cost
      ? 80 + (next.hand.length - s.hand.length) * 4
      : -1;
  if (effect === "energy")
    return s.hp > 12 &&
      s.hand.some((id) => CARDS[id].cost > s.energy) &&
      s.energy < 3
      ? 90
      : -1;
  if (effect === "rally")
    score += s.allies.filter((u) => !u.acted).length * v * 13;
  if (effect === "ready") {
    const u = s.allies.find((u) => u.uid === a.target);
    score += u?.acted ? 80 + u.attack * 5 : -50;
  }
  if (effect === "heal") {
    const u = s.allies.find((u) => u.uid === a.target),
      after = next.allies.find((u) => u.uid === a.target);
    if (u && after) score += (after.hp - u.hp) * 8;
  }
  if (effect === "shelter")
    score += s.allies.reduce(
      (n, u) =>
        n +
        Math.min(
          v,
          s.enemies
            .filter(
              (e) => e.intent!.target === u.uid || e.intent!.target === "all",
            )
            .reduce((d, e) => d + e.intent!.damage, 0),
        ) *
          4,
      0,
    );
  if (effect === "control") {
    const e = s.enemies.find((e) => e.uid === a.target)!;
    score += (e.intent!.summon?.length ?? 0) * 35;
  }
  if (effect === "shred") {
    const e = s.enemies.find((e) => e.uid === a.target)!;
    score += e.block * 4;
  }
  return score > 0 ? score + 4 : -1;
}
function progressionScore(s: GameState, a: Action, mode: Mode, p: Progression) {
  switch (a.type) {
    case "travel":
      return mode === "solo"
        ? (
            {
              battle: 70,
              elite: 0,
              event: 80,
              shop: 100,
              camp: 10,
              boss: 100,
            } as Record<string, number>
          )[a.choice]
        : (
            {
              battle: 50,
              elite: 90,
              camp: 90,
              shop: s.floor === 4 ? 100 : 10,
              event: 5,
              boss: 100,
            } as Record<string, number>
          )[a.choice];
    case "reward":
      return a.card ? value(s, a.card, mode) : 40;
    case "buy":
      return s.deck.length < 19 && value(s, a.card, mode) >= 65
        ? value(s, a.card, mode)
        : 0;
    case "remove": {
      const c = CARDS[s.deck[a.index]];
      return mode === "solo"
        ? c.type === "summon"
          ? (p === "legal-buy-first" ? 95 : 180) + c.cost
          : c.effect === "heal"
            ? 80
            : 0
        : c.effect === "heal"
          ? 50
          : 0;
    }
    case "camp":
      return a.choice === "rest"
        ? s.hp < 42
          ? 180
          : 0
        : 50 +
            (base(s.deck[a.index!]) === "silence"
              ? 80
              : base(s.deck[a.index!]) === "survey"
                ? 65
                : base(s.deck[a.index!]) === "edict"
                  ? 50
                  : 10);
    case "event":
      return a.choice === "bargain" && s.hp < 52
        ? 150
        : a.choice === "offering" && s.hp > 35
          ? 100
          : a.choice === "forage"
            ? 80
            : 0;
    case "leave":
      return 1;
    default:
      return combatScore(s, a, mode);
  }
}
function actionsFor(s: GameState, p: Progression) {
  if (p === "proposal-removal-15" && s.phase === "shop") {
    const funded = { ...s, gold: s.gold + 20 };
    return legalActions(funded).filter((a) =>
      a.type === "remove"
        ? CARDS[s.deck[a.index]].type === "summon" || s.gold >= 35
        : a.type !== "buy" ||
          legalActions(s).some((b) => b.type === "buy" && b.card === a.card),
    );
  }
  return legalActions(s);
}
function reduce(s: GameState, a: Action, p: Progression) {
  if (
    p === "proposal-removal-15" &&
    a.type === "remove" &&
    CARDS[s.deck[a.index]].type === "summon"
  ) {
    // Explicit proposed cost: fund20, reducer charges35, actual net cost15.
    const funded = { ...s, gold: s.gold + 20 };
    return applyAction(funded, a);
  }
  return applyAction(s, a);
}
function choose(s: GameState, mode: Mode, p: Progression) {
  const actions = actionsFor(s, p);
  return actions.reduce(
    (best, a) =>
      progressionScore(s, a, mode, p) > progressionScore(s, best, mode, p)
        ? a
        : best,
    actions[0],
  );
}
function runProgression(
  seed: number,
  difficulty: number,
  p: Progression,
  keepTrace = false,
  mode: Mode = "solo",
) {
  let s = createGame(seed, difficulty);
  if (p === "counterfactual-ready-opening") {
    let i = 0;
    s.deck = s.deck.map((id) =>
      CARDS[id].type === "summon" ? packet[i++] : id,
    );
  }
  let steps = 0,
    minHp = s.hp,
    removalSpend = 0,
    creatureRemovals = 0,
    purchases = 0,
    firstRemovalNode: number | null = null,
    bossEntry: GameState | undefined;
  const trace: unknown[] = [],
    encounters: unknown[] = [];
  let current:
    | {
        floor: number;
        foes: string[];
        startHp: number;
        endHp: number;
        turns: number;
        drawDead: number;
      }
    | undefined;
  for (; steps < 3000; steps++) {
    const actions = actionsFor(s, p);
    if (!actions.length) break;
    const a = choose(s, mode, p);
    if (keepTrace) trace.push({ before: s, action: a });
    if (a.type === "remove") {
      const creature = CARDS[s.deck[a.index]].type === "summon";
      creatureRemovals += creature ? 1 : 0;
      removalSpend += p === "proposal-removal-15" && creature ? 15 : 35;
      if (firstRemovalNode === null) firstRemovalNode = s.floor;
    }
    if (a.type === "buy") purchases++;
    const prev = s;
    s = reduce(s, a, p);
    if (s === prev || !validateState(s))
      throw Error(
        "Progression rejected or invalid " +
          JSON.stringify({ seed, difficulty, p, a }),
      );
    minHp = Math.min(minHp, s.hp);
    if (prev.phase !== "battle" && s.phase === "battle") {
      current = {
        floor: s.floor,
        foes: s.enemies.map((e) => e.cardId),
        startHp: s.hp,
        endHp: s.hp,
        turns: 1,
        drawDead: s.hand.filter((id) => CARDS[id].type === "summon").length,
      };
      if (s.route[0] === "boss") bossEntry = structuredClone(s);
    }
    if (current && prev.phase === "battle") {
      current.endHp = s.hp;
      current.turns = Math.max(current.turns, prev.turn);
      if (a.type === "endTurn" && s.phase === "battle")
        current.drawDead += s.hand.filter(
          (id) => CARDS[id].type === "summon",
        ).length;
      if (s.phase !== "battle") {
        encounters.push(current);
        current = undefined;
      }
    }
  }
  if (!["victory", "defeat"].includes(s.phase))
    throw Error("Incomplete progression");
  return {
    record: {
      seed,
      difficulty,
      mode,
      treatment: p,
      boss: bossForSeed(seed),
      phase: s.phase,
      floor: s.floor,
      hp: s.hp,
      minHp,
      turns: s.stats.turns,
      steps,
      removalSpend,
      creatureRemovals,
      firstRemovalNode,
      purchases,
      remainingCreatures: s.deck.filter((id) => CARDS[id].type === "summon")
        .length,
      gold: s.gold,
      deck: s.deck,
      encounters,
      ...(keepTrace ? { trace } : {}),
    },
    bossEntry,
  };
}
function canonical(seed: number, difficulty: number, node: number) {
  const map = createGame(seed, difficulty);
  map.floor = node - 1;
  map.route = [node === 10 ? "boss" : "battle"];
  const s = applyAction(map, { type: "travel", choice: map.route[0] });
  if (!validateState(s)) throw Error("Invalid canonical encounter");
  return s;
}
function fixture(
  template: GameState,
  entries: Entry[],
  seed: number,
  hp: number,
) {
  const s = structuredClone(template);
  s.deck = entries.map((e) => e.id);
  const ranked = entries
    .map((e) => ({ ...e, rank: mix(seed, e.key) }))
    .sort((a, b) => a.rank - b.rank || a.key - b.key);
  const shuffled = ranked.map((e) => e.id);
  s.hand = [];
  s.draw = shuffled;
  s.discard = [];
  s.allies = [];
  s.hp = hp;
  s.block = 0;
  for (let i = 0; i < 5 && s.draw.length; i++) s.hand.push(s.draw.pop()!);
  if (!validateState(s)) throw Error("Invalid paired deck fixture");
  return s;
}
function fight(s: GameState, mode: Mode, keepTrace = false) {
  const initial = structuredClone(s),
    trace: unknown[] = [],
    cardsUsed: Record<string, number> = {};
  let steps = 0,
    minHp = s.hp,
    drawDead = s.hand.filter((id) => CARDS[id].type === "summon").length;
  for (; steps < 1500 && s.phase === "battle"; steps++) {
    const a = choose(s, mode, "legal-remove-first");
    if (keepTrace) trace.push({ before: s, action: a });
    if (a.type === "play") {
      const id = base(s.hand[a.index]);
      cardsUsed[id] = (cardsUsed[id] ?? 0) + 1;
    }
    const next = applyAction(s, a);
    if (next === s || !validateState(next))
      throw Error("Matched fixture invalid");
    s = next;
    minHp = Math.min(minHp, s.hp);
    if (a.type === "endTurn")
      drawDead += s.hand.filter((id) => CARDS[id].type === "summon").length;
  }
  if (s.phase === "battle") throw Error("Matched fixture incomplete");
  return {
    phase: s.phase,
    hp: s.hp,
    minHp,
    turns: initial.turn + s.stats.turns - initial.stats.turns,
    steps,
    drawDead,
    cardsUsed,
    ...(keepTrace ? { initial, trace } : {}),
  };
}
function entriesFor(treatment: string): Entry[] {
  const original = STARTER_DECK.map((id, key) => ({ id, key })),
    trimmed = original.filter((e) => CARDS[e.id].type !== "summon");
  if (treatment === "starter") return original;
  if (treatment === "remove-bindings") return trimmed;
  const added = packet.map((id, i) => ({ id, key: 100 + i }));
  return treatment === "buy-packet"
    ? original.concat(added)
    : trimmed.concat(added);
}
function matchedSolo(
  seed: number,
  difficulty: number,
  node: number,
  hp: number,
  keepTrace: boolean,
) {
  const template = canonical(seed, difficulty, node);
  return ["starter", "remove-bindings", "buy-packet", "remove-and-buy"].map(
    (treatment) => ({
      seed,
      difficulty,
      node,
      hpStart: hp,
      boss: node === 10 ? bossForSeed(seed) : null,
      treatment,
      fixtureEnemyHash: createHash("sha256")
        .update(JSON.stringify(template.enemies))
        .digest("hex"),
      fixtureRng: template.rng,
      ...fight(
        fixture(template, entriesFor(treatment), seed, hp),
        "solo",
        keepTrace,
      ),
    }),
  );
}
function bossPair(seed: number, difficulty: number, keepTrace: boolean) {
  const path = runProgression(
    seed,
    difficulty,
    "legal-remove-first",
    false,
    "pack",
  );
  if (!path.bossEntry)
    return {
      seed,
      difficulty,
      reached: false,
      wholeRun: path.record.phase,
      tests: [],
    };
  const s = path.bossEntry,
    boss = bossForSeed(seed);
  const counter =
    boss === "cantor" ? "silence" : boss === "ironjaw" ? "sunder" : "aegis";
  const entries = s.deck.map((id, key) => ({ id, key }));
  const index = entries.findIndex((e) => base(e.id) === "scour");
  if (index < 0) throw Error("No generic swap slot");
  const treatments = [
    { name: "original-slot", id: entries[index].id },
    { name: "quarry-counter", id: counter },
    { name: "general-sustain", id: "gravetithe" },
  ];
  const tests = treatments.map((t) => {
    const changed = entries.map((e, i) =>
      i === index ? { ...e, id: t.id } : e,
    );
    return {
      seed,
      difficulty,
      boss,
      treatment: t.name,
      card: t.id,
      swapIndex: index,
      startHp: s.hp,
      fixtureEnemyHash: createHash("sha256")
        .update(JSON.stringify(s.enemies))
        .digest("hex"),
      fixtureRng: s.rng,
      ...fight(fixture(s, changed, seed ^ 0x61ac3b45, s.hp), "pack", keepTrace),
    };
  });
  return {
    seed,
    difficulty,
    reached: true,
    wholeRun: path.record.phase,
    tests,
  };
}
function summarize<T extends { phase: string; hp: number; turns: number }>(
  rows: T[],
) {
  const n = rows.length,
    mean = (fn: (r: T) => number) =>
      n
        ? Number((rows.reduce((sum, r) => sum + fn(r), 0) / n).toFixed(2))
        : null;
  return {
    n,
    wins: rows.filter((r) => r.phase === "victory" || r.phase === "reward")
      .length,
    defeats: rows.filter((r) => r.phase === "defeat").length,
    meanHp: mean((r) => r.hp),
    meanTurns: mean((r) => r.turns),
  };
}
const cohort = process.argv[2] === "holdout" ? "holdout" : "pilot",
  n = Math.max(
    6,
    Math.min(120, Number(process.argv[3]) || (cohort === "pilot" ? 24 : 72)),
  ),
  start = cohort === "pilot" ? 12001 : 16001;
const progressions: ReturnType<typeof runProgression>["record"][] = [],
  battles: ReturnType<typeof matchedSolo>[number][] = [],
  bossPairs: ReturnType<typeof bossPair>[] = [];
for (let i = 0; i < n; i++) {
  const seed = start + i;
  for (const difficulty of [0, 1, 2])
    for (const p of [
      "legal-buy-first",
      "legal-remove-first",
      "proposal-removal-15",
      "counterfactual-ready-opening",
    ] as Progression[])
      progressions.push(runProgression(seed, difficulty, p, i < 2).record);
  for (const difficulty of [0, 2])
    for (const node of [1, 4, 8, 10])
      for (const hp of [45, 65])
        battles.push(...matchedSolo(seed, difficulty, node, hp, i === 0));
  bossPairs.push(bossPair(seed, 2, i < 2));
}
const progressionSummary = [0, 1, 2].flatMap((difficulty) =>
  [
    "legal-buy-first",
    "legal-remove-first",
    "proposal-removal-15",
    "counterfactual-ready-opening",
  ].map((treatment) => {
    const rows = progressions.filter(
        (r) => r.difficulty === difficulty && r.treatment === treatment,
      ),
      mean = (fn: (r: (typeof rows)[number]) => number) =>
        Number((rows.reduce((s, r) => s + fn(r), 0) / rows.length).toFixed(2));
    return {
      difficulty,
      treatment,
      ...summarize(rows),
      meanRemovalSpend: mean((r) => r.removalSpend),
      meanCreatureRemovals: mean((r) => r.creatureRemovals),
      meanRemainingCreatures: mean((r) => r.remainingCreatures),
      preBossDefeats: rows.filter((r) => r.phase === "defeat" && r.floor < 10)
        .length,
      bossDefeats: rows.filter((r) => r.phase === "defeat" && r.floor === 10)
        .length,
      byQuarry: Object.fromEntries(
        ["ironjaw", "cantor", "cindermaw"].map((b) => [
          b,
          summarize(rows.filter((r) => r.boss === b)),
        ]),
      ),
    };
  }),
);
const battleSummary = [0, 2].flatMap((difficulty) =>
  [1, 4, 8, 10].flatMap((node) =>
    [45, 65].flatMap((hpStart) =>
      ["starter", "remove-bindings", "buy-packet", "remove-and-buy"].map(
        (treatment) => {
          const rows = battles.filter(
            (r) =>
              r.difficulty === difficulty &&
              r.node === node &&
              r.hpStart === hpStart &&
              r.treatment === treatment,
          );
          return {
            difficulty,
            node,
            hpStart,
            treatment,
            ...summarize(rows),
            ...(node === 10
              ? {
                  byQuarry: Object.fromEntries(
                    ["ironjaw", "cantor", "cindermaw"].map((b) => [
                      b,
                      summarize(rows.filter((r) => r.boss === b)),
                    ]),
                  ),
                }
              : {}),
          };
        },
      ),
    ),
  ),
);
const bossTests = bossPairs.flatMap((p) => p.tests);
const bossSummary = ["ironjaw", "cantor", "cindermaw"].flatMap((boss) =>
  ["original-slot", "quarry-counter", "general-sustain"].map((treatment) => ({
    boss,
    treatment,
    ...summarize(
      bossTests.filter((r) => r.boss === boss && r.treatment === treatment),
    ),
  })),
);
const pairedPreparation = bossPairs
  .filter((p) => p.reached)
  .map((p) => {
    const original = p.tests.find((r) => r.treatment === "original-slot")!,
      counter = p.tests.find((r) => r.treatment === "quarry-counter")!,
      sustain = p.tests.find((r) => r.treatment === "general-sustain")!;
    return {
      seed: p.seed,
      boss: original.boss,
      originalWon: original.phase !== "defeat",
      counterWon: counter.phase !== "defeat",
      sustainWon: sustain.phase !== "defeat",
      counterHpDelta: counter.hp - original.hp,
      sustainHpDelta: sustain.hp - original.hp,
      counterTurnDelta: counter.turns - original.turns,
    };
  });
const summary = {
  cohort,
  seedRange: [start, start + n - 1],
  n,
  progressionSummary,
  battleSummary,
  bossSummary,
  preparationReached: bossPairs.filter((p) => p.reached).length,
  preparationNotReached: bossPairs.filter((p) => !p.reached).length,
  pairedPreparation,
};
const payload = {
  version: "investigation-v0.3",
  generatedAt: new Date().toISOString(),
  sourceHashes,
  method: {
    progression:
      "Four treatments: two actual legal policies, one explicitly modified15goldcreature removal wrapper, one counterfactual startingdeck. Whole-run later RNG differs after actions; not isolated singlecard comparisons.",
    matchedSolo:
      "Frozen single-encounter enemies/HP/intentions/rng; deterministic card-slot keyed shuffle shares relative ranks across remove/acquire2x2 treatments. Counterfactual fixture states pass validation; not earned real progression states.",
    bossPreparation:
      "Actual legal pack route supplies bossentryHP/relics/deck. One Scour slot replaced by announcedquarrycounter or generalGraveTithe. All arms share enemy roster, HP,rng and keyed drawslots; cannot infer human fun or whole-run causal effect.",
  },
  summary,
  progressions,
  battles,
  bossPairs,
};
mkdirSync("reviews/solo-v0.3", { recursive: true });
writeFileSync(
  `reviews/solo-v0.3/${cohort}-summary.json`,
  JSON.stringify({ sourceHashes, ...summary }, null, 2),
);
writeFileSync(
  `reviews/solo-v0.3/${cohort}-evidence.json.gz`,
  gzipSync(JSON.stringify(payload)),
);
console.log(
  JSON.stringify(
    {
      cohort,
      n,
      sourceHashes,
      progressionSummary,
      bossSummary,
      preparationReached: summary.preparationReached,
    },
    null,
    2,
  ),
);
