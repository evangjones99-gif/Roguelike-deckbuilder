"""Point the reviewed bundle producer at matching preserved package inputs."""
from pathlib import Path
import hashlib,json,os
ROOT=Path('/workspace/Roguelike-deckbuilder');HERE=Path(__file__).parent
LINUX=Path('/tmp/hollowpact-linux-v08-width-r1/linux-unpacked')
PROXY=Path('/tmp/hollowpact-v08-windows-asar-only-independent-run-36806506465')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(1048576):h.update(b)
 return h.hexdigest()
inventory=json.loads((ROOT/'reviews/root-v0.8-hunter-width-integration/LINUX-PACKAGE-IDENTITY-r2.json').read_text())
expected={r['path']:r for r in inventory['packrecords']}
actual={str(p.relative_to(LINUX)) for p in LINUX.rglob('*') if p.is_file()}
assert actual==set(expected) and len(actual)==74
for name,row in expected.items():
 p=LINUX/name;assert not p.is_symlink() and sha(p)==row['sha256'] and p.stat().st_size==row['bytes'] and p.stat().st_mode&0o7777==row['mode']
assert {str(p.relative_to(PROXY)) for p in PROXY.rglob('*') if p.is_file()}=={'resources/app.asar'}
assert sha(PROXY/'resources/app.asar')==inventory['asarSHA256']=='c383c4437ac5467146174c6ea039b2a8b28af43d609701379e8cf695f59d530c'
pointer=ROOT/'build-desktop/linux-unpacked';old=ROOT/'build-desktop/linux-unpacked-v07-before-v08'
windows=ROOT/'build-desktop/win-unpacked'
assert pointer.is_symlink() and os.readlink(pointer)=='/tmp/hollowpact-native-v07/build-desktop/linux-unpacked'
assert not old.exists() and not old.is_symlink() and not windows.exists() and not windows.is_symlink()
record={'previousLinuxPointer':str(pointer),'previousLinuxTarget':os.readlink(pointer),'retainedOldPointer':str(old),'matchingLinux':str(LINUX),'linuxFiles':74,'windowsAsarOnlyProxy':str(PROXY),'scope':'Current Linux74-file package preserved and used for TAR. Windows pointer is ASAR-ONLY validation proxy for reviewed bundle mode; never a complete package/default Windows repack/launch. Exact original Windows ZIP is separately added. All old original files remain unchanged.'}
with (HERE/'PACKAGE-STAGING.json').open('x') as f:json.dump(record,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
os.rename(pointer,old);os.symlink(str(LINUX),pointer);os.symlink(str(PROXY),windows)
assert old.resolve()==Path(record['previousLinuxTarget']) and pointer.resolve()==LINUX and windows.resolve()==PROXY
print(json.dumps(record))
