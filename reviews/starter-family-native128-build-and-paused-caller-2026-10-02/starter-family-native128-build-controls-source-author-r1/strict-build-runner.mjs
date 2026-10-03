// FUTURE Root-only strict build. This source packet does not execute Node.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { createRequire } from 'node:module';
import { pathToFileURL } from 'node:url';
const stage='/workspace/scratch/starter-family-native128-stage-r1';
if(process.cwd()!==stage) throw new Error('Exact fresh pixel stage required');
const assembly=JSON.parse(fs.readFileSync('.control/ASSEMBLY.json'));
if(assembly.stage!==stage||fs.existsSync('dist')) throw new Error('Wrong or already-built stage');
const require=createRequire(path.resolve('package.json'));
const tscEntry=path.join(path.dirname(require.resolve('typescript/package.json')),'bin','tsc');
execFileSync(process.execPath,[tscEntry,'--noEmit'],{stdio:'inherit'});
function files(dir){return fs.readdirSync(dir,{withFileTypes:true}).flatMap(e=>e.isDirectory()?files(path.join(dir,e.name)):[path.join(dir,e.name)]);}
const runtime=[...files('src'),...files('desktop'),...files('public'),'index.html','THIRD-PARTY.md','package.json','package-lock.json','tsconfig.json','vite.config.ts','scripts/build.mjs'].map(f=>f.split(path.sep).join('/')).sort();
function bodySHA(file){
  const fd=fs.openSync(fs.realpathSync(file),fs.constants.O_RDONLY|fs.constants.O_NOATIME|fs.constants.O_NOFOLLOW);
  const hash=crypto.createHash('sha256'),buffer=Buffer.alloc(65536);
  try{let n;while((n=fs.readSync(fd,buffer,0,buffer.length,null))>0)hash.update(buffer.subarray(0,n));}
  finally{fs.closeSync(fd);}
  return hash.digest('hex');
}
const hashes=Object.fromEntries(runtime.map(file=>[file,bodySHA(file)]));
if(JSON.stringify(hashes)!==JSON.stringify(assembly.inputs)||runtime.length!==assembly.inputCount) throw new Error('Actual full source membership/body mismatch');
const sourceDigest=crypto.createHash('sha256').update(JSON.stringify(hashes)).digest('hex');
if(sourceDigest!==assembly.sourceDigest) throw new Error('Assembly/source digest mismatch');
process.env.VITE_BUILD_ID=sourceDigest;
const viteApi=path.join(path.dirname(require.resolve('vite/package.json')),'dist','node','index.js');
const {build}=await import(pathToFileURL(viteApi).href);
await build({configLoader:'runner',publicDir:false,cacheDir:path.resolve('.vite-cache')});
fs.mkdirSync('dist/licenses',{recursive:true});fs.copyFileSync('THIRD-PARTY.md','dist/CREDITS.md');
fs.writeFileSync('dist/build-provenance.json',JSON.stringify({version:JSON.parse(fs.readFileSync('package.json')).version,sourceDigest,hashes,node:process.version},null,2)+'\n');
console.log(JSON.stringify({sourceDigest,inputs:runtime.length,strictTypecheck:true,publicDir:false,cache:'.vite-cache',mediaMountedAfterBuild:false}));
