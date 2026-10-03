from pathlib import Path
import os,json,hashlib,resource
resource.setrlimit(resource.RLIMIT_DATA,(24*1048576,24*1048576))
P=Path('/workspace/scratch/five-rebuilt-png-sharing-independent-r1')
def pin(p):
 p=Path(p);fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME);h=hashlib.sha256();size=0
 with os.fdopen(fd,'rb') as f:
  for b in iter(lambda:f.read(65536),b''):h.update(b);size+=len(b)
 return {'path':str(p),'sha256':h.hexdigest(),'bytes':size}
def save(n,j):
 with (P/n).open('x') as f:json.dump(j,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
proof=json.loads((P/'PROOF.json').read_text());fresh=json.loads((P/'REFRESH.json').read_text())
for guard in ['PROOF-GUARD','REFRESH-GUARD']:
 q=json.loads((P/guard/'RESULT.json').read_text());assert q['exit_code']==0 and q['failure'] is None and q['memory_events_before']==q['memory_events_after']
assert pin(P/'PROOF.json')==fresh['oldProof']
for q in fresh['freshPins']:assert pin(q['path'])==q
method,publisher,producer=proof['methods'];hold=next(q for q in proof['sourceControls'] if q['path'].endswith('/Roguelike-deckbuilder/AGENTS.md'))
assert len(fresh['freshTenFullBodiesAndStableMetadata'])==5 and fresh['currentFiveMapEntriesMatch'] and fresh['protectedZipStatBefore']==fresh['protectedZipStatAfter']
gate={'decision':'ACCEPT_CONDITIONAL_EXACT_REBUILT_FIVE_PHYSICAL_SHARING_ONLY','replacementBetter':True,'oldRedundantPrivatePhysicalEncodingsNoLongerNeeded':True,'everyLogicalPathBodyStillNeeded':True,'proposal':proof['proposal'],'method':method,'publisher':publisher,'producer':producer,'currentHold':hold,'selectedMap':proof['selectedMap'],'proof':pin(P/'PROOF.json'),'refreshProof':pin(P/'REFRESH.json'),'review':pin(P/'REVIEW.md'),'firstPOSTControls':proof['firstPOSTControls'],'R3CompleteGate':proof['R3CompleteGate'],'R3Preservation':proof['R3Preservation'],'R3ExistingCapsule':proof['R3ExistingCapsuleFullEncodingSHA'],'candidateGroup':'/workspace/scratch/audio-host-independent-v08/independent/rebuilt-dist/art','names':['adversaries-atlas.png','companions-atlas.png','hound-poses.png','pact-seal.png','warleader-poses.png'],'grossAllocationBytes':10170368,'normalOriginalGuard':pin(P/'PROOF-GUARD/RESULT.json'),'normalFreshGuard':pin(P/'REFRESH-GUARD/RESULT.json'),'bounds':{'rootAllocatedPacketCapBytes':163840,'reviewTargetBytes':131072,'reviewFileCountLimit':24,'publisherCopiedKnownBytes':294650,'publisherKnownIdentityBytes':32027,'publisherConservativeTotalPublicationUpperBound':481397,'publisherCapBytes':524288,'publisherDiskPreflightBytes':70254592,'qualification':'64MiB+3MiB modeled disk reserve; copied/logical bounds exclude unbounded Git/log/allocation cost. Measure actual objects/free; fresh ordinary64 producer/action may refuse, no56 exception.'},'conditions':['Fresh exact-source publication of complete existing R3 review/capsule, AGENTS, first POST/actual/control records and proposal/gate/methods; confirmed remote=currentHEAD clean push then durable Root producer judgment','Action freshfull10 stat/body/xattrs, current143 before/after and protectedZIP stat exact; original64 disk/64+512 action admission unchanged','External sole canonical writer; no live original-inode/time-sensitive/private writable need; reproduction uses NEW stages/inodes','Only five redundant physical encodings; all logical paths/bodies/source/rights/provenance/reviews/rollback retained; no automatic action retry'],'limitations':['Known gaps1,1,1,0,1; no universal aliases/Fds/mmap/future consumer absence/OS hold claim','Private inode/time/write isolation lost; no original-inode backup/exact metadata rollback/all-five atomicity','Durable per-leaf prefix; failures require preservation/diagnosis, no automatic restoration','Historical66/51/current143 aggregates not replayed here; five map entries/full10 fresh bodies verified; action current143 strict','R3 logical complete roundtrip gate reused; encodingSHA fresh; dependencies not self-contained, no default/game/rights promotion','Publisher/Git reserve estimate and fsync calls not universal cost/power-loss/exclusive attribution/net gain proof','Outage pending editor locally terminated without observed remote completion; recovered stage found no final controls; original proof preserved and19 pins/full10 refreshed under original guard'],'allObservedProofFDsAndChildrenClosed':True,'noActionExecutedByReviewer':True,'sealClosure':'Root must await original64+512 SEAL-GUARD result0; seal guard files not recursively included in manifest.'}
save('GATE.json',gate)
members=[pin(p) for p in sorted(P.rglob('*')) if p.is_file() and 'SEAL-GUARD' not in p.parts];total=sum(q['bytes'] for q in members)
assert total+8192<131072 and len(members)+4<=24
rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024;assert rss<24*1048576
save('FINAL-SEAL.json',{'decision':gate['decision'],'files':members,'packetBytesBeforeSeal':total,'rootAllocatedCapBytes':163840,'targetCapBytes':131072,'fileCountLimit':24,'conservativeAdditionalSealGuardAndSealBytes':8192,'publisherConservativeTotalPublicationUpperBound':481397,'ownMaxRSSBytes':rss,'closure':gate['sealClosure']})
fd=os.open(P,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
try:os.fsync(fd)
finally:os.close(fd)
print(json.dumps({'gate':pin(P/'GATE.json'),'finalSeal':pin(P/'FINAL-SEAL.json'),'packetBeforeSeal':total,'ownMaxRSSBytes':rss,'allFDsClosed':True}))
