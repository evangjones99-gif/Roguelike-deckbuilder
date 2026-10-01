import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {expectedDigest,expectedAsar,hash,layout,noLinks,builderConfig,guardInclude,directoryWitness} from './windows-installer-guards.mjs';
assert.equal(process.platform,'win32','Native Windows preparation required');
assert.equal(process.arch,'x64');
assert.equal(process.env.GITHUB_ACTIONS,'true','Hosted CI-only installer research');
assert.equal(process.env.RUNNER_OS,'Windows');
assert.match(process.env.GITHUB_RUN_ID??'',/^[1-9][0-9]*$/);
assert.match(process.env.GITHUB_RUN_ATTEMPT??'',/^[1-9][0-9]*$/);
assert.equal(process.env.GITHUB_REPOSITORY,'evangjones99-gif/Roguelike-deckbuilder');
assert.equal(process.env.GITHUB_REF,'refs/heads/codex/lanternbound-production');
assert.match(process.env.GITHUB_SHA??'',/^[a-f0-9]{40}$/);
assert.equal(execFileSync('git',['rev-parse','HEAD'],{encoding:'utf8'}).trim(),process.env.GITHUB_SHA);
const runtime=JSON.parse(fs.readFileSync('dist/build-provenance.json','utf8'));
assert.equal(runtime.sourceDigest,expectedDigest);assert.equal(runtime.version,'0.7.0');
assert.equal(Object.keys(runtime.hashes).length,29);
assert.equal(hash(JSON.stringify(runtime.hashes)),expectedDigest);
for(const [file,sha] of Object.entries(runtime.hashes)) {
  // .gitattributes enforces LF; build.mjs hashes exact raw bytes.
  assert.equal(hash(fs.readFileSync(file)),sha,`Source differs from production provenance: ${file}`);
}
const localAppData=process.env.LOCALAPPDATA;const defaultCache=path.join(localAppData,'hollowpact-updater');
const defaultCacheBefore=await directoryWitness(defaultCache);
const v=layout(localAppData,crypto.randomBytes(16).toString('hex'));
noLinks(v.base);assert.ok(!fs.existsSync(v.base),'QA base already exists');
assert.ok(!fs.existsSync('build-installer'),'Never reuse/overwrite an earlier installer output');
fs.mkdirSync(v.base,{recursive:true});fs.writeFileSync(v.marker,v.token+'\n',{flag:'wx'});
fs.writeFileSync(v.sentinel,'preserve '+v.token+'\n',{flag:'wx'});
fs.mkdirSync('build-installer',{recursive:true});
const include=path.resolve('build-installer','qa-only.nsh');
fs.writeFileSync(include,guardInclude(v),{flag:'wx'});
const {build}=JSON.parse(fs.readFileSync('package.json','utf8'));
const config=builderConfig(build,v,include);
fs.writeFileSync('build-installer/qa-config.json',JSON.stringify(config,null,2)+'\n',{flag:'wx'});
fs.writeFileSync('build-installer/request.json',JSON.stringify({schema:1,version:runtime.version,sourceDigest:expectedDigest,
  expectedAsar,commit:process.env.GITHUB_SHA,ref:process.env.GITHUB_REF,runId:process.env.GITHUB_RUN_ID,
  attempt:process.env.GITHUB_RUN_ATTEMPT,localAppData,defaultCache,defaultCacheBefore,layout:v,includeSHA256:hash(fs.readFileSync(include)),
  configSHA256:hash(fs.readFileSync('build-installer/qa-config.json'))},null,2)+'\n',{flag:'wx'});
console.log('Prepared isolated QA installer configuration; no installer has been executed.');
