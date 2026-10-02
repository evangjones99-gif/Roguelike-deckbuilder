import os,json,hashlib,ast,resource
from pathlib import Path
P=Path(__file__).parent;A=Path('/workspace/scratch/wording-grounded-trials-checkpoint-source-author-r1')
def read(p):
 fd=os.open(p,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW)
 try:return b''.join(iter(lambda:os.read(fd,65536),b''))
 finally:os.close(fd)
def pin(p):
 b=read(p);return {'path':str(p),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
v=json.loads(read(A/'PLAN.json'));m=json.loads(read(A/'MANIFEST.json'));f=json.loads(read(A/'FINAL-SEAL.json'))
for x in m['bodies']:
 z=pin(A/x['name']);assert z['bytes']==x['bytes'] and z['sha256']==x['sha256']
print('HELPER',read(A/'preserve-checkpoint.py').decode());ast.parse(read(A/'preserve-checkpoint.py'))
print('INVERSE',read(A/'METHOD-INVERSE.json').decode());print('PROTOCOL',read(A/'PROTOCOL.txt').decode());print('PROOF',read(A/'SOURCE-PROOF.json').decode())
print('SELECTEDPLAN',json.dumps({k:v[k]for k in ('rowColumns','existingCapsules','runtimeAuthorities','actualComparisons','nestedLogicalGzipDomains','originalReviewGatesVerbatim','metadataSnapshot','externalDependencies','optionalInputDomains','futureSelectionContract','proposedArchive','publicationPlan','sourceReadQualifications')},indent=2)[:17000])
print('ROW_SAMPLE',v['rows'][:2]);print('ROOT_SAMPLE',v['roots'][:3]);print('OWN_RSS',resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024)
