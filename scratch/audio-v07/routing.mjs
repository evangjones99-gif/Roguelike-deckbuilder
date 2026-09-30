/** Proposed observer only. Consumes resolved events; never predicts or applies rules. */
export function cuesForTransition(previous,next,events,action){
 const units=new Map([...previous.allies,...previous.enemies,...next.allies,...next.enemies].map(unit=>[unit.uid,unit]));
 const result=[],groups=new Set();let wounds=0;
 const add=(cue,key,gain=1)=>{if(groups.has(key))return;groups.add(key);result.push({cue,key,gain,offset:Math.min(.4,result.length*.035)});};
 for(const event of events){
  if(event.type==='summon'){if(event.side==='ally')add('bind_seal',`bind/${event.target}`,.6);add('summon_arrival',`arrival/${event.target}`,event.side==='ally'?.8:.6);continue;}
  if(event.type==='control'||event.type==='ward'){add('bind_seal',`seal/${event.source}/${event.cardId||''}`,.45);continue;}
  if(event.type!=='hit'||event.damage<=0)continue;
  const species=units.get(event.source)?.species;
  const cue=species==='hound'?'hound_bite':species==='dragon'?'dragon_breath':['wraith','necromancer'].includes(species)?'wraith_magic':'warlord_iron';
  // One source attack/body cue for an actual multitarget transition; never seven breaths.
  add(cue,`strike/${event.source}/${event.kind}/${event.cardId||''}`,event.hpLost>0?.8:.4);
  if(event.target==='hunter'&&event.hpLost>0&&wounds<2){add('hunter_wound',`wound/${wounds++}`,.7);}
 }
 if(action?.type==='camp')add('camp_settle','camp',.6);
 if(!result.length&&!events.some(event=>event.type==='hit'))add('ui_confirm','accepted-ui',.4);
 return result.slice(0,8);
}
