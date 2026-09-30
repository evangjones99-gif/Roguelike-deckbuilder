import assert from 'node:assert/strict';
import{readFileSync,writeFileSync,existsSync}from'node:fs';
import{gzipSync}from'node:zlib';
import{createHash}from'node:crypto';
import{createGame,applyAction,applyActionWithEvents,legalActions,validateState,type GameState,type Action}from'./frozen-v05/src/engine';
import{chooseHeuristic}from'./frozen-v05/scripts/simulate';
const root='/workspace/Roguelike-deckbuilder',out='/workspace/scratch/gameplay-v06-input';
const sha=(value:string)=>createHash('sha256').update(value).digest('hex');
const full=JSON.parse(readFileSync(root+'/reviews/screenshots-v0.2/full-fixture.json','utf8'));
const old=JSON.parse(readFileSync(root+'/reviews/gameplay-v0.4-preview-fixtures.json','utf8'));
const generation=(s:GameState,kind:1|2)=>kind===1?structuredClone(s):{...structuredClone(s),schema:3 as const,engineKind:2 as const};
function reference(name:string,state:GameState,actions:Action[]=[]){assert.ok(validateState(state),name);let next=state;const steps=actions.map(action=>{assert.ok(legalActions(next).some(a=>JSON.stringify(a)===JSON.stringify(action)));const resolved=applyActionWithEvents(next,action);assert.ok(validateState(resolved.state));const result={action,before:next,after:resolved.state,events:resolved.events};next=resolved.state;return result;});return{name,state,steps};}
function hand(s:GameState,ids:string[]){const pile=[...s.hand,...s.draw,...s.discard];for(const id of ids){const index=pile.indexOf(id);assert.ok(index>=0,'Real copy required: '+id);pile.splice(index,1);}s.hand=ids;s.draw=pile;s.discard=[];assert.ok(validateState(s));return s;}
const fixtures:any[]=[];
for(const kind of [1,2] as const){
 const nonfinal=generation(full,kind);nonfinal.enemies[0].hp=1;nonfinal.enemies[0].block=0;
 const command:Action={type:'attack',unit:nonfinal.allies[0].uid,target:nonfinal.enemies[0].uid};
 fixtures.push({...reference('nonfinal-kill',nonfinal,[command]),kind});
 const terminal=structuredClone(nonfinal);terminal.enemies=terminal.enemies.slice(0,1);fixtures.push({...reference('terminal-reward',terminal,[command]),kind});
 const noUnspent=generation(full,kind);noUnspent.allies.forEach(a=>a.acted=true);fixtures.push({...reference('no-unspent',noUnspent,[{type:'endTurn'}]),kind});
 const summoned=hand(applyAction(createGame(121,0,{engineKind:kind}),{type:'travel',choice:'battle'}),['cairnhound','cairnhound']);fixtures.push({...reference('hand-two-summons',summoned,[{type:'play',index:0}]),kind});
 const fallen=generation(old.fixtures.find((f:any)=>f.name==='blocked-lethal-retaliation').state,kind);fixtures.push({...reference('source-falls',fallen,[{type:'attack',unit:fallen.allies[0].uid,target:fallen.enemies[0].uid}]),kind});
 fixtures.push({...reference('full-roster',generation(full,kind)),kind});
}
const start=createGame(47101,1),trace:any[]=[];let s=start;
for(let i=0;i<1500&&legalActions(s).length;i++){const action=chooseHeuristic(s),after=applyAction(s,action);assert.ok(validateState(after));trace.push({action,beforeHash:sha(JSON.stringify(s)),afterHash:sha(JSON.stringify(after)),phase:after.phase});s=after;}
assert.ok(['victory','defeat'].includes(s.phase));
const campaign={seed:47101,difficulty:1,kind:2,policy:'Frozen v0.5 repository chooseHeuristic, reused policy not new human decisions',start,trace,final:s};
const legacyInput=JSON.parse((await import('node:zlib')).gunzipSync(readFileSync(root+'/reviews/gameplay-v0.5-runtime/campaign-inputs.json.gz')).toString()).runs.find((r:any)=>r.engineKind===1);
const legacy={...legacyInput,start:legacyInput.start,trace:legacyInput.trace,kind:1,qualified:'Legally earned prior prefix, simulated reference. Remaining119 actual input controls planned.'};
const path=out+'/references.json.gz';assert.equal(existsSync(path),false);writeFileSync(path,gzipSync(JSON.stringify({method:'Exact actual archived-v0.5 reducer oracles; synthetic diagnostics clearly distinct from legally earned progression. No input adapter/focus implementation copied.',fixtures,campaigns:[campaign,legacy]})));console.log(JSON.stringify({fixtures:fixtures.length,campaigns:[{seed:campaign.seed,phase:s.phase,hp:s.hp,steps:trace.length},{seed:legacy.seed,phase:legacy.phase,hp:legacy.hp,steps:legacy.trace.length}]}));
