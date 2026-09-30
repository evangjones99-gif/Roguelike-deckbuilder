import fs from'node:fs';import{validateState,applyActionWithEvents}from'../../src/engine';import{ENEMIES}from'../../src/content';
const out='/workspace/Roguelike-deckbuilder/reviews/arena-v0.6-contact',old=JSON.parse(fs.readFileSync('/workspace/Roguelike-deckbuilder/reviews/visual-v0.5-runtime/affected-final/fixtures.json','utf8')).cases,cases:any[]=[];
function add(name:string,before:any,action:any){const unchanged=JSON.stringify(before);const r=applyActionWithEvents(before,action);if(JSON.stringify(before)!==unchanged||!validateState(before)||!validateState(r.state))throw Error('Invalid or mutated '+name);cases.push({name,before,action,...r})}
for(const c of old)add(c.name,c.before,c.action);
const fullL=old.find((c:any)=>c.name==='hound-leftward'),fullR=old.find((c:any)=>c.name==='hound-rightward');
for(const [name,base,target]of [['hound-near-left',fullL,'e34'],['hound-near-right',fullR,'e31'],['hound-vertical',fullR,'e30']]as const){add(name,structuredClone(base.before),{...base.action,target})}
const blocked=structuredClone(fullL.before);blocked.enemies[0].block=50;add('hound-far-left-blocked',blocked,fullL.action);
const counter=structuredClone(fullL.before);counter.enemies[0]={...counter.enemies[0],...ENEMIES.ironjaw,cardId:'ironjaw',maxHp:112,hp:20,block:3};add('hound-far-left-counter',counter,fullL.action);
const mutual=structuredClone(counter);mutual.allies.find((a:any)=>a.uid===fullL.action.unit).hp=2;mutual.enemies[0].hp=2;add('hound-far-left-mutual-death',mutual,fullL.action);
const duel=structuredClone(old.find((c:any)=>c.name==='warleader-nonlethal-reaction').before);const unit=duel.allies.find((a:any)=>/hound/.test(a.species));unit.acted=false;add('hound-duel-short-range',duel,{type:'attack',unit:unit.uid,target:duel.enemies[0].uid});
fs.writeFileSync(out+'/fixtures.json',JSON.stringify({provenance:'First11 independent v0.5 final reviewer diagnostic fixtures, preserved unchanged in old evidence; additional validated contact probes. Canonical engine/events unchanged; no natural reachability claim.',cases},null,2));console.log(cases.map(x=>x.name))
