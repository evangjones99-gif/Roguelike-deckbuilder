from pathlib import Path
import os,json,hashlib,resource
resource.setrlimit(resource.RLIMIT_DATA,(24*1048576,24*1048576))
P=Path('/workspace/scratch/next-five-png-sharing-independent-r1');S=P.parent;R=Path('/workspace/Roguelike-deckbuilder')
def pin(p):
 p=Path(p);fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME);h=hashlib.sha256();size=0
 with os.fdopen(fd,'rb') as f:
  for b in iter(lambda:f.read(65536),b''):h.update(b);size+=len(b)
 return {'path':str(p),'bytes':size,'sha256':h.hexdigest()}
def save(n,j):
 with (P/n).open('x') as f:json.dump(j,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
proof=json.loads((P/'PROOF.json').read_text());result=json.loads((P/'PROOF-GUARD/RESULT.json').read_text())
assert result['exit_code']==0 and result['failure'] is None and result['memory_events_before']==result['memory_events_after']
for old in [proof['proposal'],proof['authorSeal'],proof['selectedMap'],*proof['methodsFullPinnedASTParsedUnexecuted'],*proof['sourceControls']]:
 q=pin(old['path']);assert q['sha256']==old['sha256'] and q['bytes']==old['bytes']
assert proof['grossAllocationBytes']==10170368 and proof['ownMaxRSSBytes']<24*1048576
def simple(q):return {'path':q['path'],'sha256':q['sha256']}
hold=next(q for q in proof['sourceControls'] if q['path']==str(R/'AGENTS.md'))
gate={'decision':'ACCEPT_CONDITIONAL_EXACT_FIVE_PATH_PHYSICAL_SHARING_ONLY','replacementBetter':True,'oldRedundantPrivatePhysicalEncodingsNoLongerNeeded':True,'everyLogicalPathBodyStillNeeded':True,'method':simple(proof['methodsFullPinnedASTParsedUnexecuted'][0]),'publisher':simple(proof['methodsFullPinnedASTParsedUnexecuted'][1]),'producerMethod':simple(proof['methodsFullPinnedASTParsedUnexecuted'][2]),'proposal':simple(proof['proposal']),'authorSeal':simple(proof['authorSeal']),'currentHold':simple(hold),'selectedMap':simple(proof['selectedMap']),'independentProof':pin(P/'PROOF.json'),'independentReview':pin(P/'REVIEW.md'),'candidateGroup':'/workspace/scratch/audio-host-independent-v08/candidate/dist/art','names':['adversaries-atlas.png','companions-atlas.png','hound-poses.png','pact-seal.png','warleader-poses.png'],'grossAllocationBytes':10170368,'independentPacketCapBytes':98304,'publicationOtherCopiedBodyBytes':proof['publicationBaseCopiedBodyBytes'],'publicationConservativeCopiedBodyUpperBound':proof['publicationConservativeCopiedBodyUpperBound'],'publicationCopiedBodyCapBytes':524288,'conditions':['Root sole producer records exact once-only judgment only after fresh current confirmed clean publication push','Normal64MiB disk and64+512MiB work/reserve guard admission and live stops remain unchanged','Action fresh full10 body metadata/xattr preflight and current143 identity before/after, protected ZIP stat exact','Every path/body/source/review/rights/provenance/rollback remains; four-raw proposal unexecuted; no other action','No active original-inode/time-sensitive consumer or private writable-isolation need; future reproduction in NEW stages/inodes'],'limitations':['Five old inode/time/write isolation surrendered; byte/path rollback requires new copies, original inode/ctime history not recoverable','Known metadata alias inventory gaps1,1,1,0,1; unknown aliases/Fds/mmap/future consumers not disproved','Coordinated immutable holds are not OS protection','Durable per-leaf prefix, no all-five atomicity/automatic rollback or automatic retry','Publisher receipt file and its P directory fsynced, outer scratch directory entry not separately fsynced','Gross allocation is not exact net gain; publication generated metadata/Git/logs/allocation overhead outside copied-body bound','Historical66/51 and selected87/56 full body aggregates not independently replayed; five entries and exact maps verified','No game improvement/commercial rights/release claim; no image decode/build/Node/browser/Git/action executed by reviewer'],'proofGuardNormal':True,'allProofInputFDsClosed':True,'sealClosure':'Root must await this SEAL-GUARD result0 and unchanged memory events before any further stage; seal guard outputs not recursively included in manifest.'}
save('GATE.json',gate)
members=[]
for p in sorted(P.rglob('*')):
 if p.is_file() and 'SEAL-GUARD' not in p.parts:members.append(pin(p))
total=sum(q['bytes'] for q in members);assert total+8192<98304
save('FINAL-SEAL.json',{'decision':gate['decision'],'files':members,'packetBytesBeforeSeal':total,'ownMaxRSSBytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,'packetCapBytes':98304,'conservativeAdditionalSealGuardAndSealBytes':8192,'publisherOtherCopiedBytes':proof['publicationBaseCopiedBodyBytes'],'publicationConservativeCopiedBodyUpperBound':proof['publicationConservativeCopiedBodyUpperBound'],'closure':gate['sealClosure']})
fd=os.open(P,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
try:os.fsync(fd)
finally:os.close(fd)
assert resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024<24*1048576
print(json.dumps({'gate':pin(P/'GATE.json'),'finalSeal':pin(P/'FINAL-SEAL.json'),'packetBeforeSeal':total,'ownMaxRSSBytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,'allFDsClosed':True}))
