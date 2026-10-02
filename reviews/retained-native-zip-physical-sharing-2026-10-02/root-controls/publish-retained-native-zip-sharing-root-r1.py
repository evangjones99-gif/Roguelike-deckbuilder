from pathlib import Path
import os,json,hashlib,subprocess,sys,stat,tarfile,gzip,io
R=Path('/workspace/Roguelike-deckbuilder');S=Path('/workspace/scratch');M=Path(__file__).parent
D=R/'reviews/retained-native-zip-physical-sharing-2026-10-02';P=S/'retained-native-zip-sharing-push-root-r1'
def body(p):
 fd=os.open(p,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW)
 with os.fdopen(fd,'rb') as f:
  before=os.fstat(f.fileno());v=f.read(262145);assert len(v)<262144 and before==os.fstat(f.fileno())
 assert before==os.lstat(p);return v
def sha(p):
 h=hashlib.sha256();fd=os.open(p,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW)
 with os.fdopen(fd,'rb') as f:
  for b in iter(lambda:f.read(65536),b''):h.update(b)
 return h.hexdigest()
def walk(root,rel=Path('.')):
 fd=os.open(root/rel,os.O_RDONLY|os.O_DIRECTORY|os.O_NOATIME|os.O_NOFOLLOW)
 try:
  with os.scandir(fd) as it:rows=sorted((e.name,e.stat(follow_symlinks=False)) for e in it)
 finally:os.close(fd)
 for n,s in rows:
  assert not stat.S_ISLNK(s.st_mode)
  if stat.S_ISDIR(s.st_mode):yield from walk(root,rel/n)
  else:assert stat.S_ISREG(s.st_mode) and s.st_size<262144;yield root/rel/n,rel/n,s.st_size
gate=S/'retained-native-zip-sharing-independent-r1/GATE.json';g=json.loads(body(gate));action=M/'share-retained-native-zip-root-r1.py';proposal=M/'PROPOSAL.json';caller=S/'target-clear-default-caller-independent-r1/GATE.json'
assert len(sys.argv)==2 and sha(gate)==sys.argv[1] and g['decision'].startswith('ACCEPT') and g['replacementBetter'] and g['oldIndependentEncodingNoLongerNeeded']
assert g['method']['sha256']==sha(action) and g['proposal']['sha256']==sha(proposal) and g['currentHold']['sha256']==sha(R/'AGENTS.md')
assert sha(caller)=='36ddead7bcd9647706f33c766952732dc3ff7b42455f2c678b125569bde2c31a'
assert g['plannedHold']['sha256']==sha(M/'AGENTS.planned.md')
E=json.loads(body(proposal));assert E['currentHold']['sha256']==sha(R/'AGENTS.md') and E['plannedHold']['sha256']==sha(M/'AGENTS.planned.md')
prior=json.loads(body(M/'PRIOR-FOUR-CONTROLS.json'));assert prior['POSTClosed'] and sha(Path(prior['postGatePath']))==prior['postGateSHA256']
pg=json.loads(body(Path(prior['postGatePath'])));assert pg['decision'].startswith('ACCEPT')
initial_free=os.statvfs(R).f_bavail*os.statvfs(R).f_frsize
assert initial_free>=int(65.5*1048576) #ordinary64 plus qualified1.5MiB text/Git estimate; native70/70.5 unchanged
assert not D.exists() and not P.exists()
plan=[]
for root,label in [(M,'author'),(gate.parent,'independent')]+[(Path(f['path']),f['label']) for f in prior['folders']]:
 for a,rel,n in walk(root):plan.append((a,label+'/'+str(rel),n))
for leaf in prior['files']:
 a=Path(leaf['path']);assert sha(a)==leaf['sha256'];plan.append((a,'prior-four/'+leaf['label'],a.stat().st_size))
for leaf in prior['exactPriorMemberPins']:assert sha(Path(leaf['path']))==leaf['sha256'] and os.lstat(leaf['path']).st_size==leaf['bytes']
plan.append((caller,'controls/DEFAULT-CALLER-GATE.json',caller.stat().st_size))
assert len(plan)<400 and len({logical for a,logical,n in plan})==len(plan) and sum(n for a,l,n in plan)<2*1048576
P.mkdir()
def run(args):
 p=subprocess.run(args,cwd=R,text=True,capture_output=True,timeout=55)
 with (P/'COMMANDS.jsonl').open('a') as f:f.write(json.dumps({'args':args,'rc':p.returncode,'stdout':p.stdout,'stderr':p.stderr})+'\n');f.flush();os.fsync(f.fileno())
 assert p.returncode==0,(args,p.stderr);return p.stdout.strip()
assert run(['git','rev-parse','HEAD'])=='6a8f435c4249828a799e7ccc29a310223a214831'
owned=str(D.relative_to(R))
for line in run(['git','status','--porcelain','--untracked-files=all']).splitlines():assert line[3:]=='AGENTS.md' or line[3:].startswith(owned+'/'),line
objects_before=run(['git','count-objects','-v'])
D.mkdir();records={logical:{'originalPath':str(a),'bytes':n,'sha256':sha(a)} for a,logical,n in plan}
manifest=json.dumps({'schema':'exact-source-support-bundle-r1','logicalBodies':records},sort_keys=True,separators=(',',':')).encode()+b'\n'
archive=D/'source-support.tar.gz'
with archive.open('xb') as raw,gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0) as gz,tarfile.open(fileobj=gz,mode='w|',format=tarfile.USTAR_FORMAT) as tar:
 def add(name,v):
  info=tarfile.TarInfo(name);info.size=len(v);info.mode=0o600;info.mtime=0;info.uid=info.gid=0;tar.addfile(info,io.BytesIO(v))
 add('MANIFEST.json',manifest)
 for a,logical,n in plan:
  v=body(a);assert len(v)==n and hashlib.sha256(v).hexdigest()==records[logical]['sha256'];add('bodies/'+logical,v)
 raw.flush()
fd=os.open(archive,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW);seen=set();manifest_seen=False
with os.fdopen(fd,'rb') as raw,tarfile.open(fileobj=raw,mode='r|gz') as tar:
 for m in tar:
  assert m.isfile()
  if m.name=='MANIFEST.json':assert not manifest_seen and tar.extractfile(m).read()==manifest;manifest_seen=True;continue
  assert m.name.startswith('bodies/');logical=m.name[7:];assert logical in records and logical not in seen
  h=hashlib.sha256();size=0
  with tar.extractfile(m) as f:
   for b in iter(lambda:f.read(65536),b''):h.update(b);size+=len(b)
  assert h.hexdigest()==records[logical]['sha256'] and size==records[logical]['bytes'];seen.add(logical)
assert manifest_seen and seen==set(records)
readable=[(Path(prior['postGatePath']),D/'previous-four-POST-GATE.json'),(proposal,D/'PROPOSAL.json'),(gate,D/'independent/GATE.json'),(caller,D/'root-controls/DEFAULT-CALLER-GATE.json')]+[(M/n,D/'root-controls'/n) for n in ['share-retained-native-zip-root-r1.py','publish-retained-native-zip-sharing-root-r1.py','judge-retained-native-zip-sharing-root-r1.py']]
for a,b in readable:
 v=body(a);b.parent.mkdir(parents=True,exist_ok=True)
 with b.open('xb') as f:f.write(v);f.flush();os.fsync(f.fileno())
 assert sha(b)==hashlib.sha256(v).hexdigest()
bundle={'path':str(archive),'sha256':sha(archive),'bytes':archive.stat().st_size,'manifestSHA256':hashlib.sha256(manifest).hexdigest(),'logicalBodies':len(records),'roundtripExact':True}
with (D/'SUPPORT-BUNDLE.json').open('x') as f:json.dump(bundle,f,indent=2);f.write('\n')
with (D/'README.md').open('x') as f:f.write('Exact native0.6.1 ZIP physical-sharing proposal only. Both complete archive paths/container bytes remain; no archive/version/body retirement. Full source, independent BEFORE and completed priorFourPOST/transaction proof are retained in deterministic source-support.tar.gz with exact original locators/member SHA/size manifest and full verified roundtrip. Private original proof remains. Source workflow hold prepends exact immutable/fresh-stage-only ZIP leaves to AGENTS. Future reproduction/reassembly uses fresh paths; extraction reads old archive into new output. Scratch private inode/time/write isolation would be lost and canonical nlink/ctime changed only after independent preference, confirmed current push and Root judgment. Root method shares one explicit scratch ZIP via durably journaled temp hardlink/atomic replacement. No other files/parts/extracted datasets/rights/oldversion/ZIP body cleanup. Protected1.8GB archive stat only. No new nativeOS/gameplay/default/fun claims.\n')
allocated=sum(s.st_blocks*512 for p,rel,n in walk(D) for s in [os.lstat(p)])+sum(os.lstat(root).st_blocks*512 for root,dirs,files in os.walk(D))
assert allocated<=512*1024 #hard publication allocation budget including folder blocks
assert sha(R/'AGENTS.md')==E['currentHold']['sha256']
planned=body(M/'AGENTS.planned.md');assert planned.endswith(body(R/'AGENTS.md'))
fd=os.open(R/'AGENTS.md',os.O_WRONLY|os.O_TRUNC|os.O_NOFOLLOW)
with os.fdopen(fd,'wb') as f:f.write(planned);f.flush();os.fsync(f.fileno())
assert sha(R/'AGENTS.md')==E['plannedHold']['sha256']
run(['git','add','-f','--',owned,'AGENTS.md']);run(['git','-c','gc.auto=0','commit','-m','Preserve reviewed native ZIP physical-sharing proposal'])
head=run(['git','rev-parse','HEAD']);run(['git','-c','gc.auto=0','push','origin','HEAD:codex/lanternbound-production']);remote=run(['git','ls-remote','origin','refs/heads/codex/lanternbound-production']).split()[0];assert remote==head and not run(['git','status','--porcelain'])
objects_after=run(['git','count-objects','-v'])
receipt={'commit':head,'remote':remote,'confirmed':True,'clean':True,'gateSHA256':sha(gate),'proposalSHA256':sha(proposal),'methodSHA256':sha(action),'holdSHA256':sha(R/'AGENTS.md'),'selectedMapSHA256':E['selectedMap']['sha256'],'callerGateSHA256':sha(caller),'initialFree':initial_free,'reserveEstimateBytes':int(1.5*1048576),'sourceAllocationCapBytes':512*1024,'publicationAllocatedBytes':allocated,'supportBundle':bundle,'priorPostGateSHA256':prior['postGateSHA256'],'gitObjectsBefore':objects_before,'gitObjectsAfter':objects_after,'finalFreeBeforeReceipt':os.statvfs(R).f_bavail*os.statvfs(R).f_frsize,'noRetirementAction':True}
with (P/'PUSH-CONFIRMED.json').open('x') as f:json.dump(receipt,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
fd=os.open(P,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
try:os.fsync(fd)
finally:os.close(fd)
print(json.dumps({'confirmed':True,'clean':True,'commit':head,'freeAfterReceipt':os.statvfs(R).f_bavail*os.statvfs(R).f_frsize}))
