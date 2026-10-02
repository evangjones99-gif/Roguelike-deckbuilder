// Exercise only the exact changed assertion, without importing the native smoke script.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import vm from 'node:vm';
import assert from 'node:assert/strict';

const directory = path.dirname(fileURLToPath(import.meta.url));
const proposed = fs.readFileSync(path.join(directory, 'windows-smoke.proposed.mjs'), 'utf8');
const before = fs.readFileSync(path.join(directory, 'windows-smoke.before.mjs'), 'utf8');
const oldLine = "  assert.equal(evidence.portrait.backgroundPosition, '0% 0%');";
const newBlock = proposed.match(/^  \/\/ CSSOM may serialize[^\n]*\n  assert\.ok\([^\n]*\n    'Title hunter crop must stay at zero on both axes'\);$/m)?.[0];
assert.ok(newBlock, 'Exact proposed assertion block absent');
assert.equal(before.split(oldLine).length, 2, 'Original assertion is not unique');
assert.equal(before.replace(oldLine, newBlock), proposed, 'Changes escape the one assertion block');
const accepted = ['0% 0%', '0px 0px', '0% 0px', '0px 0%'];
const rejected = [
  '1px 0px', '0px 1px', '-1px 0px', '0px -1px',
  '0.001px 0px', '0px 0.001px', '1% 0%', '0% 1%', '-1% 0%', '0% -1%',
  '50% 0%', '0% 100%', '100% 100%', '512px 0px', '0px 512px',
  'left top', 'center center', 'right bottom', '0em 0em', '0 0',
  'calc(0px) 0px', '0px 0px, 0px 0px', '0px', '',
  ' 0px 0px', '0px 0px ', '0px  0px', '0px\t0px', '0px 0px\n',
  '0.0px 0px', '-0px 0px', null, undefined, 0,
];
const run = (value, block = newBlock) => vm.runInNewContext(block,
  {assert, evidence: {portrait: {backgroundPosition: value}}}, {timeout: 50});
const results = [];
for (const value of accepted) {
  run(value);
  results.push({value, accepted: true, pass: true});
}
for (const value of rejected) {
  assert.throws(() => run(value), error => error.code === 'ERR_ASSERTION', `Unexpected acceptance: ${String(value)}`);
  results.push({value: value === undefined ? '<undefined>' : value, accepted: false, pass: true});
}
run('0% 0%', oldLine);
assert.throws(() => run('0px 0px', oldLine), error => error.code === 'ERR_ASSERTION');
const actualPath = '/workspace/scratch/windows-opening-smoke-actual-evidence-r2/selected/reviews/windows-native/0.9.0/run-37075108377-1/smoke.json';
const actual = JSON.parse(fs.readFileSync(actualPath, 'utf8'));
assert.equal(actual.runId, '37075108377');
assert.equal(actual.failedPhase, 'decode actual packaged hunt-entry hunter sheet');
assert.deepEqual({width: actual.portrait.width, height: actual.portrait.height,
  protocol: actual.portrait.protocol, size: actual.portrait.backgroundSize},
  {width: 1536, height: 1024, protocol: 'file:', size: '300% 200%'});
assert.ok(new URL(actual.portrait.url).pathname.endsWith('/dist/art/hunter-marek-v07-r3.png'));
assert.equal(actual.portrait.backgroundPosition, '0px 0px');
run(actual.portrait.backgroundPosition);
assert.throws(() => run(actual.portrait.backgroundPosition, oldLine), error => error.code === 'ERR_ASSERTION');
const report = {status: 'PASS_PURE_ASSERTION_CASES', cases: results, acceptedCount: accepted.length,
  rejectedCount: rejected.length, reproducesOldObservedFailure: true,
  currentRunOnlyObservedValue: {path: actualPath, runId: actual.runId, smokeReportedCommit: actual.commit,
    runtimeSourceDigest: actual.runtimeSourceDigest, backgroundPosition: actual.portrait.backgroundPosition,
    oldAssertionRejects: true, proposedAssertionAccepts: true},
  exactOneBlockScopeVerified: true, rawEvidenceSerializationPreserved: true,
  nativeSmokeImportsExecuted: false, browserGameElectronExecuted: false};
fs.writeFileSync(path.join(directory, 'ZERO-POSITION-CASES.json'), JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify({status: report.status, accepted: accepted.length, rejected: rejected.length}));
