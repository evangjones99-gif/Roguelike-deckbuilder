"""Recover exact tested ZIP from authenticated, independently pinned wrappers."""
from pathlib import Path
import hashlib, json, os, zipfile

ROOT = Path('/workspace/retained-native-experiments/windows-run-36806506465')
MANIFEST = Path('/workspace/scratch/windows-native-independent-v08-run-36806506465/raw-small-members/build-desktop/windows-transfer/manifest.json')
WRAPPERS = [
 ('/workspace/attachments/f5626c5c-e38e-4b13-957d-55f9b64fff61/hollowpact-v08-part-01-wrapper.zip','3cc5393d9846363e39f2af10e9eb75cc080d15b2c8c087291c315a7bbdf7c0c0'),
 ('/workspace/attachments/c932c5ca-a11d-48c5-af39-14c986d9435b/hollowpact-v08-part-02-wrapper.zip','31d2afa556f6150bcbc6e049f2e61f6e42adc96b1e83df628d84dfd1a3a1cdba'),
 ('/workspace/attachments/cfe874b9-eace-4f30-82e6-a078057deb24/hollowpact-v08-part-03-wrapper.zip','1b282438e7bb1dbfa4726f0617198374f97c0a1469cd5d1d77bf3c6fb261ace9'),
 ('/workspace/attachments/606ead1b-64f4-44e8-8b9a-77d7b856d782/hollowpact-v08-part-04-wrapper.zip','2ff076e443d91e6e03736ce67ffe5bb2218728769ce61a189f46324bcae0f6ba'),
 ('/workspace/attachments/c3697e52-57cf-48cb-b9ef-db997e91cbfe/hollowpact-v08-part-05-wrapper.zip','c4a072669d879ff4124ee89caf67a832a0f98a163a3507021624593756a11cc9'),
 ('/workspace/attachments/98c0c74c-7d05-4c1a-b621-928c2939dac6/hollowpact-v08-part-06-wrapper.zip','72e3be0057dc79a2593ddf7a496715277a913db58bf42dbb49f83dce3a6a4634'),
 ('/workspace/attachments/9ac53102-39bf-41b7-b9a5-0dbb0b91840b/hollowpact-v08-part-07-wrapper.zip','85f793346a4c7ba3fa525acb405ec0e2051ea6598f74fadc9b074b1ff4b4e24d'),
 ('/workspace/attachments/029356e8-50f8-4dfe-95fe-f0063c5dcb0e/hollowpact-v08-part-08-wrapper.zip','27092d7152b25b1c86d680e751006c9e907913a3e00ed3c68a1674df0c780613'),
]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(1048576): h.update(b)
 return h.hexdigest()
manifest=json.loads(MANIFEST.read_bytes())
assert manifest['sourceDigest']=='23477f68c99d6d60b0b3f82b286a8d33bb6da6f2ca92c103fbecf5663634959f'
assert manifest['sha256']=='1ce6c74baea02686183e833c28738e04d19f80d5826218a0d732eff304dce563'
assert len(manifest['parts'])==len(WRAPPERS)==8
rows=[]
for (raw,expected),part in zip(WRAPPERS,manifest['parts']):
 p=Path(raw); assert p.is_file() and not p.is_symlink() and sha(p)==expected
 with zipfile.ZipFile(p) as z:
  leaves=[m for m in z.infolist() if not m.is_dir()]
  assert len(leaves)==1 and leaves[0].filename==part['filename'] and leaves[0].file_size==part['bytes']
  assert z.testzip() is None
 rows.append({'path':raw,'bytes':p.stat().st_size,'sha256':expected,'member':part})
ROOT.mkdir(exist_ok=False,parents=True)
(ROOT/'manifest.original.json').write_bytes(MANIFEST.read_bytes())
out=ROOT/manifest['archive']
with out.open('xb') as dest:
 for row in rows:
  h=hashlib.sha256();n=0
  with zipfile.ZipFile(row['path']) as z, z.open(row['member']['filename']) as source:
   while b:=source.read(1048576):dest.write(b);h.update(b);n+=len(b)
  assert n==row['member']['bytes'] and h.hexdigest()==row['member']['sha256']
 dest.flush();os.fsync(dest.fileno())
assert out.stat().st_size==manifest['bytes'] and sha(out)==manifest['sha256']
with zipfile.ZipFile(out) as z: assert z.testzip() is None
receipt={'runtime':manifest['sourceDigest'],'archive':str(out),'bytes':out.stat().st_size,'sha256':sha(out),'wrappers':rows,'scope':'Exact original tested portable Windows archive. All wrappers, parts and whole ZIP checked; no repacking or local Windows execution. Raw wrappers remain at original paths. Native member/ASAR/PE independent audit pending.'}
(ROOT/'RECOVERY.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items() if k!='wrappers'}))
