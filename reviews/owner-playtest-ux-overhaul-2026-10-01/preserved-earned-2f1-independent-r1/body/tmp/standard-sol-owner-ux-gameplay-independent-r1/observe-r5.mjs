// Prepared independent observation harness. No game imports or synthetic play.
import fs from 'node:fs/promises';
import path from 'node:path';
import readline from 'node:readline';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
const HERE=path.dirname(fileURLToPath(import.meta.url));
assert.equal(process.argv[2],'--root-browser-grant','ROOT must grant exclusive browser window first');
const [variant,seed,difficulty,widthText]=process.argv.slice(3);
assert(['candidate','baseline'].includes(variant));
assert(/^\d+$/.test(seed)&&['0','1','2'].includes(difficulty));
const width=Number(widthText);assert([1440,390].includes(width));
const resume=process.argv[7]==='--resume';assert(process.argv.length===(resume?8:7));
const profile=path.join(HERE,'profile-'+variant+'-'+seed+'-'+difficulty);
if(resume){assert((await fs.stat(profile)).isDirectory(),'trusted-play profile must already exist');}
else await fs.mkdir(profile,{recursive:false});
const expected=variant==='candidate'?'2f1fd23d0af5d43d7ee1ed9242063404bd242702df44d2db7b15f007e8306629':'801db1ce4000c15268569cb047e7388148a65105c7b86208611ceb3aff40f029';
const baseURL=variant==='candidate'?'http://127.0.0.1:4777':'http://127.0.0.1:4173';
const H=b=>crypto.createHash('sha256').update(b).digest('hex');
const auditRaw=await fs.readFile(path.join(HERE,'AUDIT-before.json'));
const audit=JSON.parse(auditRaw);assert.equal(audit.variants[variant].sourceDigest,expected);
const M=1048576,work=640*M,reserve=512*M,evidenceLimit=64*M;
const initial=Number(await fs.readFile('/sys/fs/cgroup/memory.current','utf8'));
const maximum=Number(await fs.readFile('/sys/fs/cgroup/memory.max','utf8'));
assert(maximum-initial>=work+reserve,'fresh browser admission lacks640MiB+512MiB');
let v=await fs.statfs(HERE);assert(v.bavail*v.bsize>=evidenceLimit+M);
const run=path.join(HERE,'run-'+variant+'-'+seed+'-'+Date.now());
await fs.mkdir(run,{recursive:false});
const browserTmp=await fs.mkdtemp('/tmp/gp-');
const log=await fs.open(path.join(run,'ACTIONS.jsonl'),'wx');
let bytes=0,sequence=0,browser,page,timer,lines,breached=false;
async function record(value){
  const b=Buffer.from(JSON.stringify({sequence:sequence++,wallUTC:new Date().toISOString(),monotonicMs:performance.now(),...value})+'\n');
  assert(bytes+b.length<=evidenceLimit,'evidence budget');
  await log.write(b);await log.sync();bytes+=b.length;
}
async function sample(label){
  const current=Number(await fs.readFile('/sys/fs/cgroup/memory.current','utf8'));
  const vf=await fs.statfs(run);
  const row={label,current,maximum,delta:current-initial,headroom:maximum-current,free:vf.bavail*vf.bsize,evidenceBytes:bytes};
  if(!(row.delta<=work&&row.headroom>=reserve&&row.free>=M)){breached=true;const e=new Error('browser resource admission breached '+JSON.stringify(row));e.resource=row;throw e;}
  return row;
}
async function observation(){
  return page.evaluate(async()=>{
    const shown=e=>{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width>0&&r.height>0&&s.display!=='none'&&s.visibility!=='hidden'};
    const buttons=[...document.querySelectorAll('button,input,label')].filter(shown).slice(0,200).map(e=>({tag:e.tagName,text:e.innerText||'',label:e.getAttribute('aria-label'),ui:e.dataset.ui,action:e.dataset.action,unit:e.dataset.unit,card:e.dataset.card,index:e.dataset.index,choice:e.dataset.choice,disabled:e.disabled,ariaDisabled:e.getAttribute('aria-disabled'),name:e.getAttribute('name'),value:e instanceof HTMLInputElement?e.value:undefined,classes:e.className}));
    const raw=localStorage.getItem('hollowpact.run.v2');
    const saveSHA256=raw===null?null:[...new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(raw)))].map(n=>n.toString(16).padStart(2,'0')).join('');
    return {viewport:{width:innerWidth,height:innerHeight},visibleText:document.body.innerText.slice(0,18000),buttons,preview:document.querySelector('#consequence-preview')?.textContent||null,announcer:document.querySelector('#announcer')?.textContent||null,dialog:document.querySelector('dialog[open]')?.innerText||null,focus:{tag:document.activeElement?.tagName,ui:document.activeElement?.dataset.ui,unit:document.activeElement?.dataset.unit},saveSHA256,events:window.__independentGameplayEvents.splice(0)};
  });
}
async function locate(c){
  assert(typeof c.selector==='string'&&c.selector.length<500);
  const loc=page.locator(c.selector).nth(c.index??0);
  assert(await loc.isVisible(),'control not visibly present');
  assert(!await loc.isDisabled(),'control disabled');
  await loc.scrollIntoViewIfNeeded();
  let box=await loc.boundingBox();assert(box&&box.width&&box.height);
  await page.mouse.move(box.x+box.width/2,box.y+box.height/2);
  await page.waitForTimeout(240);box=await loc.boundingBox();assert(box);
  const x=box.x+box.width/2,y=box.y+box.height/2;
  await page.mouse.move(x,y);
  assert(await loc.evaluate((e,p)=>{const hit=document.elementFromPoint(p.x,p.y);return e===hit||e.contains(hit)},{x,y}),'intended control center is obstructed');
  return {loc,x,y};
}
try{
  await record({kind:'ADMISSION',variant,intendedSeed:seed,intendedDifficulty:Number(difficulty),sourceDigest:expected,auditSHA256:H(auditRaw),harnessSHA256:H(await fs.readFile(fileURLToPath(import.meta.url))),browserTmp,profile,resume,initial,maximum,work,reserve,run,independence:'Only unrelated retirement tooling previously authored; no game implementation'});
  const {chromium}=await import('/workspace/Roguelike-deckbuilder/node_modules/playwright/index.mjs');
  browser=await chromium.launchPersistentContext(profile,{executablePath:'/usr/bin/chromium',args:['--no-sandbox'],env:{...process.env,TMPDIR:browserTmp},viewport:{width,height:width===390?844:900},deviceScaleFactor:1});
  const context=browser;
  // Observation only: no settings/tutorial/save writes, canvas hook or clock.
  await context.addInitScript(()=>{
    window.__independentGameplayEvents=[];
    for(const type of ['pointerdown','pointerup','click','keydown','keyup','input','change','focusin'])document.addEventListener(type,e=>{
      const t=e.target;
      window.__independentGameplayEvents.push({type,isTrusted:e.isTrusted,key:e.key,ui:t.closest?.('[data-ui]')?.dataset.ui,unit:t.closest?.('[data-unit]')?.dataset.unit,action:t.closest?.('[data-action]')?.dataset.action,card:t.closest?.('[data-card]')?.dataset.card,at:performance.now()});
      if(window.__independentGameplayEvents.length>1000)window.__independentGameplayEvents.splice(0,500);
    },true);
  });
  page=await context.newPage();
  page.on('pageerror',e=>record({kind:'PAGE_ERROR',message:e.message}).catch(()=>{}));
  page.on('requestfailed',r=>record({kind:'REQUEST_FAILED',url:r.url(),failure:r.failure()}).catch(()=>{}));
  const served=await page.request.get(baseURL+'/build-provenance.json');assert(served.ok());
  assert.equal((await served.json()).sourceDigest,expected,'served build mismatch');
  await page.goto(baseURL,{waitUntil:'domcontentloaded'});
  await page.locator('[data-ui="new"]').first().waitFor();
  await record({kind:'READY',observation:await observation(),resource:await sample('browser-ready')});
  console.log(JSON.stringify({ready:true,run,variant,intendedSeed:seed}));
  timer=setInterval(()=>{sample('periodic').catch(async e=>{breached=true;await record({kind:'RESOURCE_FAILURE',error:e.message,resource:e.resource}).catch(()=>{});await browser.close();lines?.close()})},1000);
  lines=readline.createInterface({input:process.stdin,crlfDelay:Infinity});
  for await(const line of lines){
    if(!line.trim())continue;
    let c;
    try{
      c=JSON.parse(line);assert(typeof c.command==='string');
      if(!['observe','wait','shot','note','finish'].includes(c.command))assert(typeof c.rationale==='string'&&c.rationale.length>=8&&c.rationale.length<=1500,'action requires visible-evidence rationale');
      await record({kind:'BEFORE',command:c,observation:await observation(),resource:await sample('before-command')});
      const started=performance.now();
      if(c.command==='click'){const {x,y}=await locate(c);await page.mouse.down();await page.waitForTimeout(60);await page.mouse.up();}
      else if(c.command==='hover'){await locate(c);}
      else if(c.command==='key'){assert(typeof c.key==='string'&&c.key.length<=50);await page.keyboard.press(c.key);}
      else if(c.command==='type'){assert(typeof c.text==='string'&&c.text.length<=1000);await page.keyboard.type(c.text,{delay:35});}
      else if(c.command==='wait'){assert(Number.isInteger(c.ms)&&c.ms>=0&&c.ms<=2000);await page.waitForTimeout(c.ms);}
      else if(c.command==='resize'){assert([1440,390].includes(c.width));assert([900,844].includes(c.height));await page.setViewportSize({width:c.width,height:c.height});}
      else if(c.command==='reload'){await page.reload({waitUntil:'domcontentloaded'});}
      else if(c.command==='shot'){
        assert(/^[a-z0-9-]{1,60}$/.test(c.label));
        const file=path.join(run,sequence+'-'+c.label+'.jpg');
        const b=await page.screenshot({type:'jpeg',quality:75});assert(bytes+b.length<=evidenceLimit);
        await fs.writeFile(file,b,{flag:'wx'});bytes+=b.length;
        await record({kind:'CAPTURE',path:file,bytes:b.length,sha256:H(b),personallyViewed:false});
      }else if(c.command==='note'){assert(typeof c.text==='string'&&c.text.length<=3000);}
      else if(!['observe','finish'].includes(c.command))throw Error('unknown command');
      await record({kind:'AFTER',command:c,actionElapsedMs:performance.now()-started,observation:await observation(),resource:await sample('after-command')});
      console.log(JSON.stringify({completed:c.command,sequence,observation:await observation()}));
      if(c.command==='finish'){lines.close();break;}
    }catch(e){await record({kind:'COMMAND_FAILED',command:c||line.slice(0,1500),error:e.stack,resource:e.resource});console.log(JSON.stringify({commandFailed:true,error:e.message}));if(breached){lines.close();throw e;}}
  }
}catch(e){await record({kind:'RUN_FAILED',error:e.stack,breached}).catch(()=>{});throw e;}
finally{clearInterval(timer);await browser?.close();await record({kind:'BROWSER_CLOSED',breached}).catch(()=>{});await log.close();}
