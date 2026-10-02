from pathlib import Path
import json,hashlib,subprocess,time,os
R=Path('/workspace/Roguelike-deckbuilder'); S=Path('/workspace/scratch'); P=S/'default-wait-checkpoint-push-root-r1';P.mkdir()
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(65536),b''):h.update(b)
 return h.hexdigest()
def copy_tree(a,b):
 assert not b.exists();b.mkdir(parents=True)
 records={}
 for p in sorted(a.rglob('*')):
  if p.is_file():
   q=b/p.relative_to(a);q.parent.mkdir(parents=True,exist_ok=True)
   with p.open('rb') as src,q.open('xb') as dst:
    for chunk in iter(lambda:src.read(65536),b''):dst.write(chunk)
   assert digest(p)==digest(q);records[str(q.relative_to(b))]=digest(q)
 (b/'COPY-IDENTITIES.json').write_text(json.dumps(records,indent=2)+'\n')
def run(args):
 c=subprocess.run(args,cwd=R,text=True,capture_output=True,timeout=55)
 with (P/'COMMANDS.jsonl').open('a') as f:f.write(json.dumps({'args':args,'rc':c.returncode,'stdout':c.stdout,'stderr':c.stderr,'utcNs':time.time_ns()})+'\n');f.flush();os.fsync(f.fileno())
 assert c.returncode==0,(args,c.stderr)
 return c.stdout.rstrip('\n')
assert run(['git','rev-parse','HEAD'])=='ccee87f5361146580094a75c7c564766724733cd'
D=R/'reviews/opening-default-wait-cue-2026-10-02'; A=R/'reviews/cairn-contact-native-study-2026-10-02'
assert digest(D/'evidence.tar.gz')=='dd9003b676ae49b8a81441f73dfaec51b4309206a3ce32716cb2c8c1fcda169f'
assert digest(A/'evidence.tar.gz')=='7cfa83f2f715d44c35981b2d65c0eba34a50ac098d714e8ba1a63f2f2bb315bf'
assert digest(S/'default-wait-cue-preservation-independent-r1/GATE.json')=='2d970f4d64d30b401ae3c861e9c70065109b2094864b261a48ac711cec12eefc'
copy_tree(S/'default-wait-cue-preservation-independent-r1',D/'independent-preservation')
for dst,script,guard in [(D,'archive-default-wait-cue-evidence-root-r1.py','default-wait-cue-preservation-guard-root-r1'),(A,'archive-contact-native-study-root-r1.py','contact-native-preservation-guard-root-r1')]:
 copy_tree(S/guard,dst/'preservation-method/guard')
 q=dst/'preservation-method'/script;q.write_bytes((S/script).read_bytes());assert digest(q)==digest(S/script)
with (D/'README.md').open('a') as f:f.write('\nIndependent preservation gate `2d970f4d` verifies all209 blobs/226 logical originals, full87/56 selected maps, six raw pairs, four original captures and retained rollback. The101 omitted media bodies remain needed. Canonical OriginalPath entries are mutable; exact archived bytes and frozen stage preserve this checkpoint. The original reviewer dictionary/array assumption failure is retained with its corrected successful verifier. No retirement authority follows.\n')
allowed=['AGENTS.md','docs/CONTINUATION.md','docs/PRODUCTION.md','docs/OPENING-TARGET-WAIT.md','src/main.ts','src/tactile-hand.ts']
owned=['reviews/opening-default-wait-cue-2026-10-02','reviews/cairn-contact-native-study-2026-10-02']
for line in run(['git','status','--porcelain','--untracked-files=all']).splitlines():assert line[3:] in allowed or any(line[3:].startswith(o+'/') for o in owned),line
maps=json.loads((S/'target-wait-default-promotion-root-r1/RESULT.json').read_text())
def check_maps():
 for rel,sha in maps['canonicalInputs'].items():assert digest(R/rel)==sha,rel
 for rel,sha in maps['canonicalOutputs'].items():assert digest(R/'dist'/rel)==sha,rel
 assert len(list((R/'dist').rglob('*'))))>=56
check_maps()
run(['git','add','--',*allowed]);run(['git','add','-f','--',*owned]);run(['git','-c','gc.auto=0','commit','-m','Enable reviewed named target waiting feedback and preserve art rejection'])
head=run(['git','rev-parse','HEAD']);run(['git','-c','gc.auto=0','push','origin','HEAD:codex/lanternbound-production']);remote=run(['git','ls-remote','origin','refs/heads/codex/lanternbound-production']).split()[0]
assert head==remote and not run(['git','status','--porcelain']);check_maps()
(P/'PUSH-CONFIRMED.json').write_text(json.dumps({'commit':head,'remote':remote,'confirmed':True,'clean':True,'selectedSourceDigest':maps['sourceDigest'],'selectedOutputDigest':maps['outputsDigest'],'noCleanup':True},indent=2)+'\n')
print(json.dumps({'commit':head,'confirmed':True,'clean':True,'free':os.statvfs(R).f_bavail*os.statvfs(R).f_frsize}))
