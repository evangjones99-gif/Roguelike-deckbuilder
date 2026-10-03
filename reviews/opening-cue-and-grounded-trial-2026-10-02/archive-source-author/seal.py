import ast,hashlib,json,pathlib,resource
P=pathlib.Path('/workspace/scratch/wording-grounded-trials-checkpoint-source-author-r1');R=pathlib.Path('/workspace/Roguelike-deckbuilder')
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def j(p):return json.loads(pathlib.Path(p).read_bytes())
proof=j(P/'SOURCE-PROOF.json');plan=j(P/'PLAN.json');guard=j(P/'PLAN-GUARD-R1/RESULT.json')
assert guard['exit_code']==0 and guard['failure'] is None and guard['memory_events_before']==guard['memory_events_after']
assert sha(P/'PLAN.json')==proof['planSHA256'] and sha(P/'preserve-checkpoint.py')==proof['helperSHA256']
for doc in plan['metadataSnapshot']['docs']:assert sha(doc['path'])==doc['sha256']
for gate in plan['originalReviewGatesVerbatim']:assert sha(gate['path'])==gate['sha256']
baseline=R/'reviews/opening-turn-payoff-default-2026-10-02/source-author/preserve-checkpoint.py';assert sha(baseline)=='367ea7aeeb38186cc546c0bf52ee5e0e65e7705f9dda6d7ccf27c4097c441a69'
baselineSupport={'path':str(baseline),'sha256':sha(baseline),'bytes':baseline.stat().st_size,'status':'Exact published f912 preserver baseline, required external provenance support; already retained original, not recopied or inside new TAR member table.','existingPublishedFamily':'/workspace/Roguelike-deckbuilder/reviews/opening-turn-payoff-default-2026-10-02','doNotRemove':True}
inv=j(P/'METHOD-INVERSE.json');s=(P/'preserve-checkpoint.py').read_text();ast.parse(s);compile(s,str(P/'preserve-checkpoint.py'),'exec')
for item in reversed(inv['changes']):assert s.count(item['after'])==1;s=s.replace(item['after'],item['before'])
assert hashlib.sha256(s.encode()).hexdigest()==baselineSupport['sha256']
assert not (R/'src/opening-turn-payoff.css').exists()
rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss;assert rss<=24576
manifest={'sealed':True,'sourceOnly':True,'archiveOrPublisherExecuted':False,'requiresIndependentSourceReviewRootActualGrantAndCompleteReview':True,'bodies':[{'name':n,'bytes':(P/n).stat().st_size,'sha256':sha(P/n)} for n in ['PLAN.json','preserve-checkpoint.py']],'methodInverseSHA256':sha(P/'METHOD-INVERSE.json'),'proofSHA256':sha(P/'SOURCE-PROOF.json'),'scope':'Two distinct actual hypotheses preserved without converting negative pixel/expiry/alpha findings into acceptance. No publisher authored.','sourceFamilyLogicalCapBytes':256*1024,'baselineRequiredPublishedSupport':baselineSupport,'fourPriorPushedMetadataDocsHeldThroughArchive':True,'optionalUnimplementedMasterAndNegativePrototypesIncluded':True}
close={'status':'TOOL_GUARD_CLOSED_SOURCE_ONLY_AFTER_OUTER_SEAL_RETURNS','logicalRows':proof['logicalRows'],'newUniqueBodies':proof['newUniqueBodies'],'newUniqueOriginalBytes':proof['newUniqueOriginalBytes'],'gzipEstimateExcludesTarAndReceipts':proof['gzipEstimateBytes'],'existingReferenceOccurrences':230,'actualArchiveOutputCapBytes':16*1048576,'proposedActualWorkMiB':128,'proposedActualReserveMiB':512,'sourceGuardResultSHA256':sha(P/'PLAN-GUARD-R1/RESULT.json'),'sourceGuardNormalExit':0,'sourceOwnMaxRSSKiB':proof['ownRSSKiB'],'sealOwnRSSKiB':rss,'completeHelperInverse':True,'originalsArchivesCanonicalCodeMetadataUntouched':True,'scopeFailuresAndNegativeReviewsRetained':True,'universalAtimeMetadataClosureClaim':False,'archivePublisherGitSelectionCleanupExecuted':False}
def enc(v):return (json.dumps(v,indent=2)+'\n').encode()
bs=enc(baselineSupport);mb=enc(manifest);cb=enc(close);pre=sum(x.stat().st_size for x in P.rglob('*') if x.is_file());assert pre+len(bs)+len(mb)+len(cb)+16384<=256*1024
(P/'BASELINE-SUPPORT.json').write_bytes(bs);(P/'MANIFEST.json').write_bytes(mb);(P/'CLOSURE.json').write_bytes(cb)
rows=[{'path':str(x.relative_to(P)),'bytes':x.stat().st_size,'sha256':sha(x)} for x in sorted(P.rglob('*')) if x.is_file() and 'SEAL-GUARD' not in str(x)]
receipt={'status':'TOOL_GUARD_CLOSED_SOURCE_PROPOSAL','manifestSHA256':sha(P/'MANIFEST.json'),'planSHA256':proof['planSHA256'],'methodSHA256':proof['helperSHA256'],'closureSHA256':sha(P/'CLOSURE.json'),'packetCapBytes':256*1024,'logicalBeforeReceiptBytes':sum(x.stat().st_size for x in P.rglob('*') if x.is_file()),'rows':rows,'sealOwnRSSKiB':rss,'movingOuterSealGuardExcludedUntilClose':True}
(P/'FINAL-SEAL.json').write_bytes(enc(receipt));actual=sum(x.stat().st_size for x in P.rglob('*') if x.is_file());assert actual<=256*1024
print(json.dumps({'PLAN.json':sha(P/'PLAN.json'),'helper':proof['helperSHA256'],'MANIFEST.json':sha(P/'MANIFEST.json'),'CLOSURE.json':sha(P/'CLOSURE.json'),'FINAL-SEAL.json':sha(P/'FINAL-SEAL.json'),'logicalBeforeOuterCloseBytes':actual,'sealOwnRSSKiB':rss}))
