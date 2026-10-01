import assert from 'node:assert/strict';
import path from 'node:path';
import fs from 'node:fs';
import crypto from 'node:crypto';
export const expectedDigest = '8a33f950ed57093a222baf9b7883a5c1ccf2deb2e8412429ef0fe05d370467cb';
export const expectedAsar = '0d82286ca7e49206b5085c3544d377735f3af048129abdd1b261d9d1b4086251';
export const expectedVersion = '0.9.0';
export const expectedInputCount = 77;
export const hash = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
export async function hashFile(file) { const h=crypto.createHash('sha256');for await(const b of fs.createReadStream(file))h.update(b);return h.digest('hex'); }
export function layout(localAppData, token) {
  assert.match(token, /^[a-f0-9]{32}$/);
  // Restrict the command-line and NSIS literals: /D must be the unquoted final argument.
  assert.ok(path.win32.isAbsolute(localAppData) && /^[A-Za-z]:\\/.test(localAppData));
  assert.ok(!/[\x00-\x1f"$;&|<>%]/.test(localAppData));
  assert.equal(path.win32.normalize(localAppData), localAppData, 'Noncanonical LocalAppData');
  assert.ok(!localAppData.endsWith('\\'),'Trailing separator/root not allowed');
  assert.ok(!localAppData.slice(2).includes(':'),'Refusing alternate data stream path');
  assert.ok(localAppData.slice(3).split('\\').every(c=>c && !/[. ]$/.test(c) && !/^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(\..*)?$/i.test(c)), 'Ambiguous/reserved Windows component');
  const base=path.win32.join(localAppData,'HollowpactInstallerQA',token);
  return {token, base, install:path.win32.join(base,'installation'), profile:path.win32.join(base,'profile'),
    marker:path.win32.join(base,'owner-token.txt'), sentinel:path.win32.join(base,'preserve-me.txt'),
    generator:path.win32.join(base,'uninstaller-generator'), cache:path.win32.join(base,'installer-cache'),
    executableName:`Hollowpact-QA-${token}`, appId:`com.hollowpact.qa.${token}`,
    guid:`${token.slice(0,8)}-${token.slice(8,12)}-${token.slice(12,16)}-${token.slice(16,20)}-${token.slice(20)}`};
}
export function checkLayout(value, localAppData) {assert.deepEqual(value,layout(localAppData,value.token));return value;}
export function noLinks(file, io=fs, paths=path) {
  for(let p=paths.resolve(file);;) {
    try { const s=io.lstatSync(p);assert.ok(!s.isSymbolicLink(),`Refusing link/junction: ${p}`); }
    catch(e){if(e.code!=='ENOENT')throw e;}
    const parent=paths.dirname(p);if(parent===p)break;p=parent;
  }
}
export function checkOwnership(value, localAppData, io=fs, paths=path) {
  checkLayout(value,localAppData);
  for(const p of [value.base,value.install,value.profile,value.marker,value.sentinel,value.generator,value.cache])noLinks(p,io,paths);
  assert.equal(io.readFileSync(value.marker,'utf8'), value.token+'\n','Missing/wrong QA ownership marker');
  assert.equal(io.readFileSync(value.sentinel,'utf8'),'preserve '+value.token+'\n','Outside-install sentinel modified');
}
export function commandArguments(operation,value,localAppData) {
  checkLayout(value,localAppData);
  if(operation==='install')return ['/S','/currentuser',`/D=${value.install}`];
  assert.equal(operation,'uninstall');
  // Let standard NSIS copy itself to TEMP, so the verified installation can be removed completely.
  // native() waits the launcher; smoke additionally polls full installation absence before acceptance.
  return ['/S','/currentuser'];
}
export function guardInclude(v) {
  // Paths were restricted by layout; values cannot inject NSIS source or arguments.
  const common=`  IfSilent +3\n    SetErrorLevel 81\n    Quit\n  StrCmp $installMode \"CurrentUser\" +3\n    SetErrorLevel 82\n    Quit\n  StrCmp $INSTDIR \"${v.install}\" +3\n    SetErrorLevel 83\n    Quit\n  System::Call 'kernel32::GetFileAttributesW(w \"$INSTDIR\") i .r0'\n  IntCmp $0 -1 attrsDone\n  IntOp $0 $0 & 0x400\n  IntCmp $0 0 attrsDone\n    SetErrorLevel 84\n    Quit\n  attrsDone:\n  ClearErrors\n  FileOpen $0 \"${v.marker}\" r\n  IfErrors badOwner\n  FileRead $0 $1\n  FileClose $0\n  StrCmp $1 \"${v.token}$\\n\" goodOwner\n  badOwner:\n    SetErrorLevel 85\n    Quit\n  goodOwner:\n`;
  return `; QA ONLY: exact run identity, no process kills, no app-data removal.\n!macro customHeader\n  !undef KF_FLAG_CREATE\n  !define KF_FLAG_CREATE 0\n  !ifdef BUILD_UNINSTALLER\n    InstallDir \"${v.generator}\"\n  !else\n    InstallDir \"${v.install}\"\n  !endif\n  !ifdef APP_INSTALLER_STORE_FILE\n    !undef APP_INSTALLER_STORE_FILE\n  !endif\n  !define APP_INSTALLER_STORE_FILE \"HollowpactInstallerQA\\${v.token}\\installer-cache\\installer.exe\"\n!macroend\n!macro customCheckAppRunning\n  nsProcess::_FindProcess /NOUNLOAD \"\${APP_EXECUTABLE_FILENAME}\"\n  Pop $0\n  IntCmp $0 603 +3\n    SetErrorLevel 86\n    Quit\n!macroend\n!macro customInit\n${common}  ReadRegStr $0 HKCU \"\${INSTALL_REGISTRY_KEY}\" InstallLocation\n  StrCmp $0 \"\" +3\n    SetErrorLevel 87\n    Quit\n  ReadRegStr $0 HKLM \"\${INSTALL_REGISTRY_KEY}\" InstallLocation\n  StrCmp $0 \"\" +3\n    SetErrorLevel 88\n    Quit\n  FindFirst $0 $1 \"$INSTDIR\\*.*\"\n  checkEmpty:\n    StrCmp $1 \"\" emptyDone\n    StrCmp $1 \".\" emptyNext\n    StrCmp $1 \"..\" emptyNext\n    FindClose $0\n    SetErrorLevel 89\n    Quit\n  emptyNext:\n    FindNext $0 $1\n    Goto checkEmpty\n  emptyDone:\n    FindClose $0\n!macroend\n!macro customUnInit\n${common}!macroend\n!macro customRemoveFiles\n  StrCmp $INSTDIR \"${v.install}\" +3\n    SetErrorLevel 90\n    Quit\n  SetOutPath $TEMP\n  RMDir /r \"${v.install}\"\n!macroend\n`;
}

export function checkInstalledRegistry(rows,v) {
  assert.equal(rows.length,4,'Need both views/hives');
  assert.equal(new Set(rows.map(r=>r.hive+'/'+r.view)).size,4,'Duplicate registry observation');
  for(const row of rows) {
    assert.ok(['Registry32','Registry64'].includes(row.view));
    if(row.hive==='CurrentUser') {
      // HKCU\SOFTWARE is shared on this Windows host; two logical views alias the same per-user key.
      assert.equal(row.install,true);assert.equal(row.uninstall,true);
      assert.equal(path.win32.resolve(row.location).toLowerCase(),path.win32.resolve(v.install).toLowerCase());
    } else {assert.equal(row.hive,'LocalMachine');assert.equal(row.install,false);assert.equal(row.uninstall,false);}
  }
}
export async function directoryWitness(directory) {
  noLinks(directory);
  if(!fs.existsSync(directory))return {exists:false};
  assert.ok(fs.lstatSync(directory).isDirectory());
  const entries={};
  async function visit(p) {
    for(const e of fs.readdirSync(p,{withFileTypes:true}).sort((a,b)=>a.name.localeCompare(b.name))) {
      const file=path.join(p,e.name);noLinks(file);const s=fs.lstatSync(file);
      if(s.isDirectory()) {entries[path.relative(directory,file).replaceAll('\\','/')+'/']={directory:true};await visit(file);}
      else {assert.ok(s.isFile(),'Refuse unusual cache entry');entries[path.relative(directory,file).replaceAll('\\','/')]={bytes:s.size,sha256:await hashFile(file)};}
    }
  }
  await visit(directory);return {exists:true,entries};
}

export function builderConfig(build,v,include) {
  return {...build,appId:v.appId,directories:{...build.directories,output:'build-installer'},forceCodeSigning:false,
    publish:null,win:{...build.win,target:['nsis'],executableName:v.executableName,signAndEditExecutable:true,signExecutable:false},
    nsis:{guid:v.guid,oneClick:true,perMachine:false,allowElevation:false,packElevateHelper:false,
      runAfterFinish:false,deleteAppDataOnUninstall:false,createDesktopShortcut:false,createStartMenuShortcut:false,
      differentialPackage:false,include,artifactName:'Hollowpact-QA-Installer-${version}-x64.exe'}};
}
