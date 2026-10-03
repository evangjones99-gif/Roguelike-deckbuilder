import test from 'node:test';
import assert from 'node:assert/strict';
import { applyAction, applyActionWithEvents, createGame, legalActions, validateState, type GameState } from '../src/engine';
import { hunterEventCues, hunterGeometry, hunterPose, observeHunter } from '../src/hunter-presence';

function fixture(cards: string[], hp = 65) {
  const map = createGame(7803);map.deck=cards.slice();map.hp=hp;
  const state=applyAction(map,{type:'travel',choice:'battle'});
  assert.ok(validateState(state));return state;
}
function resolve(state: GameState,id:string,target?:string) {
  return applyActionWithEvents(state,{type:'play',index:state.hand.indexOf(id),...(target?{target}:{})});
}
test('actual bind, ward, healing, control, rally and self-injury produce distinct observer cues',()=>{
  let s=fixture(['cairnhound','ironward','sutures','silence','edict'],42);
  const bind=resolve(s,'cairnhound');assert.ok(validateState(bind.state));
  assert.equal(hunterEventCues(bind.events,0).filter(e=>e.kind==='bind').length,1);
  s=bind.state;
  const ward=resolve(s,'ironward');assert.ok(hunterEventCues(ward.events,0).some(e=>e.kind==='ward'));
  const healer=fixture(['gravetithe','ironward','scour','silence','edict'],42);
  const heal=resolve(healer,'gravetithe',healer.enemies[0].uid);assert.ok(hunterEventCues(heal.events,0).some(e=>e.kind==='heal'));
  const control=resolve(s,'silence',s.enemies[0].uid);
  assert.ok(control.events.some(e=>e.type==='control'));
  assert.ok(hunterEventCues(control.events,0).every(e=>e.kind==='ritual'));
  const rally=resolve(s,'edict');assert.ok(rally.events.some(e=>e.type==='buff'));
  assert.ok(hunterEventCues(rally.events,0).every(e=>e.kind==='ritual'));
  const blood=resolve(fixture(['bloodprice','scour','ironward','sutures','silence']),'bloodprice');
  assert.ok(hunterEventCues(blood.events,0).some(e=>e.kind==='reaction'));
  assert.ok(!hunterEventCues(blood.events,0).some(e=>e.kind==='ritual'));
});
test('fully blocked actual hit braces; lethal actual trace falls at its executed impact only',()=>{
  let s=fixture(['ironward+','scour','sutures','silence','edict']);
  s=resolve(s,'ironward+').state;
  let result=applyActionWithEvents(s,{type:'endTurn'});
  assert.ok(result.events.some(e=>e.type==='hit'&&e.target==='hunter'&&e.hpLost===0&&e.blocked>0));
  assert.ok(hunterEventCues(result.events,0).some(e=>e.kind==='brace'));
  s=fixture(['scour','sutures','silence','edict','ironward'],1);
  result=applyActionWithEvents(s,{type:'endTurn'});
  assert.equal(result.state.phase,'defeat');
  const h=observeHunter(result.state);h.cues=hunterEventCues(result.events,0);
  const death=h.cues.find(c=>c.kind==='death');assert.ok(death);
  assert.notEqual(hunterPose(h,death.start-.001),'death');
  assert.equal(hunterPose(h,death.start+.001),'death');
  assert.equal(hunterPose(observeHunter(result.state),0),'death');
});
test('observation never mutates canonical state, UID allocation, RNG, event snapshots or legal actions',()=>{
  let accepted=0;
  for (let seed=7811;seed<=7818;seed++) {
    let s=createGame(seed,seed%3);let h=observeHunter(s),r=seed;
    for(let n=0;n<300&&legalActions(s).length;n++) {
      const original=JSON.stringify(s), legal=JSON.stringify(legalActions(s));
      h=observeHunter(s,h);hunterGeometry(1024,360);hunterPose(h,n);
      assert.equal(JSON.stringify(s),original);assert.equal(JSON.stringify(legalActions(s)),legal);
      const actions=legalActions(s);r=(Math.imul(r,1664525)+1013904223)>>>0;
      const {state,events}=applyActionWithEvents(s,actions[r%actions.length]);
      assert.ok(validateState(state));const bytes=JSON.stringify(events);
      h.cues=hunterEventCues(events,n);assert.equal(JSON.stringify(events),bytes);
      h=observeHunter(state,h);assert.equal(h.hp,state.hp);assert.equal(h.block,state.block);s=state;accepted++;
    }
  }
  assert.ok(accepted>100);console.log(JSON.stringify({acceptedObservedStates:accepted,seeds:'7811..7818',difficulty:'seed%3',scope:'Actual legal random actions, no human fun inference'}));
});
test('unified hunter placement is deterministic and occupies no creature slot',()=>{
  for(const [w,h] of [[1024,360],[1400,274],[2560,400],[390,270]]) {
    const g=hunterGeometry(w,h);assert.equal(g.torso.x,w*.50);assert.equal(g.torso.y,h*.80);
    assert.ok(g.feet.y<h);assert.ok(g.feet.y-g.bodyHeight>0);
    assert.ok(g.bodyWidth<Math.min(w/7,h*.2));
  }
  assert.equal(observeHunter(createGame(2)).visible,false);
});

test('command directs hunter without rewriting its real companion hit and timing boundaries stay bounded',()=>{
  const s=fixture(['cairnhound','scour','ironward','silence','edict']);
  const bound=resolve(s,'cairnhound').state;
  const r=applyActionWithEvents(bound,{type:'attack',unit:bound.allies[0].uid,target:bound.enemies[0].uid});
  assert.ok(r.events.some(e=>e.type==='hit'&&e.kind==='command'&&e.source===bound.allies[0].uid));
  const h=observeHunter(r.state);h.cues=hunterEventCues(r.events,0);
  assert.ok(h.cues.some(c=>c.kind==='order'&&c.source===bound.allies[0].uid));
  assert.equal(hunterPose(h,.139),'anticipation');assert.equal(hunterPose(h,.14),'attack');
  assert.equal(hunterPose(h,.32),'recovery');assert.equal(hunterPose(h,.58),'idle');
  assert.ok(!r.events.some(e=>e.type==='hit'&&e.source==='hunter'));
});
test('all full R3 pose cells fit desktop/mobile with one shared foot plane and target identity stays canonical',async()=>{
  const {HUNTER_R3_FRAMES,hunterSourcePoint}=await import('../src/hunter-presence');
  for(const [w,h] of [[390,220],[502,277],[758,277],[1398,277],[1398,328]]){
    const g=hunterGeometry(w,h),cell=g.bodyHeight*512/418;
    for(const f of Object.values(HUNTER_R3_FRAMES)){
      assert.ok(g.feet.y-cell*f.groundY/512>=2);
      assert.ok(g.feet.y+cell*(512-f.groundY)/512<=h-2+.00001);
    }
    const state=fixture(['scour','silence','edict','ironward','sutures']);const model=observeHunter(state);
    const bytes=JSON.stringify(state);model.facing=-1;hunterSourcePoint(model,w,h,0,false);
    assert.equal(JSON.stringify(state),bytes);assert.equal(model.hp,state.hp);
  }
});
