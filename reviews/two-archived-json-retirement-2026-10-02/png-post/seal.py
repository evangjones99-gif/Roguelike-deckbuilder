import os,json,pathlib,hashlib,time,resource
resource.setrlimit(resource.RLIMIT_DATA,(24*1048576,24*1048576))
P=pathlib.Path('/workspace/scratch/second-three-png-sharing-post-independent-r4');S=pathlib.Path('/workspace/scratch');C=pathlib.Path('/sys/fs/cgroup')
def j(p):
 with p.open() as f:return json.load(f)
def h(p):
 z=hashlib.sha256();n=0
 with p.open('rb') as f:
  for b in iter(lambda:f.read(32768),b''):z.update(b);n+=len(b)
 return {'sha256':z.hexdigest(),'bytes':n}
def wr(n,o):
 with (P/n).open('x') as f:json.dump(o,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def snap():
 c=int((C/'memory.current').read_text());mx=int((C/'memory.max').read_text());v=os.statvfs(P)
 return {'current':c,'headroom':mx-c,'free':v.f_bavail*v.f_frsize,'utcNs':time.time_ns()}
i=snap();ev=(C/'memory.events').read_text();assert i['headroom']>=576*1048576 and i['free']>=64*1048576
p=j(P/'PROOF.json');r=j(P/'GUARD-r2/RESULT.json');fail=j(P/'GUARD/RESULT.json');assert fail['exit_code']==1 and fail['failure'] is None and fail['memory_events_before']==fail['memory_events_after'];assert j(P/'GUARD-r2/ADMISSION.json')['admitted'] and r['exit_code']==0 and r['failure'] is None and r['memory_events_before']==r['memory_events_after'];pts=[r['initial']]+r['samples']+[r['final']]
for x in pts:assert x['headroom']>=512*1048576 and x['current']-r['initial']['current']<=64*1048576 and x['free']>=1048576
oldfail=S/'second-three-png-sharing-actual-guard-root-r3';of=j(oldfail/'RESULT.json');assert of['exit_code']==1 and of['failure'] is None and of['memory_events_before']==of['memory_events_after']
review='''Accepted the exact completed second three-PNG r4 postcheck. No further storage or cleanup action is authorized.

The historical independent/rebuilt-dist abbey-courtyard, tool-vignettes and hunter-portrait recipients now share their intended canonical public inodes at nlink6. Full current nofollow lstat/fstat/SHA256/xattrs agree with RESULT and remain unchanged through O_NOATIME streaming; direct recipient/anchor ancestor chains are opened with O_PATH/O_DIRECTORY/O_NOFOLLOW. Each anchor nlink changed5 to6 and ctime changed, while all other rebound-anchor metadata remains exact. Five distinct known physical entries match, leaving one unresolved entry per leaf. Its shared metadata/body implications stay qualified; no universal logical-symlink/FD/mmap/future-writer absence or OS protection is claimed.

Original proposal45ed75b5, accepted rebind gatefedeb00d, method5c03ec51, producer judgmenteca6c758 and confirmed matching clean local/remote90d12893 push6c7fabe8 bind the action. Durable BEFORE retains the old independent nlink1 metadata, original proposalMetadata and fresh preflight. Comparison proves initial rebinding changes only atime; no timestamp resetting occurred and subsequent fullsnapshot checks remain strict. Nine monotonic pre-link/durable-link/durable-replacement entries exactly match the named three paths; all unique temps are absent. The prior r3 fullstat assertion refusal remains preserved before its transaction, never relabelled successful. The prior first POST014c is retained as historical nlink5 evidence, not rewritten to current6.

All current selected87 runtime inputs and56 outputs match1d5bf40a/30ddc549 and the pinned complete map. Protected original ZIP fullstat still matches the first independent ledger; its body was never read. Old66-source/51-output aggregate manifests remain pinned historical evidence, not a fresh full body replay. Their rights/provenance and negative consumer findings remain needed, and commercial clearance is not granted.

Gross allocation8,499,200 bytes and observed window free64,778,240 to73,240,576 before RESULT write yield8,462,336 gain,36,864 below gross. Subsequent proof/publication footprints and other activity affect capacity; neither lasting free space nor exclusive attribution is established. Root actual guard used the separately reviewed recovery-only56MiB disk floor because initial free was below ordinary64MiB;64MiB work+512 reserve remained unchanged. All5 points/3 samples pass, sampled maxdelta9,797,632/minhead2,198,024,192 bytes, events unchanged and normal0. Ordinary build64/native70 admission thresholds remain intact. Finite guard normal completion/held-descriptor finally closure is not exhaustive global PID/backend attribution.

Intentional old private inode/time/write isolation losses match specific judgment. Exact bytes/paths/source/reviews/provenance/rollback bytes remain; original inode history cannot be recreated. No backups or all-three atomicity are claimed; durable per-leaf prefix requires fresh diagnosis on interruption, no automatic retry or additional paths. Current clean push is verified by the preaction pinned Root method and receipt, without a fresh Git command from this reviewer.

The first reviewer verifier contained a missing closing bracket and failed before execution/body reads/proof writes. New verify-r2 adds that bracket; original failed source/guard/log remain. Corrected verifier passes ordinary source64+512/disk64 with ownRSS11,124,736 bytes. No Node/Git/browser/build/native/images/art writes/protectedarchivebody or storage action occurred; only this new bounded proof was written. All readers/guards/FDs close before return.
'''
with (P/'REVIEW.md').open('x') as f:f.write(review);f.flush();os.fsync(f.fileno())
vm=next(int(x.split()[1])*1024 for x in pathlib.Path('/proc/self/status').read_text().splitlines() if x.startswith('VmHWM:'));assert vm<24*1048576
f=snap();assert f['headroom']>=512*1048576 and f['current']-i['current']<=64*1048576 and f['free']>=64*1048576 and ev==(C/'memory.events').read_text()
g={k:p[k] for k in ['decision','actualControls','proposal','beforeGate','judgment','push','method','hold','selectedMap','commit','knownAliases','initialAtimeOnlyRebinding','allNineJournalEntriesOrderedExactly','allTempAbsent','allPathsExactBodiesRetained','window','fullCurrent87Inputs56OutputsExact','sourceDigest','outputsDigest','protectedFullStatUnchangedMetadataOnly','historical66Source51OutputLedgersPinnedNotNewReplay','previous014cPOSTRetainedAsHistoricalNlink5','rootActualGuard','scope','reviewerMethodFailure']}
g.update({'proof':h(P/'PROOF.json'),'currentThreeBodiesStatsXattrsExact':True,'preservedRootR3PreactionFailure':{'result':h(oldfail/'RESULT.json'),'executionLog':h(oldfail/'EXECUTION.log'),'rc':1},'noNewActionCleanupOrGameArtQualityClaim':True,'reviewerGuard64Work512ReserveDisk64':{'result':h(P/'GUARD-r2/RESULT.json'),'originalFailedGuard':h(P/'GUARD/RESULT.json'),'points':len(pts),'minHeadroom':min(x['headroom'] for x in pts),'maxAggregateDelta':max(x['current']-r['initial']['current'] for x in pts),'eventsUnchanged':True,'ownVmHWM':p['ownVmHWM']},'seal64Work512Reserve':{'initial':i,'finalBeforeSmallSealWrites':f,'eventsUnchanged':True,'ownVmHWM':vm},'CLOSED':'All finite readers/guards/FDs closed; direct sealer launches no child. No exhaustive global closure/actor attribution.'})
wr('GATE.json',g);wr('MANIFEST.json',{'decision':p['decision'],'selfExcluded':True,'CLOSED':True,'bodies':[{'name':str(x.relative_to(P)),**h(x)} for x in sorted(P.rglob('*')) if x.is_file()]})
size=sum(x.stat().st_size for x in P.rglob('*') if x.is_file());assert size<=96*1024
print(json.dumps({'GATE':h(P/'GATE.json'),'MANIFEST':h(P/'MANIFEST.json'),'PROOF':h(P/'PROOF.json'),'packetBytes':size,'CLOSED':True}))
