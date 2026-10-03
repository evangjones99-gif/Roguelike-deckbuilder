/** Actual legal-campaign search/replay; no state injection or proposed prices. */
import { createHash } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";
import { gzipSync } from "node:zlib";
import {
  applyAction,
  createGame,
  legalActions,
  validateState,
  CARDS,
  type GameState,
  type Action,
} from "../../src/engine";
import * as legacy from "../ml-policy-v0.2/engine";
import { chooseHeuristic } from "../../scripts/simulate";
const hash = (p: string) =>
  createHash("sha256").update(readFileSync(p)).digest("hex");
function decide(s: GameState): Action {
  const actions = legalActions(s),
    guard = s.enemies.find(
      (e) => e.cardId === "ironjaw" && e.intent!.label.includes("block"),
    );
  if (s.phase === "reward")
    return (
      actions.find((a) => a.type === "reward" && a.card === "silence") ??
      chooseHeuristic(s)
    );
  if (s.phase === "camp") {
    const index = s.deck.findIndex((id) => id === "silence");
    if (index >= 0 && s.hp > 24)
      return { type: "camp", choice: "train", index };
    return chooseHeuristic(s);
  }
  if (s.phase === "shop")
    return (
      actions.find((a) => a.type === "buy" && a.card === "silence") ??
      chooseHeuristic(s)
    );
  if (s.phase === "battle" && s.route[0] === "boss") {
    if (guard) {
      const silence = actions
        .filter(
          (a) =>
            a.type === "play" &&
            CARDS[s.hand[a.index]].effect === "control" &&
            a.target === guard.uid,
        )
        .sort(
          (a, b) =>
            CARDS[s.hand[(a as Extract<Action, { type: "play" }>).index]].cost -
            CARDS[s.hand[(b as Extract<Action, { type: "play" }>).index]].cost,
        )[0];
      if (silence) return silence;
      const survey = actions.find(
        (a) =>
          a.type === "play" &&
          CARDS[s.hand[a.index]].effect === "draw" &&
          s.energy > CARDS[s.hand[a.index]].cost,
      );
      if (survey) return survey;
      const price = actions.find(
        (a) =>
          a.type === "play" &&
          CARDS[s.hand[a.index]].effect === "energy" &&
          s.hp > 12,
      );
      if (price) return price;
    }
    // Preserve the boss while searching subsequent guard turns; protect/heal.
    const safe = actions.filter(
      (a) =>
        a.type === "play" &&
        [
          "block",
          "shelter",
          "hunterheal",
          "communion",
          "heal",
          "draw",
        ].includes(CARDS[s.hand[a.index]].effect ?? ""),
    );
    if (safe.length) {
      const relevant = safe
        .map((a) => ({ a, next: applyAction(s, a) }))
        .filter(
          ({ next }) =>
            next.hp > s.hp ||
            next.block > s.block ||
            next.hand.length > s.hand.length,
        );
      if (relevant.length) return relevant[0].a;
    }
    return { type: "endTurn" };
  }
  return chooseHeuristic(s);
}
const out = "reviews/solo-v0.3/silence-overflow-campaign.json";
let found: unknown;
for (let seed = 3; seed <= 30000 && !found; seed += 3) {
  let s = createGame(seed),
    old = legacy.createGame(seed),
    actions: Action[] = [],
    guards: unknown[] = [];
  for (let step = 0; step < 650 && legalActions(s).length; step++) {
    if (
      s.phase === "battle" &&
      s.route[0] === "boss" &&
      s.deck.filter((id) => id.replace("+", "") === "silence").length < 3
    )
      break;
    const action = decide(s);
    if (
      !legalActions(s).some((a) => JSON.stringify(a) === JSON.stringify(action))
    )
      throw Error("Not legal");
    const before = structuredClone(s);
    s = applyAction(s, action);
    old = legacy.applyAction(old, action);
    actions.push(action);
    if (s === before) throw Error("Rejected action");
    if (JSON.stringify(s) !== JSON.stringify(old))
      throw Error("Legacy replay differs");
    if (
      action.type === "play" &&
      CARDS[before.hand[action.index]].effect === "control" &&
      before.route[0] === "boss"
    )
      guards.push({
        acceptedActionNumber: actions.length,
        turn: before.turn,
        card: before.hand[action.index],
        energyBefore: before.energy,
        cost: CARDS[before.hand[action.index]].cost,
        labelLengthBefore: before.enemies[0].intent!.label.length,
        labelLengthAfter: s.enemies[0].intent!.label.length,
      });
    if (!validateState(s)) {
      if (!validateState(before)) throw Error("Before was not a valid save");
      found = {
        finding:
          "Three legal Silence casts during an Ironjaw guard append repeated status suffixes beyond save validator bound.",
        seed,
        difficulty: 0,
        acceptedActionCount: actions.length,
        firstInvalidAcceptedAction: action,
        validBefore: true,
        validAfter: false,
        phase: s.phase,
        floor: s.floor,
        turn: s.turn,
        energyBefore: before.energy,
        energyAfter: s.energy,
        playedCard: action.type === "play" ? before.hand[action.index] : null,
        deckSilenceCopies: s.deck.filter(
          (id) => id.replace("+", "") === "silence",
        ),
        guardCasts: guards,
        sourceHashes: {
          engine: hash("src/engine.ts"),
          content: hash("src/content.ts"),
          archivedEngine: hash("reviews/ml-policy-v0.2/engine.ts"),
          harness: hash("reviews/solo-v0.3/silence-overflow-reproduction.ts"),
        },
        actions,
        beforeState: before,
        afterState: s,
        method:
          "Every action came from actual legalActions; no save/health/deck/gold/RNG injection. Current and archived reducers yield byte-identical states throughout. The final reducer action is accepted although resulting save is invalid.",
      };
      break;
    }
  }
}
if (!found) throw Error("No reachable reproduction in searched range");
writeFileSync(out, JSON.stringify(found, null, 2));
writeFileSync(out + ".gz", gzipSync(JSON.stringify(found)));
const { actions, beforeState, afterState, ...summary } = found as Record<
  string,
  unknown
>;
console.log(JSON.stringify(summary, null, 2));
