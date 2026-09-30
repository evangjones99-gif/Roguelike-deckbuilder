from pathlib import Path
import hashlib,json,zipfile,re
out=Path('reviews/technical-v0.6.1-native-evidence');root=Path('/workspace/scratch/native-windows-v061/run-36791619534-1');assert (root/'transfer-verification.json').is_file();api=json.loads((out/'api-run.json').read_text());manifest=json.loads((root/'evidence-extracted/build-desktop/windows-transfer/manifest.json').read_text());artifacts={a['id']:a for a in api['artifacts']};sha=lambda b:hashlib.sha256(b).hexdigest();downloads=json.loads(Path('/workspace/scratch/native-windows-v061-transfer.json').read_text());assert len(downloads)==9;assert all(d['status']=='fulfilled' for d in downloads);records=[];whole=hashlib.sha256();total=0
for part in manifest['parts']:
 d=next(d for d in downloads if f'-part-{part["index"]:02}-' in d['artifact']['name']);path=Path(d['local']['path']);a=artifacts[d['artifact']['id']];wrapper=path.read_bytes();assert len(wrapper)==a['size_in_bytes'];assert sha(wrapper)==a['digest'].split(':')[1];assert a['workflow_run']['head_sha']=='9e6e7d7e76a2ce606acae24d2f6a27c903b54a5f'
 with zipfile.ZipFile(path) as z:
  assert z.testzip() is None;members=[i.filename for i in z.infolist() if not i.is_dir()];assert len(members)==1;data=z.read(members[0]);assert Path(members[0]).name==part['filename']
 assert len(data)==part['bytes'];assert sha(data)==part['sha256'];assert data==(root/'parts'/part['filename']).read_bytes();whole.update(data);total+=len(data);records.append({'part':part['index'],'artifactId':a['id'],'wrapperSHA':sha(wrapper),'wrapperBytes':len(wrapper),'innerSHA':sha(data),'innerBytes':len(data)})
archive=root/manifest['archive'];blob=archive.read_bytes();assert len(blob)==manifest['bytes']==total==183597187;assert sha(blob)==manifest['sha256']==whole.hexdigest()=='06e48cce30ccd2a8fcfcc7a829ec79d3fa6b628541a19effa368852df0bce90b'
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None;files=[i for i in z.infolist() if not i.is_dir()];assert len(files)==72
 for i in files:
  assert not i.filename.startswith('/') and '..' not in Path(i.filename).parts;assert z.read(i.filename)==(root/'native-extracted'/i.filename).read_bytes()
d=next(d for d in downloads if d['artifact']['id']==11131988966);evidence=Path(d['local']['path']);a=artifacts[d['artifact']['id']];blob=evidence.read_bytes();assert len(blob)==a['size_in_bytes']==9545515;assert sha(blob)==a['digest'].split(':')[1]=='1741107cb452d08eb9c2f33a02f8ff1c64076776892b512cd075747adff6f047';canonical=Path('reviews/windows-native/0.6.1/run-36791619534-1')
with zipfile.ZipFile(evidence) as z:
 assert z.testzip() is None;current=[]
 for i in z.infolist():
  if not i.is_dir() and 'reviews/windows-native/0.6.1/run-36791619534-1/' in i.filename:
   assert z.read(i.filename)==Path(i.filename).read_bytes();assert z.read(i.filename)==(root/'evidence-extracted'/i.filename).read_bytes();current.append(i.filename)
 metadata={'ci-build-provenance.json':'dist/build-provenance.json','ci-builder-config.json':'build-desktop/windows-native-config.json','transfer-manifest.json':'build-desktop/windows-transfer/manifest.json'}
 for target,source in metadata.items():assert (canonical/target).read_bytes()==z.read(source)==(root/'evidence-extracted'/source).read_bytes()
assert len(current)==8
result={'method':'Reviewer independently hashes9API-pinned wrappers,8innerparts,whole ZIP; CRC/every72file byte; original current8evidence and3available metadata copies. No binary execution.','run':api['run'],'wrappersVerified':9,'parts':records,'zipFilesMatched':len(files),'archiveSHA256':manifest['sha256'],'archiveBytes':manifest['bytes'],'currentEvidenceRawFilesByteExact':current,'currentAvailableMetadataCopiesByteExact':metadata,'smallEvidenceArtifactId':a['id'],'smallEvidenceSHA256':a['digest'].split(':')[1],'smallEvidenceBytes':a['size_in_bytes'],'downloadErrors':[],'optionalBuilderEffectiveYAMLNotClaimed':True}
(out/'transfer.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['parts','currentEvidenceRawFilesByteExact']},indent=2))
