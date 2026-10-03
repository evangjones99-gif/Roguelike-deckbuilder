import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {hashFile,noLinks,expectedDigest} from './windows-installer-guards.mjs';
export async function splitInstaller(file,destination,partBytes=24*1024*1024,maxParts=8) {
  assert.ok(Number.isSafeInteger(partBytes)&&partBytes>0&&partBytes<=24*1024*1024);
  assert.ok(Number.isSafeInteger(maxParts)&&maxParts>0&&maxParts<=8);
  noLinks(file);noLinks(destination);assert.ok(!fs.existsSync(destination),'Never overwrite previous transfer');
  const before=fs.statSync(file);assert.ok(before.isFile());
  assert.ok(before.size>0&&before.size<=partBytes*maxParts,'Empty/oversized installer; explicitly review transfer capacity');
  const originalSHA256=await hashFile(file);
  fs.mkdirSync(destination,{recursive:false});const parts=[];
  const fd=fs.openSync(file,'r'),buffer=Buffer.allocUnsafe(partBytes),whole=crypto.createHash('sha256');
  try {
    for(let offset=0,index=1;offset<before.size;offset+=partBytes,index++) {
      const length=Math.min(partBytes,before.size-offset);let filled=0;
      while(filled<length){const n=fs.readSync(fd,buffer,filled,length-filled,offset+filled);assert.ok(n>0,'Unexpected source EOF');filled+=n;}
      const bytes=buffer.subarray(0,length),filename=`part-${String(index).padStart(2,'0')}.bin`;
      fs.writeFileSync(path.join(destination,filename),bytes,{flag:'wx'});whole.update(bytes);
      parts.push({index,filename,bytes:length,sha256:crypto.createHash('sha256').update(bytes).digest('hex')});
    }
  }finally{fs.closeSync(fd);}
  assert.equal(fs.statSync(file).size,before.size);assert.equal(await hashFile(file),originalSHA256,'Original installer changed during transfer');
  assert.equal(whole.digest('hex'),originalSHA256,'Ordered parts differ from original installer');
  return {filename:path.basename(file),bytes:before.size,sha256:originalSHA256,partBytes,parts};
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)) {
  assert.equal(process.platform,'win32');assert.equal(process.env.GITHUB_ACTIONS,'true');
  const request=JSON.parse(fs.readFileSync('build-installer/request.json','utf8'));
  assert.equal(request.sourceDigest,expectedDigest);assert.equal(request.commit,process.env.GITHUB_SHA);
  const file=path.resolve('build-installer',`Hollowpact-QA-Installer-${request.version}-x64.exe`);
  const output=path.resolve('build-installer/installer-transfer');
  const split=await splitInstaller(file,output);
  const smokeFile=path.resolve('reviews/windows-installer',request.version,`run-${request.runId}-${request.attempt}`,'installer-smoke.json');
  const smoke=fs.existsSync(smokeFile)?JSON.parse(fs.readFileSync(smokeFile,'utf8')):null;
  if(smoke?.installerSHA256)assert.equal(split.sha256,smoke.installerSHA256);
  const manifest={schema:1,scope:'Exact original unsigned QA-isolated installer transfer; parts alone are not runnable',
    version:request.version,sourceDigest:request.sourceDigest,commit:request.commit,ref:request.ref,
    runId:request.runId,attempt:request.attempt,nativeQAStatus:smoke?.status??'no-native-test-receipt',...split,
    reconstruction:'Download each numbered artifact from this same run/attempt; extract exactly its part-NN.bin, verify every size/SHA256, concatenate numeric index order, verify complete bytes/SHA256 before execution or preservation. Failed/unexecuted candidates remain failed/unexecuted.'};
  fs.writeFileSync(path.join(output,'manifest.json'),JSON.stringify(manifest,null,2)+'\n',{flag:'wx'});
  console.log(`Retained exact original installer in ${split.parts.length} bounded parts; native status ${manifest.nativeQAStatus}.`);
}
