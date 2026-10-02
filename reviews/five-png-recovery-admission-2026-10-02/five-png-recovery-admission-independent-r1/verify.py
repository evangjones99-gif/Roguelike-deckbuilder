from pathlib import Path
import os,json,hashlib,stat,resource,ast,difflib
resource.setrlimit(resource.RLIMIT_DATA,(24*1048576,24*1048576))
S=Path('/workspace/scratch');R=Path('/workspace/Roguelike-deckbuilder');P=S/'five-png-recovery-admission-independent-r1';OLD=S/'next-five-png-sharing-independent-r1'
def pin(p,body=False):
 p=Path(p);assert not p.is_symlink();fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME);h=hashlib.sha256();n=0;parts=[]
 with os.fdopen(fd,'rb') as f:
  for b in iter(lambda:f.read(65536),b''):
   h.update(b);n+=len(b)
   if body:parts.append(b);assert n<262144
 q={'path':str(p),'bytes':n,'sha256':h.hexdigest()};return (q,b''.join(parts)) if body else q
def load(p):
 q,b=pin(p,True);return q,json.loads(b)
def save(n,j):
 with (P/n).open('x') as f:json.dump(j,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
pins=[];bodies={}
fixed=[('share-five-retained-pngs-root-r2.py','92796922f14a22c4145b572cf0a9c8b4913b269a650fbb156e1289104cf6957e'),('judge-five-png-sharing-root-r2.py','6df74d829adfea1af04138be52caed7d400df17a8bfbca9b967240544e9dab8f'),('publish-five-png-recovery-root-r1.py','a0cc8a898cc98d8789f5fce777e5f7f3f4f69cf2b6901cd537ea239cc924d8b74'),('guard-source-recovery-56m-root-r2.py','c2b24f58d6abbbe0449fc49515e6bb9eeaf0997bd287642d87a3a1754388fff3')]
for n,h in fixed:
 q,b=pin(S/n,True);assert q['sha256']==h;ast.parse(b);pins.append(q);bodies[n]=b.decode()
op,original=pin(S/'share-five-retained-pngs-root-r1.py',True);assert op['sha256']=='55cc724ef39fd38ef1c56bedcbf4c7a5e870e3c3f119dbe8a478c234658e5e97'
expected=original.decode().replace('initial_free>=64*1048576','initial_free>=56*1048576').replace('.root-share-five-r1.tmp','.root-share-five-r2.tmp').replace('five-retained-png-sharing-actual-root-r1','five-retained-png-sharing-actual-root-r2')
assert bodies[fixed[0][0]]==expected
diff=list(difflib.unified_diff(original.decode().splitlines(),expected.splitlines(),fromfile=op['path'],tofile=pins[0]['path'],lineterm=''))
guard=bodies[fixed[3][0]]
for text in ['reserve=512*1048576','initial[\'free\']>=56*1048576','row[\'free\']<1048576','row[\'headroom\']<reserve','row[\'delta\']>work','assert int(work_mb) in (64,256)','os.killpg(process.pid,signal.SIGTERM)','subprocess.Popen(command']:
 assert text in guard
assert "command[1].startswith('/workspace/scratch/')" in guard
pp,e=load(S/'five-retained-png-recovery-proposal-r1/PROPOSAL.json');assert pp['sha256']=='b4e8803f2411e932c994b01aa50152fee4b4bd9d2c8757258ae7c686b75745bc'
gp,g=load(OLD/'GATE.json');assert gp['sha256']=='c5a2f58872df98a604589d46a0ccb2caf9a1c88520831b4b176eb6d0727fa8df' and g['replacementBetter'] and g['oldRedundantPrivatePhysicalEncodingsNoLongerNeeded'] and g['everyLogicalPathBodyStillNeeded']
prior=pin(OLD/'PROOF.json');assert prior['sha256']==g['independentProof']['sha256']
for rel,h in [('next-five-png-sharing-independent-r1/GATE.json',gp['sha256']),('next-five-png-sharing-independent-r1/PROOF.json',prior['sha256']),('five-retained-png-recovery-proposal-r1/PROPOSAL.json',pp['sha256'])]:
 assert pin(R/'reviews/five-retained-png-physical-sharing-2026-10-02'/rel)['sha256']==h
hp=pin(R/'AGENTS.md');assert hp['sha256']==g['currentHold']['sha256']=='b674fd4456ad4332c97ad4538fbf8c008842c708964a16e1acde77790bea0906'
mp=pin(S/'target-wait-default-promotion-root-r1/RESULT.json');assert mp['sha256']==g['selectedMap']['sha256']=='31a221091d2ffbc6d58dfc1385962c441df9789c66729ef64d20b95208a8fabd'
pushp,push=load(S/'five-png-proposal-push-root-r1/PUSH-CONFIRMED.json');assert push['confirmed'] and push['clean'] and push['remote']==push['commit']=='1ea32dc666c5d4c33da1824bf5b9bf5f027ebda1' and push['gateSHA256']==gp['sha256']
refp,ref=pin(R/'.git/refs/heads/codex/lanternbound-production',True);assert ref.decode().strip()==push['commit']
refusalp,refusal=load(S/'five-png-producer-guard-root-r1/ADMISSION.json');assert refusal['admitted'] is False and refusal['initial']['free']==66977792 and refusal['work']==64*1048576 and refusal['reserve']==512*1048576
assert sorted(x.name for x in (S/'five-png-producer-guard-root-r1').iterdir())==['ADMISSION.json']
for name in ['five-png-producer-judgment-root-r1.json','five-png-producer-judgment-root-r2.json','five-retained-png-sharing-actual-root-r1','five-retained-png-sharing-actual-root-r2','five-png-recovery-push-root-r1']:assert not (S/name).exists()
keys=['st_dev','st_ino','st_mode','st_nlink','st_uid','st_gid','st_size','st_blocks','st_atime_ns','st_mtime_ns','st_ctime_ns']
media=[]
for pair in e['pairs']:
 for kind in ['anchor','candidate']:
  old=pair[kind];path=Path(old['path']);fd=os.open('/',os.O_PATH|os.O_DIRECTORY|os.O_NOFOLLOW)
  try:
   for part in path.parent.parts[1:]:
    n=os.open(part,os.O_PATH|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd);os.close(fd);fd=n
   f=os.open(path.name,os.O_PATH|os.O_NOFOLLOW,dir_fd=fd)
   try:
    z={k:getattr(os.fstat(f),k) for k in keys};attrs={k:os.getxattr('/proc/self/fd/'+str(f),k).hex() for k in os.listxattr('/proc/self/fd/'+str(f))}
   finally:os.close(f)
  finally:os.close(fd)
  assert stat.S_ISREG(z['st_mode']) and all(z[k]==v for k,v in old['fstat'].items() if k!='st_atime_ns') and attrs==old['xattrs']=={}
  if kind=='candidate':
   assert z['st_nlink']==1
   for suffix in ['.root-share-five-r1.tmp','.root-share-five-r2.tmp']:assert not path.with_name(path.name+suffix).exists()
  media.append({'path':str(path),'kind':kind,'metadata':z,'xattrs':attrs,'bytesNotRead':True,'initialAtimeChanged':z['st_atime_ns']!=old['fstat']['st_atime_ns']})
copiedsource=sum(q['bytes'] for q in pins[:3]);base=copiedsource+refusalp['bytes'];assert base+48*1024<128*1024
rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024;assert rss<24*1048576
free=os.statvfs(R).f_bavail*os.statvfs(R).f_frsize
save('PROOF.json',{'newSourcePins':pins,'priorActionSource':op,'mechanicalActionDiff':diff,'proposal':pp,'priorGate':gp,'priorTenBodyProof':prior,'currentHold':hp,'selectedMap':mp,'priorConfirmedPush':pushp,'priorConfirmedPushFields':push,'currentBranchRef':refp,'normalProducerRefusal':refusalp,'refusalFields':refusal,'noProducerOrActionArtifactsObserved':True,'freshTenMetadataOnly':media,'publisherOtherCopiedBodyBytes':base,'publisherConservativeCopiedBodyUpperBound':base+48*1024,'publisherCopiedBodyCapBytes':128*1024,'transactionLogicalModeledCapBytes':65536,'transactionQualification':'Five ledger leaf pairs and proposalMetadata snapshots plus finite15 journal rows/temp filenames/results modeled below64KiB; no filesystem/Git/command log or inode allocation overhead universal bound. No new private-inode backup.','ownMaxRSSBytes':rss,'freeAtProofEndBeforeProofWrite':free,'resourceProfile':'Explicitly unmetered finite bootstrap source/AST/diff/metadata/read/seal review only. Not normal64 guard compliance and not global56 workload admission.','guardQualification':'Filename filter is not exact allowlist or OS scope. Only external sole-writer Root and exact pinned three invocations constrain this exception.','allInputFDsClosed':True,'mediaBytesNotRehashed':True,'noGitOrActionExecuted':True})
print(json.dumps({'sourceProofNormal':True,'ownMaxRSSBytes':rss,'publisherOtherBytes':base,'publisherUpperBound':base+48*1024,'freeAtEnd':free,'allFDsClosed':True,'unmetered':True}))
