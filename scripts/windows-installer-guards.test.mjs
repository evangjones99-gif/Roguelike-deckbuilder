import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {createRequire} from 'node:module';
import {layout,checkLayout,checkOwnership,noLinks,commandArguments,builderConfig,guardInclude,hashFile,checkInstalledRegistry,directoryWitness} from './windows-installer-guards.mjs';
const root='C:\\Users\\QA User\\AppData\\Local',token='0123456789abcdef0123456789abcdef';
const v=layout(root,token);
test('paths keep installation, profile and sentinel in distinct exact run locations',()=>{
  assert.equal(path.win32.relative(v.base,v.install),'installation');
  assert.equal(path.win32.relative(v.base,v.profile),'profile');
  assert.ok(!v.profile.startsWith(v.install+'\\'));assert.notEqual(v.appId,'com.hollowpact.game');
  assert.notEqual(v.executableName,'Hollowpact');assert.notEqual(layout(root,'f'.repeat(32)).guid,v.guid);
});
test('reject path injection, UNC, traversal and noncanonical roots',()=>{
  for(const value of ['C:\\Local$evil','C:\\Local"evil','C:\\Local\nfoo','C:\\Local;evil','C:\\Local%evil','C:\\Local|evil','C:\\Local:stream','C:\\Local.','C:\\Local ','C:\\CON\\Local',
    '\\\\server\\share','C:\\Users\\x\\..\\y','C:\\Users\\QA\\Local\\'])assert.throws(()=>layout(value,token));
  for(const value of ['','../old','A'.repeat(32),'0'.repeat(31)])assert.throws(()=>layout(root,value));
});
test('refuse ownership layouts redirected toward older releases or user profiles',()=>{
  for(const property of ['install','profile','base','marker','sentinel','generator','cache','appId','guid','executableName'])
    assert.throws(()=>checkLayout({...v,[property]:'C:\\old-version'},root));
});
test('Windows ancestor model rejects junctions, even if the leaf does not yet exist',()=>{
  const io={lstatSync(p){if(p===path.win32.dirname(v.base))return{isSymbolicLink:()=>true};
    const e=new Error('absent');e.code='ENOENT';throw e;}};
  assert.throws(()=>noLinks(v.install,io,path.win32),/link\/junction/);
});
test('missing marker, wrong token and changed outside-install sentinel abort before commands',()=>{
  for(const state of ['missing','wrong-owner','wrong-sentinel']){
    const io={lstatSync:()=>({isSymbolicLink:()=>false}),readFileSync(p){
      if(state==='missing')throw new Error('missing marker');
      if(p===v.marker)return state==='wrong-owner'?'other\n':token+'\n';
      return state==='wrong-sentinel'?'changed\n':'preserve '+token+'\n';}};
    assert.throws(()=>checkOwnership(v,root,io,path.win32));
  }
});
test('controlled installer /D remains last and uninstall allows standard temporary self-copy',()=>{
  assert.deepEqual(commandArguments('install',v,root),['/S','/currentuser',`/D=${v.install}`]);
  assert.deepEqual(commandArguments('uninstall',v,root),['/S','/currentuser']);
  assert.throws(()=>commandArguments('delete-all',v,root));
  assert.throws(()=>commandArguments('uninstall',{...v,install:'C:\\'},root));
});
test('real filesystem symlink escape rejected without touching linked data',async()=>{
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),'hollowpact-guard-test-'));
  try{const keep=path.join(dir,'keep');fs.mkdirSync(keep);fs.writeFileSync(path.join(keep,'sentinel'),'unchanged');
    const before=await hashFile(path.join(keep,'sentinel'));
    fs.symlinkSync(keep,path.join(dir,'link'),process.platform==='win32'?'junction':'dir');
    assert.throws(()=>noLinks(path.join(dir,'link','child')),/link\/junction/);
    assert.equal(await hashFile(path.join(keep,'sentinel')),before);
  }finally{fs.rmSync(dir,{recursive:true});} // Only this newly created test fixture is removed.
});
test('actual installed electron-builder schema accepts isolated unsigned resource-enabled config',async()=>{
  const require=createRequire(path.resolve(process.env.HOLLOWPACT_QA_PROJECT??process.cwd(),'package.json'));
  const {validateConfiguration}=require('app-builder-lib/out/util/config/config.js');
  const pkg=require(path.resolve(process.env.HOLLOWPACT_QA_PROJECT??process.cwd(),'package.json'));
  const c=builderConfig(pkg.build,v,'C:\\QA\\qa-only.nsh');
  await validateConfiguration(c);
  assert.equal(c.productName,'Hollowpact');assert.equal(c.win.signAndEditExecutable,true);
  assert.equal(c.win.signExecutable,false);assert.equal(c.nsis.deleteAppDataOnUninstall,false);
  assert.equal(c.nsis.runAfterFinish,false);assert.equal(c.nsis.createDesktopShortcut,false);
  assert.equal(c.nsis.createStartMenuShortcut,false);assert.equal(c.nsis.perMachine,false);
  assert.equal(c.nsis.packElevateHelper,false);assert.equal(c.publish,null);
});
test('custom NSIS guards preserve data and suppress stock kill/uninstall redirection behavior',()=>{
  const s=guardInclude(v);assert.ok(s.includes('!macro customCheckAppRunning'));
  assert.ok(s.includes('nsProcess::_FindProcess'));assert.ok(!s.includes('KillProcess'));
  assert.ok(s.includes('HKCU'));assert.ok(s.includes('HKLM'));assert.ok(s.includes('0x400'));
  assert.ok(s.includes(`RMDir /r "${v.install}"`));assert.ok(!s.includes('RMDir /r "$APPDATA'));
  assert.ok(s.includes(`StrCmp $INSTDIR "${v.install}"`));assert.ok(s.includes('IntCmp $0 -1 attrsDone'));
});

test('NSIS uninstaller generator uses owned scratch, actual install distinct, and cache redirection suppresses defaults',()=>{
  const s=guardInclude(v);assert.ok(s.includes(`!ifdef BUILD_UNINSTALLER\n    InstallDir "${v.generator}"`));
  assert.ok(s.includes(`!else\n    InstallDir "${v.install}"`));assert.notEqual(v.generator,v.install);
  assert.ok(s.includes('!undef APP_INSTALLER_STORE_FILE'));
  assert.ok(s.includes(`!define APP_INSTALLER_STORE_FILE "HollowpactInstallerQA\\${v.token}\\installer-cache\\installer.exe"`));
  assert.ok(s.includes('!undef KF_FLAG_CREATE\n  !define KF_FLAG_CREATE 0'));
});
test('shared per-user registry aliases accepted; wrong target, HKLM registration and incomplete views rejected',()=>{
  const rows=['CurrentUser','LocalMachine'].flatMap(hive=>['Registry32','Registry64'].map(view=>({hive,view,
    install:hive==='CurrentUser',uninstall:hive==='CurrentUser',location:hive==='CurrentUser'?v.install:null})));
  assert.doesNotThrow(()=>checkInstalledRegistry(rows,v));
  for(const changed of [rows.slice(1),rows.map((r,i)=>i===0?{...r,location:'C:\\old-version'}:r),
    rows.map((r,i)=>i===2?{...r,install:true,location:v.install}:r),
    rows.map((r,i)=>i===0?{...r,uninstall:false}:r),[rows[0],rows[0],rows[2],rows[3]]])
    assert.throws(()=>checkInstalledRegistry(changed,v));
});
test('default-cache witness detects extra installer copy, preserves existing bytes and refuses links',async()=>{
  const d=fs.mkdtempSync(path.join(os.tmpdir(),'hollowpact-cache-guard-'));
  try{const cache=path.join(d,'hollowpact-updater');assert.deepEqual(await directoryWitness(cache),{exists:false});
    fs.mkdirSync(cache);const existing=path.join(cache,'keep.json');fs.writeFileSync(existing,'preserved');
    const before=await directoryWitness(cache);fs.writeFileSync(path.join(cache,'installer.exe'),'unwanted copy');
    assert.notDeepEqual(await directoryWitness(cache),before);assert.equal((await directoryWitness(cache)).entries['keep.json'].sha256,before.entries['keep.json'].sha256);
    fs.symlinkSync(cache,path.join(d,'escape'),process.platform==='win32'?'junction':'dir');
    await assert.rejects(()=>directoryWitness(path.join(d,'escape')),/link\/junction/);
  }finally{fs.rmSync(d,{recursive:true});} // Newly created disposable fixture only.
});
