import {_electron as electron} from '@playwright/test';
import fs from 'node:fs';
import path from 'node:path';
const runtime=JSON.parse(fs.readFileSync('dist/build-provenance.json','utf8'));
if(runtime.sourceDigest!=='004102e32dcc9f52038bcc0976a8d33909c44b2e972ef6ea06b88a2fd0bb4f9e')throw Error('Wrong frozen runtime');
const profile=`/tmp/hollowpact-url-rejection-${process.pid}-${Date.now()}`;
const app=await electron.launch({executablePath:path.resolve('node_modules/electron/dist/electron'),args:['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader',`--user-data-dir=${profile}`,'.'],cwd:process.cwd(),env:{...process.env,DISPLAY:':99'},timeout:30000});
try{
 const page=await app.firstWindow();const requests=[],failed=[],errors=[];
 page.on('request',r=>requests.push(r.url()));page.on('requestfailed',r=>failed.push({url:r.url(),error:r.failure()?.errorText}));page.on('pageerror',e=>errors.push(e.message));
 await page.waitForLoadState('domcontentloaded');
 await page.locator('[data-ui="new"]').click();await page.locator('#seed').fill('121');await page.locator('#new-game-form button[type="submit"]').click();
 const tutorial=page.locator('[data-ui="learned"]');if(await tutorial.isVisible())await tutorial.click();
 await page.locator('[data-action="travel"]').first().click();await page.waitForTimeout(700);
 const observed=await page.evaluate(async()=>{const image=new Image();image.src='/art/hunter-marek-v07-r3.png';const loaded=await new Promise(resolve=>{image.onload=()=>resolve(true);image.onerror=()=>resolve(false)});return{baseURI:document.baseURI,resolvedHunterURL:image.src,loaded,notice:document.querySelector('.arena-art-status')?.textContent,canonical:JSON.parse(localStorage.getItem('hollowpact.run.v2'))};});
 await page.screenshot({path:'reviews/root-v0.7-native-file-url-rejection/actual-electron-file.png'});
 const result={scope:'Actual development Electron app loadFile from current frozen dist, not an ASAR/package or clean consumer install. Existing virtual display :99/softwareGPU/--no-sandbox, no Windows/Deck/hardware claim.',runtime,profile,observed,failed,errors,localOnly:requests.every(url=>url.startsWith('file:'))};
 fs.writeFileSync('reviews/root-v0.7-native-file-url-rejection/result.json',JSON.stringify(result,null,2)+'\n',{flag:'wx'});
 if(observed.loaded||!observed.resolvedHunterURL.startsWith('file:///art/'))throw Error('Expected actual file URL failure not reproduced');
 console.log('Actual Electron loadFile reproduces absent file:///art/hunter-marek-v07-r3.png; controls/canonical remain functional. Candidate rejected.');
}finally{await app.close();}
