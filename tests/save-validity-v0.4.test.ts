import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import {
  applyAction, applyActionWithEvents, createGame, legalActions,
  recoverLegacySilenceSave, validateState, type Action, type GameState,
} from "../src/engine";
import * as legacy from "../reviews/ml-policy-v0.2/engine";
import { chooseHeuristic } from "../scripts/simulate";

const fixture = JSON.parse(readFileSync(new URL(
  "../reviews/solo-v0.3/silence-overflow-campaign.json", import.meta.url,
), "utf8")) as {
  seed: number; difficulty: number; actions: Action[];
  beforeState: GameState; afterState: GameState;
};
const suffix = " · silenced (armor remains)";
// The compatibility exception is exclusively the repeated status text, including
// its later combat-log observation. Every other saved field remains compared.
function canonicalLabels(s: GameState): GameState {
  const copy = structuredClone(s);
  const clean = (label: string) =>
    label.replace(/(?: · silenced \(armor remains\)){2,}/g, suffix);
  for (const enemy of copy.enemies)
    if (enemy.intent) enemy.intent.label = clean(enemy.intent.label);
  copy.log = copy.log.map(clean);
  return copy;
}
function replay() {
  let current = createGame(fixture.seed, fixture.difficulty, { engineKind: 1 }),
    old = legacy.createGame(fixture.seed, fixture.difficulty);
  for (const [index, action] of fixture.actions.entries()) {
    assert.ok(legalActions(current).some(a => JSON.stringify(a) === JSON.stringify(action)));
    const input = JSON.stringify(current);
    const resolved = applyActionWithEvents(current, action);
    assert.equal(JSON.stringify(current), input);
    old = legacy.applyAction(old, action);
    current = resolved.state;
    assert.ok(validateState(current), `accepted action ${index + 1} invalid`);
    assert.deepEqual(current, canonicalLabels(old), `action ${index + 1}`);
    assert.deepEqual(applyAction(JSON.parse(input), action), current);
    assert.deepEqual(applyActionWithEvents(JSON.parse(input), action), resolved);
    if (index >= 116) {
      assert.equal(current.enemies[0].intent!.label.length, 62);
      assert.equal(resolved.events.filter(e => e.type === "control").length,
        index === 116 ? 1 : 0);
    }
  }
  return { current, old };
}

test("all 119 reachable campaign actions remain valid with unchanged mechanics and payments", () => {
  const { current, old } = replay();
  assert.equal(validateState(old), false);
  assert.equal(current.energy, 1);
  assert.deepEqual(current.deck.filter(id => id.startsWith("silence")),
    ["silence+", "silence", "silence"]);
  assert.equal(current.enemies[0].intent!.damage, 0);
  assert.deepEqual(current.enemies[0].intent!.summon, []);
  assert.equal(current.schema, 2);
});

test("guard armor, fresh intentions and serialized continuation match legacy mechanics", () => {
  let { current, old } = replay();
  const end = applyActionWithEvents(current, { type: "endTurn" });
  old = legacy.applyAction(old, { type: "endTurn" });
  current = end.state;
  assert.deepEqual(current, canonicalLabels(old));
  assert.equal(current.enemies[0].block, 14);
  assert.equal(current.enemies[0].intent!.label, "Iron cleaver");
  assert.ok(end.events.some(e => e.type === "ward" && e.amount === 14));
  for (let i = 0; i < 100 && legalActions(current).length; i++) {
    const action = chooseHeuristic(current);
    current = applyAction(JSON.parse(JSON.stringify(current)), action);
    old = legacy.applyAction(old, action);
    assert.ok(validateState(current));
    assert.deepEqual(current, canonicalLabels(old));
  }
  assert.equal(current.phase, "victory");
});

test("exact inherited overflow recovery is valid, detached and preserves the original bytes", () => {
  const original = JSON.stringify(fixture.afterState);
  const recovered = recoverLegacySilenceSave(fixture.afterState);
  assert.ok(recovered && validateState(recovered));
  assert.deepEqual(recovered, canonicalLabels(fixture.afterState));
  assert.equal(JSON.stringify(fixture.afterState), original);
  assert.deepEqual(recoverLegacySilenceSave(JSON.parse(original)), recovered);
  recovered.deck[0] = "scour";
  recovered.enemies[0].intent!.label = "Changed only detached result";
  assert.equal(JSON.stringify(fixture.afterState), original);
});

test("normal valid saves and unrelated corruption never enter recovery", () => {
  assert.equal(recoverLegacySilenceSave(createGame(1989)), null);
  assert.equal(recoverLegacySilenceSave(fixture.beforeState), null);
  const mutations: ((s: GameState) => void)[] = [
    s => { s.hp = -1; },
    s => { s.rng = 0; },
    s => { s.deck.push("scour"); },
    s => { s.enemies[0].intent!.damage = 1; },
    s => { s.enemies[0].intent!.target = "hunter"; },
    s => { s.enemies[0].intent!.summon = ["thrall"]; },
    s => { s.turn = 4; },
    s => { s.enemies[0].intent!.label = "Forged shield" + suffix.repeat(4); },
    s => { s.enemies[0].intent!.label += " junk"; },
    s => { s.enemies[0].intent!.label += suffix.repeat(400); },
    s => { s.enemies[0].cardId = "__proto__"; },
    s => { s.schema = 3 as 2; },
  ];
  for (const mutate of mutations) {
    const value = structuredClone(fixture.afterState);
    mutate(value);
    const original = JSON.stringify(value);
    assert.equal(recoverLegacySilenceSave(value), null);
    assert.equal(JSON.stringify(value), original);
  }
  for (const value of [null, undefined, [], {}, "save", 1,
    new Proxy({}, { getPrototypeOf() { throw Error("hostile"); } })])
    assert.equal(recoverLegacySilenceSave(value), null);
});

test("a valid legacy double suffix becomes canonical on the next paid Silence", () => {
  assert.ok(validateState(fixture.beforeState));
  const action = fixture.actions.at(-1)!;
  const result = applyActionWithEvents(fixture.beforeState, action);
  assert.ok(validateState(result.state));
  assert.equal(result.state.energy, fixture.beforeState.energy - 2);
  assert.equal(result.state.enemies[0].intent!.label.length, 62);
  const event = result.events.find(e => e.type === "control");
  assert.ok(event?.type === "control");
  assert.equal(event.before.label.length, 89);
  assert.equal(event.after.label.length, 62);
});
