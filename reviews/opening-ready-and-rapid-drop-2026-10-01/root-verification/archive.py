import pathlib, hashlib, json, tarfile, gzip, io, os, time

scratch = pathlib.Path('/workspace/scratch')
repo = pathlib.Path('/workspace/Roguelike-deckbuilder')
out = repo / 'reviews/opening-ready-and-rapid-drop-2026-10-01'
out.mkdir(exist_ok=False)
names = '''ready-coach-comparison-actual-r1 ready-coach-actual-gameplay-independent-r1 ready-coach-actual-technical-independent-r1 ready-coach-visual-independent-r1 ready-coach-default-source-root-r1 ready-coach-default-source-technical-independent-r1 ready-default-build-method-independent-r1 ready-default-build-root-r1 ready-default-build-technical-independent-r1 ready-default-300-caller-root-r1 ready-default-300-caller-independent-r1 ready-default-first300-actual-r1 ready-default-first300-post-root-r1 ready-default-first300-gameplay-independent-r1 ready-default-first300-technical-independent-r1 ready-default-first300-visual-independent-r1 ready-default-promotion-root-r1 ready-default-promotion-and-settle-build-independent-r1 settle-drag-source-root-r1 settle-drag-source-technical-independent-r1 settle-drag-build-root-r1 settle-drag-caller-author-r1 settle-drag-caller-author-r2 settle-drag-caller-technical-independent-r1 settle-drag-caller-technical-independent-r2 settle-drag-comparison-actual-r1 settle-drag-actual-gameplay-independent-r1 settle-drag-actual-technical-independent-r1 settle-drag-actual-visual-independent-r1 cairn128-private-media-encoding-independent-r1 cairn128-private-media-encoding-independent-r2 cairn128-private-media-encoding-independent-r3 cairn128-encoding-sharing-post-independent-r1 cairn-contact-native-author-r1 primary-opening-input-feel-research-root-r1 primary-five-minute-loops-research-root-r1 primary-small-team-craft-research-root-r1'''.split()
names += ['cairn128-encoding-sharing-transaction-root-r1', 'cairn128-encoding-sharing-guard-root-r1']
entries, excluded, blobs = [], [], {}
media = {'.png', '.jpg', '.jpeg', '.wav', '.webp', '.mp4', '.zip', '.gz'}

def digest(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        while chunk := f.read(65536): h.update(chunk)
    return h.hexdigest()

def record(p, logical, keep=True):
    assert p.is_file() and not p.is_symlink(), str(p)
    item = {'path': logical, 'originalPath': str(p), 'bytes': p.stat().st_size, 'sha256': digest(p)}
    if keep:
        entries.append(item)
        blobs.setdefault(item['sha256'], p)
    else:
        item['reason'] = 'Body retained at original path; excluded from this bounded evidence capsule, not retired.'
        excluded.append(item)

for name in names:
    root = scratch / name
    assert root.is_dir(), name
    for p in sorted(root.rglob('*')):
        if not p.is_file() or p.is_symlink(): continue
        keep = p.suffix.lower() not in media
        if p.suffix.lower() in {'.jpg', '.jpeg'}:
            keep = name == 'ready-default-first300-actual-r1' or (name == 'settle-drag-comparison-actual-r1' and '-hold-release-' in p.name)
        record(p, 'packets/' + name + '/' + p.relative_to(root).as_posix(), keep)

stage = scratch / 'ready-default-stage-r1'
freeze = json.loads((scratch / 'ready-default-build-root-r1/RUNTIME-FREEZE.json').read_text())
for rel, expected in freeze['inputs'].items():
    p = stage / rel
    assert digest(p) == expected, rel
    record(p.resolve(), 'selected/inputs/' + rel, p.suffix.lower() not in media)
for rel, expected in freeze['outputs'].items():
    p = stage / 'dist' / rel
    assert digest(p) == expected, rel
    record(p.resolve(), 'selected/outputs/' + rel, p.suffix.lower() not in media)
for directory in ['tests', 'scripts', 'reviews']:
    for p in sorted((stage / directory).rglob('*')):
        if p.is_file() and not p.is_symlink(): record(p, 'selected/typecheck-support/' + p.relative_to(stage).as_posix())
record(stage / 'playwright.config.ts', 'selected/typecheck-support/playwright.config.ts')
for name in ['ready-coach-comparison-grant-root-r1.json', 'ready-default-first300-grant-root-r1.json', 'settle-drag-comparison-grant-root-r1.json', 'share-reviewed-cairn128-encodings-root-r1.py', 'share-reviewed-cairn128-encodings-root-r2.py', 'share-reviewed-cairn128-encodings-root-r3.py', 'cairn128-encoding-sharing-judgment-root-r1.json', 'cairn128-encoding-sharing-judgment-root-r2.json', 'cairn128-encoding-sharing-root-checks-r1.json', 'cairn128-encoding-sharing-git-hold-readback-root-r1.json']:
    record(scratch / name, 'root-controls/' + name)
record(pathlib.Path('/workspace/SECONDARY-EVIDENCE.json'), 'external-review-input/SECONDARY-EVIDENCE.json')
record(pathlib.Path(__file__), 'capsule-author/archive.py')

manifest = {'kind': 'bounded development evidence capsule, not a release or self-contained game', 'sourceDigest': freeze['sourceDigest'], 'outputsDigest': freeze['outputsDigest'], 'inputCount': len(freeze['inputs']), 'outputCount': len(freeze['outputs']), 'entries': entries, 'excludedRetainedBodies': excluded, 'bodyEncoding': 'content-addressed SHA256 blobs; manifest maps each logical and original path', 'captureScope': 'All six actual default first300 original JPEGs and the two actual held-release originals. Other original photos/media retained and pinned outside the capsule.', 'limitations': 'Includes negative candidates and source-reader failures; mechanical pass is not query improvement or human fun. Workflow media mounts are not OS read-only or a self-contained release. No deletion or retirement occurs.'}
raw = (json.dumps(manifest, indent=2) + '\n').encode()
manifest_sha = hashlib.sha256(raw).hexdigest()
archive = out / 'evidence.tar.gz'
with archive.open('xb') as f, gzip.GzipFile(fileobj=f, mode='wb', mtime=0, compresslevel=9) as gz, tarfile.open(fileobj=gz, mode='w|') as tar:
    info = tarfile.TarInfo('MANIFEST.json'); info.size = len(raw); info.mode = 0o600
    tar.addfile(info, io.BytesIO(raw))
    for sha, p in sorted(blobs.items()):
        info = tarfile.TarInfo('blobs/' + sha); info.size = p.stat().st_size; info.mode = 0o600
        with p.open('rb') as body: tar.addfile(info, body)
    f.flush()
assert archive.stat().st_size <= 2621440, ('capsule size limit', archive.stat().st_size)
verified = set()
with tarfile.open(archive, 'r|gz') as tar:
    for member in tar:
        with tar.extractfile(member) as body:
            h = hashlib.sha256()
            while chunk := body.read(65536): h.update(chunk)
        got = h.hexdigest()
        if member.name == 'MANIFEST.json': assert got == manifest_sha
        else:
            sha = member.name.removeprefix('blobs/')
            assert got == sha and sha in blobs
            verified.add(sha)
assert verified == set(blobs)
for item in entries + excluded: assert digest(pathlib.Path(item['originalPath'])) == item['sha256'], item['originalPath']
summary = {k: manifest[k] for k in ['kind', 'sourceDigest', 'outputsDigest', 'inputCount', 'outputCount', 'captureScope', 'limitations']}
summary.update({'archiveSHA256': digest(archive), 'archiveBytes': archive.stat().st_size, 'manifestSHA256': manifest_sha, 'logicalBodies': len(entries), 'uniqueBlobs': len(blobs), 'retainedExcludedBodies': len(excluded), 'roundtripAllUniqueBodies': True, 'originalBodiesRechecked': True, 'freeBytesAfter': os.statvfs(out).f_bavail * os.statvfs(out).f_frsize})
(out / 'SUMMARY.json').write_text(json.dumps(summary, indent=2) + '\n')
(out / 'README.md').write_text('# Opening READY and rapid-card evidence\n\nThe selected default READY cue is the only promoted gameplay presentation change. The private settleDrag trial showed no benefit and remains unselected. The actual first300 did not finish an encounter.\n\n`evidence.tar.gz` uses a logical-path manifest and content-addressed blobs. It preserves complete raw saves, source/build identities, callers, independent findings, read-method failures, resource/closure receipts, rollback code and selected captures. See SUMMARY.json for hashes and exclusions. All excluded original images/media remain at their pinned original paths; this is not full archival coverage, a self-contained game release or permission to retire them.\n\nNo human enjoyment, fully pixel scene, guaranteed drag repair or Steam/platform qualification is established.\n')
print(json.dumps(summary))
