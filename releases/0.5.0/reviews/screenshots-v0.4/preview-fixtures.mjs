import fs from'node:fs/promises';import{validateState,applyActionWithEvents,legalActions}from'../../src/engine.ts';import{ENEMIES}from'../../src/content.ts';
const full=JSON.parse(await fs.readFile('reviews/screenshots-v0.2/full-fixture.json','utf8'));
function sparse(){const s=structuredClone(full);s.allies=s.allies.slice(0,1);s.enemies=s.enemies.slice(0,1);s.deck=[s.allies[0].cardId,'scour','silence','sutures','gravetithe','bloodprice','sunder'];s.hand=['scour','silence','sutures','gravetithe','bloodprice'];s.draw=['sunder'];s.discard=[];return s}
const cases=[];
let s=sparse();s.allies[0].hp=2;s.allies[0].attack=7;s.enemies[0]={...s.enemies[0],...ENEMIES.ironjaw,cardId:'ironjaw',hp:2,maxHp:ENEMIES.ironjaw.hp,block:3};cases.push({id:'mutual-lethal',state:s,action:{type:'attack',unit:s.allies[0].uid,target:s.enemies[0].uid}});
s=sparse();s.allies[0].hp=1;cases.push({id:'heal-binding',state:s,action:{type:'play',index:s.hand.indexOf('sutures'),target:s.allies[0].uid}});
s=sparse();cases.push({id:'silence-enemy',state:s,action:{type:'play',index:s.hand.indexOf('silence'),target:s.enemies[0].uid}});
s=sparse();s.hp=1;cases.push({id:'self-lethal',state:s,action:{type:'play',index:s.hand.indexOf('bloodprice')}});
s=sparse();s.hp=60;cases.push({id:'siphon-heal',state:s,action:{type:'play',index:s.hand.indexOf('gravetithe'),target:s.enemies[0].uid}});
s=structuredClone(full);const wanted=['scour','sunder','killcommand','silence','sutures'];for(const old of s.hand)s.draw.push(old);s.hand=[];for(const id of wanted){const at=s.draw.indexOf(id);if(at<0)throw Error('Missing '+id);s.draw.splice(at,1);s.hand.push(id)}s.enemies[0]={...s.enemies[0],...ENEMIES.ironjaw,cardId:'ironjaw',hp:2,maxHp:ENEMIES.ironjaw.hp,block:3};s.allies[0].hp=2;s.allies[0].attack=7;cases.push({id:'full-roster-counter',state:s,action:{type:'attack',unit:s.allies[0].uid,target:s.enemies[0].uid}});
for(const c of cases){if(!validateState(c.state))throw Error('Invalid '+c.id);if(!legalActions(c.state).some(a=>JSON.stringify(a)===JSON.stringify(c.action)))throw Error('Illegal '+c.id);c.expected=applyActionWithEvents(c.state,c.action)}
await fs.writeFile('reviews/screenshots-v0.4/preview-fixtures.json',JSON.stringify(cases,null,2));console.log(cases.map(c=>({id:c.id,phase:c.expected.state.phase,hits:c.expected.events.filter(e=>e.type==='hit'),events:c.expected.events.length})));
