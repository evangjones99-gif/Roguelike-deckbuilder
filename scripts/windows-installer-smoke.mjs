import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {execFileSync,spawn} from 'node:child_process';
import {pathToFileURL} from 'node:url';
import {_electron as electron,expect} from '@playwright/test';
import {extractFile} from '@electron/asar';
import * as ResEdit from 'resedit';
import {tsImport} from 'tsx/esm/api';
import {expectedDigest,expectedAsar,hash,hashFile,checkOwnership,noLinks,commandArguments,checkInstalledRegistry,directoryWitness} from './windows-installer-guards.mjs';
assert.equal(process.platform,'win32','Actual native Windows x64 required; no mock installer pass');
assert.equal(process.arch,'x64');
assert.equal(process.env.GITHUB_ACTIONS,'true');assert.equal(process.env.RUNNER_OS,'Windows');
const request=JSON.parse(fs.readFileSync('build-installer/request.json','utf8'));
assert.equal(request.sourceDigest,expectedDigest);assert.equal(request.expectedAsar,expectedAsar);
assert.equal(request.commit,process.env.GITHUB_SHA);assert.equal(request.ref,'refs/heads/codex/lanternbound-production');
assert.equal(request.localAppData,process.env.LOCALAPPDATA);
const v=request.layout,output=path.resolve('reviews/windows-installer',request.version,`run-${request.runId}-${request.attempt}`);
assert.ok(!fs.existsSync(output),'Never overwrite an installer attempt');fs.mkdirSync(output,{recursive:true});
const installer=path.resolve('build-installer',`Hollowpact-QA-Installer-${request.version}-x64.exe`);
const staged=path.resolve('build-installer/win-unpacked');
const exe=path.join(v.install,v.executableName+'.exe');
let app,page,phase='preflight';
const report={schema:1,request,status:'running',steps:[],errors:[],limits:[
  'QA-isolated appId/GUID/executable name; same-game runtime, not production-identity install/update qualification',
  'Unsigned Windows Server 2022 hosted-runner automated QA; no physical consumer/SmartScreen/security/hardware acceptance',
  'Test-only native download-path handler; no chooser/listening/human-fun/Steam proof',
  'Explicit isolated user-data profile preserved after uninstall; default production profile behavior untested']};
const mark=p=>{phase=p;report.steps.push(p);};
function entries(dir){return fs.readdirSync(dir,{withFileTypes:true}).flatMap(e=>{
  assert.ok(!e.isSymbolicLink());const p=path.join(dir,e.name);return e.isDirectory()?entries(p):[p];});}
async function snapshot(dir){const result={};for(const p of entries(dir).sort())result[path.relative(dir,p).replaceAll('\\','/')]=await hashFile(p);return result;}
function signature(file){return execFileSync('pwsh.exe',['-NoProfile','-NonInteractive','-Command',
  "$ErrorActionPreference='Stop'; Import-Module Microsoft.PowerShell.Security -ErrorAction Stop; (Get-AuthenticodeSignature -LiteralPath $env:HOLLOWPACT_QA_SIGNFILE).Status.ToString()"],
  {encoding:'utf8',env:{...process.env,HOLLOWPACT_QA_SIGNFILE:file}}).trim();}
function resource(file){const executable=ResEdit.NtExecutable.from(fs.readFileSync(file),{ignoreCert:true});
  const r=ResEdit.NtExecutableResource.from(executable).entries;
  const result={icons:r.filter(e=>e.type===3).map(e=>hash(Buffer.from(e.bin))),
    strings:ResEdit.Resource.VersionInfo.fromEntries(r).flatMap(e=>e.getAllLanguagesForStringValues().map(l=>e.getStringValues(l)))};
  assert.ok(result.icons.length>0,'Missing branded icon');
  assert.ok(result.strings.some(s=>s.ProductName==='Hollowpact'),'Wrong product resources');
  assert.ok(result.strings.some(s=>s.ProductVersion===request.version||s.ProductVersion===request.version+'.0'),'Wrong product version resources');
  assert.ok(result.strings.some(s=>s.FileVersion===request.version||s.FileVersion===request.version+'.0'),'Wrong file version resources');
  assert.notDeepEqual(result.icons.sort(),stockIcons,'Stock Electron icon retained');return result;}
const stock=ResEdit.NtExecutable.from(fs.readFileSync('node_modules/electron/dist/electron.exe'),{ignoreCert:true});
const stockIcons=ResEdit.NtExecutableResource.from(stock).entries.filter(e=>e.type===3).map(e=>hash(Buffer.from(e.bin))).sort();
function registryState(){const script=`$result=@(); foreach($h in @([Microsoft.Win32.RegistryHive]::CurrentUser,[Microsoft.Win32.RegistryHive]::LocalMachine)){foreach($v in @([Microsoft.Win32.RegistryView]::Registry32,[Microsoft.Win32.RegistryView]::Registry64)){
  $base=[Microsoft.Win32.RegistryKey]::OpenBaseKey($h,$v);$i=$null;$u=$null;try{
    $i=$base.OpenSubKey('Software\\'+$env:HOLLOWPACT_QA_GUID);$u=$base.OpenSubKey('Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\'+$env:HOLLOWPACT_QA_GUID);
    $result+=@{hive=$h.ToString();view=$v.ToString();install=($null -ne $i);uninstall=($null -ne $u);location=$(if($null -ne $i){$i.GetValue('InstallLocation')}else{$null})};
  }finally{if($null -ne $i){$i.Dispose()};if($null -ne $u){$u.Dispose()};$base.Dispose()}}}; ConvertTo-Json -InputObject $result -Depth 5`;
  return JSON.parse(execFileSync('powershell.exe',['-NoProfile','-NonInteractive','-Command',script],
    {encoding:'utf8',env:{...process.env,HOLLOWPACT_QA_GUID:v.guid}}).replace(/^\uFEFF/,''));}
async function native(operation,file){checkOwnership(v,request.localAppData);noLinks(file);
  const args=commandArguments(operation,v,request.localAppData);
  // Explicit verbatim joining is required by NSIS /D and _?=: final unquoted path can contain spaces.
  // Filename is handled by spawn, not a shell. layout() rejects command/NSIS metacharacters.
  const code=await new Promise((resolve,reject)=>{
    const child=spawn(file,args,{shell:false,windowsVerbatimArguments:true,stdio:['ignore','pipe','pipe']});
    child.stdout.on('data',b=>fs.appendFileSync(path.join(output,operation+'.log'),b));
    child.stderr.on('data',b=>fs.appendFileSync(path.join(output,operation+'.log'),b));
    const timer=setTimeout(()=>{child.kill();reject(new Error(operation+' timeout; installation preserved for diagnosis'));},180000);
    child.once('error',e=>{clearTimeout(timer);reject(e);});child.once('exit',c=>{clearTimeout(timer);resolve(c);});
  });assert.equal(code,0,`${operation} exited ${code}`);report[operation]={file,args,exitCode:code};}
async function launch(){const env={...process.env};delete env.ELECTRON_RUN_AS_NODE;
  app=await electron.launch({executablePath:exe,args:[`--user-data-dir=${v.profile}`],env,timeout:60000});
  page=await app.firstWindow({timeout:30000});await page.waitForLoadState('domcontentloaded');page.setDefaultTimeout(15000);page.on('pageerror',e=>report.errors.push(e.message));
  page.on('request',r=>{if(!['file:','blob:'].includes(new URL(r.url()).protocol))report.errors.push('Unexpected nonlocal request: '+r.url());});
  const info=await app.evaluate(({app,BrowserWindow})=>({profile:app.getPath('userData'),prefs:BrowserWindow.getAllWindows()[0].webContents.getLastWebPreferences()}));
  assert.equal(path.resolve(info.profile).toLowerCase(),path.resolve(v.profile).toLowerCase());
  assert.equal(info.prefs.sandbox,true);assert.equal(info.prefs.contextIsolation,true);assert.equal(info.prefs.nodeIntegration,false);
  report.launches??=[];report.launches.push({profile:info.profile,sandbox:true,contextIsolation:true,nodeIntegration:false});}
const readSave=()=>page.evaluate(()=>localStorage.getItem('hollowpact.run.v2'));
try{
  checkOwnership(v,request.localAppData);assert.ok(!fs.existsSync(v.install),'Refusing preexisting target');
  assert.equal(request.defaultCache,path.join(request.localAppData,'hollowpact-updater'));
  assert.deepEqual(await directoryWitness(request.defaultCache),request.defaultCacheBefore,'Builder changed production-name updater cache');
  report.defaultCacheBefore=request.defaultCacheBefore;
  report.generatorBefore=await directoryWitness(v.generator);
  assert.equal(report.generatorBefore.exists,true,'Expected generator-owned directory evidence');
  assert.equal(hash(fs.readFileSync('build-installer/qa-config.json')),request.configSHA256);
  assert.equal(hash(fs.readFileSync('build-installer/qa-only.nsh')),request.includeSHA256);
  report.registryBefore=registryState();assert.ok(report.registryBefore.every(k=>!k.install&&!k.uninstall),'QA GUID already registered; refuse upgrade');
  report.installerSHA256=await hashFile(installer);report.installerResources=resource(installer);
  assert.equal(signature(installer),'NotSigned');report.signature='NotSigned';
  const stagedAsar=path.join(staged,'resources/app.asar');assert.equal(await hashFile(stagedAsar),expectedAsar);
  const runtime=JSON.parse(extractFile(stagedAsar,'dist/build-provenance.json').toString());
  assert.equal(runtime.sourceDigest,expectedDigest);assert.equal(runtime.version,request.version);assert.equal(Object.keys(runtime.hashes).length,29);
  assert.equal(hash(JSON.stringify(runtime.hashes)),expectedDigest);
  const build=JSON.parse(fs.readFileSync('dist/build-provenance.json','utf8'));assert.deepEqual(runtime,build);
  for(const f of ['src/engine.ts','src/content.ts','src/world-rng.ts'])assert.equal(await hashFile(f),runtime.hashes[f]);
  const {applyAction,legalActions}=await tsImport(pathToFileURL(path.resolve('src/engine.ts')).href,import.meta.url);
  const stagedFiles=await snapshot(staged);report.stagedFiles=stagedFiles;
  mark('actual silent per-user NSIS installation');await native('install',installer);
  checkOwnership(v,request.localAppData);assert.ok(fs.existsSync(exe));
  report.registryInstalled=registryState();checkInstalledRegistry(report.registryInstalled,v);
  report.registrySharedAlias='HKCU32/HKCU64 report the same exact per-user installation; no HKLM registration';
  assert.deepEqual(await directoryWitness(request.defaultCache),request.defaultCacheBefore,'Install changed production-name updater cache');
  noLinks(v.cache);assert.equal(await hashFile(path.join(v.cache,'installer.exe')),report.installerSHA256,'Installer cache escaped owned path or differs');
  report.ownedInstallerCache={path:path.join(v.cache,'installer.exe'),sha256:report.installerSHA256};
  report.installedFiles=await snapshot(v.install);
  for(const [f,h] of Object.entries(stagedFiles))assert.equal(report.installedFiles[f],h,`Installed bytes differ: ${f}`);
  assert.equal(await hashFile(path.join(v.install,'resources/app.asar')),expectedAsar);
  report.executableResources=resource(exe);assert.equal(signature(exe),'NotSigned');
  report.executableSHA256=await hashFile(exe);report.asarSHA256=await hashFile(path.join(v.install,'resources/app.asar'));
  assert.equal(hash(extractFile(path.join(v.install,'resources/app.asar'),path.join('dist','art','hunter-marek-v07-r3.png'))),'4492577d3bacc868e9b66da0abf25915bdeaf68bc8f5c31ae8a1d8db485f3c53');
  mark('actual installed executable binding and command');await launch();
  await page.locator('[data-ui="settings"]').click();await page.locator('#mute').uncheck();await page.locator('#motion').uncheck();
  await page.getByRole('button',{name:'Close dialog',exact:true}).click();
  await page.evaluate(()=>{window.__installerHunterDraws=[];const original=CanvasRenderingContext2D.prototype.drawImage;
    window.__installerRestoreDraw=()=>{CanvasRenderingContext2D.prototype.drawImage=original;};
    CanvasRenderingContext2D.prototype.drawImage=function(image,...args){if(this.canvas.id==='arena'&&image instanceof HTMLImageElement&&image.src.endsWith('/art/hunter-marek-v07-r3.png')&&window.__installerHunterDraws.length<64)
      window.__installerHunterDraws.push({url:image.src,width:image.naturalWidth,height:image.naturalHeight,source:args.slice(0,4)});return original.call(this,image,...args);};});
  await page.locator('[data-ui="new"]').click();await page.locator('#seed').fill('121');
  await page.locator('#new-game-form button[type="submit"]').click();await page.locator('[data-ui="learned"]').click();
  await page.locator('[data-action="travel"][data-choice="battle"]').first().click();
  const before=JSON.parse(await readSave());const bind=legalActions(before).find(a=>a.type==='play'&&before.hand[a.index]==='cairnhound');assert.ok(bind);
  await page.locator(`[data-ui="play-card"][data-index="${bind.index}"]`).click();
  const bound=applyAction(before,bind);assert.deepEqual(JSON.parse(await readSave()),bound);
  const command=legalActions(bound).find(a=>a.type==='attack');assert.ok(command);
  await page.locator(`[data-unit="${command.unit}"]`).click();await page.locator(`[data-unit="${command.target}"]`).click();
  const commanded=applyAction(bound,command);assert.deepEqual(JSON.parse(await readSave()),commanded);
  await expect.poll(()=>page.evaluate(()=>window.__installerHunterDraws.length)).toBeGreaterThan(0);
  report.hunterDraws=await page.evaluate(()=>{window.__installerRestoreDraw();return window.__installerHunterDraws;});
  for(const d of report.hunterDraws){assert.equal(new URL(d.url).protocol,'file:');assert.ok(new URL(d.url).pathname.endsWith('/resources/app.asar/dist/art/hunter-marek-v07-r3.png'));
    assert.equal(d.width,1536);assert.equal(d.height,1024);assert.equal(d.source[2],512);assert.equal(d.source[3],512);}
  const saved=await readSave();fs.writeFileSync(path.join(output,'saved-campaign.json'),saved+'\n',{flag:'wx'});
  report.canonical={binding:bind,command,exactState:true,saveSHA256:hash(saved)};
  await page.reload();await page.locator('[data-ui="resume"]').click();assert.equal(await readSave(),saved);
  mark('optional local synthetic negative feedback export');
  const destination=path.join(output,'synthetic-negative-feedback.json');
  await app.evaluate(({session},p)=>{globalThis.__qaDownload='pending';session.defaultSession.once('will-download',(_e,item)=>{
    item.setSavePath(p);item.once('done',(_e,state)=>globalThis.__qaDownload=state);});},destination);
  const storage=await page.evaluate(()=>JSON.stringify({...localStorage}));
  const text='[AUTOMATED INSTALLER QA — not human feedback] Target choice unclear.';
  await page.locator('[data-ui="feedback"]').click();await page.locator('#feedback-confusion').fill(text);
  await page.locator('#feedback-choice').fill('Synthetic installer interaction check.');await page.locator('#feedback-replay').selectOption('no');
  await page.locator('#feedback-form button[type="submit"]').click();
  await expect.poll(()=>app.evaluate(()=>globalThis.__qaDownload)).toBe('completed');
  const feedback=JSON.parse(fs.readFileSync(destination,'utf8'));assert.equal(feedback.context.build.sourceDigest,expectedDigest);
  assert.equal(feedback.responses.confusion,text);assert.equal(feedback.responses.replayIntent,'no');
  assert.equal(await page.evaluate(()=>JSON.stringify({...localStorage})),storage);
  await app.close();app=undefined;
  mark('full installed process relaunch preserves local save');await launch();await page.locator('[data-ui="resume"]').click();
  assert.equal(await readSave(),saved);await page.screenshot({path:path.join(output,'installed-resumed.png')});
  await app.close();app=undefined;assert.deepEqual(report.errors,[]);
  const profileBefore=await snapshot(v.profile);report.profileFilesBeforeUninstall=profileBefore;
  const uninstallers=fs.readdirSync(v.install).filter(f=>/^Uninstall.*\.exe$/i.test(f));assert.equal(uninstallers.length,1);
  const uninstaller=path.join(v.install,uninstallers[0]);const uninstallHash=await hashFile(uninstaller);
  assert.equal(uninstallHash,report.installedFiles[uninstallers[0]],'Uninstaller changed since verified install');
  mark('guarded unique-installation-only native uninstall');checkOwnership(v,request.localAppData);
  assert.equal(await hashFile(exe),stagedFiles[v.executableName+'.exe']);
  await native('uninstall',uninstaller);
  report.uninstall.method='Standard NSIS self-copy to TEMP; launcher exit alone is not completion evidence';
  await expect.poll(()=>!fs.existsSync(v.install),{timeout:45000}).toBe(true);
  report.uninstall.completeUniqueDirectoryRemoved=true;
  for(const f of Object.keys(stagedFiles))assert.ok(!fs.existsSync(path.join(v.install,f)),`Installed staged payload survived uninstall: ${f}`);
  assert.ok(!fs.existsSync(exe),'Installed executable survived uninstall');
  assert.ok(!fs.existsSync(path.join(v.install,'resources/app.asar')),'Installed ASAR survived uninstall');
  report.registryUninstalled=registryState();assert.ok(report.registryUninstalled.every(k=>!k.install&&!k.uninstall),'QA registration survived uninstall');
  checkOwnership(v,request.localAppData);assert.deepEqual(await snapshot(v.profile),profileBefore,'Uninstall modified preserved QA profile');
  assert.deepEqual(await snapshot(staged),stagedFiles,'Uninstall modified staged package');
  assert.deepEqual(await directoryWitness(request.defaultCache),request.defaultCacheBefore,'Uninstall changed production-name updater cache');
  assert.equal(await hashFile(path.join(v.cache,'installer.exe')),report.installerSHA256,'Owned cached installer changed');
  report.defaultCacheAfterUninstall=await directoryWitness(request.defaultCache);
  report.uninstall.uninstallerSHA256=uninstallHash;report.uninstall.profilePreserved=true;report.uninstall.sentinelPreserved=true;
  report.status='passed';
}catch(e){report.status='failed';report.failedPhase=phase;report.failure=e.stack??String(e);process.exitCode=1;
  if(v&&fs.existsSync(v.install)){report.remainingInstallDirectoryPresent=true;try{checkOwnership(v,request.localAppData);report.remainingInstallInventory=entries(v.install).map(p=>path.relative(v.install,p));}catch(inventoryError){report.remainingInstallInventoryError=inventoryError.message;}}
  if(page&&!page.isClosed())await page.screenshot({path:path.join(output,'failure.png')}).catch(()=>{});
}finally{
  if(app)await app.close().catch(e=>{report.errors.push(e.message);report.status='failed';process.exitCode=1;});
  // Preserve profiles, installed failure state, source, installer and reports. No recursive QA cleanup.
  fs.writeFileSync(path.join(output,'installer-smoke.json'),JSON.stringify(report,null,2)+'\n',{flag:'wx'});
  console.log(report.status+'; evidence '+output);
}
