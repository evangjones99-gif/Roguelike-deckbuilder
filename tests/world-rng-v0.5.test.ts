import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { applyAction, applyActionWithEvents, createGame, legalActions,
  recoverLegacySilenceSave, validateState, type Action, type GameState,
} from "../src/engine";
import { worldRank, worldDrawSeed, worldOrder, worldFormation,
  type WorldPurpose } from "../src/world-rng";
import { BASE_CARD_IDS, RELICS, bossForSeed, SHOP_PRICES } from "../src/content";
import * as v04 from "./fixtures/v0.4/engine";
import { chooseHeuristic } from "../scripts/simulate";

const hash = (name: string) => createHash("sha256")
  .update(readFileSync(new URL(name, import.meta.url))).digest("hex");
function accepted(s: GameState, a: Action): GameState {
  assert.ok(legalActions(s).some(legal => JSON.stringify(legal) === JSON.stringify(a)));
  const before = JSON.stringify(s), next = applyAction(s, a);
  assert.notEqual(next, s);
  assert.equal(JSON.stringify(s), before);
  assert.ok(validateState(next));
  return next;
}
function fight(s: GameState): GameState {
  for (let i = 0; i < 500 && s.phase === "battle"; i++)
    s = accepted(s, chooseHeuristic(s));
  assert.equal(s.phase, "reward", "reachable arm must survive this early contract");
  return s;
}
function roster(s: GameState) { return s.enemies.map(e => e.cardId); }
function firstReward(seed: number): GameState {
  return fight(accepted(createGame(seed), { type: "travel", choice: "battle" }));
}

test("generation2 production hash matches frozen research vectors and browser comparison evidence", () => {
  const golden = JSON.parse(readFileSync(new URL(
    "../reviews/world-rng-v0.5/golden-vectors-r1.json", import.meta.url), "utf8"));
  assert.equal(golden.nodeBrowserExact, true);
  for (const g of golden.golden) {
    const [, generation, seed, purpose, node, kind, identity] = g.key;
    assert.equal(generation, 2);
    assert.equal(worldRank(purpose, { seed, node, kind }, identity)
      .toString(16).padStart(16, "0"), g.expected);
  }
  assert.equal(worldDrawSeed({ seed: 1989, node: 10, kind: "boss" }), 3179913161);
  assert.equal(worldDrawSeed({ seed: 4294967295, node: 10, kind: "boss" }), 687320204);
});

test("generation classification is explicit and old serialization has no new fields", () => {
  const next = createGame(1989), old = createGame(1989, 0, { engineKind: 1 });
  assert.equal(next.schema, 3);
  assert.equal(next.engineKind, 2);
  assert.ok(validateState(next) && validateState(old));
  assert.deepEqual(old, v04.createGame(1989));
  assert.equal(Object.hasOwn(old, "engineKind"), false);
  for (const marker of [undefined, 1, 2, 3, "2", null]) {
    assert.equal(validateState({ ...old, engineKind: marker }), false);
    assert.equal(validateState({ ...next, engineKind: marker }), marker === 2);
  }
  const { engineKind: ignored, ...unmarked } = next;
  assert.equal(validateState(unmarked), false);
  assert.equal(validateState({ ...old, schema: 1 }), false);
  assert.equal(validateState({ ...next, schema: 4 }), false);
  assert.equal(validateState({ ...next, phase: "menu" }), false);
  assert.throws(() => createGame(1, 0, { engineKind: 3 as 2 }), RangeError);
});

test("actual v0.4 fixture provenance and kind1 continuation stay byte exact", () => {
  assert.equal(hash("fixtures/v0.4/engine.ts"), "ee85f1400a9d02142aee1dd66f82722453f35930bbf2c0c229ad38e38a818d0d");
  assert.equal(hash("fixtures/v0.4/content.ts"), "2f45160b3e577a7cd44381cb361c4407661a68819ff827a24b8ab34ce15c4234");
  for (let seed = 8101; seed <= 8118; seed++) {
    let s = createGame(seed, seed % 3, { engineKind: 1 }),
      old = v04.createGame(seed, seed % 3);
    for (let i = 0; i < 1000 && legalActions(s).length; i++) {
      const a = chooseHeuristic(s), result = applyActionWithEvents(JSON.parse(JSON.stringify(s)), a);
      const previous = JSON.stringify(s);
      old = v04.applyAction(old, a);
      assert.deepEqual(result, v04.applyActionWithEvents(JSON.parse(previous), a));
      s = result.state;
      assert.equal(JSON.stringify(s), JSON.stringify(old));
      assert.equal(s.schema, 2);
      assert.equal(Object.hasOwn(s, "engineKind"), false);
      assert.ok(validateState(s));
    }
    assert.ok(["victory", "defeat"].includes(s.phase));
  }
});

test("reachable card acquisition, draw history and shop sculpture cannot reroll common world nodes", () => {
  for (let seed = 6501; seed <= 6512; seed++) {
    const reward = firstReward(seed);
    let take = accepted(reward, { type: "reward", card: reward.rewards[0] }),
      skip = accepted(reward, { type: "reward", card: null });
    take = accepted(take, { type: "travel", choice: "battle" });
    skip = accepted(skip, { type: "travel", choice: "battle" });
    assert.deepEqual(roster(take), roster(skip));
    assert.equal(take.deck.length, skip.deck.length + 1);
    take = fight(take); skip = fight(skip);
    assert.deepEqual(take.rewards, skip.rewards);
    take = accepted(take, { type: "reward", card: null });
    skip = accepted(skip, { type: "reward", card: null });
    take = accepted(take, { type: "travel", choice: "shop" });
    skip = accepted(skip, { type: "travel", choice: "shop" });
    assert.deepEqual(take.rewards, skip.rewards);
    const takeRng = take.rng, skipRng = skip.rng, bought = take.rewards[0];
    take = accepted(take, { type: "buy", card: bought });
    skip = accepted(skip, { type: "remove", index: 0 });
    assert.equal(take.rng, takeRng); assert.equal(skip.rng, skipRng);
    assert.equal(SHOP_PRICES.remove, 35);
    take = accepted(take, { type: "leave" }); skip = accepted(skip, { type: "leave" });
    take = accepted(take, { type: "travel", choice: "elite" });
    skip = accepted(skip, { type: "travel", choice: "elite" });
    assert.deepEqual(roster(take), roster(skip));
    take = fight(take); skip = fight(skip);
    assert.deepEqual(take.rewards, skip.rewards);
    assert.deepEqual(take.relics, skip.relics);
    assert.ok(take.log.some(l => l.includes(RELICS[take.relics.at(-1)!].name)));
  }
});

test("reachable alternate route choices do not advance any shared world cursor", () => {
  for (let seed = 6601; seed <= 6608; seed++) {
    let combat = accepted(firstReward(seed), { type: "reward", card: null }),
      event = JSON.parse(JSON.stringify(combat)) as GameState;
    combat = fight(accepted(combat, { type: "travel", choice: "battle" }));
    combat = accepted(combat, { type: "reward", card: null });
    event = accepted(event, { type: "travel", choice: "event" });
    event = accepted(event, { type: "event", choice: "forage" });
    const a = accepted(combat, { type: "travel", choice: "shop" }),
      b = accepted(event, { type: "travel", choice: "shop" });
    assert.deepEqual(a.rewards, b.rewards);
    const nextA = accepted(accepted(a, { type: "leave" }), { type: "travel", choice: "elite" }),
      nextB = accepted(accepted(b, { type: "leave" }), { type: "travel", choice: "elite" });
    assert.deepEqual(roster(nextA), roster(nextB));
  }
});

test("identity ranking is pure and invariant to catalogue ordering and owned exclusions", () => {
  const context = Object.freeze({ seed: 1989, node: 4, kind: "elite" });
  for (const purpose of ["reward", "shop", "relic"] as WorldPurpose[]) {
    const ids = purpose === "relic" ? Object.keys(RELICS) : BASE_CARD_IDS;
    const ranked = worldOrder(Object.freeze(ids.slice()), purpose, context);
    assert.deepEqual(worldOrder([...ids].reverse(), purpose, context), ranked);
    const owned = new Set(ranked.slice(0, 2));
    assert.deepEqual(worldOrder(ids.filter(id => !owned.has(id)), purpose, context),
      ranked.filter(id => !owned.has(id)));
  }
  const seen = new Set<string>();
  for (let seed = 1; seed <= 80; seed++) seen.add(worldFormation({ seed, node: 4, kind: "elite" }).join(","));
  assert.equal(seen.size, 4);
  assert.throws(() => worldFormation({ seed: 1, node: 3, kind: "shop" }), RangeError);
});

test("new-generation full serialized/event replays preserve stream positions and query purity", () => {
  const phases = new Set<string>();
  let turns = 0, reshuffles = 0, bosses = 0;
  for (let seed = 9101; seed <= 9136; seed++) {
    let s = createGame(seed, seed % 3);
    for (let i = 0; i < 1000 && legalActions(s).length; i++) {
      phases.add(s.phase);
      const a = chooseHeuristic(s), before = JSON.stringify(s), rng = s.rng;
      const preview = applyActionWithEvents(s, a);
      assert.equal(JSON.stringify(s), before);
      assert.equal(s.rng, rng);
      assert.deepEqual(applyActionWithEvents(JSON.parse(before), a), preview);
      assert.deepEqual(applyAction(JSON.parse(before), a), preview.state);
      if (a.type === "endTurn" && s.draw.length < 5 && preview.state.phase === "battle")
        reshuffles++;
      if (a.type === "travel" && a.choice === "boss") {
        assert.equal(preview.state.enemies[0].cardId, bossForSeed(seed));
        bosses++;
      }
      s = preview.state;
      assert.ok(validateState(s));
      if (a.type === "endTurn") turns++;
    }
    assert.ok(["victory", "defeat"].includes(s.phase));
    assert.equal(bossForSeed(s.seed), bossForSeed(seed));
    assert.deepEqual(applyActionWithEvents(s, { type: "endTurn" }), { state: s, events: [] });
  }
  assert.ok(turns > 200, "many actual draw/reshuffle boundaries must be exercised");
  assert.ok(reshuffles > 10, "actual discard recycling boundaries must be exercised");
  assert.ok(bosses > 10);
  for (const phase of ["map", "battle", "reward", "shop", "camp", "event"])
    assert.ok(phases.has(phase), "missing save checkpoint " + phase);
});

test("explicit kind2 legal-random campaigns validate and serialize every accepted state", () => {
  for (let seed = 9301; seed <= 9336; seed++) {
    let s = createGame(seed, seed % 3), decisionRng = seed;
    for (let i = 0; i < 1500 && legalActions(s).length; i++) {
      const actions = legalActions(s);
      decisionRng = (Math.imul(decisionRng, 1664525) + 1013904223) >>> 0;
      const a = actions[Math.floor((decisionRng / 4294967296) * actions.length)];
      const before = JSON.stringify(s), next = applyActionWithEvents(s, a);
      assert.equal(JSON.stringify(s), before);
      assert.deepEqual(next, applyActionWithEvents(JSON.parse(before), a));
      s = next.state;
      assert.ok(validateState(s));
      assert.equal(s.schema, 3); assert.equal(s.engineKind, 2);
      assert.ok(validateState(JSON.parse(JSON.stringify(s))));
    }
    assert.ok(["victory", "defeat"].includes(s.phase));
    assert.equal(legalActions(s).length, 0);
  }
});

test("recovery rejects nonserializable programmatic extras and cannot switch generations", () => {
  const fixture = JSON.parse(readFileSync(new URL(
    "../reviews/solo-v0.3/silence-overflow-campaign.json", import.meta.url), "utf8"));
  const cycle = structuredClone(fixture.afterState); cycle.extra = cycle;
  assert.equal(recoverLegacySilenceSave(cycle), null);
  assert.equal(recoverLegacySilenceSave({ ...fixture.afterState, extra: 1n }), null);
  assert.equal(recoverLegacySilenceSave({ ...fixture.afterState, engineKind: 2 }), null);
  assert.equal(recoverLegacySilenceSave({ ...fixture.afterState, schema: 3, engineKind: 2 }), null);
  assert.ok(recoverLegacySilenceSave(fixture.afterState));
});

test("new-run Revenant cancellation says damage is canceled; legacy text remains byte exact", () => {
  // Deliberately unearned five-card combat fixtures isolate wording, not progression.
  for (const engineKind of [1, 2] as const) {
    let s: GameState | undefined;
    for (let seed = 1; seed <= 20; seed++) {
      const map = createGame(seed, 0, { engineKind });
      map.deck = ["silence+", "silence", "silence", "scour", "ironward"];
      const entered = accepted(map, { type: "travel", choice: "battle" });
      if (entered.enemies.some(e => e.cardId === "revenant")) { s = entered; break; }
    }
    assert.ok(s);
    const target = s.enemies.find(e => e.cardId === "revenant")!.uid;
    for (const [index, card] of ["silence+", "silence", "silence"].entries()) {
      const a: Action = { type: "play", index: s.hand.indexOf(card), target };
      const result = applyActionWithEvents(s, a);
      if (engineKind === 1)
        assert.deepEqual(result, v04.applyActionWithEvents(s as v04.GameState, a));
      s = result.state;
      assert.ok(validateState(s));
      const intent = s.enemies.find(e => e.uid === target)!.intent!;
      assert.equal(intent.damage, 0);
      assert.deepEqual(intent.summon, []);
      assert.equal(intent.label, engineKind === 2
        ? "Silenced · damage and reinforcements canceled"
        : "Spectral rend · ignores block · silenced (armor remains)");
      assert.equal(result.events.filter(e => e.type === "control").length, index === 0 ? 1 : 0);
    }
    assert.equal(s.energy, 0);
    const ended = applyActionWithEvents(s, { type: "endTurn" });
    assert.equal(ended.events.some(e => e.type === "ward" && e.target === target), false);
  }
});
