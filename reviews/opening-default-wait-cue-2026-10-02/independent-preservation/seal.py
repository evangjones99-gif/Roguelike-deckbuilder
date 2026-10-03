import os,json,pathlib,hashlib,time,resource
resource.setrlimit(resource.RLIMIT_DATA,(24*1048576,24*1048576))
P=pathlib.Path('/workspace/scratch/default-wait-cue-preservation-independent-r1');C=pathlib.Path('/sys/fs/cgroup')
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
 return {'current':c,'maximum':mx,'headroom':mx-c,'free':v.f_bavail*v.f_frsize,'utcNs':time.time_ns()}
initial=snap();events=(C/'memory.events').read_text();assert initial['headroom']>=576*1048576 and initial['free']>=64*1048576
p=j(P/'PROOF.json');r=j(P/'GUARD-r2/RESULT.json');assert r['exit_code']==0 and r['failure'] is None and r['memory_events_before']==r['memory_events_after'] and j(P/'GUARD/RESULT.json')['exit_code']==1
pts=[r['initial']]+r['samples']+[r['final']]
for x in pts:assert x['headroom']>=512*1048576 and x['current']-r['initial']['current']<=64*1048576 and x['free']>=1048576
report='''Accepted exact preservation of the already selected default named-wait development checkpoint. All209 archive blobs roundtrip, all226 unique logical mappings match their complete original bodies, and all selected source/build/caller/actual/three-review/Root-promotion directories and nested control manifests are complete. Full87/56 maps match frozen and current canonical bodies. All six complete raw saved pairs and four original JPEG encoded bodies (776,612B) remain intact. No image was decoded or viewed.

The101 runtime PNG/WAV omissions match their pins at retained original paths and remain necessary. The old READY251c/2c66 full maps match its frozen stage; two original source files and all five original code outputs match the archived rollback bodies. Root producer judgment and exact independent review pins are retained, with no retirement/media-body-write claim expanded. The earlier opt-in capsule remains byte-exact33a7. This archive is not a self-contained release or cleanup authority.

Selected-baseline OriginalPath entries identify mutable canonical working-copy paths. Their current bytes match now, while exact archive blobs and the fixed frozen default stage preserve checkpoint bytes through future authorized edits. Later working-copy changes must not rewrite this checkpoint or be mistaken for preservation failure of its immutable body.

Root and reviewer finite64MiB+512reserve guards pass with unchanged memory events, separately measured own reader RSS14,622,720B. One original reviewer rc1 assumed nested files manifests used dictionaries; visual review uses an absolute-path array. The original verifier/log remain intact; verify-r2 normalizes both forms and passes without changing archive or originals. Sampling may include overlapping tiny source actors and does not establish exhaustive backend/global attribution. No extraction, compiler, Node, Git, browser, native action, backend or image view ran. Only this new review packet was written. All readers/tools/guards/FDs close before return. No new art/default choice, occlusion or rapid-drop repair, human fun, version/tag/release or retirement approval follows.
'''
with (P/'REVIEW.md').open('x') as f:f.write(report);f.flush();os.fsync(f.fileno())
vm=next(int(x.split()[1])*1024 for x in pathlib.Path('/proc/self/status').read_text().splitlines() if x.startswith('VmHWM:'));assert vm<24*1048576
final=snap();assert final['headroom']>=512*1048576 and final['current']-initial['current']<=64*1048576 and final['free']>=64*1048576 and events==(C/'memory.events').read_text()
gate={'decision':p['decision'],'proof':h(P/'PROOF.json'),'archive':p['archive'],'manifestSHA256':p['manifestSHA256'],'counts':p['counts'],'allBlobsRoundtripAndLogicalOriginalsExact':True,'completeMapsAndReviewPinsAndSixRawPairs':True,'currentCanonical87Inputs56OutputsMatchCheckpoint':True,'oldReadyFullMapsAndTwoSourcesFiveOutputsRetainedExact':True,'fourOriginalEncodedJPEGsRetainedNoDecodeView':True,'neededOmissions':101,'noRetirement':True,'mutableOriginalPathQualification':'Canonical working-copy paths match at this checkpoint; immutable archive blobs and fixed frozen stage retain bytes across future authorized updates.','previousOptInCapsuleUnchanged':p['previousOptInCapsuleUnchanged'],'preservedReviewerFailure':p['preservedReviewerMethodFailure'],'reviewerGuard64Aggregate512Reserve':{'result':h(P/'GUARD-r2/RESULT.json'),'points':len(pts),'minimumHeadroom':min(x['headroom'] for x in pts),'maximumAggregateDelta':max(x['current']-r['initial']['current'] for x in pts),'eventsUnchanged':True,'ownVmHWM':p['ownVmHWM']},'seal64Aggregate512Reserve':{'initial':initial,'finalBeforeSmallSealWrites':final,'eventsUnchanged':True,'ownVmHWM':vm},'limits':p['scope'],'CLOSED':'All finite readers/guards/tools/FDs closed; direct sealer launches no children. Sharedcgroup samples not exclusive global/backend attribution.'}
wr('GATE.json',gate)
rows=[{'name':str(x.relative_to(P)),**h(x)} for x in sorted(P.rglob('*')) if x.is_file()];wr('MANIFEST.json',{'decision':p['decision'],'bodies':rows,'selfExcluded':True,'CLOSED':True})
size=sum(x.stat().st_size for x in P.rglob('*') if x.is_file());assert size<=160*1024
print(json.dumps({'GATE':h(P/'GATE.json'),'MANIFEST':h(P/'MANIFEST.json'),'PROOF':h(P/'PROOF.json'),'packetBytes':size,'CLOSED':True}))
