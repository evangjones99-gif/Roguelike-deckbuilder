import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {tsImport} from 'tsx/esm/api';
import {assertCurrentRuntime,audioInputs,pcmWitness,packagedAssetWitness,assertNativeDecodedSounds,earnedCryptTrace,cryptActions,expectedCryptSHA256,decodeInstalledSounds} from './windows-installer-current-validation.mjs';
import {expectedDigest,expectedAsar,hash} from './windows-installer-guards.mjs';

const runtime=JSON.parse(fs.readFileSync('dist/build-provenance.json','utf8'));
const readParts=parts=>fs.readFileSync(path.join(...parts));
const assets=packagedAssetWitness(runtime,readParts);
const engine=await tsImport(pathToFileURL(path.resolve('src/engine.ts')).href,import.meta.url);
const {encounterEnvironment}=await tsImport(pathToFileURL(path.resolve('src/encounter-environment.ts')).href,import.meta.url);
const fixture=earnedCryptTrace(engine,encounterEnvironment);
const nativeFixture=()=>({elapsedMs:100,records:assets.sounds.map(sound=>({...sound,url:'file:///C:/QA/installation/resources/app.asar/dist/audio/'+sound.name}))});

test('current0.8 ordered provenance is76 exact actual source bytes and fixed ASAR pin',()=>{
 assertCurrentRuntime(runtime);assert.equal(expectedAsar,'c383c4437ac5467146174c6ea039b2a8b28af43d609701379e8cf695f59d530c');
 for(const [file,digest] of Object.entries(runtime.hashes))assert.equal(hash(fs.readFileSync(file)),digest);
 assert.equal(hash(JSON.stringify(runtime.hashes)),expectedDigest);
});
test('old0.7, stale version/count/content/order provenance refused',()=>{
 for(const changed of [
  {...runtime,version:'0.7.0'}, {...runtime,sourceDigest:'0be4f01d416e6fc4cca3f19b6916b5b65993b9fd426a926a1ede6d8487834a35'},
  {...runtime,hashes:Object.fromEntries(Object.entries(runtime.hashes).slice(1))},
  {...runtime,hashes:{...runtime.hashes,'src/engine.ts':'0'.repeat(64)}},
  {...runtime,hashes:Object.fromEntries(Object.entries(runtime.hashes).reverse())},
 ])assert.throws(()=>assertCurrentRuntime(changed));
});
test('all39 actual production WAVs and actual crypt payload match source SHA and PCM format',()=>{
 assert.equal(audioInputs(runtime).length,39);assert.equal(assets.sounds.length,39);
 assert.equal(assets.crypt.sha256,expectedCryptSHA256);assert.deepEqual([assets.crypt.width,assets.crypt.height],[2069,760]);
 for(const sound of assets.sounds){
  const original=fs.readFileSync(sound.source);assert.equal(hash(original),sound.sha256);
  assert.deepEqual(pcmWitness(original),Object.fromEntries(Object.entries(sound).filter(([key])=>!['source','name','sha256'].includes(key))));
 }
});
test('tampered or missing packaged WAV/crypt refuses before native install',()=>{
 for(const wanted of ['dist/audio/bind_seal-1.wav','dist/art/ossuary-crypt-v08-r2.png']){
  assert.throws(()=>packagedAssetWitness(runtime,parts=>{
   const bytes=Buffer.from(readParts(parts));if(parts.join('/')===wanted)bytes[bytes.length-1]^=1;return bytes;
  }));
  assert.throws(()=>packagedAssetWitness(runtime,parts=>{if(parts.join('/')===wanted)throw Error('missing');return readParts(parts);}));
 }
});
test('truncated/invalid RIFF, unsupported PCM and silent production data fail',()=>{
 const original=fs.readFileSync(assets.sounds[0].source);
 for(const change of [b=>b.subarray(0,b.length-1),b=>{b.write('RIFX',0);return b;},b=>{b.writeUInt32LE(0,4);return b;},
  b=>{b.writeUInt16LE(3,20);return b;},b=>{b.writeUInt16LE(1,22);return b;},b=>{b.writeUInt32LE(44100,24);return b;},
  b=>{b.writeUInt32LE(0,28);return b;},b=>{b.writeUInt16LE(2,32);return b;},b=>{b.writeUInt16LE(8,34);return b;},
  b=>{b.writeUInt32LE(0,40);return b;},b=>{b.fill(0,44);return b;}])assert.throws(()=>pcmWitness(change(Buffer.from(original))));
});
test('native-result validator accepts exact original metrics but refuses stale/duplicate/nonlocal/nonfinite/wrong decoding',()=>{
 assertNativeDecodedSounds(assets,nativeFixture());
 for(const change of [r=>r.records.pop(),r=>r.records.push(r.records[0]),r=>{r.records[1].name=r.records[0].name;},
  r=>{r.records[0].url='https://example.com/'+r.records[0].name;},r=>{r.records[0].url='file:///C:/other/'+r.records[0].name;},
  r=>{r.records[0].bytes++;},r=>{r.records[0].frames--;},r=>{r.records[0].channels=1;},r=>{r.records[0].sampleRate=44100;},
  r=>{r.records[0].peak=NaN;},r=>{r.records[0].meanSquare=0;},r=>{r.records[0].duration+=0.001;},r=>{r.elapsedMs=100001;}]){
  const result=nativeFixture();change(result);assert.throws(()=>assertNativeDecodedSounds(assets,result));
 }
});
test('serializable renderer refuses noninstalled origins and malformed decode count without fetch or native mock pass',async()=>{
 const previous=globalThis.location;let touched=false;
 try{
  globalThis.location={href:'https://example.com/index.html'};
  await assert.rejects(()=>decodeInstalledSounds(assets.sounds),/Not an installed/);
  globalThis.location={href:'file:///C:/installation/resources/app.asar/dist/index.html'};
  await assert.rejects(()=>decodeInstalledSounds(assets.sounds.slice(1)),/decode count/);
  touched=true;
 }finally{if(previous===undefined)delete globalThis.location;else globalThis.location=previous;}
 assert.equal(touched,true);
});
test('crypt fixture earns battle victory/event/camp/elite through14 exact legal reducer actions, no injected campaign',()=>{
 assert.equal(cryptActions.length,14);assert.equal(fixture.rows.length,14);assert.equal(fixture.seed,44);
 let state=engine.createGame(44,0),victory=false;
 for(const row of fixture.rows){
  assert.equal(hash(JSON.stringify(state)),row.beforeSHA256);assert.ok(engine.legalActions(state).some(a=>JSON.stringify(a)===JSON.stringify(row.action)));
  state=engine.applyAction(state,row.action);assert.ok(engine.validateState(state));assert.equal(hash(JSON.stringify(state)),row.afterSHA256);
  victory||=state.phase==='reward';
 }
 assert.ok(victory);assert.deepEqual(state,fixture.state);assert.equal(encounterEnvironment(state),'crypt');
 assert.equal(state.floor,4);assert.deepEqual(state.enemies.map(e=>e.cardId),['brood','acolyte']);
});
test('earned crypt binding and necromancer command are legal, preserve selector and exact serialized reload',()=>{
 let state=structuredClone(fixture.state);
 const bind=engine.legalActions(state).find(a=>a.type==='play'&&state.hand[a.index]==='cairnhound');assert.ok(bind);
 state=engine.applyAction(state,bind);
 const command=engine.legalActions(state).find(a=>a.type==='attack'&&state.enemies.find(e=>e.uid===a.target)?.cardId==='acolyte');assert.ok(command);
 state=engine.applyAction(state,command);assert.ok(engine.validateState(state));assert.equal(encounterEnvironment(state),'crypt');
 assert.equal(state.stats.cardsPlayed,6);assert.deepEqual(JSON.parse(JSON.stringify(state)),state);
 assert.equal(encounterEnvironment(JSON.parse(JSON.stringify(state))),'crypt');
});
test('crypt fixture refuses mismatched or altered canonical dependencies instead of drifting silently',()=>{
 assert.throws(()=>earnedCryptTrace({...engine,createGame:()=>engine.createGame(121,0)},encounterEnvironment));
 assert.throws(()=>earnedCryptTrace({...engine,legalActions:s=>engine.legalActions(s).filter(a=>a.type!=='reward')},encounterEnvironment));
 assert.throws(()=>earnedCryptTrace(engine,()=> 'courtyard'));
});

test('native receipt elapsed boundary admits zero and maximum, refuses negative/nonfinite/over-limit values',()=>{
 for(const elapsedMs of [0,100000]){const result=nativeFixture();result.elapsedMs=elapsedMs;assertNativeDecodedSounds(assets,result);}
 for(const elapsedMs of [-1,-Number.MIN_VALUE,NaN,Infinity,-Infinity,100001,'100',null,undefined]){
  const result=nativeFixture();result.elapsedMs=elapsedMs;assert.throws(()=>assertNativeDecodedSounds(assets,result));
 }
});
test('native receipt refuses remote file authorities even with an exact installed ASAR suffix and PCM metrics',()=>{
 for(const authority of ['remote-host','127.0.0.1','[::1]','remote-host.example']){
  const result=nativeFixture();result.records[0].url=`file://${authority}/share/resources/app.asar/dist/audio/${result.records[0].name}`;
  assert.notEqual(new URL(result.records[0].url).hostname,'');assert.throws(()=>assertNativeDecodedSounds(assets,result));
 }
});
test('renderer rejects remote file authorities before count admission, offline context creation or fetch',async()=>{
 const originals=new Map(['location','OfflineAudioContext','fetch'].map(key=>[key,Object.getOwnPropertyDescriptor(globalThis,key)]));
 let contextCalls=0,fetchCalls=0;
 try{
  Object.defineProperty(globalThis,'OfflineAudioContext',{configurable:true,value:class {constructor(){contextCalls++;throw Error('Native API must not be reached');}}});
  Object.defineProperty(globalThis,'fetch',{configurable:true,value:()=>{fetchCalls++;throw Error('Fetch must not be reached');}});
  for(const authority of ['remote-host','127.0.0.1','[::1]','remote-host.example']){
   Object.defineProperty(globalThis,'location',{configurable:true,value:{href:`file://${authority}/share/resources/app.asar/dist/index.html`}});
   await assert.rejects(()=>decodeInstalledSounds(assets.sounds),/Not an installed ASAR sound path/);
   await assert.rejects(()=>decodeInstalledSounds(assets.sounds.slice(1)),/Not an installed ASAR sound path/);
  }
 }finally{for(const [key,descriptor] of originals){if(descriptor)Object.defineProperty(globalThis,key,descriptor);else delete globalThis[key];}}
 assert.equal(contextCalls,0);assert.equal(fetchCalls,0);
});
