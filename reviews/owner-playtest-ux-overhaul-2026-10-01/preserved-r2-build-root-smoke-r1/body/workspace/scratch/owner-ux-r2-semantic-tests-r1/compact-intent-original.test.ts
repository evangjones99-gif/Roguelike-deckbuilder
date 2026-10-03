/** Diagnostic reducer fixtures; these are not earned-play or human-fun evidence. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {createGame, applyAction, applyActionWithEvents, legalActions, validateState, CARDS, type GameState, type Unit, type Action} from '../src/engine';
import {ENEMIES} from '../src/content';
import {compactIntent} from '../src/compact-intent';

function battle(kind:1|2=2):GameState {
  const state=applyAction(createGame(121,0,{engineKind:kind}),{type:'travel',choice:'battle'});
  state.allies=[]; state.enemies=[]; state.turn=1; state.relics=[];
  return state;
}
function hostile(state:GameState,id:string,damage:number,target='hunter',summon?:string[]):Unit {
  const def=ENEMIES[id];
  const unit:Unit={...def,uid:`e${state.nextUid++}`,cardId:id,hp:def.hp,maxHp:def.hp,block:0,acted:false,intent:{damage,target,label:'Loaded diagnostic intent',...(summon?{summon}: {})}};
  state.enemies.push(unit);return unit;
}
function binding(state:GameState):Unit {
  const card=CARDS.cairnhound;
  const unit:Unit={uid:`a${state.nextUid++}`,cardId:card.id,name:card.name,species:card.species!,color:card.color,hp:card.hp!,maxHp:card.hp!,attack:card.attack!,block:0,acted:false};
  state.allies.push(unit);state.deck.push(card.id);return unit;
}
function resolve(state:GameState,action:Action={type:'endTurn'}) {
  assert.equal(validateState(state),true,'diagnostic input validates');
  assert.ok(legalActions(state).some(a=>JSON.stringify(a)===JSON.stringify(action)),'action is legal');
  const bytes=JSON.stringify(state);
  const result=applyActionWithEvents(state,action);
  assert.equal(JSON.stringify(state),bytes,'observing events does not mutate input');
  assert.deepEqual(result.state,applyAction(state,action),'traced and normal rules agree');
  assert.equal(validateState(result.state),true,'resolved state validates');
  return result;
}
function description(state:GameState,unit:Unit) {
  const bytes=JSON.stringify(state),text=compactIntent(state,unit);
  assert.equal(JSON.stringify(state),bytes);assert.ok(Object.isFrozen(text)&&Object.isFrozen(text.lines));
  assert.equal(text.essentialRows,text.lines.length);return text;
}

for(const kind of [1,2] as const) for(const [id,amount] of [['ironjaw',14],['raider',4],['cindermaw',10]] as const) {
 test(`schema kind${kind}: ${id} guard and actual Silence retain ${amount} armor`,()=>{
  const state=battle(kind),foe=hostile(state,id,0);foe.intent!.target=foe.uid;
  assert.ok(description(state,foe).lines.includes(`Guard ${amount}`));
  const ward=resolve(state).events.find(event=>event.type==='ward'&&event.source===foe.uid);
  assert.ok(ward&&ward.type==='ward');assert.equal(ward.amount,amount);
  state.draw.push(...state.hand);state.hand=['silence'];state.deck.push('silence');
  const cancelled=resolve(state,{type:'play',index:0,target:foe.uid}).state;
  const controlled=cancelled.enemies.find(unit=>unit.uid===foe.uid)!;
  const text=description(cancelled,controlled);assert.ok(text.lines.includes(`Guard ${amount}`));assert.ok(text.lines.includes('Silenced'));
  const events=resolve(cancelled).events;
  assert.ok(events.some(event=>event.type==='ward'&&event.source===foe.uid&&event.amount===amount));
  assert.ok(!events.some(event=>event.type==='hit'&&event.source===foe.uid));
 });
}
test('guard is absent in an attack phase after Silence',()=>{
 const state=battle();state.turn=2;const foe=hostile(state,'ironjaw',7);
 state.draw.push(...state.hand);state.hand=['silence'];state.deck.push('silence');
 const controlled=resolve(state,{type:'play',index:0,target:foe.uid}).state;
 assert.ok(description(controlled,controlled.enemies[0]).lines.includes('No damage'));
 assert.ok(!resolve(controlled).events.some(event=>(event.type==='ward'||event.type==='hit')&&event.source===foe.uid));
});
for(const id of ['revenant','thrall']) test(`${id} single target: summary agrees with actual block admission`,()=>{
 const state=battle(),ally=binding(state);ally.block=7;const foe=hostile(state,id,7,ally.uid);
 const text=description(state,foe);assert.ok(text.lines.includes('→ Binding 1'));assert.equal(text.lines.includes('Ignores block'),id==='revenant');
 const hit=resolve(state).events.find(event=>event.type==='hit'&&event.source===foe.uid);
 assert.ok(hit&&hit.type==='hit');assert.equal(hit.target,ally.uid);assert.equal(hit.blocked,id==='revenant'?0:7);assert.equal(hit.hpLost,id==='revenant'?7:0);
});
test('loaded revenant area damage uses block and hits every live target',()=>{
 const state=battle(),first=binding(state),second=binding(state);state.block=2;first.block=7;second.block=0;
 const foe=hostile(state,'revenant',7,'all'),text=description(state,foe);
 assert.ok(text.lines.includes('Hunter + all'));assert.ok(!text.lines.includes('Ignores block'));
 const hits=resolve(state).events.filter(event=>event.type==='hit'&&event.source===foe.uid);
 assert.deepEqual(hits.map(event=>event.target),['hunter',first.uid,second.uid]);
 assert.deepEqual(hits.map(event=>event.type==='hit'?event.blocked:null),[2,7,0]);
 assert.deepEqual(hits.map(event=>event.type==='hit'?event.hpLost:null),[5,0,7]);
});
test('marked Binding 2 dying first redirects a later bypass hit to hunter',()=>{
 const state=battle();binding(state);const marked=binding(state);marked.hp=1;state.block=7;
 hostile(state,'thrall',1,marked.uid);const revenant=hostile(state,'revenant',7,marked.uid);
 const text=description(state,revenant);assert.ok(text.lines.includes('→ Binding 2'));assert.match(text.fullText,/redirects/);
 const events=resolve(state).events,death=events.findIndex(event=>event.type==='death'&&event.target===marked.uid),hit=events.findIndex(event=>event.type==='hit'&&event.source===revenant.uid);
 assert.ok(death>=0&&hit>death);const actual=events[hit];assert.ok(actual.type==='hit');assert.equal(actual.target,'hunter');assert.equal(actual.blocked,0);assert.equal(actual.hpLost,7);
});
for(const count of [1,5,6]) test(`raise plan respects post-phase timing and cap with ${count} existing hostiles`,()=>{
 const state=battle(),raiser=hostile(state,'acolyte',0,'hunter',['thrall','thrall']);
 while(state.enemies.length<count)hostile(state,'thrall',1);
 const text=description(state,raiser);assert.ok(text.lines.includes('Raise 2 thralls'));assert.match(text.fullText,/after the enemy phase/);assert.match(text.fullText,/six-hostile limit/);
 const result=resolve(state),arrivals=result.events.filter(event=>event.type==='summon'&&event.side==='enemy');assert.equal(arrivals.length,Math.min(2,6-count));
 for(const arrival of arrivals){assert.equal(arrival.source,raiser.uid);assert.ok(!result.events.some(event=>event.type==='hit'&&event.source===arrival.target));}
 const lastHit=result.events.map(event=>event.type==='hit'&&event.kind==='enemy').lastIndexOf(true);
 assert.ok(result.events.findIndex(event=>event.type==='summon')<0||result.events.findIndex(event=>event.type==='summon')>lastHit);
});
test('fatal hunter phase suppresses planned reinforcements',()=>{
 const state=battle();state.hp=1;const raiser=hostile(state,'acolyte',0,'hunter',['thrall']);hostile(state,'thrall',1);
 assert.match(description(state,raiser).fullText,/hunter survives/);const result=resolve(state);
 assert.equal(result.state.phase,'defeat');assert.ok(!result.events.some(event=>event.type==='summon'));
});
test('structured loaded facts override misleading labels and formatter is pure',()=>{
 const state=battle(),foe=hostile(state,'revenant',7,'all',['thrall']);foe.intent!.label='Silenced';
 const text=description(state,foe);assert.ok(text.lines.includes('Hunter + all'));assert.ok(text.lines.includes('+ 1 thrall'));assert.ok(!text.lines.includes('No damage'));
 const result=resolve(state);assert.ok(result.events.some(event=>event.type==='hit'&&event.source===foe.uid));assert.ok(result.events.some(event=>event.type==='summon'&&event.source===foe.uid));
 const absent=battle(),target=hostile(absent,'thrall',3,'a99999');assert.ok(description(absent,target).lines.includes('→ Hunter'));assert.ok(resolve(absent).events.some(event=>event.type==='hit'&&event.target==='hunter'));
});
