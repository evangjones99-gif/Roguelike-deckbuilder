import hashlib,json,os,pathlib,resource
P=pathlib.Path('/workspace/scratch/opening-turn-payoff-opening-checkpoint-preservation-independent-r1');O=pathlib.Path('/workspace/scratch/opening-turn-payoff-opening-checkpoint-output-root-r1')
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def j(p):return json.loads(pathlib.Path(p).read_bytes())
proof=j(P/'PROOF.json');g=j(P/'COMPLETE-GUARD-R1/RESULT.json');assert g['exit_code']==0 and g['failure'] is None and g['memory_events_before']==g['memory_events_after']
assert sha('/workspace/Roguelike-deckbuilder/AGENTS.md')==proof['AGENTSSHA256']
for n,s in proof['pins'].items():assert sha(pathlib.Path('/workspace/scratch/opening-turn-payoff-opening-checkpoint-source-author-r1')/n)==s
i=j(O/'INDEX.json');ca=proof['completeArchive'];assert i['newArchive']=={'path':ca['path'],'sha256':ca['sha256'],'bytes':ca['compressedBytes']}
for n,key in [('INDEX.json','indexSHA256'),('READ-OBSERVATIONS.json','observationsSHA256'),('RESULT.json','resultSHA256')]:assert sha(O/n)==ca[key]
rootGuard=pathlib.Path('/workspace/scratch/opening-turn-payoff-opening-checkpoint-archive-guard-root-r1')
for n,key in [('RESULT.json','guardResultSHA256'),('ADMISSION.json','guardAdmissionSHA256'),('EXECUTION.log','terminalStdoutSHA256')]:assert sha(rootGuard/n)==proof['rootActual'][key]
z=pathlib.Path('/workspace/scratch/retained-original-archives/preflight-bdf273-original-r4.zip')
def meta(p):
 s=p.stat();return {k:getattr(s,k) for k in ['st_dev','st_ino','st_mode','st_nlink','st_uid','st_gid','st_size','st_atime_ns','st_mtime_ns','st_ctime_ns','st_blocks','st_blksize']}|{'xattrs':{n:os.getxattr(p,n).hex() for n in os.listxattr(p)}}
zb=meta(z)
gate={'decision':'ACCEPT_COMPLETE_EXACT_OPENING_CUE_BYTE_PRESERVATION','archive':ca,'rootActual':proof['rootActual'],'sourceGate':{'path':'/workspace/scratch/opening-turn-payoff-opening-checkpoint-source-independent-r1/SOURCE-GATE.json','sha256':'4bfbc6ee637d79b98831fcf0dfe72233e3fec55309695b137956753920e097aa'},'proof':{'path':str(P/'PROOF.json'),'sha256':sha(P/'PROOF.json')},'review':{'path':str(P/'REVIEW.md'),'sha256':sha(P/'REVIEW.md')},'method':{'sha256':proof['pins']['preserve-checkpoint.py']},'plan':{'sha256':proof['pins']['PLAN.json']},'currentHold':{'sha256':proof['AGENTSSHA256']},'logicalRows':490,'all490FreshOriginalHashesMatch':True,'rawSavedPairCount':12,'originalJPEGCount':16,'callerBodyCount':40,'completeReviewRootCount':7,'runtimeMaps':[[89,56],[89,56],[88,56]],'externalGameMediaIdentityOccurrences':303,'selfContainedRelease':False,'existingAuthority':{'priorCompleteGateSHA256':'11707477d92cc0a041f3dbbfd77d5ba6ef185a4d5df3bb181f2285d827dfeb05','all831IndexAndFullCompressedArchiveRehashed':True,'old697DecodedBodiesNotReplayed':True},'originalsRetained':True,'protectedZIPBodyRead':False,'runtimeDefaultWordingArtSelectionOrCleanupAuthority':False,'limitations':['Byte-preservation acceptance only, no visual/gameplay/novice/enjoyment/platform improvement claim.','Existing capsule and both indexes are required; node_modules/held game media remain external.','Helper metadata checks cover only specified subset; no fullmetadata/xattr/time-reset/durability claim.','Terminal caps supported by retained stdout, not just earlier RESULT fields.','Shared cgroup attribution nonexclusive; no universal actor closure claim.'],'normalIndependentGuard':{'resultSHA256':sha(P/'COMPLETE-GUARD-R1/RESULT.json'),'exitCode':0,'failure':None,'ownMaxRSSKiB':proof['ownMaxRSSKiB']},'status':'TOOL_GUARD_CLOSED_COMPLETE_PRESERVATION_ONLY'}
gb=(json.dumps(gate,indent=2)+'\n').encode();pre=sum(p.stat().st_size for p in P.rglob('*') if p.is_file());assert pre+len(gb)+8192<=96*1024
assert meta(z)==zb
(P/'GATE.json').write_bytes(gb)
rows=[{'path':str(p.relative_to(P)),'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(P.rglob('*')) if p.is_file() and 'SEAL-GUARD' not in str(p)]
rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss;assert rss<=24576
receipt={'status':'TOOL_GUARD_CLOSED_COMPLETE','gateSHA256':sha(P/'GATE.json'),'familyLogicalCapBytes':96*1024,'logicalBeforeReceiptBytes':sum(p.stat().st_size for p in P.rglob('*') if p.is_file()),'sealOwnMaxRSSKiB':rss,'allRows':rows,'outerSealGuardMovingUntilCloseExcluded':True,'protectedZIPFullStatXattrsStableNoBodyRead':True}
(P/'FINAL-SEAL.json').write_text(json.dumps(receipt,indent=2)+'\n');actual=sum(p.stat().st_size for p in P.rglob('*') if p.is_file());assert actual<=96*1024
print(json.dumps({'GATE.json':sha(P/'GATE.json'),'FINAL-SEAL.json':sha(P/'FINAL-SEAL.json'),'logicalBeforeOuterGuardCloseBytes':actual,'sealOwnMaxRSSKiB':rss}))
