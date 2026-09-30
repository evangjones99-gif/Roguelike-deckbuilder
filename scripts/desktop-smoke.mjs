import { _electron as electron } from '@playwright/test';
import fs from 'node:fs';
const version=JSON.parse(fs.readFileSync('package.json')).version;
const executablePath=process.argv[2]??'./build-desktop/linux-unpacked/lanternbound';
const app=await electron.launch({executablePath,args:['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader',`--user-data-dir=/tmp/lanternbound-smoke-${version}`],env:{...process.env,DISPLAY:process.env.DISPLAY??':99'},timeout:30000});
try {
  const page=await app.firstWindow();const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.waitForLoadState('domcontentloaded');
  await page.locator('[data-ui="settings"]').click();
  await page.locator('#motion').uncheck();
  await page.locator('[data-ui="close"]').first().click();
  await page.locator('[data-ui="new"]').click();
  await page.locator('#seed').fill('117');
  await page.locator('#new-game-form button[type="submit"]').click();
  const tutorial=page.locator('[data-ui="learned"]');if(await tutorial.isVisible())await tutorial.click();
  await page.locator('[data-action="travel"]').first().click();
  await page.locator('[data-ui="play-card"][data-card="mossling"]').first().click();
  await page.locator('.ally.ready').first().click();
  await page.locator('.enemy.valid-target').first().click();
  await page.screenshot({path:`reviews/linux-desktop-${version}-battle.png`});
  const saved=await page.evaluate(()=>JSON.parse(localStorage.getItem('lanternbound.run.v1')));
  if(saved.phase!=='battle'||!saved.allies.some(u=>u.acted)||errors.length)throw new Error('Desktop interaction smoke failed: '+errors.join(';'));
  fs.writeFileSync(`reviews/linux-desktop-${version}-smoke.json`,JSON.stringify({version,executablePath,display:'Xvfb',rendering:'SwiftShader software GPU',sandboxDisabledForTest:true,steps:['launch offline packaged binary','settings motion off','seed117 start','tutorial/map','summon Mossling','command against enemy'],state:{phase:saved.phase,allies:saved.allies.length,enemies:saved.enemies.length,hp:saved.hp},errors,limitations:['Linux host only, virtual display/software GPU','Test launches with --no-sandbox due cloud constraints; normal sandboxed clean-machine launch unverified','Windows binary packaging verified separately; Windows launch not tested','No Steam depot/install test'],runtimeSourceDigest:JSON.parse(fs.readFileSync('dist/build-provenance.json')).sourceDigest},null,2)+'\n');
  console.log('Packaged Linux launch and summon-command smoke passed.');
} finally { await app.close(); }
