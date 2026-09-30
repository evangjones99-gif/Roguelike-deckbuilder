from pathlib import Path
import hashlib,json,zipfile
out=Path('reviews/technical-v0.6-native-evidence');root=Path('/workspace/scratch/native-windows-v06/run-36789372782-1');api=json.loads((out/'api-run.json').read_text());manifest=json.loads((root/'evidence-extracted/build-desktop/windows-transfer/manifest.json').read_text());artifacts={a['id']:a for a in api['artifacts']};sha=lambda b:hashlib.sha256(b).hexdigest()
downloads=json.loads((root/'downloads-r1.json').read_text());downloads=[d for d in downloads if d['status']=='fulfilled']+[json.loads((root/'download-part8-r2.json').read_text())];records=[];whole=hashlib.sha256();total=0
for part in manifest['parts']:
 d=next(d for d in downloads if d['part']==part['index']);path=Path(d['local']['path']);a=artifacts[d['artifact']['id']];wrapper=path.read_bytes();assert len(wrapper)==a['size_in_bytes'];assert sha(wrapper)==a['digest'].split(':')[1];assert a['workflow_run']['head_sha']=='f54a64d6bed7f1d63607d9efde2b26176e303724'
 with zipfile.ZipFile(path) as z:
  assert z.testzip() is None;members=[i.filename for i in z.infolist() if not i.is_dir()];assert len(members)==1;data=z.read(members[0]);assert Path(members[0]).name==part['filename']
 assert len(data)==part['bytes'];assert sha(data)==part['sha256'];assert data==(root/'parts'/part['filename']).read_bytes();whole.update(data);total+=len(data);records.append({'part':part['index'],'artifactId':a['id'],'wrapperSHA':sha(wrapper),'wrapperBytes':len(wrapper),'innerSHA':sha(data),'innerBytes':len(data)})
archive=root/manifest['archive'];blob=archive.read_bytes();assert len(blob)==manifest['bytes']==total;assert sha(blob)==manifest['sha256']==whole.hexdigest();assert len(blob)==183597193;assert sha(blob)=='74439d2bdfb851252d8f815c4265338f4b104e0eb61ace06704823010210ffbf'
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None;files=[i for i in z.infolist() if not i.is_dir()];assert len(files)==72
 for i in files:
  assert not i.filename.startswith('/') and '..' not in Path(i.filename).parts
  assert z.read(i.filename)==(root/'native-extracted'/i.filename).read_bytes()
evidence=Path('/workspace/attachments/d860ae0b-e155-4938-90db-4dc3b3ce8770/hollowpact-0.6.0-native-evidence-36789372782-1.zip');a=artifacts[11131875023];blob=evidence.read_bytes();assert len(blob)==a['size_in_bytes']==6834648;assert sha(blob)==a['digest'].split(':')[1]=='ea64967af81c0a50a7c9279c0e4688607f81a5e0ddfbb72222ab722b05fcb3ed'
with zipfile.ZipFile(evidence) as z:
 assert z.testzip() is None
 current=[]
 for i in z.infolist():
  if not i.is_dir() and 'reviews/windows-native/0.6.0/run-36789372782-1/' in i.filename:
   assert z.read(i.filename)==Path(i.filename).read_bytes();assert z.read(i.filename)==(root/'evidence-extracted'/i.filename).read_bytes();current.append(i.filename)
assert len(current)==8
result={'method':'Reviewer personally hashes downloaded API-pinned wrappers/parts/whole ZIP, CRC and every ZIP/package/current-evidence byte; no binary execution','run':api['run'],'wrappersVerified':9,'parts':records,'zipFilesMatched':len(files),'archiveSHA256':manifest['sha256'],'archiveBytes':manifest['bytes'],'currentEvidenceRawFilesByteExact':current,'smallEvidenceSHA256':a['digest'].split(':')[1],'smallEvidenceBytes':a['size_in_bytes'],'retainedOriginalPart8Failure':'downloads-r1.json [object Object]; actual reason unavailable, retry2 succeeds and hashes exact'}
(out/'transfer.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['parts','currentEvidenceRawFilesByteExact']},indent=2))
