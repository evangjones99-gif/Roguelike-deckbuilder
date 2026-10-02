import os,json,pathlib,hashlib,time,resource
resource.setrlimit(resource.RLIMIT_DATA,(24*1048576,24*1048576))
P=pathlib.Path('/workspace/scratch/target-clear-rejection-preservation-independent-r1');C=pathlib.Path('/sys/fs/cgroup')
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
p=j(P/'PROOF.json');r=j(P/'GUARD/RESULT.json');assert j(P/'GUARD/ADMISSION.json')['admitted'] and r['exit_code']==0 and r['failure'] is None and r['memory_events_before']==r['memory_events_after'];pts=[r['initial']]+r['samples']+[r['final']]
for x in pts:assert x['headroom']>=512*1048576 and x['current']-r['initial']['current']<=64*1048576 and x['free']>=1048576
review='''Accepted the exact rejected ghost R1 preservation capsule and byte-exact published three-PNG POST records. This is preservation acceptance only, no source or visual promotion and no cleanup authority.

Archive1,336,063 bytes SHA0871ec41c94e39313eb132aa1296385e3e6461e7be0a03e9ef333e4d8453b8a3 and manifestc061f51137513fb0bb3553aa6e7d76b6750a2f4abe3a50aa2dea53fddc9e9181 verify. Every249 unique blob hashes correctly and roundtrips to all264 safe unique logical originals. Included evidence directories and nested manifests are complete and byte-exact. Exact freeze0410/source2b3fcb03/output8235e599 maps contain88 inputs and56 outputs, agreeing with retained actual before/after/served maps. The complete frozen stage/media are excluded and remain necessary; the capsule is not self-contained and does not authorize retiring any original.

All four original JPEG encoded bodies, total784,953 bytes, and six complete raw save checkpoint pairs match. Images were hashed without decoding or viewing. The exact technical GATE4cc1dc2d, gameplay FINALa79d25ed and visual GATE851c1a5c remain retained with their separate findings: technical identity/purity/calculation acceptance and gameplay/visual rejection for default selection. No geometry or native action was repeated. Two refused Root resource grants, later admitted grant, and read-only inactive cache-hint methods/receipts remain included without material-retirement or causal-effect overclaims.

The failed oversized visual R1 packet and its supplemental correction are preserved. Its two temporarily removed unsealed JSON paths now match their recorded original bodies and full streaming gzip decompressions. Exact body restoration is proven; original pre-removal inode/time identity was not recorded and remains unknown. Fresh R2 cap applies to its supplement only, not the failed oversized packet. Original failed methods/findings were not rewritten by this review.

All22 published copies of completed PNG POST review, original transaction before/journal/result, guard, producer judgment, confirmed push and capsule preservation-method records match source bodies and COPY-IDENTITIES. Exact3 path/byte retention, intentional inode/time/write-isolation losses, one unresolved shared alias per leaf and no new cleanup authority remain unchanged. Commercial rights remain pending. Large protected ZIP, retained source bundle and Git pack bodies were not read.

Root preservation64+512 guard completes rc0 with all13 resource points bounded and events unchanged; finite closure assertions are not exhaustive global/backend attribution. This independent64+512 source verifier passes with ownRSS below24MiB. Initial discovery incorrectly assumed evidence/root prefixes and raised IndexError for a top-level helper name; corrected discovery uses direct scratch-relative names and records the failure, without changing archive/source/runtime. No guarded verification failure occurred. All O_NOATIME tar/gzip/origin readers, guards and FDs close before return. No Node, browser, build, Git, image/native/backend action, extraction or runtime/source/canonical mutation occurred; only this new proof packet was written.
'''
with (P/'REVIEW.md').open('x') as f:f.write(review);f.flush();os.fsync(f.fileno())
vm=next(int(x.split()[1])*1024 for x in pathlib.Path('/proc/self/status').read_text().splitlines() if x.startswith('VmHWM:'));assert vm<24*1048576
f=snap();assert f['headroom']>=512*1048576 and f['current']-i['current']<=64*1048576 and f['free']>=64*1048576 and ev==(C/'memory.events').read_text()
g={k:p[k] for k in ['decision','archive','manifestSHA256','counts','sourceDigest','outputsDigest','maps','threeIndependentActualFindings','completeRawSavePairs','fourOriginalJPEGs','copyIdentities','rootPreservationGuard','ownMethodDiscoveryFailure','scope']}
g.update({'proof':h(P/'PROOF.json'),'allBlobsLogicalOriginsRoundtripExact':True,'allPublishedPostCopiesExact':True,'restoredVisualBodiesAndGzipExact':True,'preRemovalVisualFilesystemMetadataUnknown':True,'originalFailedVisualPacketStillNeeded':True,'refusedRootGrantsAndCacheHintMethodsIncluded':True,'neededFrozenStageMediaExcludedNotSelfContained':True,'noCleanupRetirementOrSourceR2Authority':True,'reviewerGuard64Aggregate512Reserve':{'result':h(P/'GUARD/RESULT.json'),'points':len(pts),'minimumHeadroom':min(x['headroom'] for x in pts),'maximumAggregateDelta':max(x['current']-r['initial']['current'] for x in pts),'eventsUnchanged':True,'ownVmHWM':p['ownVmHWM'],'qualification':'Coordinated tiny source reader sharing allowed; sampled aggregate not exclusive actor accounting.'},'seal64Work512Reserve':{'initial':i,'finalBeforeSmallSealWrites':f,'eventsUnchanged':True,'ownVmHWM':vm},'CLOSED':'All finite reviewer source/tar/gzip readers/guards/FDs closed; direct sealer has no child. No exhaustive global/backend attribution.'})
wr('GATE.json',g);wr('MANIFEST.json',{'decision':p['decision'],'bodies':[{'name':str(x.relative_to(P)),**h(x)} for x in sorted(P.rglob('*')) if x.is_file()],'selfExcluded':True,'CLOSED':True})
size=sum(x.stat().st_size for x in P.rglob('*') if x.is_file());assert size<=192*1024
print(json.dumps({'GATE':h(P/'GATE.json'),'MANIFEST':h(P/'MANIFEST.json'),'PROOF':h(P/'PROOF.json'),'packetBytes':size,'CLOSED':True}))
