/** Independent reviewer policy: deliberately does not import training/heuristic scripts. */
import { createHash } from 'node:crypto';
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { applyAction, createGame, legalActions, validateState, CARDS, type Action, type GameState } from '../src/engine';

type Policy = 'pack' | 'spells' | 'starter' | 'first-target' | 'safe-route' | 'bare-starter';
const policies: Policy[] = ['pack', 'spells', 'starter', 'first-target', 'safe-route', 'bare-starter'];
const rank: Record<string, number> = { wisp: 30, witch: 20, wolf: 10, briar: 8, sentinel: 3, crown: 1 };
const packValue: Record<string, number> = { rally: 90, communion: 90, willowdrake: 85, thunderrook: 80, thorns: 78, siphon: 70, moonmoth: 62, shelter: 60, recall: 58, lanternowl: 55, brookotter: 52, cinderfox: 50, stonehart: 45, reedkin: 45, insight: 40, bramblecat: 35, mossling: 30, mend: 20, ward: 10 };
const spellValue: Record<string, number> = { siphon: 95, thorns: 85, rally: 80, gust: 75, communion: 65, insight: 62, recall: 58, shelter: 50, spark: 40, ward: 28, kindle: 10, mend: 10 };
function value(card: string, p: Policy) {
  return (p === 'spells' ? spellValue[card] : packValue[card]) ?? 15;
}
function score(s: GameState, a: Action, p: Policy): number {
  if (a.type === 'travel') {
    const safe = p === 'safe-route';
    if (p === 'bare-starter') return ({ boss: 100, battle: 90, elite: 1, camp: 70, shop: s.floor === 4 ? 80 : 20, event: 5 } as Record<string, number>)[a.choice];
    return ({ boss: 100, elite: safe ? 1 : 90, battle: safe ? 50 : 80,
      event: safe ? 60 : 5, camp: 70, shop: s.floor === 4 ? 80 : 20 } as Record<string, number>)[a.choice];
  }
  if (a.type === 'reward') return (p === 'starter' || p === 'bare-starter') ? (a.card === null ? 100 : 0) : (a.card ? value(a.card,p) - Math.max(0,s.deck.length-16)*7 : 28);
  if (a.type === 'camp' && p === 'bare-starter') return a.choice === 'rest' ? 100 : -1;
  if (a.type === 'camp') return a.choice === 'rest' ? (s.hp < 35 ? 100 : 0) : 80;
  if (a.type === 'event') return a.choice === 'offering' && s.hp > 30 ? 100 : a.choice === 'forage' ? 80 : 0;
  if (a.type === 'buy') return (p === 'starter' || p === 'bare-starter') ? -1 : value(a.card,p) >= 50 && s.deck.length < 18 ? value(a.card,p) : -1;
  if (a.type === 'remove') return (p === 'starter' || p === 'bare-starter') ? -1 : s.deck[a.index] === 'mend' ? 35 : (s.deck[a.index] === 'ward' && s.deck.length > 13 ? 25 : -1);
  if (a.type === 'leave') return 1;
  if (a.type === 'endTurn') return 0;
  const e = 'target' in a ? s.enemies.find(e=>e.uid === a.target) : undefined;
  const targetRank = e ? (p === 'first-target' ? 30 - s.enemies.indexOf(e)*30 : rank[e.cardId] ?? 0) : 0;
  const defense = s.enemies.reduce((sum,e)=>sum + ((e.intent?.target === 'hunter' || e.intent?.target === 'all') && e.cardId !== 'wisp' ? e.intent.damage : 0),0) - s.block;
  if (a.type === 'attack') {
    const u = s.allies.find(u=>u.uid === a.unit)!;
    return 60 + Math.min(u.attack, e!.hp + e!.block)*2 + targetRank + (u.attack >= e!.hp+e!.block ? 100 : 0);
  }
  if (a.type !== 'play') return 0;
  const c = CARDS[s.hand[a.index]];
  const ally = s.allies.find(u=>u.uid === a.target);
  if (c.type === 'summon') return 150 + (c.attack ?? 0)*2 - c.cost*2;
  const v = c.value ?? 0;
  if (['damage','pack','siphon'].includes(c.effect!)) {
    const damage = v + (c.effect === 'pack' ? s.allies.length*2 : 0) + (s.relics.includes('moon-charm') ? 1 : 0);
    return 50 + targetRank + Math.min(damage,e!.hp+e!.block)*3/c.cost + (damage >= e!.hp+e!.block ? 100 : 0) + (c.effect === 'siphon' && s.hp < s.maxHp ? 15 : 0);
  }
  if (c.effect === 'rally') return s.allies.length ? 95 + s.allies.length*v*8 : -1;
  if (c.effect === 'ready') return ally?.acted ? 90 + ally.attack*5 : -1;
  if (c.effect === 'draw') return s.energy > c.cost ? 120 : -1;
  if (c.effect === 'energy') return s.energy < 4 && s.hp > 10 && s.hand.some(id=>CARDS[id].cost > s.energy) ? 130 : -1;
  if (c.effect === 'aoe') return 55 + s.enemies.reduce((n,e)=>n+Math.min(e.hp+e.block,v)*6,0)/c.cost;
  if (c.effect === 'block') return defense > 0 ? 45 + Math.min(defense,v)*4 : -1;
  if (c.effect === 'shelter') {
    const hits = s.allies.reduce((n,u)=>n+s.enemies.filter(e=>e.intent?.target === u.uid || e.intent?.target === 'all').length,0);
    return defense > 0 || hits ? 55 + Math.max(0,Math.min(defense,v))*4 + hits*8 : -1;
  }
  if (c.effect === 'heal') return ally && ally.maxHp > ally.hp ? 50 + Math.min(ally.maxHp-ally.hp,v)*5 : -1;
  if (c.effect === 'communion') return s.maxHp-s.hp > 0 && s.allies.length ? 65+Math.min(s.maxHp-s.hp,v*s.allies.length)*5 : -1;
  return -1;
}
function run(seed: number, difficulty: number, policy: Policy, keepTrace = false) {
  let s = createGame(seed,difficulty), steps=0, minHp=s.hp, rests=0, trains=0, purchases=0, removals=0, skips=0, wastedEnergy=0, hunterLoss=0;
  let battle: { floor:number; kind:string; foes:string[]; startHp:number; turn:number; endHp:number; maxTurn:number } | undefined;
  const battles: NonNullable<typeof battle>[]=[];
  const trace: any[]=[];
  for (;steps<3000;steps++) {
    const actions=legalActions(s);
    if (!actions.length) break;
    const a=actions.reduce((best,a)=>score(s,a,policy)>score(s,best,policy)?a:best,actions[0]);
    if (keepTrace) trace.push({ floor:s.floor, turn:s.turn, hp:s.hp, phase:s.phase, energy:s.energy, hand:s.hand.slice(), allies:s.allies.map(u=>({id:u.cardId,hp:u.hp,attack:u.attack,acted:u.acted})), enemies:s.enemies.map(e=>({id:e.cardId,hp:e.hp,block:e.block,intent:e.intent})), action:a });
    if (a.type==='endTurn') wastedEnergy+=s.energy;
    if (a.type==='camp') a.choice==='rest'?rests++:trains++;
    if (a.type==='buy') purchases++;
    if (a.type==='remove') removals++;
    if (a.type==='reward' && a.card===null) skips++;
    const prev=s;
    s=applyAction(s,a);
    if (s===prev) throw Error('Policy chose rejected action');
    if (!validateState(s)) throw Error('Invalid legal-action state at '+JSON.stringify({seed,difficulty,policy,a}));
    if (prev.phase==='battle') hunterLoss+=Math.max(0,prev.hp-s.hp);
    minHp=Math.min(minHp,s.hp);
    if (prev.phase!=='battle' && s.phase==='battle') battle={floor:s.floor,kind:s.route[0],foes:s.enemies.map(e=>e.cardId),startHp:s.hp,turn:s.turn,endHp:s.hp,maxTurn:s.turn};
    if (battle && prev.phase==='battle') { battle.endHp=s.hp; battle.maxTurn=Math.max(battle.maxTurn,prev.turn); if(s.phase!=='battle') { battles.push(battle); battle=undefined; } }
  }
  return { seed,difficulty,policy,phase:s.phase,hp:s.hp,minHp,hunterLoss,turns:s.stats.turns,steps,rests,trains,purchases,removals,skips,wastedEnergy,gold:s.gold,deck:s.deck,relics:s.relics,battles,...(keepTrace?{trace}:{}) };
}
const n = Math.max(1, Math.min(200, Number(process.argv[2])||48));
const runs = policies.flatMap(p=>[0,1,2].flatMap(d=>Array.from({length:n},(_,i)=>run(1001+i,d,p,i<2))));
const summary = policies.flatMap(policy=>[0,1,2].map(difficulty=>{
  const rs=runs.filter(r=>r.policy===policy && r.difficulty===difficulty);
  const avg=(k: keyof typeof rs[number])=>Number((rs.reduce((n,r)=>n+(typeof r[k]==='number'?r[k] as number:0),0)/rs.length).toFixed(2));
  return {policy,difficulty,seeds:n,wins:rs.filter(r=>r.phase==='victory').length,losses:rs.filter(r=>r.phase==='defeat').length,incomplete:rs.filter(r=>!['victory','defeat'].includes(r.phase)).length,meanHp:avg('hp'),meanMinHp:avg('minHp'),lowestMinHp:Math.min(...rs.map(r=>r.minHp)),meanHunterLoss:avg('hunterLoss'),meanTurns:avg('turns'),meanRests:avg('rests'),meanTrains:avg('trains'),meanPurchases:avg('purchases'),meanRemovals:avg('removals'),meanSkips:avg('skips'),meanGold:avg('gold')};
}));
const sourceHashes=Object.fromEntries(['src/engine.ts','src/content.ts','scripts/review-playtest.ts'].map(path=>[path,createHash('sha256').update(readFileSync(path)).digest('hex')]));
mkdirSync('reviews',{recursive:true});
writeFileSync('reviews/gameplay-v0.1-experiments.json',JSON.stringify({version:'0.1.0',method:'Independent deterministic agent policies through legalActions/applyAction; no humans and no browser assertions',sourceHashes,seedRange:[1001,1000+n],summary,runs},null,2));
console.log(JSON.stringify({sourceHashes,summary},null,2));
