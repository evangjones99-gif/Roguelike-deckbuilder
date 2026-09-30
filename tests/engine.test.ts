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
  type Action,
} from "../src/engine";
import { ENEMIES, SHOP_PRICES, BASE_CARD_IDS } from "../src/content";
import { chooseHeuristic, run } from "../scripts/simulate";
function battle(
  cards = ["mossling", "spark", "ward", "rally", "mend"],
  seed = 1,
): GameState {
  const s = createGame(seed);
  s.deck = cards;
  return applyAction(s, { type: "travel", choice: "battle" });
}
function hand(s: GameState, ids: string[]) {
  s.deck = ids.slice();
  s.hand = ids.slice();
  s.draw = [];
  s.discard = [];
  s.allies = [];
}
function enemy(s: GameState, id: string, hp?: number): Unit {
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
function addAlly(s: GameState, id = "mossling"): Unit {
  const c = CARDS[id];
  const u = {
    uid: "a" + s.nextUid++,
    cardId: id,
    name: c.name,
    species: c.species!,
    color: c.color,
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
function settle(s: GameState): GameState {
  for (let i = 0; i < 400 && s.phase === "battle"; i++)
    s = applyAction(s, chooseHeuristic(s));
  assert.notEqual(s.phase, "battle");
  return s;
}
test("all original cards and upgrades are complete, targeted spells are explicit", () => {
  assert.equal(BASE_CARD_IDS.length, 24);
  assert.equal(Object.keys(CARDS).length, 48);
  for (const id of BASE_CARD_IDS) {
    assert.equal(CARDS[id].id, id);
    assert.equal(CARDS[id + "+"].id, id + "+");
    assert.ok(CARDS[id].text);
    assert.ok(CARDS[id + "+"].text);
    assert.ok(CARDS[id + "+"].type === CARDS[id].type);
  }
  assert.equal(cardTarget("spark"), "enemy");
  assert.equal(cardTarget("mend"), "ally");
  assert.equal(cardTarget("mossling"), "none");
});
test("seeds and serialized runs reproduce exactly and reducers preserve input", () => {
  let a = createGame(718),
    b = createGame(718);
  for (let i = 0; i < 200 && legalActions(a).length; i++) {
    const act = chooseHeuristic(a),
      before = JSON.stringify(a);
    a = applyAction(a, act);
    assert.equal(JSON.stringify(b), before);
    b = applyAction(JSON.parse(JSON.stringify(b)), act);
    assert.deepEqual(a, b);
    assert.ok(validateState(a));
  }
  assert.deepEqual(run(718, "heuristic"), run(718, "heuristic"));
});
test("invalid actions, missing target, overfull board and unaffordable cards leave identity unchanged", () => {
  let s = battle();
  assert.equal(applyAction(s, { type: "travel", choice: "boss" }), s);
  assert.equal(applyAction(s, { type: "play", index: -1 }), s);
  assert.equal(
    applyAction(s, { type: "attack", unit: "bogus", target: "e1" }),
    s,
  );
  hand(s, ["spark", "mossling", "ward", "mend", "rally"]);
  assert.equal(applyAction(s, { type: "play", index: 0 }), s);
  assert.equal(applyAction(s, { type: "play", index: 0, target: "hunter" }), s);
  assert.equal(
    applyAction(s, { type: "play", index: 3, target: s.enemies[0].uid }),
    s,
  );
  s.energy = 0;
  assert.equal(applyAction(s, { type: "play", index: 1 }), s);
  s.energy = 5;
  for (let i = 0; i < 6; i++) addAlly(s);
  assert.equal(applyAction(s, { type: "play", index: 1 }), s);
});
test("each live summon owns exactly one deck copy and cannot redraw", () => {
  let s = battle(["mossling", "spark", "ward", "mend", "rally"]);
  s = applyAction(s, { type: "play", index: s.hand.indexOf("mossling") });
  const u = s.allies[0];
  assert.equal(u.acted, false);
  assert.equal(
    [...s.hand, ...s.draw, ...s.discard].includes("mossling"),
    false,
  );
  assert.ok(validateState(s));
  s.enemies = [enemy(s, "crown", 500)];
  s.enemies[0].intent = { damage: 0, target: s.enemies[0].uid, label: "Armor" };
  for (let i = 0; i < 5; i++) {
    s = applyAction(s, { type: "endTurn" });
    assert.equal(
      [...s.hand, ...s.draw, ...s.discard].includes("mossling"),
      false,
    );
    assert.ok(validateState(s));
    s.enemies[0].intent = {
      damage: 0,
      target: s.enemies[0].uid,
      label: "Armor",
    };
  }
});
test("dead summon returns one copy to shared discard and can be summoned later", () => {
  let s = battle(["mossling", "spark", "ward", "mend", "rally"]);
  s = applyAction(s, { type: "play", index: s.hand.indexOf("mossling") });
  s.allies[0].hp = 1;
  s.enemies = [enemy(s, "wolf")];
  s.enemies[0].intent = {
    damage: 20,
    target: s.allies[0].uid,
    label: "Pounce",
  };
  s = applyAction(s, { type: "endTurn" });
  assert.equal(s.allies.length, 0);
  assert.equal(
    [...s.hand, ...s.draw, ...s.discard].filter((id) => id === "mossling")
      .length,
    1,
  );
  assert.ok(validateState(s));
});
test("new summon commands immediately once; ready spell permits another command", () => {
  let s = battle(["mossling", "recall", "ward", "mend", "rally"]);
  s.enemies = [enemy(s, "crown", 150)];
  s = applyAction(s, { type: "play", index: s.hand.indexOf("mossling") });
  const uid = s.allies[0].uid,
    eid = s.enemies[0].uid;
  s = applyAction(s, { type: "attack", unit: uid, target: eid });
  assert.equal(s.allies[0].acted, true);
  assert.equal(applyAction(s, { type: "attack", unit: uid, target: eid }), s);
  s = applyAction(s, {
    type: "play",
    index: s.hand.indexOf("recall"),
    target: uid,
  });
  assert.equal(s.allies[0].acted, false);
  s = applyAction(s, { type: "attack", unit: uid, target: eid });
  assert.equal(s.enemies[0].hp, 144);
});
test("visible enemy intent stays stable when companions are summoned", () => {
  let s = battle();
  const before = structuredClone(s.enemies.map((e) => e.intent));
  s = applyAction(s, { type: "play", index: s.hand.indexOf("mossling") });
  assert.deepEqual(
    s.enemies.map((e) => e.intent),
    before,
  );
});
test("dead companion intent target falls back to hunter without secretly retargeting", () => {
  let s = battle();
  hand(s, ["ward", "ward", "ward", "ward", "ward"]);
  const u = addAlly(s);
  u.hp = 1;
  s.enemies = [enemy(s, "wolf"), enemy(s, "wolf")];
  for (const e of s.enemies)
    e.intent = { damage: 5, target: u.uid, label: "Pounce" };
  const hp = s.hp;
  s = applyAction(s, { type: "endTurn" });
  assert.equal(s.hp, hp - 5);
  assert.equal(s.allies.length, 0);
  assert.ok(validateState(s));
});
test("wisp ignores armor; ordinary attacks consume armor", () => {
  let s = battle();
  s.allies = [];
  s.enemies = [enemy(s, "briar"), enemy(s, "wisp")];
  s.block = 20;
  const hp = s.hp;
  s = applyAction(s, { type: "endTurn" });
  assert.equal(s.hp, hp - 4);
  assert.equal(s.block, 0);
});
test("sentinel defense persists through player turn and alternates with attack", () => {
  let s = battle();
  s.enemies = [enemy(s, "sentinel")];
  s.enemies[0].intent = {
    damage: 0,
    target: s.enemies[0].uid,
    label: "Root armor · gain 6 block",
  };
  s = applyAction(s, { type: "endTurn" });
  assert.equal(s.enemies[0].block, 6);
  assert.equal(s.enemies[0].intent!.damage, s.enemies[0].attack + 3);
  assert.equal(s.enemies[0].intent!.target, "hunter");
  s = applyAction(s, { type: "endTurn" });
  assert.equal(s.enemies[0].block, 0);
  assert.equal(s.enemies[0].intent!.damage, 0);
});
test("wolf prefers front companion, imp weakest, witch alternates curse, boss cycles", () => {
  let s = battle();
  const strong = addAlly(s, "stonehart"),
    weak = addAlly(s, "reedkin");
  s.enemies = [
    enemy(s, "wolf"),
    enemy(s, "briar"),
    enemy(s, "witch"),
    enemy(s, "crown"),
  ];
  for (const e of s.enemies)
    e.intent = { damage: 0, target: e.uid, label: "Wait" };
  s = applyAction(s, { type: "endTurn" });
  assert.equal(s.enemies[0].intent!.target, strong.uid);
  assert.equal(s.enemies[1].intent!.target, weak.uid);
  assert.equal(s.enemies[2].intent!.damage, s.enemies[2].attack + 3);
  assert.equal(s.enemies[3].intent!.target, "all");
  assert.equal(s.enemies[3].intent!.damage, 5);
  s.enemies = s.enemies.slice(3);
  s = applyAction(s, { type: "endTurn" });
  assert.equal(s.enemies[0].intent!.target, "hunter");
  assert.equal(s.enemies[0].intent!.damage, s.enemies[0].attack + 5);
});
test("rally, moth spell armor, pack damage, relic bonus combine meaningfully", () => {
  let s = battle();
  hand(s, ["moonmoth", "rally", "thorns", "ward", "spark"]);
  s.enemies = [enemy(s, "crown", 100)];
  s.relics = ["moon-charm"];
  s.energy = 10;
  s = applyAction(s, { type: "play", index: 0 });
  const uid = s.allies[0].uid;
  s = applyAction(s, { type: "play", index: s.hand.indexOf("rally") });
  assert.equal(s.allies[0].attack, 5);
  assert.equal(s.block, 2);
  s = applyAction(s, {
    type: "play",
    index: s.hand.indexOf("thorns"),
    target: s.enemies[0].uid,
  });
  assert.equal(s.enemies[0].hp, 92);
  assert.equal(s.block, 4);
  assert.ok(s.allies.find((u) => u.uid === uid));
});
test("battle temporary stats reset while collection and hunter health persist", () => {
  let s = battle();
  s = settle(s);
  assert.equal(s.phase, "reward");
  const deck = s.deck.slice();
  assert.equal(s.allies.length, 0);
  assert.equal(s.hand.length, 0);
  s = applyAction(s, { type: "reward", card: null });
  assert.deepEqual(s.deck, deck);
  const hp = s.hp;
  s = applyAction(s, { type: "travel", choice: "battle" });
  assert.equal(s.hp, hp);
  assert.equal(s.energy, 5);
  assert.equal(s.turn, 1);
  assert.ok(validateState(s));
});
test("reward offers unique legal cards, awards gold once, can skip", () => {
  let s = settle(battle()),
    before = s.gold;
  assert.equal(s.rewards.length, 3);
  assert.equal(new Set(s.rewards).size, 3);
  assert.equal(before, 90);
  const id = s.rewards[0],
    size = s.deck.length;
  s = applyAction(s, { type: "reward", card: id });
  assert.equal(s.deck.length, size + 1);
  assert.equal(s.deck.at(-1), id);
  assert.equal(s.phase, "map");
  assert.equal(applyAction(s, { type: "reward", card: id }), s);
  assert.equal(s.gold, before);
});
test("shop purchases and removal use real prices, no repeated item, leave advances once", () => {
  let s = createGame(1);
  s.floor = 2;
  s.route = ["camp", "shop"];
  s = applyAction(s, { type: "travel", choice: "shop" });
  const id = s.rewards.find((id) => CARDS[id].type === "spell") ?? s.rewards[0],
    gold = s.gold;
  s = applyAction(s, { type: "buy", card: id });
  assert.equal(s.gold, gold - SHOP_PRICES[CARDS[id].type]);
  assert.equal(s.rewards.includes(id), false);
  assert.equal(applyAction(s, { type: "buy", card: id }), s);
  s.gold = 35;
  const size = s.deck.length;
  s = applyAction(s, { type: "remove", index: 0 });
  assert.equal(s.gold, 0);
  assert.equal(s.deck.length, size - 1);
  assert.equal(applyAction(s, { type: "remove", index: 0 }), s);
  s = applyAction(s, { type: "leave" });
  assert.equal(s.phase, "map");
  assert.equal(s.floor, 3);
  assert.ok(validateState(s));
});
test("camp enhancement is permanent, rest capped, shrine cannot kill hunter or duplicate relic", () => {
  let s = createGame(1);
  s.floor = 2;
  s.route = ["camp", "shop"];
  s = applyAction(s, { type: "travel", choice: "camp" });
  s = applyAction(s, { type: "camp", choice: "train" });
  assert.equal(s.deck[0], "mossling+");
  s.floor = 4;
  s.route = ["event", "shop"];
  s = applyAction(s, { type: "travel", choice: "event" });
  s.hp = 8;
  assert.equal(applyAction(s, { type: "event", choice: "offering" }), s);
  s.hp = 30;
  s = applyAction(s, { type: "event", choice: "offering" });
  assert.equal(s.hp, 22);
  assert.deepEqual(s.relics, ["moon-charm"]);
  assert.equal(s.phase, "map");
  s.floor = 8;
  s.route = ["camp", "event"];
  s = applyAction(s, { type: "travel", choice: "camp" });
  s.hp = 60;
  s = applyAction(s, { type: "camp", choice: "rest" });
  assert.equal(s.hp, 65);
  assert.ok(validateState(s));
});
test("hunter death ends immediately even when finishing the last enemy in the same action", () => {
  let s = battle();
  hand(s, ["kindle", "spark", "ward", "rally", "mend"]);
  s.hp = 2;
  s = applyAction(s, { type: "play", index: 0 });
  assert.equal(s.phase, "defeat");
  assert.equal(s.hp, 0);
  assert.equal(legalActions(s).length, 0);
  assert.ok(validateState(s));
  assert.equal(applyAction(s, { type: "endTurn" }), s);
});
test("boss victory terminal state preserves collection and has no further actions", () => {
  let s = createGame(43);
  for (let i = 0; i < 1000 && legalActions(s).length; i++) {
    s = applyAction(s, chooseHeuristic(s));
    assert.ok(validateState(s));
  }
  assert.equal(s.phase, "victory");
  assert.equal(s.floor, 10);
  assert.equal(s.enemies.length, 0);
  assert.equal(legalActions(s).length, 0);
  assert.ok(s.stats.battles >= 5);
});
test("save validator rejects primitive, cyclic missing fields, corrupt numbers, ids and conservation", () => {
  for (const value of [null, undefined, {}, [], 1, "save", true, new Date()])
    assert.equal(validateState(value), false);
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
    ["hand", ["spark", "spark", "spark", "spark", "spark"]],
  ] as [string, unknown][]) {
    const bad = structuredClone(s);
    (bad as unknown as Record<string, unknown>)[field] = value;
    assert.equal(validateState(bad), false, field);
  }
  const dup = structuredClone(s);
  dup.enemies[1].uid = dup.enemies[0].uid;
  assert.equal(validateState(dup), false);
  const constructor = structuredClone(s);
  constructor.enemies[0].cardId = "constructor";
  assert.equal(validateState(constructor), false);
  const badIntent = structuredClone(s);
  badIntent.enemies[0].intent!.target = "foreign";
  assert.equal(validateState(badIntent), false);
  assert.equal(
    validateState(
      new Proxy(
        {},
        {
          get() {
            throw new Error("hostile");
          },
        },
      ),
    ),
    false,
  );
  assert.ok(validateState(JSON.parse(JSON.stringify(s))));
});
test("100 independent legal random runs conserve copies and end within simulation budget", () => {
  for (let seed = 1; seed <= 100; seed++) {
    const result = run(seed, "random");
    assert.ok(["victory", "defeat"].includes(result.phase));
    assert.ok(result.steps < 3000);
  }
});

test("menu is presentation only and cannot be restored as a dead-end run", () => {
  const save = JSON.parse(JSON.stringify(createGame(77))) as GameState;
  save.phase = "menu";
  assert.equal(legalActions(save).length, 0);
  assert.equal(validateState(save), false);
  assert.ok(validateState(createGame(77)));
});

test("save validation reserves the final combat node for the boss", () => {
  const save = battle();
  save.floor = 10;
  save.route = ["battle"];
  save.hand = ["spark"];
  save.draw = save.deck.slice();
  save.draw.splice(save.draw.indexOf("spark"), 1);
  save.discard = [];
  save.allies = [];
  save.enemies = [enemy(save, "briar", 1)];
  assert.equal(validateState(save), false);
  // This corrupt save would otherwise yield a reward at floor ten, from
  // which no legitimate next map exists. The load gate must reject it.
  const won = applyAction(save, {
    type: "play",
    index: 0,
    target: save.enemies[0].uid,
  });
  assert.equal(won.phase, "reward");
  assert.equal(validateState(won), false);
  const finalMap = createGame(77);
  finalMap.floor = 9;
  finalMap.route = ["boss"];
  const boss = applyAction(finalMap, { type: "travel", choice: "boss" });
  assert.ok(validateState(boss));
  assert.equal(boss.floor, 10);
  assert.deepEqual(boss.route, ["boss"]);
});

test("encounter saves require a choice offered by their actual node", () => {
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
  for (let index = 0; index < choices.length; index++) {
    for (const choice of choices[index]) {
      const map = createGame(101);
      map.floor = index;
      map.route = choices[index];
      const entered = applyAction(map, { type: "travel", choice });
      assert.ok(validateState(entered), `generated ${index + 1} ${choice}`);
      for (let node = 1; node <= 10; node++) {
        const moved = structuredClone(entered);
        moved.floor = node;
        assert.equal(
          validateState(moved),
          choices[node - 1].includes(choice),
          `node ${node} ${choice}`,
        );
      }
    }
  }
});
