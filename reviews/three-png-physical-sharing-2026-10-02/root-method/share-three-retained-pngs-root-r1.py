from pathlib import Path
import os,json,hashlib,time,sys,subprocess,stat
S=Path('/workspace/scratch');R=Path('/workspace/Roguelike-deckbuilder')
proposal,proposal_sha,gate,gate_sha,judgment,judgment_sha,push,push_sha=sys.argv[1:]
def sha(p):
 h=hashlib.sha256();fd=os.open(p,os.O_RDONLY|os.O_NOATIME)
 with os.fdopen(fd,'rb') as f:
  for b in iter(lambda:f.read(65536),b''):h.update(b)
 return h.hexdigest()
def read(p):return json.loads(Path(p).read_text())
def meta(p):
 t=os.stat(p);return {k:getattr(t,k) for k in ['st_dev','st_ino','st_mode','st_nlink','st_uid','st_gid','st_size','st_blocks','st_atime_ns','st_mtime_ns','st_ctime_ns']}
def syncdir(p):
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY)
 try:os.fsync(fd)
 finally:os.close(fd)
def save(p,j):
 with p.open('x') as f:json.dump(j,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 syncdir(p.parent)
for p,h in [(proposal,proposal_sha),(gate,gate_sha),(judgment,judgment_sha),(push,push_sha)]:assert sha(p)==h,p
j=read(judgment);assert j['decision']=='AUTHORIZE_EXACT_THREE_PATH_PHYSICAL_SHARING_ONCE' and j['proposalSHA256']==proposal_sha and j['independentGateSHA256']==gate_sha
assert read(gate)['decision'].startswith('ACCEPT')
pushed=read(push);assert pushed['confirmed'] and pushed['clean'] and pushed['commit']==j['commit']
assert (R/'.git/refs/heads/codex/lanternbound-production').read_text().strip()==j['commit']
status=subprocess.run(['git','status','--porcelain'],cwd=R,text=True,capture_output=True,timeout=10);assert status.returncode==0 and not status.stdout,status.stdout
v=os.statvfs(R);initial_free=v.f_bavail*v.f_frsize;assert initial_free>=64*1048576
cg=Path('/sys/fs/cgroup');assert int((cg/'memory.max').read_text())-int((cg/'memory.current').read_text())>=576*1048576
E=read(proposal);pairs=E['pairs'];assert len(pairs)==3 and E['verification']=='EXACT_MATCH'
names={'abbey-courtyard.png','tool-vignettes.png','hunter-portrait.png'};assert {Path(x['candidate']['path']).name for x in pairs}==names
oldroot=S/'audio-host-independent-v08/candidate/dist/art';anchors=R/'public/art'
for x in pairs:
 a=x['canonical'];b=x['candidate'];ap=Path(a['path']);bp=Path(b['path']);assert ap.parent==anchors and bp.parent==oldroot and ap.name==bp.name
 assert not ap.is_symlink() and not bp.is_symlink() and stat.S_ISREG(ap.stat().st_mode) and stat.S_ISREG(bp.stat().st_mode)
 assert meta(ap)==a['metadata'] and meta(bp)==b['metadata'];assert b['metadata']['st_nlink']==1 and a['metadata']['st_dev']==b['metadata']['st_dev']==27
 assert not os.listxattr(ap) and not os.listxattr(bp);assert sha(ap)==sha(bp)==a['sha256']==b['sha256'];assert not bp.with_name(bp.name+'.root-share-r1.tmp').exists()
# The separately reviewed proposal retains full original metadata and consumer/alias coverage.
P=S/'three-retained-png-sharing-actual-root-r1';P.mkdir();syncdir(P.parent)
save(P/'BEFORE.json',{'utcNs':time.time_ns(),'pairs':pairs,'initialFree':initial_free,'proposalSHA256':proposal_sha,'gateSHA256':gate_sha,'judgmentSHA256':judgment_sha,'pushSHA256':push_sha,'commit':j['commit']})
log=P/'JOURNAL.jsonl'
def journal(entry):
 with log.open('a') as f:f.write(json.dumps({'utcNs':time.time_ns(),**entry})+'\n');f.flush();os.fsync(f.fileno())
 syncdir(P)
for x in pairs:
 ap=Path(x['canonical']['path']);bp=Path(x['candidate']['path']);tmp=bp.with_name(bp.name+'.root-share-r1.tmp')
 journal({'operation':'PRE_LINK','source':str(ap),'target':str(bp),'temp':str(tmp)})
 os.link(ap,tmp);syncdir(bp.parent);journal({'operation':'LINK_DURABLE','target':str(bp),'temp':str(tmp)})
 os.replace(tmp,bp);syncdir(bp.parent);journal({'operation':'REPLACED_DURABLE','target':str(bp),'tempAbsent':not tmp.exists()})
 assert sha(ap)==sha(bp)==x['canonical']['sha256'];assert meta(ap)['st_ino']==meta(bp)['st_ino']
final_free=os.statvfs(R).f_bavail*os.statvfs(R).f_frsize
result={'normal':True,'pairs':[{'candidate':x['candidate']['path'],'canonical':x['canonical']['path'],'sha256':sha(x['candidate']['path']),'candidateMetadata':meta(x['candidate']['path']),'canonicalMetadata':meta(x['canonical']['path'])} for x in pairs],'grossAllocationBytes':sum(x['candidate']['metadata']['st_blocks']*512 for x in pairs),'windowFreeBefore':initial_free,'windowFreeAfterBeforeResultWrite':final_free,'netWindowGainBytes':final_free-initial_free,'allPathsBodiesKept':True,'allTempAbsent':all(not Path(x['candidate']['path']+'.root-share-r1.tmp').exists() for x in pairs),'losses':'Three original private inodes/time metadata and write isolation replaced by exact held canonical bodies. Anchors/known aliases gain one link and ctime changes. Original stats/provenance retained; no OS-enforced read-only claim or all-path power-loss atomicity.','noOtherActionAuthorized':True}
save(P/'RESULT.json',result);print(json.dumps({'normal':True,'gross':result['grossAllocationBytes'],'netWindowGain':result['netWindowGainBytes'],'freeBeforeResultWrite':final_free}))
