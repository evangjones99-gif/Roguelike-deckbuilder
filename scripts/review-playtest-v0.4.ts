/** Independent acceptance audit. Owns only new review evidence; never mutates runtime. */
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { mkdtempSync, readFileSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { pathToFileURL } from 'node:url';
import { gunzipSync } from 'node:zlib';
import * as current from '../src/engine';
import { ENEMIES } from '../src/content';
const digest = (file: string) => createHash('sha256').update(readFileSync(file)).digest('hex');
const sourceHashes = Object.fromEntries(['src/engine.ts','src/content.ts','scripts/review-playtest-v0.4.ts'].map(f=>[f,digest(f)]));
const archive='releases/0.3.0/hollowpact-0.3.0-source.zip';
const dir=mkdtempSync(join(tmpdir(),'hollowpact-v04-independent-'));
const archivedHashes: Record<string,string>={};
for(const name of ['engine','content']) {
  const bytes=execFileSync('unzip',['-p',archive,`src/${name}.ts`]);
  archivedHashes[name]=createHash('sha256').update(bytes).digest('hex');
  writeFileSync(join(dir,`${name}.ts`),bytes);
}
writeFileSync(join(dir,'package.json'),'{"type":"module"}');
const archived=await import(pathToFileURL(join(dir,'engine.ts')).href) as typeof current;
assert.equal(archivedHashes.engine,'4b24a1bd90a05326ec76db361001bf034af6f6ed0e5f86bcab295e9ae0a5f5af');
assert.equal(archivedHashes.content,sourceHashes['src/content.ts']);
const legacy=JSON.parse(gunzipSync(readFileSync('reviews/solo-v0.3/silence-overflow-campaign.json.gz')).toString()) as {seed:number;difficulty:number;actions:current.Action[];afterState:current.GameState};
function normalizeLabels(s: current.GameState) {
  const copy=structuredClone(s);
  for(const e of copy.enemies) if(e.intent) e.intent.label=e.intent.label.replace(/(?: · silenced \(armor remains\))+$/u,' · silenced (armor remains)');
  copy.log=copy.log.map(line=>line.replace(/(?: · silenced \(armor remains\))+\.$/u,' · silenced (armor remains).'));
  return copy;
}
let s=current.createGame(legacy.seed,legacy.difficulty),old=archived.createGame(legacy.seed,legacy.difficulty);
const casts: unknown[]=[];
for(const [i,a] of legacy.actions.entries()) {
  const incoming=JSON.stringify(s);
  assert.ok(current.legalActions(s).some(b=>JSON.stringify(a)===JSON.stringify(b)),`Action${i+1} is legal`);
  const result=current.applyActionWithEvents(s,a),ordinary=current.applyAction(s,a);
  assert.equal(JSON.stringify(s),incoming,'Input mutation');
  assert.deepEqual(result.state,ordinary,'Observation API changed result');
  s=result.state;old=archived.applyAction(old,a);
  assert.ok(current.validateState(s),`Invalid repaired intermediate${i+1}`);
  assert.deepEqual(s,normalizeLabels(old),`Unexpected mechanics difference${i+1}`);
  if(i>=116)casts.push({actionNumber:i+1,action:a,energy:s.energy,label:s.enemies[0].intent!.label,controlEvents:result.events.filter(e=>e.type==='control').length});
}
assert.deepEqual(old,legacy.afterState);
const repairedCampaign=s;
const continued=current.applyActionWithEvents(s,{type:'endTurn'}),oldContinued=archived.applyAction(old,{type:'endTurn'});
assert.deepEqual(continued.state,normalizeLabels(oldContinued),'Guard continuation changes mechanics');
assert.ok(current.validateState(continued.state));
assert.equal(continued.state.enemies[0].block,14,'Ironjaw armor survives silence');
assert.equal(continued.state.turn,4);
assert.ok(!continued.state.enemies[0].intent!.label.includes('silenced'),'New-turn control resets');

const raw=structuredClone(legacy.afterState),before=JSON.stringify(raw);
const recovered=current.recoverLegacySilenceSave(raw);
assert.equal(JSON.stringify(raw),before,'Recovery mutates raw save');
assert.deepEqual(recovered,repairedCampaign,'Recovery differs from repaired legal campaign');
assert.ok(current.validateState(JSON.parse(JSON.stringify(recovered))));
assert.equal(current.recoverLegacySilenceSave(recovered),null,'Already valid saves use normal loader');
const rejected: string[]=[];
const mutations: [string,(s:current.GameState)=>void][]=[
 ['negativeHP',s=>{s.hp=-1;}],['zeroBattleHP',s=>{s.hp=0;}],['missingDeckCopy',s=>{s.deck.pop();}],
 ['duplicateUID',s=>{s.enemies.push(structuredClone(s.enemies[0]));}],['unallocatedUID',s=>{s.enemies[0].uid='e999999';}],
 ['forgedPassive',s=>{s.enemies[0].passive='forged';}],['unknownEnemy',s=>{s.enemies[0].cardId='missing';}],
 ['wrongGuardTurn',s=>{s.turn=4;}],['wrongTarget',s=>{s.enemies[0].intent!.target='hunter';}],
 ['nonzeroDamage',s=>{s.enemies[0].intent!.damage=1;}],['missingEmptySummon',s=>{delete s.enemies[0].intent!.summon;}],
 ['reinforcement',s=>{s.enemies[0].intent!.summon=['thrall'];}],['modifiedGuardPrefix',s=>{s.enemies[0].intent!.label='forged '+s.enemies[0].intent!.label;}],
 ['modifiedSuffix',s=>{s.enemies[0].intent!.label=s.enemies[0].intent!.label.replace('armor remains','armor stays');}],
 ['trailingText',s=>{s.enemies[0].intent!.label+=' extra';}],['hugeLabel',s=>{s.enemies[0].intent!.label='Raise plated shield · gain 14 block'+' · silenced (armor remains)'.repeat(400);}],
 ['wrongSchema',s=>{(s as any).schema=1;}],['incompatiblePhase',s=>{s.phase='camp';}],
 ['wrongRoute',s=>{s.route=['shop'];}],['invalidRng',s=>{s.rng=NaN;}],['forgedCard',s=>{s.hand[0]='forged';}],
];
for(const [name,mutate] of mutations) {
 const v=structuredClone(raw);mutate(v);const before=JSON.stringify(v);
 assert.equal(current.recoverLegacySilenceSave(v),null,`Recovery must reject ${name}`);
 assert.equal(JSON.stringify(v),before,`Rejected recovery mutates ${name}`);rejected.push(name);
}
for(const v of [null,7,'text',[],{},Object.assign(Object.create(null),raw)])assert.equal(current.recoverLegacySilenceSave(v),null);
const defeat=structuredClone(raw);defeat.phase='defeat';defeat.hp=0;
const recoveredDefeat=current.recoverLegacySilenceSave(defeat);assert.ok(recoveredDefeat&&current.validateState(recoveredDefeat));

const guardFixtures: unknown[]=[];
for(const id of ['raider','ironjaw','cindermaw']) {
 const map=current.createGame(41);map.deck=['silence+','silence','silence','survey','ironward'];
 let state=current.applyAction(map,{type:'travel',choice:'battle'});
 const def=ENEMIES[id];state.enemies=[{...def,cardId:id,uid:'e'+state.nextUid++,maxHp:def.hp,block:0,acted:false,intent:{target:'hunter',damage:0,label:'initial'}}];
 // A structurally valid unearned diagnostic roster, not a reached progression claim.
 state.turn=1;state.enemies[0].intent={target:state.enemies[0].uid,damage:0,label:id==='raider'?'Raise shield · gain 4 block':id==='ironjaw'?'Raise plated shield · gain 14 block':'Fold armored wings · gain 10 block'};
 assert.ok(current.validateState(state));const labels:string[]=[],controls:number[]=[];
 for(const card of ['silence+','silence','silence']) {
  const r=current.applyActionWithEvents(state,{type:'play',index:state.hand.indexOf(card),target:state.enemies[0].uid});
  assert.notEqual(r.state,state);state=r.state;assert.ok(current.validateState(state));labels.push(state.enemies[0].intent!.label);controls.push(r.events.filter(e=>e.type==='control').length);
 }
 assert.ok(labels.every(label=>label===labels[0]));assert.deepEqual(controls,[1,0,0]);
 const end=current.applyAction(state,{type:'endTurn'});assert.ok(current.validateState(end));
 assert.equal(end.enemies[0].block,id==='raider'?4:id==='ironjaw'?14:10);
 assert.ok(!end.enemies[0].intent!.label.includes('silenced'));
 const overflow=structuredClone(state);overflow.enemies[0].intent!.label=labels[0]+' · silenced (armor remains)'.repeat(3);
 const recover=current.recoverLegacySilenceSave(overflow);assert.ok(recover&&current.validateState(recover));assert.deepEqual(recover,state);
 guardFixtures.push({id,fixtureKind:'Structurally valid unearned diagnostic roster',labels,controls,armorAfterEnd:end.enemies[0].block,newTurnIntent:end.enemies[0].intent,recoveryMatchesCanonical:true});
}
assert.equal(digest('src/engine.ts'),sourceHashes['src/engine.ts'],'Source changed during audit');
const evidencePath='reviews/gameplay-v0.4-evidence.json',evidence=JSON.parse(readFileSync(evidencePath,'utf8'));
evidence.saveRepairAudit={method:'Independent archived-v0.3 differential replay of119 genuinely legal campaign actions plus strict recovery mutations and explicitly unearned three-family guard fixtures. No production browser visited.',sourceHashes,archivedHashes,archiveSHA:digest(archive),actions:119,everyIntermediateValid:true,mechanicsIdenticalExceptCanonicalGuardStatus:true,casts,continuation:{turn:continued.state.turn,armor:continued.state.enemies[0].block,intent:continued.state.enemies[0].intent},recovery:{inputUnchanged:true,matchesRepairedCampaign:true,serializedValid:true,validSaveNormalLoader:true,defeatVariantValid:true,rejectedMutations:rejected},guardFixtures};
writeFileSync(evidencePath,JSON.stringify(evidence,null,2)+'\n');
console.log(JSON.stringify(evidence.saveRepairAudit,null,2));
