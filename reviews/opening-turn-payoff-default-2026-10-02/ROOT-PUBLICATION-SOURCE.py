from pathlib import Path
import hashlib,json,os,shutil,time
S=Path('/workspace/scratch'); R=Path('/workspace/Roguelike-deckbuilder'); D=R/'reviews/opening-turn-payoff-default-2026-10-02'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(32768),b''):h.update(b)
 return h.hexdigest()
G=S/'opening-turn-payoff-opening-checkpoint-preservation-independent-r1/GATE.json'
assert sha(G)=='940a3ec99f960aea7cbd5c9b942da6f595e0a4d45463ac963979eac03cfd425d'
A=S/'opening-turn-payoff-opening-checkpoint-output-root-r1'
assert sha(A/'evidence-f9121c7b6416398241d1b5a160b4781f17a45dff4813260edaf4c3b6df1761af.tar.gz')=='f9121c7b6416398241d1b5a160b4781f17a45dff4813260edaf4c3b6df1761af'
assert not D.exists() and not D.is_symlink()
assert os.statvfs(R).f_bavail*os.statvfs(R).f_frsize>=71*1048576
assert all(p.is_dir() and not p.is_symlink() for p in [R,R/'reviews'])
D.mkdir(mode=0o700); rows=[]
def copy(p,d):
 assert p.is_file() and not p.is_symlink() and not d.exists()
 h=sha(p); d.parent.mkdir(parents=True,exist_ok=True)
 with p.open('rb') as f,d.open('xb') as w:
  shutil.copyfileobj(f,w,32768);w.flush();os.fsync(w.fileno())
 assert sha(d)==h
 rows.append({'originalPath':str(p),'destination':str(d.relative_to(R)),'sha256':h,'bytes':d.stat().st_size})
for origin,name in [('opening-turn-payoff-opening-checkpoint-output-root-r1','archive'),('opening-turn-payoff-opening-checkpoint-source-author-r1','source-author'),('opening-turn-payoff-opening-checkpoint-source-independent-r1','source-independent'),('opening-turn-payoff-opening-checkpoint-preservation-independent-r1','preservation-independent'),('opening-turn-payoff-opening-checkpoint-archive-guard-root-r1','root-archive-guard')]:
 root=S/origin
 for p in sorted(root.rglob('*')):
  if p.is_file():copy(p,D/name/p.relative_to(root))
copy(S/'opening-turn-payoff-opening-checkpoint-archive-grant-root-r1.json',D/'ROOT-GRANT.json')
copy(S/'pixel-cue-evidence-push-source-root-r1.py',D/'previous-push/source.py')
copy(S/'pixel-cue-evidence-push-receipt-root-r1.json',D/'previous-push/receipt.json')
copy(Path(__file__),D/'ROOT-PUBLICATION-SOURCE.py')
scope='Preservation of earlier opt-in and default spent-command cue comparisons: 490 logical identities,298 new stored bodies,187 retained-capsule references,16 original screenshots,12 saved-state pairs and seven review trees. Earlier three actual reviews narrowly accepted information behavior with wording debt; runtime promotion deferred to actual review of clearer wording. New wording build, grounded pixel build and their future comparisons are outside archive scope. Existing selected runtime unchanged. No cleanup, tag, self-contained release, first300 or human enjoyment claim. Metadata and inherited old697-body review qualifications remain.'
with (D/'PUBLICATION.json').open('x') as f:
 json.dump({'utcNs':time.time_ns(),'preservationGateSHA256':sha(G),'records':rows,'scope':scope,'sourceBootstrapUnmetered':True},f,indent=2);f.write(chr(10));f.flush();os.fsync(f.fileno())
with (D/'README.md').open('x') as f:f.write(scope+chr(10))
assert sum(p.stat().st_size for p in D.rglob('*') if p.is_file())<=8*1048576
print(json.dumps({'destination':str(D),'copiedBodies':len(rows),'copiedBytes':sum(x['bytes'] for x in rows),'publicationSHA256':sha(D/'PUBLICATION.json')}))
