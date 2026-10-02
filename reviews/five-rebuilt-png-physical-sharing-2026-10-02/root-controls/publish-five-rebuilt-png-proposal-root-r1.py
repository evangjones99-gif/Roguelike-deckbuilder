from pathlib import Path
import os,json,hashlib,subprocess,time,sys,stat
S=Path('/workspace/scratch');R=Path('/workspace/Roguelike-deckbuilder');M=Path(__file__).parent
D=R/'reviews/five-rebuilt-png-physical-sharing-2026-10-02';P=S/'five-rebuilt-png-proposal-push-root-r1'
R3=R/'reviews/opening-target-clear-ghost-opt-in-2026-10-02'
R3_ARCHIVE=R3/'evidence-0f6cec73b283cffd830f57d60a37edde43d1670e814d18a33eeb54d05afc37fa.tar.gz'
R3_GATE=S/'target-clear-ghost-preservation-independent-r1/GATE.json'
R3_GATE_SHA='6ec96568886fbeede7c9abacd6365edffa9cb4a7401c9d143ca50a281fd6ac65'
EXPECTED_HEAD='cec3e628dc0dc71c4a2d3139728eae309d7f492e'
EXPECTED_PROPOSAL='371c1e2df47f30e4abca9abece46864b53f4fb6f25e9a78926ee98a0d7a054c5'
EXPECTED_HOLD='6f76b3a724bcf4cd9db8587158a8bd454531c8a8b59fc8680bf7661d896ee2d8'
COPY_CAP=512*1024;DISK_MIN=64*1048576+3*1048576
def sha(p):
 h=hashlib.sha256();fd=os.open(p,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW)
 with os.fdopen(fd,'rb') as f:
  for b in iter(lambda:f.read(65536),b''):h.update(b)
 return h.hexdigest()
def read(p):
 fd=os.open(p,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW)
 with os.fdopen(fd,'r') as f:return json.load(f)
def md(s):return {k:getattr(s,k) for k in ['st_dev','st_ino','st_mode','st_nlink','st_uid','st_gid','st_size','st_blocks','st_atime_ns','st_mtime_ns','st_ctime_ns']}
def syncdir(p):
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
 try:os.fsync(fd)
 finally:os.close(fd)
def object_snapshot():
 rows={};todo=[R/'.git/objects'];count=0
 while todo:
  here=todo.pop();fd=os.open(here,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_NOATIME)
  try:
   with os.scandir(fd) as it:entries=[(e.name,e.stat(follow_symlinks=False)) for e in it]
  finally:os.close(fd)
  for name,s in entries:
   count+=1;assert count<100000
   p=here/name;assert not stat.S_ISLNK(s.st_mode)
   if stat.S_ISDIR(s.st_mode):todo.append(p)
   else:assert stat.S_ISREG(s.st_mode);rows[str(p.relative_to(R/'.git/objects'))]=(s.st_size,s.st_blocks*512)
 return rows
gate=S/'five-rebuilt-png-sharing-independent-r1/GATE.json';proposal=S/'five-rebuilt-png-recovery-proposal-r1/PROPOSAL.json'
assert len(sys.argv)==2 and sha(gate)==sys.argv[1]
g=read(gate);assert g['decision'].startswith('ACCEPT') and g['proposal']['sha256']==EXPECTED_PROPOSAL==sha(proposal)
method=M/'share-five-rebuilt-pngs-root-r1.py';assert sha(method)==g['method']['sha256']
assert sha(R/'AGENTS.md')==EXPECTED_HOLD==g['currentHold']['sha256']
assert sha(S/'target-wait-default-promotion-root-r1/RESULT.json')==g['selectedMap']['sha256']=='31a221091d2ffbc6d58dfc1385962c441df9789c66729ef64d20b95208a8fabd'
assert not D.exists() and not P.exists() and R3.is_dir() and not R3.is_symlink()
assert R3_ARCHIVE.is_file() and not R3_ARCHIVE.is_symlink() and os.lstat(R3_ARCHIVE).st_size==1981882
assert sha(R3/'PRESERVATION.json')=='b33053ab9a070a4f8da8b059cf984256eb204a4c2de690b4ff794b622334a046'
assert sha(R3_GATE)==R3_GATE_SHA and read(R3_GATE)['decision'].startswith('ACCEPT')
# Existing R3 archive is committed in place, never opened/copied by this Python publisher.
plan=[]
def walk(root,relative=Path('.')):
 here=root/relative;fd=os.open(here,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_NOATIME)
 try:
  with os.scandir(fd) as it:entries=sorted((e.name,e.stat(follow_symlinks=False)) for e in it)
 finally:os.close(fd)
 for name,s in entries:
  rel=relative/name
  assert not stat.S_ISLNK(s.st_mode)
  if stat.S_ISDIR(s.st_mode):yield from walk(root,rel)
  else:assert stat.S_ISREG(s.st_mode);yield root/rel,rel,s
for folder in ['five-rebuilt-png-recovery-proposal-r1','five-rebuilt-png-sharing-independent-r1','five-png-sharing-post-independent-r2']:
 for source,relative,s in walk(S/folder):plan.append((source,D/folder/relative,s))
for name in ['share-five-rebuilt-pngs-root-r1.py','publish-five-rebuilt-png-proposal-root-r1.py','judge-five-rebuilt-png-sharing-root-r1.py']:
 a=M/name;plan.append((a,D/'root-controls'/name,os.lstat(a)))
plan.append((R3_GATE,D/'root-controls/R3-PRESERVATION-COMPLETE-GATE.json',os.lstat(R3_GATE)))
for name in ['BEFORE.json','JOURNAL.jsonl','RESULT.json']:
 a=S/'five-retained-png-sharing-actual-root-r2'/name;plan.append((a,D/'previous-first-five-actual'/name,os.lstat(a)))
for a,b in [(S/'five-png-producer-judgment-root-r2.json',D/'previous-first-five-controls/PRODUCER-JUDGMENT.json'),(S/'five-png-recovery-push-root-r1/PUSH-CONFIRMED.json',D/'previous-first-five-controls/PUSH-CONFIRMED.json')]:plan.append((a,b,os.lstat(a)))
copied=sum(s.st_size for a,b,s in plan);assert copied<COPY_CAP
assert all(stat.S_ISREG(s.st_mode) and s.st_size<262144 for a,b,s in plan)
assert len({str(b) for a,b,s in plan})==len(plan)
readme='''# Rebuilt five PNGs: exact physical sharing proposal

This separately reviewed proposal preserves five immutable historical independently rebuilt media paths and exact bodies while replacing private encodings with held canonical anchors. Source/build/rebuild records, rights/provenance, findings and useful rollback stay. Private inode/time/write isolation would be surrendered; each anchor nlink/ctime changes, including qualified unknown aliases. Fresh-stage holds are coordinated workflow protection, not OS enforcement. Current push and explicit producer judgment must precede Root action. No action, art improvement or R3 default promotion is claimed here.

The exact previous first-five completed POST and three actual controls plus producer/push receipts are preserved alongside this second proposal, independent gate and three method sources. The complete existing R3 opt-in comparison capsule is committed in place separately; no R3 archive/media body is opened or recopied by this Python publisher. All earlier reviews and protected archives stay untouched.
'''
# Preflight generated identity overhead as well as copy bodies before any destination writes.
estimated={str(b.relative_to(D)):{'originalPath':str(a),'bytes':s.st_size,'sha256':'0'*64,'sourceMetadata':md(s)} for a,b,s in plan}
assert copied+len((json.dumps(estimated,indent=2)+'\n').encode())+len(readme.encode())<COPY_CAP
free_before=os.statvfs(R).f_bavail*os.statvfs(R).f_frsize;assert free_before>=DISK_MIN
objects_before=object_snapshot()
P.mkdir();syncdir(P.parent)
def run(args):
 q=subprocess.run(args,cwd=R,text=True,capture_output=True,timeout=55)
 with (P/'COMMANDS.jsonl').open('a') as f:f.write(json.dumps({'args':args,'rc':q.returncode,'stdout':q.stdout,'stderr':q.stderr,'utcNs':time.time_ns()})+'\n');f.flush();os.fsync(f.fileno())
 assert q.returncode==0,(args,q.stderr)
 return q.stdout.rstrip('\n')
assert run(['git','rev-parse','HEAD'])==EXPECTED_HEAD
owned=str(D.relative_to(R));r3owned=str(R3.relative_to(R))
for line in run(['git','status','--porcelain','--untracked-files=all']).splitlines():assert line[3:]=='AGENTS.md' or line[3:].startswith(owned+'/') or line[3:].startswith(r3owned+'/'),line
D.mkdir();records={}
for source,target,expected in plan:
 assert md(os.lstat(source))==md(expected) and not target.exists();target.parent.mkdir(parents=True,exist_ok=True)
 fd=os.open(source,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME)
 with os.fdopen(fd,'rb') as f:
  assert md(os.fstat(f.fileno()))==md(expected);v=f.read(262145)
  assert len(v)==expected.st_size and md(os.fstat(f.fileno()))==md(expected)
 assert md(os.lstat(source))==md(expected)
 dest=os.open(target,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
 with os.fdopen(dest,'wb') as out:out.write(v);out.flush();os.fsync(out.fileno())
 h=hashlib.sha256(v).hexdigest();assert sha(target)==h
 records[str(target.relative_to(D))]={'originalPath':str(source),'bytes':len(v),'sha256':h,'sourceMetadata':md(expected)}
identity=(json.dumps(records,indent=2)+'\n').encode();publication_bytes=copied+len(identity)+len(readme.encode());assert publication_bytes<COPY_CAP
for target,body in [(D/'COPY-IDENTITIES.json',identity),(D/'README.md',readme.encode())]:
 fd=os.open(target,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
 with os.fdopen(fd,'wb') as out:out.write(body);out.flush();os.fsync(out.fileno())
syncdir(D)
run(['git','add','-f','--',owned,r3owned,'AGENTS.md'])
run(['git','-c','gc.auto=0','commit','-m','Preserve opt-in ghost evidence and reviewed rebuilt-media sharing proposal'])
head=run(['git','rev-parse','HEAD']);run(['git','-c','gc.auto=0','push','origin','HEAD:codex/lanternbound-production']);remote=run(['git','ls-remote','origin','refs/heads/codex/lanternbound-production']).split()[0]
assert remote==head and not run(['git','status','--porcelain'])
objects_after=object_snapshot();added=set(objects_after)-set(objects_before)
object_receipt={'beforeLogicalBytes':sum(v[0] for v in objects_before.values()),'afterLogicalBytes':sum(v[0] for v in objects_after.values()),'beforeAllocatedBytes':sum(v[1] for v in objects_before.values()),'afterAllocatedBytes':sum(v[1] for v in objects_after.values()),'newObjectFiles':len(added),'newObjectLogicalBytes':sum(objects_after[k][0] for k in added),'newObjectAllocatedBytes':sum(objects_after[k][1] for k in added),'metadataOnlyNoObjectBodyReads':True}
free_before_receipt=os.statvfs(R).f_bavail*os.statvfs(R).f_frsize
with (P/'PUSH-CONFIRMED.json').open('x') as f:json.dump({'commit':head,'remote':remote,'confirmed':True,'clean':True,'gateSHA256':sha(gate),'methodSHA256':sha(method),'proposalSHA256':EXPECTED_PROPOSAL,'holdSHA256':sha(R/'AGENTS.md'),'R3CompleteGateSHA256':R3_GATE_SHA,'R3PreservationSHA256':sha(R3/'PRESERVATION.json'),'copiedBytes':copied,'newPublicationBytes':publication_bytes,'existingR3ArchiveNotCopiedOrOpenedByPython':True,'initialFree':free_before,'diskAdmissionBytes':DISK_MIN,'diskEstimate':'64MiB floor plus3MiB total: at most512KiB source copies and2.5MiB estimated Git objects for existing1,981,882B gzip and bounded compressible text. Estimate is not an OS size limit or guaranteed cost; ordinary guard/live floor and build/native thresholds unchanged.','gitObjects':object_receipt,'finalFreeBeforeReceiptWrite':free_before_receipt,'noStorageAction':True,'durableReceiptFileAndParentFsync':True},f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
syncdir(P)
print(json.dumps({'commit':head,'confirmed':True,'clean':True,'copiedBytes':copied,'newPublicationBytes':publication_bytes,'gitObjects':object_receipt,'freeAfterReceiptWrite':os.statvfs(R).f_bavail*os.statvfs(R).f_frsize}))
