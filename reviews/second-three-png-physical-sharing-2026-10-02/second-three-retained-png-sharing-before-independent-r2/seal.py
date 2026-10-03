import pathlib,os,json,hashlib,resource,time
p=pathlib.Path(__file__).parent
def rec(path):
 fd=os.open(path,os.O_RDONLY|os.O_NOATIME)
 with os.fdopen(fd,'rb') as f:b=f.read()
 return {'path':str(path),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
proof=json.loads((p/'PROOF.json').read_text())
for name in ['methodR2','proposal','authorSeal','currentHold','priorR1Proof','priorR1GateRejection','priorR1Review','priorR1Manifest','priorR1FinalSeal','selectedMap']:assert rec(proof[name]['path'])==proof[name]
closed=[]
for name,expected in [('read-guard-r1',0),('verify-guard-r1',1),('verify-guard-r2',0)]:
 path=p/name/'RESULT.json';r=json.loads(path.read_text());assert r['exit_code']==expected and r['failure'] is None and r['memory_events_before']==r['memory_events_after'];closed.append(rec(path))
rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss;assert rss<24*1024
gate={'decision':'ACCEPT_EXACT_THREE_PATH_SHARING_AND_R2_ACTION_SOURCE_CONDITIONAL_PUSH_PRODUCER','method':proof['methodR2'],'proposal':proof['proposal'],'authorSeal':proof['authorSeal'],'currentHold':proof['currentHold'],'selectedMap':proof['selectedMap'],'r1SourceRejection':proof['priorR1GateRejection'],'priorProof':proof['priorR1Proof'],'sourceProof':rec(p/'PROOF.json'),'review':rec(p/'REVIEW.md'),'grossPotentialAllocationBytes':8499200,'allThreeLogicalPathsBodiesAndRightsPreservedByPlan':True,'oldPrivateEncodingIsolationNoLongerNeeded':True,'oldMetadataProvenanceConsumerRecordsStillNeeded':True,'unknownPhysicalAliasesPerAnchor':1,'knownPhysicalAliasesPerAnchor':4,'noOldInodeBackupAcceptedVariant':True,'allThreeAtomicity':False,'requiresProducerJudgmentAndNewConfirmedCurrentPush':True,'rootSoleActionGrantStillRequired':True,'actionExecutedByReviewer':False,'sourceGuardsClosed':closed,'ownSealerRSSKiB':rss,'resourceQualification':'Source64aggregate+512unchangedreserve/disk64 ownRSS24; sharedsampled delta notexclusive attribution. No action/Git/Node/backend.','state':'SOURCE_REVIEW_SEALED_PENDING_OUTER_GUARD_READBACK','utcNs':time.time_ns()}
(p/'GATE.json').write_text(json.dumps(gate,indent=2)+'\n')
manifest={'files':[rec(x) for x in sorted(p.rglob('*')) if x.is_file() and x.name not in ['MANIFEST.json','FINAL-SEAL.json'] and 'seal-guard-r1' not in str(x.relative_to(p))]}
(p/'MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
total=sum(x.stat().st_size for x in p.rglob('*') if x.is_file());assert total<=192*1024
print(json.dumps({'packetBytes':total,'ownRSSKiB':rss,'review':rec(p/'REVIEW.md'),'gate':rec(p/'GATE.json'),'manifest':rec(p/'MANIFEST.json')}))
