import os,json,hashlib,tarfile,stat,resource
from pathlib import Path
resource.setrlimit(resource.RLIMIT_DATA,(24*1048576,24*1048576))
P=Path(__file__).parent;R=Path('/workspace/Roguelike-deckbuilder');S=Path('/workspace/scratch')
RAW=S/'target-clear-ghost-comparison-actual-r3';CP=R/'reviews/opening-target-clear-ghost-opt-in-2026-10-02/evidence-0f6cec73b283cffd830f57d60a37edde43d1670e814d18a33eeb54d05afc37fa.tar.gz'
CS='0f6cec73b283cffd830f57d60a37edde43d1670e814d18a33eeb54d05afc37fa';MS='38e3cd6de37f9bbc8bbc59f7b3222c0d6774eaee55bd2862c6111e53588b62ba'
parents={}
def md(s):return {k:getattr(s,k) for k in ['st_dev','st_ino','st_mode','st_nlink','st_uid','st_gid','st_size','st_blocks','st_atime_ns','st_mtime_ns','st_ctime_ns']}
def op(path):
 path=Path(path);f=os.open('/',os.O_PATH|os.O_DIRECTORY|os.O_NOFOLLOW);cur=''
 try:
  for part in path.parent.parts[1:]:
   q=os.open(part,os.O_PATH|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=f);os.close(f);f=q;cur+='/'+part
   if cur not in parents:parents[cur]={'metadata':md(os.fstat(f)),'xattrs':{n:os.getxattr('/proc/self/fd/'+str(f),n).hex() for n in os.listxattr('/proc/self/fd/'+str(f))}}
  return os.open(path.name,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW,dir_fd=f)
 finally:os.close(f)
def pin(path,keep=False):
 path=Path(path);before=md(os.lstat(path));f=op(path);assert before==md(os.fstat(f)) and stat.S_ISREG(before['st_mode']);xattrs={n:os.getxattr(f,n).hex() for n in os.listxattr(f)};h=hashlib.sha256();n=0;chunks=[]
 while True:
  b=os.read(f,65536)
  if not b:break
  h.update(b);n+=len(b)
  if keep:chunks.append(b);assert n<262144
 assert before==md(os.fstat(f));os.close(f);assert before==md(os.lstat(path))
 p={'path':str(path),'sha256':h.hexdigest(),'bytes':n,'lstat':before,'fstat':before,'xattrs':xattrs,'metadataStable':True,'O_NOATIME':True}
 return (p,b''.join(chunks)) if keep else p
raw=[pin(RAW/n) for n in ['VISUAL-RESULT.json','VISUAL-PROGRESS.json']]
assert all(x['fstat']['st_dev']==27 and x['fstat']['st_nlink']==1 for x in raw)
assert raw[0]['sha256']!=raw[1]['sha256'] and raw[0]['fstat']['st_ino']!=raw[1]['fstat']['st_ino']
capsule=pin(CP);assert capsule['sha256']==CS and capsule['bytes']==1981882
f=op(CP);found={};manifest=None;manifestSHA=None
with os.fdopen(f,'rb') as stream:
 before=md(os.fstat(stream.fileno()))
 with tarfile.open(fileobj=stream,mode='r|gz') as tar:
  for m in tar:
   if m.name=='MANIFEST.json':
    assert m.size<1048576;b=tar.extractfile(m).read();manifestSHA=hashlib.sha256(b).hexdigest();assert manifestSHA==MS;manifest=json.loads(b)
   elif m.name in {'blobs/'+x['sha256'] for x in raw}:
    assert m.isfile() and m.name not in found;h=hashlib.sha256();n=0
    with tar.extractfile(m) as b:
     for chunk in iter(lambda:b.read(65536),b''):h.update(chunk);n+=len(chunk)
    found[m.name]={'sha256':h.hexdigest(),'bytes':n}
 assert before==md(os.fstat(stream.fileno()))
assert capsule['fstat']==md(os.lstat(CP)) and manifest is not None and len(found)==2
assert isinstance(manifest['roots'],dict) and isinstance(manifest['rows'],list)
entries=[{'originalPath':str(Path(manifest['roots'][r[0]])/r[1]),'path':r[0]+'/'+r[1],'bytes':r[2],'sha256':r[3],'row':r} for r in manifest['rows']]
mapping=[]
for x in raw:
 hits=[e for e in entries if e.get('originalPath')==x['path']];assert len(hits)==1;e=hits[0]
 assert (e['sha256'],e['bytes'])==(x['sha256'],x['bytes']) and found['blobs/'+x['sha256']]=={'sha256':x['sha256'],'bytes':x['bytes']}
 mapping.append({'originalPath':x['path'],'logicalPath':e['path'],'blobMember':'blobs/'+x['sha256'],'sha256':x['sha256'],'bytes':x['bytes']})
complete,b=pin(S/'target-clear-ghost-preservation-independent-r1/GATE.json',True);assert complete['sha256']=='6ec96568886fbeede7c9abacd6365edffa9cb4a7401c9d143ca50a281fd6ac65';assert json.loads(b)['decision'].startswith('ACCEPT')
selected,b=pin(S/'target-clear-ghost-promotion-root-r3/RESULT.json',True);sel=json.loads(b)
ik='canonicalInputs' if 'canonicalInputs' in sel else 'inputs';ok='canonicalOutputs' if 'canonicalOutputs' in sel else 'outputs';assert len(sel[ik])==88 and len(sel[ok])==56
selected.update({'inputKey':ik,'outputKey':ok,'inputCount':88,'outputCount':56})
consumers=[]
paths=[S/'target-clear-default-build-author-r1'/n for n in ['RUNTIME-FREEZE.json','bounded-build-r2.py','SEAL-BUILD-r1.py','ASSEMBLE-DEFAULT-r1.py','FINAL-SEAL.json']]+[S/'target-clear-default-build-independent-r1/GATE.json',S/'target-clear-default-build-independent-r1/MANIFEST.json']+[S/'target-clear-default-caller-author-r1'/n for n in ['driver-paired-r1.mjs','supervise-paired-r1.py','EXPECTED-CANDIDATE.json','PROTOCOL.md']]+[S/'target-clear-ghost-actual-gameplay-independent-r3/read_gameplay.py',S/'target-clear-ghost-publish-author-r1/CAPSULE-MAPPING.json',S/'target-clear-ghost-publish-author-r1/completedpromote.py']
for path in paths:
 try:
  q,b=pin(path,True);text=b.decode();hits=[{'line':i,'text':line[:500]} for i,line in enumerate(text.splitlines(),1) if any(k in line for k in ['target-clear-ghost-comparison-actual-r3','VISUAL-RESULT.json','VISUAL-PROGRESS.json'])]
  consumers.append({'pin':q,'referenceLines':hits,'historicalRole':str(path).find('actual-gameplay-independent-r3')>=0,'mappingRole':path.name=='CAPSULE-MAPPING.json','currentPendingConsumer':('/target-clear-default-' in str(path))})
 except OSError as e:consumers.append({'path':str(path),'locatorFailure':str(e),'assessed':False})
hold,b=pin(R/'AGENTS.md',True);head,b=pin(R/'.git/refs/heads/codex/lanternbound-production',True);assert b.decode().strip()=='b18e752fc528db4c9e447de071977253375f613e'
prior=pin(S/'retire-two-archived-json-copies-root-r1.py')
j={'decision':'CONDITIONAL_R3_TWO_RAW_PHYSICAL_RETIREMENT_PROPOSAL_ONLY_NO_ACTION','rawFiles':raw,'capsule':capsule,'manifestSHA256':MS,'exactLogicalMapping':mapping,'fullFreshArchivedBodyEquality':True,'independentCompleteGate':complete,'selectedMap':selected,'currentHold':hold,'currentConfirmedHEADControl':head,'consumerChecks':consumers,'parentRights':parents,'grossAllocationBytes':sum(x['fstat']['st_blocks']*512 for x in raw),'logicalBytes':sum(x['bytes'] for x in raw),'successorPreference':'Already published whole byte-exact compressed capsule retains both distinct full JSON bodies and original logical/provenance mappings efficiently. The complete independent303unique/318logical/134dependency gate is pinned; this fresh audit stream-matches both bodies again. No alias-equality assumption or archive replacement.','oldLooseNeedDecision':'CONDITIONAL pending consumer interpretation and final pending caller pins. Historical hardcoded R3 readers need fresh reconstruction/path adaptation, not continuously present duplicate raw paths. Current builder/caller/reviews must not need these old large bodies to execute pending default work; unresolved source references or missing locators require explicit independent resolution before preference/no-longer-needed acceptance.','losses':['Exactly two original raw paths/inodes/physical allocation/time identity cease; old hardcoded readers must reconstruct exact bodies into NEW explicit paths and adapt NEW reader copy.','Fresh restore metadata is new; no inode/time rollback. Capsule bytes/logical mapping, all JPEG/screenshots/source/saves/events/findings/control manifests and every other file remain unchanged.','Finite static consumer evidence only; no universal future dependencies, global FDs or future writers.','Two unlink operations are durable per-leaf prefix, not atomic together; partial failure remains for diagnosis, no retry or blanket cleanup.'],'requirementsBeforeAction':['Independent exact gate explicitly prefers compressed successor and old loose copies no longer needed; settle prior decisions remain unchanged.','Current pending caller final pins/consumer interpretation resolved and Root producer judgment before action.','Fresh confirmed clean push of proposal, independent controls and methods; Root action only, ordinary64+512/disk64 unchanged, native70/70.5 unchanged.','Fresh both raw/capsule full body and metadata preflight, complete logical/archived-body equality, selected current88/56 full bodies pre/post, protected ZIP fullstat only, exact-two durable journal.'],'capacityQualification':'Gross allocation, not promised net. Source/publication/action/Git and filesystem overhead reduce actual measured recovery; no threshold reduction.','reconstruction':'New restore helper source only; pinned capsule/full manifest/exact logical mapping, streaming selected blob64KiB into explicitly NEW O_EXCL|O_NOFOLLOW destination, length/SHA/fsync. Never overwrite old path or execute restore now.','priorMethod':prior,'bootstrapFailures':['Initial capsule parser assumed an older entries/logicalBodies schema and failed before producing proposal; original source/guard/log retained. Fresh corrected reader uses exact roots/rows manifest schema verified by bounded probe.','Old POST PROOF.json locator absent; old GATE supplied actual old action method. Old guessed publisher/judge filenames absent; original two-file method embeds producer in action. New scope creates distinct pre-action judgment as required. Tiny initial read discovery unmetered; all relied controls pinned in this normal guarded source phase.'],'ownMaxRSSBytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,'bodyChunkBytes':65536,'allInputFDsClosed':True}
assert j['ownMaxRSSBytes']<24*1048576
with (P/'PROPOSAL.json').open('x') as o:json.dump(j,o,indent=2);o.write('\n')
print(json.dumps({'rawSHA256':[x['sha256'] for x in raw],'grossAllocationBytes':j['grossAllocationBytes'],'logicalBytes':j['logicalBytes'],'selectedMapSHA256':selected['sha256'],'ownMaxRSSBytes':j['ownMaxRSSBytes'],'consumerReferences':[{'path':c.get('pin',{}).get('path',c.get('path')),'lines':c.get('referenceLines'),'failure':c.get('locatorFailure')} for c in consumers]}))
