import pathlib,os,json,hashlib,resource
p=pathlib.Path(__file__).parent
def rec(path):
 fd=os.open(path,os.O_RDONLY|os.O_NOATIME)
 with os.fdopen(fd,'rb') as f:b=f.read()
 return {'path':str(path),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
proof=json.loads((p/'PROOF.json').read_text());assert rec(proof['methodR1']['path'])==proof['methodR1']
rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss;assert rss<24*1024
gate={'decision':'REJECT_EXACT_METHOD_R1_SCHEMA_AND_IDENTITY_RECHECK','method':proof['methodR1'],'proposal':proof['proposal'],'currentHold':proof['currentHold']['receipt'],'sourceProof':rec(p/'PROOF.json'),'review':rec(p/'R1-REVIEW.md'),'conditionalLogicalSharingPreference':True,'actionAuthorized':False,'producerAndNewCurrentPush':'pending','ownRSSKiB':rss,'sourceScope':'64aggregate+512reserve/disk64 ownRSS24; no action/Git/images/Node; r1 rejection retained unchanged for fresh successor.'}
(p/'R1-GATE.json').write_text(json.dumps(gate,indent=2)+'\n')
manifest={'files':[rec(x) for x in sorted(p.rglob('*')) if x.is_file() and x.name not in ['R1-MANIFEST.json','R1-FINAL-SEAL.json'] and 'seal-guard-r1' not in str(x.relative_to(p))]}
(p/'R1-MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
total=sum(x.stat().st_size for x in p.rglob('*') if x.is_file());assert total<=192*1024
print(json.dumps({'packetBytes':total,'ownRSSKiB':rss,'gate':rec(p/'R1-GATE.json'),'review':rec(p/'R1-REVIEW.md'),'manifest':rec(p/'R1-MANIFEST.json')}))
