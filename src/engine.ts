import {
  CARDS,
  BASE_CARD_IDS,
  STARTER_DECK,
  ENEMIES,
  RELICS,
  SHOP_PRICES,
  bossForSeed,
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
  passive?: string;
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
  intent?: { damage: number; target: string; label: string; summon?: string[] };
  passive?: string;
  color: string;
}
export interface GameState {
  schema: 2;
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
  | { type: "camp"; choice: "rest" | "train"; index?: number }
  | { type: "buy"; card: string }
  | { type: "remove"; index: number }
  | { type: "leave" }
  | { type: "event"; choice: string };
/** Ordered observations of actual resolution. Never saved or used for game rules. */
export type ResolvedHitKind =
  "command" | "spell" | "enemy" | "retaliation" | "summon" | "self";
export type ResolvedEvent =
  | {
      type: "hit";
      source: string;
      target: string;
      kind: ResolvedHitKind;
      damage: number;
      blocked: number;
      hpLost: number;
      beforeHp: number;
      afterHp: number;
      cardId?: string;
    }
  | {
      type: "heal";
      source: string;
      target: string;
      amount: number;
      beforeHp: number;
      afterHp: number;
    }
  | { type: "ward"; source: string; target: string; amount: number }
  | {
      type: "control";
      source: string;
      target: string;
      cardId: string;
      before: NonNullable<Unit["intent"]>;
      after: NonNullable<Unit["intent"]>;
    }
  | {
      type: "buff";
      source: string;
      target: string;
      cardId: string;
      stat: "attack";
      before: number;
      after: number;
      amount: number;
    }
  | {
      type: "summon";
      source: string;
      target: string;
      cardId: string;
      unit: Unit;
      side: "ally" | "enemy";
    }
  | { type: "death"; source: string; target: string; cardId?: string };
export type TransitionEvent = ResolvedEvent;
interface ResolutionTrace {
  events: ResolvedEvent[];
  source: string;
  kind: ResolvedHitKind;
  cardId?: string;
}
function trace(
  events: ResolvedEvent[] | undefined,
  source: string,
  kind: ResolvedHitKind,
  cardId?: string,
): ResolutionTrace | undefined {
  return events
    ? { events, source, kind, ...(cardId ? { cardId } : {}) }
    : undefined;
}
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
    schema: 2,
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
    log: ["A scarred hunter. One final contract. No pact is harmless."],
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
    : ["damage", "siphon", "pack", "shred", "control", "solo"].includes(
          c.effect!,
        )
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
  const boss = ["ironjaw", "cantor", "cindermaw"].includes(id);
  const scale =
    id === "thrall"
      ? Math.floor(s.floor / 3) + s.difficulty
      : Math.max(0, s.floor - 1) + s.difficulty * (boss ? 12 : 2);
  return {
    uid: "e" + s.nextUid++,
    cardId: id,
    ...e,
    hp: e.hp + scale,
    maxHp: e.hp + scale,
    attack: e.attack + Math.floor(Math.max(0, s.floor - 1) / 4) + s.difficulty,
    block: 0,
    acted: false,
  };
}
function intentions(s: GameState) {
  for (const e of s.enemies) {
    const weakest = s.allies.slice().sort((a, b) => a.hp - b.hp)[0];
    let target = "hunter",
      damage = e.attack,
      label = "Strike",
      summon: string[] | undefined;
    switch (e.cardId) {
      case "thrall":
        target = weakest?.uid ?? "hunter";
        label = "Claw weakest creature";
        break;
      case "raider":
      case "ironjaw":
        if (s.turn % 2 === 1) {
          damage = 0;
          target = e.uid;
          label =
            e.cardId === "ironjaw"
              ? "Raise plated shield · gain 14 block"
              : "Raise shield · gain 4 block";
        } else {
          damage += e.cardId === "ironjaw" ? 3 : 1;
          label = "Iron cleaver";
        }
        break;
      case "revenant":
        label = "Spectral rend · ignores block";
        break;
      case "acolyte":
        if (s.turn % 2 === 1) {
          damage = 0;
          target = e.uid;
          summon = ["thrall"];
          label = "Raise 1 Bone Thrall";
        } else {
          label = "Grave curse";
        }
        break;
      case "brood":
        if (s.turn % 2 === 0) {
          target = "all";
          damage = 3 + s.difficulty;
          label = "Cinder breath · all targets";
        } else {
          target = s.allies[0]?.uid ?? "hunter";
          label = "Rending bite";
        }
        break;
      case "cantor":
        if (s.turn % 3 === 1) {
          damage = 0;
          target = e.uid;
          summon = ["thrall", "thrall"];
          label = "Raise 2 Bone Thralls";
        } else if (s.turn % 3 === 2) {
          label = "Death litany";
        } else {
          target = "all";
          damage = 5 + s.difficulty;
          label = "Grave tempest · all targets";
        }
        break;
      case "cindermaw":
        if (s.turn % 3 === 1) {
          damage = 0;
          target = e.uid;
          label = "Fold armored wings · gain 10 block";
        } else if (s.turn % 3 === 2) {
          target = "all";
          damage = 7 + s.difficulty;
          label = "Ashen breath · all targets";
        } else {
          damage += 4;
          label = "Crushing maw";
        }
        break;
    }
    e.intent = { target, damage, label, ...(summon ? { summon } : {}) };
  }
}
function beginBattle(s: GameState, kind: string, events?: ResolvedEvent[]) {
  s.phase = "battle";
  s.route = [kind];
  s.block = 0;
  s.energy =
    5 +
    (s.relics.includes("brass-bell") ? 1 : 0) +
    (s.relics.includes("grave-coin") ? 1 : 0);
  s.turn = 1;
  s.allies = [];
  s.hand = [];
  s.discard = [];
  s.draw = shuffle(s, s.deck);
  s.stats.battles++;
  s.stats.turns++;
  const boss = bossForSeed(s.seed);
  const sets =
    kind === "boss"
      ? [[boss]]
      : kind === "elite"
        ? [
            ["raider", "revenant", "acolyte"],
            ["brood", "acolyte"],
            ["raider", "raider", "revenant"],
            ["acolyte", "revenant", "revenant"],
          ]
        : s.floor <= 2
          ? [
              ["raider", "revenant"],
              ["raider", "thrall"],
            ]
          : [
              ["brood", "thrall"],
              ["raider", "revenant"],
              ["acolyte", "thrall"],
              ["revenant", "thrall", "thrall"],
            ];
  s.enemies = sets[Math.floor(random(s) * sets.length)].map((id) =>
    enemy(s, id),
  );
  for (const e of s.enemies)
    events?.push({
      type: "summon",
      source: "world",
      target: e.uid,
      cardId: e.cardId,
      unit: structuredClone(e),
      side: "enemy",
    });
  draw(s, 5);
  intentions(s);
  note(
    s,
    kind === "boss"
      ? "Final contract: " + ENEMIES[boss].name + "."
      : kind === "elite"
        ? "An elder contract waits in the ruins."
        : "The keep has teeth.",
  );
}
function hitUnit(
  s: GameState,
  u: Unit,
  damage: number,
  source: boolean,
  pierce = false,
  resolution?: ResolutionTrace,
) {
  const beforeHp = u.hp,
    blocked = pierce ? 0 : Math.min(u.block, damage);
  const dealt = Math.min(u.hp, Math.max(0, damage - (pierce ? 0 : u.block)));
  if (!pierce) u.block = Math.max(0, u.block - damage);
  u.hp -= dealt;
  if (source) s.stats.damageDealt += dealt;
  if (resolution) {
    const { events, ...from } = resolution;
    events.push({
      type: "hit",
      ...from,
      target: u.uid,
      damage,
      blocked,
      hpLost: dealt,
      beforeHp,
      afterHp: u.hp,
    });
    if (beforeHp > 0 && u.hp <= 0)
      events.push({
        type: "death",
        source: resolution.source,
        target: u.uid,
        cardId: u.cardId,
      });
  }
}
function hitHunter(
  s: GameState,
  damage: number,
  pierce = false,
  resolution?: ResolutionTrace,
) {
  const beforeHp = s.hp,
    blocked = pierce ? 0 : Math.min(s.block, damage);
  const dealt = Math.max(0, damage - (pierce ? 0 : s.block));
  if (!pierce) s.block = Math.max(0, s.block - damage);
  s.hp = Math.max(0, s.hp - dealt);
  if (resolution) {
    const { events, ...from } = resolution;
    events.push({
      type: "hit",
      ...from,
      target: "hunter",
      damage,
      blocked,
      hpLost: beforeHp - s.hp,
      beforeHp,
      afterHp: s.hp,
    });
    if (beforeHp > 0 && s.hp <= 0)
      events.push({
        type: "death",
        source: resolution.source,
        target: "hunter",
      });
  }
}
function heal(
  s: GameState,
  n: number,
  events?: ResolvedEvent[],
  source = "hunter",
) {
  const beforeHp = s.hp;
  s.hp = Math.min(s.maxHp, s.hp + n);
  if (s.hp > beforeHp)
    events?.push({
      type: "heal",
      source,
      target: "hunter",
      amount: s.hp - beforeHp,
      beforeHp,
      afterHp: s.hp,
    });
}
function healUnit(
  u: Unit,
  n: number,
  events?: ResolvedEvent[],
  source = "hunter",
) {
  const beforeHp = u.hp;
  u.hp = Math.min(u.maxHp, u.hp + n);
  if (u.hp > beforeHp)
    events?.push({
      type: "heal",
      source,
      target: u.uid,
      amount: u.hp - beforeHp,
      beforeHp,
      afterHp: u.hp,
    });
}
function ward(
  s: GameState,
  u: Unit | undefined,
  n: number,
  events?: ResolvedEvent[],
  source = "hunter",
) {
  if (u) u.block += n;
  else s.block += n;
  if (n > 0)
    events?.push({
      type: "ward",
      source,
      target: u?.uid ?? "hunter",
      amount: n,
    });
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
function finish(s: GameState, events?: ResolvedEvent[]) {
  clean(s);
  if (s.hp <= 0) {
    s.phase = "defeat";
    note(s, "The pact breaks. The ruins keep another name.");
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
  heal(
    s,
    (kind === "elite" ? 3 : 2) + (s.relics.includes("blood-vial") ? 2 : 0),
    events,
  );
  if (kind === "boss") {
    s.phase = "victory";
    s.route = [];
    note(
      s,
      "Contract fulfilled. You leave the ruins scarred, alive, and paid.",
    );
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
function targetedSpell(
  s: GameState,
  target: Unit,
  damage: number,
  resolution?: ResolutionTrace,
) {
  const widow = s.allies.filter((u) => u.species === "spider").length * 2;
  const relic = s.relics.includes("moon-charm") ? 1 : 0;
  const resistance = target.cardId === "revenant" ? 2 : 0;
  hitUnit(
    s,
    target,
    Math.max(0, damage + widow + relic - resistance),
    true,
    false,
    resolution,
  );
}
function play(
  s: GameState,
  a: Extract<Action, { type: "play" }>,
  events?: ResolvedEvent[],
) {
  const id = s.hand.splice(a.index, 1)[0],
    c = CARDS[id];
  s.energy -= c.cost;
  s.stats.cardsPlayed++;
  if (c.type === "summon") {
    const hpBonus = s.relics.includes("ember-seed") ? 2 : 0;
    const u: Unit = {
      uid: "a" + s.nextUid++,
      cardId: id,
      name: c.name,
      species: c.species!,
      hp: c.hp! + hpBonus,
      maxHp: c.hp! + hpBonus,
      attack: c.attack! + (s.relics.includes("war-brand") ? 1 : 0),
      block: 0,
      acted: false,
      color: c.color,
      passive: c.passive,
    };
    s.allies.push(u);
    events?.push({
      type: "summon",
      source: "hunter",
      target: u.uid,
      cardId: id,
      unit: structuredClone(u),
      side: "ally",
    });
    switch (c.effect) {
      case "hunter-ward":
        ward(s, undefined, 2, events, u.uid);
        break;
      case "draw":
        draw(s, 1);
        break;
      case "hunter-heal":
        heal(s, 2, events, u.uid);
        break;
      case "pack-ward":
        for (const a of s.allies) ward(s, a, 3, events, u.uid);
        break;
      case "enemy-burn":
        for (const e of s.enemies)
          hitUnit(s, e, 2, true, false, trace(events, u.uid, "summon", id));
        break;
    }
    note(s, "Bound " + c.name + ".");
  } else {
    const v = c.value ?? 0,
      target = s.enemies.find((e) => e.uid === a.target),
      ally = s.allies.find((u) => u.uid === a.target);
    const spellTrace = trace(events, "hunter", "spell", id);
    switch (c.effect) {
      case "damage":
        targetedSpell(s, target!, v, spellTrace);
        break;
      case "block":
        ward(s, undefined, v, events);
        break;
      case "heal":
        healUnit(ally!, v, events);
        ward(s, ally!, 2, events);
        break;
      case "rally":
        for (const u of s.allies) {
          const before = u.attack;
          u.attack += v;
          if (u.attack !== before)
            events?.push({
              type: "buff",
              source: "hunter",
              target: u.uid,
              cardId: id,
              stat: "attack",
              before,
              after: u.attack,
              amount: u.attack - before,
            });
        }
        break;
      case "aoe":
        for (const e of s.enemies)
          hitUnit(
            s,
            e,
            v + (s.relics.includes("moon-charm") ? 1 : 0),
            true,
            false,
            spellTrace,
          );
        break;
      case "ready":
        ally!.acted = false;
        ward(s, ally!, v, events);
        break;
      case "siphon":
        targetedSpell(s, target!, v, spellTrace);
        heal(s, 3, events);
        break;
      case "draw":
        draw(s, v);
        break;
      case "energy":
        s.energy += v;
        hitHunter(s, 3, true, trace(events, "hunter", "self", id));
        break;
      case "shelter":
        ward(s, undefined, v, events);
        for (const u of s.allies) ward(s, u, v, events);
        break;
      case "pack":
        targetedSpell(s, target!, v + s.allies.length * 2, spellTrace);
        break;
      case "communion":
        heal(s, v * s.allies.length, events);
        break;
      case "shred":
        target!.block = 0;
        targetedSpell(s, target!, v, spellTrace);
        break;
      case "control":
        const beforeIntent = structuredClone(target!.intent!);
        target!.intent = {
          ...target!.intent!,
          damage: 0,
          label: target!.intent!.label.includes("block")
            ? target!.intent!.label + " · silenced (armor remains)"
            : "Silenced · damage and reinforcements canceled",
          summon: [],
        };
        if (JSON.stringify(beforeIntent) !== JSON.stringify(target!.intent))
          events?.push({
            type: "control",
            source: "hunter",
            target: target!.uid,
            cardId: id,
            before: beforeIntent,
            after: structuredClone(target!.intent),
          });
        break;
      case "solo":
        targetedSpell(
          s,
          target!,
          v + (s.allies.length === 0 ? 4 : 0),
          spellTrace,
        );
        break;
      case "hunterheal":
        heal(s, v, events);
        break;
    }
    s.discard.push(id);
    note(s, "Cast " + c.name + ".");
  }
  finish(s, events);
}
function endTurn(s: GameState, events?: ResolvedEvent[]) {
  // A fixed roster snapshot prevents newly raised thralls acting before their
  // first visible intent. Reinforcements appear only after this enemy phase.
  for (const e of s.enemies) e.block = 0;
  const reinforcements: { id: string; source: string }[] = [];
  for (const e of s.enemies.slice()) {
    const i = e.intent!;
    if (i.summon?.length)
      reinforcements.push(...i.summon.map((id) => ({ id, source: e.uid })));
    const enemyTrace = trace(events, e.uid, "enemy", e.cardId);
    if (i.damage === 0) {
      // Only an actual guard phase grants armor. A canceled attack cannot
      // become an accidental guard, and canceling a guard preserves armor.
      if (e.cardId === "ironjaw" && s.turn % 2 === 1)
        ward(s, e, 14, events, e.uid);
      else if (e.cardId === "cindermaw" && s.turn % 3 === 1)
        ward(s, e, 10, events, e.uid);
      else if (e.cardId === "raider" && s.turn % 2 === 1)
        ward(s, e, 4, events, e.uid);
    } else if (i.target === "all") {
      hitHunter(s, i.damage, false, enemyTrace);
      for (const u of s.allies)
        hitUnit(s, u, i.damage, false, false, enemyTrace);
    } else {
      const u = s.allies.find((u) => u.uid === i.target && u.hp > 0);
      if (u)
        hitUnit(s, u, i.damage, false, e.cardId === "revenant", enemyTrace);
      else hitHunter(s, i.damage, e.cardId === "revenant", enemyTrace);
    }
    note(s, e.name + ": " + i.label + ".");
    clean(s);
    if (s.hp <= 0) break;
  }
  if (s.hp > 0)
    for (const raisedPlan of reinforcements)
      if (s.enemies.length < 6) {
        const raised = enemy(s, raisedPlan.id);
        s.enemies.push(raised);
        events?.push({
          type: "summon",
          source: raisedPlan.source,
          target: raised.uid,
          cardId: raised.cardId,
          unit: structuredClone(raised),
          side: "enemy",
        });
        note(s, raised.name + " rises. It will act next turn.");
      }
  finish(s, events);
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
  s.energy =
    5 + (s.relics.includes("grave-coin") && s.allies.length === 0 ? 1 : 0);
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
      ...s.deck.flatMap((id, index) =>
        id.endsWith("+")
          ? []
          : [{ type: "camp" as const, choice: "train" as const, index }],
      ),
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
      ...(s.hp > 4 && s.deck.length > 5 && s.deck.includes("scour")
        ? [{ type: "event" as const, choice: "purge" }]
        : []),
      ...(s.gold >= 30 && s.hp < s.maxHp
        ? [{ type: "event" as const, choice: "bargain" }]
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
    case "camp":
      return a.type === "camp" && a.choice === b.choice && a.index === b.index;
    case "travel":
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
function reduceAction(
  state: GameState,
  action: Action,
  events?: ResolvedEvent[],
): GameState {
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
        beginBattle(s, action.choice, events);
      else {
        s.phase = action.choice as "camp" | "shop" | "event";
        s.route = [action.choice];
        if (action.choice === "shop")
          s.rewards = shuffle(s, BASE_CARD_IDS).slice(0, 5);
        note(s, "Reached the " + action.choice + ".");
      }
      break;
    case "play":
      play(s, action, events);
      break;
    case "attack": {
      const u = s.allies.find((u) => u.uid === action.unit)!,
        e = s.enemies.find((e) => e.uid === action.target)!;
      u.acted = true;
      const wasArmored = e.block > 0;
      const hp = e.hp;
      hitUnit(
        s,
        e,
        u.attack + (u.species === "hound" && !wasArmored ? 2 : 0),
        true,
        false,
        trace(events, u.uid, "command", u.cardId),
      );
      if (u.species === "stalker" && e.hp < hp) healUnit(u, 2, events, u.uid);
      if (u.species === "colossus") ward(s, undefined, 2, events, u.uid);
      if (wasArmored && (e.cardId === "raider" || e.cardId === "ironjaw")) {
        hitUnit(
          s,
          u,
          e.cardId === "ironjaw" ? 2 : 1,
          false,
          true,
          trace(events, e.uid, "retaliation", e.cardId),
        );
        note(s, e.name + " retaliates against " + u.name + ".");
      }
      note(s, u.name + " strikes " + e.name + ".");
      finish(s, events);
      break;
    }
    case "endTurn":
      endTurn(s, events);
      break;
    case "reward":
      if (action.card) s.deck.push(action.card);
      map(s);
      break;
    case "camp":
      if (action.choice === "rest") {
        heal(s, 18, events);
        note(s, "Restored 18 HP beside the contract fire.");
      } else {
        const id = s.deck[action.index!];
        s.deck[action.index!] = id + "+";
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
        hitHunter(s, 8, true, trace(events, "hunter", "self"));
        s.relics.push("moon-charm");
        note(s, "The wraithglass oath is sealed in blood.");
      } else if (action.choice === "purge") {
        hitHunter(s, 4, true, trace(events, "hunter", "self"));
        s.deck.splice(s.deck.indexOf("scour"), 1);
        note(s, "An old Scour contract burns.");
      } else if (action.choice === "bargain") {
        s.gold -= 30;
        heal(s, 16, events);
        note(s, "The surgeon closes your wounds.");
      } else if (action.choice === "forage") {
        s.gold += 25;
        note(s, "Found 25 gold beneath the roots.");
      }
      map(s);
      break;
  }
  return s;
}
/** Existing reducer API: same state and random sequence as the archived rules. */
export function applyAction(state: GameState, action: Action): GameState {
  return reduceAction(state, action);
}
/** Resolution observations are transient and independent of returned saved state. */
export function applyActionWithEvents(
  state: GameState,
  action: Action,
): { state: GameState; events: ResolvedEvent[] } {
  const events: ResolvedEvent[] = [];
  return { state: reduceAction(state, action, events), events };
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
      s.schema !== 2 ||
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
      !strings(s.relics, 6) ||
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
        if (u.passive !== def.passive) return false;
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
            i.label.length > 100 ||
            (i.summon !== undefined &&
              (!strings(
                i.summon,
                u.cardId === "cantor" ? 2 : u.cardId === "acolyte" ? 1 : 0,
              ) ||
                i.summon.some((id) => id !== "thrall") ||
                i.damage !== 0))
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
