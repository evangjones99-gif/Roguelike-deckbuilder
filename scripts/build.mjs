import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
// Invoke installed JavaScript entry points directly: npx.cmd is not a native executable on Windows.
const tscEntry = path.join(path.dirname(require.resolve('typescript/package.json')), 'bin', 'tsc');
execFileSync(process.execPath, [tscEntry, '--noEmit'], { stdio: 'inherit' });
function files(dir) { return fs.readdirSync(dir,{withFileTypes:true}).flatMap(e=>e.isDirectory()?files(path.join(dir,e.name)):[path.join(dir,e.name)]); }
const runtimeSources = [...files('src'),...files('desktop'),...(fs.existsSync('public')?files('public'):[]),'index.html','THIRD-PARTY.md','package.json','package-lock.json','tsconfig.json','vite.config.ts','scripts/build.mjs'].map(file => file.split(path.sep).join('/')).sort();
const hashes = Object.fromEntries(runtimeSources.map(file=>[file,crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex')]));
const sourceDigest = crypto.createHash('sha256').update(JSON.stringify(hashes)).digest('hex');
// Embed the same immutable runtime identity in optional local playtest exports.
const viteEntry = path.join(path.dirname(require.resolve('vite/package.json')), 'bin', 'vite.js');
execFileSync(process.execPath, [viteEntry, 'build'], { stdio: 'inherit', env: {...process.env, VITE_BUILD_ID: sourceDigest} });
fs.mkdirSync('dist/licenses',{recursive:true});
fs.copyFileSync('THIRD-PARTY.md','dist/CREDITS.md');
fs.writeFileSync('dist/build-provenance.json',JSON.stringify({version:JSON.parse(fs.readFileSync('package.json')).version,sourceDigest,hashes,node:process.version},null,2)+'\n');
console.log(`Runtime source digest: ${sourceDigest}`);
