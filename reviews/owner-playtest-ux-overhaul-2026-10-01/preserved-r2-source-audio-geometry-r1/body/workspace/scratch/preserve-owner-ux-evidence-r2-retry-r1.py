#!/usr/bin/env python3
"""Exclusive bounded evidence preservation; no game execution or source edits."""
import contextlib
import hashlib
import json
import os
import pathlib
import resource
import stat
import sys
import time

M = 1024 * 1024
WORK, RESERVE, BODY, TOTAL, RECEIPTS = 24*M, 512*M, 10*M, 64*M, 2*M
resource.setrlimit(resource.RLIMIT_DATA, (WORK, WORK))
ROOT = pathlib.Path('/workspace/Roguelike-deckbuilder')
BASE = ROOT / 'reviews/owner-playtest-ux-overhaul-2026-10-01'
SCRATCH = pathlib.Path('/workspace/scratch')
GAMEPLAY = pathlib.Path('/tmp/standard-sol-owner-ux-gameplay-independent-r1')
FREEZE = SCRATCH / 'owner-ux-r2-runtime-freeze-r1.json'
STAGE = pathlib.Path('/dev/shm/hollowpact-owner-ux-overhaul-root-r2')
RUNTIME = '5d2c2509e14b0a173a7a2ef6180c71f675babe6010a3bf110bc7cd02a6f0e893'
BASELINE = '801db1ce4000c15268569cb047e7388148a65105c7b86208611ceb3aff40f029'
CAPSULES = {
    'earned': BASE / 'preserved-earned-2f1-independent-r1',
    'runtime': BASE / 'preserved-r2-build-root-smoke-r1',
    'source': BASE / 'preserved-r2-source-audio-geometry-r1',
}
DFLAGS = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
RFLAGS = os.O_RDONLY | os.O_NOFOLLOW | os.O_NOATIME
rows, empty_dirs, exclusions, references, plan = [], [], [], [], {}
receipt_bytes = 0
created = []

def stamp(s):
    return {k: getattr(s, 'st_'+k) for k in
            ('dev', 'ino', 'mode', 'uid', 'gid', 'nlink', 'size', 'atime_ns', 'mtime_ns', 'ctime_ns')}

@contextlib.contextmanager
def parent(path):
    path = pathlib.Path(path)
    assert path.is_absolute() and '..' not in path.parts
    fd = os.open('/', DFLAGS)
    try:
        for part in path.parts[1:-1]:
            nxt = os.open(part, DFLAGS, dir_fd=fd)
            os.close(fd)
            fd = nxt
        yield fd, path.name
    finally:
        os.close(fd)

def guard(label, need=0, fresh=False):
    current = int(pathlib.Path('/sys/fs/cgroup/memory.current').read_text())
    maximum = int(pathlib.Path('/sys/fs/cgroup/memory.max').read_text())
    memory = {}
    for line in pathlib.Path('/proc/self/status').read_text().splitlines():
        if line.startswith(('VmRSS:', 'VmHWM:')):
            k, v, _ = line.split(); memory[k[:-1]] = int(v)*1024
    vf = os.statvfs(BASE)
    row = {'label': label, 'current': current, 'maximum': maximum,
           'headroom': maximum-current, 'free': vf.f_bavail*vf.f_frsize,
           **memory}
    assert row['headroom'] >= RESERVE+(WORK if fresh else 0), row
    assert memory['VmHWM'] <= WORK and memory['VmRSS'] <= WORK, row
    assert row['free'] >= need+RECEIPTS+M, row
    return row

def read_json(path):
    with parent(path) as (pfd, name):
        fd = os.open(name, RFLAGS, dir_fd=pfd)
        try:
            before = stamp(os.fstat(fd)); assert before['size'] <= RECEIPTS
            b = bytearray()
            while chunk := os.read(fd, 65536): b.extend(chunk)
            assert stamp(os.fstat(fd)) == before
            assert stamp(os.stat(name, dir_fd=pfd, follow_symlinks=False)) == before
            return json.loads(b)
        finally:
            os.close(fd)

def walk(group, root, profiles=False):
    assert root.is_dir() and not root.is_symlink(), str(root)
    found = []
    for current, dirs, names in os.walk(root, followlinks=False):
        dirs.sort(); names.sort()
        for d in list(dirs):
            path = pathlib.Path(current)/d
            assert not path.is_symlink(), str(path)
            if profiles and d.startswith('profile-'):
                exclusions.append({'path': str(path), 'reason': 'Retained original real-play Chromium profile; no contents read/copied; capsule is not a complete profile archive.'})
                dirs.remove(d)
        if not dirs and not names: empty_dirs.append({'group': group, 'path': current})
        for n in names:
            path = pathlib.Path(current)/n
            assert stat.S_ISREG(path.lstat().st_mode), str(path)
            found.append(path)
    for path in found: add(group, path)

def add(group, path, expected=None):
    path = pathlib.Path(path)
    with parent(path) as (pfd, name):
        s = os.stat(name, dir_fd=pfd, follow_symlinks=False)
    assert stat.S_ISREG(s.st_mode) and s.st_size <= BODY, str(path)
    key = (group, str(path)); row = {'group': group, 'original': str(path),
        'plannedSourceMetadata': stamp(s), 'expectedSHA256': expected}
    if key in plan:
        assert plan[key] == row
    else: plan[key] = row

def mkdir_exact(path):
    with parent(path) as (pfd, name):
        os.mkdir(name, 0o755, dir_fd=pfd); os.fsync(pfd)

def mkdir_parents(path, capsule):
    relative = path.relative_to(capsule)
    current = capsule
    for part in relative.parts[:-1]:
        current /= part
        if not current.exists(): mkdir_exact(current)
        assert current.is_dir() and not current.is_symlink()

def write_receipt(capsule, name, data):
    global receipt_bytes
    b = (json.dumps(data, indent=2, sort_keys=True)+'\n').encode()
    receipt_bytes += len(b); assert receipt_bytes <= RECEIPTS
    with parent(capsule/name) as (pfd, leaf):
        fd = os.open(leaf, os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW, 0o644, dir_fd=pfd)
        try:
            view = memoryview(b)
            while view: view = view[os.write(fd, view):]
            os.fsync(fd)
        finally: os.close(fd)
        os.fsync(pfd)
    return {'path': str(capsule/name), 'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest()}

def copy_one(row):
    source = pathlib.Path(row['original'])
    capsule = CAPSULES[row['group']]
    target = capsule/'body'/str(source).lstrip('/')
    mkdir_parents(target, capsule)
    guard('before-copy', row['plannedSourceMetadata']['size'], fresh=True)
    with parent(source) as (sparent, sname), parent(target) as (dparent, dname):
        sfd = os.open(sname, RFLAGS, dir_fd=sparent)
        dfd = None
        try:
            before = stamp(os.fstat(sfd)); assert before == row['plannedSourceMetadata']
            assert stat.S_ISREG(before['mode']) and before['size'] <= BODY
            dfd = os.open(dname, os.O_RDWR|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_NOATIME, 0o600, dir_fd=dparent)
            h = hashlib.sha256(); count = 0
            while chunk := os.read(sfd, 65536):
                count += len(chunk); assert count <= BODY; h.update(chunk)
                view = memoryview(chunk)
                while view: view = view[os.write(dfd, view):]
                guard('stream-copy')
            digest = h.hexdigest(); assert count == before['size']
            if row['expectedSHA256']: assert digest == row['expectedSHA256'], str(source)
            ds = os.fstat(dfd)
            if (ds.st_uid, ds.st_gid) != (before['uid'], before['gid']):
                os.fchown(dfd, before['uid'], before['gid'])
            os.fchmod(dfd, stat.S_IMODE(before['mode']))
            os.utime(dfd, ns=(before['atime_ns'], before['mtime_ns']))
            os.fsync(dfd); os.fsync(dparent)
            target_before = stamp(os.fstat(dfd)); os.lseek(dfd, 0, os.SEEK_SET)
            rh = hashlib.sha256()
            while chunk := os.read(dfd, 65536): rh.update(chunk); guard('roundtrip-hash')
            assert rh.hexdigest() == digest
            assert stamp(os.fstat(dfd)) == target_before
            assert stamp(os.fstat(sfd)) == before
            assert stamp(os.stat(sname, dir_fd=sparent, follow_symlinks=False)) == before
            assert stamp(os.stat(dname, dir_fd=dparent, follow_symlinks=False)) == target_before
            for key in ('mode','uid','gid','size','atime_ns','mtime_ns'):
                assert target_before[key] == before[key]
            assert target_before['nlink'] == 1
            return {**row, 'copy': str(target), 'bytes': count, 'sha256': digest,
                    'sourceBeforeAndAfterExact': before,
                    'copyBeforeAndAfterReadbackExact': target_before,
                    'note': 'Copied bytes and preservable metadata exact. Copy dev/inode/ctime are independently recorded, not claimed equal to the source.'}
        finally:
            if dfd is not None: os.close(dfd)
            os.close(sfd)

try:
    initial = guard('fresh-preservation-admission', TOTAL, fresh=True)
    freeze = read_json(FREEZE)
    assert freeze['stage'] == str(STAGE) and freeze['sourceDigest'] == RUNTIME
    assert freeze['inputCount'] == len(freeze['inputs']) == 85
    assert freeze['outputCount'] == len(freeze['outputs']) == 56
    audit = read_json(GAMEPLAY/'AUDIT-after.json')['variants']['baseline']
    assert audit['sourceDigest'] == BASELINE and audit['root'] == str(ROOT)
    walk('earned', GAMEPLAY, profiles=True)
    for path in sorted(SCRATCH.glob('owner-ux-r2-browser-smoke-r[1-6]')): walk('runtime', path)
    for path in sorted(SCRATCH.glob('owner-ux-r2-semantic-tests-r*')): walk('runtime', path)
    for path in sorted(SCRATCH.glob('owner-ux-r2-strict-build-r*')): walk('runtime', path)
    for path in sorted(SCRATCH.glob('owner-ux-compact-playtest-r[1-4].mjs')): add('runtime', path)
    for path in sorted(pathlib.Path('/tmp').glob('hollowpact-owner-ux-compact-playtest-*')): walk('runtime', path)
    for path in (FREEZE, SCRATCH/'owner-ux-r2-public-copy-r1.json'): add('runtime', path)
    for name in ('compact-intent.test.ts','audio-presentation-delay.test.ts'):
        add('runtime', STAGE/'tests'/name)
    for name in ('standard-sol-field-geometry-integration-r2',
                 'standard-sol-owner-ux-audio-timing-author-r2',
                 'standard-sol-owner-ux-audio-timing-independent-r2',
                 'standard-sol-owner-ux-audio-timing-independent-r2-supplement-r1',
                 'standard-sol-owner-ux-audio-timing-independent-r3',
                 'standard-sol-owner-ux-audio-timing-independent-r4'):
        walk('source', pathlib.Path('/tmp')/name)
    optional = sorted(SCRATCH.glob('owner-ux-r2-source*'))
    for path in optional:
        if path.is_dir(): walk('source', path)
        else: add('source', path)
    if not optional: exclusions.append({'path': str(SCRATCH/'owner-ux-r2-source*'), 'reason': 'No matching source packet existed at enumeration.'})
    add('source', pathlib.Path(__file__).resolve())
    add('source', SCRATCH/'preserve-owner-ux-evidence-r2.py')
    add('source', SCRATCH/'preserve-owner-ux-evidence-r2-failure-r1.json')
    for domain, entries, baseline_entries in (
            ('inputs', freeze['inputs'], audit['inputs']),
            ('outputs', freeze['outputs'], audit['outputs'])):
        for relative, digest in sorted(entries.items()):
            baseline_key = relative if domain == 'inputs' else 'dist/'+relative
            source = STAGE/(relative if domain == 'inputs' else 'dist/'+relative)
            baseline = ROOT/baseline_key
            old = baseline_entries.get(baseline_key)
            if old and old['sha256'] == digest:
                with parent(source) as (pfd, name): metadata = stamp(os.stat(name, dir_fd=pfd, follow_symlinks=False))
                with parent(baseline) as (pfd, name): bs = os.stat(name, dir_fd=pfd, follow_symlinks=False)
                baseline_pin = [bs.st_dev, bs.st_ino, bs.st_mode, bs.st_size, bs.st_mtime_ns, bs.st_ctime_ns]
                assert baseline_pin == old['metadata'], str(baseline)
                references.append({'domain': domain, 'relative': relative, 'sha256': digest,
                    'unchangedBodyReference': str(baseline), 'baselineMetadata': stamp(bs),
                    'r2Metadata': metadata, 'verification': 'Digest equality from full frozen R2 ledger and prior accepted full baseline audit; baseline identity checked now. Unchanged bodies not reread or duplicated.'})
            else: add('runtime', source, expected=digest)
    total = sum(x['plannedSourceMetadata']['size'] for x in plan.values())
    assert total <= TOTAL
    guard('enumerated-admission', total, fresh=True)
    for capsule in CAPSULES.values(): mkdir_exact(capsule); created.append(capsule)
    input_manifest = {'status': 'enumerated before copying', 'time_ns': time.time_ns(),
        'helper': str(pathlib.Path(__file__).resolve()), 'bodyCap': BODY, 'aggregateBodyCap': TOTAL,
        'memoryWork': WORK, 'reserve': RESERVE, 'receiptCap': RECEIPTS, 'diskResidual': M,
        'initialResource': initial, 'plannedBodyBytes': total, 'files': list(plan.values()),
        'emptyOriginalDirectories': empty_dirs, 'exclusions': exclusions,
        'unchangedR2BodyReferences': references,
        'direction': 'Preserve evidence only. R2 strict build and 390 smoke passed; desktop resource failures retained. Earned 2f1 qualified REJECT. ROOT801db unchanged. No AAA, milestone or promotion claim.'}
    write_receipt(CAPSULES['runtime'], 'INPUT-MANIFEST.json', input_manifest)
    for row in plan.values(): rows.append(copy_one(row))
    # A final original/copy identity pass closes the copying interval.
    for row in rows:
        for path, expected in ((row['original'], row['sourceBeforeAndAfterExact']),
                               (row['copy'], row['copyBeforeAndAfterReadbackExact'])):
            with parent(path) as (pfd, name): assert stamp(os.stat(name, dir_fd=pfd, follow_symlinks=False)) == expected, path
    identities = []
    for group, capsule in CAPSULES.items():
        manifest = {'status': 'PASS exclusive streamed byte/hash/metadata roundtrip',
            'group': group, 'files': [r for r in rows if r['group'] == group],
            'allOriginalsRetained': True, 'exclusions': exclusions,
            'fullR2Freeze': str(CAPSULES['runtime']/'body'/str(FREEZE).lstrip('/')),
            'r2Digest': RUNTIME, 'baselineDigest': BASELINE,
            'unchangedR2BodyReferences': references if group == 'runtime' else [],
            'limitations': ['Not a complete Chromium profile capsule.', 'Unchanged R2 bodies remain explicit ROOT baseline references; full byte ledger preserved.', 'Preservation author check is not independent acceptance.', 'No new gameplay, build, test, audio-listening, AAA or promotion result.'],
            'finalResource': guard('receipt-finalization')}
        identities.append(write_receipt(capsule, 'PRESERVATION.json', manifest))
    print(json.dumps({'status': 'PASS preservation author roundtrip', 'files': len(rows),
        'bytes': total, 'unchangedReferences': len(references), 'identities': identities,
        'resource': guard('complete'), 'independentCheckRequired': True}))
except BaseException as error:
    for capsule in created:
        try: write_receipt(capsule, 'FAILURE.json', {'status': 'FAILED; preserve all partial bodies and originals', 'error': repr(error), 'copiedRows': rows})
        except BaseException: pass
    raise
