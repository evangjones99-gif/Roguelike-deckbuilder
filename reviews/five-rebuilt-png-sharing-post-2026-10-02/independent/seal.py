from pathlib import Path
import os,json,hashlib,resource
resource.setrlimit(resource.RLIMIT_DATA,(24*1048576,24*1048576))
P=Path('/workspace/scratch/five-rebuilt-png-sharing-post-independent-r1');S=P.parent
def pin(p):
 p=Path(p);fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME);h=hashlib.sha256();size=0
 with os.fdopen(fd,'rb') as f:
  for b in iter(lambda:f.read(65536),b''):h.update(b);size+=len(b)
 return {'path':str(p),'bytes':size,'sha256':h.hexdigest()}
def save(n,j):
 with (P/n).open('x') as f:json.dump(j,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
proof=json.loads((P/'PROOF.json').read_text());g=json.loads((P/'PROOF-GUARD/RESULT.json').read_text());assert g['exit_code']==0 and g['failure'] is None and g['memory_events_before']==g['memory_events_after']
assert len(proof['fullTenBodiesAndStatsXattrs'])==5 and len(proof['fullCurrent143Bodies'])==143 and len(proof['journalRows'])==15
assert [x['canonical']['metadata']['st_nlink'] for x in proof['fullTenBodiesAndStatsXattrs']]==[6,6,6,5,6]
assert proof['actionResult']['sha256']=='0a323350d510a8791d333535c2cacd54f65d70b29ee7aed3c06111d68da69a0e'
for q in [proof['proposal'],proof['admissionGate'],proof['producer'],proof['confirmedPush'],proof['actionBefore'],proof['actionResult'],proof['actionJournal'],*proof['sourceHoldAndMapPins']]:
 z=pin(q['path']);assert (z['sha256'],z['bytes'])==(q['sha256'],q['bytes'])
guards=[]
for name,work in [('five-rebuilt-png-publication-guard-root-r1',256),('five-rebuilt-png-producer-guard-root-r1',64),('five-rebuilt-png-sharing-guard-root-r1',64)]:
 path=S/name;ad=json.loads((path/'ADMISSION.json').read_text());r=json.loads((path/'RESULT.json').read_text());assert ad['admitted'] and ad['work']==work*1048576 and ad['reserve']==512*1048576 and r['exit_code']==0 and r['failure'] is None and r['memory_events_before']==r['memory_events_after']
 guards.append({'name':name,'workMiB':work,'admission':pin(path/'ADMISSION.json'),'result':pin(path/'RESULT.json'),'executionLog':pin(path/'EXECUTION.log'),'normal':True})
assert proof['protectedZipStatBefore']==proof['protectedZipStatAfter'] and proof['protectedZipBodyNeverOpened']
gate={'decision':'ACCEPT_COMPLETED_EXACT_REBUILT_FIVE_PHYSICAL_SHARING_POST_ONLY','proof':pin(P/'PROOF.json'),'review':pin(P/'REVIEW.md'),'normalOriginal64PostGuard':pin(P/'PROOF-GUARD/RESULT.json'),'RootGuardControls':guards,'fullTenMediaBodiesAndFreshMetadataExact':True,'fullCurrent143BodiesExact':True,'nlinks':[6,6,6,5,6],'nlinkIncrementEach':1,'allEmptyMediaXattrsExact':True,'orderedFifteenJournalRecordsVerified':True,'allTempsAbsent':True,'originalMetadataRetained':True,'atimeQualification':'Action-to-POST observation stored; other exact stat fields and fresh stable O_NOATIME snapshots preserved, no timestamp reset or action retry','protectedZipFullStatExactBodyNeverOpened':True,'sourceProposalHoldMapProducerPushGatePinsExact':True,'grossAllocationBytes':10170368,'actionPreResultNetWindowGainBytes':10137600,'limitations':['Per-leaf durable prefix verified from exact source/returned guards/journal; no crash injection/all-five atomicity/automatic rollback or retry','Private inode/time/write isolation lost; no original-inode backup/exact inode/ctime rollback','Known physical alias gaps1,1,1,0,1; no global FD/mmap/future consumer absence/OS hold claim','Historical full66/51 aggregate not replayed; current143 bodies freshly verified','No fresh Git/network operation by reviewer; confirmed receipt chronology checked','Window gain not exclusive actor attribution/final recovery; no game/art/R3/rights completion or further storage action claim'],'noNewVerifierFailure':True,'allObservedProofFDsAndChildrenClosed':True,'packetCapBytes':131072,'sealClosure':'Await original64+512 SEAL-GUARD normal0; its files not recursively included in seal manifest.'}
save('GATE.json',gate)
members=[pin(p) for p in sorted(P.rglob('*')) if p.is_file() and 'SEAL-GUARD' not in p.parts];total=sum(q['bytes'] for q in members);assert total+8192<131072
rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024;assert rss<24*1048576
save('FINAL-SEAL.json',{'decision':gate['decision'],'files':members,'packetBytesBeforeSeal':total,'additionalSealGuardAndSealConservativeBytes':8192,'packetCapBytes':131072,'ownMaxRSSBytes':rss,'closure':gate['sealClosure']})
fd=os.open(P,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
try:os.fsync(fd)
finally:os.close(fd)
print(json.dumps({'gate':pin(P/'GATE.json'),'finalSeal':pin(P/'FINAL-SEAL.json'),'packetBeforeSeal':total,'ownMaxRSSBytes':rss,'allFDsClosed':True}))
