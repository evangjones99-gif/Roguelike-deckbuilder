import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import crypto from 'node:crypto';
import {splitInstaller} from './windows-installer-transfer.mjs';
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
test('ordered bounded parts reconstruct exact original including partial tail; no original rewrite',async()=>{
  const d=fs.mkdtempSync(path.join(os.tmpdir(),'hollowpact-transfer-guard-'));
  try {const b=Buffer.from(Array.from({length:65536*3+91},(_,i)=>(i*17+i%13)%256));const file=path.join(d,'original.exe');
    fs.writeFileSync(file,b);const out=path.join(d,'parts');const r=await splitInstaller(file,out,65536,8);
    assert.equal(r.parts.length,4);assert.equal(r.bytes,b.length);assert.equal(r.sha256,hash(b));
    const chunks=r.parts.map(p=>{const data=fs.readFileSync(path.join(out,p.filename));assert.equal(data.length,p.bytes);assert.equal(hash(data),p.sha256);assert.ok(data.length<=65536);return data;});
    assert.deepEqual(Buffer.concat(chunks),b);assert.deepEqual(fs.readFileSync(file),b);
    await assert.rejects(()=>splitInstaller(file,out,65536,8),/overwrite/);
  }finally{fs.rmSync(d,{recursive:true});} // Only this new disposable fixture.
});
test('empty/oversized sources and path links reject without creating output or changing sentinel',async()=>{
  const d=fs.mkdtempSync(path.join(os.tmpdir(),'hollowpact-transfer-guard-'));
  try {for(const size of [0,9]){const f=path.join(d,`size-${size}.exe`),out=path.join(d,`out-${size}`);fs.writeFileSync(f,Buffer.alloc(size,7));
    await assert.rejects(()=>splitInstaller(f,out,1,8),/Empty\/oversized/);assert.ok(!fs.existsSync(out));assert.equal(fs.statSync(f).size,size);}
    const kept=path.join(d,'keep');fs.mkdirSync(kept);fs.writeFileSync(path.join(kept,'sentinel'),'untouched');
    const f=path.join(d,'source.exe');fs.writeFileSync(f,'test');fs.symlinkSync(kept,path.join(d,'redirect'),process.platform==='win32'?'junction':'dir');
    await assert.rejects(()=>splitInstaller(f,path.join(d,'redirect','output'),1,8),/link\/junction/);
    assert.equal(fs.readFileSync(path.join(kept,'sentinel'),'utf8'),'untouched');assert.ok(!fs.existsSync(path.join(kept,'output')));
  }finally{fs.rmSync(d,{recursive:true});}
});
