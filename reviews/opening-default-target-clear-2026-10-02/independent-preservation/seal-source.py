from pathlib import Path
import json,hashlib,os,resource
resource.setrlimit(resource.RLIMIT_DATA,(24*1048576,24*1048576))
P=Path('/workspace/scratch/default-clear-preservation-independent-r1')
R=Path('/workspace/Roguelike-deckbuilder')
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
proof=load(P/'SOURCE-PROOF.json');guard=load(P/'SOURCE-GUARD-r2/RESULT.json')
assert guard['exit_code']==0 and guard['failure'] is None
assert guard['memory_events_before']==guard['memory_events_after']
for q in proof['methods']+[proof['plan'],proof['sourceSeal'],proof['reviewControls'],proof['beforeMap'],proof['candidateFreeze'],proof['currentHEADSourcePin']]+proof['actualReviewGates']:assert pin(q['path'])=={k:q[k] for k in ['path','sha256','bytes']}
hold=pin(R/'AGENTS.md');assert hold['sha256']=='5535eb9614b43580396baa35af5e4610b506f3e2cc91645a27b4e1d29d9bbca9'
zpath=Path('/workspace/scratch/retained-original-archives/preflight-bdf273-original-r4.zip');s=os.lstat(zpath)
z={k:getattr(s,k) for k in proof['protectedZIPFullStat']}
prior=load(Path('/workspace/scratch/retained-native-zip-sharing-post-independent-r1/PROOF.json'))
assert z==proof['protectedZIPFullStat']==prior['protectedZIPFullStatAfter']
gate={'decision':'ACCEPT_CONDITIONAL_SOURCE_METHODS_ONLY','completeCoverage':False,'sourceProof':pin(P/'SOURCE-PROOF.json'),'review':pin(P/'SOURCE-REVIEW.md'),'sourcePlan':proof['plan'],'sourceSeal':proof['sourceSeal'],'methods':proof['methods'],'reviewControls':proof['reviewControls'],'actualReviewGates':proof['actualReviewGates'],'beforeMap':proof['beforeMap'],'candidateFreeze':proof['candidateFreeze'],'currentHold':hold,'currentHEAD':'c2050598c334fa390a61d1b385c309dc6fa17c87','ordinarySourceGuard':pin(P/'SOURCE-GUARD-r2/RESULT.json'),'retainedFailedReader':pin(P/'verify-source.py'),'retainedFailedGuard':pin(P/'SOURCE-GUARD/RESULT.json'),'correctedReader':pin(P/'verify-source-r2.py'),'sourceChildRSSBytes':proof['ownMaxRSSBytes'],'plannedLogicalBodies':370,'plannedUniqueBlobs':320,'plannedActualFiles':28,'aggregateAuditedCallerControls':37,'oldCallerBodies':34,'compactNewBodies':3,'fullOldAndCandidateBodiesChecked':288,'unchangedHeldMedia':51,'neededDependencies':204,'canonicalDistSuccessfulCount':56,'oldMainAndFiveOutputsRetentionRequired':True,'protectedZIPFullStatUnchanged':True,'protectedZIPBodyNeverOpened':True,'limits':['Source-only conditional eligibility, no constructed archive or roundtrip claim.','Root must allocate capsule256+512 and get independent COMPLETE GATE before selection; exact Root methods and external source pins only.','No selection-wide atomicity, automatic rollback, whole-power-loss durability or self-contained release claim. OldJS rename retained; transient57 then strict56 output leaves.','Narrow actual diagnostic pair acceptance; no fun, first300 improvement, engine/native/platform/version or dense/cancel/reduced-motion claim.','Sampled resource evidence and child RSS only; original review-count failure retained.'],'noReviewerGitArchiveConstructionPromotionEngineBrowserNodeMediaCleanup':True}
save(P/'SOURCE-GATE.json',gate)
files={str(p.relative_to(P)):pin(p) for p in sorted(P.rglob('*')) if p.is_file() and 'SEAL-GUARD' not in p.parts}
rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024;assert rss<24*1048576
seal={'phase':'IMMUTABLE_CONDITIONAL_SOURCE_REVIEW','files':files,'sourceGate':pin(P/'SOURCE-GATE.json'),'maxRSSBytes':rss,'packetLogicalCapBytes':96*1024,'runtimeSealGuardExcludedUntilExternalCompletion':True,'completeCapsulePhaseNotPerformed':True}
encoded=json.dumps(seal,separators=(',',':')).encode()
actual=sum(p.stat().st_size for p in P.rglob('*') if p.is_file());assert actual+len(encoded)+1+16384<=96*1024
save(P/'SOURCE-SEAL.json',seal)
fd=os.open(P,os.O_RDONLY|os.O_DIRECTORY)
try:os.fsync(fd)
finally:os.close(fd)
print(json.dumps({'sourceGate':pin(P/'SOURCE-GATE.json'),'sourceSeal':pin(P/'SOURCE-SEAL.json'),'measuredLogicalBytesBeforeGuardFinal':sum(p.stat().st_size for p in P.rglob('*') if p.is_file()),'reservedRuntimeGuardBytes':16384,'ownRSSBytes':rss,'allOwnFDsClosed':True}))
