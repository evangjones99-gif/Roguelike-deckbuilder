from pathlib import Path
import os, sys, json, hashlib, stat, tarfile, subprocess, time
R=Path('/workspace/Roguelike-deckbuilder');S=Path('/workspace/scratch')
proposal,proposal_sha,gate,gate_sha,judgment,judgment_sha,push,push_sha=sys.argv[1:]
KEYS=['st_dev','st_ino','st_mode','st_nlink','st_uid','st_gid','st_size','st_blocks','st_atime_ns','st_mtime_ns','st_ctime_ns']
def md(t):return {k:getattr(t,k) for k in KEYS}
def digest(f):
 h=hashlib.sha256()
 for b in iter(lambda:f.read(65536),b''):h.update(b)
 return h.hexdigest()
def sha(p):
 fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME)
 with os.fdopen(fd,'rb') as f:return digest(f)
def body(p):
 fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME)
 with os.fdopen(fd,'rb') as f:return f.read(262145)
def parentfd(p):
 fd=os.open('/',os.O_PATH|os.O_DIRECTORY|os.O_NOFOLLOW)
 try:
  for part in p.parent.parts[1:]:
   assert part not in ('','.', '..');q=os.open(part,os.O_PATH|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd);os.close(fd);fd=q
  return fd
 except BaseException:os.close(fd);raise
def syncfd(fd):
 q=os.open('.',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd)
 try:os.fsync(q)
 finally:os.close(q)
def save(p,j):
 with p.open('x') as f:json.dump(j,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 fd=parentfd(p)
 try:syncfd(fd)
 finally:os.close(fd)
def check(fd,name,expected,h):
 before=md(os.stat(name,dir_fd=fd,follow_symlinks=False));assert before==expected and stat.S_ISREG(before['st_mode'])
 f=os.open(name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME,dir_fd=fd)
 try:
  assert md(os.fstat(f))==expected and not os.listxattr('/proc/self/fd/'+str(f))
  with os.fdopen(os.dup(f),'rb') as stream:assert digest(stream)==h
  assert md(os.fstat(f))==expected
 finally:os.close(f)
 assert md(os.stat(name,dir_fd=fd,follow_symlinks=False))==expected
assert proposal==str(S/'four-archived-raw-retirement-source-author-r2/PROPOSAL.json')
assert gate==str(S/'four-archived-raw-retirement-independent-r2/GATE.json') and judgment==str(S/'four-archived-raw-retirement-producer-root-r2.json')
assert push==str(S/'four-archived-raw-retirement-push-root-r2/PUSH-CONFIRMED.json')
for p,h in [(proposal,proposal_sha),(gate,gate_sha),(judgment,judgment_sha),(push,push_sha)]:assert sha(p)==h
e=json.loads(body(Path(proposal)));g=json.loads(body(Path(gate)));p=json.loads(body(Path(push)))
assert g['decision'].startswith('ACCEPT') and g['replacementBetter'] and g['oldLooseCopiesNoLongerNeeded']
assert g['method']['sha256']==sha(Path(__file__)) and g['proposal']['sha256']==proposal_sha
assert g['currentHold']['sha256']==sha(R/'AGENTS.md')
judged=json.loads(body(Path(judgment)));assert judged['decision']=='AUTHORIZE_EXACT_FOUR_ARCHIVED_RAW_RETIREMENTS_ONCE'
assert judged['proposalSHA256']==proposal_sha and judged['gateSHA256']==gate_sha and judged['methodSHA256']==sha(Path(__file__)) and judged['pushSHA256']==push_sha
assert p['confirmed'] and p['clean'] and p['gateSHA256']==gate_sha and p['methodSHA256']==sha(Path(__file__))
assert judged['commit']==p['commit']
assert judged['callerGateSHA256']==p['callerGateSHA256']==sha(S/'target-clear-default-caller-independent-r1/GATE.json')=='36ddead7bcd9647706f33c766952732dc3ff7b42455f2c678b125569bde2c31a'
assert body(R/'.git/refs/heads/codex/lanternbound-production').decode().strip()==p['commit']
q=subprocess.run(['git','status','--porcelain'],cwd=R,text=True,capture_output=True,timeout=10);assert q.returncode==0 and not q.stdout
published=R/'reviews/four-archived-json-retirement-2026-10-02'
assert body(published/'independent/GATE.json')==body(Path(gate))
assert body(published/'root-controls'/Path(__file__).name)==body(Path(__file__))
bundle=p['supportBundle'];assert bundle['roundtripExact'] and Path(bundle['path'])==published/'source-support.tar.gz'
assert sha(published/'source-support.tar.gz')==bundle['sha256']
assert json.loads(body(published/'SUPPORT-BUNDLE.json'))==bundle
assert sha(published/'previous-R3-POST-GATE.json')==p['priorPostGateSHA256']=='2e8735abe975b28e42a1ce9d3a178ad6db9c251ca4f1de6acee3a979a361ec97'
fd=os.open(published/'source-support.tar.gz',os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW)
with os.fdopen(fd,'rb') as f,tarfile.open(fileobj=f,mode='r|gz') as tar:
 m=next(iter(tar));assert m.name=='MANIFEST.json' and m.isfile() and m.size<1048576
 assert hashlib.sha256(tar.extractfile(m).read()).hexdigest()==bundle['manifestSHA256']
initial_free=os.statvfs(R).f_bavail*os.statvfs(R).f_frsize;assert initial_free>=64*1048576
cg=Path('/sys/fs/cgroup');assert int((cg/'memory.max').read_text())-int((cg/'memory.current').read_text())>=576*1048576
selected_path=S/'target-clear-ghost-promotion-root-r3/RESULT.json'
assert sha(selected_path)==e['selectedMap']['sha256']==g['selectedMap']['sha256']
selected=json.loads(body(selected_path))
def selected_exact():
 assert len(selected[e['selectedMap']['inputKey']])==88 and len(selected[e['selectedMap']['outputKey']])==56
 for rel,h in selected[e['selectedMap']['inputKey']].items():assert sha(R/rel)==h,rel
 for rel,h in selected[e['selectedMap']['outputKey']].items():assert sha(R/'dist'/rel)==h,rel
selected_exact()
protected=S/'retained-original-archives/preflight-bdf273-original-r4.zip';protected_before=md(os.stat(protected,follow_symlinks=False))
assert (protected_before['st_dev'],protected_before['st_ino'],protected_before['st_size'],protected_before['st_nlink'])==(27,678628,1856041104,1)
raw=e['rawFiles'];caps=e['capsules']
allowed={str(S/root/name) for root in ['target-wait-default-comparison-actual-r1','target-clear-ghost-comparison-actual-r1'] for name in ['VISUAL-RESULT.json','VISUAL-PROGRESS.json']}
assert len(raw)==4 and {x['path'] for x in raw}==allowed
assert all(x['fstat']['st_dev']==27 and x['fstat']['st_nlink']==1 and not x['xattrs'] for x in raw)
fixed={str(R/'reviews/opening-default-wait-cue-2026-10-02/evidence.tar.gz'):('dd9003b676ae49b8a81441f73dfaec51b4309206a3ce32716cb2c8c1fcda169f','bfc53a7026de9e48aeeac0c8e162577c7ee93e255b4205424a364083428a1849'),str(R/'reviews/opening-target-clear-rejected-2026-10-02/evidence.tar.gz'):('0871ec41c94e39313eb132aa1296385e3e6461e7be0a03e9ef333e4d8453b8a3','c061f51137513fb0bb3553aa6e7d76b6750a2f4abe3a50aa2dea53fddc9e9181')}
assert len(caps)==2 and {c['capsule']['path'] for c in caps}==set(fixed)
handles={}
def verify_capsule(c):
 x=c['capsule'];path=Path(x['path']);fd=handles[x['path']][2]
 check(fd,path.name,x['currentMetadata'],x['sha256'])
 assert (x['sha256'],c['manifestSHA256'])==fixed[x['path']]
 assert sha(Path(c['independentGATE']['path']))==c['independentGATE']['sha256']
 mappings=c['exactLogicalMapping'];assert len(mappings)==2
 assert {v['originalPath'] for v in mappings}<={v['path'] for v in raw}
 wanted={'blobs/'+v['entry']['sha256']:v['entry'] for v in mappings};found={};manifest=None;count=0
 f=os.open(path.name,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW,dir_fd=fd)
 try:
  assert md(os.fstat(f))==x['currentMetadata']
  with os.fdopen(os.dup(f),'rb') as stream,tarfile.open(fileobj=stream,mode='r|gz') as tar:
   for m in tar:
    count+=1;assert count<800
    if m.name=='MANIFEST.json':
     assert manifest is None and m.isfile() and m.size<1048576
     v=tar.extractfile(m).read();assert hashlib.sha256(v).hexdigest()==c['manifestSHA256'];manifest=json.loads(v)
    if m.name in wanted:
     assert m.isfile() and m.name not in found
     with tar.extractfile(m) as body:found[m.name]={'sha256':digest(body),'bytes':m.size}
  assert manifest is not None and set(found)==set(wanted)
  for member,v in wanted.items():assert found[member]=={'sha256':v['sha256'],'bytes':v['bytes']}
  for mapping in mappings:
   entry=mapping['entry'];assert manifest['logicalBodies'][entry['logicalPath']]=={k:entry[k] for k in ('originalPath','bytes','sha256')}
   assert entry['originalPath']==mapping['originalPath']
   v=next(v for v in raw if v['path']==mapping['originalPath']);assert (v['sha256'],v['bytes'])==(entry['sha256'],entry['bytes'])
  assert md(os.fstat(f))==x['currentMetadata']
 finally:os.close(f)
 check(fd,path.name,x['currentMetadata'],x['sha256'])
try:
 for x in [*(c['capsule'] for c in caps),*raw]:
  path=Path(x['path']);fd=parentfd(path);handles[x['path']]=(x,path,fd)
  fresh=md(os.stat(path.name,dir_fd=fd,follow_symlinks=False))
  assert all(fresh[k]==v for k,v in x['fstat'].items() if k!='st_atime_ns')
  x['proposalMetadata']=x['fstat'].copy();x['currentMetadata']=fresh
  check(fd,path.name,fresh,x['sha256'])
 assert {v['originalPath'] for c in caps for v in c['exactLogicalMapping']}==allowed
 for c in caps:verify_capsule(c)
 P=S/'four-archived-json-retirement-actual-root-r2';P.mkdir();ancestor=parentfd(P)
 try:syncfd(ancestor)
 finally:os.close(ancestor)
 save(P/'BEFORE.json',{'rawFiles':raw,'capsules':caps,'initialFree':initial_free,'proposalSHA256':proposal_sha,'gateSHA256':gate_sha,'judgmentSHA256':judgment_sha,'pushSHA256':push_sha,'protectedZIPStat':protected_before})
 save(P/'PRODUCER.json',judged)
 for x in raw:
  path=Path(x['path']);fd=handles[x['path']][2]
  check(fd,path.name,x['currentMetadata'],x['sha256'])
  for c in caps:verify_capsule(c)
  def journal(operation):
   with (P/'JOURNAL.jsonl').open('a') as f:f.write(json.dumps({'utcNs':time.time_ns(),'operation':operation,'path':str(path),'sha256':x['sha256']})+'\n');f.flush();os.fsync(f.fileno())
   packetfd=parentfd(P/'JOURNAL.jsonl')
   try:syncfd(packetfd)
   finally:os.close(packetfd)
  journal('PRE_UNLINK');os.unlink(path.name,dir_fd=fd);syncfd(fd);journal('UNLINK_DURABLE')
  try:os.stat(path.name,dir_fd=fd,follow_symlinks=False);raise AssertionError('retired path still exists')
  except FileNotFoundError:pass
 for c in caps:verify_capsule(c)
 selected_exact();assert md(os.stat(protected,follow_symlinks=False))==protected_before
 final_free=os.statvfs(R).f_bavail*os.statvfs(R).f_frsize
 save(P/'RESULT.json',{'normal':True,'retiredPaths':[x['path'] for x in raw],'preservedBodies':[x['sha256'] for x in raw],'capsuleSHA256s':[c['capsule']['sha256'] for c in caps],'grossAllocationBytes':sum(x['fstat']['st_blocks']*512 for x in raw),'windowFreeBefore':initial_free,'windowFreeAfterBeforeResultWrite':final_free,'netWindowGainBytes':final_free-initial_free,'capsulesAndCurrent88_56Exact':True,'protectedZIPBefore':protected_before,'protectedZIPAfter':md(os.stat(protected,follow_symlinks=False)),'protectedOriginalStatExact':True,'noOtherAction':True})
 print(json.dumps({'normal':True,'freeBeforeResultWrite':final_free,'netWindowGain':final_free-initial_free}))
finally:
 for x,path,fd in handles.values():os.close(fd)
