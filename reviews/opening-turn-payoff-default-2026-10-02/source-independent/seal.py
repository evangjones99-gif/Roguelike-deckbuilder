import hashlib,json,os,pathlib,resource,stat
P=pathlib.Path('/workspace/scratch/opening-turn-payoff-opening-checkpoint-source-independent-r1');A=pathlib.Path('/workspace/scratch/opening-turn-payoff-opening-checkpoint-source-author-r1')
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
proof=json.loads((P/'PROOF.json').read_bytes())
for n,s in proof['pins'].items():assert sha(A/n)==s
guard=json.loads((P/'AUDIT-GUARD-R1/RESULT.json').read_bytes());assert guard['exit_code']==0 and guard['failure'] is None and guard['memory_events_before']==guard['memory_events_after']
hold=pathlib.Path('/workspace/Roguelike-deckbuilder/AGENTS.md');assert sha(hold)==proof['AGENTSSHA256']
zp=pathlib.Path('/workspace/scratch/retained-original-archives/preflight-bdf273-original-r4.zip')
def meta(p):
 s=p.stat();return {k:getattr(s,k) for k in ['st_dev','st_ino','st_mode','st_nlink','st_uid','st_gid','st_size','st_atime_ns','st_mtime_ns','st_ctime_ns','st_blocks','st_blksize']}|{'xattrs':{n:os.getxattr(p,n).hex() for n in os.listxattr(p)}}
zb=meta(zp)
gate={'decision':'ACCEPT_CONDITIONAL_EXACT_CHECKPOINT_PRESERVATION_SOURCE_ONLY','plan':{'path':str(A/'PLAN.json'),'sha256':proof['pins']['PLAN.json']},'method':{'path':str(A/'preserve-checkpoint.py'),'sha256':proof['pins']['preserve-checkpoint.py']},'manifest':{'sha256':proof['pins']['MANIFEST.json']},'authorClosure':{'sha256':proof['pins']['CLOSURE.json']},'currentHold':{'path':str(hold),'sha256':proof['AGENTSSHA256']},'proof':{'path':str(P/'PROOF.json'),'sha256':sha(P/'PROOF.json')},'review':{'path':str(P/'REVIEW.md'),'sha256':sha(P/'REVIEW.md')},'futureRootArgv':['python',str(A/'preserve-checkpoint.py'),str(A/'PLAN.json'),proof['pins']['PLAN.json'],'NEW_FRESH_OUTPUT_DIRECTORY'],'futureGuard':{'workMiB':128,'reserveMiB':512,'diskMinimumMiB':64,'ownRSSMiB':24,'outputLogicalAndAllocatedMiB':16,'finiteMethodChecksSeconds':60},'requiresActualIndependentCompleteReviewBeforePublication':True,'runtimeSelectionGitCleanupAuthorized':False,'existingCapsule':{'sha256':'ce0f8f40bcf0f0b22e5e4d93eef3d4660662826e617900aba09ac208c148dc13','indexSHA256':'115bbdb35d9cdff98503a3a5c63ced87e49a48d198194c9caa45268254bec0cf','priorCompleteGateSHA256':'11707477d92cc0a041f3dbbfd77d5ba6ef185a4d5df3bb181f2285d827dfeb05','sourcePhaseArchiveBodyRead':False},'coverage':{'logicalRows':490,'newUniqueBodies':298,'existingReferences':187,'callerBodies':40,'fullRuntimeMapCounts':[[89,56],[89,56],[88,56]],'externalGameMediaOccurrences':303,'selfContainedRelease':False},'qualifications':['Actual helper metadata checks cover a subset, not all stat fields/xattrs.','O_NOATIME fallback and standard-read atime qualified; no time reset.','Terminal allocated/RSS/elapsed stdout must be retained because RESULT was written before terminal measurements.','Fresh Root guard/admission required; 17MiB is an estimate, not internal disk admission.','No gameplay/default/wording/platform/human enjoyment claim.'],'normalSourceGuard':{'resultSHA256':sha(P/'AUDIT-GUARD-R1/RESULT.json'),'exitCode':0,'failure':None,'auditOwnMaxRSSKiB':proof['ownMaxRSSKiB']},'status':'SOURCE_FINITE_CLOSED_PENDING_ROOT_ACTUAL_AND_INDEPENDENT_COMPLETE'}
gb=(json.dumps(gate,indent=2)+'\n').encode()
pre=sum(p.stat().st_size for p in P.rglob('*') if p.is_file());assert pre+len(gb)+8192<=96*1024
assert meta(zp)==zb
(P/'SOURCE-GATE.json').write_bytes(gb)
rows=[{'path':str(p.relative_to(P)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(P.rglob('*')) if p.is_file() and not 'SEAL-GUARD' in str(p)]
rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss;assert rss<=24576
receipt={'status':'TOOL_GUARD_CLOSED_SOURCE_ONLY_CONDITIONAL','sourceGateSHA256':sha(P/'SOURCE-GATE.json'),'familyCapBytes':96*1024,'logicalBeforeReceiptBytes':sum(p.stat().st_size for p in P.rglob('*') if p.is_file()),'guardLogExcludedAsMovingUntilOuterClose':True,'rows':rows,'sealOwnMaxRSSKiB':rss,'protectedZIPFullStatXattrsStableNoBodyRead':True,'allOriginalsRetained':True}
(P/'FINAL-SEAL.json').write_text(json.dumps(receipt,indent=2)+'\n')
actual=sum(p.stat().st_size for p in P.rglob('*') if p.is_file());assert actual<=96*1024
print(json.dumps({'SOURCE-GATE.json':sha(P/'SOURCE-GATE.json'),'FINAL-SEAL.json':sha(P/'FINAL-SEAL.json'),'logicalPacketBytesBeforeOuterClose':actual,'ownMaxRSSKiB':rss}))
