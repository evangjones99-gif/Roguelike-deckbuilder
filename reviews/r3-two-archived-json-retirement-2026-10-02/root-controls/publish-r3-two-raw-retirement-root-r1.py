from pathlib import Path
import os,json,hashlib,subprocess,sys,stat
R=Path('/workspace/Roguelike-deckbuilder');S=Path('/workspace/scratch');M=Path(__file__).parent
D=R/'reviews/r3-two-archived-json-retirement-2026-10-02';P=S/'r3-two-raw-retirement-push-root-r1'
def sha(p):
 h=hashlib.sha256();f=os.open(p,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW)
 with os.fdopen(f,'rb') as r:
  for b in iter(lambda:r.read(65536),b''):h.update(b)
 return h.hexdigest()
gate=S/'r3-two-raw-retirement-independent-r1/GATE.json';g=json.loads(gate.read_text());action=M/'retire-r3-two-archived-json-root-r1.py';proposal=M/'PROPOSAL.json';caller=S/'target-clear-default-caller-independent-r1/GATE.json'
assert len(sys.argv)==2 and sha(gate)==sys.argv[1] and g['decision'].startswith('ACCEPT') and g['replacementBetter'] and g['oldLooseCopiesNoLongerNeeded']
assert g['method']['sha256']==sha(action) and g['proposal']['sha256']==sha(proposal) and g['currentHold']['sha256']==sha(R/'AGENTS.md')
assert sha(caller)=='36ddead7bcd9647706f33c766952732dc3ff7b42455f2c678b125569bde2c31a'
assert not D.exists() and not P.exists()
assert os.statvfs(R).f_bavail*os.statvfs(R).f_frsize>=65*1048576 #64floor plus1MiB estimated bounded text copy/Git overhead; no native threshold change
plan=[]
def walk(root,rel=Path('.')):
 fd=os.open(root/rel,os.O_RDONLY|os.O_DIRECTORY|os.O_NOATIME|os.O_NOFOLLOW)
 try:
  with os.scandir(fd) as it:rows=[(e.name,e.stat(follow_symlinks=False)) for e in it]
 finally:os.close(fd)
 for n,s in rows:
  assert not stat.S_ISLNK(s.st_mode)
  if stat.S_ISDIR(s.st_mode):yield from walk(root,rel/n)
  else:assert stat.S_ISREG(s.st_mode);yield root/rel/n,rel/n,s.st_size
for source,folder in [(M,'proposal'),(gate.parent,'independent')]:
 for a,rel,n in walk(source):plan.append((a,D/folder/rel,n))
for n in ['retire-r3-two-archived-json-root-r1.py','publish-r3-two-raw-retirement-root-r1.py','judge-r3-two-raw-retirement-root-r1.py']:
 a=M/n;plan.append((a,D/'root-controls'/n,a.stat().st_size))
plan.append((caller,D/'root-controls/DEFAULT-CALLER-GATE.json',caller.stat().st_size));assert sum(n for a,b,n in plan)<512*1024
P.mkdir()
def run(args):
 p=subprocess.run(args,cwd=R,text=True,capture_output=True,timeout=55)
 with (P/'COMMANDS.jsonl').open('a') as f:f.write(json.dumps({'args':args,'rc':p.returncode,'stdout':p.stdout,'stderr':p.stderr})+'\n');f.flush();os.fsync(f.fileno())
 assert p.returncode==0,(args,p.stderr);return p.stdout.strip()
assert run(['git','rev-parse','HEAD'])=='b18e752fc528db4c9e447de071977253375f613e'
owned=str(D.relative_to(R))
for line in run(['git','status','--porcelain','--untracked-files=all']).splitlines():assert line[3:]=='AGENTS.md' or line[3:].startswith(owned+'/'),line
D.mkdir();records={}
for a,b,n in plan:
 before=os.lstat(a);fd=os.open(a,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW)
 with os.fdopen(fd,'rb') as f:v=f.read(262145);assert len(v)==n and n<262144 and before==os.fstat(f.fileno())
 assert before==os.lstat(a);b.parent.mkdir(parents=True,exist_ok=True)
 with b.open('xb') as f:f.write(v);f.flush();os.fsync(f.fileno())
 h=hashlib.sha256(v).hexdigest();assert sha(b)==h;records[str(b.relative_to(D))]={'originalPath':str(a),'bytes':n,'sha256':h}
with (D/'COPY-IDENTITIES.json').open('x') as f:json.dump(records,f,indent=2);f.write('\n')
with (D/'README.md').open('x') as f:f.write('Reviewed proposal only: retire exactly two loose R3 rich JSON encodings after current push and separate producer judgment. Distinct full bodies/logical provenance stay in the unchanged published complete capsule. All screenshots/saves/events/source/reviews and protected originals remain. Raw paths/inodes/times would be lost; historical readers require fresh reconstruction and explicit new-reader adaptation. No action, default promotion, native or fun claim.\n')
assert sum(p.stat().st_size for p in D.rglob('*') if p.is_file())<512*1024
run(['git','add','-f','--',owned,'AGENTS.md']);run(['git','-c','gc.auto=0','commit','-m','Preserve reviewed exact R3 raw encoding retirement proposal'])
head=run(['git','rev-parse','HEAD']);run(['git','-c','gc.auto=0','push','origin','HEAD:codex/lanternbound-production']);remote=run(['git','ls-remote','origin','refs/heads/codex/lanternbound-production']).split()[0];assert remote==head and not run(['git','status','--porcelain'])
with (P/'PUSH-CONFIRMED.json').open('x') as f:json.dump({'commit':head,'remote':remote,'confirmed':True,'clean':True,'gateSHA256':sha(gate),'proposalSHA256':sha(proposal),'methodSHA256':sha(action),'callerGateSHA256':sha(caller),'copiedBytes':sum(x['bytes'] for x in records.values()),'finalFreeBeforeReceipt':os.statvfs(R).f_bavail*os.statvfs(R).f_frsize,'noRetirementAction':True},f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
fd=os.open(P,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
try:os.fsync(fd)
finally:os.close(fd)
print(json.dumps({'confirmed':True,'clean':True,'commit':head,'freeAfterReceipt':os.statvfs(R).f_bavail*os.statvfs(R).f_frsize}))
