from pathlib import Path
import os,json,hashlib,subprocess,time
R=Path('/workspace/Roguelike-deckbuilder');S=Path('/workspace/scratch');P=S/'target-clear-rejection-push-root-r2';P.mkdir()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(args):
    q=subprocess.run(args,cwd=R,text=True,capture_output=True,timeout=55)
    with (P/'COMMANDS.jsonl').open('a') as f:f.write(json.dumps({'args':args,'rc':q.returncode,'stdout':q.stdout,'stderr':q.stderr,'utcNs':time.time_ns()})+'\n');f.flush();os.fsync(f.fileno())
    assert q.returncode==0,(args,q.stderr)
    return q.stdout.rstrip('\n')
assert run(['git','rev-parse','HEAD'])=='34f0a2a4c4b19191efd56277e57b25ba0cf3788e'
gate=S/'target-clear-rejection-preservation-independent-r1/GATE.json';g=json.loads(gate.read_text());assert g['decision'].startswith('ACCEPT')
owned=['reviews/opening-target-clear-rejected-2026-10-02','reviews/three-png-physical-sharing-post-2026-10-02','reviews/second-three-png-physical-sharing-2026-10-02'];allowed=['AGENTS.md','docs/CONTINUATION.md','docs/PRODUCTION.md']
for line in run(['git','status','--porcelain','--untracked-files=all']).splitlines():assert line[3:] in allowed or any(line[3:].startswith(x+'/') for x in owned),line
D=R/owned[0]/'independent-preservation';assert not D.exists();D.mkdir()
for p in sorted(gate.parent.rglob('*')):
    if p.is_file():
        assert not p.is_symlink();q=D/p.relative_to(gate.parent);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes());assert sha(q)==sha(p)
for src in [S/'publish-target-clear-and-storage-post-root-r1.py',Path(__file__)]:
    q=R/owned[1]/'publication-method'/src.name;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(src.read_bytes());assert sha(q)==sha(src)
maps=json.loads((S/'target-wait-default-promotion-root-r1/RESULT.json').read_text())
def checkmaps():
    for rel,h in maps['canonicalInputs'].items():assert sha(R/rel)==h,rel
    for rel,h in maps['canonicalOutputs'].items():assert sha(R/'dist'/rel)==h,rel
checkmaps()
assert sha(R/owned[0]/'evidence.tar.gz')=='0871ec41c94e39313eb132aa1296385e3e6461e7be0a03e9ef333e4d8453b8a3'
run(['git','add','--',*allowed]);run(['git','add','-f','--',*owned]);run(['git','-c','gc.auto=0','commit','-m','Record rejected drag placement and completed scoped storage review'])
head=run(['git','rev-parse','HEAD']);run(['git','-c','gc.auto=0','push','origin','HEAD:codex/lanternbound-production']);remote=run(['git','ls-remote','origin','refs/heads/codex/lanternbound-production']).split()[0]
assert remote==head and not run(['git','status','--porcelain']);checkmaps()
(P/'PUSH-CONFIRMED.json').write_text(json.dumps({'commit':head,'remote':remote,'confirmed':True,'clean':True,'selectedSourceDigest':maps['sourceDigest'],'selectedOutputDigest':maps['outputsDigest'],'preservationGateSHA256':sha(gate),'noCleanupOrGamePromotion':True},indent=2)+'\n')
print(json.dumps({'commit':head,'confirmed':True,'clean':True,'free':os.statvfs(R).f_bavail*os.statvfs(R).f_frsize}))
