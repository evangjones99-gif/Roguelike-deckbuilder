import {_electron as electron} from '@playwright/test';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {extractFile} from '@electron/asar';

const executablePath='./build-desktop/linux-unpacked/hollowpact';
const expected=JSON.parse(fs.readFileSync('dist/build-provenance.json','utf8'));
const packed=JSON.parse(extractFile('build-desktop/linux-unpacked/resources/app.asar','dist/build-provenance.json').toString());
const captureId = `${packed.sourceDigest.slice(0,12)}-${process.pid}-${Date.now()}`;
if(packed.sourceDigest!==expected.sourceDigest||packed.version!==expected.version)throw new Error('Packaged provenance mismatch');
const profile=fs.mkdtempSync(path.join(os.tmpdir(),'hollowpact-feedback-'));
const output=path.join(profile,'field-report.json');
const app=await electron.launch({executablePath,args:['--no-sandbox',`--user-data-dir=${profile}`],env:{...process.env,DISPLAY:process.env.DISPLAY??':99'},timeout:30000});
try {
  // Test-only native save destination; production contains no added privileged API.
  await app.evaluate(({session},output)=>{
    globalThis.__feedbackDownload={state:'pending'};
    session.defaultSession.on('will-download',(_event,item)=>{
      item.setSavePath(output);
      item.once('done',(_event,state)=>{globalThis.__feedbackDownload={state};});
    });
  },output);
  const page=await app.firstWindow();const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.waitForLoadState('domcontentloaded');
  const portrait=await page.locator('.title-hunter').evaluate(async element=>{
    const image=new Image();image.src=getComputedStyle(element).backgroundImage.slice(5,-2);await image.decode();
    return {width:image.naturalWidth,height:image.naturalHeight};
  });
  if(portrait.width!==1199||portrait.height!==1312)throw new Error('Packaged hunter portrait missing');
  await page.locator('[data-ui="new"]').click();await page.locator('#seed').fill('121');
  await page.locator('#new-game-form button[type="submit"]').click();
  const tutorial=page.locator('[data-ui="learned"]');if(await tutorial.isVisible())await tutorial.click();
  await page.locator('[data-action="travel"]').first().click();
  const before=await page.evaluate(()=>({...localStorage}));
  await page.locator('[data-ui="feedback"]').click();
  await page.locator('#feedback-confusion').fill('[Automated packaged QA, not human feedback] <script>window.qa=1</script> Target unclear.');
  await page.locator('#feedback-choice').fill('None in this synthetic check.');
  await page.locator('#feedback-replay').selectOption('no');
  await page.locator('#feedback-form button[type="submit"]').click();
  let download;
  for(let tries=0;tries<40;tries++) {
    download=await app.evaluate(()=>globalThis.__feedbackDownload);
    if(download.state!=='pending')break;
    await new Promise(resolve=>setTimeout(resolve,100));
  }
  if(download?.state!=='completed')throw new Error(`Native feedback download ${JSON.stringify(download)}`);
  const report=JSON.parse(fs.readFileSync(output,'utf8'));
  if(report.context.build.sourceDigest!==packed.sourceDigest||report.context.build.version!==packed.version||report.context.run.seed!==121||report.responses.replayIntent!=='no')throw new Error('Native feedback context mismatch');
  if(JSON.stringify(await page.evaluate(()=>({...localStorage})))!==JSON.stringify(before)||errors.length)throw new Error('Feedback mutated storage or caused page errors');
  const evidence={version:packed.version,runtimeSourceDigest:packed.sourceDigest,platform:'packaged Linux under Xvfb',sandboxDisabledForTest:true,portrait,download:download.state,context:report.context,responses:report.responses,storageUnchanged:true,errors,limits:['Test-only native save-path selection','No native Windows or Steam installation test','Synthetic QA; not human feedback']};
  fs.writeFileSync(`reviews/linux-feedback-${packed.version}-${captureId}-smoke.json`,JSON.stringify(evidence,null,2)+'\n');
  console.log('Packaged portrait and actual offline negative-feedback download passed.');
} finally {await app.close();}
