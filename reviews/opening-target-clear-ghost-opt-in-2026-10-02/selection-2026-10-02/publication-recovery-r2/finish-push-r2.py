from pathlib import Path
import hashlib,json,os,subprocess,time
R=Path('/workspace/Roguelike-deckbuilder');S=Path('/workspace/scratch')
D=R/'reviews/five-rebuilt-png-sharing-post-2026-10-02'
E=R/'reviews/opening-target-clear-ghost-opt-in-2026-10-02/selection-2026-10-02'
P=S/'target-clear-selection-push-recovery-root-r2'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert not P.exists()
identities=json.loads((D/'COPY-IDENTITIES.json').read_text())
for rel,row in identities.items():
    assert sha(R/rel)==row['sha256']==sha(Path(row['originalPath']))
selected=json.loads((S/'target-clear-ghost-promotion-root-r3/RESULT.json').read_text())
for rel,h in selected['inputs'].items():assert sha(R/rel)==h,rel
for rel,h in selected['outputs'].items():assert sha(R/'dist'/rel)==h,rel
Q=E/'publication-recovery-r2';assert not Q.exists();Q.mkdir()
for source,name in [(S/'publish-target-clear-selection-root-r1.py','failed-publisher-r1.py'),(S/'target-clear-selection-publication-guard-root-r1/EXECUTION.log','failed-execution-r1.log'),(S/'target-clear-selection-publication-guard-root-r1/RESULT.json','failed-guard-r1.json'),(Path(__file__),'finish-push-r2.py')]:
    with (Q/name).open('xb') as f:f.write(source.read_bytes());f.flush();os.fsync(f.fileno())
(Q/'README.md').write_text('The first publisher copied and verified evidence, then stopped before git add/commit/push: its command helper used strip(), removing the first Git porcelain status leading space. This separate recovery keeps all copies/first source/failure logs, verifies their bodies and exact selected runtime, preserves raw status columns with rstrip newline only, and performs the pending bounded commit/push once. No source/runtime/review/cleanup retry or rewrite.\n')
P.mkdir()
def run(args):
    q=subprocess.run(args,cwd=R,text=True,capture_output=True,timeout=55)
    with (P/'COMMANDS.jsonl').open('a') as f:f.write(json.dumps({'args':args,'rc':q.returncode,'stdout':q.stdout,'stderr':q.stderr,'utcNs':time.time_ns()})+'\n');f.flush();os.fsync(f.fileno())
    assert q.returncode==0,(args,q.stderr)
    return q.stdout.rstrip('\n')
assert run(['git','rev-parse','HEAD'])=='cb0f9ebd907ba2f709b53af8190efe1d5bc84127'
owned=[str(D.relative_to(R)),str(E.relative_to(R))]
allowed=['src/main.ts','src/tactile-hand.ts','src/tactile-ghost-placement.ts','docs/CONTINUATION.md','docs/PRODUCTION.md']
for line in run(['git','status','--porcelain','--untracked-files=all']).splitlines():
    assert line[3:] in allowed or any(line[3:].startswith(p+'/') for p in owned),line
run(['git','add','-f','--',*allowed,*owned])
run(['git','-c','gc.auto=0','commit','-m','Select reviewed opt-in target clarity and preserve completed storage proof'])
head=run(['git','rev-parse','HEAD']);run(['git','-c','gc.auto=0','push','origin','HEAD:codex/lanternbound-production'])
remote=run(['git','ls-remote','origin','refs/heads/codex/lanternbound-production']).split()[0]
assert head==remote and not run(['git','status','--porcelain'])
receipt={'commit':head,'remote':remote,'confirmed':True,'clean':True,'sourceDigest':'9f57b1b6d0bcbba495d5dff38f14e01ccb813ba577174a06b6b0469c2d445e39','outputsDigest':'a02d5d6292d424bd1bbe26cbdd84a6806eac17ec84adc484549a7972a3e69c3e','defaultEnabled':False,'firstFailureRetained':True,'noCleanupOrReleaseTag':True}
with (P/'PUSH-CONFIRMED.json').open('x') as f:json.dump(receipt,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
print(json.dumps(receipt))
