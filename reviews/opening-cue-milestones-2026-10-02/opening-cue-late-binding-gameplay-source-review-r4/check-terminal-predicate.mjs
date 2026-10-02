// Offline check only: extracts a pure predicate; never imports or executes the caller.
import fs from 'node:fs';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
const path='/workspace/scratch/opening-cue-late-binding-caller-source-r4/driver-cue.mjs';
const body=fs.readFileSync(path,'utf8');
const source=body.split('await page.waitForFunction(')[1].split(',phase,{timeout:waitMs,polling:100});')[0];
assert(source.startsWith('terminalPhase=>'));
const predicate=Function('document','return ('+source+');');
const base={phase:'reward',settling:false,busy:'false',dockHidden:true,arenaHidden:'true',heading:true,appPresent:true};
const cases=[
 ['settled reward with retained hidden dock markup',{},true],
 ['settled defeat',{phase:'defeat'},true,'defeat'],
 ['settled victory',{phase:'victory'},true,'victory'],
 ['wrong rendered phase',{phase:'battle'},false],
 ['final impact still settling',{settling:true},false],
 ['scene still busy',{busy:'true'},false],
 ['dock actionable',{dockHidden:false},false],
 ['arena still exposed',{arenaHidden:'false'},false],
 ['missing terminal heading',{heading:false},false],
 ['missing app',{appPresent:false},false],
];
const receipts=[];
for(const [label,change,expected,savedPhase='reward'] of cases){
 const state={...base,...change};
 const nodes={
  '#app':state.appPresent?{classList:{contains(name){return name==='phase-'+state.phase||(name==='settling-combat'&&state.settling);}}}:null,
  '#dock':{hidden:state.dockHidden,innerHTML:'<strong class="first-binding-cue">Choose a hostile.</strong>'},
  '#scene-ui':{getAttribute(){return state.busy;},querySelector(){return state.heading?{}:null;}},
  '#arena-wrap':{getAttribute(){return state.arenaHidden;}},
 };
 const document={querySelector(selector){return nodes[selector]??null;}};
 const actual=!!predicate(document)(savedPhase);
 assert.equal(actual,expected,label);
 receipts.push({label,savedPhase,actual,expected});
}
const receipt={offlineSourcePredicateOnly:true,noCallerImport:true,noAppBrowserServerOrBuild:true,driverSHA256:createHash('sha256').update(body).digest('hex'),cases:receipts,passed:true,peakRSSKiB:process.resourceUsage().maxRSS};
assert(receipt.peakRSSKiB<=65536,'Own offline Node peak exceeds 64MiB');
fs.writeFileSync('/workspace/scratch/opening-cue-late-binding-gameplay-source-review-r4/PREDICATE-CHECK.json',JSON.stringify(receipt,null,2)+'\n');
console.log(JSON.stringify({passed:true,cases:cases.length,peakRSSKiB:receipt.peakRSSKiB}));
