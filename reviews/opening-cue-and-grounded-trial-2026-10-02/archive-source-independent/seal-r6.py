import os,json,hashlib,resource
from pathlib import Path
P=Path(__file__).parent;A=Path('/workspace/scratch/wording-grounded-trials-checkpoint-source-author-r1')
def body(v):return (json.dumps(v,indent=2,sort_keys=True)+'\n').encode()
def pin(p):
 h=hashlib.sha256();n=0
 with p.open('rb')as f:
  while chunk:=f.read(65536):h.update(chunk);n+=len(chunk)
 return {'path':str(p),'bytes':n,'sha256':h.hexdigest()}
checks=json.loads((P/'SOURCE-CHECKS.json').read_bytes());ids=json.loads((P/'IDENTITIES.json').read_bytes())
guards=[]
for d in sorted(P.glob('source-guard-*')):
 r=json.loads((d/'RESULT.json').read_bytes());assert r['exit_code']==0 and r['failure'] is None and r['memory_events_before']==r['memory_events_after']
 guards.append({'path':str(d),'resultSHA256':pin(d/'RESULT.json')['sha256'],'normalExit':0,'samples':len(r['samples']),'minimumSampledHeadroomBytes':min(x['headroom'] for x in r['samples']),'childGroupClosure':r['scope']})
review={'decision':'ACCEPT_CHECKPOINT_ARCHIVE_CONSTRUCTION_SOURCE_ONLY','sourceOnly':True,
 'findings':['The exact four substitutions reproduce the published predecessor and invert completely. The helper adds a second inherited capsule reference without changing archive construction semantics; it corrects the earlier overstated stat field to inode/size/mtime-only checks.',
 'All 952 root/relative-leaf/SHA/length/role/storage rows are bounded and safe. All 722 newBlob occurrences match live original SHA and length; their 711 unique bodies total 14,555,377 bytes. All 227 ce0f and three f912 references match the exact prior indexes. Both prior COMPLETE gate bodies independently match the pinned accepted hashes, with archive decoding inherited rather than repeated.',
 'The complete eight original JPEGs for each of the two actuals, both forty-control sets, source and failure histories, all seven unchanged review decisions, all three frozen runtime authorities and four held metadata documents are present or explicitly retained dependencies. New optional starter master and negative alpha/expiry evidence remain unimplemented and rejected as applicable; the mutable successor is excluded.',
 'New tar names are exact blobs/<lowercase SHA256>, regular files only. Streaming write hashes full original bytes; streaming readback rejects duplicates, wrong sizes and unexpected names and compares full bytes without filesystem extraction. The known plan supplies the path bounds; the helper is eligible only with this pinned plan.',
 'Root must use fresh output, outer 128 MiB work plus 512 MiB reserve and disk minimum 64 MiB, while the helper checks own RSS at 24 MiB, elapsed 60 seconds, and output cap 16 MiB. Compression estimate is provisional. Actual guard, terminal stdout, full readback, total logical and allocated output and independent COMPLETE review remain required.'],
 'limits':['No archive was created, no prior archive or protected release was decoded, and no build, native game, publication, canonical edit, deletion, selection or asset transformation occurred.',
 'Existing archive bodies and nested logical gzip decode were not repeated in this SOURCE lane. Exact stored bodies, prior indexes and prior accepted COMPLETE gates bind those inherited proofs; the future helper rehashes both compressed archives and indexes.',
 'Final-leaf O_NOFOLLOW and requested O_NOATIME protect reads only within workflow holds. Parent directories are not held by directory descriptors; no OS race, universal future consumer, full stat/xattr preservation or metadata replay guarantee is claimed. EPERM fallback can advance atime and is recorded.',
 'Files are flushed and fsynced, but the helper does not fsync directory entries after mkdir/rename. This acceptance makes no directory crash-durability or fully atomic rollback claim. Failed partial outputs must be retained; publication requires a later separate method and approval.',
 'The capsule depends on both published prior capsules, their exact indexes and COMPLETE proofs, the unchanged published predecessor support, external held game media, historical master references and installed node_modules. It is not a self-contained release.',
 'The original pixel visual/default rejection and false transient coverage remain unchanged. Preservation acceptance does not approve courtyard depth, sustained corpse payoff, default pixel selection, animation, first300 coverage or human enjoyment.'],
 'readQualification':{'guardedSourceChecks':guards,'maxRecordedOwnRSSBytes':checks['ownRSSBytes'],'guardSamplesNotContinuousOrExclusive':True,'tinySourceBootstrapAndAdaptiveReadbackUnmetered':True,'adaptiveReadsUsedOrdinaryJSONReadsMayAdvanceAtime':True,'explicitTimestampWrites':False,'finalSealerTinyUnmeteredNoResourceGuardClaim':True},
 'reviewMethodFailures':{'failedR1Directory':str(P.parent/'wording-grounded-trials-checkpoint-source-independent-r1'),'failedR1Bytes':ids['failedR1Bytes'],'failedR1Pins':'IDENTITIES.json','failure':'Printed full PLAN into original guarded EXECUTION.log; that retained r1 exceeded its initial 128 KiB cap and remains failed. Root authorized fresh r2 with separate 128 KiB allocation; r1 is excluded from r2 cap and remains needed, pinned, unchanged.','adaptiveUnmeteredReadFailure':'One finite standard-library source read attempted nonexistent runtimeAuthorities.freeze and exited KeyError before any write; corrected to freezePath. Tool return only, no false guarded success.','largeToolReturnTruncation':'One readback tail was truncated; conclusions use full bounded process reads and compact SOURCE-CHECKS, not that truncated display.'},
 'sourceChecks':pin(P/'SOURCE-CHECKS.json'),'referenceChecks':pin(P/'REFERENCE-CHECKS.json'),'originalsRetained':True,'allOwnObservedGuardChildrenClosed':True}
review['reviewMethodFailures']['firstFinalSealer']='seal-r5.py failed its own RSS assertion before any final-control writes; preserved unchanged. Its exact numeric RSS was not emitted. A later finite source probe showed inherited process ru_maxrss 98720 KiB, which does not identify current reviewer resident use. Fresh sealer streams hashes and executes in a forked bounded source child with a fresh own-usage counter; tool transport and bootstrap remain unmetered.'
gate={'decision':review['decision'],'sourceOnly':True,'archiveSourceEligible':True,'preservationSourceEligible':True,'plan':pin(A/'PLAN.json'),'method':pin(A/'preserve-checkpoint.py'),'authorManifest':pin(A/'MANIFEST.json'),'authorFinalSeal':pin(A/'FINAL-SEAL.json'),'reviewedGuardProfile':{'workMiB':128,'reserveMiB':512,'diskMinimumMiB':64,'ownRSSCapBytes':25165824,'methodWholeCeilingSeconds':60,'logicalAndAllocatedOutputCapBytes':16777216},'requiresRootActualGrant':True,'requiresIndependentCompletePreservationReview':True,'publicationOrSelectionAuthorized':False,'oldInputsRemovalAuthorized':False,'sourceAlgorithmApprovalIsNotActualPreservationOrArtApproval':True,'TOOL_GUARD_CLOSED':True}
pending={'REVIEW.json':body(review),'GATE.json':body(gate)}
existing=[dict(pin(x),relativePath=str(x.relative_to(P)))for x in sorted(P.rglob('*'))if x.is_file()]
manifest={'sourceOnly':True,'acceptedFamilyCapBytes':131072,'failedR1SeparateNeededPreserved':True,'failedR1Bytes':ids['failedR1Bytes'],'bodies':existing+[{'path':str(P/k),'relativePath':k,'bytes':len(v),'sha256':hashlib.sha256(v).hexdigest()}for k,v in pending.items()]}
pending['MANIFEST.json']=body(manifest)
base=sum(x['bytes']for x in existing)+sum(len(v)for v in pending.values())
final={'sealed':True,'sourceOnly':True,'archiveExecuted':False,'TOOL_GUARD_CLOSED':True,'manifestSHA256':hashlib.sha256(pending['MANIFEST.json']).hexdigest(),'gateSHA256':hashlib.sha256(pending['GATE.json']).hexdigest(),'reviewSHA256':hashlib.sha256(pending['REVIEW.json']).hexdigest(),'acceptedR2CapBytes':131072,'failedR1Bytes':ids['failedR1Bytes'],'acceptedR2LogicalBytes':0,'combinedNeededReviewLogicalBytes':0,'sealerOwnRSSBytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,'sealerGuarded':False}
for _ in range(5):
 size=base+len(body(final));final['acceptedR2LogicalBytes']=size;final['combinedNeededReviewLogicalBytes']=size+ids['failedR1Bytes']
pending['FINAL-SEAL.json']=body(final);assert base+len(pending['FINAL-SEAL.json'])==final['acceptedR2LogicalBytes']<=131072
assert final['sealerOwnRSSBytes']<24*1048576
for k,v in pending.items():
 with (P/k).open('xb')as f:f.write(v);f.flush();os.fsync(f.fileno())
fd=os.open(P,os.O_DIRECTORY|os.O_RDONLY);os.fsync(fd);os.close(fd)
assert sum(x.stat().st_size for x in P.rglob('*')if x.is_file())==final['acceptedR2LogicalBytes']
print(json.dumps(final,sort_keys=True))
