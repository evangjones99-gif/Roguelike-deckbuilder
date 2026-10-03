/** Run only after root releases the production FPS-comparison pause. */
import { chromium } from 'playwright';
import { mkdir, writeFile, readFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import path from 'node:path';
const root=path.resolve(import.meta.dirname,'../../..');
const out=path.join(import.meta.dirname,'shadow-prototype-captures');await mkdir(out,{recursive:true});
const browser=await chromium.launch({headless:true,executablePath:'/usr/bin/chromium',args:['--no-sandbox']});
const page=await browser.newPage({viewport:{width:1440,height:1080},deviceScaleFactor:1});const errors=[];page.on('pageerror',e=>errors.push(e.message));
await page.goto('http://127.0.0.1:4380/assets/rig-lab/hound-v0.3/shadow-prototype.html');await page.waitForFunction(()=>window.PROTOTYPE_READY===true);
const evidence=[];
for(const pose of ['idle','attack','recovery','death']){
  await page.selectOption('#pose',pose);await page.selectOption('#formation','single');
  await page.screenshot({path:path.join(out,`${pose}-single.png`),fullPage:true});evidence.push(await page.evaluate(()=>window.PROTOTYPE_EVIDENCE));
}
for(const formation of ['sparse','full']){
  await page.selectOption('#pose','attack');await page.selectOption('#formation',formation);await page.screenshot({path:path.join(out,`attack-${formation}.png`),fullPage:true});evidence.push(await page.evaluate(()=>window.PROTOTYPE_EVIDENCE));
}
const files=['src/art.ts','src/arena.ts','public/art/hound-poses.png','public/art/abbey-courtyard.png','assets/rig-lab/hound-v0.3/shadow-prototype.html'];const hashes={};
for(const file of files)hashes[file]=createHash('sha256').update(await readFile(path.join(root,file))).digest('hex');
await writeFile(path.join(out,'evidence.json'),JSON.stringify({sourceHashes:hashes,errors,evidence,scope:'Isolated static Canvas comparison. Not a production FPS test, runtime integration test, independent acceptance or human feedback.'},null,2)+'\n');
await browser.close();if(errors.length)throw new Error(errors.join('\n'));console.log('Captured actual baseline/candidate Canvas draws for six static pose/formation cases.');
