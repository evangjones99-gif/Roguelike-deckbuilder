import test from "node:test";
import assert from "node:assert/strict";
import {
  applyAction,
  createGame,
  legalActions,
  validateState,
  CARDS,
  cardTarget,
  type GameState,
  type Unit,
} from "../src/engine";
import {
  ENEMIES,
  SHOP_PRICES,
  BASE_CARD_IDS,
  RELICS,
  BOSS_IDS,
  bossForSeed,
} from "../src/content";
import { chooseHeuristic, run } from "../scripts/simulate";
const FIVE = ["cairnhound", "scour", "ironward", "sutures", "sunder"];
function battle(cards = FIVE, seed = 1): GameState {
  const s = createGame(seed);
  s.deck = cards.slice();
  return applyAction(s, { type: "travel", choice: "battle" });
}
function hand(s: GameState, ids: string[]) {
  s.deck = ids.slice();
  s.hand = ids.slice();
  s.draw = [];
  s.discard = [];
  s.allies = [];
}
function foe(s: GameState, id: string, hp?: number): Unit {
  const d = ENEMIES[id];
  return {
    uid: "e" + s.nextUid++,
    cardId: id,
    ...d,
    hp: hp ?? d.hp,
    maxHp: hp ?? d.hp,
    block: 0,
    acted: false,
    intent: { damage: d.attack, target: "hunter", label: "Strike" },
  };
}
function ally(s: GameState, id = "cairnhound"): Unit {
  const c = CARDS[id];
  const u = {
    uid: "a" + s.nextUid++,
    cardId: id,
    name: c.name,
    species: c.species!,
    color: c.color,
    passive: c.passive,
    hp: c.hp!,
    maxHp: c.hp!,
    attack: c.attack!,
    block: 0,
    acted: false,
  };
  s.allies.push(u);
  s.deck.push(id);
  return u;
}
function play(s: GameState, id: string, target?: string) {
  return applyAction(s, {
    type: "play",
    index: s.hand.indexOf(id),
    ...(target ? { target } : {}),
  });
}
function command(s: GameState, unit: Unit, target: Unit) {
  return applyAction(s, { type: "attack", unit: unit.uid, target: target.uid });
}
function enter(node: number, choice: string, seed = 1) {
  const s = createGame(seed);
  s.floor = node - 1;
  s.route = [choice];
  return applyAction(s, { type: "travel", choice });
}
function settle(s: GameState) {
  for (let i = 0; i < 500 && s.phase === "battle"; i++)
    s = applyAction(s, chooseHeuristic(s));
  assert.notEqual(s.phase, "battle");
  return s;
}

test("24 original cards, four creature families and enhancement texts are complete", () => {
  assert.equal(BASE_CARD_IDS.length, 24);
  assert.equal(Object.keys(CARDS).length, 48);
  const families = new Set<string>();
  for (const id of BASE_CARD_IDS) {
    const c = CARDS[id],
      u = CARDS[id + "+"];
    assert.equal(c.id, id);
    assert.equal(u.id, id + "+");
    assert.equal(u.type, c.type);
    assert.ok(c.text && u.text);
    if (c.type === "summon") {
      families.add(c.species!);
      assert.ok(c.passive);
      assert.equal(u.hp, c.hp! + 3);
      assert.equal(u.attack, c.attack! + 1);
    } else assert.ok(c.effect);
  }
  assert.deepEqual([...families], ["hound", "stalker", "colossus", "spider"]);
  assert.equal(CARDS["silence+"].cost, 1);
  assert.equal(cardTarget("silence"), "enemy");
  assert.equal(cardTarget("sunder"), "enemy");
  assert.equal(cardTarget("sutures"), "ally");
});

test("schema 2 saves reject historical schema, presentation menu and malformed inputs", () => {
  const s = createGame(77, 0, { engineKind: 1 });
  assert.equal(s.schema, 2);
  assert.ok(validateState(s));
  assert.equal(validateState({ ...s, schema: 1 }), false);
  assert.equal(validateState({ ...s, phase: "menu" }), false);
  for (const bad of [null, undefined, {}, [], 1, "save", true, new Date()])
    assert.equal(validateState(bad), false);
  assert.equal(
    validateState(
      new Proxy(
        {},
        {
          get() {
            throw Error("hostile");
          },
        },
      ),
    ),
    false,
  );
});

test("serialized action replay is exact, pure, and deterministic through terminal state", () => {
  let a = createGame(718),
    b = createGame(718);
  for (let i = 0; i < 700 && legalActions(a).length; i++) {
    const action = chooseHeuristic(a),
      before = JSON.stringify(a);
    const next = applyAction(a, action);
    assert.equal(JSON.stringify(a), before);
    a = next;
    b = applyAction(JSON.parse(JSON.stringify(b)), action);
    assert.deepEqual(a, b);
    assert.ok(validateState(a));
  }
  assert.equal(a.phase, "victory");
  assert.deepEqual(run(718, "heuristic"), run(718, "heuristic"));
});

test("invalid indices, targets, phase, budget and board size return original object", () => {
  const s = battle();
  assert.equal(applyAction(s, { type: "play", index: -1 }), s);
  assert.equal(
    applyAction(s, { type: "play", index: s.hand.indexOf("scour") }),
    s,
  );
  assert.equal(
    applyAction(s, {
      type: "play",
      index: s.hand.indexOf("scour"),
      target: "hunter",
    }),
    s,
  );
  assert.equal(applyAction(s, { type: "travel", choice: "boss" }), s);
  assert.equal(
    applyAction(s, {
      type: "attack",
      unit: "missing",
      target: s.enemies[0].uid,
    }),
    s,
  );
  s.energy = 0;
  assert.equal(play(s, "cairnhound"), s);
  s.energy = 5;
  for (let i = 0; i < 6; i++) ally(s);
  assert.equal(play(s, "cairnhound"), s);
});

test("living creatures own one card copy outside piles; dead creatures rejoin discard", () => {
  let s = battle();
  s = play(s, "cairnhound");
  assert.equal(s.allies[0].acted, false);
  assert.equal(
    [...s.hand, ...s.draw, ...s.discard].includes("cairnhound"),
    false,
  );
  assert.ok(validateState(s));
  const u = s.allies[0];
  s.enemies = [foe(s, "thrall", 200)];
  s.enemies[0].intent = { damage: 0, target: "hunter", label: "Canceled" };
  for (let i = 0; i < 4; i++) {
    s = applyAction(s, { type: "endTurn" });
    assert.equal(
      [...s.hand, ...s.draw, ...s.discard].includes("cairnhound"),
      false,
    );
    assert.ok(validateState(s));
    s.enemies[0].intent = { damage: 0, target: "hunter", label: "Canceled" };
  }
  s.allies[0].hp = 1;
  s.enemies[0].intent = { damage: 99, target: u.uid, label: "Claw" };
  s = applyAction(s, { type: "endTurn" });
  assert.equal(s.allies.length, 0);
  assert.equal(
    [...s.hand, ...s.draw, ...s.discard].filter((id) => id === "cairnhound")
      .length,
    1,
  );
  assert.ok(validateState(s));
});

test("two identical source copies remain separate when one dies", () => {
  let s = battle(["cairnhound", "cairnhound", "scour", "ironward", "survey"]);
  s = play(s, "cairnhound");
  s = play(s, "cairnhound");
  assert.equal(s.allies.length, 2);
  const dead = s.allies[0].uid;
  s.allies[0].hp = 1;
  s.enemies = [foe(s, "thrall")];
  s.enemies[0].intent = { damage: 99, target: dead, label: "Claw" };
  s = applyAction(s, { type: "endTurn" });
  assert.equal(s.allies.length, 1);
  assert.equal(
    [...s.hand, ...s.draw, ...s.discard].filter((id) => id === "cairnhound")
      .length,
    1,
  );
  assert.ok(validateState(s));
});

test("Cairn Hound executes exposed targets but does not receive bonus against armor", () => {
  let s = battle();
  s = play(s, "cairnhound");
  s.enemies = [foe(s, "cindermaw", 100)];
  const u = s.allies[0],
    e = s.enemies[0];
  s = command(s, u, e);
  assert.equal(s.enemies[0].hp, 95);
  s.allies[0].acted = false;
  s.enemies[0].block = 2;
  s = command(s, s.allies[0], s.enemies[0]);
  assert.equal(s.enemies[0].hp, 94);
  assert.equal(s.enemies[0].block, 0);
});

test("Fen Stalker heals only when its command deals health damage", () => {
  let s = battle();
  hand(s, ["fenstalker", "scour", "ironward", "sutures", "sunder"]);
  s = play(s, "fenstalker");
  s.allies[0].hp = 4;
  s.enemies = [foe(s, "cindermaw", 100)];
  s.enemies[0].block = 10;
  s = command(s, s.allies[0], s.enemies[0]);
  assert.equal(s.allies[0].hp, 4);
  s.allies[0].acted = false;
  s.enemies[0].block = 0;
  s = command(s, s.allies[0], s.enemies[0]);
  assert.equal(s.allies[0].hp, 6);
});

test("Briar Colossus grants hunter block after every command, even into armor", () => {
  let s = battle();
  hand(s, ["briarcolossus", "scour", "ironward", "sutures", "sunder"]);
  s = play(s, "briarcolossus");
  s.enemies = [foe(s, "cindermaw", 100)];
  s.enemies[0].block = 20;
  s = command(s, s.allies[0], s.enemies[0]);
  assert.equal(s.block, 2);
  assert.equal(s.enemies[0].hp, 100);
});

test("Ash Widow amplifies targeted damage, relic combines, Revenant resists it", () => {
  let s = battle();
  hand(s, ["ashwidow", "scour", "witchfire", "ironward", "sunder"]);
  s.energy = 10;
  s.relics = ["moon-charm"];
  s.enemies = [foe(s, "revenant", 100), foe(s, "thrall", 100)];
  s = play(s, "ashwidow");
  s = play(s, "scour", s.enemies[0].uid);
  assert.equal(s.enemies[0].hp, 93);
  s = play(s, "witchfire");
  assert.equal(s.enemies[0].hp, 88);
  assert.equal(s.enemies[1].hp, 95);
  assert.ok(validateState(s));
});

test("Grave Resonance supports a spell-only opening and loses solo bonus after binding", () => {
  let s = battle();
  hand(s, ["resonance", "resonance", "cairnhound", "ironward", "sunder"]);
  s.energy = 10;
  s.enemies = [foe(s, "cantor", 100)];
  s = play(s, "resonance", s.enemies[0].uid);
  assert.equal(s.enemies[0].hp, 86);
  s = play(s, "cairnhound");
  s = play(s, "resonance", s.enemies[0].uid);
  assert.equal(s.enemies[0].hp, 76);
});

test("ready permits a second command while ordinary commands are once per turn", () => {
  let s = battle();
  hand(s, ["cairnhound", "killcommand", "scour", "ironward", "sunder"]);
  s.enemies = [foe(s, "cindermaw", 100)];
  s = play(s, "cairnhound");
  s = command(s, s.allies[0], s.enemies[0]);
  assert.equal(command(s, s.allies[0], s.enemies[0]), s);
  s = play(s, "killcommand", s.allies[0].uid);
  s = command(s, s.allies[0], s.enemies[0]);
  assert.equal(s.enemies[0].hp, 90);
});

test("Ironjaw armor retaliates through creature block; Sundering Hex prevents retaliation", () => {
  let s = battle();
  s = play(s, "cairnhound");
  s.enemies = [foe(s, "ironjaw", 100)];
  s.enemies[0].block = 14;
  s.allies[0].block = 20;
  const hp = s.allies[0].hp;
  s = command(s, s.allies[0], s.enemies[0]);
  assert.equal(s.allies[0].hp, hp - 2);
  assert.equal(s.enemies[0].block, 11);
  s = play(s, "sunder", s.enemies[0].uid);
  assert.equal(s.enemies[0].block, 0);
  assert.equal(s.enemies[0].hp, 97);
  s.allies[0].acted = false;
  s = command(s, s.allies[0], s.enemies[0]);
  assert.equal(s.allies[0].hp, hp - 2);
  assert.equal(s.enemies[0].hp, 92);
  assert.ok(validateState(s));
});

test("retaliation deaths return exactly one source card and no duplicate draws", () => {
  let s = battle();
  s = play(s, "cairnhound");
  s.allies[0].hp = 2;
  s.enemies = [foe(s, "ironjaw", 100)];
  s.enemies[0].block = 14;
  s = command(s, s.allies[0], s.enemies[0]);
  assert.equal(s.allies.length, 0);
  assert.equal(s.discard.filter((id) => id === "cairnhound").length, 1);
  assert.ok(validateState(s));
});

test("announced targets stay stable across bindings and commands; missing creature falls back to hunter", () => {
  let s = battle();
  const before = structuredClone(s.enemies.map((e) => e.intent));
  s = play(s, "cairnhound");
  assert.deepEqual(
    s.enemies.map((e) => e.intent),
    before,
  );
  s.enemies = [foe(s, "thrall"), foe(s, "thrall")];
  const u = s.allies[0];
  u.hp = 1;
  for (const e of s.enemies)
    e.intent = { damage: 5, target: u.uid, label: "Claw" };
  s.block = 0;
  const hp = s.hp;
  s = applyAction(s, { type: "endTurn" });
  assert.equal(s.hp, hp - 5);
  assert.equal(s.allies.length, 0);
  assert.ok(validateState(s));
});

test("Revenant strikes ignore hunter armor and have explicit visible text", () => {
  let s = battle();
  s.enemies = [foe(s, "revenant")];
  s.block = 30;
  const hp = s.hp;
  s = applyAction(s, { type: "endTurn" });
  assert.equal(s.hp, hp - 5);
  assert.ok(s.enemies[0].intent!.label.includes("ignores block"));
});

test("Cantor raises announced thralls after enemy resolution; no hidden immediate attacks", () => {
  let s = enter(10, "boss", 1);
  assert.equal(s.enemies[0].cardId, "cantor");
  assert.deepEqual(s.enemies[0].intent!.summon, ["thrall", "thrall"]);
  const hp = s.hp;
  s = applyAction(s, { type: "endTurn" });
  assert.equal(s.hp, hp);
  assert.equal(s.enemies.length, 3);
  assert.ok(
    s.enemies
      .slice(1)
      .every((e) => e.cardId === "thrall" && e.intent!.damage > 0),
  );
  assert.equal(s.enemies[0].intent!.label, "Death litany");
  assert.ok(validateState(s));
});

test("reinforcements respect six slots and cannot carry an unannounced extra enemy", () => {
  let s = enter(10, "boss", 1);
  for (let i = 0; i < 4; i++) {
    const e = foe(s, "thrall");
    e.intent = { damage: 0, target: "hunter", label: "Canceled" };
    s.enemies.push(e);
  }
  s = applyAction(s, { type: "endTurn" });
  assert.equal(s.enemies.length, 6);
  assert.equal(s.enemies.filter((e) => e.cardId === "thrall").length, 5);
  assert.ok(validateState(s));
});

test("Silence cancels necromancy; canceled attacks do not become armor; guard remains guard", () => {
  let s = enter(10, "boss", 1);
  hand(s, ["silence", "scour", "ironward", "sutures", "sunder"]);
  s = play(s, "silence", s.enemies[0].uid);
  assert.deepEqual(s.enemies[0].intent!.summon, []);
  assert.ok(validateState(s));
  s = applyAction(s, { type: "endTurn" });
  assert.equal(s.enemies.length, 1);
  assert.equal(s.enemies[0].block, 0);
  s = play(s, "silence", s.enemies[0].uid);
  assert.ok(validateState(s));
  const hp = s.hp;
  s = applyAction(s, { type: "endTurn" });
  assert.equal(s.hp, hp);
  assert.equal(s.enemies[0].block, 0);
  let guarded = enter(10, "boss", 0);
  hand(guarded, ["silence", "scour", "ironward", "sutures", "sunder"]);
  guarded = play(guarded, "silence", guarded.enemies[0].uid);
  assert.ok(guarded.enemies[0].intent!.label.includes("armor remains"));
  guarded = applyAction(guarded, { type: "endTurn" });
  assert.equal(guarded.enemies[0].block, 14);
  assert.ok(validateState(guarded));
});

test("killing the raising source before ending the turn prevents its reinforcements", () => {
  let s = enter(6, "battle");
  s.enemies = [foe(s, "acolyte", 1), foe(s, "thrall", 100)];
  s.enemies[0].intent = {
    damage: 0,
    target: s.enemies[0].uid,
    label: "Raise 1 Bone Thrall",
    summon: ["thrall"],
  };
  hand(s, ["scour", "ironward", "ironward", "sunder", "survey"]);
  s = play(s, "scour", s.enemies[0].uid);
  s = applyAction(s, { type: "endTurn" });
  assert.equal(s.enemies.length, 1);
  assert.equal(s.enemies[0].cardId, "thrall");
  assert.ok(validateState(s));
});

test("Cindermaw guard/breath/strike cycle has readable damage windows and expires armor", () => {
  let s = enter(10, "boss", 2);
  assert.equal(s.enemies[0].cardId, "cindermaw");
  assert.equal(s.enemies[0].intent!.damage, 0);
  s = applyAction(s, { type: "endTurn" });
  assert.equal(s.enemies[0].block, 10);
  assert.equal(s.enemies[0].intent!.target, "all");
  assert.equal(s.enemies[0].intent!.damage, 7);
  s = applyAction(s, { type: "endTurn" });
  assert.equal(s.enemies[0].block, 0);
  assert.equal(s.enemies[0].intent!.target, "hunter");
  assert.equal(s.enemies[0].intent!.damage, s.enemies[0].attack + 4);
  s = applyAction(s, { type: "endTurn" });
  assert.equal(s.enemies[0].intent!.damage, 0);
});

test("boss is forecastable from run seed independently of earlier RNG consumption", () => {
  assert.equal(BOSS_IDS.length, 3);
  for (let seed = 0; seed < 12; seed++) {
    const expected = bossForSeed(seed);
    const s = createGame(seed);
    s.floor = 9;
    s.route = ["boss"];
    s.rng = (s.rng + 91501) >>> 0;
    const entered = applyAction(s, { type: "travel", choice: "boss" });
    assert.equal(entered.enemies[0].cardId, expected);
    assert.ok(validateState(entered));
  }
});

test("elite formations offer four distinct questions and never guarantee all six relics", () => {
  const found = new Set<string>();
  for (let seed = 1; seed <= 100; seed++) {
    const s = enter(4, "elite", seed);
    found.add(s.enemies.map((e) => e.cardId).join(","));
    assert.ok(validateState(s));
  }
  assert.equal(found.size, 4);
  assert.equal(Object.keys(RELICS).length, 6);
  let s = createGame(27);
  for (let i = 0; i < 1000 && legalActions(s).length; i++) {
    const acts = legalActions(s);
    const action =
      s.phase === "map"
        ? (acts.find((a) => a.type === "travel" && a.choice === "elite") ??
          chooseHeuristic(s))
        : chooseHeuristic(s);
    s = applyAction(s, action);
    assert.ok(validateState(s));
  }
  assert.ok(s.relics.length < 6);
});

test("targeted camp upgrade changes precisely the selected duplicate entry", () => {
  let s = enter(3, "camp");
  const ids = s.deck.slice(),
    target = ids.indexOf("sunder");
  const train = legalActions(s).filter(
    (a) => a.type === "camp" && a.choice === "train",
  );
  assert.equal(train.length, ids.length);
  assert.equal(applyAction(s, { type: "camp", choice: "train" }), s);
  assert.equal(applyAction(s, { type: "camp", choice: "train", index: -1 }), s);
  s = applyAction(s, { type: "camp", choice: "train", index: target });
  assert.deepEqual(
    s.deck,
    ids.map((id, i) => (i === target ? id + "+" : id)),
  );
  assert.ok(validateState(s));
  let duplicated = enter(3, "camp");
  duplicated = applyAction(duplicated, {
    type: "camp",
    choice: "train",
    index: 1,
  });
  assert.equal(duplicated.deck[0], "cairnhound");
  assert.equal(duplicated.deck[1], "cairnhound+");
  assert.equal(duplicated.phase, "map");
});

test("relic effects support summon endurance, command attack, solo economy and recovery", () => {
  let s = battle();
  s.relics = ["ember-seed", "war-brand"];
  s = play(s, "cairnhound");
  assert.equal(s.allies[0].maxHp, 9);
  assert.equal(s.allies[0].attack, 4);
  let solo = enter(10, "boss", 1);
  solo.relics = ["grave-coin"];
  solo = applyAction(solo, { type: "endTurn" });
  assert.equal(solo.energy, 6);
  solo = play(solo, "cairnhound");
  solo.enemies.forEach(
    (e) => (e.intent = { damage: 0, target: "hunter", label: "Canceled" }),
  );
  solo = applyAction(solo, { type: "endTurn" });
  assert.equal(solo.energy, 5);
  const opener = createGame(10);
  opener.relics = ["brass-bell", "grave-coin"];
  const opened = applyAction(opener, { type: "travel", choice: "battle" });
  assert.equal(opened.energy, 7);
  let recovery = battle();
  recovery.hp = 30;
  recovery.relics = ["blood-vial"];
  recovery.enemies = [foe(recovery, "thrall", 1)];
  recovery = play(recovery, "scour", recovery.enemies[0].uid);
  assert.equal(recovery.hp, 34);
});

test("rewards, real shop costs and removals cannot be collected twice", () => {
  let s = settle(battle());
  assert.equal(s.phase, "reward");
  assert.equal(s.gold, 90);
  assert.equal(s.rewards.length, 3);
  assert.equal(new Set(s.rewards).size, 3);
  const card = s.rewards[0],
    len = s.deck.length;
  s = applyAction(s, { type: "reward", card });
  assert.equal(s.deck.length, len + 1);
  assert.equal(applyAction(s, { type: "reward", card }), s);
  let shop = enter(3, "shop");
  const item = shop.rewards[0],
    gold = shop.gold;
  shop = applyAction(shop, { type: "buy", card: item });
  assert.equal(shop.gold, gold - SHOP_PRICES[CARDS[item].type]);
  assert.equal(applyAction(shop, { type: "buy", card: item }), shop);
  shop.gold = 35;
  const size = shop.deck.length;
  shop = applyAction(shop, { type: "remove", index: 0 });
  assert.equal(shop.gold, 0);
  assert.equal(shop.deck.length, size - 1);
  assert.equal(applyAction(shop, { type: "remove", index: 0 }), shop);
  shop = applyAction(shop, { type: "leave" });
  assert.equal(shop.floor, 3);
  assert.ok(validateState(shop));
});

test("crypt events provide paid recovery, card purge or bounded relic oath", () => {
  let s = enter(5, "event");
  s.hp = 40;
  const gold = s.gold;
  s = applyAction(s, { type: "event", choice: "bargain" });
  assert.equal(s.hp, 56);
  assert.equal(s.gold, gold - 30);
  assert.ok(validateState(s));
  let purge = enter(5, "event");
  const len = purge.deck.length,
    hp = purge.hp;
  purge = applyAction(purge, { type: "event", choice: "purge" });
  assert.equal(purge.deck.length, len - 1);
  assert.equal(purge.deck.filter((id) => id === "scour").length, 1);
  assert.equal(purge.hp, hp - 4);
  assert.ok(validateState(purge));
  let oath = enter(5, "event");
  oath.hp = 8;
  assert.equal(applyAction(oath, { type: "event", choice: "offering" }), oath);
  oath.hp = 30;
  oath = applyAction(oath, { type: "event", choice: "offering" });
  assert.equal(oath.hp, 22);
  assert.deepEqual(oath.relics, ["moon-charm"]);
  assert.ok(validateState(oath));
});

test("temporary attack bonuses reset between contracts while permanent deck and HP persist", () => {
  let s = battle();
  hand(s, ["cairnhound", "edict", "scour", "ironward", "sunder"]);
  s = play(s, "cairnhound");
  s = play(s, "edict");
  assert.equal(s.allies[0].attack, 5);
  s = settle(s);
  const deck = s.deck.slice();
  assert.equal(s.allies.length, 0);
  s = applyAction(s, { type: "reward", card: null });
  const hp = s.hp;
  s = applyAction(s, { type: "travel", choice: "battle" });
  assert.equal(s.hp, hp);
  assert.deepEqual(s.deck, deck);
  assert.equal(s.turn, 1);
  s = play(s, "cairnhound");
  assert.equal(s.allies[0].attack, 3);
  assert.ok(validateState(s));
});

test("hunter self-damage defeat is immediate and terminal; terminal turn is counted", () => {
  let s = battle();
  hand(s, ["bloodprice", "scour", "ironward", "sutures", "sunder"]);
  s.hp = 3;
  s = play(s, "bloodprice");
  assert.equal(s.phase, "defeat");
  assert.equal(s.hp, 0);
  assert.equal(s.stats.turns, 1);
  assert.equal(legalActions(s).length, 0);
  assert.equal(applyAction(s, { type: "endTurn" }), s);
  assert.ok(validateState(s));
});

test("all three boss contracts can finish in a valid terminal collection state", () => {
  for (const seed of [42, 43, 44]) {
    let s = createGame(seed);
    for (let i = 0; i < 1000 && legalActions(s).length; i++) {
      s = applyAction(s, chooseHeuristic(s));
      assert.ok(validateState(s));
    }
    assert.equal(s.phase, "victory");
    assert.equal(s.floor, 10);
    assert.equal(s.enemies.length, 0);
    assert.equal(s.allies.length, 0);
    assert.equal(legalActions(s).length, 0);
    assert.ok(s.stats.turns >= s.stats.battles);
  }
});

test("save validation rejects prototype identities, forged passives and illegal reinforcement fields", () => {
  const s = battle();
  for (const [field, value] of [
    ["rng", 0],
    ["gold", NaN],
    ["hp", Infinity],
    ["hp", -1],
    ["maxHp", 0],
    ["energy", 0.5],
    ["floor", 11],
    ["difficulty", 3],
    ["deck", ["__proto__"]],
    ["route", ["fake"]],
    ["stats", null],
    ["allies", [null]],
    ["hand", ["scour", "scour", "scour", "scour", "scour"]],
  ] as [string, unknown][]) {
    const bad = structuredClone(s);
    (bad as unknown as Record<string, unknown>)[field] = value;
    assert.equal(validateState(bad), false, field);
  }
  const duplicate = structuredClone(s);
  duplicate.enemies[1].uid = duplicate.enemies[0].uid;
  assert.equal(validateState(duplicate), false);
  const prototype = structuredClone(s);
  prototype.enemies[0].cardId = "constructor";
  assert.equal(validateState(prototype), false);
  const passive = structuredClone(s);
  passive.enemies[0].passive = "No actual rule.";
  assert.equal(validateState(passive), false);
  const reinforce = structuredClone(s);
  reinforce.enemies[0].intent!.summon = ["thrall"];
  assert.equal(validateState(reinforce), false);
  const cantor = enter(10, "boss", 1);
  cantor.enemies[0].intent!.summon = ["constructor"];
  assert.equal(validateState(cantor), false);
  cantor.enemies[0].intent!.summon = ["thrall", "thrall", "thrall"];
  assert.equal(validateState(cantor), false);
  assert.ok(validateState(JSON.parse(JSON.stringify(s))));
});

test("every encounter must match its actual node; final combat allows only boss", () => {
  const choices = [
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
  for (let i = 0; i < choices.length; i++)
    for (const choice of choices[i]) {
      const entered = enter(i + 1, choice, 101);
      assert.ok(validateState(entered));
      for (let floor = 1; floor <= 10; floor++) {
        const moved = structuredClone(entered);
        moved.floor = floor;
        assert.equal(
          validateState(moved),
          choices[floor - 1].includes(choice),
          `${floor} ${choice}`,
        );
      }
    }
  const forged = battle();
  forged.floor = 10;
  forged.enemies = [foe(forged, "thrall", 1)];
  assert.equal(validateState(forged), false);
  const invalidReward = play(forged, "scour", forged.enemies[0].uid);
  assert.equal(invalidReward.phase, "reward");
  assert.equal(validateState(invalidReward), false);
});

test("300 seeded legal-random runs validate every intermediate state across difficulties", () => {
  for (let difficulty = 0; difficulty <= 2; difficulty++)
    for (let seed = 1; seed <= 100; seed++) {
      const result = run(seed, "random", difficulty);
      assert.ok(["victory", "defeat"].includes(result.phase));
      assert.ok(result.steps < 3000);
    }
});
