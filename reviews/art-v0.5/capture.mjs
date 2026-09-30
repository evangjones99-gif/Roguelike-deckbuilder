import {chromium} from '@playwright/test';
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
const ROOT='/workspace/Roguelike-deckbuilder';
const OUT=path.join(ROOT,'reviews/art-v0.5');
const browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox']});
const records={scope:'Independent CSS-only art study, not runtime QA or human preference data',method:'Original RGB sheet as CSS background; equal quadrant cells with 2px source inset; cover within cell and explicit px offset. No art image editing.',views:[],hashes:{}};
try{
 const page=await browser.newPage();const failures=[];page.on('pageerror',e=>failures.push(String(e)));page.on('requestfailed',r=>failures.push(r.url()+': '+r.failure()?.errorText));
 for(const width of [1440,1280,390]){
  await page.setViewportSize({width,height:900});await page.goto('http://127.0.0.1:5185/reviews/art-v0.5/prototype.html');await page.locator('.source').waitFor();await page.evaluate(async()=>{await Promise.all([...document.images].map(i=>i.decode()));await document.fonts.ready});
  await page.screenshot({path:path.join(OUT,`study-${width}.png`),fullPage:true});
  if(width===1440){for(const id of ['large','pairs','narrow','focused','recommended','anchors']) await page.locator('#'+id).screenshot({path:path.join(OUT,id+'.png')});}
  records.views.push(await page.evaluate(()=>({width:innerWidth,horizontalOverflow:document.documentElement.scrollWidth>innerWidth,source:{width:document.querySelector('.source').naturalWidth,height:document.querySelector('.source').naturalHeight},samples:[...document.querySelectorAll('.card')].map(c=>({name:c.querySelector('.name').textContent,classes:c.className,banner:c.querySelector('.banner').getBoundingClientRect().toJSON(),crop:c.querySelector('.banner').dataset.sourceWindow??null,costInside:c.querySelector('.cost').getBoundingClientRect().right<=c.getBoundingClientRect().right,rulesInside:c.querySelector('.rules').getBoundingClientRect().bottom<=c.getBoundingClientRect().bottom,rulesFont:getComputedStyle(c.querySelector('.rules')).fontSize}))})));}
 records.failures=failures;
 for(const f of ['assets/art-sources/v0.5/tool-vignettes-still-life.png','src/main.ts','src/style.css','src/content.ts','reviews/art-v0.5/prototype.html','reviews/art-v0.5/capture.mjs']) records.hashes[f]=crypto.createHash('sha256').update(await fs.readFile(path.join(ROOT,f))).digest('hex');
 await fs.writeFile(path.join(OUT,'capture.json'),JSON.stringify(records,null,2)+'\n');
 console.log(JSON.stringify({failures,views:records.views.map(v=>({width:v.width,overflow:v.horizontalOverflow,cards:v.samples.length,contained:v.samples.every(c=>c.costInside&&c.rulesInside)})),hashes:records.hashes},null,2));
}finally{await browser.close();}
