from pathlib import Path
import os,json,hashlib,resource
resource.setrlimit(resource.RLIMIT_DATA,(24*1048576,24*1048576))
P=Path('/workspace/scratch/default-clear-preservation-independent-r1')
def pin(p):
 p=Path(p);h=hashlib.sha256()
 with os.fdopen(os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME),'rb') as f:
  s=os.fstat(f.fileno())
  for b in iter(lambda:f.read(65536),b''):h.update(b)
  assert s==os.fstat(f.fileno())==os.lstat(p)
 return {'path':str(p),'sha256':h.hexdigest(),'bytes':s.st_size}
def load(p):
 with os.fdopen(os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME),'rb') as f:return json.load(f)
def save(p,d):
 with p.open('x') as f:json.dump(d,f,separators=(',',':'));f.write('\n');f.flush();os.fsync(f.fileno())
proof=load(P/'COMPLETE-PROOF.json');source=load(P/'SOURCE-GATE.json');guard=load(P/'COMPLETE-GUARD/RESULT.json')
assert proof['completeCoverage'] is True and guard['exit_code']==0 and guard['failure'] is None and guard['memory_events_before']==guard['memory_events_after']
assert pin(P/'SOURCE-GATE.json')==proof['sourceGate'] and pin(P/'SOURCE-SEAL.json')==proof['sourceSeal']
for q in source['methods']+[source['sourcePlan'],source['sourceSeal'],source['reviewControls'],source['beforeMap'],source['candidateFreeze'],source['currentHold']]+source['actualReviewGates']:assert pin(q['path'])=={k:q[k] for k in ['path','sha256','bytes']}
assert pin(proof['summary']['path'])==proof['summary'] and pin(proof['RootCapsuleGuard']['path'])==proof['RootCapsuleGuard']
z=os.lstat('/workspace/scratch/retained-original-archives/preflight-bdf273-original-r4.zip');assert {k:getattr(z,k) for k in proof['protectedZIPFullStatAfter']}==proof['protectedZIPFullStatAfter']
gate={'decision':'ACCEPT_COMPLETE_DECLARED_CAPSULE_FOR_EXACT_ROOT_SELECTION','completeCoverage':True,'archiveSHA256':proof['archive']['sha256'],'manifestSHA256':proof['manifestSHA256'],'logicalBodies':370,'uniqueBlobs':320,'neededDependencies':204,'archive':proof['archive'],'summary':proof['summary'],'proof':pin(P/'COMPLETE-PROOF.json'),'review':pin(P/'COMPLETE-REVIEW.md'),'sourceGate':proof['sourceGate'],'sourceSeal':proof['sourceSeal'],'methods':source['methods'],'actualReviewGates':source['actualReviewGates'],'beforeMap':source['beforeMap'],'candidateFreeze':source['candidateFreeze'],'currentHold':proof['currentHold'],'bodyGuard':pin(P/'COMPLETE-GUARD/RESULT.json'),'RootCapsuleGuard':proof['RootCapsuleGuard'],'ownBodyRSSBytes':proof['ownMaxRSSBytes'],'allLogicalOriginalsAndDependenciesExact':True,'fullOldAndCandidateMapsChecked':288,'protectedZIPBodyNeverOpened':True,'protectedZIPFullStatUnchanged':True,'limits':['Root exact reviewed selection/publication methods only with fresh admission; no reviewer transaction.','No selection-wide atomicity or automatic rollback. Old main+five outputs retained, oldJS same-device rename and final exact56 outputs; partial durable prefixes need manual Root restoration.','External retained dependencies are required; capsule is not a self-contained executable environment.','No new gameplay/fun/300-second/native/platform/version/cleanup claim. Resource samples are not exclusive attribution.']}
save(P/'GATE.json',gate)
files={str(p.relative_to(P)):pin(p) for p in sorted(P.rglob('*')) if p.is_file() and 'COMPLETE-SEAL-GUARD' not in p.parts}
rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024;assert rss<24*1048576
seal={'phase':'COMPLETE_CAPSULE_PRESERVATION_REVIEW','files':files,'gate':pin(P/'GATE.json'),'packetLogicalCapBytes':96*1024,'ownSealRSSBytes':rss,'runtimeCompleteSealGuardExcludedUntilExternalCompletion':True,'selectionPerformedByReviewer':False}
encoded=json.dumps(seal,separators=(',',':')).encode();total=sum(p.stat().st_size for p in P.rglob('*') if p.is_file());assert total+len(encoded)+1+8192<=96*1024
save(P/'COMPLETE-SEAL.json',seal)
fd=os.open(P,os.O_RDONLY|os.O_DIRECTORY)
try:os.fsync(fd)
finally:os.close(fd)
print(json.dumps({'gate':pin(P/'GATE.json'),'seal':pin(P/'COMPLETE-SEAL.json'),'logicalBytesBeforeGuardFinal':sum(p.stat().st_size for p in P.rglob('*') if p.is_file()),'reservedGuardCompletionBytes':8192,'ownSealRSSBytes':rss,'allOwnFDsClosed':True}))
