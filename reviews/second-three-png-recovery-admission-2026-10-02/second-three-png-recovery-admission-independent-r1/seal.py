import pathlib,os,json,hashlib,resource,time
p=pathlib.Path(__file__).parent
def rec(path):
 fd=os.open(path,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW)
 with os.fdopen(fd,'rb') as f:b=f.read()
 return {'path':str(path),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
a=json.loads((p/'PROOF.json').read_text());d=json.loads((p/'DURABLE-CONTROLS-PROOF.json').read_text())
for r in [a['guard'],a['methodR3'],a['proposal'],d['publisher'],d['producer'],d['authorProposal'],d['currentHold'],d['selectedMap']]:assert rec(r['path'])==r
closed=[]
for folder in sorted(p.glob('*-guard-r1')):
 if folder.name=='seal-guard-r1':continue
 result=folder/'RESULT.json';r=json.loads(result.read_text());assert r['exit_code']==0 and r['failure'] is None and r['memory_events_before']==r['memory_events_after'];closed.append(rec(result))
rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss;assert rss<24*1024
gate={'decision':'ACCEPT_PINNED_BOUNDED_56M_SOURCE_RECOVERY_ADMISSION_AND_R3_METHOD','method':a['methodR3'],'proposal':d['authorProposal'],'currentHold':d['currentHold'],'selectedMap':d['selectedMap'],'admissionGuard':a['guard'],'admissionProposal':a['proposal'],'publisher':d['publisher'],'producer':d['producer'],'approvedInvocations':d['approvedInvocations'],'sourceProof':rec(p/'PROOF.json'),'durableControlsProof':rec(p/'DURABLE-CONTROLS-PROOF.json'),'transactionBound':rec(p/'TRANSACTION-BOUND.json'),'review':rec(p/'REVIEW.md'),'diskAdmissionMiB':56,'memoryReserveMiB':512,'liveDiskStopMiB':1,'ordinaryStrictBuildAdmissionMiB':64,'nativeAdmissionMiB':70,'sourceProofMaxBytes':192*1024,'publicationCopiedPayloadMaxBytes':512*1024,'publicationUpperPayloadWithMaxReviewBytes':278514,'transactionControlMaxBytes':65536,'guardNamespaceIsolationClaim':False,'publisherReceiptAloneFullyAncestorDurable':False,'successfulDurableProducerCompletionRequiredBeforeAction':True,'requiresNewCurrentPushProducerAndRootSoleActionGrant':True,'noExtraMediaPathsNoBackupNoAutomaticRetry':True,'actionExecutedByReviewer':False,'sourceGuardsClosed':closed,'ownSealerRSSKiB':rss,'resourceQualification':'Exactboundedsource only64aggregate+512reserve/56disk admission, ownRSS<24; sharedsampled delta notexclusive attribution. Bootstrapunmetered; no arbitraryPython/backend/global enforcementclaim.','state':'REVIEW_SEALED_PENDING_OUTER_GUARD_RESULT_READBACK','utcNs':time.time_ns()}
(p/'GATE.json').write_text(json.dumps(gate,indent=2)+'\n')
manifest={'files':[rec(x) for x in sorted(p.rglob('*')) if x.is_file() and x.name not in ['MANIFEST.json','FINAL-SEAL.json'] and 'seal-guard-r1' not in str(x.relative_to(p))]}
(p/'MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
total=sum(x.stat().st_size for x in p.rglob('*') if x.is_file());assert total<=192*1024
print(json.dumps({'packetBytes':total,'ownRSSKiB':rss,'review':rec(p/'REVIEW.md'),'gate':rec(p/'GATE.json'),'manifest':rec(p/'MANIFEST.json')}))
