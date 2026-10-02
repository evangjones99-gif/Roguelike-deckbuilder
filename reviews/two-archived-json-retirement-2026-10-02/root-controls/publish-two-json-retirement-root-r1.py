from pathlib import Path
import os,json,hashlib,subprocess,time
S=Path('/workspace/scratch');R=Path('/workspace/Roguelike-deckbuilder')
D=R/'reviews/two-archived-json-retirement-2026-10-02';P=S/'two-json-retirement-push-root-r1'
gate=S/'two-json-raw-retirement-independent-r1/GATE.json'
method=S/'retire-two-archived-json-copies-root-r1.py'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
g=json.loads(gate.read_text());assert g['decision'].startswith('ACCEPT') and g['replacementBetter'] and g['oldLooseCopiesNoLongerNeeded']
assert g['method']['sha256']==sha(method) and g['publisher']['sha256']==sha(Path(__file__))
assert not D.exists() and not P.exists();D.mkdir();P.mkdir();records={}
def copy(a,b):
 assert a.is_file() and not a.is_symlink() and not b.exists();b.parent.mkdir(parents=True,exist_ok=True)
 fd=os.open(a,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME)
 with os.fdopen(fd,'rb') as f:v=f.read()
 b.write_bytes(v);h=hashlib.sha256(v).hexdigest();assert sha(b)==h
 records[str(b.relative_to(D))]={'originalPath':str(a),'bytes':len(v),'sha256':h}
for original,dest in [('settle-json-raw-retirement-proposal-r1','proposal'),('two-json-raw-retirement-independent-r1','independent'),('second-three-png-sharing-post-independent-r4','png-post'),('second-three-png-sharing-actual-guard-root-r4','png-action-guard'),('second-three-retained-png-sharing-actual-root-r4','png-action')]:
 for p in sorted((S/original).rglob('*')):
  if p.is_file():copy(p,D/dest/p.relative_to(S/original))
for name in [method.name,Path(__file__).name]:copy(S/name,D/'root-controls'/name)
assert sum(x['bytes'] for x in records.values())<=384*1024
(D/'COPY-IDENTITIES.json').write_text(json.dumps(records,indent=2)+'\n')
(D/'README.md').write_text('''# Reviewed physical copies, preserved evidence

The second three-PNG transaction retained every image path and body and recovered8,462,336 bytes in its recorded finite window before the result write. Its independent post-check and exact transaction controls are copied here; original packets/reviews remain unchanged.

The separate two-JSON proposal concerns only loose VISUAL-RESULT/PROGRESS scratch encodings from the rejected settleDrag comparison. They are different bodies. The published opening-ready-and-rapid-drop evidence capsule retains both exact blob bodies and logical names, with the original independent roundtrip review unchanged. This supplement records a fresh complete two-body roundtrip, mappings, current/historical consumer scope, and unexecuted fresh-path restoration source. Current callers create fresh outputs. Historical hardcoded readers require reconstruction or a new path-scoped reader; original raw paths and inode/time metadata would be lost. This is selective encoding retirement, not removal of unique findings, human feedback, art rights, source, captures, saves or events. Unknown future consumers/global open files are not disproved.

This pre-action publication claims no JSON retirement. Root producer judgment, current confirmed clean push and fresh64MiB/64+512 admission are required before the one exact action. Durable per-leaf journal, complete archive/body rechecks and unchanged87/56 current build checks are required; interruption stops with evidence retained and no automatic retry. Native70 and strictbuild64 admissions remain unchanged. The R3 ghost is privately built and unselected; no visual improvement or human enjoyment is asserted here.
''')
def run(args):
 q=subprocess.run(args,cwd=R,text=True,capture_output=True,timeout=55)
 with (P/'COMMANDS.jsonl').open('a') as f:f.write(json.dumps({'args':args,'rc':q.returncode,'stdout':q.stdout,'stderr':q.stderr,'utcNs':time.time_ns()})+'\n');f.flush();os.fsync(f.fileno())
 assert q.returncode==0,(args,q.stderr)
 return q.stdout.rstrip('\n')
assert run(['git','rev-parse','HEAD'])=='90d128934e5a86c66c4fa92d0eebb1906a3f2b37'
owned=str(D.relative_to(R))
for line in run(['git','status','--porcelain','--untracked-files=all']).splitlines():assert line[3:].startswith(owned+'/'),line
run(['git','add','-f','--',owned]);run(['git','-c','gc.auto=0','commit','-m','Preserve reviewed exact archived JSON retirement proposal and PNG postcheck'])
head=run(['git','rev-parse','HEAD']);run(['git','-c','gc.auto=0','push','origin','HEAD:codex/lanternbound-production']);remote=run(['git','ls-remote','origin','refs/heads/codex/lanternbound-production']).split()[0]
assert remote==head and not run(['git','status','--porcelain'])
with (P/'PUSH-CONFIRMED.json').open('x') as f:json.dump({'commit':head,'remote':remote,'confirmed':True,'clean':True,'gateSHA256':sha(gate),'methodSHA256':sha(method),'copiedBytes':sum(v['bytes'] for v in records.values()),'noJSONRetirement':True},f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
for directory in [P,S]:
 fd=os.open(directory,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
 try:os.fsync(fd)
 finally:os.close(fd)
print(json.dumps({'commit':head,'confirmed':True,'clean':True,'free':os.statvfs(R).f_bavail*os.statvfs(R).f_frsize}))
