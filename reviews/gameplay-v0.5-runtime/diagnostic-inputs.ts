import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {applyAction,applyActionWithEvents,createGame,validateState} from '/workspace/Roguelike-deckbuilder/src/engine.ts';
const old=JSON.parse(readFileSync('reviews/gameplay-v0.4-preview-fixtures.json','utf8'));
const previews=old.fixtures.map((f:any)=>{assert.ok(validateState(f.state));const result=applyActionWithEvents(f.state,f.action);assert.deepEqual(result.state,f.after);return {...f,events:result.events};});
const privacy:any[]=[];
for(const p of old.privacyPairs)for(const engineKind of [1,2]){
 const states=p.states.map((s:any)=>engineKind===1?s:{...s,schema:3,engineKind:2});
 states.forEach((s:any)=>assert.ok(validateState(s)));const actual=states.map((s:any)=>applyAction(s,p.action));
 privacy.push({name:p.name,engineKind,states,action:p.action,future:actual.map((s:any)=>s[p.futureField]),futureField:p.futureField});
}
let tools=applyAction(createGame(321),{type:'travel',choice:'battle'});
const ids=['scour','harpoon','ironward','aegis','sutures','edict'];tools.deck=[...ids,'cairnhound','silence','survey'];tools.hand=ids;tools.draw=['cairnhound','silence','survey'];tools.discard=[];tools.energy=12;assert.ok(validateState(tools));
const arena=JSON.parse(readFileSync('reviews/arena-v0.5-evidence/fixtures.json','utf8'));
for(const f of arena){assert.ok(validateState(f.before));let s=f.before;for(const t of f.transitions??[f]){const result=applyActionWithEvents(s,t.action);assert.deepEqual(result.state,t.state);assert.deepEqual(result.events,t.events);s=result.state;}}
const schema=[{schema:4,engineKind:3},{schema:3,engineKind:9},{schema:3,engineKind:undefined},{schema:2,engineKind:2}].map(marker=>({...createGame(321),...marker}));schema.forEach(s=>assert.equal(validateState(s),false));
const path='reviews/gameplay-v0.5-runtime/diagnostic-inputs.json';assert.equal(existsSync(path),false);writeFileSync(path,JSON.stringify({qualification:'Structurally valid unearned diagnostics, not complete earned campaigns. Archived inputs never modified.',sourceEngineSHA:createHash('sha256').update(readFileSync('src/engine.ts')).digest('hex'),previews,privacy,tools,schema,arena},null,2)+'\n');
console.log(JSON.stringify({previews:previews.length,privacy:privacy.map(p=>({name:p.name,engineKind:p.engineKind,actualHiddenFutureDiffers:JSON.stringify(p.future[0])!==JSON.stringify(p.future[1])})),arena:arena.length}));
