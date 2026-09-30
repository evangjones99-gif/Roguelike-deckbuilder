import{chromium}from'../node_modules/playwright/index.mjs';import{readFileSync,writeFileSync}from'node:fs';
if(process.argv[2]!=='--go')throw Error('Wait for root production freeze GO');
const root=process.cwd(),endpoint=process.argv[3]||'http://127.0.0.1:4173',input=JSON.parse(readFileSync('reviews/gameplay-v0.4-preview-fixtures.json','utf8'));
const browser=await chromium.launch({headless:true,executablePath:'/usr/bin/chromium',args:['--no-sandbox']}),results=[];
try{for(const f of input.fixtures){
 const context=await browser.newContext({viewport:{width:1440,height:900},reducedMotion:'no-preference'}),page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.addInitScript(state=>{localStorage.setItem('hollowpact.run.v2',JSON.stringify(state));localStorage.setItem('hollowpact.settings.v2',JSON.stringify({mute:true,volume:0,motion:true}));localStorage.setItem('hollowpact.tutorial.v2','yes');},f.state);
 await page.goto(endpoint);const servedBuild=(await(await page.request.get(endpoint+'/build-provenance.json')).json()).sourceDigest;await page.locator('[data-ui="resume"]').click();
 const snapshot=await page.evaluate(()=>JSON.stringify(Object.entries(localStorage))),a=f.action;
 if(a.type==='attack')await page.locator(`[data-unit="${a.unit}"]`).click();
 else if(a.target)await page.locator(`[data-ui="play-card"][data-index="${a.index}"]`).click();
 else await page.locator(`[data-ui="play-card"][data-index="${a.index}"]`).hover();
 if(a.target)await page.locator(`[data-unit="${a.target}"]`).hover();
 const preview=await page.locator('#consequence-preview').innerText();for(const text of f.expected)if(!preview.includes(text))throw Error(`${f.name} preview missing ${text}: ${preview}`);
 const unchanged=snapshot===await page.evaluate(()=>JSON.stringify(Object.entries(localStorage)));if(!unchanged)throw Error('Preview mutated storage');
 const saved=await page.evaluate(()=>JSON.parse(localStorage.getItem('hollowpact.run.v2')));if(JSON.stringify(saved)!==JSON.stringify(f.state))throw Error('Preview changed canonical state/RNG');
 const aria={role:await page.locator('#consequence-preview').getAttribute('role'),live:await page.locator('#consequence-preview').getAttribute('aria-live')};
 await page.screenshot({path:`${root}/reviews/gameplay-v0.4-preview-${f.name}.png`});
 if(a.target){await page.keyboard.press('Escape');const instruction=await page.locator('#consequence-preview').innerText();if(instruction===preview)throw Error('Cancel leaves old consequence');if(snapshot!==await page.evaluate(()=>JSON.stringify(Object.entries(localStorage))))throw Error('Cancel changed state');if(a.type==='attack')await page.locator(`[data-unit="${a.unit}"]`).click();else await page.locator(`[data-ui="play-card"][data-index="${a.index}"]`).click();await page.locator(`[data-unit="${a.target}"]`).click();}
 else await page.locator(`[data-ui="play-card"][data-index="${a.index}"]`).click();
 const after=await page.evaluate(()=>JSON.parse(localStorage.getItem('hollowpact.run.v2')));if(JSON.stringify(after)!==JSON.stringify(f.after))throw Error(`${f.name} actual result differs from independently asserted fixture`);
 await page.waitForFunction(()=>!document.querySelector('#app').classList.contains('settling-combat'));
 results.push({name:f.name,servedBuild,preview,storageUnchanged:unchanged,canonicalStateAndRngUnchanged:true,actualResultMatchesExpected:true,aria,errors,method:'Production controls on disclosed structurally valid unearned fixture. Literal expected outcomes asserted independently in fixture generator. Preview, Escape cancel and actual saved resolution compared.'});await context.close();
}const path='reviews/gameplay-v0.4-evidence.json',e=JSON.parse(readFileSync(path,'utf8'));e.previewBrowser=results;writeFileSync(path,JSON.stringify(e,null,2)+'\n');console.log(JSON.stringify(results));}finally{await browser.close();}
