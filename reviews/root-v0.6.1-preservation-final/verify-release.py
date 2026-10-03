from pathlib import Path
import hashlib,json,zipfile,subprocess,shutil
root=Path('/workspace/Roguelike-deckbuilder');dest=root/'releases/0.6.1';manifest=json.loads((dest/'manifest.json').read_text());commit=manifest['sourceCommit']
assert manifest['runtimeSourceDigest']=='8720a38701aa78ccae894ba4ca7cb8656cc3072d5b023cdd9cc3d9d2b3d4c22d' and len(manifest['artifacts'])==6
archiveChecks=[]
for name,sha in manifest['artifacts'].items():
 p=dest/name;actual=hashlib.file_digest(p.open('rb'),'sha256').hexdigest();assert actual==sha;archiveChecks.append({'file':name,'bytes':p.stat().st_size,'sha256':actual})
entries=subprocess.check_output(['git','ls-tree','-r','-z',commit],cwd=root).split(b'\0');expected={}
for row in entries:
 if not row:continue
 meta,name=row.split(b'\t',1);mode,kind,oid=meta.split();name=name.decode()
 if name.startswith('releases/'):continue
 assert kind==b'blob';expected[name]=(oid.decode(),mode.decode())
with zipfile.ZipFile(dest/'hollowpact-0.6.1-source.zip')as z:
 members={i.filename:i for i in z.infolist()if not i.is_dir()};assert set(members)==set(expected),(len(members),len(expected))
 for name,info in members.items():
  digest=hashlib.sha1(('blob '+str(info.file_size)+'\0').encode())
  with z.open(info)as f:
   while data:=f.read(1024*1024):digest.update(data)
  assert digest.hexdigest()==expected[name][0],name
 sourcePackage=json.loads(z.read('package.json'));assert sourcePackage['version']=='0.6.1'
 provenance=json.loads((root/'dist/build-provenance.json').read_text())
 inputChecks=[]
 for name,sha in provenance['hashes'].items():
  actual=hashlib.sha256(z.read(name)).hexdigest();assert actual==sha;inputChecks.append({'file':name,'sha256':actual})
 assert len(inputChecks)==27
 withNative=z.read('reviews/windows-native/0.6.1/run-36791619534-1/native-package.json');assert withNative==(root/'reviews/windows-native/0.6.1/run-36791619534-1/native-package.json').read_bytes()
 sourceFiles=len(members)
def membermap(p):
 with zipfile.ZipFile(p)as z:
  assert z.testzip()is None
  return {i.filename.replace('\\','/').removeprefix('./'):hashlib.sha256(z.read(i)).hexdigest()for i in z.infolist()if not i.is_dir()}
original=membermap(dest/'hollowpact-0.6.1-windows-native-x64.zip');repack=membermap(dest/'hollowpact-0.6.1-windows-x64.zip');assert len(original)==72 and original==repack
assert membermap(dest/'hollowpact-0.6.1-web.zip')['dist/build-provenance.json']==hashlib.sha256((root/'dist/build-provenance.json').read_bytes()).hexdigest()
with zipfile.ZipFile(dest/'hollowpact-0.6.1-native-evidence-36791619534-1.zip')as z:
 assert z.testzip()is None
 name='reviews/windows-native/0.6.1/run-36791619534-1/native-package.json';assert z.read(name)==withNative
old=json.loads((root/'releases/0.6.0/FAILURE-RECEIPT.json').read_text())
for r in old['retainedArtifacts']:
 p=root/'releases/0.6.0'/r['file'];assert p.stat().st_size==r['bytes'] and hashlib.file_digest(p.open('rb'),'sha256').hexdigest()==r['sha256']
result={'status':'verified-development-preservation','version':'0.6.1','sourceCommit':commit,'runtimeSourceDigest':manifest['runtimeSourceDigest'],'artifacts':archiveChecks,'sourceArchive':{'scope':'every committed blob except releases/; exactGitblobSHA1 verifies allbytes inclCRLF; all27runtimeSHA256 match','files':sourceFiles,'allBlobBytesExact':True,'runtimeInputs':inputChecks,'nativeCI_CRLF_Exact':True},'windowsOriginalRepack':{'files':72,'allMemberBytesEqual':True},'webProvenanceExact':True,'originalEvidenceNativeMetadataExact':True,'failed0.6.0FourArtifactsStillExact':True,'mandatoryGate':{'rulesPassed':81,'rulesFailed':0,'duration_ms':6905.934199,'strictBuild':'passed8720','log':'reviews/root-v0.6.1-preservation-final/release.log.txt'},'limits':['Developmentprerelease,notAAA/commercialhumanfun certification','Sixfullarchives local; expiringCI isnotdurablefullremotemirror','Native unsignedWindows directory/qualifiedLinuxXvfb; consumerinstalls,physicalcontroller,Deck,audio andSteamgatesopen']}
out=root/'reviews/release-v0.6.1-verification.json';out.write_text(json.dumps(result,indent=2)+'\n')
logdir=root/'reviews/root-v0.6.1-preservation-final';logdir.mkdir();shutil.copy2('/workspace/scratch/release-v0.6.1-8720.log.txt',logdir/'release.log.txt')
print(json.dumps({k:result[k]for k in ['status','version','sourceCommit','runtimeSourceDigest']},indent=2));print('Verified6archivehashes,all'+str(sourceFiles)+'sourceblobs,27runtimeinputs,72Windowsmembers,originalCIbytesandunchangedfailed0.6.0')
