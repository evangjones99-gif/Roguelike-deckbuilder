import {
  applyAction,
  createGame,
  legalActions,
  CARDS,
  validateState,
  type Action,
  type GameState,
} from "../src/engine";
export function heuristicScore(s: GameState, a: Action): number {
  switch (a.type) {
    case "travel":
      return (
        {
          camp: s.hp < s.maxHp - 15 ? 100 : 20,
          event: 40,
          shop: 25,
          elite: s.hp > 42 ? 35 : 5,
          battle: 30,
          boss: 100,
        } as Record<string, number>
      )[a.choice];
    case "play": {
      const c = CARDS[s.hand[a.index]],
        u = s.enemies.find((e) => e.uid === a.target),
        ally = s.allies.find((u) => u.uid === a.target);
      const danger =
        s.enemies.reduce(
          (v, e) =>
            v +
            (e.intent?.target === "hunter" || e.intent?.target === "all"
              ? e.intent.damage
              : 0),
          0,
        ) - s.block;
      let score =
        c.type === "summon" ? 100 + (c.attack ?? 0) * 4 - c.cost * 3 : 20;
      switch (c.effect) {
        case "damage":
        case "siphon":
        case "pack":
          score =
            55 +
            (u
              ? Math.min(
                  c.value! + (c.effect === "pack" ? s.allies.length * 2 : 0),
                  u.hp,
                )
              : 0) *
              3 +
            (u && u.hp <= c.value! ? 30 : 0);
          break;
        case "aoe":
          score =
            50 +
            s.enemies.reduce((n, e) => n + Math.min(e.hp, c.value!) * 3, 0);
          break;
        case "rally":
          score = s.allies.length
            ? 45 + s.allies.filter((u) => !u.acted).length * c.value! * 5
            : 0;
          break;
        case "block":
          score = danger > 0 ? 35 + Math.min(danger, c.value!) * 4 : 0;
          break;
        case "shelter":
          score =
            danger > 0 ||
            s.allies.some((u) =>
              s.enemies.some((e) => e.intent?.target === u.uid),
            )
              ? 70
              : 0;
          break;
        case "heal":
          score = ally ? Math.min(ally.maxHp - ally.hp, c.value!) * 10 : 0;
          break;
        case "ready":
          score = ally?.acted ? 60 + ally.attack * 3 : 0;
          break;
        case "draw":
          score = s.energy > c.cost ? 80 : 10;
          break;
        case "energy":
          score =
            s.hp > 10 && s.hand.some((id) => CARDS[id].cost > s.energy)
              ? 110
              : 0;
          break;
        case "communion":
          score = Math.min(s.maxHp - s.hp, c.value! * s.allies.length) * 8;
          break;
      }
      return score;
    }
    case "attack": {
      const u = s.allies.find((u) => u.uid === a.unit)!,
        e = s.enemies.find((e) => e.uid === a.target)!;
      return (
        65 +
        Math.min(u.attack, e.hp) * 3 +
        (u.attack >= e.hp + e.block ? 40 : 0) -
        e.block * 2
      );
    }
    case "endTurn":
      return 1;
    case "reward":
      return a.card
        ? { summon: 30, spell: 10 }[CARDS[a.card].type] +
            ([
              "rally",
              "thorns",
              "shelter",
              "siphon",
              "willowdrake",
              "moonmoth",
              "communion",
            ].includes(a.card)
              ? 30
              : 0) -
            s.deck.length
        : 5;
    case "camp":
      return a.choice === "rest" ? (s.hp < s.maxHp - 15 ? 100 : 0) : 50;
    case "buy":
      return s.deck.length < 16 &&
        (CARDS[a.card].type === "summon" ||
          ["rally", "siphon", "thorns", "shelter"].includes(a.card))
        ? 50
        : 0;
    case "remove":
      return s.deck.length > 9 && s.deck[a.index] === "spark" ? 20 : 0;
    case "leave":
      return 1;
    case "event":
      return a.choice === "offering" && s.hp > 30
        ? 60
        : a.choice === "forage"
          ? 50
          : 0;
    default:
      return 0;
  }
}
export function chooseHeuristic(s: GameState): Action {
  const actions = legalActions(s);
  return actions.reduce(
    (best, a) => (heuristicScore(s, a) > heuristicScore(s, best) ? a : best),
    actions[0],
  );
}
export function run(
  seed: number,
  policy: "random" | "heuristic",
  difficulty = 0,
) {
  let s = createGame(seed, difficulty),
    r = seed || 1,
    steps = 0;
  for (; steps < 3000 && legalActions(s).length; steps++) {
    const actions = legalActions(s);
    r = (Math.imul(r, 1664525) + 1013904223) >>> 0;
    const action =
      policy === "heuristic"
        ? chooseHeuristic(s)
        : actions[Math.floor((r / 4294967296) * actions.length)];
    s = applyAction(s, action);
    if (!validateState(s))
      throw Error(
        "Invalid state at seed " + seed + " action " + JSON.stringify(action),
      );
  }
  return {
    seed,
    policy,
    phase: s.phase,
    hp: s.hp,
    floor: s.floor,
    turns: s.stats.turns,
    steps,
  };
}
if (process.argv[1]?.endsWith("simulate.ts")) {
  const n = Math.min(1000, Math.max(1, Number(process.argv[2]) || 100));
  const results = ["random", "heuristic"].map((policy) => {
    const runs = Array.from({ length: n }, (_, i) =>
      run(i + 1, policy as "random" | "heuristic"),
    );
    return {
      policy,
      seeds: n,
      victories: runs.filter((r) => r.phase === "victory").length,
      defeats: runs.filter((r) => r.phase === "defeat").length,
      incomplete: runs.filter((r) => !["victory", "defeat"].includes(r.phase))
        .length,
      meanFloor: Number((runs.reduce((t, r) => t + r.floor, 0) / n).toFixed(2)),
      meanTurns: Number((runs.reduce((t, r) => t + r.turns, 0) / n).toFixed(2)),
    };
  });
  console.log(
    JSON.stringify(
      { version: "0.1.0", difficulty: 0, seedRange: [1, n], results },
      null,
      2,
    ),
  );
}
