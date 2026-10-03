import assert from 'node:assert/strict';
import {chromium} from '/workspace/Roguelike-deckbuilder/node_modules/playwright/index.mjs';
import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
const digest=process.argv[2],observe=process.argv.includes('--observe-blocker');assert.match(digest,/^[0-9a-f]{64}$/);
const root='/workspace/Roguelike-deckbuilder',out=root+'/reviews/gameplay-v0.5-runtime',runs=JSON.parse(gunzipSync(readFileSync(out+'/campaign-inputs.json.gz')).toString()).runs;
const path=out+`/settings-${observe?'blocker':'repaired'}-${digest.slice(0,8)}.json`;assert.equal(existsSync(path),false);
const browser=await chromium.launch({headless:true,executablePath:'/usr/bin/chromium',args:['--no-sandbox']}),results=[];
try{for(const kind of [1,2])for(const setting of ['null','{malformed']){
 const run=runs.find(r=>r.engineKind===kind),raw=' \n'+JSON.stringify(run.start)+'\n',c=await browser.newContext({viewport:{width:1440,height:900}});
 await c.addInitScript(({raw,setting})=>{if(localStorage.getItem('hollowpact.run.v2')===null)localStorage.setItem('hollowpact.run.v2',raw);localStorage.setItem('hollowpact.settings.v2',setting);localStorage.setItem('hollowpact.tutorial.v2','yes');},{raw,setting});
 const p=await c.newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));await p.goto('http://127.0.0.1:4173');const build=await(await p.request.get('http://127.0.0.1:4173/build-provenance.json')).json();assert.equal(build.sourceDigest,digest);const resumes=await p.locator('[data-ui="resume"]').count();assert.equal(resumes,observe?0:1);assert.equal(await p.evaluate(()=>localStorage.getItem('hollowpact.run.v2')),raw);
 let actionExact=false,reloadExact=false;if(!observe){await p.locator('[data-ui="resume"]').click();assert.equal(await p.evaluate(()=>localStorage.getItem('hollowpact.run.v2')),raw);const a=run.trace[0].action;await p.locator(a.type==='buy'?`[data-action="buy"][data-card="${a.card}"]`:`[data-action="travel"][data-choice="${a.choice}"]`).click();const saved=await p.evaluate(()=>localStorage.getItem('hollowpact.run.v2'));assert.equal(createHash('sha256').update(JSON.stringify(JSON.parse(saved))).digest('hex'),run.trace[0].afterHash);actionExact=true;await p.reload();await p.locator('[data-ui="resume"]').click();assert.equal(await p.evaluate(()=>localStorage.getItem('hollowpact.run.v2')),saved);reloadExact=true;}
 assert.deepEqual(errors,[]);results.push({kind,setting,build:digest,validRawUnchangedOnTitle:true,resumeCount:resumes,notice:await p.locator('.save-notice').count()?await p.locator('.save-notice').innerText():null,actualNextActionExact:actionExact,reloadExact,errors});await c.close();
}writeFileSync(path,JSON.stringify({method:'Independent actual production settings-corruption probe; campaign state produced by legal reference progression, exact primary raw bytes checked. Corrupt settings never injected into campaign data.',observeBlocker:observe,results},null,2)+'\n');console.log(JSON.stringify(results));}finally{await browser.close();}
