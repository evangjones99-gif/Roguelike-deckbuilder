/** Optional local presentation: never changes rules or saves. */
import { CuePlayer } from './audio-player.mjs';
import { cuesForTransition, type RoutedCue } from './audio-routing.mjs';
import { CREATURE_IMPACT_MS } from './art';
import type { GameState, TransitionEvent, Action } from './engine';
const families = ['bind_seal','summon_arrival','hound_bite','warlord_iron','wraith_magic','dragon_breath','hunter_wound','camp_settle','ui_confirm','ui_back','dragon_bite','scour_tool','neutral_hit'];
export function contactCues(before:GameState, after:GameState, events:readonly TransitionEvent[], action:Action, animated:boolean):RoutedCue[] {
 const delays=new Map<string,number>(), times=new Map<string,number>(); let wounds=0;
 const delayFor=(source:string, retaliation=false)=>{
  if(retaliation)return .04;
  if(action.type!=='endTurn'||!before.enemies.some(u=>u.uid===source))return 0;
  if(!delays.has(source))delays.set(source,delays.size*(after.phase!=='battle'?.009:.05));return delays.get(source)!;
 };
 for(const event of events){
  // Same branch order and source admission as current arena.playAction(); death adds no fabricated attack.
  if(event.type==='death')continue;
  const delay=animated && before.phase==='battle' ? CREATURE_IMPACT_MS/1000+delayFor(event.source,event.type==='hit'&&event.kind==='retaliation') : 0;
  if(event.type==='hit'){
   const key=`strike/${event.source}/${event.kind}/${('cardId' in event?event.cardId:'')||''}`;if(!times.has(key))times.set(key,delay);
   if(event.damage>0&&event.target==='hunter'&&event.hpLost>0&&wounds<2)times.set(`wound/${wounds++}`,delay);
  }else if(event.type==='summon'){times.set(`bind/${event.target}`,delay);times.set(`arrival/${event.target}`,delay);}
  else if(event.type==='control'||event.type==='ward'){const key=`seal/${event.source}/${('cardId' in event?event.cardId:'')||''}`;if(!times.has(key))times.set(key,delay);}
  // Buff/heal also reserve caster position in renderer order even without an authored corresponding cue.
 }
 return cuesForTransition(before,after,events,action).map(cue=>({...cue,offset:times.get(cue.key)??0}));
}
export interface ContactCuePlan { cues:RoutedCue[]; anchorOffsetSeconds:number }
/** Renderer-owned allocation/queue lead precedes the existing impact offsets.
 * Keep that lead on the audio anchor: CuePlayer intentionally bounds each cue's
 * contact offset to .6s, which must not truncate a longer presentation queue. */
export function contactCuePlan(before:GameState, after:GameState, events:readonly TransitionEvent[], action:Action, animated:boolean, presentationDelayMs=0):ContactCuePlan {
 const anchorOffsetSeconds=animated&&before.phase==='battle'&&Number.isFinite(presentationDelayMs)&&presentationDelayMs>0 ? presentationDelayMs/1000 : 0;
 return {cues:contactCues(before,after,events,action,animated),anchorOffsetSeconds};
}
export class HostAudio {
 readonly player:CuePlayer;
 private epoch=0;private activating:Promise<boolean>|null=null; private hidden=false;private closed=false;private warmed=false;private nativeBlocked=false;private nativeController=false;
 constructor(base:string){this.player=new CuePlayer(base);}
 gesture(){
  if(this.closed||this.hidden||this.nativeBlocked||this.player.muted||this.player.volume<=0)return;
  if(this.activating||this.warmed&&this.player.context?.state==='running')return;
  const epoch=this.epoch;
  this.activating=this.player.enable().then(async enabled=>{
   if(!enabled||epoch!==this.epoch||this.closed||this.hidden||this.nativeBlocked){this.player.cancel();return false;}
   const results=await Promise.allSettled(families.flatMap(cue=>[1,2,3].map(variant=>this.player.load(cue,variant))));
   const decoded=results.filter(r=>r.status==='fulfilled').length;this.warmed=decoded===39;return true;
  }).catch(()=>false).finally(()=>{this.activating=null;});
 }
 nativeSetup(){this.nativeController=true;}
 controllerGesture(){if(this.nativeController)this.gesture();}
 nativeLifecycle(blocked:boolean){this.cancel(blocked?'native-inactive':'native-restore-barrier');this.nativeBlocked=blocked;return this.epoch;}
 settings(mute:boolean,volume:number){this.player.settings(mute,volume);if(mute||volume<=0)this.epoch++;}
 cancel(reason:string){this.epoch++;this.player.cancel();}
 visibility(hidden:boolean){this.hidden=hidden;if(hidden)this.cancel('hidden');}
 ui(back=false){if(this.closed||this.hidden||this.nativeBlocked)return;void this.player.play(back?'ui_back':'ui_confirm',.4).catch(()=>{});}
 transition(before:GameState,after:GameState,events:readonly TransitionEvent[],action:Action,animated:boolean,presentationDelayMs=0){
  if(this.closed||this.hidden||this.nativeBlocked||!this.player.enabled)return;
  const canonical=JSON.stringify({before,after,events,action});
  const plan=contactCuePlan(before,after,events,action,animated,presentationDelayMs);
  if(JSON.stringify({before,after,events,action})!==canonical)throw new Error('Audio observer mutated rules');
  const anchor=this.player.context!.currentTime+plan.anchorOffsetSeconds;
  void this.player.playBatchAt(plan.cues,anchor).catch(()=>{});
 }
 async dispose(){this.closed=true;this.cancel('dispose');await this.player.dispose();}
}
