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
assert proposal==str(S/'r3-two-raw-retirement-source-author-r1/PROPOSAL.json')
assert gate==str(S/'r3-two-raw-retirement-independent-r1/GATE.json') and judgment==str(S/'r3-two-raw-retirement-producer-root-r1.json')
assert push==str(S/'r3-two-raw-retirement-push-root-r1/PUSH-CONFIRMED.json')
for p,h in [(proposal,proposal_sha),(gate,gate_sha),(judgment,judgment_sha),(push,push_sha)]:assert sha(p)==h
e=json.loads(Path(proposal).read_text());g=json.loads(Path(gate).read_text());p=json.loads(Path(push).read_text())
assert g['decision'].startswith('ACCEPT') and g['replacementBetter'] and g['oldLooseCopiesNoLongerNeeded']
assert g['method']['sha256']==sha(Path(__file__)) and g['proposal']['sha256']==proposal_sha
assert g['currentHold']['sha256']==sha(R/'AGENTS.md')
judged=json.loads(Path(judgment).read_text());assert judged['decision']=='AUTHORIZE_EXACT_TWO_R3_RAW_RETIREMENTS_ONCE'
assert judged['proposalSHA256']==proposal_sha and judged['gateSHA256']==gate_sha and judged['methodSHA256']==sha(Path(__file__)) and judged['pushSHA256']==push_sha
assert p['confirmed'] and p['clean'] and p['gateSHA256']==gate_sha and p['methodSHA256']==sha(Path(__file__))
assert judged['commit']==p['commit']
assert judged['callerGateSHA256']==p['callerGateSHA256']==sha(S/'target-clear-default-caller-independent-r1/GATE.json')=='36ddead7bcd9647706f33c766952732dc3ff7b42455f2c678b125569bde2c31a'
assert (R/'.git/refs/heads/codex/lanternbound-production').read_text().strip()==p['commit']
q=subprocess.run(['git','status','--porcelain'],cwd=R,text=True,capture_output=True,timeout=10);assert q.returncode==0 and not q.stdout
published=R/'reviews/r3-two-archived-json-retirement-2026-10-02'
assert (published/'independent/GATE.json').read_bytes()==Path(gate).read_bytes()
assert (published/'root-controls'/Path(__file__).name).read_bytes()==Path(__file__).read_bytes()
initial_free=os.statvfs(R).f_bavail*os.statvfs(R).f_frsize;assert initial_free>=64*1048576
cg=Path('/sys/fs/cgroup');assert int((cg/'memory.max').read_text())-int((cg/'memory.current').read_text())>=576*1048576
selected_path=S/'target-clear-ghost-promotion-root-r3/RESULT.json'
assert sha(selected_path)==e['selectedMap']['sha256']==g['selectedMap']['sha256']
selected=json.loads(selected_path.read_text())
def selected_exact():
 assert len(selected[e['selectedMap']['inputKey']])==88 and len(selected[e['selectedMap']['outputKey']])==56
 for rel,h in selected[e['selectedMap']['inputKey']].items():assert sha(R/rel)==h,rel
 for rel,h in selected[e['selectedMap']['outputKey']].items():assert sha(R/'dist'/rel)==h,rel
selected_exact()
protected=S/'retained-original-archives/preflight-bdf273-original-r4.zip';protected_before=md(os.stat(protected,follow_symlinks=False))
assert (protected_before['st_dev'],protected_before['st_ino'],protected_before['st_size'],protected_before['st_nlink'])==(27,678628,1856041104,1)
raw=e['rawFiles'];root=S/'target-clear-ghost-comparison-actual-r3'
assert len(raw)==2 and {Path(x['path']).name for x in raw}=={'VISUAL-RESULT.json','VISUAL-PROGRESS.json'}
assert all(Path(x['path']).parent==root and x['fstat']['st_dev']==27 and x['fstat']['st_nlink']==1 for x in raw)
capsule=e['capsule'];cp=Path(capsule['path'])
assert cp==R/'reviews/opening-target-clear-ghost-opt-in-2026-10-02/evidence-0f6cec73b283cffd830f57d60a37edde43d1670e814d18a33eeb54d05afc37fa.tar.gz'
assert capsule['sha256']=='0f6cec73b283cffd830f57d60a37edde43d1670e814d18a33eeb54d05afc37fa'
assert e['manifestSHA256']=='38e3cd6de37f9bbc8bbc59f7b3222c0d6774eaee55bd2862c6111e53588b62ba'
assert sha(Path(e['independentCompleteGate']['path']))==e['independentCompleteGate']['sha256']=='6ec96568886fbeede7c9abacd6365edffa9cb4a7401c9d143ca50a281fd6ac65'
handles=[]
try:
 for x in [capsule,*raw]:
  path=Path(x['path']);fd=parentfd(path);handles.append((x,path,fd));fresh=md(os.stat(path.name,dir_fd=fd,follow_symlinks=False))
  assert all(fresh[k]==v for k,v in x['fstat'].items() if k!='st_atime_ns')
  x['proposalMetadata']=x['fstat'].copy();x['currentMetadata']=fresh
  check(fd,path.name,fresh,x['sha256'])
 capsule_fd=os.open(cp.name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME,dir_fd=handles[0][2])
 try:
  assert md(os.fstat(capsule_fd))==capsule['currentMetadata'];found={};manifest=None;count=0
  with os.fdopen(os.dup(capsule_fd),'rb') as stream,tarfile.open(fileobj=stream,mode='r|gz') as tar:
   for m in tar:
    count+=1;assert count<=800
    if m.name=='MANIFEST.json':
     assert m.isfile() and m.size<1048576;v=tar.extractfile(m).read();assert hashlib.sha256(v).hexdigest()==e['manifestSHA256'];manifest=json.loads(v)
    if m.name in {'blobs/'+x['sha256'] for x in raw}:
     assert m.isfile() and m.name not in found;stream_body=tar.extractfile(m)
     with stream_body:found[m.name]={'sha256':digest(stream_body),'bytes':m.size}
  assert manifest is not None and len(found)==2
  for x in raw:assert found['blobs/'+x['sha256']]=={'sha256':x['sha256'],'bytes':x['bytes']}
  for mapping in e['exactLogicalMapping']:
   assert mapping['originalPath'] in {x['path'] for x in raw} and mapping['blobMember']=='blobs/'+mapping['sha256']
   entries=[{'originalPath':str(Path(manifest['roots'][row[0]])/row[1]),'path':row[0]+'/'+row[1],'sha256':row[3],'bytes':row[2]} for row in manifest['rows'] if str(Path(manifest['roots'][row[0]])/row[1])==mapping['originalPath']]
   assert len(entries)==1 and entries[0]['path']==mapping['logicalPath']
   assert (entries[0]['sha256'],entries[0]['bytes'])==(mapping['sha256'],mapping['bytes'])
  assert len(e['exactLogicalMapping'])==2 and {x['originalPath'] for x in e['exactLogicalMapping']}=={x['path'] for x in raw}
  assert md(os.fstat(capsule_fd))==capsule['currentMetadata']
 finally:os.close(capsule_fd)
 P=S/'r3-two-archived-json-retirement-actual-root-r1';P.mkdir();ancestor=parentfd(P)
 try:syncfd(ancestor)
 finally:os.close(ancestor)
 save(P/'BEFORE.json',{'rawFiles':raw,'capsule':capsule,'initialFree':initial_free,'proposalSHA256':proposal_sha,'gateSHA256':gate_sha,'judgmentSHA256':judgment_sha,'pushSHA256':push_sha,'protectedZIPStat':protected_before})
 save(P/'PRODUCER.json',judged)
 for x,path,fd in handles[1:]:
  check(fd,path.name,x['currentMetadata'],x['sha256']);check(handles[0][2],cp.name,capsule['currentMetadata'],capsule['sha256'])
  def journal(operation):
   with (P/'JOURNAL.jsonl').open('a') as f:f.write(json.dumps({'utcNs':time.time_ns(),'operation':operation,'path':str(path),'sha256':x['sha256']})+'\n');f.flush();os.fsync(f.fileno())
   packetfd=parentfd(P/'JOURNAL.jsonl')
   try:syncfd(packetfd)
   finally:os.close(packetfd)
  journal('PRE_UNLINK');os.unlink(path.name,dir_fd=fd);syncfd(fd);journal('UNLINK_DURABLE')
  try:os.stat(path.name,dir_fd=fd,follow_symlinks=False);raise AssertionError('retired path still exists')
  except FileNotFoundError:pass
 check(handles[0][2],cp.name,capsule['currentMetadata'],capsule['sha256']);selected_exact();assert md(os.stat(protected,follow_symlinks=False))==protected_before
 final_free=os.statvfs(R).f_bavail*os.statvfs(R).f_frsize
 save(P/'RESULT.json',{'normal':True,'retiredPaths':[x['path'] for x in raw],'preservedBodies':[x['sha256'] for x in raw],'capsuleSHA256':capsule['sha256'],'grossAllocationBytes':sum(x['fstat']['st_blocks']*512 for x in raw),'windowFreeBefore':initial_free,'windowFreeAfterBeforeResultWrite':final_free,'netWindowGainBytes':final_free-initial_free,'capsuleAndCurrent88_56Exact':True,'protectedZIPBefore':protected_before,'protectedZIPAfter':md(os.stat(protected,follow_symlinks=False)),'protectedOriginalStatExact':True,'noOtherAction':True})
 print(json.dumps({'normal':True,'freeBeforeResultWrite':final_free,'netWindowGain':final_free-initial_free}))
finally:
 for x,path,fd in handles:os.close(fd)
