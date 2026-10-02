from pathlib import Path
import hashlib,json,os,subprocess,time
R=Path('/workspace/Roguelike-deckbuilder');S=Path('/workspace/scratch')
D=R/'reviews/five-rebuilt-png-sharing-post-2026-10-02'
E=R/'reviews/opening-target-clear-ghost-opt-in-2026-10-02/selection-2026-10-02'
P=S/'target-clear-selection-push-root-r1'
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(65536),b''):h.update(b)
    return h.hexdigest()
assert sha(S/'five-rebuilt-png-sharing-post-independent-r1/GATE.json')=='fa0c02948e5091af3500f0ef36914240b0b2da6e92bd27a812007f25ba59853d'
selected=json.loads((S/'target-clear-ghost-promotion-root-r3/RESULT.json').read_text())
assert selected['normal'] and selected['defaultEnabled'] is False
for rel,h in selected['inputs'].items():assert sha(R/rel)==h,rel
for rel,h in selected['outputs'].items():assert sha(R/'dist'/rel)==h,rel
assert not D.exists() and not E.exists() and not P.exists()
plan=[]
for p in sorted((S/'five-rebuilt-png-sharing-post-independent-r1').rglob('*')):
    if p.is_file():plan.append((p,D/'independent'/p.relative_to(S/'five-rebuilt-png-sharing-post-independent-r1')))
for folder,names,dest in [
    ('five-rebuilt-png-sharing-actual-root-r1',['BEFORE.json','JOURNAL.jsonl','RESULT.json'],D/'actual'),
    ('five-rebuilt-png-proposal-push-root-r1',['PUSH-CONFIRMED.json'],D/'controls'),
    ('target-clear-ghost-promotion-root-r3',['BEFORE-87-56-MAPS.json','PRODUCER-JUDGMENT.json','RESULT.json'],E/'selection'),
]:
    for n in names:plan.append((S/folder/n,dest/n))
plan.append((S/'five-rebuilt-png-producer-judgment-root-r1.json',D/'controls/PRODUCER-JUDGMENT.json'))
for folder,dest in [('five-rebuilt-png-publication-guard-root-r1',D/'publication-guard'),('five-rebuilt-png-producer-guard-root-r1',D/'producer-guard'),('five-rebuilt-png-sharing-guard-root-r1',D/'action-guard'),('target-clear-ghost-promotion-guard-root-r3',E/'promotion-guard')]:
    for n in ['ADMISSION.json','EXECUTION.log','RESULT.json']:plan.append((S/folder/n,dest/n))
assert sum(p.stat().st_size for p,q in plan)<256*1024
records={}
for source,target in plan:
    assert not source.is_symlink() and not target.exists()
    data=source.read_bytes();assert len(data)<262144
    target.parent.mkdir(parents=True,exist_ok=True)
    with target.open('xb') as f:f.write(data);f.flush();os.fsync(f.fileno())
    assert sha(target)==sha(source)
    records[str(target.relative_to(R))]={'originalPath':str(source),'bytes':len(data),'sha256':sha(target)}
(D/'COPY-IDENTITIES.json').write_text(json.dumps(records,indent=2)+'\n')
(D/'README.md').write_text('Independent POST accepts exact second-five physical sharing after confirmed push and Root judgment. Ten media and all143 prior runtime bodies, metadata, journals and protected archive stat passed. Gross10,170,368B; measured pre-result net10,137,600B. Every historical path/body remains. Private inode/time/write isolation is lost; known unresolved aliases1/1/1/0/1 remain qualified. Per-leaf durable prefix, no all-five atomicity, no protected archive body read and no further cleanup authority. Original source/gates/controls remain retained.\n')
(E/'README.md').write_text('Root selected the exact independently reviewed R3 opt-in build: source9f57b1b6/outputsa02d5d62,88/56. Default remains OFF; targetClearGhost=1 enables the candidate. Named waiting cue stays ON. Previous two source bodies, five nonmedia outputs and full maps remain in the complete capsule and retained rollback. Sparse actual readability and six full matching checkpoints are accepted; motion/dense layout/cancel/rapid-drop repair/novice300/human fun/pixel art/default promotion remain unqualified. No media write, retirement, version or release tag. Continue into fresh default-on strict build and actual comparison.\n')
P.mkdir()
def run(args):
    q=subprocess.run(args,cwd=R,text=True,capture_output=True,timeout=55)
    with (P/'COMMANDS.jsonl').open('a') as f:f.write(json.dumps({'args':args,'rc':q.returncode,'stdout':q.stdout,'stderr':q.stderr,'utcNs':time.time_ns()})+'\n');f.flush();os.fsync(f.fileno())
    assert q.returncode==0,(args,q.stderr)
    return q.stdout.strip()
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
receipt={'commit':head,'remote':remote,'confirmed':True,'clean':True,'sourceDigest':'9f57b1b6d0bcbba495d5dff38f14e01ccb813ba577174a06b6b0469c2d445e39','outputsDigest':'a02d5d6292d424bd1bbe26cbdd84a6806eac17ec84adc484549a7972a3e69c3e','defaultEnabled':False,'copiedBytes':sum(v['bytes'] for v in records.values()),'noReleaseTag':True}
with (P/'PUSH-CONFIRMED.json').open('x') as f:json.dump(receipt,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
print(json.dumps(receipt))
