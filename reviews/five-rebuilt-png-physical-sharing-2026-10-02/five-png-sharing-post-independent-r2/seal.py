from pathlib import Path
import os,json,hashlib,resource
resource.setrlimit(resource.RLIMIT_DATA,(24*1048576,24*1048576))
P=Path('/workspace/scratch/five-png-sharing-post-independent-r2')
def pin(p):
 p=Path(p);fd=os.open(p,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW);h=hashlib.sha256();size=0
 with os.fdopen(fd,'rb') as f:
  for b in iter(lambda:f.read(65536),b''):h.update(b);size+=len(b)
 return {'path':str(p),'bytes':size,'sha256':h.hexdigest()}
def save(n,j):
 with (P/n).open('x') as f:json.dump(j,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
proof=json.loads((P/'PROOF.json').read_text());result=json.loads((P/'PROOF-GUARD-r2/RESULT.json').read_text())
assert result['exit_code']==0 and result['failure'] is None and result['memory_events_before']==result['memory_events_after']
assert len(proof['fullTenBodiesAndStatsXattrs'])==5 and len(proof['fullCurrent143Bodies'])==143 and len(proof['journalRows'])==15
for q in [proof['proposal'],proof['admissionGate'],proof['priorPhysicalGate'],proof['priorTenBodyProof'],proof['producer'],proof['confirmedPush'],proof['actionBefore'],proof['actionResult'],proof['actionJournal'],*proof['sourceHoldAndMapPins']]:
 z=pin(q['path']);assert z['sha256']==q['sha256'] and z['bytes']==q['bytes']
assert proof['protectedZipStatBefore']==proof['protectedZipStatAfter'] and proof['protectedZipBodyNeverOpened'] and proof['ownMaxRSSBytes']<24*1048576
gate={'decision':'ACCEPT_COMPLETED_EXACT_FIVE_PNG_PHYSICAL_SHARING_POST_ONLY','proof':pin(P/'PROOF.json'),'review':pin(P/'REVIEW.md'),'methodNotes':pin(P/'METHOD-NOTES-r1.json'),'normalPostGuard':pin(P/'PROOF-GUARD-r2/RESULT.json'),'tenFullBodiesAndFreshSnapshotsExact':True,'allCurrent143BodiesExact':True,'canonicalNlinks':[5,5,5,4,5],'nlinkDeltaEach':1,'emptyMediaXattrsExact':True,'fifteenOrderedJournalRowsVerified':True,'allTempsAbsent':True,'protectedZipFullStatBeforeAfterExactBodyNeverOpened':True,'sourceHoldProposalProducerGatePushPinsExact':True,'originalMetadataRetained':True,'atimeQualification':'Action-to-POST atime advances recorded; all other action-result fields exact; no timestamp reset. Original failed exact-atime source/log/guard preserved.','grossAllocationBytes':10170368,'actionPreResultNetWindowGainBytes':10141696,'limits':['Historical full66/51 aggregate not newly replayed; current143 full bodies freshly verified','Known unresolved physical alias gaps1,1,1,0,1; no global FD/mmap/future consumer or OS read-only claim','Five private inode/time/write isolation lost; no exact inode/ctime rollback or old-inode backup','Returned fsync per-leaf prefix/source/records verified; no crash injection/all-five atomicity/automatic rollback or retry','Historical window free-space gain not exclusive actor attribution or exact final recovery','Confirmed receipt checked; no new Git/network operation by reviewer','No game/art/rights completion claim; no additional action or cleanup authority'],'normal64DiskWork64Reserve512Post':True,'allSuccessfulProofFDsAndChildrenClosed':True,'packetCapBytes':131072,'sealClosure':'Await normal SEAL-GUARD result0; current seal guard outputs are not recursively included in FINAL-SEAL manifest.'}
save('GATE.json',gate)
members=[pin(p) for p in sorted(P.rglob('*')) if p.is_file() and 'SEAL-GUARD' not in p.parts];total=sum(q['bytes'] for q in members);assert total+8192<131072
rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024;assert rss<24*1048576
save('FINAL-SEAL.json',{'decision':gate['decision'],'files':members,'packetBytesBeforeSeal':total,'conservativeAdditionalSealGuardAndSealBytes':8192,'packetCapBytes':131072,'ownMaxRSSBytes':rss,'closure':gate['sealClosure']})
fd=os.open(P,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
try:os.fsync(fd)
finally:os.close(fd)
print(json.dumps({'gate':pin(P/'GATE.json'),'finalSeal':pin(P/'FINAL-SEAL.json'),'packetBeforeSeal':total,'ownMaxRSSBytes':rss,'allFDsClosed':True}))
