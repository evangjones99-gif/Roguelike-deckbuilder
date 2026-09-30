import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { execFileSync } from 'node:child_process';
execFileSync('npx', ['tsc', '--noEmit'], { stdio: 'inherit' });
function files(dir) { return fs.readdirSync(dir,{withFileTypes:true}).flatMap(e=>e.isDirectory()?files(path.join(dir,e.name)):[path.join(dir,e.name)]); }
const runtimeSources = [...files('src'),...files('desktop'),...(fs.existsSync('public')?files('public'):[]),'index.html','THIRD-PARTY.md','package.json','package-lock.json','tsconfig.json','vite.config.ts','scripts/build.mjs'].sort();
const hashes = Object.fromEntries(runtimeSources.map(file=>[file,crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex')]));
const sourceDigest = crypto.createHash('sha256').update(JSON.stringify(hashes)).digest('hex');
// Embed the same immutable runtime identity in optional local playtest exports.
execFileSync('npx', ['vite', 'build'], { stdio: 'inherit', env: {...process.env, VITE_BUILD_ID: sourceDigest} });
fs.mkdirSync('dist/licenses',{recursive:true});
fs.copyFileSync('THIRD-PARTY.md','dist/CREDITS.md');
fs.writeFileSync('dist/build-provenance.json',JSON.stringify({version:JSON.parse(fs.readFileSync('package.json')).version,sourceDigest,hashes,node:process.version},null,2)+'\n');
console.log(`Runtime source digest: ${sourceDigest}`);
