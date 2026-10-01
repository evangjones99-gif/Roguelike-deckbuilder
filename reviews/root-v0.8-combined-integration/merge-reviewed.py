"""One-time root semantic merge of separately accepted source candidates."""
from pathlib import Path
import json,hashlib,shutil,zipfile
root=Path.cwd();out=root/'reviews/root-v0.8-combined-integration';old=json.loads((root/'dist/build-provenance.json').read_text());assert old['sourceDigest']=='0be4f01d416e6fc4cca3f19b6916b5b65993b9fd426a926a1ede6d8487834a35'
for name,expected in old['hashes'].items():assert hashlib.sha256((root/name).read_bytes()).hexdigest()==expected,name
assert json.loads((out/'BASELINE-SOURCE.json').read_text())==old
records=[]
with zipfile.ZipFile(root/'releases/0.7.0/hollowpact-0.7.0-web.zip') as z:
 actual={str(p.relative_to(root/'dist')) for p in (root/'dist').rglob('*') if p.is_file()};assert set(z.namelist())==actual
 for rel in sorted(actual):
  b=(root/'dist'/rel).read_bytes();assert z.read(rel)==b
  records.append({'path':rel,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
assert len(records)==15
baseline=Path('/tmp/hollowpact-root-production-baseline-v07');assert not baseline.exists();shutil.move(root/'dist',baseline)
(out/'BASELINE-BUILD-RETENTION.json').write_text(json.dumps({'directory':str(baseline),'scope':'Unchanged exact15 outputs moved as comparison build; every byte matches retained official0.7 web ZIP. TMP is not durable backup.','files':records},indent=2)+'\n')
audio=Path('/workspace/scratch/audio-shipping-v08-r1/candidate');files=[p for p in (audio/'src').glob('audio*') if p.is_file()];assert len(files)==5
for p in files+[audio/'src/main.ts',audio/'desktop/main.cjs',audio/'desktop/audio-lifecycle.cjs']:
 dest=root/p.relative_to(audio);shutil.copyfile(p,dest)
(root/'public/audio').mkdir(exist_ok=False)
for p in (audio/'public/audio').glob('*.wav'):shutil.copyfile(p,root/'public/audio'/p.name)
assert len(list((root/'public/audio').glob('*.wav')))==39
enc=Path('/workspace/scratch/encounter-art-author-v08-r2/candidate')
for name in ['src/art.ts','src/arena.ts','src/encounter-environment.ts','public/art/ossuary-crypt-v08-r2.png']:shutil.copyfile(enc/name,root/name)
shutil.copyfile(audio/'THIRD-PARTY.md',root/'THIRD-PARTY.md')
with (root/'THIRD-PARTY.md').open('a') as f:f.write('\n- v0.8 adds an original AI-generated ossuary crypt panorama for reconstructed necromancer/spectral encounters. Original pixels, exact request, rejected drafts and generation provenance are retained in assets/art-sources/v0.8/crypt-r2 and canonical crypt-panorama-v0.8-r2-* evidence. Rights review and store AI-content disclosure remain pending.\n')
art=Path('/workspace/scratch/crypt-panorama-author-v08-r2');dest=root/'assets/art-sources/v0.8/crypt-r2';dest.mkdir(parents=True,exist_ok=False)
for name in ['generated-original.png','REQUEST.txt','PROVENANCE.json','README.md','PLACEMENT-MATH.json','FROZEN-FILES.json']:shutil.copyfile(art/name,dest/name)
provenance=root/'public/art/PROVENANCE.json';d=json.loads(provenance.read_text());d['version']='0.8.0';d['sourceRecords']+=' v0.8 exact crypt generation request, original PNG and placement/provenance remain in assets/art-sources/v0.8/crypt-r2; full rejected studies and independent evidence remain canonical.'
d['images'].append({'file':'ossuary-crypt-v08-r2.png','sha256':'ff9818614003e9432ee1868c2f60b336d0b5dfe63f5c01e380832f1e880c4b00','width':2069,'height':760,'mode':'RGB','creatorTool':'image_gen.imagegen','rightsReview':'pending before commercial distribution','preservedSource':'assets/art-sources/v0.8/crypt-r2/generated-original.png','preservedRequest':'assets/art-sources/v0.8/crypt-r2/REQUEST.txt','firstIntroducedVersion':'0.8.0','presentation':'Original unchanged painted environment. Pure canonical original encounter context selects necromancer/spectral contracts; legacy nonboss encounters retain the abbey.'})
provenance.write_text(json.dumps(d,indent=2)+'\n')
shutil.copyfile('/workspace/scratch/audio-shipping-v08-r1/AUDIO-PROVENANCE.json',out/'AUDIO-PROVENANCE.json')
for name in ['package.json','package-lock.json']:
 p=root/name;d=json.loads(p.read_text());assert d['version']=='0.7.0';d['version']='0.8.0'
 if name=='package-lock.json':assert d['packages']['']['version']=='0.7.0';d['packages']['']['version']='0.8.0'
 p.write_text(json.dumps(d,indent=2)+'\n')
print('Merged reviewed audio/selector; exact old15 outputs retained. Apply only accepted three hound timing hunks next.')
