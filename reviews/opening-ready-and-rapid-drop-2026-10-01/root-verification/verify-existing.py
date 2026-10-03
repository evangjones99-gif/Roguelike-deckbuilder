import pathlib, hashlib, json, tarfile, os, resource
repo=pathlib.Path('/workspace/Roguelike-deckbuilder')
out=repo/'reviews/opening-ready-and-rapid-drop-2026-10-01'
archive=out/'evidence.tar.gz'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(65536):h.update(b)
 return h.hexdigest()
manifest=None;verified={}
with tarfile.open(archive,'r|gz') as tar:
 for member in tar:
  with tar.extractfile(member) as body:
   if member.name=='MANIFEST.json':
    raw=body.read();manifest=json.loads(raw);manifest_sha=hashlib.sha256(raw).hexdigest()
   else:
    h=hashlib.sha256();size=0
    while b:=body.read(65536):h.update(b);size+=len(b)
    assert h.hexdigest()==member.name.removeprefix('blobs/')
    verified[h.hexdigest()]=size
assert manifest and len({x['path'] for x in manifest['entries']})==len(manifest['entries'])
assert set(verified)=={x['sha256'] for x in manifest['entries']}
for x in manifest['entries']:
 assert verified[x['sha256']]==x['bytes']
 assert sha(pathlib.Path(x['originalPath']))==x['sha256'],x['originalPath']
for x in manifest['excludedRetainedBodies']:assert sha(pathlib.Path(x['originalPath']))==x['sha256']
summary={k:manifest[k] for k in ['kind','sourceDigest','outputsDigest','inputCount','outputCount','captureScope','limitations']}
summary.update({'archiveSHA256':sha(archive),'archiveBytes':archive.stat().st_size,'manifestSHA256':manifest_sha,'logicalBodies':len(manifest['entries']),'uniqueBlobs':len(verified),'retainedExcludedBodies':len(manifest['excludedRetainedBodies']),'roundtripAllUniqueBodies':True,'originalBodiesRechecked':True,'ownMaximumRSSBytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,'freeBytesAfter':os.statvfs(out).f_bavail*os.statvfs(out).f_frsize,'declaredBudgetDeviation':{'plannedCompressedCapBytes':2621440,'actualCompressedBytes':archive.stat().st_size,'originalGuardExit':1,'originalFailure':'Soft capsule size-cap assertion after complete archive write. Preserve exact artifact; verify without rewriting/re-encoding. No runtime retry.'}})
(out/'SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n')
(out/'README.md').write_text('''# Opening READY and rapid-card evidence

Only the independently accepted default READY guidance is selected. The private settleDrag trial showed no benefit and remains withheld. The actual first300 ended in turn1 without an enemy response or encounter clear. All18 full saved checkpoint pairs in the shorter drag diagnostic match (the caller asserts a15-pair normalized subset).

The unchanged evidence.tar.gz contains a logical-path MANIFEST.json and SHA256 content-addressed blobs. SUMMARY.json pins every byte. It preserves raw saves/traces, source/build identities, callers, independent findings and their read-method failures, resource/closure receipts, R8 rollback code, native-art negative recipes, primary research and the reviewed52-path physical-sharing receipts. All six default first300 photographs and both held-release photographs are included. Other original photographs/media remain at their pinned original paths and are explicitly excluded; this is bounded evidence, not full archival coverage or a self-contained game release.

The first archive command failed its2.5MiB compressed-size assertion after writing a complete3303630B artifact. That exact artifact and failed guard remain retained. A separate finite verification checks every661 blob,737 logical entry and excluded retained body without rewriting the archive. The storage-budget deviation is explicit, not a test pass or a reason to remove anything. New repository publication still requires independent capsule review and confirmed push.

This is a development checkpoint, not a new version or release. No human enjoyment, fully pixel scene, guaranteed drag repair or native Steam qualification follows. No old artifact or media body was deleted.
''')
failure=pathlib.Path('/workspace/scratch/ready-and-drag-evidence-capsule-root-r1/guard-r1/RESULT.json')
(out/'ARCHIVE-CAP-FAILURE.json').write_text(failure.read_text())
print(json.dumps(summary))
