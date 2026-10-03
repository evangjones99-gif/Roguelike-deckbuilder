/** Independent v0.5 audit. No runtime mutation, no virtual prices/world sampler. */
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFileSync,writeFileSync,mkdtempSync,existsSync} from 'node:fs';
import {execFileSync} from 'node:child_process';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {pathToFileURL} from 'node:url';
import {gzipSync,gunzipSync} from 'node:zlib';
import * as engine from '/workspace/Roguelike-deckbuilder/src/engine';
import {applyAction,createGame,legalActions,validateState,CARDS,type GameState,type Action,type Unit} from '/workspace/Roguelike-deckbuilder/src/engine';
import {BASE_CARD_IDS,RELICS,SHOP_PRICES,bossForSeed} from '/workspace/Roguelike-deckbuilder/src/content';
import {worldOrder,worldRank,worldFormation} from '/workspace/Roguelike-deckbuilder/src/world-rng';
import {chooseHeuristic} from '/workspace/Roguelike-deckbuilder/scripts/simulate.ts';
type Mode='solo'|'pack'|'widow-hybrid'|'lean-pack';
type Progression='legal-remove-first'|'legal-buy-first';
const base=(id:string)=>id.replace('+','');
// Copied evaluator only; original investigation's counterfactual wrappers excluded.
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
  if (mode === "widow-hybrid" && c.type === "summon" && c.species !== "spider")
    return -100;
  if (mode === "lean-pack" && c.species === "spider") return -100;
  let v =
    (mode === "solo" || mode === "widow-hybrid" ? soloValues : packValues)[
      base(id)
    ] ?? 20;
  if (mode === "widow-hybrid" && c.species === "spider") v = 110;
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
      if (mode === "widow-hybrid")
        return c.type === "summon" && c.species !== "spider" ? 180 + c.cost : 0;
      if (mode === "lean-pack")
        return c.species === "spider" ? 180 : c.effect === "heal" ? 50 : 0;
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

const hash=(v:string|Buffer)=>createHash('sha256').update(v).digest('hex');
const runs:any[]=[];
for(const [seed,policy] of [[44102,'lean'],[44110,'pack']] as const){
 let s=createGame(seed,2);const start=s,trace:any[]=[];
 for(let i=0;i<1500&&legalActions(s).length;i++){
  const actions=legalActions(s),mode:Mode=policy==='lean'?'lean-pack':'pack';
  const action=actions.reduce((best,a)=>progressionScore(s,a,mode,'legal-remove-first')>progressionScore(s,best,mode,'legal-remove-first')?a:best,actions[0]);
  const after=applyAction(s,action);assert.ok(validateState(after));
  trace.push({beforeHash:hash(JSON.stringify(s)),action,afterHash:hash(JSON.stringify(after)),phase:after.phase,floor:after.floor,hp:after.hp,played:action.type==='play'?s.hand[action.index]:null});s=after;
 }
 assert.ok(['victory','defeat'].includes(s.phase));runs.push({seed,difficulty:2,policy,engineKind:2,fresh:true,start,trace,phase:s.phase,hp:s.hp});
}
const oldRuns=JSON.parse(gunzipSync(readFileSync('reviews/gameplay-v0.4-browser-inputs.json.gz')).toString()),legacy=oldRuns.find((r:any)=>r.seed===6503);
let s=createGame(6503,2,{engineKind:1}),start:GameState|null=null;const trace:any[]=[];
for(const [i,t] of legacy.trace.entries()){
 for(const k of ['floor','phase','turn','hp','energy','hand','allies','enemies'] as const)assert.deepEqual(s[k],t[k]);
 if(i===70)start=s;
 const after=applyAction(s,t.action);assert.ok(validateState(after));
 if(i>=70)trace.push({beforeHash:hash(JSON.stringify(s)),action:t.action,afterHash:hash(JSON.stringify(after)),phase:after.phase,floor:after.floor,hp:after.hp,played:t.action.type==='play'?s.hand[t.action.index]:null});s=after;
}
assert.equal(s.phase,'victory');assert.equal(s.hp,41);runs.push({seed:6503,difficulty:2,policy:'preserved v0.2 Pack',engineKind:1,fresh:false,earnedPrefixActions:70,start,trace,phase:s.phase,hp:s.hp});
const out='reviews/gameplay-v0.5-runtime/campaign-inputs.json.gz';assert.equal(existsSync(out),false);
writeFileSync(out,gzipSync(JSON.stringify({engineHash:hash(readFileSync('src/engine.ts')),generatorHash:hash(readFileSync(import.meta.filename)),qualification:'Reference generated through legal engine actions; fresh policies copied from preserved review evaluator; legacy resumes after a70-action earned prefix of preserved actual campaign.',runs})));
console.log(JSON.stringify(runs.map(r=>({seed:r.seed,kind:r.engineKind,controls:r.trace.length,phase:r.phase,hp:r.hp}))));
