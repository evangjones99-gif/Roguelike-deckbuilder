/** Local cue playback: bounded admission, epoch cancellation and output shaping. */
export function mixGraph(context,destination=context.destination){
 const master=context.createGain(),compressor=context.createDynamicsCompressor(),ceiling=context.createWaveShaper();
 compressor.threshold.value=-12;compressor.knee.value=6;compressor.ratio.value=4;compressor.attack.value=.003;compressor.release.value=.14;
 const curve=new Float32Array(4097);for(let i=0;i<curve.length;i++){const x=2*i/(curve.length-1)-1;curve[i]=.45*Math.tanh(1.6*x)/Math.tanh(1.6);}
 ceiling.curve=curve;ceiling.oversample='4x';master.connect(compressor);compressor.connect(ceiling);ceiling.connect(destination);
 return{master,compressor,ceiling};
}
const finite=(value,fallback=0)=>Number.isFinite(value)?value:fallback;
const bounded=(value,min,max,fallback=0)=>Math.min(max,Math.max(min,finite(value,fallback)));
const priorityFor=cue=>cue==='hunter_wound'?100:cue.startsWith('ui_')||cue==='camp_settle'?10:cue==='bind_seal'?30:50;
export class CuePlayer{
 constructor(assetBase){this.assetBase=assetBase;this.context=null;this.master=null;this.cache=new Map();this.active=new Set();this.variant=0;this.muted=false;this.volume=.35;this.enabled=false;this.epoch=0;this.contextGeneration=0;}
 ticket(){return{epoch:this.epoch,context:this.context,contextGeneration:this.contextGeneration};}
 current(ticket){return ticket.epoch===this.epoch&&ticket.context===this.context&&ticket.contextGeneration===this.contextGeneration&&this.enabled&&!this.muted&&this.volume>0;}
 async enable(){if(!this.context){this.context=new AudioContext({sampleRate:48000});this.contextGeneration++;this.master=mixGraph(this.context).master;}const ticket=this.ticket();await ticket.context.resume();if(ticket.epoch!==this.epoch||ticket.context!==this.context)return false;this.enabled=true;this.settings(this.muted,this.volume);return true;}
 retire(entry,delay=.012){const context=entry.context;this.active.delete(entry);try{entry.voice.gain.cancelScheduledValues(context.currentTime);entry.voice.gain.setTargetAtTime(0,context.currentTime,.003);entry.source.stop(context.currentTime+delay);}catch{}return context.currentTime+delay;}
 cancel(){this.epoch++;for(const entry of [...this.active])this.retire(entry);}
 settings(muted,volume){this.muted=!!muted;this.volume=bounded(volume,0,1);if(this.muted||!this.volume)this.cancel();if(this.master&&this.context){this.master.gain.cancelScheduledValues(this.context.currentTime);this.master.gain.setTargetAtTime(this.muted?0:this.volume,this.context.currentTime,.008);}}
 async load(cue,variant){if(!/^[a-z_]+$/.test(cue)||![1,2,3].includes(variant)||!this.context)throw new Error('Invalid/unactivated local cue request');const key=`${cue}-${variant}`,context=this.context;
  if(!this.cache.has(key)){const promise=fetch(new URL(`${key}.wav`,this.assetBase)).then(response=>{if(!response.ok)throw new Error('Local sound unavailable');return response.arrayBuffer();}).then(bytes=>context.decodeAudioData(bytes)).catch(error=>{if(this.cache.get(key)===promise)this.cache.delete(key);throw error;});this.cache.set(key,promise);}return this.cache.get(key);
 }
 schedule(buffer,cue,variant,gain,at,ticket=this.ticket()){
  if(!this.current(ticket)||!Number.isFinite(gain)||!Number.isFinite(at))return false;
  const priority=priorityFor(cue),normal=[...this.active].filter(entry=>entry.priority<100);
  if(priority<100&&normal.length>=7)return false;
  let start=Math.max(at,this.context.currentTime);
  if(this.active.size>=8){if(priority<100)return false;const victim=[...this.active].sort((a,b)=>a.priority-b.priority||a.start-b.start)[0];start=Math.max(start,this.retire(victim)+.001);}
  const source=this.context.createBufferSource(),voice=this.context.createGain();source.buffer=buffer;voice.gain.value=bounded(gain,0,1);source.connect(voice);voice.connect(this.master);
  const entry={source,voice,context:this.context,priority,start};this.active.add(entry);source.onended=()=>{this.active.delete(entry);source.disconnect();voice.disconnect();};source.start(start);
  return true;
 }
 async play(cue,gain=.8,offset=0){const ticket=this.ticket();if(!this.current(ticket))return false;const variant=(this.variant++%3)+1;let buffer;try{buffer=await this.load(cue,variant);}catch(error){if(!this.current(ticket))return false;throw error;}if(!this.current(ticket))return false;return this.schedule(buffer,cue,variant,gain,this.context.currentTime+bounded(offset,0,.4),ticket);}
 async playBatchAt(cues,anchor){const ticket=this.ticket();if(!this.current(ticket)||!Number.isFinite(anchor))return[];const picked=cues.map((cue,index)=>({...cue,index,priority:priorityFor(cue.cue)})).sort((a,b)=>b.priority-a.priority||a.index-b.index).slice(0,8);let prepared;
  try{prepared=await Promise.all(picked.map(async cue=>{const variant=(this.variant++%3)+1;return{...cue,variant,buffer:await this.load(cue.cue,variant)};}));}catch(error){if(!this.current(ticket))return[];throw error;}
  if(!this.current(ticket))return[];return prepared.map(cue=>{const at=anchor+bounded(cue.offset,0,.6);if(this.context.currentTime-at>.06)return false;return this.schedule(cue.buffer,cue.cue,cue.variant,cue.gain??.8,at,ticket);});
 }
 async dispose(){this.cancel();this.active.clear();this.enabled=false;const context=this.context;this.context=null;this.master=null;this.contextGeneration++;this.cache.clear();if(context&&context.state!=='closed')await context.close();}
}
