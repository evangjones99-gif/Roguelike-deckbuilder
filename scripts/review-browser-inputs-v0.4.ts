import { readFileSync, writeFileSync } from 'node:fs';
import { gunzipSync, gzipSync } from 'node:zlib';
import { createGame, applyAction, validateState } from '../src/engine';
const historic=JSON.parse(gunzipSync(readFileSync('reviews/gameplay-v0.2-experiments.json.gz')).toString());
const runs=historic.runs.filter((r:any)=>r.difficulty===2&&((r.seed===6503&&r.policy==='pack')||(r.seed===6501&&r.policy==='front-focused')));
if(runs.length!==2)throw Error('Expected two preserved traces');
const known=JSON.parse(gunzipSync(readFileSync('reviews/solo-v0.3/silence-overflow-campaign.json.gz')).toString());
let state=createGame(known.seed,known.difficulty);const trace=[];
for(const action of known.actions){trace.push({phase:state.phase,floor:state.floor,turn:state.turn,hp:state.hp,energy:state.energy,hand:state.hand,allies:state.allies,enemies:state.enemies,action});state=applyAction(state,action);if(!validateState(state))throw Error('Invalid119campaign');}
runs.push({seed:known.seed,difficulty:known.difficulty,policy:'Known legal save-defect campaign',knownCampaign:true,phase:state.phase,hp:state.hp,trace,continued:applyAction(state,{type:'endTurn'})});
writeFileSync('reviews/gameplay-v0.4-browser-inputs.json.gz',gzipSync(JSON.stringify(runs)));
console.log(JSON.stringify(runs.map((r:any)=>({seed:r.seed,difficulty:r.difficulty,actions:r.trace.length,phase:r.phase}))));
