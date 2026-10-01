/** Authored timing/cancellation checks; source prepared until runtime granted.
 * Mock WebAudio deadlines are not hearing, device or native platform evidence. */
import test from 'node:test';
import assert from 'node:assert/strict';
import { build } from 'esbuild';
import { fileURLToPath } from 'node:url';
import { createGame, applyAction, applyActionWithEvents, validateState, type Action } from '../src/engine';
type HostAudioInstance=import('../src/audio-host').HostAudio;
// art.ts uses Vite's BASE_URL. Bundle the actual host with the same local base
// define for these Node checks instead of fabricating presentation constants or
// changing game/art source. No WebAudio hardware is activated by this import.
const compiled=await build({entryPoints:[fileURLToPath(new URL('../src/audio-host.ts',import.meta.url))],bundle:true,write:false,platform:'node',format:'esm',define:{'import.meta.env.BASE_URL':'"/"'}});
const audio:typeof import('../src/audio-host')=await import(`data:text/javascript;base64,${Buffer.from(compiled.outputFiles![0].text).toString('base64')}`);
const {HostAudio,contactCues,contactCuePlan}=audio;

function transition() {
  const before=applyAction(createGame(121),{type:'travel',choice:'battle'});
  const pile=[...before.hand,...before.draw,...before.discard],index=pile.indexOf('scour');
  assert.ok(index>=0);before.hand=[pile.splice(index,1)[0]];before.draw=pile;before.discard=[];
  assert.equal(validateState(before),true);
  const action:Action={type:'play',index:0,target:before.enemies[0].uid};
  const {state:after,events}=applyActionWithEvents(before,action);
  return {before,after,events,action};
}
function freeze<T>(value:T):T {
  if(value&&typeof value==='object'){Object.freeze(value);for(const item of Object.values(value))freeze(item);}
  return value;
}
const tick=()=>new Promise<void>(resolve=>setImmediate(resolve));
function audioHarness() {
  const host=new HostAudio('http://127.0.0.1/audio/'),scheduled:{cue:string;at:number}[]=[];
  host.player.enabled=true;host.player.context={currentTime:7} as AudioContext;
  host.player.load=async()=>({} as AudioBuffer);
  // Exercise actual CuePlayer.playBatchAt offset bounds and epoch checks; only
  // hardware buffer scheduling is replaced with a deadline observation.
  const player=host.player as unknown as {schedule(buffer:AudioBuffer,cue:string,variant:number,gain:number,at:number,ticket:unknown):boolean};
  player.schedule=(_buffer,cue,_variant,_gain,at)=>{scheduled.push({cue,at});return true;};
  return {host,scheduled};
}

test('omitted/zero timing preserves the old pure contact cues and canonical bytes',()=>{
  const {before,after,events,action}=freeze(transition()),raw=JSON.stringify({before,after,events,action});
  const old=contactCues(before,after,events,action,true);
  assert.deepEqual(contactCuePlan(before,after,events,action,true),{cues:old,anchorOffsetSeconds:0});
  assert.deepEqual(contactCuePlan(before,after,events,action,true,0),{cues:old,anchorOffsetSeconds:0});
  assert.equal(JSON.stringify({before,after,events,action}),raw);
});
test('renderer allocation and queued lead shift the anchor without altering contact offsets',()=>{
  const {before,after,events,action}=freeze(transition()),cues=contactCues(before,after,events,action,true);
  assert.ok(cues.length>0);
  for(const delay of [320,800,1710]){
    const plan=contactCuePlan(before,after,events,action,true,delay);
    assert.equal(plan.anchorOffsetSeconds,delay/1000);assert.deepEqual(plan.cues,cues);
  }
});
test('invalid timing and nonanimated/noncombat presentation remain immediate',()=>{
  const {before,after,events,action}=freeze(transition());
  for(const delay of [-1,NaN,Infinity,-Infinity])assert.equal(contactCuePlan(before,after,events,action,true,delay).anchorOffsetSeconds,0);
  assert.equal(contactCuePlan(before,after,events,action,false,800).anchorOffsetSeconds,0);
  assert.ok(contactCuePlan(before,after,events,action,false,800).cues.every(cue=>cue.offset===0));
  const map=createGame(121),travel:Action={type:'travel',choice:'battle'};
  assert.equal(contactCuePlan(map,before,[],travel,true,800).anchorOffsetSeconds,0);
});
test('arrival bind/impact groups and enemy-phase wound/stagger cues keep their relative contact times',()=>{
  const before=applyAction(createGame(121),{type:'travel',choice:'battle'});
  before.deck.push('emberwidow');before.draw.push(...before.hand);before.hand=['emberwidow'];
  assert.equal(validateState(before),true);
  const action:Action={type:'play',index:0},arrival=applyActionWithEvents(before,action);
  const plan=contactCuePlan(before,arrival.state,arrival.events,action,true,320);
  assert.equal(plan.anchorOffsetSeconds,.32);
  assert.deepEqual(plan.cues,contactCues(before,arrival.state,arrival.events,action,true));
  assert.ok(plan.cues.some(cue=>cue.key.startsWith('bind/')));
  assert.ok(plan.cues.some(cue=>cue.key.startsWith('arrival/')));
  assert.ok(plan.cues.some(cue=>cue.key.startsWith('strike/')));
  const endTurn:Action={type:'endTurn'},phase=applyActionWithEvents(before,endTurn);
  const enemyPlan=contactCuePlan(before,phase.state,phase.events,endTurn,true,1710);
  assert.equal(enemyPlan.anchorOffsetSeconds,1.71);
  assert.deepEqual(enemyPlan.cues,contactCues(before,phase.state,phase.events,endTurn,true));
  assert.ok(enemyPlan.cues.some(cue=>cue.key.startsWith('wound/')));
  assert.ok(enemyPlan.cues.filter(cue=>cue.key.startsWith('wound/')).length<=2);
});
test('actual player deadline includes an800ms anchor lead beyond its unchanged600ms offset cap',async()=>{
  const {before,after,events,action}=freeze(transition()),{host,scheduled}=audioHarness();
  const cues=contactCues(before,after,events,action,true);host.transition(before,after,events,action,true,800);await tick();
  assert.equal(scheduled.length,cues.length);
  for(const cue of cues){const observed=scheduled.find(row=>row.cue===cue.cue);assert.ok(observed);assert.equal(observed.at,7+.8+Math.min(.6,Math.max(0,cue.offset)));assert.ok(observed.at>7+.6);}
});
test('pending delayed decode cannot escape cancellation or native restoration epoch barriers',async()=>{
  for(const cancel of [(host:HostAudioInstance)=>host.cancel('diagnostic'),(host:HostAudioInstance)=>host.visibility(true),(host:HostAudioInstance)=>host.settings(true,.35),(host:HostAudioInstance)=>{host.nativeLifecycle(true);host.nativeLifecycle(false);}]){
    const {before,after,events,action}=transition(),{host,scheduled}=audioHarness(),release:((buffer:AudioBuffer)=>void)[]=[];
    host.player.load=()=>new Promise<AudioBuffer>(resolve=>release.push(resolve));
    host.transition(before,after,events,action,true,800);assert.ok(release.length>0);cancel(host);
    for(const resolve of release)resolve({} as AudioBuffer);await tick();assert.deepEqual(scheduled,[]);
  }
});
test('hidden and native inactive hosts never start a delayed batch',async()=>{
  for(const block of [(host:HostAudioInstance)=>host.visibility(true),(host:HostAudioInstance)=>host.nativeLifecycle(true)]){
    const {before,after,events,action}=transition(),{host,scheduled}=audioHarness();let loads=0;
    host.player.load=async()=>{loads++;return {} as AudioBuffer;};block(host);host.transition(before,after,events,action,true,800);await tick();
    assert.equal(loads,0);assert.deepEqual(scheduled,[]);
  }
});
test('late cold assets still skip their shifted deadline rather than playing a stale impact',async()=>{
  const {before,after,events,action}=transition(),{host,scheduled}=audioHarness(),release:((buffer:AudioBuffer)=>void)[]=[];
  host.player.load=()=>new Promise<AudioBuffer>(resolve=>release.push(resolve));host.transition(before,after,events,action,true,800);
  assert.ok(release.length>0);(host.player.context as unknown as {currentTime:number}).currentTime=10;
  for(const resolve of release)resolve({} as AudioBuffer);await tick();assert.deepEqual(scheduled,[]);
});
