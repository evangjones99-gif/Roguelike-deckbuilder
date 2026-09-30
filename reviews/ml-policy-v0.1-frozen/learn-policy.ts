/** Small deterministic evolutionary policy search. Synthetic outcomes are not a fun metric. */
import { createGame, applyAction, legalActions, CARDS, type GameState, type Action } from '../src/engine';
import { createHash } from 'node:crypto';
import { mkdirSync, writeFileSync, existsSync, readFileSync, copyFileSync } from 'node:fs';

const output = process.argv[2] ?? 'reviews/ml-policy';
if (existsSync(output + '/report.json')) throw new Error('Refusing to overwrite prior experiment; choose a fresh output directory.');
mkdirSync(output, { recursive: true });
const sourceHash = (p:string) => createHash('sha256').update(readFileSync(p)).digest('hex');
const initialHashes = ['src/engine.ts','src/content.ts','scripts/learn-policy.ts'].map(sourceHash);
for (const file of ['src/engine.ts','src/content.ts','scripts/learn-policy.ts']) copyFileSync(file,output+'/'+file.split('/').at(-1));
let rng = 38291;
function rand() { rng ^= rng << 13; rng ^= rng >>> 17; rng ^= rng << 5; return (rng >>> 0) / 4294967296; }
const sum = (s:GameState, field:'hp'|'attack') => s.allies.reduce((n,u)=>n+u[field],0);
const enemyHp = (s:GameState) => s.enemies.reduce((n,u)=>n+u.hp,0);
const incoming = (s:GameState) => s.enemies.reduce((n,u)=>n+(u.intent?.target==='hunter'||u.intent?.target==='all'?u.intent.damage:0),0);
const baseWeights = [2.8, 4.5, 2.2, 0.65, 0.9, 0.3, -0.8, 3];
function features(s:GameState,a:Action,n:GameState):number[] {
  const remainsBattle = n.phase==='battle';
  return [
    (enemyHp(s)-(remainsBattle?enemyHp(n):0))/10,
    (n.hp-s.hp)/10,
    remainsBattle?(sum(n,'attack')-sum(s,'attack'))/5:0,
    remainsBattle?(sum(n,'hp')-sum(s,'hp'))/15:0,
    remainsBattle?(Math.min(n.block,incoming(s))-Math.min(s.block,incoming(s)))/10:0,
    remainsBattle?(n.energy-s.energy)/5:0,
    a.type==='endTurn'?1:0,
    n.phase==='reward'||n.phase==='victory'?1:n.phase==='defeat'?-2:0,
  ];
}
function outside(s:GameState,actions:Action[]):Action {
  if (s.phase==='map') return actions.find(a=>a.type==='travel'&&a.choice==='camp') ?? actions.find(a=>a.type==='travel'&&a.choice==='battle') ?? actions[0];
  if (s.phase==='camp') return actions.find(a=>a.type==='camp'&&a.choice===(s.hp<s.maxHp-14?'rest':'train')) ?? actions[0];
  if (s.phase==='event') return actions.find(a=>a.type==='event'&&a.choice==='forage') ?? actions[0];
  if (s.phase==='shop') return actions.find(a=>a.type==='leave') ?? actions[0];
  if (s.phase==='reward') {
    if (s.deck.length>=19) return actions.find(a=>a.type==='reward'&&a.card===null)!;
    return actions.slice().sort((a,b)=>cardValue(b)-cardValue(a))[0];
  }
  return actions[0];
}
function cardValue(a:Action):number {
  if(a.type!=='reward'||a.card===null) return 0;
  const c=CARDS[a.card];
  return c.type==='summon'?(c.attack??0)*2+(c.hp??0)*0.25-c.cost*0.5:
    ({rally:15,communion:14,ready:13,pack:11,siphon:10,aoe:8,draw:7,block:4,damage:5,energy:1,heal:3,shelter:5}[c.effect as 'rally']??4);
}
function choose(s:GameState,w:number[],mode:'linear'|'random'):Action {
  const actions=legalActions(s);
  if(mode==='random') return actions[Math.floor(rand()*actions.length)];
  if(s.phase!=='battle') return outside(s,actions);
  let chosen=actions[0], best=-Infinity;
  for(const a of actions) {
    const n=applyAction(s,a), f=features(s,a,n);
    let score=f.reduce((v,x,i)=>v+x*w[i],0);
    if(a.type==='attack') score+=0.15; // Deterministic tie-break favoring free commands.
    if(score>best) {best=score;chosen=a;}
  }
  return chosen;
}
type Episode={seed:number;win:boolean;floor:number;hp:number;steps:number;turns:number;cards:number;damage:number;stalled:boolean;score:number};
function episode(seed:number,w:number[],mode:'linear'|'random'='linear'):Episode {
  let s=createGame(seed,1),steps=0;
  while(s.phase!=='victory'&&s.phase!=='defeat'&&steps<700) {
    const legal=legalActions(s);if(!legal.length) break;
    s=applyAction(s,choose(s,w,mode));steps++;
  }
  const win=s.phase==='victory';
  return {seed,win,floor:s.floor,hp:s.hp,steps,turns:s.stats.turns,cards:s.stats.cardsPlayed,damage:s.stats.damageDealt,stalled:s.phase!=='victory'&&s.phase!=='defeat',score:(win?100:0)+s.floor*3+s.hp*0.1-steps*0.002};
}
const trainSeeds=Array.from({length:8},(_,i)=>200+i);
const testSeeds=Array.from({length:32},(_,i)=>9000+i);
const mean=(e:Episode[])=>e.reduce((v,x)=>v+x.score,0)/e.length;
let learned=baseWeights.slice(), best=mean(trainSeeds.map(s=>episode(s,learned)));
const history:{generation:number;trainingScore:number;weights:number[]}[]=[{generation:0,trainingScore:best,weights:learned.slice()}];
for(let gen=1;gen<=6;gen++) {
  const center=learned.slice();
  for(let candidate=0;candidate<6;candidate++) {
    const w=center.map(x=>Math.max(-6,Math.min(8,x+(rand()*2-1)*(1.6/gen+0.2))));
    const score=mean(trainSeeds.map(s=>episode(s,w)));
    if(score>best) {best=score;learned=w;}
  }
  history.push({generation:gen,trainingScore:best,weights:learned.slice()});
  console.log(`Generation ${gen}: training score ${best.toFixed(3)}`);
}
// Freeze policy before touching disjoint held-out seeds.
writeFileSync(output+'/policy.json',JSON.stringify({kind:'linear-transition-policy',method:'seeded evolutionary search',features:['enemyHpReduction','hunterHpChange','companionAttackChange','companionHpChange','effectiveHunterBlockChange','energyChange','endTurn','terminalProgress'],weights:learned,trainingSeeds:trainSeeds,randomSeed:38291},null,2)+'\n');
const results={ random:testSeeds.map(s=>episode(s,baseWeights,'random')), heuristic:testSeeds.map(s=>episode(s,baseWeights)), learned:testSeeds.map(s=>episode(s,learned)) };
const summaries=Object.fromEntries(Object.entries(results).map(([name,episodes])=>[name,{episodes:episodes.length,wins:episodes.filter(x=>x.win).length,winRate:episodes.filter(x=>x.win).length/episodes.length,meanFloor:episodes.reduce((n,x)=>n+x.floor,0)/episodes.length,meanSteps:episodes.reduce((n,x)=>n+x.steps,0)/episodes.length,meanTurns:episodes.reduce((n,x)=>n+x.turns,0)/episodes.length,stalled:episodes.filter(x=>x.stalled).length}]));
const bytes=JSON.stringify(results,null,2)+'\n';
if (['src/engine.ts','src/content.ts','scripts/learn-policy.ts'].some((p,i)=>sourceHash(p)!==initialHashes[i])) throw new Error('Source changed during experiment; preserve this incomplete directory and rerun against frozen source.');
writeFileSync(output+'/episodes.json',bytes);
const report={method:'Evolutionary search of a linear action policy over complete synthetic runs. Reward favors completion, progress and survival, not enjoyment.',engineSha256:createHash('sha256').update(readFileSync('src/engine.ts')).digest('hex'),contentSha256:createHash('sha256').update(readFileSync('src/content.ts')).digest('hex'),scriptSha256:createHash('sha256').update(readFileSync('scripts/learn-policy.ts')).digest('hex'),datasetSha256:createHash('sha256').update(bytes).digest('hex'),trainSeeds,testSeeds,history,summaries,limitations:['32 held-out seeds, one difficulty, one starting deck; limited coverage.','Random policy is deliberately weak and not a human comparator.','Policy search can exploit mechanics; inspect outcomes rather than maximizing win rate alone.','No human feedback, preference prediction or proof of fun.','Outcome comparison does not authorize automatic rules changes.']};
writeFileSync(output+'/report.json',JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(summaries,null,2));
