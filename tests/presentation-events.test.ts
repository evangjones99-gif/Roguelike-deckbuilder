import test from "node:test";
import assert from "node:assert/strict";
import {
  applyAction,
  applyActionWithEvents,
  createGame as createCurrentGame,
  legalActions,
  validateState,
  CARDS,
  type GameState,
  type Action,
  type Unit,
  type ResolvedEvent,
} from "../src/engine";
import * as archived from "../reviews/ml-policy-v0.2/engine";
import { ENEMIES } from "../src/content";
import { chooseHeuristic } from "../scripts/simulate";
const createGame = (seed: number, difficulty = 0) =>
  createCurrentGame(seed, difficulty, { engineKind: 1 });
const starting = ["cairnhound", "scour", "ironward", "sutures", "sunder"];
function battle(cards = starting) {
  const map = createGame(31);
  map.deck = cards.slice();
  return applyAction(map, { type: "travel", choice: "battle" });
}
function foe(s: GameState, id: string, hp?: number): Unit {
  const def = ENEMIES[id];
  return {
    uid: "e" + s.nextUid++,
    cardId: id,
    ...def,
    hp: hp ?? def.hp,
    maxHp: hp ?? def.hp,
    block: 0,
    acted: false,
    intent: { damage: def.attack, target: "hunter", label: "Strike" },
  };
}
function play(s: GameState, id: string, target?: string) {
  return {
    type: "play",
    index: s.hand.indexOf(id),
    ...(target ? { target } : {}),
  } as Action;
}
function onlyHits(events: ResolvedEvent[]) {
  return events.filter(
    (event): event is Extract<ResolvedEvent, { type: "hit" }> =>
      event.type === "hit",
  );
}

test("events and ordinary reducer remain byte equivalent to archived v0.2 across seeded legal runs", () => {
  let accepted = 0;
  for (let difficulty = 0; difficulty <= 2; difficulty++)
    for (let seed = 7101; seed <= 7124; seed++) {
      let current = createGame(seed, difficulty),
        old = archived.createGame(seed, difficulty);
      assert.equal(JSON.stringify(current), JSON.stringify(old));
      for (let step = 0; step < 1500 && legalActions(current).length; step++) {
        const action = chooseHeuristic(current),
          before = JSON.stringify(current);
        const result = applyActionWithEvents(current, action),
          ordinary = applyAction(current, action);
        old = archived.applyAction(old, action);
        assert.equal(
          JSON.stringify(current),
          before,
          "incoming state was mutated",
        );
        assert.equal(
          JSON.stringify(result.state),
          JSON.stringify(old),
          "archived rules changed",
        );
        assert.equal(
          JSON.stringify(ordinary),
          JSON.stringify(old),
          "ordinary reducer changed",
        );
        assert.ok(validateState(result.state));
        const replay = applyActionWithEvents(JSON.parse(before), action);
        assert.deepEqual(replay.events, result.events, "event replay differs");
        assert.equal(
          JSON.stringify(replay.state),
          JSON.stringify(result.state),
        );
        current = result.state;
        accepted++;
      }
      assert.ok(["victory", "defeat"].includes(current.phase));
    }
  assert.ok(accepted > 5000);
});

test("invalid actions produce no observations and preserve object identity", () => {
  const s = battle();
  for (const action of [
    { type: "play", index: -1 },
    { type: "attack", unit: "missing", target: s.enemies[0].uid },
    { type: "travel", choice: "boss" },
  ] as Action[]) {
    const result = applyActionWithEvents(s, action);
    assert.equal(result.state, s);
    assert.deepEqual(result.events, []);
  }
});

test("first lethal hunter strike suppresses every later enemy strike", () => {
  const s = battle();
  s.hp = 1;
  s.block = 0;
  s.enemies = [foe(s, "thrall"), foe(s, "thrall"), foe(s, "revenant")];
  for (const e of s.enemies)
    e.intent = { damage: 7, target: "hunter", label: "Lethal strike" };
  const result = applyActionWithEvents(s, { type: "endTurn" }),
    hits = onlyHits(result.events);
  assert.equal(result.state.phase, "defeat");
  assert.equal(hits.length, 1);
  assert.equal(hits[0].source, s.enemies[0].uid);
  assert.equal(hits[0].target, "hunter");
  assert.equal(hits[0].hpLost, 1);
  assert.equal(hits[0].beforeHp, 1);
  assert.equal(hits[0].afterHp, 0);
  assert.deepEqual(
    result.events.map((e) => e.type),
    ["hit", "death"],
  );
  assert.equal(
    JSON.stringify(result.state),
    JSON.stringify(archived.applyAction(s as archived.GameState, { type: "endTurn" })),
  );
});

test("a later strike resolves to hunter after its announced creature target dies", () => {
  let s = battle();
  s = applyAction(s, play(s, "cairnhound"));
  const binding = s.allies[0];
  binding.hp = 1;
  s.block = 0;
  s.enemies = [foe(s, "thrall"), foe(s, "thrall")];
  for (const e of s.enemies)
    e.intent = { damage: 6, target: binding.uid, label: "Claw same binding" };
  const result = applyActionWithEvents(s, { type: "endTurn" }),
    hits = onlyHits(result.events);
  assert.deepEqual(
    hits.map((e) => ({ source: e.source, target: e.target, hpLost: e.hpLost })),
    [
      { source: s.enemies[0].uid, target: binding.uid, hpLost: 1 },
      { source: s.enemies[1].uid, target: "hunter", hpLost: 6 },
    ],
  );
  assert.deepEqual(
    result.events.map((e) => e.type),
    ["hit", "death", "hit"],
  );
  assert.equal(result.state.hp, 59);
  assert.equal(result.state.allies.length, 0);
  assert.equal(
    result.state.discard.filter((id) => id === "cairnhound").length +
      result.state.hand.filter((id) => id === "cairnhound").length +
      result.state.draw.filter((id) => id === "cairnhound").length,
    1,
  );
});

test("one executed area attack finishes its real targets even if hunter dies, then skips later enemies", () => {
  let s = battle();
  s = applyAction(s, play(s, "cairnhound"));
  s.allies[0].hp = 1;
  s.hp = 1;
  s.block = 0;
  s.enemies = [foe(s, "brood"), foe(s, "thrall")];
  s.enemies[0].intent = { damage: 5, target: "all", label: "Cinder breath" };
  s.enemies[1].intent = { damage: 7, target: "hunter", label: "Later claw" };
  const result = applyActionWithEvents(s, { type: "endTurn" }),
    hits = onlyHits(result.events);
  assert.equal(hits.length, 2);
  assert.ok(hits.every((hit) => hit.source === s.enemies[0].uid));
  assert.deepEqual(
    hits.map((hit) => hit.target),
    ["hunter", s.allies[0].uid],
  );
  assert.equal(result.state.allies.length, 0);
  assert.equal(
    JSON.stringify(result.state),
    JSON.stringify(archived.applyAction(s as archived.GameState, { type: "endTurn" })),
  );
});

test("fully blocked attacks are observed with zero health loss and real absorbed damage", () => {
  const s = battle();
  s.enemies = [foe(s, "thrall")];
  s.block = 10;
  s.enemies[0].intent = { damage: 6, target: "hunter", label: "Claw" };
  const result = applyActionWithEvents(s, { type: "endTurn" }),
    hit = onlyHits(result.events)[0];
  assert.equal(hit.damage, 6);
  assert.equal(hit.blocked, 6);
  assert.equal(hit.hpLost, 0);
  assert.equal(hit.beforeHp, 65);
  assert.equal(hit.afterHp, 65);
  assert.equal(hit.kind, "enemy");
  assert.equal(
    result.events.some((e) => e.type === "death"),
    false,
  );
});

test("piercing and self damage report zero block absorption despite existing wards", () => {
  const s = battle();
  s.enemies = [foe(s, "revenant")];
  s.block = 20;
  const pierced = applyActionWithEvents(s, { type: "endTurn" });
  assert.equal(onlyHits(pierced.events)[0].blocked, 0);
  assert.equal(onlyHits(pierced.events)[0].hpLost, 5);
  const self = battle(["bloodprice", "scour", "ironward", "sutures", "sunder"]);
  self.block = 20;
  self.hp = 3;
  const spent = applyActionWithEvents(self, play(self, "bloodprice"));
  assert.equal(onlyHits(spent.events)[0].kind, "self");
  assert.equal(onlyHits(spent.events)[0].blocked, 0);
  assert.equal(spent.state.block, 20);
  assert.deepEqual(
    spent.events.map((e) => e.type),
    ["hit", "death"],
  );
});

test("stalker recovery and retaliation remain distinct despite zero net creature HP change", () => {
  let s = battle(["fenstalker", "scour", "ironward", "sutures", "sunder"]);
  s = applyAction(s, play(s, "fenstalker"));
  s.allies[0].hp = 4;
  s.allies[0].block = 20;
  s.enemies = [foe(s, "ironjaw", 100)];
  s.enemies[0].block = 1;
  const result = applyActionWithEvents(s, {
    type: "attack",
    unit: s.allies[0].uid,
    target: s.enemies[0].uid,
  });
  assert.equal(result.state.allies[0].hp, 4);
  assert.deepEqual(
    result.events.map((e) => e.type),
    ["hit", "heal", "hit"],
  );
  const hits = onlyHits(result.events);
  assert.equal(hits[0].kind, "command");
  assert.equal(hits[0].blocked, 1);
  assert.equal(hits[0].hpLost, 3);
  assert.equal(hits[1].kind, "retaliation");
  assert.equal(hits[1].source, s.enemies[0].uid);
  assert.equal(hits[1].target, s.allies[0].uid);
  assert.equal(hits[1].blocked, 0);
  assert.equal(hits[1].hpLost, 2);
});

test("retaliation death follows command hit and returns exactly one real card copy", () => {
  let s = battle();
  s = applyAction(s, play(s, "cairnhound"));
  s.allies[0].hp = 2;
  s.enemies = [foe(s, "ironjaw", 100)];
  s.enemies[0].block = 14;
  const result = applyActionWithEvents(s, {
    type: "attack",
    unit: s.allies[0].uid,
    target: s.enemies[0].uid,
  });
  assert.deepEqual(
    result.events.map((e) => e.type),
    ["hit", "hit", "death"],
  );
  assert.equal(result.events[2].target, s.allies[0].uid);
  assert.equal(result.state.allies.length, 0);
  assert.equal(
    result.state.discard.filter((id) => id === "cairnhound").length,
    1,
  );
});

test("spell area damage records resolved roster targets and each death in order", () => {
  const s = battle(["witchfire", "scour", "ironward", "sutures", "sunder"]);
  s.enemies = [foe(s, "thrall", 2), foe(s, "thrall", 3)];
  const result = applyActionWithEvents(s, play(s, "witchfire"));
  assert.equal(result.state.phase, "reward");
  assert.deepEqual(
    result.events
      .filter((e) => e.type === "hit" || e.type === "death")
      .map((e) => [e.type, e.target]),
    [
      ["hit", s.enemies[0].uid],
      ["death", s.enemies[0].uid],
      ["hit", s.enemies[1].uid],
      ["death", s.enemies[1].uid],
    ],
  );
  assert.ok(
    onlyHits(result.events).every(
      (e) =>
        e.kind === "spell" && e.source === "hunter" && e.cardId === "witchfire",
    ),
  );
});

test("binding snapshots survive on-bind victory cleanup and cannot mutate returned state", () => {
  const s = battle(["emberwidow", "scour", "ironward", "sutures", "sunder"]);
  s.enemies = [foe(s, "thrall", 1)];
  const result = applyActionWithEvents(s, play(s, "emberwidow"));
  assert.equal(result.state.phase, "reward");
  const event = result.events[0];
  assert.equal(event.type, "summon");
  assert.ok(event.type === "summon");
  assert.equal(event.side, "ally");
  assert.equal(event.unit.cardId, "emberwidow");
  assert.equal(event.unit.hp, CARDS.emberwidow.hp);
  assert.deepEqual(
    result.events.map((e) => e.type),
    ["summon", "hit", "death"],
  );
  const live = battle();
  const bound = applyActionWithEvents(live, play(live, "cairnhound"));
  const snapshot = bound.events.find((e) => e.type === "summon");
  assert.ok(snapshot?.type === "summon");
  snapshot.unit.hp = 999;
  assert.equal(bound.state.allies[0].hp, 7);
  bound.state.allies[0].hp = 1;
  assert.equal(snapshot.unit.hp, 999);
});

test("necromancy emits summons from actual raising source without immediate enemy hits", () => {
  const map = createGame(1);
  map.floor = 9;
  map.route = ["boss"];
  const s = applyAction(map, { type: "travel", choice: "boss" });
  const result = applyActionWithEvents(s, { type: "endTurn" });
  assert.deepEqual(
    result.events.map((e) => e.type),
    ["summon", "summon"],
  );
  for (const e of result.events) {
    assert.ok(e.type === "summon");
    assert.equal(e.source, s.enemies[0].uid);
    assert.equal(e.side, "enemy");
    assert.equal(e.cardId, "thrall");
    assert.equal(e.unit.uid, e.target);
  }
  const silenced = battle([
    "silence",
    "scour",
    "ironward",
    "sutures",
    "sunder",
  ]);
  silenced.enemies = [foe(silenced, "acolyte")];
  silenced.enemies[0].intent = {
    damage: 0,
    target: silenced.enemies[0].uid,
    label: "Raise",
    summon: ["thrall"],
  };
  const control = applyActionWithEvents(
    silenced,
    play(silenced, "silence", silenced.enemies[0].uid),
  );
  assert.equal(control.events.length, 1);
  assert.equal(control.events[0].type, "control");
  assert.deepEqual(
    applyActionWithEvents(control.state, { type: "endTurn" }).events,
    [],
  );
});

test("healing and wards emit actual gains only, with guard source resolved explicitly", () => {
  let s = battle();
  const bind = applyActionWithEvents(s, play(s, "cairnhound"));
  assert.deepEqual(
    bind.events.map((e) => e.type),
    ["summon", "ward"],
  );
  assert.equal(bind.events[1].source, bind.state.allies[0].uid);
  s = bind.state;
  s.allies[0].hp = 6;
  const restored = applyActionWithEvents(
    s,
    play(s, "sutures", s.allies[0].uid),
  );
  assert.deepEqual(
    restored.events.map((e) => e.type),
    ["heal", "ward"],
  );
  const healing = restored.events[0];
  assert.ok(healing.type === "heal");
  assert.equal(healing.amount, 1);
  assert.equal(healing.beforeHp, 6);
  assert.equal(healing.afterHp, 7);
  const map = createGame(0);
  map.floor = 9;
  map.route = ["boss"];
  const guard = applyAction(map, { type: "travel", choice: "boss" });
  const guarded = applyActionWithEvents(guard, { type: "endTurn" });
  assert.deepEqual(guarded.events, [
    {
      type: "ward",
      source: guard.enemies[0].uid,
      target: guard.enemies[0].uid,
      amount: 14,
    },
  ]);
});

test("random legal replays preserve archived states across rewards, crypt, shop and control branches", () => {
  const visited = new Set<string>();
  for (let seed = 7901; seed <= 7948; seed++) {
    let current = createGame(seed, seed % 3),
      old = archived.createGame(seed, seed % 3),
      rng = seed;
    for (let step = 0; step < 1500 && legalActions(current).length; step++) {
      const actions = legalActions(current);
      rng = (Math.imul(rng, 1664525) + 1013904223) >>> 0;
      const action = actions[Math.floor((rng / 4294967296) * actions.length)];
      if (action.type === "play")
        visited.add("effect:" + CARDS[current.hand[action.index]].effect);
      else
        visited.add(
          action.type + ("choice" in action ? ":" + action.choice : ""),
        );
      const result = applyActionWithEvents(current, action);
      old = archived.applyAction(old, action);
      assert.equal(JSON.stringify(result.state), JSON.stringify(old));
      assert.ok(validateState(result.state));
      current = result.state;
    }
    assert.ok(["victory", "defeat"].includes(current.phase));
  }
  for (const action of [
    "travel",
    "reward",
    "buy",
    "remove",
    "camp:rest",
    "camp:train",
    "event:purge",
    "event:bargain",
    "effect:control",
    "effect:energy",
  ]) {
    assert.ok(
      [...visited].some(
        (value) => value === action || value.startsWith(action + ":"),
      ),
      action + " was not exercised",
    );
  }
});

test("Silence reports a truthful noninjury control event and redundant silence emits no second cue", () => {
  const s = battle(["silence", "silence", "scour", "ironward", "survey"]);
  s.enemies = [foe(s, "acolyte")];
  s.enemies[0].intent = {
    damage: 9,
    target: "hunter",
    label: "Raising curse",
    summon: ["thrall"],
  };
  const before = structuredClone(s.enemies[0].intent);
  const result = applyActionWithEvents(s, play(s, "silence", s.enemies[0].uid));
  assert.equal(result.events.length, 1);
  const event = result.events[0];
  assert.ok(event.type === "control");
  assert.equal(event.source, "hunter");
  assert.equal(event.target, s.enemies[0].uid);
  assert.equal(event.cardId, "silence");
  assert.deepEqual(event.before, before);
  assert.equal(event.after.damage, 0);
  assert.deepEqual(event.after.summon, []);
  assert.equal(
    result.events.some((e) => e.type === "hit" || e.type === "death"),
    false,
  );
  assert.equal(
    JSON.stringify(result.state),
    JSON.stringify(
      archived.applyAction(s as archived.GameState, play(s, "silence", s.enemies[0].uid)),
    ),
  );
  const again = applyActionWithEvents(
    result.state,
    play(result.state, "silence", s.enemies[0].uid),
  );
  assert.deepEqual(again.events, []);
  event.after.damage = 999;
  assert.equal(result.state.enemies[0].intent!.damage, 0);
});

test("Edict reports each real attack increase in roster order without invented injuries", () => {
  let s = battle(["cairnhound", "fenstalker", "edict", "ironward", "survey"]);
  s.energy = 10;
  s = applyAction(s, play(s, "cairnhound"));
  s = applyAction(s, play(s, "fenstalker"));
  const before = s.allies.map((u) => ({ uid: u.uid, attack: u.attack }));
  const result = applyActionWithEvents(s, play(s, "edict"));
  assert.deepEqual(
    result.events,
    before.map((u) => ({
      type: "buff",
      source: "hunter",
      target: u.uid,
      cardId: "edict",
      stat: "attack",
      before: u.attack,
      after: u.attack + 2,
      amount: 2,
    })),
  );
  assert.equal(
    result.events.some((e) => e.type === "hit" || e.type === "death"),
    false,
  );
  assert.equal(
    JSON.stringify(result.state),
    JSON.stringify(archived.applyAction(s as archived.GameState, play(s, "edict"))),
  );
  const empty = battle(["edict", "scour", "ironward", "sutures", "survey"]);
  assert.deepEqual(
    applyActionWithEvents(empty, play(empty, "edict")).events,
    [],
  );
});
