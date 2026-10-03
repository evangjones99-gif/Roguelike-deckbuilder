from pathlib import Path
import os,json,hashlib,subprocess,time
S=Path('/workspace/scratch');R=Path('/workspace/Roguelike-deckbuilder');D=R/'reviews/second-three-png-recovery-admission-2026-10-02';P=S/'recovery-admission-push-root-r1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
gate=S/'second-three-png-recovery-admission-independent-r1/GATE.json';g=json.loads(gate.read_text());assert g['decision'].startswith('ACCEPT')
assert g.get('actionExecutedByReviewer',False)==False
assert not D.exists() and not P.exists();D.mkdir();P.mkdir();records={}
def copy(a,b):
    assert not a.is_symlink() and not b.exists();b.parent.mkdir(parents=True,exist_ok=True)
    fd=os.open(a,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME)
    with os.fdopen(fd,'rb') as f:v=f.read()
    b.write_bytes(v);h=hashlib.sha256(v).hexdigest();assert sha(b)==h
    records[str(b.relative_to(D))]={'originalPath':str(a),'bytes':len(v),'sha256':h}
for folder in ['second-three-png-recovery-admission-independent-r1','second-three-png-judgment-guard-root-r1','target-clear-rejection-push-root-r2','target-clear-rejection-push-guard-root-r2','second-three-png-proposal-preservation-guard-root-r1']:
    for p in sorted((S/folder).rglob('*')):
        if p.is_file():copy(p,D/folder/p.relative_to(S/folder))
for name in ['guard-source-recovery-56m-root-r1.py','guard-source-recovery-56m-root-r2.py','share-second-three-retained-pngs-root-r3.py','bounded-source-recovery-admission-proposal-root-r1.json','bounded-source-recovery-admission-proposal-root-r2.json','draft-bounded-recovery-admission-root-r1.py','refine-bounded-recovery-guard-root-r1.py','draft-recovery-producer-control-root-r1.py','preserve-second-three-png-proposal-root-r1.py','publish-reviewed-recovery-admission-root-r1.py','judge-second-three-png-sharing-root-r2.py']:
    copy(S/name,D/'root-controls'/name)
assert sum(x['bytes'] for x in records.values())<512*1048576//1024
(D/'COPY-IDENTITIES.json').write_text(json.dumps(records,indent=2)+'\n')
(D/'README.md').write_text('''# Narrow recovery admission revision

Confirmed clean push9ce3d3bf retained rejected ghost actual and completed prior PNG POST plus the next proposal. It left about66.2MB free; the normal64MiB source guard refused producer-judgment launch before execution. All original refusals/methods remain. No transaction followed that refusal.

This separate source review assesses56MiB initial disk for only bounded, pinned source/publication/recovery invocations. The wrapper preserves memory work/reserve/live-stop limits. Its filename filter is not universal child-workload isolation or an exact script allowlist: the independent gate and coordinated sole writer bind the permitted invocations. It authorizes neither arbitrary Python nor a lower build/browser/native/image/release admission. Strict build64MiB and native70MiB remain unchanged.

The r3 sharing method differs from accepted r2 only by56MiB disk preflight and fresh transaction/temp identifiers. Identity, full three-body/stat/xattr/held-parent/current clean confirmed-push/producer/durable-prefix checks remain. Bounded BEFORE/journal/RESULT directory writes are small compared with the disk reserve, with no large old-inode backups. Every path/body/provenance remains retained; original private inode/time/write isolation and anchor link/ctime losses still require explicit producer acceptance. One existing alias per anchor remains unresolved. No space gain or storage action is claimed here.

Finite tiny bootstrap scripts prepared this proposal and producer control outside a guard after normal admission refused; their resources are unmetered, and no guarded bootstrap compliance is claimed. A pointless always-true assertion in the unexecuted r1 wrapper was removed in fresh r2; both originals remain. This is a resource-recovery scope correction, not a quality or retirement badge. The live selected build is still1d5bf40a/30ddc549 with painted art; R3 actor-safe ghost source remains opt-in/unbuilt.
''')
def run(args):
    q=subprocess.run(args,cwd=R,text=True,capture_output=True,timeout=55)
    with (P/'COMMANDS.jsonl').open('a') as f:f.write(json.dumps({'args':args,'rc':q.returncode,'stdout':q.stdout,'stderr':q.stderr,'utcNs':time.time_ns()})+'\n');f.flush();os.fsync(f.fileno())
    assert q.returncode==0,(args,q.stderr)
    return q.stdout.rstrip('\n')
assert run(['git','rev-parse','HEAD'])=='9ce3d3bf9970e28631295b35e34dd0529ae413a8'
owned=str(D.relative_to(R))
for line in run(['git','status','--porcelain','--untracked-files=all']).splitlines():assert line[3:].startswith(owned+'/'),line
run(['git','add','-f','--',owned]);run(['git','-c','gc.auto=0','commit','-m','Preserve reviewed bounded recovery admission before storage action'])
head=run(['git','rev-parse','HEAD']);run(['git','-c','gc.auto=0','push','origin','HEAD:codex/lanternbound-production']);remote=run(['git','ls-remote','origin','refs/heads/codex/lanternbound-production']).split()[0]
assert remote==head and not run(['git','status','--porcelain'])
(P/'PUSH-CONFIRMED.json').write_text(json.dumps({'commit':head,'remote':remote,'confirmed':True,'clean':True,'gateSHA256':sha(gate),'methodSHA256':sha(S/'share-second-three-retained-pngs-root-r3.py'),'holdSHA256':sha(R/'AGENTS.md'),'copiedBytes':sum(v['bytes'] for v in records.values()),'noStorageAction':True},indent=2)+'\n')
print(json.dumps({'commit':head,'confirmed':True,'clean':True,'free':os.statvfs(R).f_bavail*os.statvfs(R).f_frsize}))
