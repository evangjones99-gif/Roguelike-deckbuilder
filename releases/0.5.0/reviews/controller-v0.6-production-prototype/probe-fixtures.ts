import {readFileSync,writeFileSync} from 'node:fs';
import {applyAction,validateState,createGame} from '/workspace/Roguelike-deckbuilder/src/engine.ts';
const root='/workspace/Roguelike-deckbuilder/';
const full=JSON.parse(readFileSync(root+'reviews/screenshots-v0.2/full-fixture.json','utf8'));
if(!validateState(full))throw Error('Legacy fixture must stay valid');
const command={type:'attack',unit:full.allies[0].uid,target:full.enemies[0].uid} as const;
const kind2=applyAction(createGame(121),{type:'travel',choice:'battle'});
const pool=[...kind2.hand,...kind2.draw,...kind2.discard];
const hand=['cairnhound','sutures','scour'];for(const id of hand){const at=pool.indexOf(id);if(at<0)throw Error('Starter card not in live deck');pool.splice(at,1);}
kind2.hand=hand;kind2.draw=pool;kind2.discard=[];
if(!validateState(kind2))throw Error('Kind2 fixture must conserve cards');
const summon={type:'play',index:0} as const;
writeFileSync('/workspace/scratch/controller-v06-production-input/probe-fixtures.json',JSON.stringify({syntheticFixtures:true,full,command,expectedCommand:applyAction(full,command),kind2,summon,expectedSummon:applyAction(kind2,summon),digest:JSON.parse(readFileSync(root+'dist/build-provenance.json','utf8')).sourceDigest},null,2));
console.log('Prepared validated legacy and kind2 canonical fixture expectations.');
