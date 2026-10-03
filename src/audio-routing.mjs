/** Read-only event routing by actual creature identity and aggregate consequence. */
export function cuesForTransition(previous,next,events,action){
 const units=new Map([...next.allies,...next.enemies,...previous.allies,...previous.enemies].map(unit=>[unit.uid,unit]));
 const cues=[],groups=new Map();let wounds=0;
 const add=(cue,key,gain,priority,order,details={})=>cues.push({cue,key,gain,priority,offset:Math.min(.4,order*.035),...details});
 for(let index=0;index<events.length;index++){const event=events[index];
  if(event.type==='summon'){if(event.side==='ally')add('bind_seal',`bind/${event.target}`,.6,30,index);add('summon_arrival',`arrival/${event.target}`,event.side==='ally'?.8:.6,50,index);continue;}
  if(event.type==='control'||event.type==='ward'){const key=`seal/${event.source}/${event.cardId||''}`;if(!cues.some(cue=>cue.key===key))add('bind_seal',key,.45,30,index);continue;}
  if(event.type!=='hit'||event.damage<=0)continue;
  const key=`strike/${event.source}/${event.kind}/${event.cardId||''}`;
  if(!groups.has(key))groups.set(key,{key,source:event.source,kind:event.kind,cardId:event.cardId,index,hpLost:0,blocked:0,targets:new Set()});
  const group=groups.get(key);group.hpLost+=event.hpLost;group.blocked+=event.blocked;group.targets.add(event.target);
  if(event.target==='hunter'&&event.hpLost>0&&wounds<2)add('hunter_wound',`wound/${wounds++}`,.7,100,index,{hpLost:event.hpLost});
 }
 for(const group of groups.values()){
  const unit=units.get(group.source),species=unit?.species;let cue='neutral_hit';
  if(group.kind==='spell'&&group.cardId?.replace(/\+$/,'')==='scour')cue='scour_tool';
  else if(species==='hound')cue='hound_bite';
  else if(species==='dragon')cue=group.targets.size>1||unit.intent?.target==='all'||/breath|firestorm/i.test(unit.intent?.label||'')?'dragon_breath':'dragon_bite';
  else if(species==='warlord')cue='warlord_iron';
  else if(['wraith','necromancer'].includes(species))cue='wraith_magic';
  add(cue,group.key,group.hpLost>0?.8:.4,50,group.index,{aggregateHpLost:group.hpLost,aggregateBlocked:group.blocked,affectedTargets:group.targets.size});
 }
 if(action?.type==='camp')add('camp_settle','camp',.6,10,events.length);
 if(!cues.length&&!events.some(event=>event.type==='hit'))add('ui_confirm','accepted-ui',.4,10,0);
 return cues.sort((a,b)=>b.priority-a.priority||a.offset-b.offset).slice(0,8);
}
