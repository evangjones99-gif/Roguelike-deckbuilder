import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {extractFile,getRawHeader} from '@electron/asar';
import {expectedAsar,expectedDigest,expectedInputCount,expectedVersion,hash,hashFile} from './windows-installer-guards.mjs';
const ledgerPath=new URL('./windows-installer-asar-payload.json',import.meta.url);
const expectedPayload=JSON.parse(fs.readFileSync(ledgerPath,'utf8'));
assert.equal(expectedPayload.asarSHA256,expectedAsar);
assert.equal(expectedPayload.sourceDigest,expectedDigest);
assert.equal(expectedPayload.sourceInputCount,expectedInputCount);
assert.equal(expectedPayload.version,expectedVersion);

/** Necessary exact-package correspondence; does not qualify installation or platform quality. */
export async function assertPackagedAsar(archive,sourceRoot,expected=expectedPayload){
 const actualSHA=await hashFile(archive);assert.equal(actualSHA,expected.asarSHA256,'Exact builder ASAR bytes differ');
 assert.equal(fs.statSync(archive).size,expected.asarBytes,'Exact builder ASAR size differs');
 const raw=getRawHeader(archive);assert.equal(hash(raw.headerString),expected.rawHeaderStringSHA256,'Exact builder ASAR header/order differs');
 const observed=[];
 function walk(node,parts=[]){
  assert.ok(node&&typeof node==='object'&&!Array.isArray(node),'Invalid ASAR node');
  assert.ok(!Object.hasOwn(node,'link')&&!Object.hasOwn(node,'unpacked')&&!Object.hasOwn(node,'executable'),'Unexpected link/unpacked/executable ASAR node');
  if(Object.hasOwn(node,'files')){
   assert.deepEqual(Object.keys(node),['files'],'Unexpected directory header metadata');
   assert.ok(node.files&&typeof node.files==='object'&&!Array.isArray(node.files));
   for(const [name,child]of Object.entries(node.files)){
    assert.ok(name&&!name.includes('/')&&!name.includes('\\')&&!name.includes(':')&&name!=='.'&&name!=='..'&&!/[\x00-\x1f]/.test(name),'Unsafe ASAR path component');
    walk(child,[...parts,name]);
   }
  }else{
   assert.deepEqual(Object.keys(node),['size','offset','integrity'],'Unexpected file header metadata');
   const name=parts.join('/');assert.ok(name);assert.ok(Number.isSafeInteger(node.size)&&node.size>=0);assert.match(node.offset,/^(0|[1-9][0-9]*)$/);
   // Header and ledger paths stay POSIX; ASAR lookup traverses host-native separators.
   const bytes=extractFile(archive,path.join(...parts),false);assert.equal(bytes.length,node.size);
   observed.push({path:name,bytes:bytes.length,sha256:hash(bytes),offset:node.offset,integrity:node.integrity});
  }
 }
 walk(raw.header);
 assert.equal(observed.length,expected.leafCount,'Closed ASAR leaf count differs');
 assert.deepEqual(observed,expected.leaves,'Closed ASAR names/order/size/raw SHA/offset/integrity differ');
 const runtime=JSON.parse(extractFile(archive,path.join('dist','build-provenance.json')).toString());
 assert.equal(runtime.version,expected.version);assert.equal(runtime.sourceDigest,expected.sourceDigest);
 assert.equal(Object.keys(runtime.hashes).length,expected.sourceInputCount);
 assert.equal(hash(JSON.stringify(runtime.hashes)),expected.sourceDigest,'Exact ordered source digest differs');
 assert.deepEqual(runtime.hashes,expected.sourceHashes,'All pinned source hashes differ');
 function localFiles(directory){return fs.readdirSync(directory,{withFileTypes:true}).flatMap(e=>{const f=path.join(directory,e.name);return e.isDirectory()?localFiles(f):[path.relative(sourceRoot,f).split(path.sep).join('/')];});}
 const sourceFiles=[...['src','desktop','public'].filter(d=>fs.existsSync(path.join(sourceRoot,d))).flatMap(d=>localFiles(path.join(sourceRoot,d))),...['index.html','THIRD-PARTY.md','package.json','package-lock.json','tsconfig.json','vite.config.ts','scripts/build.mjs'].filter(f=>fs.existsSync(path.join(sourceRoot,...f.split('/'))))].sort();
 assert.deepEqual(sourceFiles,Object.keys(runtime.hashes).sort(),'Closed local runtime source set differs');
 const local=JSON.parse(fs.readFileSync(path.join(sourceRoot,'dist','build-provenance.json'),'utf8'));assert.deepEqual(runtime,local,'Packaged/local full build metadata differs');
 for(const [file,digest]of Object.entries(runtime.hashes)){
  assert.ok(!path.posix.isAbsolute(file)&&!file.includes('\\')&&file.split('/').every(p=>p&&p!=='.'&&p!=='..')&&!file.includes(':')&&!/[\x00-\x1f]/.test(file));
  assert.equal(hash(fs.readFileSync(path.join(sourceRoot,...file.split('/')))),digest,`Raw source changed: ${file}`);
 }
 const manifestBytes=extractFile(archive,'package.json');const manifest=JSON.parse(manifestBytes.toString());
 assert.equal(hash(manifestBytes),expected.normalizedManifest.sha256,'Normalized manifest exact bytes differ');
 assert.equal(manifestBytes.length,expected.normalizedManifest.bytes);assert.deepEqual(Object.keys(manifest),expected.normalizedManifest.keys);assert.deepEqual(manifest,expected.normalizedManifest.json);
 const sourcePackage=JSON.parse(fs.readFileSync(path.join(sourceRoot,'package.json'),'utf8'));
 for(const [key,value]of Object.entries(manifest))assert.deepEqual(value,sourcePackage[key],`Normalized manifest source field differs: ${key}`);
 const dist=observed.filter(p=>p.path.startsWith('dist/'));assert.equal(dist.length,expected.distOutputCount);
 assert.deepEqual(localFiles(path.join(sourceRoot,'dist')).sort(),dist.map(f=>f.path).sort(),'Closed local dist set differs');
 for(const file of dist)assert.equal(hash(fs.readFileSync(path.join(sourceRoot,...file.path.split('/')))),file.sha256,`Raw dist changed: ${file.path}`);
 for(const file of observed.filter(p=>p.path.startsWith('desktop/')))assert.equal(runtime.hashes[file.path],file.sha256,`Raw desktop differs: ${file.path}`);
 return {schema:1,version:runtime.version,sourceDigest:runtime.sourceDigest,sourceInputs:Object.keys(runtime.hashes).length,distOutputs:dist.length,leafCount:observed.length,asarSHA256:actualSHA,asarBytes:expected.asarBytes,headerStringSHA256:hash(raw.headerString),normalizedManifestSHA256:hash(manifestBytes),leaves:observed};
}
