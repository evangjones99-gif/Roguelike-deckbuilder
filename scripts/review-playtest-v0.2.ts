/** Independent v0.2 reviewer: no imports from existing heuristic or ML scripts. */
import { createHash } from 'node:crypto';
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { applyAction, createGame, legalActions, validateState, CARDS, type Action, type GameState } from '../src/engine';
import { bossForSeed } from '../src/content';

type Policy = 'pack' | 'widow-spells' | 'solo-attempt' | 'starter' | 'front-focused' | 'no-counter' | 'bare-starter' | 'crypt' | 'boss-aware';
const policies: Policy[] = ['pack','widow-spells','solo-attempt','starter','front-focused','no-counter','bare-starter','crypt','boss-aware'];
const packValues: Record<string,number> = { gravehound:75,fenraker:75,fenstalker:60,ossuarycolossus:70,briarcolossus:55,cairnhound:70,ashwidow:60,emberwidow:70,edict:80,killcommand:72,gravetithe:80,survey:70,aegis:65,harpoon:80,covenant:80,sunder:75,silence:75,resonance:45,draught:65,sutures:38,ironward:30,witchfire:50,scour:35,bloodprice:15 };
const spellValues: Record<string,number> = { ashwidow:90,emberwidow:95,gravetithe:90,resonance:85,survey:90,silence:80,sunder:85,draught:80,witchfire:65,harpoon:65,scour:58,ironward:45,aegis:50,bloodprice:45,edict:20,sutures:30 };
const base=(id:string)=>id.replace('+','');
function acquisition(s:GameState,id:string,p:Policy) {
  if(p==='no-counter'&&['control','shred'].includes(CARDS[id].effect??'')) return -100;
  if(p==='solo-attempt') return CARDS[id].type==='summon'?-100:(({resonance:110,gravetithe:100,survey:95,silence:90,sunder:85,draught:95,scour:70,ironward:70,witchfire:60,bloodprice:55} as Record<string,number>)[base(id)]??-10);
  let v=(p==='widow-spells'?spellValues:packValues)[base(id)]??25;
  if(p==='boss-aware') {
    const boss=bossForSeed(s.seed);
    const focus:Record<string,number>=boss==='cantor'?{silence:35,witchfire:28,aegis:20,covenant:15,killcommand:12,edict:-20}:boss==='ironjaw'?{sunder:30,killcommand:15,gravetithe:10}: {aegis:30,ossuarycolossus:20,fenraker:18,draught:15,silence:18};
    v+=focus[base(id)]??0;
  }
  return v-Math.max(0,s.deck.length-16)*6;
}
function threatening(s:GameState,e:GameState['enemies'][number]) {
  if(!e.intent) return 0;
  const i=e.intent;
  const hunter=i.target==='hunter'||i.target==='all';
  const livingTarget=s.allies.find(u=>u.uid===i.target);
  const hunterDamage=hunter||(!livingTarget&&i.damage>0)?Math.max(0,i.damage-(e.cardId==='revenant'?0:s.block)):0;
  const allyDamage=i.target==='all'?s.allies.reduce((n,u)=>n+Math.min(u.hp,Math.max(0,i.damage-u.block)),0):livingTarget?Math.min(livingTarget.hp,Math.max(0,i.damage-livingTarget.block)):0;
  return hunterDamage*5+allyDamage*1.5+(i.summon?.length??0)*18+(hunterDamage>=s.hp&&hunterDamage>0?200:0);
}
function score(s:GameState,a:Action,p:Policy):number {
  if(a.type==='travel') {
    if(p==='solo-attempt') return ({boss:100,event:70,battle:65,elite:1,shop:80,camp:10} as Record<string,number>)[a.choice];
    if(p==='bare-starter') return ({boss:100,battle:90,elite:1,camp:70,shop:s.floor===4?80:20,event:5} as Record<string,number>)[a.choice];
    if(p==='crypt') return ({boss:100,event:100,camp:70,shop:30,battle:80,elite:s.hp>38?85:10} as Record<string,number>)[a.choice];
    return ({boss:100,battle:70,elite:90,camp:80,shop:s.floor===4?90:20,event:5} as Record<string,number>)[a.choice];
  }
  if(a.type==='reward') return p==='starter'||p==='bare-starter'?(a.card===null?100:-1):a.card?acquisition(s,a.card,p):35;
  if(a.type==='camp') {
    if(p==='bare-starter') return a.choice==='rest'?100:-1;
    if(a.choice==='rest') return s.hp<39?150:0;
    const id=s.deck[a.index!], c=CARDS[id];
    if(p==='no-counter'&&['control','shred'].includes(c.effect??'')) return -1;
    return (p==='boss-aware'?Math.max(0,acquisition(s,id,p)-60)*0.8:0)+50+(base(id)==='silence'?50:base(id)==='edict'?50:base(id)==='survey'?35:base(id)==='resonance'?30:c.species==='hound'?25:15)+(p==='widow-spells'&&(c.effect==='damage'||c.effect==='siphon'||c.species==='spider')?20:0);
  }
  if(a.type==='event') {
    if(a.choice==='bargain') return s.hp<42?130:10;
    if(a.choice==='offering') return p==='solo-attempt'||p==='widow-spells'? (s.hp>27?110:-1):s.hp>48?90:0;
    if(a.choice==='purge') return p==='crypt'&&s.hp>38&&s.deck.length>14?95:p==='solo-attempt'?-1:5;
    return a.choice==='forage'?75:0;
  }
  if(a.type==='buy') {
    if(p==='starter'||p==='bare-starter') return -1;
    const v=acquisition(s,a.card,p);
    return v>=60&&s.deck.length<18?v:-1;
  }
  if(a.type==='remove') {
    if(p==='starter'||p==='bare-starter') return -1;
    const c=CARDS[s.deck[a.index]];
    if(p==='solo-attempt') return c.type==='summon'?90+(c.cost>1?10:0):c.effect==='heal'||c.effect==='shred'?45:-1;
    return c.effect==='heal'?45:c.effect==='block'&&s.deck.length>14?38:-1;
  }
  if(a.type==='leave') return 1;
  if(a.type==='endTurn') return 0;
  const e='target'in a?s.enemies.find(e=>e.uid===a.target):undefined;
  const order=e?(p==='front-focused'?30-s.enemies.indexOf(e)*30:({revenant:30,acolyte:22,cantor:16,brood:12,thrall:8,raider:6,ironjaw:4,cindermaw:4} as Record<string,number>)[e.cardId]??0):0;
  if(a.type==='attack') {
    const u=s.allies.find(u=>u.uid===a.unit)!;
    const damage=u.attack+(u.species==='hound'&&e!.block===0?2:0), recoil=e!.block>0&&(e!.cardId==='raider'||e!.cardId==='ironjaw')?(e!.cardId==='ironjaw'?2:1):0;
    return 65+order+Math.min(damage,e!.hp+e!.block)*3+(damage>=e!.hp+e!.block?95+threatening(s,e!):0)+(u.species==='colossus'?6:0)-(p==='no-counter'?0:recoil*(u.hp<=recoil?80:5));
  }
  if(a.type!=='play') return 0;
  const c=CARDS[s.hand[a.index]],v=c.value??0,ally=s.allies.find(u=>u.uid===a.target);
  if(c.type==='summon') {
    if(p==='solo-attempt') return -1;
    return 135+(c.attack??0)*3-c.cost*3+(p==='widow-spells'&&c.species==='spider'?20:0);
  }
  if(['damage','shred','pack','solo','siphon'].includes(c.effect!)) {
    if(p==='no-counter'&&c.effect==='shred') return -1;
    const amp=s.allies.filter(u=>u.species==='spider').length*2+(s.relics.includes('moon-charm')?1:0)-(e!.cardId==='revenant'?2:0);
    const damage=v+amp+(c.effect==='pack'?s.allies.length*2:0)+(c.effect==='solo'&&s.allies.length===0?4:0);
    const block=c.effect==='shred'?0:e!.block;
    return 45+order+Math.min(damage,e!.hp+block)*3/c.cost+(damage>=e!.hp+block?95+threatening(s,e!):0)+(c.effect==='shred'?e!.block*5:0)+(c.effect==='siphon'&&s.hp<s.maxHp?18:0);
  }
  if(c.effect==='control') return p==='no-counter'||!e!.intent?-1:threatening(s,e!)>0?45+threatening(s,e!):-1;
  if(c.effect==='rally') return s.allies.length?60+s.allies.length*v*7:-1;
  if(c.effect==='ready') return ally?.acted?95+ally.attack*4:-1;
  if(c.effect==='draw') return s.energy>c.cost?115:-1;
  if(c.effect==='energy') return s.hp>15&&s.energy<3&&s.hand.some(id=>CARDS[id].cost>s.energy)?120:-1;
  if(c.effect==='aoe') return 45+s.enemies.reduce((n,e)=>n+Math.min(e.hp+e.block,v)*4,0);
  const danger=s.enemies.reduce((n,e)=>n+((e.intent?.target==='hunter'||e.intent?.target==='all'||(e.intent?.target?.startsWith('a')&&!s.allies.some(u=>u.uid===e.intent?.target)))&&e.cardId!=='revenant'?e.intent!.damage:0),0)-s.block;
  if(c.effect==='block') return danger>0?55+Math.min(danger,v)*5+(danger>=s.hp?150:0):-1;
  if(c.effect==='shelter') {
    const hits=s.allies.reduce((n,u)=>n+s.enemies.filter(e=>e.intent?.target===u.uid||e.intent?.target==='all').length,0);
    return danger>0||hits?55+Math.max(0,Math.min(danger,v))*5+hits*10+(danger>=s.hp?150:0):-1;
  }
  if(c.effect==='heal') return ally&&ally.hp<ally.maxHp?45+Math.min(ally.maxHp-ally.hp,v)*5:-1;
  if(c.effect==='communion') return s.hp<s.maxHp&&s.allies.length?65+Math.min(s.maxHp-s.hp,v*s.allies.length)*6:-1;
  if(c.effect==='hunterheal') return s.hp<s.maxHp?65+Math.min(s.maxHp-s.hp,v)*6:-1;
  return -1;
}
function run(seed:number,difficulty:number,policy:Policy,cohort:string,keepTrace:boolean) {
  let s=createGame(seed,difficulty),steps=0,minHp=s.hp,rests=0,hunterLoss=0;
  const upgrades:string[]=[],events:string[]=[],purchases:string[]=[],removals:string[]=[],rewards:(string|null)[]=[],cardsUsed:Record<string,number>={},trace:unknown[]=[],encounters:unknown[]=[];
  let battle:{floor:number;kind:string;foes:string[];startHp:number;endHp:number;maxTurn:number;raised:number}|undefined;
  for(;steps<3000;steps++) {
    const actions=legalActions(s);if(!actions.length)break;
    const a=actions.reduce((best,a)=>score(s,a,policy)>score(s,best,policy)?a:best,actions[0]);
    if(keepTrace)trace.push({floor:s.floor,phase:s.phase,turn:s.turn,hp:s.hp,energy:s.energy,hand:s.hand,allies:s.allies,enemies:s.enemies,action:a});
    if(a.type==='camp') a.choice==='rest'?rests++:upgrades.push(s.deck[a.index!]);
    if(a.type==='event')events.push(a.choice);
    if(a.type==='buy')purchases.push(a.card);
    if(a.type==='remove')removals.push(s.deck[a.index]);
    if(a.type==='reward')rewards.push(a.card);
    if(a.type==='play')cardsUsed[base(s.hand[a.index])]=(cardsUsed[base(s.hand[a.index])]??0)+1;
    const prev=s;s=applyAction(s,a);
    if(s===prev)throw Error('Rejected action '+JSON.stringify({seed,difficulty,policy,a}));
    if(!validateState(s))throw Error('Invalid state '+JSON.stringify({seed,difficulty,policy,a}));
    minHp=Math.min(minHp,s.hp);if(prev.phase==='battle')hunterLoss+=Math.max(0,prev.hp-s.hp);
    if(prev.phase!=='battle'&&s.phase==='battle')battle={floor:s.floor,kind:s.route[0],foes:s.enemies.map(e=>e.cardId),startHp:s.hp,endHp:s.hp,maxTurn:1,raised:0};
    if(battle&&prev.phase==='battle') {battle.endHp=s.hp;battle.maxTurn=Math.max(battle.maxTurn,prev.turn);battle.raised+=s.enemies.filter(e=>!prev.enemies.some(p=>p.uid===e.uid)).length;if(s.phase!=='battle'){encounters.push(battle);battle=undefined;}}
  }
  return {seed,difficulty,policy,cohort,boss:bossForSeed(seed),phase:s.phase,hp:s.hp,minHp,hunterLoss,turns:s.stats.turns,steps,rests,upgrades,events,purchases,removals,rewards,gold:s.gold,deck:s.deck,relics:s.relics,cardsUsed,encounters,...(keepTrace?{trace}:{})};
}
const n=Math.max(3,Math.min(120,Number(process.argv[2])||48));
const quarryOnly=process.argv[3]==='quarry';
const activePolicies:Policy[]=quarryOnly?['pack','boss-aware']:policies;
const difficulties=quarryOnly?[2]:[0,1,2];
const seedSets=quarryOnly?[{cohort:'quarry-holdout',start:8001,count:n}]:[{cohort:'fresh',start:6501,count:n},{cohort:'regression',start:1001,count:12}];
const runs=seedSets.flatMap(({cohort,start,count})=>activePolicies.flatMap(policy=>difficulties.flatMap(d=>Array.from({length:count},(_,i)=>run(start+i,d,policy,cohort,i<3)))));
const summary=seedSets.flatMap(({cohort})=>activePolicies.flatMap(policy=>difficulties.map(difficulty=>{
  const rs=runs.filter(r=>r.cohort===cohort&&r.policy===policy&&r.difficulty===difficulty);
  const avg=(f:(r:typeof rs[number])=>number)=>Number((rs.reduce((n,r)=>n+f(r),0)/rs.length).toFixed(2));
  const frequency=(field:'upgrades'|'events'|'purchases'|'removals')=>rs.flatMap(r=>r[field]).reduce<Record<string,number>>((m,id)=>(m[id]=(m[id]??0)+1,m),{});
  return {cohort,policy,difficulty,n:rs.length,wins:rs.filter(r=>r.phase==='victory').length,defeats:rs.filter(r=>r.phase==='defeat').length,incomplete:rs.filter(r=>!['victory','defeat'].includes(r.phase)).length,meanHp:avg(r=>r.hp),meanMinHp:avg(r=>r.minHp),lowestHp:Math.min(...rs.map(r=>r.minHp)),meanTurns:avg(r=>r.turns),meanRests:avg(r=>r.rests),meanGold:avg(r=>r.gold),meanRewardSkips:avg(r=>r.rewards.filter(c=>c===null).length),upgrades:frequency('upgrades'),events:frequency('events'),purchases:frequency('purchases'),removals:frequency('removals'),bosses:Object.fromEntries(['ironjaw','cantor','cindermaw'].map(b=>[b,{n:rs.filter(r=>r.boss===b).length,wins:rs.filter(r=>r.boss===b&&r.phase==='victory').length}]))};
})));
const sourceHashes=Object.fromEntries(['src/engine.ts','src/content.ts','scripts/review-playtest-v0.2.ts'].map(p=>[p,createHash('sha256').update(readFileSync(p)).digest('hex')]));
mkdirSync('reviews',{recursive:true});
writeFileSync(quarryOnly?'reviews/gameplay-v0.2-quarry-holdout.json':'reviews/gameplay-v0.2-experiments.json',JSON.stringify({version:'0.2.0',method:'Independent automatic deterministic legal-action policies; no human enjoyment claim',sourceHashes,seedSets,summary,runs},null,2));
console.log(JSON.stringify({sourceHashes,summary},null,2));
