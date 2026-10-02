from pathlib import Path
import os,json,hashlib,subprocess,time
S=Path('/workspace/scratch');R=Path('/workspace/Roguelike-deckbuilder');D=R/'reviews/five-retained-png-physical-sharing-2026-10-02';P=S/'five-png-proposal-push-root-r1'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(65536),b''):h.update(b)
 return h.hexdigest()
gate=S/'next-five-png-sharing-independent-r1/GATE.json';g=json.loads(gate.read_text());assert g['decision'].startswith('ACCEPT')
assert sha(S/'share-five-retained-pngs-root-r1.py')==g['method']['sha256']
assert sha(R/'AGENTS.md')==g['currentHold']['sha256']
assert not D.exists() and not P.exists();D.mkdir();P.mkdir();records={}
def copy(a,b):
 assert not a.is_symlink() and not b.exists();b.parent.mkdir(parents=True,exist_ok=True)
 fd=os.open(a,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME)
 with os.fdopen(fd,'rb') as f:v=f.read()
 assert len(v)<262144
 b.write_bytes(v);h=hashlib.sha256(v).hexdigest();assert sha(b)==h
 records[str(b.relative_to(D))]={'originalPath':str(a),'bytes':len(v),'sha256':h}
for folder in ['five-retained-png-recovery-proposal-r1','next-five-png-sharing-independent-r1','two-json-retirement-post-independent-r1','two-json-retirement-post-independent-r2']:
 for p in sorted((S/folder).rglob('*')):
  if p.is_file():copy(p,D/folder/p.relative_to(S/folder))
for name in ['share-five-retained-pngs-root-r1.py','publish-five-png-proposal-root-r1.py','judge-five-png-sharing-root-r1.py']:
 copy(S/name,D/'root-controls'/name)
assert sum(x['bytes'] for x in records.values())<512*1024
(D/'COPY-IDENTITIES.json').write_text(json.dumps(records,indent=2)+'\n')
(D/'README.md').write_text("""# Five retained PNGs: exact physical sharing proposal

This separately reviewed proposal preserves five immutable historical candidate media paths and their exact bodies while replacing private physical encodings with retained canonical anchors. Independent full body and metadata review prefers only this representation; useful source, rights/provenance, historical findings and rollback remain. Original private inode/time/write isolation would be surrendered; shared anchor link counts and ctime would change. Coordinated no-writer holds are not OS protection or global consumer absence. A fresh current push and producer judgment must precede action. No completed transaction or game/art improvement is claimed by this proposal.

The accompanying POST packets verify the earlier two loose JSON copies retired only after their exact bodies and logical identities were preserved in the unchanged published opening-ready-and-rapid-drop capsule. Its measured pre-result gain was6,008,832B; no other deletion follows. Both full and compact POST packets are retained, with the late96KiB cap qualification.
""")
def run(args):
 q=subprocess.run(args,cwd=R,text=True,capture_output=True,timeout=55)
 with (P/'COMMANDS.jsonl').open('a') as f:f.write(json.dumps({'args':args,'rc':q.returncode,'stdout':q.stdout,'stderr':q.stderr,'utcNs':time.time_ns()})+'\n');f.flush();os.fsync(f.fileno())
 assert q.returncode==0,(args,q.stderr)
 return q.stdout.rstrip('\n')
assert run(['git','rev-parse','HEAD'])=='2b21fbc736efa8e734e6b44a538e6f73ad31e86f'
owned=str(D.relative_to(R));allowed={'AGENTS.md','docs/CONTINUATION.md'}
for line in run(['git','status','--porcelain','--untracked-files=all']).splitlines():assert line[3:] in allowed or line[3:].startswith(owned+'/'),line
run(['git','add','-f','--',owned,'AGENTS.md','docs/CONTINUATION.md']);run(['git','-c','gc.auto=0','commit','-m','Preserve accepted held-card comparison and reviewed retained-media sharing proposal'])
head=run(['git','rev-parse','HEAD']);run(['git','-c','gc.auto=0','push','origin','HEAD:codex/lanternbound-production']);remote=run(['git','ls-remote','origin','refs/heads/codex/lanternbound-production']).split()[0]
assert remote==head and not run(['git','status','--porcelain'])
with (P/'PUSH-CONFIRMED.json').open('x') as f:json.dump({'commit':head,'remote':remote,'confirmed':True,'clean':True,'gateSHA256':sha(gate),'methodSHA256':sha(S/'share-five-retained-pngs-root-r1.py'),'holdSHA256':sha(R/'AGENTS.md'),'copiedBytes':sum(v['bytes'] for v in records.values()),'noStorageAction':True,'durableReceiptFileAndParentFsync':True},f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
fd=os.open(P,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
try:os.fsync(fd)
finally:os.close(fd)
print(json.dumps({'commit':head,'confirmed':True,'clean':True,'free':os.statvfs(R).f_bavail*os.statvfs(R).f_frsize}))
