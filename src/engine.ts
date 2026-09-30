import {
  CARDS,
  BASE_CARD_IDS,
  STARTER_DECK,
  ENEMIES,
  RELICS,
  SHOP_PRICES,
} from "./content";
export { CARDS } from "./content";
export interface CardDef {
  id: string;
  name: string;
  type: "summon" | "spell";
  cost: number;
  text: string;
  color: string;
  species?: string;
  hp?: number;
  attack?: number;
  effect?: string;
  value?: number;
}
export interface Unit {
  uid: string;
  cardId: string;
  name: string;
  species: string;
  hp: number;
  maxHp: number;
  attack: number;
  block: number;
  acted: boolean;
  intent?: { damage: number; target: string; label: string };
  color: string;
}
export interface GameState {
  schema: 1;
  seed: number;
  rng: number;
  phase:
    | "menu"
    | "map"
    | "battle"
    | "reward"
    | "camp"
    | "shop"
    | "event"
    | "victory"
    | "defeat";
  hp: number;
  maxHp: number;
  block: number;
  energy: number;
  gold: number;
  floor: number;
  turn: number;
  deck: string[];
  draw: string[];
  discard: string[];
  hand: string[];
  allies: Unit[];
  enemies: Unit[];
  rewards: string[];
  relics: string[];
  route: string[];
  log: string[];
  nextUid: number;
  difficulty: number;
  stats: {
    cardsPlayed: number;
    damageDealt: number;
    turns: number;
    battles: number;
  };
}
export type Action =
  | { type: "start"; seed: number; difficulty?: number }
  | { type: "travel"; choice: string }
  | { type: "play"; index: number; target?: string }
  | { type: "attack"; unit: string; target: string }
  | { type: "endTurn" }
  | { type: "reward"; card: string | null }
  | { type: "camp"; choice: "rest" | "train" }
  | { type: "buy"; card: string }
  | { type: "remove"; index: number }
  | { type: "leave" }
  | { type: "event"; choice: string };
const ROUTES = [
  ["battle"],
  ["battle", "event"],
  ["camp", "shop"],
  ["battle", "elite"],
  ["event", "shop"],
  ["battle", "elite"],
  ["camp", "shop"],
  ["elite", "battle"],
  ["camp", "event"],
  ["boss"],
];
const count = (xs: string[]) =>
  xs.reduce<Record<string, number>>(
    (m, id) => ((m[id] = (m[id] ?? 0) + 1), m),
    {},
  );
const baseId = (id: string) => id.replace("+", "");
function random(s: GameState): number {
  let x = s.rng;
  x ^= x << 13;
  x ^= x >>> 17;
  x ^= x << 5;
  s.rng = x >>> 0;
  return s.rng / 4294967296;
}
function shuffle(s: GameState, cards: string[]): string[] {
  const a = cards.slice();
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(random(s) * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}
function note(s: GameState, t: string) {
  s.log.push(t);
  s.log = s.log.slice(-60);
}
function map(s: GameState) {
  s.phase = "map";
  s.route = ROUTES[s.floor]?.slice() ?? [];
  s.rewards = [];
}
export function createGame(seed: number, difficulty = 0): GameState {
  const value = Number.isFinite(seed) ? Math.trunc(seed) >>> 0 : 1;
  return {
    schema: 1,
    seed: value,
    rng: value || 0x9e3779b9,
    phase: "map",
    hp: 65,
    maxHp: 65,
    block: 0,
    energy: 0,
    gold: 65,
    floor: 0,
    turn: 0,
    deck: STARTER_DECK.slice(),
    draw: [],
    discard: [],
    hand: [],
    allies: [],
    enemies: [],
    rewards: [],
    relics: [],
    route: ROUTES[0].slice(),
    log: ["Carry the lantern to the Hollow Crown."],
    nextUid: 1,
    difficulty: Math.max(
      0,
      Math.min(2, Math.trunc(Number.isFinite(difficulty) ? difficulty : 0)),
    ),
    stats: { cardsPlayed: 0, damageDealt: 0, turns: 0, battles: 0 },
  };
}
export function cardTarget(id: string): "enemy" | "ally" | "none" {
  const c = CARDS[id];
  return !c || c.type === "summon"
    ? "none"
    : ["damage", "siphon", "pack"].includes(c.effect!)
      ? "enemy"
      : ["heal", "ready"].includes(c.effect!)
        ? "ally"
        : "none";
}
function draw(s: GameState, n: number) {
  for (let i = 0; i < n && s.hand.length < 12; i++) {
    if (!s.draw.length) {
      s.draw = shuffle(s, s.discard);
      s.discard = [];
    }
    const id = s.draw.pop();
    if (!id) break;
    s.hand.push(id);
  }
}
function enemy(s: GameState, id: string): Unit {
  const e = ENEMIES[id];
  const scale = Math.max(0, s.floor - 1) + s.difficulty * 2;
  return {
    uid: "e" + s.nextUid++,
    cardId: id,
    ...e,
    hp: e.hp + scale,
    maxHp: e.hp + scale,
    attack: e.attack + Math.floor(scale / 4),
    block: 0,
    acted: false,
  };
}
function intentions(s: GameState) {
  for (const e of s.enemies) {
    const ally = s.allies.slice().sort((a, b) => a.hp - b.hp)[0];
    let target = "hunter",
      damage = e.attack,
      label = "Strike";
    switch (e.cardId) {
      case "briar":
        target = ally?.uid ?? "hunter";
        label = "Snag weakest companion";
        break;
      case "wolf":
        target = s.allies[0]?.uid ?? "hunter";
        damage += s.turn % 3 === 0 ? 4 : 0;
        label = s.turn % 3 === 0 ? "Savage pounce" : "Pounce";
        break;
      case "sentinel":
        if (s.turn % 2 === 1) {
          damage = 0;
          target = e.uid;
          label = "Root armor · gain 6 block";
        } else {
          damage += 3;
          label = "Heavy branch";
        }
        break;
      case "witch":
        damage += s.turn % 2 === 0 ? 3 : 0;
        label = "Lantern curse";
        break;
      case "wisp":
        label = "Piercing light · ignores block";
        break;
      case "crown":
        if (s.turn % 3 === 1) {
          damage = 0;
          target = e.uid;
          label = "Gather roots · gain 10 block";
        } else if (s.turn % 3 === 2) {
          target = "all";
          damage = 5 + s.difficulty;
          label = "Forest quake · all targets";
        } else {
          damage += 5;
          label = "Extinguish lantern";
        }
        break;
    }
    e.intent = { target, damage, label };
  }
}
function beginBattle(s: GameState, kind: string) {
  s.phase = "battle";
  s.route = [kind];
  s.block = 0;
  s.energy = 5 + (s.relics.includes("brass-bell") ? 1 : 0);
  s.turn = 1;
  s.allies = [];
  s.hand = [];
  s.discard = [];
  s.draw = shuffle(s, s.deck);
  s.stats.battles++;
  const sets =
    kind === "boss"
      ? [["crown", "wisp"]]
      : kind === "elite"
        ? [
            ["sentinel", "witch"],
            ["wolf", "wolf", "wisp"],
          ]
        : s.floor <= 2
          ? [
              ["briar", "wisp"],
              ["briar", "briar"],
            ]
          : [
              ["wolf", "wisp"],
              ["sentinel", "briar"],
              ["witch", "briar", "wisp"],
            ];
  s.enemies = sets[Math.floor(random(s) * sets.length)].map((id) =>
    enemy(s, id),
  );
  draw(s, 5);
  intentions(s);
  note(
    s,
    kind === "boss"
      ? "The Hollow Crown rises."
      : kind === "elite"
        ? "An elder contract awaits."
        : "The woodland stirs.",
  );
}
function hitUnit(
  s: GameState,
  u: Unit,
  damage: number,
  source: boolean,
  pierce = false,
) {
  const dealt = Math.min(u.hp, Math.max(0, damage - (pierce ? 0 : u.block)));
  if (!pierce) u.block = Math.max(0, u.block - damage);
  u.hp -= dealt;
  if (source) s.stats.damageDealt += dealt;
}
function hitHunter(s: GameState, damage: number, pierce = false) {
  const dealt = Math.max(0, damage - (pierce ? 0 : s.block));
  if (!pierce) s.block = Math.max(0, s.block - damage);
  s.hp = Math.max(0, s.hp - dealt);
}
function heal(s: GameState, n: number) {
  s.hp = Math.min(s.maxHp, s.hp + n);
}
function clean(s: GameState) {
  for (const a of s.allies)
    if (a.hp <= 0) {
      s.discard.push(a.cardId);
      note(s, a.name + " returns to the deck.");
    }
  s.allies = s.allies.filter((a) => a.hp > 0);
  s.enemies = s.enemies.filter((e) => e.hp > 0);
}
function finish(s: GameState) {
  clean(s);
  if (s.hp <= 0) {
    s.phase = "defeat";
    note(s, "The lantern fades. A new path awaits.");
    return;
  }
  if (s.enemies.length) return;
  const kind = s.route[0];
  s.hand = [];
  s.draw = [];
  s.discard = [];
  s.allies = [];
  s.block = 0;
  s.energy = 0;
  s.gold += kind === "elite" ? 40 : 25;
  heal(s, kind === "elite" ? 5 : 3);
  if (kind === "boss") {
    s.phase = "victory";
    s.route = [];
    note(s, "Dawn returns. The Hollow Crown is unbound.");
  } else {
    if (kind === "elite") {
      const available = Object.keys(RELICS).filter(
        (id) => !s.relics.includes(id),
      );
      if (available.length) {
        const id = available[Math.floor(random(s) * available.length)];
        s.relics.push(id);
        note(s, "Relic found: " + RELICS[id].name);
      }
    }
    s.phase = "reward";
    s.rewards = shuffle(s, BASE_CARD_IDS).slice(0, 3);
    note(s, "Contract complete. Choose one new card or travel light.");
  }
}
function play(s: GameState, a: Extract<Action, { type: "play" }>) {
  const id = s.hand.splice(a.index, 1)[0],
    c = CARDS[id];
  s.energy -= c.cost;
  s.stats.cardsPlayed++;
  if (c.type === "summon") {
    const bonus = s.relics.includes("ember-seed") ? 2 : 0;
    const u: Unit = {
      uid: "a" + s.nextUid++,
      cardId: id,
      name: c.name,
      species: c.species!,
      hp: c.hp! + bonus,
      maxHp: c.hp! + bonus,
      attack: c.attack!,
      block: 0,
      acted: false,
      color: c.color,
    };
    s.allies.push(u);
    switch (baseId(id)) {
      case "mossling":
        s.block += 3;
        break;
      case "cinderfox":
        for (const e of s.enemies) hitUnit(s, e, 2, true);
        break;
      case "reedkin":
        draw(s, 1);
        break;
      case "stonehart":
        s.block += 8;
        break;
      case "brookotter":
        heal(s, 3);
        break;
      case "thunderrook":
        for (const ally of s.allies) if (ally.uid !== u.uid) ally.attack++;
        break;
      case "lanternowl":
        s.energy++;
        break;
      case "bogturtle":
        for (const ally of s.allies) ally.block += 4;
        break;
      case "glimmerhare":
        for (const ally of s.allies) if (ally.uid !== u.uid) ally.block += 2;
        break;
      case "willowdrake":
        for (const e of s.enemies) hitUnit(s, e, 4, true);
        break;
    }
    note(s, "Summoned " + c.name + ".");
  } else {
    const v = c.value ?? 0,
      bonus = s.relics.includes("moon-charm") ? 1 : 0;
    const target = s.enemies.find((e) => e.uid === a.target),
      ally = s.allies.find((u) => u.uid === a.target);
    switch (c.effect) {
      case "damage":
        hitUnit(s, target!, v + bonus, true);
        break;
      case "block":
        s.block += v;
        break;
      case "heal":
        ally!.hp = Math.min(ally!.maxHp, ally!.hp + v);
        ally!.block += 2;
        break;
      case "rally":
        for (const u of s.allies) u.attack += v;
        break;
      case "aoe":
        for (const e of s.enemies) hitUnit(s, e, v + bonus, true);
        break;
      case "ready":
        ally!.acted = false;
        ally!.block += v;
        break;
      case "siphon":
        hitUnit(s, target!, v + bonus, true);
        heal(s, 3);
        break;
      case "draw":
        draw(s, v);
        break;
      case "energy":
        s.energy += v;
        s.hp = Math.max(0, s.hp - 2);
        break;
      case "shelter":
        s.block += v;
        for (const u of s.allies) u.block += v;
        break;
      case "pack":
        hitUnit(s, target!, v + s.allies.length * 2 + bonus, true);
        break;
      case "communion":
        heal(s, v * s.allies.length);
        break;
    }
    s.discard.push(id);
    for (const u of s.allies) if (baseId(u.cardId) === "moonmoth") s.block += 2;
    note(s, "Cast " + c.name + ".");
  }
  finish(s);
}
function endTurn(s: GameState) {
  for (const e of s.enemies) e.block = 0;
  for (const e of s.enemies) {
    const i = e.intent!;
    if (i.damage === 0) {
      e.block += e.cardId === "crown" ? 10 : 6;
      note(s, e.name + " gathers armor.");
      continue;
    }
    if (i.target === "all") {
      hitHunter(s, i.damage);
      for (const u of s.allies) hitUnit(s, u, i.damage, false);
    } else {
      const u = s.allies.find((u) => u.uid === i.target && u.hp > 0);
      if (u) hitUnit(s, u, i.damage, false, e.cardId === "wisp");
      else hitHunter(s, i.damage, e.cardId === "wisp");
    }
    note(s, e.name + ": " + i.label + ".");
    clean(s);
    if (s.hp <= 0) break;
  }
  finish(s);
  if (s.phase !== "battle") return;
  s.discard.push(...s.hand);
  s.hand = [];
  s.block = 0;
  for (const u of s.allies) {
    u.block = 0;
    u.acted = false;
  }
  s.turn++;
  s.stats.turns++;
  s.energy = 5;
  draw(s, 5);
  intentions(s);
  note(s, "Turn " + s.turn + ".");
}
export function legalActions(s: GameState): Action[] {
  if (s.phase === "map")
    return s.route.map((choice) => ({ type: "travel", choice }));
  if (s.phase === "battle") {
    const actions: Action[] = [];
    s.hand.forEach((id, index) => {
      const c = CARDS[id];
      if (c.cost > s.energy || (c.type === "summon" && s.allies.length >= 6))
        return;
      const t = cardTarget(id);
      if (t === "none") actions.push({ type: "play", index });
      else
        for (const u of t === "enemy" ? s.enemies : s.allies)
          actions.push({ type: "play", index, target: u.uid });
    });
    for (const u of s.allies)
      if (!u.acted)
        for (const e of s.enemies)
          actions.push({ type: "attack", unit: u.uid, target: e.uid });
    actions.push({ type: "endTurn" });
    return actions;
  }
  if (s.phase === "reward")
    return [
      ...(s.deck.length < 60
        ? s.rewards.map((card) => ({ type: "reward" as const, card }))
        : []),
      { type: "reward", card: null },
    ];
  if (s.phase === "camp")
    return [
      { type: "camp", choice: "rest" },
      ...(s.deck.some((id) => !id.endsWith("+"))
        ? [{ type: "camp" as const, choice: "train" as const }]
        : []),
    ];
  if (s.phase === "shop")
    return [
      ...(s.deck.length < 60
        ? s.rewards
            .filter((id) => s.gold >= SHOP_PRICES[CARDS[id].type])
            .map((card) => ({ type: "buy" as const, card }))
        : []),
      ...(s.gold >= SHOP_PRICES.remove && s.deck.length > 5
        ? s.deck.map((_, index) => ({ type: "remove" as const, index }))
        : []),
      { type: "leave" },
    ];
  if (s.phase === "event")
    return [
      ...(s.hp > 8 && !s.relics.includes("moon-charm")
        ? [{ type: "event" as const, choice: "offering" }]
        : []),
      { type: "event", choice: "forage" },
      { type: "event", choice: "leave" },
    ];
  return [];
}
function matches(a: Action, b: Action): boolean {
  if (!a || typeof a !== "object" || a.type !== b.type) return false;
  switch (b.type) {
    case "play":
      return a.type === "play" && a.index === b.index && a.target === b.target;
    case "attack":
      return a.type === "attack" && a.unit === b.unit && a.target === b.target;
    case "travel":
    case "camp":
    case "event":
      return "choice" in a && a.choice === b.choice;
    case "reward":
    case "buy":
      return "card" in a && a.card === b.card;
    case "remove":
      return a.type === "remove" && a.index === b.index;
    default:
      return true;
  }
}
export function applyAction(state: GameState, action: Action): GameState {
  if (action?.type === "start") {
    if (!Number.isFinite(action.seed)) return state;
    return createGame(action.seed, action.difficulty);
  }
  if (!legalActions(state).some((a) => matches(action, a))) return state;
  const s = structuredClone(state);
  switch (action.type) {
    case "travel":
      s.floor++;
      if (["battle", "elite", "boss"].includes(action.choice))
        beginBattle(s, action.choice);
      else {
        s.phase = action.choice as "camp" | "shop" | "event";
        s.route = [action.choice];
        if (action.choice === "shop")
          s.rewards = shuffle(s, BASE_CARD_IDS).slice(0, 5);
        note(s, "Reached the " + action.choice + ".");
      }
      break;
    case "play":
      play(s, action);
      break;
    case "attack": {
      const u = s.allies.find((u) => u.uid === action.unit)!,
        e = s.enemies.find((e) => e.uid === action.target)!;
      u.acted = true;
      hitUnit(s, e, u.attack, true);
      if (baseId(u.cardId) === "bramblecat") s.block += 2;
      note(s, u.name + " strikes " + e.name + ".");
      finish(s);
      break;
    }
    case "endTurn":
      endTurn(s);
      break;
    case "reward":
      if (action.card) s.deck.push(action.card);
      map(s);
      break;
    case "camp":
      if (action.choice === "rest") {
        heal(s, 18);
        note(s, "Restored 18 HP by the lantern.");
      } else {
        const id =
          s.deck.find(
            (id) => !id.endsWith("+") && CARDS[id].type === "summon",
          ) ?? s.deck.find((id) => !id.endsWith("+"))!;
        s.deck[s.deck.indexOf(id)] = id + "+";
        note(s, "Trained " + CARDS[id].name + ".");
      }
      map(s);
      break;
    case "buy":
      s.gold -= SHOP_PRICES[CARDS[action.card].type];
      s.deck.push(action.card);
      s.rewards.splice(s.rewards.indexOf(action.card), 1);
      note(s, "Purchased " + CARDS[action.card].name + ".");
      break;
    case "remove":
      s.gold -= SHOP_PRICES.remove;
      note(s, "Released " + CARDS[s.deck[action.index]].name + ".");
      s.deck.splice(action.index, 1);
      break;
    case "leave":
      map(s);
      break;
    case "event":
      if (action.choice === "offering") {
        s.hp -= 8;
        s.relics.push("moon-charm");
        note(s, "The moon accepts your light.");
      } else if (action.choice === "forage") {
        s.gold += 25;
        note(s, "Found 25 gold beneath the roots.");
      }
      map(s);
      break;
  }
  return s;
}
/** Validate untrusted JSON without executing reducer code. Bounds prevent pathological saves. */
export function validateState(value: unknown): value is GameState {
  try {
    if (!value || typeof value !== "object" || Array.isArray(value))
      return false;
    const s = value as GameState;
    const integer = (v: unknown, min = 0, max = 1000000) =>
      typeof v === "number" && Number.isInteger(v) && v >= min && v <= max;
    const strings = (v: unknown, max: number) =>
      Array.isArray(v) &&
      v.length <= max &&
      v.every((x) => typeof x === "string" && x.length < 400);
    if (
      s.schema !== 1 ||
      ![
        "map",
        "battle",
        "reward",
        "camp",
        "shop",
        "event",
        "victory",
        "defeat",
      ].includes(s.phase)
    )
      return false;
    if (
      !integer(s.seed, 0, 4294967295) ||
      !integer(s.rng, 1, 4294967295) ||
      !integer(s.hp, 0, 1000) ||
      !integer(s.maxHp, 1, 1000) ||
      s.hp > s.maxHp ||
      !integer(s.block) ||
      !integer(s.energy, 0, 1000) ||
      !integer(s.gold) ||
      !integer(s.floor, 0, 10) ||
      !integer(s.turn, 0, 10000) ||
      !integer(s.nextUid, 1, 1000000) ||
      !integer(s.difficulty, 0, 2)
    )
      return false;
    for (const [key, max] of [
      ["deck", 60],
      ["draw", 60],
      ["discard", 60],
      ["hand", 12],
      ["rewards", 5],
    ] as const)
      if (
        !strings(s[key], max) ||
        s[key].some((id) => !Object.hasOwn(CARDS, id))
      )
        return false;
    if (
      s.deck.length < 5 ||
      !strings(s.log, 60) ||
      !strings(s.relics, 3) ||
      new Set(s.relics).size !== s.relics.length ||
      s.relics.some((id) => !Object.hasOwn(RELICS, id)) ||
      !strings(s.route, 3) ||
      s.route.some(
        (id) =>
          !["battle", "elite", "camp", "shop", "event", "boss"].includes(id),
      )
    )
      return false;
    if (
      !s.stats ||
      typeof s.stats !== "object" ||
      !["cardsPlayed", "damageDealt", "turns", "battles"].every((k) =>
        integer(s.stats[k as keyof typeof s.stats]),
      )
    )
      return false;
    if (
      !Array.isArray(s.allies) ||
      !Array.isArray(s.enemies) ||
      s.allies.length > 6 ||
      s.enemies.length > 6
    )
      return false;
    const ids = new Set<string>();
    for (const [list, ally] of [
      [s.allies, true],
      [s.enemies, false],
    ] as const)
      for (const u of list) {
        if (
          !u ||
          typeof u !== "object" ||
          typeof u.uid !== "string" ||
          !new RegExp(ally ? "^a[1-9][0-9]*$" : "^e[1-9][0-9]*$").test(u.uid) ||
          ids.has(u.uid) ||
          Number(u.uid.slice(1)) >= s.nextUid
        )
          return false;
        ids.add(u.uid);
        const def = ally ? CARDS[u.cardId] : ENEMIES[u.cardId];
        if (
          !Object.hasOwn(ally ? CARDS : ENEMIES, u.cardId) ||
          !def ||
          (ally && CARDS[u.cardId].type !== "summon") ||
          typeof u.name !== "string" ||
          u.name.length > 100 ||
          typeof u.species !== "string" ||
          u.species !== def.species ||
          typeof u.color !== "string" ||
          !/^#[\da-fA-F]{6}$/.test(u.color) ||
          !integer(u.hp, 1, 1000) ||
          !integer(u.maxHp, 1, 1000) ||
          u.hp > u.maxHp ||
          !integer(u.attack, 0, 10000) ||
          !integer(u.block) ||
          typeof u.acted !== "boolean"
        )
          return false;
        if (!ally && (s.phase === "battle" || s.phase === "defeat")) {
          const i = u.intent;
          if (
            !i ||
            !integer(i.damage, 0, 10000) ||
            typeof i.target !== "string" ||
            !(
              i.target === "hunter" ||
              i.target === "all" ||
              i.target === u.uid ||
              /^a[1-9][0-9]*$/.test(i.target)
            ) ||
            typeof i.label !== "string" ||
            i.label.length > 100
          )
            return false;
        }
      }
    if (s.phase === "battle" || s.phase === "defeat") {
      if (
        (s.phase === "battle" && (s.hp === 0 || s.enemies.length === 0)) ||
        (s.phase === "defeat" && s.hp !== 0) ||
        s.turn < 1 ||
        s.floor < 1 ||
        s.route.length !== 1 ||
        !["battle", "elite", "boss"].includes(s.route[0])
      )
        return false;
      const actual = count([
          ...s.draw,
          ...s.discard,
          ...s.hand,
          ...s.allies.map((a) => a.cardId),
        ]),
        expected = count(s.deck);
      if (
        Object.keys(actual).length !== Object.keys(expected).length ||
        Object.keys(expected).some((id) => actual[id] !== expected[id])
      )
        return false;
    } else if (
      s.allies.length ||
      s.enemies.length ||
      s.hand.length ||
      s.draw.length ||
      s.discard.length ||
      s.hp === 0
    )
      return false;
    if (s.phase === "map" && s.floor >= 10) return false;
    if (
      s.phase === "map" &&
      JSON.stringify(s.route) !== JSON.stringify(ROUTES[s.floor] ?? [])
    )
      return false;
    if (s.phase === "victory" && (s.floor !== 10 || s.route.length))
      return false;
    // During an encounter, floor names the node already entered. A saved
    // encounter must be one of that node's actual choices, not merely a
    // recognized route string. This also reserves node ten for the boss.
    if (
      ["battle", "defeat", "reward", "camp", "shop", "event"].includes(
        s.phase,
      ) &&
      (s.route.length !== 1 || !ROUTES[s.floor - 1]?.includes(s.route[0]))
    )
      return false;
    if (
      s.phase === "reward" &&
      (s.rewards.length !== 3 ||
        s.floor < 1 ||
        s.floor >= 10 ||
        s.route.length !== 1 ||
        !["battle", "elite"].includes(s.route[0]))
    )
      return false;
    if (
      ["camp", "shop", "event"].includes(s.phase) &&
      (s.floor < 1 || s.floor >= 10 || s.route.length !== 1)
    )
      return false;
    if (
      (s.phase === "camp" && s.route[0] !== "camp") ||
      (s.phase === "shop" && s.route[0] !== "shop") ||
      (s.phase === "event" && s.route[0] !== "event")
    )
      return false;
    return true;
  } catch {
    return false;
  }
}
