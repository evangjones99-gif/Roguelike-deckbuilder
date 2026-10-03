/** Original procedural sound research. No recordings, downloaded media or runtime edits. */
import fs from 'node:fs';
import crypto from 'node:crypto';
const rate=48000;
const specs={bind_seal:[.95,-10],summon_arrival:[1.25,-10],hound_bite:[.48,-10],warlord_iron:[.85,-10],wraith_magic:[1.3,-13],dragon_breath:[1.9,-10],hunter_wound:[.55,-12],camp_settle:[.8,-18],ui_confirm:[.16,-20],ui_back:[.13,-22]};
const seeded=seed=>{let state=seed>>>0||1;return()=>{state^=state<<13;state^=state>>>17;state^=state<<5;return(state>>>0)/4294967296;};};
function wave(name,variant){
 const [duration,peakDb]=specs[name],frames=Math.ceil(duration*rate),signal=new Float64Array(frames);
 const seed=crypto.createHash('sha256').update(`${name}/${variant}`).digest().readUInt32LE(),random=seeded(seed);
 const pitch=.96+random()*.08;
 function envelope(time,duration,attack=.003){return time<0||time>=duration?0:Math.min(1,time/attack)*Math.pow(1-time/duration,2);}
 function noise(start,length,strength,low,high=0,attack=.003,pulses=0){
  let lp=0,hpBase=0;const alpha=1-Math.exp(-2*Math.PI*low/rate),highAlpha=1-Math.exp(-2*Math.PI*high/rate);
  for(let i=0;i<Math.ceil(length*rate);i++){const t=i/rate,index=Math.round(start*rate)+i;if(index>=frames)break;
   lp+=alpha*((random()*2-1)-lp);hpBase+=highAlpha*(lp-hpBase);
   const modulation=pulses?.68+.32*Math.sin(t*2*Math.PI*pulses):1;
   signal[index]+=(high?lp-hpBase:lp)*strength*envelope(t,length,attack)*modulation;
  }
 }
 function mode(start,length,frequency,strength,endFrequency=frequency,attack=.002){
  let phase=0;for(let i=0;i<Math.ceil(length*rate);i++){const t=i/rate,index=Math.round(start*rate)+i;if(index>=frames)break;
   const hz=frequency*pitch*Math.pow(endFrequency/frequency,t/length);phase+=2*Math.PI*hz/rate;
   signal[index]+=Math.sin(phase)*strength*envelope(t,length,attack);
  }
 }
 function iron(start,strength=.3){noise(start,.035,strength,11000,1600);for(const [f,g,d]of [[379,.45,.19],[623,.31,.3],[1029,.19,.42],[1461,.13,.32],[1963,.08,.2]])mode(start,d,f,strength*g);}
 if(name==='bind_seal'){noise(0,.56,.7,700,120,.07);iron(.08,.23);iron(.19,.18);iron(.31,.13);mode(.28,.45,88,.16,53);noise(.34,.48,.16,2200,700,.02);}
 if(name==='summon_arrival'){noise(0,.6,1,520,70,.12,13);noise(.12,.44,.28,2100,400,.08);mode(.3,.55,94,.22,42);iron(.35,.24);iron(.44,.14);noise(.36,.6,.5,460,40,.003);}
 if(name==='hound_bite'){noise(0,.16,.8,540,100,.025,33);noise(.11,.035,.7,9000,2100);noise(.13,.18,1,1500,240);mode(.12,.22,119,.17,62);noise(.2,.19,.3,3000,500,.01);}
 if(name==='warlord_iron'){mode(0,.28,116,.28,48);noise(0,.04,1,13000,2400);noise(.025,.23,.65,800,120);iron(.004,.5);noise(.13,.36,.17,3100,700,.004);}
 if(name==='wraith_magic'){noise(0,.7,.8,2300,620,.15,7);noise(.28,.76,.55,900,220,.07,11);mode(.33,.66,112,.06,74,.1);mode(.36,.57,115,.04,77,.1);noise(.77,.37,.2,3900,1700,.003);}
 if(name==='dragon_breath'){noise(0,1.76,1.25,4200,180,.08,19);noise(.045,1.6,1.4,560,50,.09,31);noise(.08,1.48,.65,11000,2200,.06,43);mode(0,.4,75,.17,48,.02);noise(1.35,.4,.4,1800,300,.04);}
 if(name==='hunter_wound'){mode(0,.2,109,.17,55);noise(0,.095,1,1100,100);noise(.035,.15,.6,4100,1400);noise(.16,.31,.35,2400,500,.035);}
 if(name==='camp_settle'){noise(0,.18,.45,1500,450,.02);iron(.1,.065);noise(.18,.48,.22,3800,1000,.05,18);}
 if(name==='ui_confirm'){noise(0,.035,.8,2100,700);mode(.007,.07,173,.07,109);noise(.03,.08,.12,1700,200,.01);}
 if(name==='ui_back'){noise(0,.055,.6,1300,350,.006);mode(0,.065,119,.05,79);}
 const stereo=[new Float32Array(frames),new Float32Array(frames)];let rawPeak=0;
 for(let i=0;i<frames;i++){const x=signal[i],reflection=i>720?signal[i-720]*.08:0;
  stereo[0][i]=x+reflection;stereo[1][i]=x+(i>1104?signal[i-1104]*.065:0);rawPeak=Math.max(rawPeak,Math.abs(stereo[0][i]),Math.abs(stereo[1][i]));}
 const scale=Math.pow(10,peakDb/20)/(rawPeak||1);
 for(const channel of stereo)for(let i=0;i<frames;i++)channel[i]*=scale;
 const wav=Buffer.alloc(44+frames*4);wav.write('RIFF',0);wav.writeUInt32LE(wav.length-8,4);wav.write('WAVEfmt ',8);wav.writeUInt32LE(16,16);wav.writeUInt16LE(1,20);wav.writeUInt16LE(2,22);wav.writeUInt32LE(rate,24);wav.writeUInt32LE(rate*4,28);wav.writeUInt16LE(4,32);wav.writeUInt16LE(16,34);wav.write('data',36);wav.writeUInt32LE(frames*4,40);
 let energy=0,peak=0,dc=0,clipped=0;for(let i=0;i<frames;i++)for(let c=0;c<2;c++){const x=stereo[c][i];wav.writeInt16LE(Math.round(Math.max(-1,Math.min(1,x))*32767),44+(i*2+c)*2);energy+=x*x;dc+=x;peak=Math.max(peak,Math.abs(x));if(Math.abs(x)>=1)clipped++;}
 return{wav,stats:{name,variant,seed,sampleRate:rate,channels:2,duration,frames,bytes:wav.length,peakDbFS:20*Math.log10(peak),rmsDbFS:10*Math.log10(energy/(frames*2)),dcMean:dc/(frames*2),clippedSamples:clipped,sha256:crypto.createHash('sha256').update(wav).digest('hex')}};
}
fs.mkdirSync('scratch/audio-v07/wav',{recursive:true});const stats=[];
for(const name of Object.keys(specs))for(let variant=1;variant<=3;variant++){const {wav,stats:row}=wave(name,variant);fs.writeFileSync(`scratch/audio-v07/wav/${name}-${variant}.wav`,wav);stats.push(row);}
fs.writeFileSync('scratch/audio-v07/signal-measurements.json',JSON.stringify({method:'Original seeded DSP, PCM16 stereo 48kHz. Peak/RMS are computed signal measurements, not listening or loudness acceptance.',clips:stats},null,2)+'\n');
console.log(`Rendered ${stats.length} original deterministic WAV prototypes.`);
