from pathlib import Path
import os,json,hashlib,subprocess,time
S=Path('/workspace/scratch');R=Path('/workspace/Roguelike-deckbuilder');D=R/'reviews/five-png-recovery-admission-2026-10-02';P=S/'five-png-recovery-push-root-r1'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(65536),b''):h.update(b)
 return h.hexdigest()
gate=S/'five-png-recovery-admission-independent-r1/GATE.json';g=json.loads(gate.read_text());assert g['decision'].startswith('ACCEPT')
assert sha(S/'share-five-retained-pngs-root-r2.py')==g['method']['sha256']
assert sha(R/'AGENTS.md')==g['currentHold']['sha256']
assert not D.exists() and not P.exists();D.mkdir();P.mkdir();records={}
def copy(a,b):
 assert not a.is_symlink() and not b.exists();b.parent.mkdir(parents=True,exist_ok=True)
 fd=os.open(a,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME)
 with os.fdopen(fd,'rb') as f:v=f.read()
 assert len(v)<262144
 b.write_bytes(v);h=hashlib.sha256(v).hexdigest();assert sha(b)==h
 records[str(b.relative_to(D))]={'originalPath':str(a),'bytes':len(v),'sha256':h}
for folder in ['five-png-recovery-admission-independent-r1','five-png-producer-guard-root-r1']:
 for p in sorted((S/folder).rglob('*')):
  if p.is_file():copy(p,D/folder/p.relative_to(S/folder))
for name in ['share-five-retained-pngs-root-r2.py','publish-five-png-recovery-root-r1.py','judge-five-png-sharing-root-r2.py']:
 copy(S/name,D/'root-controls'/name)
assert sum(x['bytes'] for x in records.values())<128*1024
(D/'COPY-IDENTITIES.json').write_text(json.dumps(records,indent=2)+'\n')
(D/'README.md').write_text("""# Narrow freeing-step admission supplement

Current confirmed push1ea32dc666c5d4c33da1824bf5b9bf5f027ebda1 preserved the exact five-path proposal, independent review and original methods. Publication overhead left66,977,792B, so the ordinary64MiB producer guard refused before launching its child. No sharing action ran. This separately reviewed supplement changes only initial disk admission for the exact bounded freeing-step profile to56MiB; action memory64+512, live stops, full bytes/stat/xattr/current maps, producer/push/hold preconditions and durable per-leaf prefix remain. Original methods/refusal are retained. Strict build64/native70 remain unchanged. No arbitrary workload, all-five atomicity, whole power-loss durability, retirement of logical paths or cleanup beyond these exact five physical encodings is authorized.
""")

def run(args):
 q=subprocess.run(args,cwd=R,text=True,capture_output=True,timeout=55)
 with (P/'COMMANDS.jsonl').open('a') as f:f.write(json.dumps({'args':args,'rc':q.returncode,'stdout':q.stdout,'stderr':q.stderr,'utcNs':time.time_ns()})+'\n');f.flush();os.fsync(f.fileno())
 assert q.returncode==0,(args,q.stderr)
 return q.stdout.rstrip('\n')
assert run(['git','rev-parse','HEAD'])=='1ea32dc666c5d4c33da1824bf5b9bf5f027ebda1'
owned=str(D.relative_to(R));allowed={'AGENTS.md','docs/CONTINUATION.md'}
for line in run(['git','status','--porcelain','--untracked-files=all']).splitlines():assert line[3:] in allowed or line[3:].startswith(owned+'/'),line
run(['git','add','-f','--',owned]);run(['git','-c','gc.auto=0','commit','-m','Preserve scoped freeing-step admission review after producer refusal'])
head=run(['git','rev-parse','HEAD']);run(['git','-c','gc.auto=0','push','origin','HEAD:codex/lanternbound-production']);remote=run(['git','ls-remote','origin','refs/heads/codex/lanternbound-production']).split()[0]
assert remote==head and not run(['git','status','--porcelain'])
with (P/'PUSH-CONFIRMED.json').open('x') as f:json.dump({'commit':head,'remote':remote,'confirmed':True,'clean':True,'gateSHA256':sha(gate),'methodSHA256':sha(S/'share-five-retained-pngs-root-r2.py'),'holdSHA256':sha(R/'AGENTS.md'),'copiedBytes':sum(v['bytes'] for v in records.values()),'noStorageAction':True,'durableReceiptFileAndParentFsync':True},f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
fd=os.open(P,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
try:os.fsync(fd)
finally:os.close(fd)
print(json.dumps({'commit':head,'confirmed':True,'clean':True,'free':os.statvfs(R).f_bavail*os.statvfs(R).f_frsize}))
