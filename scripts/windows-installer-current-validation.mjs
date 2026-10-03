import assert from 'node:assert/strict';
import {expectedDigest,expectedVersion,expectedInputCount,hash} from './windows-installer-guards.mjs';

export const expectedCryptSHA256='ff9818614003e9432ee1868c2f60b336d0b5dfe63f5c01e380832f1e880c4b00';
export const cryptSeed=44;
export const cryptActions=Object.freeze([
 {type:'travel',choice:'battle'}, {type:'play',index:0}, {type:'play',index:1},
 {type:'attack',unit:'a3',target:'e1'}, {type:'attack',unit:'a4',target:'e1'},
 {type:'play',index:0,target:'e1'}, {type:'play',index:0,target:'e2'}, {type:'play',index:0,target:'e2'},
 {type:'reward',card:null}, {type:'travel',choice:'event'}, {type:'event',choice:'leave'},
 {type:'travel',choice:'camp'}, {type:'camp',choice:'rest'}, {type:'travel',choice:'elite'},
].map(a=>Object.freeze(a)));

export function assertCurrentRuntime(runtime){
 assert.equal(runtime.version,expectedVersion);assert.equal(runtime.sourceDigest,expectedDigest);
 assert.equal(Object.keys(runtime.hashes).length,expectedInputCount);
 assert.equal(hash(JSON.stringify(runtime.hashes)),expectedDigest,'Exact ordered source provenance differs');
 return runtime;
}
export function audioInputs(runtime){
 assertCurrentRuntime(runtime);
 const names=Object.keys(runtime.hashes).filter(p=>p.startsWith('public/audio/')&&p.endsWith('.wav')).sort();
 assert.equal(names.length,39);
 const cues=new Map();
 for(const name of names){
  const match=/^public\/audio\/([a-z_]+)-([123])\.wav$/.exec(name);assert.ok(match,'Unexpected sound path');
  const variants=cues.get(match[1])??new Set();variants.add(match[2]);cues.set(match[1],variants);
 }
 assert.equal(cues.size,13);for(const variants of cues.values())assert.equal(variants.size,3);
 return names;
}
export function pcmWitness(bytes){
 assert.ok(Buffer.isBuffer(bytes));assert.ok(bytes.length>=48&&bytes.length<=2*1024*1024);
 assert.equal(bytes.toString('ascii',0,4),'RIFF');assert.equal(bytes.readUInt32LE(4),bytes.length-8);
 assert.equal(bytes.toString('ascii',8,12),'WAVE');assert.equal(bytes.toString('ascii',12,16),'fmt ');
 assert.equal(bytes.readUInt32LE(16),16);assert.equal(bytes.readUInt16LE(20),1);
 assert.equal(bytes.readUInt16LE(22),2);assert.equal(bytes.readUInt32LE(24),48000);
 assert.equal(bytes.readUInt32LE(28),192000);assert.equal(bytes.readUInt16LE(32),4);assert.equal(bytes.readUInt16LE(34),16);
 assert.equal(bytes.toString('ascii',36,40),'data');assert.equal(bytes.readUInt32LE(40),bytes.length-44);
 assert.equal((bytes.length-44)%4,0);const frames=(bytes.length-44)/4;assert.ok(frames>0);
 let peak=0,sum=0;
 for(let offset=44;offset<bytes.length;offset+=2){const value=bytes.readInt16LE(offset)/32768;peak=Math.max(peak,Math.abs(value));sum+=value*value;}
 assert.ok(peak>0&&peak<1,'Silent or clipped fixed production sound');
 // Chromium FixedSampleTypeTraits<int16_t>::To<float> uses different signed
 // endpoints and Float32 reciprocal multiplication, not uniform /32768.
 // This expected channel-major LE PCM is computed from SHA-pinned raw samples.
 const decodedBytes=Buffer.alloc(frames*2*4),positive=Math.fround(1/32767),negative=Math.fround(1/32768);
 let index=0,decodedPeak=0,decodedSum=0;
 for(let channel=0;channel<2;channel++)for(let frame=0;frame<frames;frame++){
  const sample=bytes.readInt16LE(44+(frame*2+channel)*2),value=Math.fround(sample*(sample<0?negative:positive));
  decodedBytes.writeFloatLE(value,index++*4);decodedPeak=Math.max(decodedPeak,Math.abs(value));decodedSum+=value*value;
 }
 return {bytes:bytes.length,frames,channels:2,sampleRate:48000,duration:frames/48000,peak,meanSquare:sum/(frames*2),
  decodedPCM:{normalization:'chromium-s16-asymmetric-f32-reciprocal-v1',layout:'channel-major-float32-le',bytes:decodedBytes.length,
   sha256:hash(decodedBytes),peak:decodedPeak,meanSquare:decodedSum/(frames*2)}};
}
export function packagedAssetWitness(runtime,readParts){
 const sounds=audioInputs(runtime).map(source=>{
  const name=source.slice('public/audio/'.length),bytes=readParts(['dist','audio',name]);
  assert.equal(hash(bytes),runtime.hashes[source],`Packaged sound differs: ${source}`);
  return {source,name,sha256:hash(bytes),...pcmWitness(bytes)};
 });
 assert.equal(runtime.hashes['public/art/ossuary-crypt-v08-r2.png'],expectedCryptSHA256);
 const crypt=readParts(['dist','art','ossuary-crypt-v08-r2.png']);assert.equal(hash(crypt),expectedCryptSHA256);
 assert.deepEqual([...crypt.subarray(0,8)],[137,80,78,71,13,10,26,10]);
 assert.equal(crypt.readUInt32BE(16),2069);assert.equal(crypt.readUInt32BE(20),760);
 return {sounds,crypt:{sha256:expectedCryptSHA256,width:2069,height:760}};
}

// Passed directly to page.evaluate. No Node API, dependency import, output device,
// source-buffer injection or connection to a live AudioContext is used.
export async function decodeInstalledSounds(sounds){
 const base=new URL('./audio/',location.href);
 if(base.protocol!=='file:'||base.hostname!==''||!base.pathname.endsWith('/resources/app.asar/dist/audio/'))throw Error('Not an installed ASAR sound path');
 if(sounds.length!==39)throw Error('Wrong fixed decode count');
 const started=performance.now(),context=new OfflineAudioContext(2,1,48000),records=[];
 async function digest(input){
  let timer;const result=await Promise.race([crypto.subtle.digest('SHA-256',input),
   new Promise((_,reject)=>{timer=setTimeout(()=>reject(Error('Installed sound hash timeout')),10000);}),
  ]).finally(()=>clearTimeout(timer));
  return [...new Uint8Array(result)].map(byte=>byte.toString(16).padStart(2,'0')).join('');
 }
 for(const sound of sounds){
  if(performance.now()-started>90000)throw Error('Installed sound decode phase deadline');
  if(!/^[a-z_]+-[123]\.wav$/.test(sound.name))throw Error('Unsafe sound filename');
  const url=new URL(sound.name,base);if(url.protocol!=='file:'||url.hostname!==''||!url.href.startsWith(base.href))throw Error('Sound escaped installed ASAR');
  const response=await fetch(url,{credentials:'omit',signal:AbortSignal.timeout(10000)});
  if(!response.ok)throw Error('Installed sound unavailable');const bytes=await response.arrayBuffer();
  if(bytes.byteLength!==sound.bytes||bytes.byteLength>2097152)throw Error('Installed sound byte count differs');
  const rawSHA256=await digest(bytes);
  if(rawSHA256!==sound.sha256)throw Error('Installed sound raw SHA differs');
  let timer;const decoded=await Promise.race([
   context.decodeAudioData(bytes),new Promise((_,reject)=>{timer=setTimeout(()=>reject(Error('Installed sound decode timeout')),10000);}),
  ]).finally(()=>clearTimeout(timer));
  if(decoded.length!==sound.frames||decoded.numberOfChannels!==sound.channels||decoded.sampleRate!==sound.sampleRate)throw Error('Installed decoded PCM format differs');
  const pcm=new ArrayBuffer(decoded.length*decoded.numberOfChannels*4),view=new DataView(pcm);let sampleIndex=0,peak=0,sum=0;
  for(let channel=0;channel<decoded.numberOfChannels;channel++)for(const value of decoded.getChannelData(channel)){
   if(!Number.isFinite(value))throw Error('Nonfinite native decoded PCM');view.setFloat32(sampleIndex++*4,value,true);peak=Math.max(peak,Math.abs(value));sum+=value*value;
  }
  const pcmSHA256=await digest(pcm);
  records.push({rawSHA256,pcmSHA256,pcmBytes:pcm.byteLength,name:sound.name,url:url.href,bytes:sound.bytes,frames:decoded.length,channels:decoded.numberOfChannels,
   sampleRate:decoded.sampleRate,duration:decoded.duration,peak,meanSquare:sum/(decoded.length*decoded.numberOfChannels)});
 }
 return {method:'Installed file fetch + offline Chromium Web Audio decode; no output/listening/application-audio claim',elapsedMs:performance.now()-started,records};
}
export function assertNativeDecodedSounds(witness,result){
 assert.equal(witness.sounds.length,39);assert.equal(result.records.length,39);
 assert.ok(Number.isFinite(result.elapsedMs)&&result.elapsedMs>=0&&result.elapsedMs<=100000);
 assert.equal(new Set(result.records.map(r=>r.name)).size,39);
 for(let i=0;i<39;i++){
  const source=witness.sounds[i],actual=result.records[i],url=new URL(actual.url);
  assert.equal(actual.name,source.name);assert.equal(url.protocol,'file:');assert.equal(url.hostname,'');
  assert.ok(url.pathname.endsWith('/resources/app.asar/dist/audio/'+source.name));
  for(const field of ['bytes','frames','channels','sampleRate'])assert.equal(actual[field],source[field]);
  assert.equal(source.decodedPCM.normalization,'chromium-s16-asymmetric-f32-reciprocal-v1');
  assert.equal(source.decodedPCM.layout,'channel-major-float32-le');
  assert.equal(actual.rawSHA256,source.sha256,'Actual fetched raw WAV differs');
  assert.equal(actual.pcmBytes,source.decodedPCM.bytes);assert.equal(actual.pcmSHA256,source.decodedPCM.sha256,'Ordered decoded Float32 PCM differs');
  for(const field of ['duration','peak','meanSquare']){
   assert.ok(Number.isFinite(actual[field])&&actual[field]>0);
   assert.ok(Math.abs(actual[field]-(field==='duration'?source.duration:source.decodedPCM[field]))<=1e-10,`Native PCM metric differs: ${source.name}/${field}`);
  }
 }
}
export function earnedCryptTrace(engine,environment){
 let state=engine.createGame(cryptSeed,0);assert.ok(engine.validateState(state));const rows=[];
 for(const action of cryptActions){
  assert.ok(engine.legalActions(state).some(a=>JSON.stringify(a)===JSON.stringify(action)),'Fixed crypt fixture action no longer legal');
  const before=JSON.stringify(state);state=engine.applyAction(state,action);assert.ok(engine.validateState(state));
  rows.push({action,beforeSHA256:hash(before),afterSHA256:hash(JSON.stringify(state))});
 }
 assert.equal(state.phase,'battle');assert.equal(state.floor,4);assert.equal(environment(state),'crypt');
 assert.deepEqual(state.enemies.map(e=>e.cardId),['brood','acolyte']);
 return {seed:cryptSeed,difficulty:0,rows,state,finalSaveSHA256:hash(JSON.stringify(state))};
}
export async function clickEarnedAction(page,action){
 if(action.type==='travel'||action.type==='event'||action.type==='camp'){
  assert.ok(/^[a-z]+$/.test(action.choice));await page.locator(`[data-action="${action.type}"][data-choice="${action.choice}"]`).click();
 }else if(action.type==='play'){
  assert.ok(Number.isInteger(action.index)&&action.index>=0);await page.locator(`[data-ui="play-card"][data-index="${action.index}"]`).click();
  if(action.target){assert.match(action.target,/^[ae][0-9]+$/);await page.locator(`[data-unit="${action.target}"]`).click();}
 }else if(action.type==='attack'){
  assert.match(action.unit,/^a[0-9]+$/);assert.match(action.target,/^e[0-9]+$/);
  await page.locator(`[data-unit="${action.unit}"]`).click();await page.locator(`[data-unit="${action.target}"]`).click();
 }else{assert.deepEqual(action,{type:'reward',card:null});await page.locator('[data-action="reward"][data-card=""]').click();}
}
