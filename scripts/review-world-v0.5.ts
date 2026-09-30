/** Independent v0.5 audit. No runtime mutation, no virtual prices/world sampler. */
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFileSync,writeFileSync,mkdtempSync,existsSync} from 'node:fs';
import {execFileSync} from 'node:child_process';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {pathToFileURL} from 'node:url';
import {gzipSync,gunzipSync} from 'node:zlib';
import * as engine from '../src/engine';
import {applyAction,createGame,legalActions,validateState,CARDS,type GameState,type Action,type Unit} from '../src/engine';
import {BASE_CARD_IDS,RELICS,SHOP_PRICES,bossForSeed} from '../src/content';
import {worldOrder,worldRank,worldFormation} from '../src/world-rng';
import {chooseHeuristic} from './simulate';
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
const sha=(v:string|Buffer)=>createHash('sha256').update(v).digest('hex');
const digest=(f:string)=>sha(readFileSync(f));
const sourceFiles=['src/engine.ts','src/content.ts','src/world-rng.ts','scripts/review-world-v0.5.ts','scripts/solo-investigation-v0.3.ts','scripts/simulate.ts','reviews/gameplay-v0.5-engine-plan.json'];
const hashes=Object.fromEntries(sourceFiles.map(f=>[f,digest(f)]));
assert.equal(hashes['src/engine.ts'],'bfc9e61299d73a344569e54e4b3f3348009f4075560dc2f0fb057f5d8a4d296b');
assert.equal(hashes['src/world-rng.ts'],'c4ea7b2bb7fc3fa3f0497111dae923566159d2b4143f01b646cb688d3223c1da');
const plan=JSON.parse(readFileSync('reviews/gameplay-v0.5-engine-plan.json','utf8'));
const outputs=['reviews/gameplay-v0.5-engine-checks-r2.json','reviews/gameplay-v0.5-engine-summary-r2.json','reviews/gameplay-v0.5-engine-runs-r2.json.gz'];
for(const f of outputs)assert.equal(existsSync(f),false,'Never overwrite preserved evidence: '+f);
const dir=mkdtempSync(join(tmpdir(),'hollowpact-independent-v05-'));
const archive='releases/0.4.0/hollowpact-0.4.0-source.zip';
const archiveHashes:Record<string,string>={};
for(const name of ['engine','content']) {
  const bytes=execFileSync('unzip',['-p',archive,`src/${name}.ts`]);
  archiveHashes[name]=sha(bytes);writeFileSync(join(dir,name+'.ts'),bytes);
}
writeFileSync(join(dir,'package.json'),'{"type":"module"}');
const archived=await import(pathToFileURL(join(dir,'engine.ts')).href) as typeof engine;
assert.equal(archiveHashes.engine,'ee85f1400a9d02142aee1dd66f82722453f35930bbf2c0c229ad38e38a818d0d');
assert.equal(archiveHashes.content,hashes['src/content.ts']);
assert.equal(SHOP_PRICES.remove,35);
const checks:any={hashes,archive,archiveHash:digest(archive),archiveHashes,legacy:[],branches:[],classification:[],pureQueries:0};
const key=(a:Action)=>JSON.stringify(a);
function accepted(s:GameState,a:Action,purity=false) {
  assert.ok(legalActions(s).some(b=>key(a)===key(b)),'Illegal action '+key(a));
  const next=applyAction(s,a);assert.notEqual(next,s);assert.ok(validateState(next));
  if(purity){const before=JSON.stringify(s),result=engine.applyActionWithEvents(s,a);
    assert.equal(JSON.stringify(s),before);assert.deepEqual(result.state,next);
    assert.deepEqual(result,engine.applyActionWithEvents(JSON.parse(before),a));checks.pureQueries++;}
  return next;
}
function fight(s:GameState){for(let i=0;i<500&&s.phase==='battle';i++)s=accepted(s,chooseHeuristic(s),true);assert.equal(s.phase,'reward');return s;}
// 120 complete actual archive comparisons; no old fixture module trusted implicitly.
for(const [policy,seeds,difficulties] of [
 ['informed',Array.from({length:24},(_,i)=>7101+i),[0,1,2]],
 ['legal-random',Array.from({length:48},(_,i)=>7901+i),[null]],
] as const)for(const seed of seeds)for(const difficulty of difficulties){
  const d=difficulty??seed%3;let s=createGame(seed,d,{engineKind:1}),old=archived.createGame(seed,d),rng=seed,steps=0;
  for(;steps<1500&&legalActions(s).length;steps++){
    const actions=legalActions(s);rng=(Math.imul(rng,1664525)+1013904223)>>>0;
    const a=policy==='informed'?chooseHeuristic(s):actions[Math.floor(rng/4294967296*actions.length)];
    const before=JSON.stringify(s),result=engine.applyActionWithEvents(s,a),expected=archived.applyActionWithEvents(old,a);
    assert.equal(JSON.stringify(s),before);assert.deepEqual(result,expected);s=result.state;old=expected.state;
    assert.ok(validateState(s));assert.equal(s.schema,2);assert.equal(Object.hasOwn(s,'engineKind'),false);
  }
  assert.ok(['victory','defeat'].includes(s.phase));checks.legacy.push({seed,difficulty:d,policy,steps,phase:s.phase,stateHash:sha(JSON.stringify(s))});
}
const overflow=JSON.parse(gunzipSync(readFileSync('reviews/solo-v0.3/silence-overflow-campaign.json.gz')).toString());
let fixed=createGame(1989,0,{engineKind:1}),old=archived.createGame(1989,0);
for(const a of overflow.actions){const current=engine.applyActionWithEvents(fixed,a),previous=archived.applyActionWithEvents(old,a);assert.deepEqual(current,previous);fixed=current.state;old=previous.state;assert.ok(validateState(fixed));}
assert.equal(overflow.actions.length,119);
assert.deepEqual(engine.recoverLegacySilenceSave(overflow.afterState),archived.recoverLegacySilenceSave(overflow.afterState));
assert.deepEqual(engine.recoverLegacySilenceSave(overflow.afterState),fixed);
const cyclic=structuredClone(overflow.afterState);cyclic.extra=cyclic;
assert.equal(engine.recoverLegacySilenceSave(cyclic),null);assert.equal(engine.recoverLegacySilenceSave({...overflow.afterState,extra:1n}),null);
checks.silence={actions:119,stateHash:sha(JSON.stringify(fixed)),exactArchivedEventsAndStates:true,exactRecovery:true,cyclicAndBigIntRejected:true};
for(const schema of [0,1,2,3,4,'3',null])for(const marker of ['absent',undefined,0,1,2,3,'2',null]){
  const s:any={...createGame(1989),schema};if(marker==='absent')delete s.engineKind;else s.engineKind=marker;
  const expected=schema===2&&marker==='absent'||schema===3&&marker===2;
  assert.equal(validateState(s),expected);checks.classification.push({schema,marker:String(marker),accepted:expected});
}
assert.throws(()=>createGame(1,0,{engineKind:3 as 2}),RangeError);
for(const purpose of ['reward','shop','relic'] as const){
  const ids=purpose==='relic'?Object.keys(RELICS):BASE_CARD_IDS,context={seed:1989,node:4,kind:'elite'};
  const ranked=worldOrder(ids,purpose,context);assert.deepEqual(worldOrder([...ids].reverse(),purpose,context),ranked);
  assert.deepEqual(worldOrder(ids.filter(id=>!ranked.slice(0,2).includes(id)),purpose,context),ranked.slice(2));
}
const golden=JSON.parse(readFileSync('reviews/world-rng-v0.5/golden-vectors-r1.json','utf8'));
for(const g of golden.golden){const [,generation,seed,purpose,node,kind,identity]=g.key;assert.equal(generation,2);assert.equal(worldRank(purpose,{seed,node,kind},identity).toString(16).padStart(16,'0'),g.expected);}
const samples:any[]=[];
for(const seed of [0,1,1989,6501,28001,4294967295])for(const purpose of ['encounter','reward','shop','relic','battle-deck'])for(let node=1;node<=10;node++)for(const kind of ['battle','elite','shop'])for(const id of ['silence','resonance','cairnhound','grave-coin'])samples.push(['hollowpact',2,seed,purpose,node,kind,id]);
samples.push(['hollowpact',2,1989,'reward',1,'battle','unicode-🜏'],['hollowpact',2,1989,'a|b',1,'c','d'],['hollowpact',2,1989,'a',1,'b|c','d'],['hollowpact',2,1989,'reward',1,'battle','quoted-"-\\']);
const actual=samples.map(([, ,seed,purpose,node,kind,id])=>worldRank(purpose,{seed,node,kind},id).toString(16).padStart(16,'0'));
assert.equal(sha(JSON.stringify({samples,actual})),golden.broaderTupleDigest);
checks.golden={count:golden.golden.length+samples.length,hash:digest('reviews/world-rng-v0.5/golden-vectors-r1.json'),qualified:'Existing research Node/Chromium seven explicit +3604 tuple digest rechecked against actual runtime; not new browser execution.'};
const roster=(s:GameState)=>s.enemies.map(e=>({id:e.cardId,hp:e.hp,maxHp:e.maxHp,attack:e.attack,block:e.block,passive:e.passive}));
// Four genuinely earned reward arms, then real purchase/removal and a common elite.
for(let seed=6501;seed<=6512;seed++){
  const reward=fight(accepted(createGame(seed),{type:'travel',choice:'battle'},true));
  const arms=[...reward.rewards,null].map(card=>accepted(reward,{type:'reward',card},true));
  const battles=arms.map(s=>accepted(s,{type:'travel',choice:'battle'},true));
  for(const s of battles)assert.deepEqual(roster(s),roster(battles[0]));
  const post=battles.map(fight);for(const s of post)assert.deepEqual(s.rewards,post[0].rewards);
  const shops=post.map(s=>accepted(accepted(s,{type:'reward',card:null}),{type:'travel',choice:'shop'},true));
  for(const s of shops)assert.deepEqual(s.rewards,shops[0].rewards);
  const sculpted=shops.map((s,i)=>accepted(s,i===0?{type:'buy',card:s.rewards[0]}:{type:'remove',index:0},true));
  sculpted.forEach((s,i)=>assert.equal(s.rng,shops[i].rng));
  const elite=sculpted.map(s=>accepted(accepted(s,{type:'leave'}),{type:'travel',choice:'elite'},true));
  for(const s of elite)assert.deepEqual(roster(s),roster(elite[0]));
  const completed=elite.map(fight);for(const s of completed){assert.deepEqual(s.rewards,completed[0].rewards);assert.deepEqual(s.relics,completed[0].relics);}
  checks.branches.push({seed,kind:'earned-acquisition-and-shop-sculpture',arms:arms.length,initialRng:battles.map(s=>s.rng),postBattleRng:post.map(s=>s.rng),commonFormation:roster(elite[0]),commonOffers:completed[0].rewards,commonRelic:completed[0].relics});
}
for(let seed=6701;seed<=6712;seed++){
  const entered=accepted(createGame(seed),{type:'travel',choice:'battle'});
  const normal=fight(entered),extraDraw=fight(accepted(entered,{type:'endTurn'},true));
  assert.deepEqual(normal.rewards,extraDraw.rewards);
  let battle=accepted(normal,{type:'reward',card:null}),event=accepted(extraDraw,{type:'reward',card:null});
  battle=accepted(fight(accepted(battle,{type:'travel',choice:'battle'})),{type:'reward',card:null});
  event=accepted(accepted(event,{type:'travel',choice:'event'}),{type:'event',choice:'forage'});
  const a=accepted(battle,{type:'travel',choice:'shop'},true),b=accepted(event,{type:'travel',choice:'shop'},true);
  assert.deepEqual(a.rewards,b.rewards);
  const eliteA=accepted(accepted(a,{type:'leave'}),{type:'travel',choice:'elite'}),eliteB=accepted(accepted(b,{type:'leave'}),{type:'travel',choice:'elite'});
  assert.deepEqual(roster(eliteA),roster(eliteB));
  checks.branches.push({seed,kind:'earned-extra-draw-and-route',firstCombatRng:[normal.rng,extraDraw.rng],differingDrawPosition:normal.rng!==extraDraw.rng,shopRng:[a.rng,b.rng],commonShop:a.rewards,commonElite:roster(eliteA)});
}
writeFileSync(outputs[0],JSON.stringify(checks,null,2)+'\n');
console.log(JSON.stringify({stage:'acceptance',legacy:checks.legacy.length,earnedBranches:checks.branches.length,pureQueries:checks.pureQueries,golden:checks.golden.count,source:hashes['src/engine.ts']}));
type Policy='pack'|'strictsolo'|'spellhybrid'|'lean';type Arm='procure'|'skip-acquisition';
const modes:Record<Policy,Mode>={pack:'pack',strictsolo:'solo',spellhybrid:'widow-hybrid',lean:'lean-pack'};
const policies=plan.policies as Policy[],arms:Arm[]=['procure','skip-acquisition'];
function choose(s:GameState,policy:Policy,arm:Arm){
  const actions=legalActions(s).filter(a=>arm==='procure'||a.type!=='buy'&&(a.type!=='reward'||a.card===null));
  assert.ok(actions.length);let best=actions[0],bestScore=-Infinity;
  for(const a of actions){const score=progressionScore(s,a,modes[policy],'legal-remove-first');if(score>bestScore){best=a;bestScore=score;}}
  return best;
}
const records:any[]=[];
for(const engineKind of [1,2] as const)for(const policy of policies)for(const difficulty of [0,1,2])for(let seed=44101;seed<=44196;seed++)for(const arm of arms){
  let s=createGame(seed,difficulty,{engineKind}),steps=0,purchases=0,removals=0;const usage:Record<string,number>={},world:any[]=[];
  const actionsHash=createHash('sha256');
  for(;steps<plan.maximumAcceptedActionsPerRun&&legalActions(s).length;steps++){
    const a=choose(s,policy,arm),before=s;
    actionsHash.update(key(a)+'\n');
    if(a.type==='play')usage[s.hand[a.index]]=(usage[s.hand[a.index]]??0)+1;
    if(a.type==='buy')purchases++;if(a.type==='remove')removals++;
    s=accepted(s,a);
    if(a.type==='travel'&&['battle','elite','boss'].includes(a.choice)){
      world.push({node:s.floor,kind:a.choice,category:'formation',value:roster(s)});
      if(engineKind===2&&a.choice!=='boss')assert.deepEqual(s.enemies.map(e=>e.cardId),worldFormation({seed,node:s.floor,kind:a.choice}));
    }
    if(a.type==='travel'&&a.choice==='shop')world.push({node:s.floor,kind:'shop',category:'offers',value:s.rewards});
    if(before.phase==='battle'&&s.phase==='reward'){
      const kind=before.route[0];world.push({node:s.floor,kind,category:'offers',value:s.rewards});
      if(kind==='elite'&&s.relics.length>before.relics.length){
        const remaining=Object.keys(RELICS).filter(id=>!before.relics.includes(id));
        const added=s.relics.at(-1);world.push({node:s.floor,kind,category:'relic',value:added,eligible:remaining});
        if(engineKind===2)assert.equal(added,worldOrder(remaining,'relic',{seed,node:s.floor,kind})[0]);
      }
    }
    if(engineKind===2&&['reward','shop'].includes(s.phase)&&before.phase!==s.phase){
      const purpose=s.phase==='shop'?'shop':'reward',kind=s.phase==='shop'?'shop':before.route[0];
      assert.deepEqual(s.rewards,worldOrder(BASE_CARD_IDS,purpose,{seed,node:s.floor,kind}).slice(0,purpose==='shop'?5:3));
    }
  }
  assert.ok(['victory','defeat'].includes(s.phase),'Nonterminal holdout '+JSON.stringify({seed,difficulty,policy,arm,engineKind,steps}));
  records.push({seed,difficulty,policy,arm,engineKind,phase:s.phase,hp:s.hp,floor:s.floor,turns:s.stats.turns,steps,deck:s.deck,gold:s.gold,relics:s.relics,purchases,removals,usage,actionHash:actionsHash.digest('hex'),world});
  if(records.length%384===0)console.log(JSON.stringify({stage:'holdout',completed:records.length,planned:plan.plannedRunCount}));
}
assert.equal(records.length,plan.plannedRunCount);
const groups:any[]=[],pairs:any[]=[],worldSummary:any[]=[];
for(const engineKind of [1,2])for(const policy of policies)for(const difficulty of [0,1,2]){
  for(const arm of arms){const rows=records.filter(r=>r.engineKind===engineKind&&r.policy===policy&&r.difficulty===difficulty&&r.arm===arm);
    const mean=(name:string)=>Number((rows.reduce((n,r)=>n+r[name],0)/rows.length).toFixed(3));
    groups.push({engineKind,policy,difficulty,arm,n:rows.length,wins:rows.filter(r=>r.phase==='victory').length,meanHP:mean('hp'),meanTurns:mean('turns'),meanSteps:mean('steps'),meanPurchases:mean('purchases'),meanRemovals:mean('removals'),meanDeck:Number((rows.reduce((n,r)=>n+r.deck.length,0)/rows.length).toFixed(3))});
  }
  const rescued:number[]=[],newLosses:number[]=[],mismatchedSeeds:number[]=[];let common=0,mismatches=0,relicEligibleDifferences=0;
  for(let seed=44101;seed<=44196;seed++){
    const a=records.find(r=>r.engineKind===engineKind&&r.policy===policy&&r.difficulty===difficulty&&r.seed===seed&&r.arm==='procure');
    const b=records.find(r=>r.engineKind===engineKind&&r.policy===policy&&r.difficulty===difficulty&&r.seed===seed&&r.arm==='skip-acquisition');
    if(a.phase==='victory'&&b.phase==='defeat')rescued.push(seed);if(a.phase==='defeat'&&b.phase==='victory')newLosses.push(seed);
    const match=new Map(b.world.map((w:any)=>[`${w.node}/${w.kind}/${w.category}`,w]));let seedMismatch=false;
    for(const w of a.world){const other:any=match.get(`${w.node}/${w.kind}/${w.category}`);if(!other)continue;
      if(w.category==='relic'&&JSON.stringify(w.eligible)!==JSON.stringify(other.eligible)){relicEligibleDifferences++;continue;}
      common++;if(JSON.stringify(w.value)!==JSON.stringify(other.value)){mismatches++;seedMismatch=true;}
    }
    if(seedMismatch)mismatchedSeeds.push(seed);
  }
  if(engineKind===2)assert.equal(mismatches,0);
  pairs.push({engineKind,policy,difficulty,procurementRescues:rescued,procurementNewLosses:newLosses});
  worldSummary.push({engineKind,policy,difficulty,commonReachedWorldRecords:common,mismatches,mismatchedSeeds,relicEligibleDifferences});
}
const data=JSON.stringify({hashes,plan,records});writeFileSync(outputs[2],gzipSync(data));
const summary={hashes,planHash:hashes['reviews/gameplay-v0.5-engine-plan.json'],runs:records.length,validTerminal:records.length,groups,pairs,worldSummary,dataset:{path:outputs[2],rawSHA256:sha(data),gzipSHA256:digest(outputs[2]),lossless:true},acceptancePath:outputs[0]};
writeFileSync(outputs[1],JSON.stringify(summary,null,2)+'\n');console.log(JSON.stringify({stage:'finished',runs:records.length,dataset:summary.dataset}));
