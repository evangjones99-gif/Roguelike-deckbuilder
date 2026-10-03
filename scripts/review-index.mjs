import fs from 'node:fs';
import path from 'node:path';
import {execFileSync}from'node:child_process';
import {fileURLToPath}from'node:url';
import {createReadStream}from'node:fs';
import{createHash}from'node:crypto';
import{Writable}from'node:stream';
import{pipeline}from'node:stream/promises';
import{createGunzip}from'node:zlib';
import{sha256File}from'./sha256-file.mjs';
/** Canonical bytes come from the already-created Git source ZIP, including
 * historical Git normalization. Existing versions and raw inputs stay intact. */
export async function reviewIndex(root,sourceCommit,sourceArchive){
 const entries=execFileSync('git',['ls-tree','-r','-z',sourceCommit,'--','reviews/'],{cwd:root,encoding:'utf8'}).split('\0').filter(Boolean);
 const declared=entries.map(entry=>{const split=entry.indexOf('\t'),[mode,kind,oid]=entry.slice(0,split).split(' ');if(split<0||kind!=='blob'||!['100644','100755'].includes(mode))throw Error('Unsupported canonical review entry');return {path:entry.slice(split+1),gitBlob:oid};});
 if(!declared.length)throw Error('No committed canonical reviews to index');
 const files=JSON.parse(execFileSync('python3',[fileURLToPath(new URL('./index-review-archive.py',import.meta.url)),path.resolve(root,sourceArchive)],{cwd:root,input:JSON.stringify({sourceCommit,files:declared}),encoding:'utf8',maxBuffer:16*1024*1024}));
 const rawGzipPairs=[];
 for(const file of files){
  if(!file.path.endsWith('.json.gz'))continue;
  const absolute=path.join(root,file.path),raw=absolute.slice(0,-3);if(!fs.existsSync(raw))continue;
  if(await sha256File(absolute)!==file.sha256)throw Error('Compressed working evidence differs from source archive: '+file.path);
  const size=fs.statSync(raw).size,hash=createHash('sha256');let bytes=0;
  await pipeline(createReadStream(absolute),createGunzip(),new Writable({write(chunk,_encoding,callback){bytes+=chunk.length;if(bytes>size){callback(Error('Compressed review exceeds original size: '+file.path));return;}hash.update(chunk);callback();}}));
  const digest=hash.digest('hex');if(bytes!==size||digest!==await sha256File(raw))throw Error('Compressed review differs from retained raw bytes: '+file.path);
  rawGzipPairs.push({rawPath:file.path.slice(0,-3),compressedPath:file.path,rawBytes:size,rawSHA256:digest});
 }
 return {schema:1,sourceCommit,sourceArchive:path.basename(sourceArchive),canonicalDirectory:'reviews/',canonicalBytes:'Source-ZIP/Git blob content; historical text normalization may differ from original working CI records, as their retained reports/artifacts qualify.',scope:'All committed canonical review bytes are verified in this same source archive. No repeated full local review tree is created for the new milestone; all previous copies and original raw inputs remain unchanged.',compressedScope:'Every available raw/JSON.gz pair is verified lossless. Without a raw counterpart, only the committed compressed bytes are verified, not an original raw value.',files,rawGzipPairs};
}
