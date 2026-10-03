import fs from 'node:fs';import path from 'node:path';import os from 'node:os';import {execFileSync} from 'node:child_process';import {fileURLToPath}from'node:url';
import {sha256File}from'./sha256-file.mjs';import {reviewIndex}from'./review-index.mjs';
const branch='refs/heads/codex/lanternbound-production';
function git(root,args){return execFileSync('git',args,{cwd:root,encoding:'utf8',maxBuffer:16*1024*1024});}
function heads(text){return text.trim().split('\n').filter(Boolean).map(line=>{const [commit,ref,...rest]=line.split(' ');if(rest.length||!/^[a-f0-9]{40}$/.test(commit))throw Error('Malformed bundle ref advertisement');return {commit,ref};}).sort((a,b)=>a.ref.localeCompare(b.ref));}
export async function verifyBundle(root,commit,bundle,temporary){
 const header=Buffer.alloc(16);const fd=fs.openSync(bundle,'r');let bytes;try{bytes=fs.readSync(fd,header,0,header.length,0)}finally{fs.closeSync(fd)}
 if(bytes!==16||!header.equals(Buffer.from('# v2 git bundle\n')))throw Error('Only exact Git bundle version 2 is supported');
 const expected=[{commit,ref:'HEAD'},{commit,ref:branch}].sort((a,b)=>a.ref.localeCompare(b.ref));
 const advertised=heads(git(root,['bundle','list-heads',bundle]));if(JSON.stringify(advertised)!==JSON.stringify(expected))throw Error('Bundle must contain only exact source HEAD and production branch');
 const bare=path.join(temporary,'restored.git');if(fs.existsSync(bare))throw Error('Bare verification destination already exists');
 git(temporary,['init','--bare',bare]);
 const verify=git(bare,['bundle','verify',bundle]);
 const unbundled=heads(git(bare,['bundle','unbundle',bundle]));if(JSON.stringify(unbundled)!==JSON.stringify(expected))throw Error('Unbundle advertised identity differs');
 git(bare,['update-ref',branch,commit]);git(bare,['symbolic-ref','HEAD',branch]);
 const fsck=git(bare,['fsck','--full','--strict']);
 if(git(bare,['rev-parse','HEAD']).trim()!==commit)throw Error('Restored HEAD differs');
 const closure=repo=>git(repo,['rev-list','--objects','--no-object-names',commit]).trim().split('\n').sort();
 const a=closure(root),b=closure(bare);if(JSON.stringify(a)!==JSON.stringify(b))throw Error('Restored reachable object closure differs');
 const all=git(bare,['cat-file','--batch-all-objects','--batch-check=%(objectname)']).trim().split('\n').sort();
 if(JSON.stringify(a)!==JSON.stringify(all))throw Error('Bundle contains objects outside the exact source reachable closure');
 const identity=JSON.parse(execFileSync('python3',[fileURLToPath(new URL('./verify-bundle-tree.py',import.meta.url)),root,bare,commit],{encoding:'utf8',maxBuffer:16*1024*1024}));
 return {format:'git-bundle-v2',sourceCommit:commit,refs:advertised,selfContained:true,restore:'Fresh bare init, bundle verify/unbundle, fixed ref restoration, fsck --full --strict, complete tree/current blob byte and reachable object comparison',verifyOutput:verify,fsckOutput:fsck,reachableObjectCount:a.length,identity};
}
export async function createSourceBundle(root,commit,dest,pkgName,version,sourceRoots){
 if(git(root,['symbolic-ref','HEAD']).trim()!==branch||git(root,['rev-parse','HEAD',branch]).trim().split('\n').some(ref=>ref!==commit))throw Error('Bundle release requires exact source HEAD/production branch');
 const archive=path.join(dest,`${pkgName}-${version}-source.bundle`);if(fs.existsSync(archive))throw Error('Source bundle already exists; refuse overwrite');
 const temporary=fs.mkdtempSync(path.join(os.tmpdir(),'hollowpact-source-bundle-'));
 try{
  const verificationZIP=path.join(temporary,`${pkgName}-${version}-verification-source.zip`);
  git(root,['archive','--format=zip',`--output=${verificationZIP}`,commit,'--',...sourceRoots]);
  const index=await reviewIndex(root,commit,verificationZIP);
  const zipProof={format:'temporary-git-zip',sourceCommit:commit,bytes:fs.statSync(verificationZIP).size,sha256:await sha256File(verificationZIP),officialArchive:false,removedAfterVerification:true,scope:'All included tracked roots except releases/, same unchanged canonical review audit. Not a retained official source ZIP.'};
  fs.unlinkSync(verificationZIP);
  git(root,['bundle','create','--version=2',archive,'HEAD',branch]);
  const proof=await verifyBundle(root,commit,archive,temporary);proof.archive=path.basename(archive);proof.bytes=fs.statSync(archive).size;proof.sha256=await sha256File(archive);proof.temporaryZIPVerification=zipProof;
  fs.writeFileSync(path.join(dest,'source-bundle-verification.json'),JSON.stringify(proof,null,2)+'\n');
  return {...index,sourceArchive:path.basename(archive),sourceArchiveFormat:'git-bundle-v2',temporaryZIPVerification:zipProof,canonicalBytes:'Current committed Git blob bytes in the independently restored official bundle; canonical reviews also audited against a temporary Git ZIP of the same commit.',scope:'All committed canonical review bytes are preserved in the verified official Git bundle. The review audit used a temporary ZIP that was removed after verification; no official source ZIP is claimed. All earlier local release/review copies and original inputs remain unchanged.'};
 }finally{fs.rmSync(temporary,{recursive:true,force:true});}
}
