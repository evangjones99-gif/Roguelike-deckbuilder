import hashlib,json,os,pathlib,resource
P=pathlib.Path(__file__).parent
def hashfile(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(32768),b''):h.update(b)
 return h.hexdigest()
proof=json.loads((P/'PROOF.json').read_bytes());r=json.loads((P/'PROOF-GUARD-R2/RESULT.json').read_bytes());assert r['exit_code']==0 and r['failure'] is None and r['memory_events_before']==r['memory_events_after']
failed=json.loads((P/'PROOF-GUARD/RESULT.json').read_bytes());assert failed['exit_code']==1 and failed['failure'] is None
gate={'decision':'ACCEPT_COMPLETE_DECLARED_PIXEL_AND_EARLIER_CUE_EVIDENCE_PRESERVATION_ONLY','scope':'Independent complete retained archive/body/logical-map preservation; no cleanup or art/default acceptance','archive':proof['archive'],'index':proof['index'],'readObservations':proof['readObservations'],'rootResult':proof['rootResult'],'rootGuard':proof['rootGuard'],'sourceGate':proof['sourceGate'],'activationSHA256':proof['activationSHA256'],'coverage':{'logicalBodies':831,'uniqueFullArchiveBodies':697,'all831OriginalBodiesIndependentlyHashEqual':True,'exactLogicalMembership':True,'threeFullMaps':proof['threeFrozenFullMaps'],'actualControlDomain':40,'sourceControlDomain':59,'formerlyMissing37Bytes':234807,'twoMastersExact':True,'sixUniqueSpritesAllRetainedOriginalPaths':True,'sixCompleteUTF8SavePairsEqual':True,'oldReviewPins':proof['oldReviewPins'],'rootThreeDocsExactActivation':True,'dependencyOccurrences':312,'externalMediaOccurrences':303,'selfContainedRelease':False},'protectedZIPBodyRead':False,'protectedZIPFullStatAndXattrsUnchanged':True,'expectedAtimeDifferencesRecorded':proof['expectedAtimeDifferencesRecorded'],'freshAtimeOnlyDifferences':proof['freshAtimeOnlyDifferences'],'outputAllocatedBytes':proof['outputAllocatedBytes'],'limits':proof['limits'],'proofSHA256':hashfile(P/'PROOF.json'),'reviewSHA256':hashfile(P/'REVIEW.md'),'proofGuardSHA256':hashfile(P/'PROOF-GUARD-R2/RESULT.json'),'ownProofRSSKiB':proof['ownMaxRSSKiB'],'packetCapBytes':64*1024,'noCleanupActionAuthority':True}
b=(json.dumps(gate,separators=(',',':'))+'\n').encode();size=sum(x.stat().st_size for x in P.rglob('*') if x.is_file());assert size+len(b)+10000<64*1024,(size,len(b))
assert not (P/'GATE.json').exists();(P/'GATE.json').write_bytes(b)
rows=[{'path':str(x.relative_to(P)),'sha256':hashfile(x),'bytes':x.stat().st_size} for x in sorted(P.rglob('*')) if x.is_file() and not str(x.relative_to(P)).startswith('SEAL-GUARD/')]
seal={'status':'SEALED_COMPLETE_PRESERVATION_REVIEW','gateSHA256':hashfile(P/'GATE.json'),'rows':rows,'packetCapBytes':64*1024,'ownMaxRSSKiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'closure':'Final seal stdout and guard receipt appended after snapshot; returned normal guard confirms closure','noOriginalEvidenceModified':True,'noFurtherActionAuthority':True}
assert seal['ownMaxRSSKiB']<=24576 and not (P/'FINAL-SEAL.json').exists();(P/'FINAL-SEAL.json').write_text(json.dumps(seal,separators=(',',':'))+'\n')
for n in ['GATE.json','FINAL-SEAL.json']:
 fd=os.open(P/n,os.O_RDONLY)
 try:os.fsync(fd)
 finally:os.close(fd)
print(json.dumps({'gateSHA256':hashfile(P/'GATE.json'),'sealSHA256':hashfile(P/'FINAL-SEAL.json'),'ownMaxRSSKiB':seal['ownMaxRSSKiB'],'logicalAtSeal':sum(x.stat().st_size for x in P.rglob('*') if x.is_file())}))
