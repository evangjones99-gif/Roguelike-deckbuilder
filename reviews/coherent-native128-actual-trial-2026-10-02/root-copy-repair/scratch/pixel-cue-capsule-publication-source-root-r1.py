from pathlib import Path
import hashlib,json,shutil,os,time
S=Path('/workspace/scratch'); R=Path('/workspace/Roguelike-deckbuilder'); D=R/'reviews/coherent-native128-actual-trial-2026-10-02'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(32768),b''):h.update(b)
 return h.hexdigest()
G=S/'pixel-cue-evidence-preservation-independent-r1/GATE.json'
assert sha(G)=='11707477d92cc0a041f3dbbfd77d5ba6ef185a4d5df3bb181f2285d827dfeb05'
A=S/'pixel-cue-evidence-capsule-root-r1'; J=json.loads((A/'RESULT.json').read_text())
archive=Path(J['archive']); assert sha(archive)==J['sha256']=='ce0f8f40bcf0f0b22e5e4d93eef3d4660662826e617900aba09ac208c148dc13'
assert sha(A/'INDEX.json')==J['indexSHA256'] and sha(A/'READ-OBSERVATIONS.json')==J['readObservationsSHA256']
assert J['logicalBodyCount']==831 and J['uniqueBodyCount']==697 and J['preservedDependencies']==312 and J['fullUniqueBodyRoundtrip']
assert not D.exists() and not D.is_symlink()
assert os.statvfs(R).f_bavail*os.statvfs(R).f_frsize>=74*1048576
for p in [R,R/'reviews']:
 assert p.is_dir() and not p.is_symlink()
D.mkdir(mode=0o700); rows=[]
def copy(p,d):
 assert p.is_file() and not p.is_symlink() and not d.exists()
 h=sha(p); d.parent.mkdir(parents=True,exist_ok=True)
 with p.open('rb') as f,d.open('xb') as w:shutil.copyfileobj(f,w,32768)
 assert sha(d)==h
 rows.append({'originalPath':str(p),'destination':str(d.relative_to(R)),'sha256':h,'bytes':d.stat().st_size})
for p in sorted(A.iterdir()):copy(p,D/p.name)
for origin,name in [('pixel-cue-evidence-preserver-source-independent-r3','source-method-independent'),('pixel-cue-evidence-preservation-independent-r1','preservation-independent'),('pixel-cue-capsule-archive-guard-root-r1','root-archive-guard'),('pixel-cue-capsule-activation-template-guard-root-r1','root-activation-template-guard')]:
 root=S/origin
 for p in sorted(root.rglob('*')):
  if p.is_file():copy(p,D/name/p.relative_to(root))
copy(S/'pixel-cue-capsule-activation-root-r1.json',D/'ROOT-ACTIVATION.json')
copy(Path(__file__),D/'ROOT-PUBLICATION-SOURCE.py')
(D/'PUBLICATION.json').open('x').write(json.dumps({'utcNs':time.time_ns(),'canonicalDestination':str(D),'archiveSHA256':J['sha256'],'preservationGateSHA256':sha(G),'records':rows,'scope':'Lossless preservation of rejected R5 pixel actual R6 and old opt-in cue source/build. Latest UI actual/default-cue/corpse evidence is outside scope. Original inputs retained; no cleanup or selection. Existing selected runtime unchanged. No self-contained release or human enjoyment claim.','sourceBootstrapUnmetered':True},indent=2)+'
')
print(json.dumps({'destination':str(D),'copiedBodies':len(rows),'copiedBytes':sum(x['bytes'] for x in rows),'archiveSHA256':J['sha256'],'publicationSHA256':sha(D/'PUBLICATION.json')}))
