import os,json,hashlib,resource
from pathlib import Path
resource.setrlimit(resource.RLIMIT_DATA,(24*1048576,24*1048576))
P=Path(__file__).parent;S=Path('/workspace/scratch');pins=[];refs=[]
for path,expected in [(S/'target-clear-default-caller-author-r1/MANIFEST.json','5de445351d0849ae37ac3e8b91538219db1e3ad29fee980570a08aa206d5d782'),(S/'target-clear-default-caller-author-r1/EXPECTED-CANDIDATE.json','a13f90f8a30eb54eae7f37e4f0a021f1e0db4299b95e465244ac55c7bd959cab'),(S/'target-clear-default-caller-author-r1/SOURCE-CLOSURE.json','659c8242ce6fdcc1dd2563892ba2825bc65e2c1c342c290071af67bdcc6b4ca5'),(S/'target-clear-ghost-publish-author-r1/promote.py',None)]:
 before=os.lstat(path);f=os.open(path,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW);assert before==os.fstat(f)
 with os.fdopen(f,'rb') as stream:b=stream.read(262145);assert len(b)<262144 and before==os.fstat(stream.fileno())
 assert before==os.lstat(path);sha=hashlib.sha256(b).hexdigest()
 if expected:assert sha==expected
 lines=[{'line':i,'text':line[:500]} for i,line in enumerate(b.decode().splitlines(),1) if any(x in line for x in ['target-clear-ghost-comparison-actual-r3','VISUAL-RESULT.json','VISUAL-PROGRESS.json','RESULT.json'])]
 pins.append({'path':str(path),'bytes':len(b),'sha256':sha,'metadataStable':True});refs.append({'path':str(path),'lines':lines})
j={'finalCallerAndCompletedPromotionPins':pins,'referenceLines':refs,'interpretation':'Pending default build/freeze/source gate and sealed caller driver/supervisor/expected/protocol need no direct old R3 VISUAL body. Generic caller VISUAL filenames are writes into its new output packet, not reads of old R3 packet. Completed promoter uses small actual RESULT.json, retained untouched. Archive CAPSULE-MAPPING documents original paths, not live dependency. Historical gameplay reader directly reads old large VISUAL-RESULT; preserve original source and reconstruct into fresh paths/adapt a NEW reader for any rerun.','limits':'Independent default caller review still pending. Independent retirement reviewer must verify these exact final current consumer bodies and no-longer-needed conclusion; no global or future-reader absence claimed.','locatorClarification':'Root clarified completed promote.py means promote.py; initial absent completedpromote.py locator retained, not game/source failure.','ownMaxRSSBytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024}
assert j['ownMaxRSSBytes']<24*1048576
with (P/'CONSUMER-SUPPLEMENT.json').open('x') as out:json.dump(j,out,indent=2);out.write('\n')
print(json.dumps({'pins':pins,'referenceLines':refs,'ownMaxRSSBytes':j['ownMaxRSSBytes']}))
