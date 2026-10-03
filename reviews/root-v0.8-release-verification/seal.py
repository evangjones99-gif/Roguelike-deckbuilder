"""Add only the exact accepted native originals to a completed bundle milestone."""
from pathlib import Path, PurePosixPath
import hashlib,json,subprocess,shutil,tarfile,zipfile,os
ROOT=Path('/workspace/Roguelike-deckbuilder');DEST=ROOT/'releases/0.8.0';EVIDENCE=Path(__file__).parent
RUNTIME='23477f68c99d6d60b0b3f82b286a8d33bb6da6f2ca92c103fbecf5663634959f'
ASAR='c383c4437ac5467146174c6ea039b2a8b28af43d609701379e8cf695f59d530c'
def sha_stream(f):
 h=hashlib.sha256()
 while b:=f.read(1048576):h.update(b)
 return h.hexdigest()
def sha(p):
 with p.open('rb') as f:return sha_stream(f)
def safe(name):
 p=PurePosixPath(name);assert not p.is_absolute() and '..' not in p.parts and '\\' not in name
 return name.removeprefix('./')
def parent_paths(files):
 return {str(parent) for name in files for parent in PurePosixPath(name).parents}
source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
assert not (ROOT/'.release-lock').exists() and not (DEST/'INCOMPLETE.txt').exists()
assert not subprocess.check_output(['git','status','--porcelain','--untracked-files=all','--','.',':(exclude)releases/0.8.0'],cwd=ROOT,text=True).strip()
producer=json.loads((DEST/'manifest.json').read_text())
assert producer['sourceCommit']==source and producer['runtimeSourceDigest']==RUNTIME
assert producer['sourceArchiveFormat']=='git-bundle-v2' and producer['platforms']==['web','linux-x64']
sentinel=DEST/'NATIVE-SEAL-IN-PROGRESS.json'
with sentinel.open('x') as f:json.dump({'sourceCommit':source,'scope':'Native additions are unsealed until root complete checks and independent acceptance. Preserve this marker on failure.'},f);f.flush();os.fsync(f.fileno())
for name in ('manifest.json','SHA256SUMS'):
 with (EVIDENCE/('producer-initial-'+name)).open('xb') as f:f.write((DEST/name).read_bytes())
linux_identity=json.loads((ROOT/'reviews/root-v0.8-hunter-width-integration/LINUX-PACKAGE-IDENTITY-r2.json').read_text())
linux_expected={r['path']:r for r in linux_identity['packrecords']};assert len(linux_expected)==74 and linux_identity['asarSHA256']==ASAR
linux={};linux_dirs=set();expected_linux_dirs=parent_paths(linux_expected)
with tarfile.open(DEST/'hollowpact-0.8.0-linux-x64.tar.gz','r:gz') as tar:
 for m in tar:
  name=safe(m.name).rstrip('/')
  if m.isdir():assert name in expected_linux_dirs and name not in linux_dirs;linux_dirs.add(name);continue
  assert m.isfile();assert name not in linux
  actual=sha_stream(tar.extractfile(m));expected=linux_expected[name]
  assert actual==expected['sha256'] and m.size==expected['bytes'] and m.mode==expected['mode']
  linux[name]={'sha256':actual,'bytes':m.size,'mode':m.mode}
assert set(linux)==set(linux_expected) and linux_dirs==expected_linux_dirs
small=Path('/workspace/scratch/windows-native-independent-v08-run-36806506465/original-native-evidence.zip')
original=Path('/workspace/retained-native-experiments/windows-run-36806506465/hollowpact-0.8.0-windows-native-x64.zip')
native=DEST/original.name;ci=DEST/'hollowpact-0.8.0-native-evidence-36806506465-1.zip'
for before,after,expected in ((original,native,'1ce6c74baea02686183e833c28738e04d19f80d5826218a0d732eff304dce563'),(small,ci,'c76748bac54fad37f88b4f53e957456b726210158ce5939540b2367c737941e6')):
 assert sha(before)==expected
 with before.open('rb') as inp,after.open('xb') as out:shutil.copyfileobj(inp,out,1048576);out.flush();os.fsync(out.fileno())
 assert sha(after)==expected
smoke=json.loads(Path('/workspace/scratch/windows-native-independent-v08-run-36806506465/raw-small-members/reviews/windows-native/0.8.0/run-36806506465-1/smoke.json').read_text())
assert smoke['runtimeSourceDigest']==RUNTIME and smoke['asarSHA256']==ASAR and smoke['status']=='passed'
windows={}
with zipfile.ZipFile(native) as z:
 assert z.testzip() is None
 for m in z.infolist():
  name=safe(m.filename);assert name==m.filename and name not in windows
  assert not m.is_dir() and (m.external_attr>>16)&0o170000!=0o120000
  with z.open(m) as f:actual=sha_stream(f)
  assert actual==smoke['packageFiles'][name]
  windows[name]={'sha256':actual,'bytes':m.file_size}
assert set(windows)==set(smoke['packageFiles']) and len(windows)==72
provenance=json.loads((ROOT/'dist/build-provenance.json').read_text());assert provenance['sourceDigest']==RUNTIME and len(provenance['hashes'])==76
for name,expected in provenance['hashes'].items():assert sha(ROOT/name)==expected
web={};web_dirs=set();expected_web_dirs={'dist'}|{'dist/'+str(p.relative_to(ROOT/'dist')) for p in (ROOT/'dist').rglob('*') if p.is_dir()}
with zipfile.ZipFile(DEST/'hollowpact-0.8.0-web.zip') as z:
 assert z.testzip() is None
 for m in z.infolist():
  name=safe(m.filename)
  assert (m.external_attr>>16)&0o170000!=0o120000
  if m.is_dir():directory=name.rstrip('/');assert directory in expected_web_dirs and directory not in web_dirs;web_dirs.add(directory);continue
  assert name.startswith('dist/') and name not in web
  rel=name[5:]
  assert rel not in web
  with z.open(m) as f:actual=sha_stream(f)
  assert actual==sha(ROOT/'dist'/rel)==sha(DEST/'web'/rel)
  web[rel]={'sha256':actual,'bytes':m.file_size}
assert len(web)==55 and set(web)=={str(p.relative_to(ROOT/'dist')) for p in (ROOT/'dist').rglob('*') if p.is_file()} and web_dirs==expected_web_dirs
index=json.loads((DEST/'reviews/INDEX.json').read_text());assert index['sourceCommit']==source
proof=json.loads((DEST/'source-bundle-verification.json').read_text());assert proof['sourceCommit']==source and proof['selfContained'] and proof['format']=='git-bundle-v2'
artifacts={p.name:sha(p) for p in sorted(DEST.iterdir()) if p.name.endswith(('.zip','.tar.gz','.bundle'))};assert len(artifacts)==5
for name,expected in producer['artifacts'].items():assert artifacts[name]==expected
old=[]
for p in sorted((ROOT/'releases').glob('*/manifest.json')):
 if p.parent==DEST or (p.parent/'INCOMPLETE.txt').exists():continue
 prior=json.loads(p.read_text())
 for name,expected in prior['artifacts'].items():
  archive=p.parent/name;assert sha(archive)==expected
  old.append({'path':str(archive.relative_to(ROOT)),'bytes':archive.stat().st_size,'sha256':expected})
assert len(old)==35
producer.update({'platforms':['web','linux-x64','windows-x64'],'artifacts':artifacts,
 'nativeWindows':{'runId':36806506465,'jobId':110191925032,'attempt':1,'headSourceCheckpoint':'2e93c2dab38c513a6f43e1dc4e31307f0866db14','actualPRMergeCheckout':'7c460a706d6e5bfd8c98d5886b3d1d5cab679cef','originalArchiveSHA256':artifacts[native.name],'originalEvidenceSHA256':artifacts[ci.name],'files':72,'matchingLinuxWindowsASAR_SHA256':ASAR,'review':'reviews/native-windows-v0.8-23477-binary-independent/REVIEW.md','qualification':'Actual thirteen-phase sandbox-enabled hosted Windows2022 portable QA; independent original ZIP/ASAR/PE audit. Muted/reduced idle hunter trial, no native crypt/audio/hearing, consumer installer/update, physical controller/Deck or Steam qualification.'},
 'nativeLinux':{'files':74,'executableSHA256':linux['hollowpact']['sha256'],'asarSHA256':ASAR,'review':'reviews/combined-v0.8-hunter-width-technical-independent/REVIEW-r2.md','qualification':'Actual four affected packaged checks on Linux/Xorg dummy/software rendering/--no-sandbox, plus retained separately scoped predecessor audio gates. No normal secure consumer install or declared hardware benchmark.'},
 'acceptance':{'gameplay':'reviews/combined-v0.8-hunter-width-gameplay-independent/REVIEW.md','visual':'reviews/combined-v0.8-hunter-width-visual-independent/REVIEW.md','technical':'reviews/combined-v0.8-hunter-width-technical-independent/REVIEW-r2.md','scope':'Scoped reviewed DEVELOPMENT preservation. AAA craft is not accepted; sparse standees/animation, anatomy/encounter variety, layout and human enjoyment remain open.'},
 'archiveLayout':'Five archives: exact source Git bundle v2, web ZIP, Linux TAR, exact original actual-tested Windows ZIP and original native evidence ZIP. Producer metadata retained separately; no Windows repack.',
 'remoteStorage':'Complete five-archive milestone local only; Actions expires30days. Historical installer drafts are separate partial research mirrors, not this game/source archive set.',
 'archiveVerification':'reviews/root-v0.8-release-verification/root-verification.json; separate final archival acceptance required before tag.'})
(DEST/'manifest.json').write_text(json.dumps(producer,indent=2)+'\n')
(DEST/'SHA256SUMS').write_text(''.join(h+'  '+n+'\n' for n,h in artifacts.items()))
receipt={'status':'PASS-root-byte-check','sourceCommit':source,'runtimeSourceDigest':RUNTIME,'inputs':76,'artifacts':{n:{'sha256':h,'bytes':(DEST/n).stat().st_size} for n,h in artifacts.items()},'linuxFiles':linux,'windowsFiles':windows,'webFiles':web,'oldSealedArchives':old,'reviewIndexFiles':len(index['files']),'reviewIndexRawGzipPairs':len(index['rawGzipPairs']),'qualification':'Root full byte/mode checks; actual producer repeats rules/strict build. Independent final source bundle/INDEX/archive audit required. No new native execution or AAA/human-fun claim.'}
with (EVIDENCE/'root-verification.json').open('x') as f:json.dump(receipt,f,indent=2);f.write('\n')
sentinel.unlink()
print(json.dumps({k:v for k,v in receipt.items() if k in ('status','sourceCommit','artifacts')}))
