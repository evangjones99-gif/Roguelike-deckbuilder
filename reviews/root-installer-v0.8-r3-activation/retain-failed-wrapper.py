"""Preserve new failed native transfer wrappers verbatim; never infer native acceptance."""
import sys,pathlib,hashlib,json,shutil,zipfile
source=pathlib.Path(sys.argv[1]);artifact_id=int(sys.argv[2]);index=int(sys.argv[3]);expected_sha=sys.argv[4];expected_bytes=int(sys.argv[5])
base=pathlib.Path('/tmp/hollowpact-installer-r2-original');base.mkdir(exist_ok=True)
manifest=pathlib.Path('/workspace/scratch/installer-native-independent-run-36802452392/raw-native-evidence/build-installer/installer-transfer/manifest.json')
data=json.loads(manifest.read_text());part=data['parts'][index-1];assert part['index']==index
blob=source.read_bytes();sha=hashlib.sha256(blob).hexdigest();assert sha==expected_sha;assert len(blob)==expected_bytes
if not source.is_symlink():
    target=base/'wrappers'/source.name;target.parent.mkdir(exist_ok=True);assert not target.exists();shutil.move(source,target);source.symlink_to(target)
assert hashlib.sha256(source.read_bytes()).hexdigest()==sha
with zipfile.ZipFile(source) as z:
    assert z.namelist()==[part['filename']];assert z.testzip() is None
    raw=z.read(part['filename']);assert len(raw)==part['bytes'];assert hashlib.sha256(raw).hexdigest()==part['sha256']
    target=base/'parts'/part['filename'];target.parent.mkdir(exist_ok=True)
    with target.open('xb') as f:f.write(raw)
receipt={'artifactId':artifact_id,'index':index,'downloadPath':str(source),'wrapperTarget':str(source.resolve()),'wrapperBytes':len(blob),'wrapperSHA256':sha,'member':part,'allWrapperCRCAndPartHashesVerified':True,'nativeQAStatus':'failed','scope':'Exact failed-run original transfer input; TMP is not durable archive storage. No installation acceptance.'}
out=pathlib.Path('/workspace/Roguelike-deckbuilder/reviews/root-installer-v0.8-r3-activation')/('download-%02d.json'%index)
with out.open('x') as f:json.dump(receipt,f,indent=2);f.write('\n')
print('Verified exact failed original part',index,len(raw),part['sha256'])
