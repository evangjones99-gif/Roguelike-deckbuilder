/** Independent fixed predictions for public tactical consequences; unearned rosters are disclosed. */
import assert from 'node:assert/strict';
import { readFileSync, writeFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { createGame, applyAction, applyActionWithEvents, validateState, type GameState, type Unit, type Action } from '../src/engine';
import { ENEMIES } from '../src/content';
function battlefield(cards:string[]) {
 const map=createGame(45001,1);map.deck=cards;
 const s=applyAction(map,{type:'travel',choice:'battle'});
 s.hand=s.deck.slice();s.draw=[];s.discard=[];s.energy=12;return s;
}
function enemy(s:GameState,id:string,hp:number,block=0) {
 const d=ENEMIES[id];const e:Unit={...d,uid:'e'+s.nextUid++,cardId:id,hp,maxHp:Math.max(hp,d.hp),block,acted:false,intent:{target:'hunter',damage:d.attack,label:'Strike'}};s.enemies.push(e);return e;
}
function binding(s:GameState,id:string,hp:number) {
 const index=s.hand.indexOf(id);const result=applyAction(s,{type:'play',index});assert.notEqual(result,s);const u=result.allies.at(-1)!;u.hp=hp;return{state:result,unit:u};
}
const fixtures:{name:string;state:GameState;action:Action;expected:string[];after:GameState;events:ReturnType<typeof applyActionWithEvents>['events']}[]=[];
function record(name:string,state:GameState,action:Action,expected:string[],check:(after:GameState,events:ReturnType<typeof applyActionWithEvents>['events'])=>void){
 assert.ok(validateState(state),`Fixture ${name} invalid`);const before=JSON.stringify(state),r=applyActionWithEvents(state,action);
 assert.equal(JSON.stringify(state),before);assert.ok(validateState(r.state));check(r.state,r.events);
 fixtures.push({name,state:structuredClone(state),action,expected,after:r.state,events:r.events});
}
{
 let s=battlefield(['cairnhound','scour','silence','ironward','survey']);s.enemies=[];const foe=enemy(s,'raider',20,8);let r=binding(s,'cairnhound',1);s=r.state;const uid=r.unit.uid;
 record('blocked-lethal-retaliation',s,{type:'attack',unit:uid,target:foe.uid},['0 health damage','3 blocked','binding 1 takes 1 retaliation (lethal)'],(a,e)=>{assert.equal(a.enemies[0].hp,20);assert.equal(a.enemies[0].block,5);assert.equal(a.allies.length,0);assert.ok(e.some(x=>x.type==='death'&&x.target===uid));});
}
{
 let s=battlefield(['cairnhound','scour','silence','ironward','survey']);s.enemies=[];const foe=enemy(s,'ironjaw',2,1);let r=binding(s,'cairnhound',2);s=r.state;const uid=r.unit.uid;
 record('mutual-death-contract-cleared',s,{type:'attack',unit:uid,target:foe.uid},['2 health damage (lethal)','1 blocked','binding 1 takes 2 retaliation (lethal)','contract cleared'],(a,e)=>{assert.equal(a.phase,'reward');assert.equal(e.filter(x=>x.type==='death').length,2);});
}
{
 let s=battlefield(['fenstalker','scour','silence','ironward','survey']);s.enemies=[];const foe=enemy(s,'ironjaw',20,1);let r=binding(s,'fenstalker',1);s=r.state;const uid=r.unit.uid;
 record('recovery-before-retaliation',s,{type:'attack',unit:uid,target:foe.uid},['3 health damage','1 blocked','binding 1: restores 2 health','binding 1 takes 2 retaliation'],(a,e)=>{assert.equal(a.allies[0].hp,1);assert.equal(a.enemies[0].hp,17);assert.equal(e.filter(x=>x.type==='death').length,0);assert.ok(e.findIndex(x=>x.type==='heal')<e.findIndex(x=>x.type==='hit'&&x.kind==='retaliation'));});
}
{
 const s=battlefield(['scour','silence','ironward','survey','bloodprice']);s.enemies=[];const foe=enemy(s,'revenant',15,4);
 record('spell-resistance-and-block',s,{type:'play',index:s.hand.indexOf('scour'),target:foe.uid},['0 health damage','4 blocked'],(a,e)=>{assert.equal(a.enemies[0].hp,15);assert.equal(a.enemies[0].block,0);const h=e.find(x=>x.type==='hit');assert.ok(h?.type==='hit'&&h.damage===4);});
 s.hp=3;
 record('bloodprice-terminal-no-draw-leak',s,{type:'play',index:s.hand.indexOf('bloodprice')},['hunter loses 3 health','HUNTER DIES · campaign ends'],(a,e)=>{assert.equal(a.phase,'defeat');assert.equal(a.hp,0);assert.ok(e.some(x=>x.type==='death'&&x.target==='hunter'));});
}
{
 const s=battlefield(['silence','scour','ironward','survey','bloodprice']);s.enemies=[];const foe=enemy(s,'acolyte',22);foe.intent={target:'hunter',damage:0,label:'Raise 1 Bone Thrall',summon:['thrall']};
 record('silence-cancels-current-intent',s,{type:'play',index:0,target:foe.uid},['Silenced · damage and reinforcements canceled'],(a,e)=>{assert.equal(a.enemies[0].intent!.damage,0);assert.deepEqual(a.enemies[0].intent!.summon,[]);assert.deepEqual(e.map(x=>x.type),['control']);});
}
const drawA=structuredClone(fixtures.find(f=>f.name==='bloodprice-terminal-no-draw-leak')!.state);
drawA.hp=15;drawA.hand=['survey','scour'];drawA.draw=['ironward','silence','bloodprice'];drawA.rng=1;
const drawB=structuredClone(drawA);drawB.draw.reverse();drawB.rng=999;
const rewardA=structuredClone(fixtures.find(f=>f.name==='mutual-death-contract-cleared')!.state);rewardA.rng=1;
const rewardB=structuredClone(rewardA);rewardB.rng=999;
const rewardAction=fixtures.find(f=>f.name==='mutual-death-contract-cleared')!.action;
const privacyPairs=[{name:'hidden-draw-order',action:{type:'play',index:0} as Action,states:[drawA,drawB],futureField:'hand' as const},{name:'hidden-reward-sampling',action:rewardAction,states:[rewardA,rewardB],futureField:'rewards' as const}].map(pair=>{
 assert.ok(pair.states.every(validateState));const future=pair.states.map(s=>applyAction(s,pair.action)[pair.futureField]);assert.notDeepEqual(future[0],future[1]);return{...pair,future};
});
const choiceState=structuredClone(fixtures.find(f=>f.name==='blocked-lethal-retaliation')!.state);
const alternative=enemy(choiceState,'revenant',15);
const alternativeAction={type:'attack',unit:choiceState.allies[0].uid,target:alternative.uid} as Action;
const alternativeAfter=applyAction(choiceState,alternativeAction);assert.equal(alternativeAfter.allies[0].hp,1);assert.equal(alternativeAfter.enemies[1].hp,10);
const targetChoice={state:choiceState,firstTarget:choiceState.enemies[0].uid,alternativeTarget:alternative.uid,alternativeAction,alternativeAfter};
const result={method:'Independent literal public-consequence assertions against fixed, structurally valid unearned rosters. States are diagnostic fixtures, not complete legally earned campaigns. Future production browser checks will resume these disclosed saves and compare visible previews/actions.',engineSHA:createHash('sha256').update(readFileSync('src/engine.ts')).digest('hex'),fixtures,privacyPairs,targetChoice};
writeFileSync('reviews/gameplay-v0.4-preview-fixtures.json',JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({fixtureCount:fixtures.length,names:fixtures.map(x=>x.name),engineSHA:result.engineSHA}));
