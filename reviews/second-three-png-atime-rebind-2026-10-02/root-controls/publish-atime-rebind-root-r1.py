from pathlib import Path
import os,json,hashlib,subprocess,time
S=Path('/workspace/scratch');R=Path('/workspace/Roguelike-deckbuilder');D=R/'reviews/second-three-png-atime-rebind-2026-10-02';P=S/'atime-rebind-push-root-r1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
gate=S/'second-three-png-atime-rebind-independent-r1/GATE.json';g=json.loads(gate.read_text());assert g['decision'].startswith('ACCEPT')
assert g.get('actionExecutedByReviewer',False)==False
assert not D.exists() and not P.exists();D.mkdir();P.mkdir();records={}
def copy(a,b):
    assert not a.is_symlink() and not b.exists();b.parent.mkdir(parents=True,exist_ok=True)
    fd=os.open(a,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME)
    with os.fdopen(fd,'rb') as f:v=f.read()
    b.write_bytes(v);h=hashlib.sha256(v).hexdigest();assert sha(b)==h
    records[str(b.relative_to(D))]={'originalPath':str(a),'bytes':len(v),'sha256':h}
for folder in ['second-three-png-atime-rebind-independent-r1','second-three-png-sharing-actual-guard-root-r3']:
    for p in sorted((S/folder).rglob('*')):
        if p.is_file():copy(p,D/folder/p.relative_to(S/folder))
for name in ['share-second-three-retained-pngs-root-r4.py','publish-atime-rebind-root-r1.py','judge-second-three-png-sharing-root-r4.py']:
    copy(S/name,D/'root-controls'/name)
assert sum(x['bytes'] for x in records.values())<512*1048576//1024
(D/'COPY-IDENTITIES.json').write_text(json.dumps(records,indent=2)+'\n')
(D/'README.md').write_text('''# Atime-only preflight correction

The prior exact r3 attempt stopped before creating the transaction directory or linking any leaf: all three canonical anchor access times differed from the proposal. Every other field and all three private recipient snapshots matched. The cause of access-time changes is not attributed. This supplemental method records both historical proposal metadata and current stable metadata. Only atime may differ at initial rebinding; all other fields, full bytes, xattrs, held-directory and per-step identity requirements remain exact. No timestamp is set or restored. Retain the original failure and all reviews. Independent source review, current confirmed push and durable producer authorization precede this fresh action. Reviewed56MiB recovery-only admission remains bounded; strict build64/native70 remain unchanged. No completed sharing or quality improvement is claimed here.
''')
def run(args):
    q=subprocess.run(args,cwd=R,text=True,capture_output=True,timeout=55)
    with (P/'COMMANDS.jsonl').open('a') as f:f.write(json.dumps({'args':args,'rc':q.returncode,'stdout':q.stdout,'stderr':q.stderr,'utcNs':time.time_ns()})+'\n');f.flush();os.fsync(f.fileno())
    assert q.returncode==0,(args,q.stderr)
    return q.stdout.rstrip('\n')
assert run(['git','rev-parse','HEAD'])=='37cf5633c68e6a82f133e508ebad5149d39d717c'
owned=str(D.relative_to(R))
for line in run(['git','status','--porcelain','--untracked-files=all']).splitlines():assert line[3:].startswith(owned+'/'),line
run(['git','add','-f','--',owned]);run(['git','-c','gc.auto=0','commit','-m','Preserve reviewed atime-only recovery preflight correction'])
head=run(['git','rev-parse','HEAD']);run(['git','-c','gc.auto=0','push','origin','HEAD:codex/lanternbound-production']);remote=run(['git','ls-remote','origin','refs/heads/codex/lanternbound-production']).split()[0]
assert remote==head and not run(['git','status','--porcelain'])
with (P/'PUSH-CONFIRMED.json').open('x') as f:json.dump({'commit':head,'remote':remote,'confirmed':True,'clean':True,'gateSHA256':sha(gate),'methodSHA256':sha(S/'share-second-three-retained-pngs-root-r4.py'),'holdSHA256':sha(R/'AGENTS.md'),'copiedBytes':sum(v['bytes'] for v in records.values()),'noStorageAction':True,'durableReceiptFileAndParentFsync':True},f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
fd=os.open(P,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
try:os.fsync(fd)
finally:os.close(fd)
print(json.dumps({'commit':head,'confirmed':True,'clean':True,'free':os.statvfs(R).f_bavail*os.statvfs(R).f_frsize}))
