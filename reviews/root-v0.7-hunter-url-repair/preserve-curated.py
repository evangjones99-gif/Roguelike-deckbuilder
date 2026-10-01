"""Append-only curated evidence capture. Never modifies original inputs."""
import hashlib, json, pathlib, shutil, tarfile

BASE = pathlib.Path('/workspace/scratch')
DEST = pathlib.Path('/workspace/Roguelike-deckbuilder/reviews')

def digest(stream):
    h = hashlib.sha256()
    for block in iter(lambda: stream.read(1024 * 1024), b''):
        h.update(block)
    return h.hexdigest()

def capture(name, target, manifest):
    root = BASE / name
    out = DEST / target
    out.mkdir(exist_ok=False)
    declared = {}
    if manifest.endswith('.json'):
        data = json.loads((root / manifest).read_text())
        records = data.get('files', data)
        if isinstance(records, dict):
            declared = records
        else:
            declared = {r['path']: r['sha256'] for r in records}
    else:
        for line in (root / manifest).read_text().splitlines():
            sha, path = line.split(None, 1)
            declared[path.lstrip(' *')] = sha
    paths = set(declared) | {manifest}
    if (root / 'ADDENDUM-MANIFEST-001.json').exists():
        extra = json.loads((root / 'ADDENDUM-MANIFEST-001.json').read_text())
        for r in extra['files']:
            declared[r['path']] = r['sha256']
        paths |= set(declared) | {'ADDENDUM-MANIFEST-001.json'}
    entries = []
    for name in sorted(paths):
        rel = pathlib.PurePosixPath(name)
        assert not rel.is_absolute() and '..' not in rel.parts
        file = root / rel
        assert file.is_file() and not file.is_symlink(), file
        with file.open('rb') as stream:
            sha = digest(stream)
        if name in declared:
            assert sha == declared[name], (name, sha, declared[name])
        entries.append({'path': name, 'bytes': file.stat().st_size, 'sha256': sha})
    archive = out / 'curated-evidence.tar.gz'
    with tarfile.open(archive, 'x:gz') as tar:
        for entry in entries:
            tar.add(root / entry['path'], arcname=entry['path'], recursive=False)
    with tarfile.open(archive, 'r:gz') as tar:
        assert {r.name for r in tar.getmembers()} == paths
        for entry in entries:
            member = tar.getmember(entry['path'])
            assert member.isfile() and member.size == entry['bytes']
            with tar.extractfile(member) as stream:
                assert digest(stream) == entry['sha256']
    for entry in entries:
        file = root / entry['path']
        if '/' not in entry['path'] and (file.suffix == '.md' or entry['path'] == manifest or 'ADDENDUM' in file.name):
            shutil.copyfile(file, out / file.name)
    with archive.open('rb') as stream:
        sha = digest(stream)
    receipt = {'sourceDirectory': str(root), 'curatedOnly': True,
               'scope': 'Exact manifest-listed evidence; support dependency symlinks and temporary browser profiles remain at original paths.',
               'archive': archive.name, 'archiveBytes': archive.stat().st_size,
               'archiveSHA256': sha, 'everyMemberStreamVerified': True, 'files': entries}
    (out / 'PRESERVATION.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(target, len(entries), archive.stat().st_size, sha, flush=True)

if __name__ == '__main__':
    import sys
    capture(*sys.argv[1:])
