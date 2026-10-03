from pathlib import Path
import hashlib,json,os,shutil,time
S=Path('/workspace/scratch');R=Path('/workspace/Roguelike-deckbuilder')
D=R/'reviews/opening-cue-and-grounded-trial-2026-10-02'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(65536):h.update(b)
 return h.hexdigest()
G=S/'wording-grounded-trials-checkpoint-complete-independent-r1/GATE.json'
assert sha(G)=='df8ef40e5409409f004d2a2c08d7ca20dfb519f31590c379459c29d2f6983a85'
A=S/'wording-grounded-trials-checkpoint-output-root-r1'
assert sha(A/'evidence-451347c174a3fe78e5f7b6ef22736b7cfbbd33b39fd04ea20556730bb3b15a8b.tar.gz')=='451347c174a3fe78e5f7b6ef22736b7cfbbd33b39fd04ea20556730bb3b15a8b'
P=S/'wording-development-source-selection-actual-root-r1/RESULT.json'
assert sha(P)==os.environ['HOLLOWPACT_SOURCE_SELECTION_RESULT_SHA256']
j=json.loads(P.read_text());assert j['decision']=='SELECTED_DEVELOPMENT_SOURCE_ONLY_DIST_RETAINED_OLD'
assert j['sourceDigest']=='64c2a14ada2b24796535f9bb71d8a6acc534685365bcf4f5665b21bf18595353'
assert not D.exists() and not D.is_symlink()
assert os.statvfs(R).f_bavail*os.statvfs(R).f_frsize>=71*1048576
assert all(p.is_dir() and not p.is_symlink() for p in [R,R/'reviews'])
D.mkdir(mode=0o700);rows=[]
def copy(p,d):
 assert p.is_file() and not p.is_symlink() and not d.exists()
 h=sha(p);d.parent.mkdir(parents=True,exist_ok=True)
 with p.open('rb') as f,d.open('xb') as w:
  shutil.copyfileobj(f,w,32768);w.flush();os.fsync(w.fileno())
 assert sha(d)==h
 rows.append({'originalPath':str(p),'destination':str(d.relative_to(R)),'sha256':h,'bytes':d.stat().st_size})
for origin,name in [
 ('wording-grounded-trials-checkpoint-output-root-r1','archive'),
 ('wording-grounded-trials-checkpoint-source-author-r1','archive-source-author'),
 ('wording-grounded-trials-checkpoint-source-independent-r1','archive-source-failed-r1'),
 ('wording-grounded-trials-checkpoint-source-independent-r2','archive-source-independent'),
 ('wording-grounded-trials-checkpoint-complete-independent-r1','archive-complete-independent'),
 ('wording-grounded-trials-checkpoint-archive-guard-root-r1','root-archive-guard'),
 ('wording-development-source-selection-author-r1','selection-source-author'),
 ('wording-development-source-selection-independent-r1','selection-source-independent'),
 ('wording-development-source-selection-actual-root-r1','selection-actual'),
 ('wording-development-source-selection-guard-root-r1','root-selection-guard')]:
 root=S/origin;assert root.is_dir() and not root.is_symlink()
 for p in sorted(root.rglob('*')):
  if p.is_file():copy(p,D/name/p.relative_to(root))
for origin,name in [
 ('wording-grounded-trials-checkpoint-archive-grant-root-r1.json','ROOT-ARCHIVE-GRANT.json'),
 ('wording-grounded-checkpoint-grant-root-r1.py','ROOT-ARCHIVE-LAUNCHER.py'),
 ('wording-development-source-selection-grant-root-r1.json','ROOT-SELECTION-GRANT.json'),
 ('wording-development-source-selection-grant-root-r1.py','ROOT-SELECTION-LAUNCHER.py'),
 ('opening-cue-checkpoint-push-receipt-root-r1.json','previous-push-receipt.json'),
 ('starter-family-master-provenance-root-r1.json','supplemental-starter-master-provenance.json')]:copy(S/origin,D/name)
copy(Path(__file__),D/'ROOT-PUBLICATION-SOURCE.py')
scope='Exact preservation of two distinct actual trials: clearer spent-command cue and rejected grounded native-pixel scene. Archive contains952 logical identities/711 new stored bodies plus230 retained-capsule references,16 original screenshots and12 complete saved-state pairs. Three independent wording reviews accept narrow clarity/behavior; pixel visual/gameplay reject corpse payoff and courtyard depth. Development source selection64c2 is separate from held dist8b and reviewed candidate build82e. All prior negative findings and relevant failures remain verbatim; external media/dependencies and inherited old capsule COMPLETE proofs remain explicit. Supplemental generated-master metadata is a tool-history derivative, not literal prompt bytes. New corpse repair/build, corrected crop diagnostics, first300/human enjoyment, default pixel selection, release/tag and cleanup are outside this archive scope.'
with (D/'PUBLICATION.json').open('x') as f:
 json.dump({'utcNs':time.time_ns(),'completePreservationGateSHA256':sha(G),'sourceSelectionResultSHA256':sha(P),'records':rows,'scope':scope,'rootPublicationBootstrapUnmetered':True},f,indent=2);f.write(chr(10));f.flush();os.fsync(f.fileno())
with (D/'README.md').open('x') as f:f.write(scope+chr(10))
assert sum(p.stat().st_size for p in D.rglob('*') if p.is_file())<=16*1048576
print(json.dumps({'destination':str(D),'copiedBodies':len(rows),'copiedBytes':sum(x['bytes'] for x in rows),'publicationSHA256':sha(D/'PUBLICATION.json')}))
