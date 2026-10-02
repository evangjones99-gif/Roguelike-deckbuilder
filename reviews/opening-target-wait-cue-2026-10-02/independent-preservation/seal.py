import os,json,pathlib,hashlib,time,resource
resource.setrlimit(resource.RLIMIT_DATA,(24*1048576,24*1048576))
P=pathlib.Path('/workspace/scratch/target-wait-cue-preservation-independent-r1');C=pathlib.Path('/sys/fs/cgroup')
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
 current=int((C/'memory.current').read_text());maximum=int((C/'memory.max').read_text());v=os.statvfs(P)
 return {'current':current,'maximum':maximum,'headroom':maximum-current,'free':v.f_bavail*v.f_frsize,'utcNs':time.time_ns()}
initial=snap();events=(C/'memory.events').read_text();assert initial['headroom']>=576*1048576 and initial['free']>=64*1048576
p=j(P/'PROOF.json');r=j(P/'GUARD-r2/RESULT.json');assert r['exit_code']==0 and r['failure'] is None and r['memory_events_before']==r['memory_events_after']
pts=[r['initial']]+r['samples']+[r['final']]
for x in pts:assert x['headroom']>=512*1048576 and x['current']-r['initial']['current']<=64*1048576 and x['free']>=1048576
assert j(P/'GUARD/RESULT.json')['exit_code']==1 and j(P/'INSPECT-GUARD/RESULT.json')['exit_code']==0
report='''Accepted exact preservation of the opt-in target-wait cue trial. All 236 archive blobs roundtrip against their hashes, all 253 logical mappings match complete original bodies, and all selected source/build/caller/actual/review directories are complete. Runtime maps cover all 87 inputs and 56 outputs; 42 code/static bodies are included and 101 PNG/WAV bodies are excluded, pinned, verified at their retained original paths and still needed.

All six complete raw saved checkpoint pairs match through the archive mapping. The exact source, build, caller and technical/visual review gates are retained; the separate gameplay seal and evidence are included. All four original JPEGs (776,624 bytes) roundtrip as complete encoded bodies. No image was decoded or viewed, and capture phaseCertified=false remains unchanged.

The producer's finite 64 MiB work / 512 MiB reserve guard completed normally with unchanged memory events. Reviewer guards closed normally after one preserved method failure: the saved-file selector assumed a filename prefix, while the files end in -OPAQUE-SAVE.json. Corrected verify-r2.py passed without altering archive or original evidence. Reader peak RSS was 14,245,888 bytes. Shared-cgroup samples and finite owned-child closure do not establish exhaustive global or backend attribution.

The archive's README and preservation record accurately describe its opt-in checkpoint. Later successors must not rewrite those historical claims. This gate does not promote a default, retire originals, authorize cleanup, establish human enjoyment, repair rapid drops, approve art, or certify a self-contained release. Only the new review packet was written; no extraction, compiler, browser, native action, Git or backend ran. All tools/readers/guards and file descriptors close before return.
'''
with (P/'REVIEW.md').open('x') as f:f.write(report);f.flush();os.fsync(f.fileno())
vm=next(int(x.split()[1])*1024 for x in pathlib.Path('/proc/self/status').read_text().splitlines() if x.startswith('VmHWM:'));assert vm<=24*1048576
final=snap();assert final['headroom']>=512*1048576 and final['current']-initial['current']<=64*1048576 and final['free']>=64*1048576 and events==(C/'memory.events').read_text()
gate={'decision':p['decision'],'proof':h(P/'PROOF.json'),'archive':p['archive'],'manifestSHA256':p['manifestSHA256'],'counts':p['counts'],'fullRoundtripAndOriginalEquality':True,'completeRuntimeMapsAndEvidenceDirectories':True,'allSixFullSavePairsMatch':True,'originalFourCapturesRetained':True,'omissions':'101 pinned PNG/WAV original bodies verified and still needed; not self-contained','sourceDigest':p['sourceDigest'],'outputsDigest':p['outputsDigest'],'preservedReviewerMethodFailure':'GUARD rc1 / wrong saved-file name selector; corrected GUARD-r2 rc0, archive and originals unchanged','reviewerGuard':{'result':h(P/'GUARD-r2/RESULT.json'),'points':len(pts),'minimumHeadroom':min(x['headroom'] for x in pts),'maximumAggregateDelta':max(x['current']-r['initial']['current'] for x in pts),'eventsUnchanged':True,'ownVmHWM':p['ownVmHWM']},'seal64Work512Reserve':{'initial':initial,'finalBeforeSmallSealWrites':final,'eventsUnchanged':True,'ownVmHWM':vm},'scope':p['scope'],'CLOSED':'All tools/readers/FDs and finite guarded child groups closed. Direct sealer launches no child. No exhaustive global/backend attribution.'}
wr('GATE.json',gate)
rows=[{'name':str(x.relative_to(P)),**h(x)} for x in sorted(P.rglob('*')) if x.is_file()]
wr('MANIFEST.json',{'decision':p['decision'],'bodies':rows,'selfExcluded':True,'CLOSED':True})
size=sum(x.stat().st_size for x in P.rglob('*') if x.is_file());assert size<=160*1024
print(json.dumps({'GATE':h(P/'GATE.json'),'MANIFEST':h(P/'MANIFEST.json'),'PROOF':h(P/'PROOF.json'),'packetBytes':size,'CLOSED':True}))
