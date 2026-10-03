// Built-in-only preflight. This module cannot launch anything or write packets.
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
export const sha=b=>createHash('sha256').update(b).digest('hex');
export function regular(file){
 assert.equal(path.resolve(file),file);let cursor='/';
 const parts=file.slice(1).split('/');
 for(let i=0;i<parts.length;i++){assert(parts[i]&&parts[i]!=='.'&&parts[i]!=='..');cursor=path.join(cursor,parts[i]);const s=fs.lstatSync(cursor);assert(!s.isSymbolicLink(),'Symlink forbidden '+cursor);assert(i===parts.length-1?s.isFile():s.isDirectory(),'Wrong file kind '+cursor);}
 return fs.readFileSync(file);
}
export function record(file,pin){const bytes=regular(file);assert.equal(sha(bytes),pin,'Authority changed '+file);return JSON.parse(bytes);}
export function members(root){const names=[];function walk(dir){for(const e of fs.readdirSync(dir,{withFileTypes:true})){assert(!e.isSymbolicLink());const file=path.join(dir,e.name);if(e.isDirectory())walk(file);else{assert(e.isFile());names.push(path.relative(root,file));}}}walk(root);return names.sort();}
export function identity(file,pin,fullHash=false){
 const parts=file.slice(1).split('/');let cursor='/';
 for(let i=0;i<parts.length;i++){cursor=path.join(cursor,parts[i]);const s=fs.lstatSync(cursor,{bigint:true});assert(!s.isSymbolicLink());assert(i===parts.length-1?s.isFile():s.isDirectory());}
 const s=fs.lstatSync(file,{bigint:true});for(const [key,value] of Object.entries({bytes:s.size,dev:s.dev,ino:s.ino,mode:s.mode,nlink:s.nlink,mtimeNs:s.mtimeNs,ctimeNs:s.ctimeNs}))assert.equal(String(value),String(pin[key]),'Measured identity changed '+file+' '+key);
 if(fullHash){let fd,h=createHash('sha256'),total=0;try{fd=fs.openSync(file,fs.constants.O_RDONLY|fs.constants.O_NOFOLLOW);const b=Buffer.allocUnsafe(65536);for(let n;(n=fs.readSync(fd,b,0,b.length,null));){h.update(b.subarray(0,n));total+=n;}const t=fs.fstatSync(fd,{bigint:true});assert.equal(t.ino,s.ino);assert.equal(t.dev,s.dev);assert.equal(t.size,s.size);assert.equal(t.mtimeNs,s.mtimeNs);assert.equal(t.ctimeNs,s.ctimeNs);}finally{if(fd!==undefined)fs.closeSync(fd);}assert.equal(total,pin.bytes);assert.equal(h.digest('hex'),pin.sha256);}
 return {dev:String(s.dev),ino:String(s.ino),mode:Number(s.mode),bytes:Number(s.size),nlink:Number(s.nlink),mtimeNs:String(s.mtimeNs),ctimeNs:String(s.ctimeNs)};
}
export function qualify(expected,expectedBytes,callerRoot){
 assert(expected.sealed===true&&expected.runtimeEligible===true&&expected.runtimeRecovery?.complete===true,'SOURCE_ONLY_UNSEALED: complete NEW stage bindings and separately reviewed Root method grant required');
 const grant=JSON.parse(regular(expected.rootMethodGrantPath));assert.equal(grant.schema,'opening-runtime-root-grant-v1');assert.equal(grant.authorized,true);assert.equal(grant.callerRoot,callerRoot);assert.equal(grant.expectedSHA256,sha(expectedBytes));assert.equal(grant.sourceManifestSHA256,sha(regular(callerRoot+'/MANIFEST.json')));assert.equal(grant.sourceSealSHA256,sha(regular(callerRoot+'/SOURCE-SEAL.json')));assert.equal(grant.actualPacket,expected.actualPacket);assert.equal(grant.driverSeconds,60);assert.equal(grant.supervisorWholeSeconds,90);assert.equal(grant.reviews.length,3);assert.deepEqual(grant.reviews.map(r=>r.role).sort(),['gameplay','technical','visual']);
 const seal=JSON.parse(regular(callerRoot+'/SOURCE-SEAL.json'));for(const ref of seal.files){const body=regular(callerRoot+'/'+ref.name);assert.equal(body.length,ref.bytes);assert.equal(sha(body),ref.sha256);}
 for(const ref of grant.reviews){const review=record(ref.path,ref.sha256);assert.equal(ref.accepted,true);assert.equal(review.accepted,true);assert.equal(review.sourceSealSHA256,grant.sourceSealSHA256);}
 const stageInodes=new Set(),stages=expected.runtimes.map(config=>{
  const freeze=record(config.freezePath,config.freezeSHA256),manifest=record(config.stageManifestPath,config.stageManifestSHA256),authority=record(config.stageAuthorityPath,config.stageAuthoritySHA256);
  for(const row of [freeze,manifest])for(const key of ['stage','sourceDigest','outputsDigest','inputCount','outputCount'])assert.equal(row[key],config[key]);
  assert.equal(manifest.schema,'regular-file-stage-v1');assert.equal(manifest.historicalMetadataRestored,false);assert.equal(authority.schema,'recovered-stage-authority-v1');assert.equal(authority.stage,config.stage);assert.equal(authority.acceptedByteExactReconstruction,true);assert.equal(authority.actualFreshBuild,config.authorityActualFreshBuild);assert.equal(authority.historicalMetadataRestored,false);assert.equal(authority.freezeSHA256,config.freezeSHA256);assert.equal(authority.stageManifestSHA256,config.stageManifestSHA256);assert.equal(authority.artDefaultOrFunAccepted,false);record(path.dirname(config.stageAuthorityPath)+'/BODY-COPY-RECEIPT.json',authority.bodyCopyReceiptSHA256);
  const review=record(config.stageReviewPath,config.stageReviewSHA256);assert.equal(review.accepted,true);
  if(config.role==='retainedB'){assert.equal(review.decision,'ACCEPT_EXACT_NEW_REGULAR_FILE_STATIC_RECONSTRUCTION_ONLY');assert.equal(review.newRuntimeFreezeSHA256,config.freezeSHA256);assert.equal(review.newStageManifestSHA256,config.stageManifestSHA256);assert.equal(review.newRootAuthoritySHA256,config.stageAuthoritySHA256);assert.equal(review.sourceDigest,config.sourceDigest);assert.equal(review.outputsDigest,config.outputsDigest);assert.equal(review.exactSource104Verified,true);assert.equal(review.exactOutputs70Verified,true);assert.equal(review.artDefaultGameplayFunApproved,false);const a=record(path.dirname(config.stageReviewPath)+'/AUDIT.json',review.fullAuditSHA256);assert.equal(a.stage,config.stage);assert.equal(a.inputCount,104);assert.equal(a.outputCount,70);}
  else{assert.equal(review.stage,config.stage);assert.equal(review.freezeSHA256,config.freezeSHA256);assert.equal(review.stageManifestSHA256,config.stageManifestSHA256);}
  const membership={...freeze.inputs,...Object.fromEntries(Object.entries(freeze.outputs).map(([k,v])=>['dist/'+k,v]))};assert.deepEqual(Object.keys(manifest.files).sort(),Object.keys(membership).sort());assert.deepEqual(members(config.stage),Object.keys(membership).sort());assert.equal(Object.keys(freeze.inputs).length,config.inputCount);assert.equal(Object.keys(freeze.outputs).length,config.outputCount);
  for(const [rel,pin] of Object.entries(manifest.files)){assert(!path.isAbsolute(rel)&&!rel.split('/').some(p=>!p||p==='.'||p==='..'));assert.equal(pin.sha256,membership[rel]);assert.equal(pin.nlink,1);assert.equal(typeof pin.mtimeNs,'string');assert.equal(typeof pin.ctimeNs,'string');identity(config.stage+'/'+rel,pin);const key=pin.dev+':'+pin.ino;assert(!stageInodes.has(key),'A/B stage bodies must have distinct new inodes');stageInodes.add(key);}
  return {config,stage:config.stage,freeze,manifest,authority};
 });
 assert.deepEqual(grant.stages,expected.runtimes.map(r=>({stage:r.stage,freezeSHA256:r.freezeSHA256,stageManifestSHA256:r.stageManifestSHA256,stageAuthoritySHA256:r.stageAuthoritySHA256})));
 const dependencies=record(expected.dependencies.path,expected.dependencies.sha256);assert.equal(dependencies.schema,'installed-dependency-identities-v1');assert.equal(dependencies.packageVersion,'1.62.0');assert.equal(dependencies.nodeVersion,'v24.19.0');assert.equal(process.version,dependencies.nodeVersion);assert.equal(dependencies.modulePath,expected.dependencies.modulePath);assert.equal(dependencies.nodePath,process.execPath);assert.equal(dependencies.browserExecutablePath,expected.dependencies.browserExecutablePath);
 for(const pin of dependencies.files)identity(pin.path,pin,true);
 return {grant,stages,dependencies};
}
