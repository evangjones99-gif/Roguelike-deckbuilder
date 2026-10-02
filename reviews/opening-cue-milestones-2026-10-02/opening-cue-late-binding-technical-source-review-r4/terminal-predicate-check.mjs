import assert from 'node:assert/strict';
const predicate=terminalPhase=>{const app=document.querySelector('#app'),dock=document.querySelector('#dock'),scene=document.querySelector('#scene-ui');return !!app&&app.classList.contains('phase-'+terminalPhase)&&!app.classList.contains('settling-combat')&&scene?.getAttribute('aria-busy')!=='true'&&dock?.hidden===true&&document.querySelector('#arena-wrap')?.getAttribute('aria-hidden')==='true'&&!!scene?.querySelector('h1');};
let cases=0;
function test(v,want,phase='reward') {
const nodes={'#app':v.app?{classList:{contains:k=>k==='settling-combat'?v.settling:k==='phase-'+v.phase}}:null,'#dock':{hidden:v.hidden},'#scene-ui':{getAttribute:()=>v.busy?'true':null,querySelector:()=>v.heading?{}:null},'#arena-wrap':{getAttribute:()=>v.arenaHidden?'true':'false'}};
globalThis.document={querySelector:k=>nodes[k]};assert.equal(!!predicate(phase),want);cases++;
}
const ready={app:true,phase:'reward',settling:false,busy:false,hidden:true,heading:true,arenaHidden:true};
test(ready,true);test({...ready,retainedCuePresent:true},true);
for(const [k,v] of [['app',false],['settling',true],['busy',true],['hidden',false],['heading',false],['arenaHidden',false],['phase','battle']])test({...ready,[k]:v},false);
for(const phase of ['victory','defeat'])test({...ready,phase},true,phase);
console.log(JSON.stringify({pureExactPredicateCases:cases}));
