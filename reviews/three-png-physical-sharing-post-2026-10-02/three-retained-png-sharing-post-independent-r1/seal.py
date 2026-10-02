import os,json,hashlib,pathlib,time,resource
resource.setrlimit(resource.RLIMIT_DATA,(24*1048576,24*1048576))
P=pathlib.Path('/workspace/scratch/three-retained-png-sharing-post-independent-r1');C=pathlib.Path('/sys/fs/cgroup')
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
 cur=int((C/'memory.current').read_text());mx=int((C/'memory.max').read_text());v=os.statvfs(P)
 return {'current':cur,'headroom':mx-cur,'free':v.f_bavail*v.f_frsize,'utcNs':time.time_ns()}
i=snap();ev=(C/'memory.events').read_text();assert i['headroom']>=576*1048576 and i['free']>=64*1048576
p=j(P/'PROOF.json');r=j(P/'GUARD/RESULT.json');assert j(P/'GUARD/ADMISSION.json')['admitted'] and r['exit_code']==0 and r['failure'] is None and r['memory_events_before']==r['memory_events_after']
pts=[r['initial']]+r['samples']+[r['final']]
for v in pts:assert v['headroom']>=512*1048576 and v['current']-r['initial']['current']<=64*1048576 and v['free']>=1048576
report='''Accepted the completed exact three-PNG transaction, with its recorded physical isolation and metadata losses. No further action is authorized.

The historical abbey-courtyard, tool-vignettes and hunter-portrait paths now match the intended canonical public inodes and exact complete bytes, full post stats and empty xattrs. Canonical links changed4 to5 and ctime changed; original canonical atime, mtime, owner/mode, size and allocation remain. The old independent nlink1 stats remain in the durable before/proposal ledgers. Temporary links are absent. Nine monotonic journal entries show the exact per-leaf pre-link, durable-link and durable-replacement sequence; this is not all-three atomicity. The current87-input/56-output selected maps and complete historical66-source/51-output maps all still match. Retained rights/provenance, source, negative findings and rollback bytes remain; commercial rights are still pending.

The exact r2 method a084f117, hold, map, positive before gate, producer judgment b0da2355 and confirmed clean matching local/remote34f0a2a4 push receipt are pinned. Root's later read-only Git confirmation belongs to the audited method/receipts; this reviewer launched no Git. Protected original archive full metadata matches the prior independent ledger; no protected archive body was read.

Gross old allocation8,499,200 bytes and reported transaction-window free67,526,656 to76,009,472 bytes give measured gain8,482,816 before RESULT write,16,384 below gross due to before/journal allocation in that window. This is a finite observation, not a current/enduring free-space guarantee or exclusive global attribution. Result, independent proof and later publication consume more capacity. Fresh admission remains required for the next actual session.

Known canonical/frozen128 paths and the new historical recipient form four observed distinct entries of nlink5, leaving one unresolved entry per leaf. Its shared ctime/nlink/body implications remain qualified; no universal alias hold, FD/mmap/process/future-writer absence proof follows. The three old private inode histories, time metadata and write isolation are intentionally gone under the independently preferred and producer-authorized tradeoff. Byte/path rollback remains available; exact original inode/ctime rollback cannot be recreated. Workflow immutable/fresh-stage rules are not OS-enforced protection. No broader cleanup, release, art quality or game behavior acceptance follows.

Root actual guard completed rc0, all five resource points/three live samples stay within64MiB delta plus512MiB reserve, minimum headroom1,458,917,376 bytes and events unchanged. Generic guard completion asserts child group closure but is not an exhaustive PID/start ledger or global backend audit. This independent NOATIME streamed verifier passes64+512 with ownRSS below24MiB; all streams/stat FDs close. No source, media, runtime or canonical mutation, Node, browser, image/native action, protected archive body read or retry was performed. Only this new bounded proof packet was written; no reviewer failures occurred.
'''
with (P/'REVIEW.md').open('x') as f:f.write(report);f.flush();os.fsync(f.fileno())
vm=next(int(v.split()[1])*1024 for v in pathlib.Path('/proc/self/status').read_text().splitlines() if v.startswith('VmHWM:'));assert vm<24*1048576
f=snap();assert f['headroom']>=512*1048576 and f['current']-i['current']<=64*1048576 and f['free']>=64*1048576 and ev==(C/'memory.events').read_text()
g={k:p[k] for k in ['decision','actualControls','beforeGate','judgment','push','rootMethod','hold','selectedMap','commit','knownAliases','journalExactNineEntriesAndPrefixOrder','grossAllocationBytes','measuredWindow','current87Inputs56OutputsExact','selectedSourceDigest','selectedOutputsDigest','historical66Source51BuildExact','protectedMetadataOnly','rootActualGuard','onlyExactThreeScope']}
g.update({'proof':h(P/'PROOF.json'),'exactThreeCurrentInodesBodiesStatsXattrs':True,'allTemporaryPathsAbsent':True,'originalPrivateMetadataRetainedNotRestored':True,'noNewActionOrRetirementAuthority':True,'noReviewerFailures':True,'reviewerGuard':{'result':h(P/'GUARD/RESULT.json'),'points':len(pts),'minHeadroom':min(v['headroom'] for v in pts),'maxAggregateDelta':max(v['current']-r['initial']['current'] for v in pts),'eventsUnchanged':True,'ownVmHWM':p['ownVmHWM']},'seal64Work512Reserve':{'initial':i,'finalBeforeSmallSealWrites':f,'eventsUnchanged':True,'ownVmHWM':vm},'CLOSED':'All finite reader/guard/FDs closed; direct sealer has no child. No further action or exhaustive global closure claim.'})
wr('GATE.json',g);wr('MANIFEST.json',{'decision':p['decision'],'selfExcluded':True,'CLOSED':True,'files':[{'name':str(x.relative_to(P)),**h(x)} for x in sorted(P.rglob('*')) if x.is_file()]})
size=sum(x.stat().st_size for x in P.rglob('*') if x.is_file());assert size<=128*1024
print(json.dumps({'GATE':h(P/'GATE.json'),'MANIFEST':h(P/'MANIFEST.json'),'PROOF':h(P/'PROOF.json'),'packetBytes':size,'CLOSED':True}))
