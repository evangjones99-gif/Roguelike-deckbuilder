"""Preserve declared hashed file bytes, never traverse directory aliases."""
from pathlib import Path, PurePosixPath
import hashlib, json, shutil, sys, tarfile

source, destination, manifest_name = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
def sha(file):
    digest = hashlib.sha256()
    with file.open('rb') as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()

manifest = source / manifest_name
data = json.loads(manifest.read_text())
rows = data.get('files', data)
if isinstance(rows, dict):
    rows = [dict(value, path=name) for name, value in rows.items()]
records, excluded = [], []
for row in rows:
    name = row['path']
    relative = PurePosixPath(name)
    assert not relative.is_absolute() and '..' not in relative.parts
    file = source / name
    if 'sha256' not in row:
        assert row.get('type') == 'symlink' and file.is_symlink()
        assert str(file.readlink()) == row['target']
        excluded.append(row)
        continue
    assert file.is_file() and sha(file) == row['sha256'], name
    if 'bytes' in row:
        assert file.stat().st_size == row['bytes'], name
    records.append({'path': name, 'bytes': file.stat().st_size,
                    'sha256': row['sha256'],
                    'referenceTarget': str(file.resolve()) if file.is_symlink() else None})
records.append({'path': manifest_name, 'bytes': manifest.stat().st_size,
                'sha256': sha(manifest), 'referenceTarget': None})
destination.mkdir(exist_ok=False)
archive = destination / 'curated-evidence.tar.gz'
with tarfile.open(archive, 'x:gz') as output:
    for row in records:
        file = source / row['path']
        entry = output.gettarinfo(str(file.resolve()), arcname=row['path'])
        assert entry.isfile()
        with file.open('rb') as handle:
            output.addfile(entry, handle)
with tarfile.open(archive, 'r:gz') as check:
    assert len(check.getmembers()) == len(records)
    for row in records:
        entry = check.getmember(row['path'])
        assert entry.isfile() and entry.size == row['bytes']
        digest = hashlib.sha256()
        with check.extractfile(entry) as handle:
            while chunk := handle.read(1024 * 1024):
                digest.update(chunk)
        assert digest.hexdigest() == row['sha256']
for row in records:
    if '/' not in row['path'] and (row['path'].endswith('.md') or row['path'] == manifest_name):
        shutil.copyfile(source / row['path'], destination / row['path'])
receipt = {'sourceDirectory': str(source), 'archiveBytes': archive.stat().st_size,
           'archiveSHA256': sha(archive), 'everyDeclaredHashedFileRoundTripVerified': True,
           'excludedUnhashedAliases': excluded, 'files': records,
           'scope': 'Only declared hashed regular-file bytes and exact original manifest. '
                    'Unhashed directory aliases retain their manifest targets; they are '
                    'not traversed or claimed as archived dependency/source backups. '
                    'Original packets and external dependencies remain unchanged.'}
(destination / 'PRESERVATION.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps({key: value for key, value in receipt.items() if key != 'files'}))
