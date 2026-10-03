import hashlib, json, shutil, zipfile, tarfile, subprocess, os
from pathlib import Path

root=Path('/workspace/Roguelike-deckbuilder')
dest=root/'releases/0.7.0'
temp=Path('/tmp/hollowpact-native-v07')
source='fdb43bd2e2833e2460ffc3776071b9ed82ad79cc'
runtime='0be4f01d416e6fc4cca3f19b6916b5b65993b9fd426a926a1ede6d8487834a35'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()==source
assert not (dest/'INCOMPLETE.txt').exists()
assert not (root/'.release-lock').exists()
producer=json.loads((dest/'manifest.json').read_text())
assert producer['sourceCommit']==source and producer['runtimeSourceDigest']==runtime
assert producer['platforms']==['web','linux-x64']
evidence=root/'reviews/root-v0.7-release-verification'
evidence.mkdir()
for name in ['manifest.json','SHA256SUMS']:
    shutil.copyfile(dest/name,evidence/('producer-initial-'+name))
for name in ['final-capacity-preflight.json','final-capacity-preflight-r2.json','release-v07-production.log']:
    shutil.copyfile(temp/name,evidence/(name+'.txt' if name.endswith('.log') else name))
shutil.copyfile(Path(__file__),evidence/'seal-native-milestone.py')

def digest_stream(stream):
    h=hashlib.sha256()
    for block in iter(lambda:stream.read(1024*1024),b''):h.update(block)
    return h.hexdigest()
def digest(path):
    with path.open('rb') as stream:return digest_stream(stream)

orig_native=temp/'windows-native/hollowpact-0.7.0-windows-native-x64.zip'
orig_evidence=Path('/workspace/attachments/e2da5cd2-439d-436f-92e3-eba835cc9807/hollowpact-0.7.0-current-native-evidence-36797759232-1.zip')
native=dest/orig_native.name
ci_evidence=dest/'hollowpact-0.7.0-native-evidence-36797759232-1.zip'
for original,retained,expected in [
 (orig_native,native,'256babeb74761b0608ae8be249f30f475522c70f86c0fd377f1bef737fb35fbe'),
 (orig_evidence,ci_evidence,'ef69c5e33c0e9b229b85883000d14a3f15a2bfcfb7ba75f18e9c0076f547e14e')]:
    assert digest(original)==expected
    with retained.open('xb') as target,original.open('rb') as inp:shutil.copyfileobj(inp,target,1024*1024)
    assert digest(retained)==expected

linux_identity=json.loads(Path('/workspace/scratch/hunter-linux-packaged-independent-v07/package-identity.json').read_text())
linux_checked={}
with tarfile.open(dest/'hollowpact-0.7.0-linux-x64.tar.gz','r:gz') as tar:
    for member in tar:
        if member.isdir():continue
        assert member.isfile(),member.name
        name=member.name.removeprefix('./')
        assert name not in linux_checked
        sha=digest_stream(tar.extractfile(member))
        assert sha==linux_identity['packagedFiles'][name],name
        original=temp/'build-desktop/linux-unpacked'/name
        assert member.mode==(original.stat().st_mode&0o7777),name
        linux_checked[name]={'sha256':sha,'bytes':member.size,'mode':member.mode}
assert set(linux_checked)==set(linux_identity['packagedFiles']) and len(linux_checked)==74

windows_identity=json.loads(Path('/workspace/scratch/hunter-native-package-independent-v07/transfer-and-files.json').read_text())
expected_windows={entry['path']:entry for entry in windows_identity['files']}
windows_checked={}
with zipfile.ZipFile(native) as archive:
    for member in archive.infolist():
        if member.is_dir():continue
        assert member.filename not in windows_checked
        with archive.open(member) as stream:sha=digest_stream(stream)
        assert sha==expected_windows[member.filename]['sha256'],member.filename
        assert member.file_size==expected_windows[member.filename]['bytes']
        windows_checked[member.filename]={'sha256':sha,'bytes':member.file_size}
assert set(windows_checked)==set(expected_windows) and len(windows_checked)==72

prov=json.loads((root/'dist/build-provenance.json').read_text())
assert prov['sourceDigest']==runtime and len(prov['hashes'])==29
for name,sha in prov['hashes'].items():assert digest(root/name)==sha,name
web_checked={}
with zipfile.ZipFile(dest/'hollowpact-0.7.0-web.zip') as archive:
    for member in archive.infolist():
        if member.is_dir():continue
        assert member.filename.startswith('dist/')
        with archive.open(member) as stream:sha=digest_stream(stream)
        relative=member.filename[5:]
        assert sha==digest(root/'dist'/relative)==digest(dest/'web'/relative),relative
        web_checked[relative]={'sha256':sha,'bytes':member.file_size}
assert len(web_checked)==15
assert digest(dest/'hollowpact-0.7.0-source.zip')==json.loads((temp/'final-capacity-preflight-r2.json').read_text())['sourceZIP_SHA256']
index=json.loads((dest/'reviews/INDEX.json').read_text())
assert index['sourceCommit']==source
artifacts={f.name:digest(f) for f in sorted(dest.iterdir()) if f.name.endswith(('.zip','.tar.gz'))}
assert len(artifacts)==5
for name,sha in producer['artifacts'].items():assert artifacts[name]==sha
producer.update({'platforms':['web','linux-x64','windows-x64'],'artifacts':artifacts,
 'nativeWindows':{'runId':36797759232,'jobId':110165002124,'attempt':1,
 'headSourceCheckpoint':'bdf27374358eb176e62f832cb50261cb3334d8df',
 'actualPRMergeCheckout':'debf73893c4e1d9acc163784a425bb0c12492ec4',
 'originalArchiveSHA256':artifacts[native.name],'originalEvidenceSHA256':artifacts[ci_evidence.name],
 'files':72,'matchingLinuxWindowsASAR_SHA256':'e270b1fc9626f6df915449200d00f86cd593e3ca70876832436dd90ef7e6d3da',
 'review':'reviews/hunter-v0.7-native-package/REVIEW.md',
 'qualification':'Unsigned portable directory on one Windows2022 CI host;13 automated phases and8 idle hunter draws. No consumer installer, physical controller, native all-pose coverage, human enjoyment, listening, Steam Deck or Steam certification.'},
 'nativeLinux':{'files':74,'executableSHA256':linux_identity['executableSHA256'],'asarSHA256':linux_identity['asarSHA256'],
 'review':'reviews/hunter-v0.7-linux-packaged-r2/REVIEW.md',
 'qualification':'Actual portable executable on Linux/Xorg dummy display97/software rendering/--no-sandbox,42 hunter draws and earned seed121 binding/command/relaunch/local export. No clean consumer install or hardware benchmark.'},
 'acceptance':{'gameplay':'reviews/hunter-v0.7-production-gameplay/REVIEW.md plus separate count correction and URI supplement',
 'visual':'reviews/hunter-v0.7-production-visual/REVIEW.md and hunter-v0.7-uri-visual/REVIEW.md',
 'technical':'reviews/hunter-v0.7-production-technical/REVIEW.md and hunter-v0.7-uri-technical/REVIEW.md',
 'scope':'Scoped reviewed DEVELOPMENT preservation. Sparse hard-cut poses, mirrored equipment, seated incapacitation, environment/species variety and human fun remain open. No AAA/commercial/Steam approval.'},
 'archiveLayout':'Five archives: sourceZIP, webZIP, LinuxTAR, exact original actual-tested WindowsZIP and exact original native evidenceZIP. The source/web/Linux producer initial metadata is retained separately; no redundant repacked Windows archive.',
 'remoteStorage':'Complete five-archive set local only. Native CI artifacts expire30days; no full remote mirror/public release claimed.',
 'retainedFailedAttempt':'All releases/0.6.0 incomplete artifacts and prior0.1–0.6.1 milestones remain unchanged; no v0.6.0 tag.',
 'archiveVerification':'reviews/root-v0.7-release-verification/root-verification.json; independent final archival acceptance required before tag.'})
(dest/'manifest.json').write_text(json.dumps(producer,indent=2)+'\n')
(dest/'SHA256SUMS').write_text(''.join(sha+'  '+name+'\n' for name,sha in artifacts.items()))
record={'status':'PASS-root-byte-check','sourceCommit':source,'runtimeSourceDigest':runtime,'inputs':29,
 'artifacts':{name:{'sha256':sha,'bytes':(dest/name).stat().st_size} for name,sha in artifacts.items()},
 'linuxFiles':linux_checked,'windowsFiles':windows_checked,'webFiles':web_checked,
 'reviewIndexFiles':len(index['files']),'reviewIndexRawGzipPairs':len(index['rawGzipPairs']),
 'producerRules':'87 passed0failed; actual transaction repeats strict build and exact runtime digest',
 'qualification':'Root streamed all74Linux/72Windows/15web files against independent frozen inventories and modes; final Git source byte/index audit belongs separate independent verifier. No new native execution or human quality endorsement.'}
(evidence/'root-verification.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({'status':record['status'],'artifacts':record['artifacts'],'reviewIndexFiles':record['reviewIndexFiles']}))
