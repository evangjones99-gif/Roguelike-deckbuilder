"""Capture explicitly hash-declared temporary bodies without editing their inputs."""
from pathlib import Path
import hashlib, json, sys, tarfile

receipt, destination = map(Path, sys.argv[1:])
original = receipt.read_bytes()
declared = json.loads(original)['files']
assert isinstance(declared, list)
def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        while block := f.read(1024 * 1024):
            h.update(block)
    return h.hexdigest()
rows = []
for index, row in enumerate(declared):
    source = Path(row['path'])
    assert source.is_absolute() and source.is_relative_to('/dev/shm')
    assert source.is_file() and not source.is_symlink()
    assert source.stat().st_size == row['bytes']
    assert digest(source) == row['sha256']
    rows.append(dict(row, archivedPath=f'bodies/{index:04d}-{source.name}'))
archive = destination / 'external-temporary-artifacts.tar.gz'
with tarfile.open(archive, 'x:gz') as output:
    entry = output.gettarinfo(str(receipt), arcname='DECLARED-RECEIPTS.json')
    assert entry.isfile()
    with receipt.open('rb') as f:
        output.addfile(entry, f)
    for row in rows:
        source = Path(row['path'])
        entry = output.gettarinfo(str(source), arcname=row['archivedPath'])
        assert entry.isfile() and entry.size == row['bytes']
        with source.open('rb') as f:
            output.addfile(entry, f)
with tarfile.open(archive, 'r:gz') as check:
    assert len(check.getmembers()) == len(rows) + 1
    assert check.extractfile('DECLARED-RECEIPTS.json').read() == original
    for row in rows:
        entry = check.getmember(row['archivedPath'])
        assert entry.isfile() and entry.size == row['bytes']
        h = hashlib.sha256()
        with check.extractfile(entry) as f:
            while block := f.read(1024 * 1024):
                h.update(block)
        assert h.hexdigest() == row['sha256']
        assert digest(Path(row['path'])) == row['sha256']
assert receipt.read_bytes() == original
result = {'originalReceipt': str(receipt),
          'receiptSHA256': hashlib.sha256(original).hexdigest(),
          'archiveBytes': archive.stat().st_size,
          'archiveSHA256': digest(archive), 'files': rows,
          'scope': 'Every explicitly declared temporary regular-file body and exact '
                   'original receipt captured and round-trip verified. Original '
                   'paths and inputs remain unchanged; no raster modification, '
                   'undeclared capture, new runtime or complete source backup claim.'}
with (destination / 'EXTERNAL-BODY-PRESERVATION.json').open('x') as f:
    json.dump(result, f, indent=2)
    f.write('\n')
print(json.dumps({k: v for k, v in result.items() if k != 'files'}))
