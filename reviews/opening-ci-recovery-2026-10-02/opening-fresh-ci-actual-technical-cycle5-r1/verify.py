"""Read-only cycle5 evidence audit; standard library, no artifact execution/extraction."""
import hashlib
import json
from pathlib import Path, PurePosixPath
import resource
import stat
import time
import zipfile

START = time.monotonic()
ROOT = Path('/workspace/scratch/opening-fresh-ci-actual-failures-cycle5-root-r1')
OUT = Path(__file__).parent
HEAD = '812668a3bde673cf9e11d93e5e5fe0e807fadaad'
PIN = '7305136b89237d756d01addaf8807f24e763e026511b48210dd021a31537d225'

def identity(path):
    n = path.stat().st_size
    sha = hashlib.sha256()
    git = hashlib.sha1(f'blob {n}\0'.encode())
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            sha.update(chunk)
            git.update(chunk)
    return {'bytes': n, 'sha256': sha.hexdigest(), 'gitBlobSHA1': git.hexdigest()}

def load(path):
    return json.loads(path.read_text())

receipt_id = identity(ROOT / 'ROOT-RECEIPT.json')
assert receipt_id['sha256'] == PIN
receipt = load(ROOT / 'ROOT-RECEIPT.json')
paths = sorted(p for p in ROOT.rglob('*') if p.is_file())
assert not any(p.is_symlink() for p in ROOT.rglob('*'))
files = {p.relative_to(ROOT).as_posix(): identity(p) for p in paths}
assert set(files) == set(receipt['files']) | {'ROOT-RECEIPT.json'}
for name, expected in receipt['files'].items():
    assert all(files[name][key] == value for key, value in expected.items()), name
assert sum(v['bytes'] for k, v in files.items() if k != 'ROOT-RECEIPT.json') == receipt['bytesBeforeReceipt']
total = sum(v['bytes'] for v in files.values())
assert len(files) == 39 and total == 1009590 and total <= 1048576
carrier = load(ROOT / 'API-CARRIER.json')
assert carrier['metadata'] == receipt['metadata']
assert carrier['metadata']['head'] == HEAD
for phase in ('baseline', 'candidate', 'windows'):
    assert carrier['logs'][phase].encode('utf-8') == (ROOT / f'{phase}-decoded-job.log').read_bytes()

phases = {}
for phase, run, job in [('baseline', 37075095591, 111063078432), ('candidate', 37075095740, 111063079212)]:
    metadata = carrier['metadata'][phase]
    assert metadata['run'] == run and metadata['job'] == job
    artifact = metadata['artifact']
    assert artifact['workflow_run']['id'] == run and artifact['workflow_run']['head_sha'] == HEAD
    zip_id = files[f'{phase}-original.zip']
    assert artifact['size_in_bytes'] == zip_id['bytes']
    assert artifact['digest'] == 'sha256:' + zip_id['sha256']
    members = {}
    with zipfile.ZipFile(ROOT / f'{phase}-original.zip') as archive:
        for member in archive.infolist():
            name = member.filename
            path = PurePosixPath(name)
            assert not path.is_absolute() and '..' not in path.parts and '\\' not in name
            assert path.as_posix() == name and name not in members
            assert stat.S_ISREG(member.external_attr >> 16) and not member.is_dir()
            sha = hashlib.sha256()
            git = hashlib.sha1(f'blob {member.file_size}\0'.encode())
            count = 0
            with archive.open(member) as stream, (ROOT / phase / name).open('rb') as original:
                for chunk in iter(lambda: stream.read(65536), b''):
                    assert original.read(len(chunk)) == chunk, name
                    count += len(chunk)
                    sha.update(chunk)
                    git.update(chunk)
                assert original.read(1) == b''
            members[name] = {'bytes': count, 'sha256': sha.hexdigest(), 'gitBlobSHA1': git.hexdigest(), 'zipCRC32': member.CRC}
            assert count == member.file_size
            assert all(members[name][k] == files[f'{phase}/{name}'][k] for k in ('bytes', 'sha256', 'gitBlobSHA1'))
    assert len(members) == 16
    assert set(members) == {p.relative_to(ROOT / phase).as_posix() for p in (ROOT / phase).rglob('*') if p.is_file()}
    diagnostic = load(ROOT / phase / 'diagnostic-index.json')
    assert set(diagnostic['proofInventory']) == set(members) - {'diagnostic-index.json'}
    for name, expected in diagnostic['proofInventory'].items():
        assert all(members[name][k] == v for k, v in expected.items()), name
    assert diagnostic['status'] == 'FAILED_OR_INCOMPLETE' and diagnostic['runtimeBuildGameplayApproval'] is False
    initial = load(ROOT / phase / 'initialization.json')
    assert initial['run'] == str(run) and initial['attempt'] == '1'
    closure = load(ROOT / phase / 'install-closure.json')
    assert closure['argv'] == ['npm', 'ci', '--ignore-scripts', '--no-audit', '--no-fund']
    assert closure['status'] == 'FAILED' and closure['reason'] == 'supervisor failure: FileNotFoundError'
    assert closure['exit'] == -9 and closure['closureObserved'] and closure['liveAtClosure'] == []
    assert 2 <= closure['elapsedSeconds'] < 5 < closure['stopSeconds'] < closure['wholeSeconds']
    assert closure['sampledAggregatePeakRSS'] < closure['workCapBytes']
    assert closure['minHostOrFiniteCgroupHeadroom'] > closure['reserveBytes']
    assert closure['firstOverflowBytesRetained'] == 0
    assert closure['rawLogComplete'] and closure['receivedRawLogBytes'] == closure['rawLogBytes'] == files[f'{phase}/install.log']['bytes']
    assert closure['rawLogBytes'] < closure['rawLogBudget']
    for stage in ('node-version', 'npm-version'):
        toolclose = load(ROOT / phase / f'{stage}-closure.json')
        assert toolclose['exit'] == 0 and toolclose['closureObserved'] and toolclose['liveAtClosure'] == []
    progress = load(ROOT / phase / 'acquisition-progress.json')
    assert progress['complete'] and progress['expected'] == len(progress['verified'])
    groups = [line for line in carrier['logs'][phase].splitlines() if '##[group]' in line]
    assert any('runner.py" install' in line for line in groups)
    assert not any('runner.py" build' in line or 'runner.py" test' in line for line in groups)
    assert not any(p.name.startswith(('build-', 'test-')) for p in (ROOT / phase).rglob('*'))
    phases[phase] = {'run': run, 'job': job, 'artifactId': artifact['id'], 'zip': zip_id, 'members': members, 'closure': closure, 'acquiredBodyCountReported': len(progress['verified']), 'executedGroups': groups, 'buildTestEvidence': 'No executed build/test command groups or build/test receipts; Root reports skipped. Linux job step API metadata is not included.'}

windows = carrier['metadata']['windows']
assert windows['run'] == 37075108377 and windows['job'] == 111063120179
job = windows['jobs']['jobs'][0]
assert job['run_id'] == windows['run'] and job['id'] == windows['job'] and job['conclusion'] == 'failure'
steps = {s['name']: s['conclusion'] for s in job['steps']}
assert steps['Rules tests'] == steps['Build production runtime'] == steps['Package unsigned Windows executable with resources enabled'] == 'success'
assert steps['Launch packaged Windows executable and verify offline interactions'] == 'failure'
assert steps['Archive candidate and record native resource evidence'] == 'skipped'
assert steps['Split tested native ZIP into bounded transfer parts'] == 'skipped'
log = carrier['logs']['windows']
assert "'0px 0px' !== '0% 0%'" in log and 'scripts/windows-smoke.mjs:134:10' in log
for artifact in windows['artifacts']['artifacts']:
    assert artifact['workflow_run']['head_sha'] == HEAD and artifact['workflow_run']['id'] == windows['run']

result = {'verdict': 'ACCEPT_PRESERVED_BYTES_AND_QUALIFIED_ACTUAL_FAILURE_ONLY', 'head': HEAD, 'rootReceipt': receipt_id, 'rootFiles': files, 'rootInclusiveFiles': len(files), 'rootInclusiveBytes': total, 'rootCapBytes': 1048576, 'phases': phases, 'windows': {'run': windows['run'], 'job': windows['job'], 'steps': steps, 'assertion': "'0px 0px' !== '0% 0%'", 'sourceLocationReported': 'scripts/windows-smoke.mjs:134:10', 'nativeZIPBodiesAudited': False}, 'method': {'streamChunkBytes': 65536, 'noExtractionOrExecution': True, 'elapsedSeconds': time.monotonic() - START, 'peakRSSBytes': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024}, 'limits': 'Sampled runtime limits, not kernel hard guarantees. Shared cgroup values observed only. No exact FileNotFoundError stack/site recorded; npm exit -9 reflects supervisory termination, not a diagnosed npm/bin failure. Decoded UTF8 logs are not original HTTP log-archive bytes. Windows ZIPs are metadata only, not downloaded or reviewed. No repair/source, gameplay, art, default, native support, release or cleanup approval.'}
assert result['method']['peakRSSBytes'] < 64 * 1024 * 1024
with (OUT / 'CHECKS.json').open('x') as f:
    json.dump(result, f, indent=2, sort_keys=True)
    f.write('\n')
print(json.dumps({k: result[k] for k in ('verdict', 'rootInclusiveFiles', 'rootInclusiveBytes', 'method')}))
