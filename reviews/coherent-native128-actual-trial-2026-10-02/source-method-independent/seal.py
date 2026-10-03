import hashlib,json,os,pathlib,resource
P=pathlib.Path(__file__).parent
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(32768),b''):h.update(b)
 return h.hexdigest()
proof=json.loads((P/'PROOF.json').read_bytes());r=json.loads((P/'PROOF-GUARD-R2/RESULT.json').read_bytes());assert r['exit_code']==0 and r['failure'] is None and r['memory_events_before']==r['memory_events_after']
failed=json.loads((P/'PROOF-GUARD/RESULT.json').read_bytes());assert failed['exit_code']==1 and failed['failure'] is None
A='/workspace/scratch/pixel-cue-evidence-preserver-source-author-r3/'
gate={'decision':'ACCEPT_EXACT_R3_PRESERVATION_METHOD_SOURCE_ONLY_PENDING_ROOT_ACTIVATION_AND_COMPLETE_ARCHIVE_REVIEW','helper':{'path':A+'build-capsule.py','sha256':proof['pins']['build-capsule.py']},'plan':proof['plan'],'supplement':{'path':A+'SUPPLEMENT.json','sha256':proof['pins']['SUPPLEMENT.json']},'expectedInventories':{'path':A+'EXPECTED-INVENTORIES.json.gz','sha256':proof['pins']['EXPECTED-INVENTORIES.json.gz']},'authorManifestSHA256':proof['pins']['MANIFEST.json'],'authorFinalSHA256':proof['pins']['FINAL-SEAL.json'],'original38FullStatDigestsVerified':True,'current39NonAtimeAndXattrsExact':True,'currentAtimeOnlyDifferences':proof['currentAtimeOnlyDifferences'],'actualControlDomain':40,'sourceControlDomain':59,'retained37OriginalBytes':234807,'RootFinalThreeDocActivationRequired':proof['RootFinalThreeDocActivationRequired'],'closedReviewPins':proof['closedPixelReviewPins'],'futureArgv':proof['futureArgv'],'futureBudget':{'workMiB':256,'reserveMiB':512,'initialDiskMiB':74,'maxAllocatedOutputBytes':16*1048576},'newUIAndCueActualOutsideScope':True,'completeArchiveRoundtripNotYetExecuted':True,'limits':proof['limits'],'proofSHA256':digest(P/'PROOF.json'),'reviewSHA256':digest(P/'REVIEW.md'),'proofGuardSHA256':digest(P/'PROOF-GUARD-R2/RESULT.json'),'ownProofRSSKiB':proof['ownMaxRSSKiB'],'ownReviewCapBytes':64*1024,'noCleanupSelectionOrRuntimeAuthority':True}
b=(json.dumps(gate,separators=(',',':'))+'\n').encode();size=sum(p.stat().st_size for p in P.rglob('*') if p.is_file());assert size+len(b)+10000<64*1024,(size,len(b))
assert not (P/'GATE.json').exists();(P/'GATE.json').write_bytes(b)
rows=[{'path':str(p.relative_to(P)),'bytes':p.stat().st_size,'sha256':digest(p)} for p in sorted(P.rglob('*')) if p.is_file() and not str(p.relative_to(P)).startswith('SEAL-GUARD/')]
seal={'status':'SEALED_SOURCE_ONLY','gateSHA256':digest(P/'GATE.json'),'rows':rows,'capBytes':64*1024,'ownMaxRSSKiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'noProductionHelperExecution':True,'closure':'Final seal stdout/guard RESULT follow snapshot; returned guard proves closure, no remote/unobserved tool cancellation claim'}
assert seal['ownMaxRSSKiB']<=24576 and not (P/'FINAL-SEAL.json').exists();(P/'FINAL-SEAL.json').write_text(json.dumps(seal,separators=(',',':'))+'\n')
for n in ['GATE.json','FINAL-SEAL.json']:
 fd=os.open(P/n,os.O_RDONLY)
 try:os.fsync(fd)
 finally:os.close(fd)
print(json.dumps({'gateSHA256':digest(P/'GATE.json'),'sealSHA256':digest(P/'FINAL-SEAL.json'),'ownMaxRSSKiB':seal['ownMaxRSSKiB'],'logicalAtSeal':sum(p.stat().st_size for p in P.rglob('*') if p.is_file())}))
