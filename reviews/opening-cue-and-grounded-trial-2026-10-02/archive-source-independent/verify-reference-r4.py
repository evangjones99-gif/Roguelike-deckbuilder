import os,json,hashlib,resource
from pathlib import Path
P=Path(__file__).parent;A=Path('/workspace/scratch/wording-grounded-trials-checkpoint-source-author-r1')
def read(p):
 fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME)
 try:return b''.join(iter(lambda:os.read(fd,65536),b''))
 finally:os.close(fd)
j=json.loads(read(A/'PLAN.json'));out={'priorCompleteGates':[],'freezeDomains':[],'sourceOnly':True}
dirs=['coherent-native128-actual-trial-2026-10-02','opening-turn-payoff-default-2026-10-02']
for c,d in zip(j['existingCapsules'],dirs):
 p=Path('/workspace/Roguelike-deckbuilder/reviews')/d/'preservation-independent/GATE.json';b=read(p)
 assert hashlib.sha256(b).hexdigest()==c['completeGateSHA256'];v=json.loads(b);assert str(v['decision']).startswith('ACCEPT')
 out['priorCompleteGates'].append({'path':str(p),'sha256':c['completeGateSHA256'],'decision':v['decision'],'proofInheritedNoArchiveDecode':True})
for x in j['runtimeAuthorities']:
 v=json.loads(read(Path(x['freezePath'])))
 out['freezeDomains'].append({'path':x['freezePath'],'sha256':x['freezeSHA256'],'keys':list(v),'expectedInputs':x['inputCount'],'expectedOutputs':x['outputCount'],'exactFrozenAuthority':True})
assert not any((Path(j['roots'][x[0]])/x[1]).suffix.lower() in ('.zip','.dmg','.exe','.appimage') for x in j['rows'])
out['noProtectedReleaseLeavesInRows']=True;out['ownRSSBytes']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024;assert out['ownRSSBytes']<24*1048576
with (P/'REFERENCE-CHECKS.json').open('x') as f:json.dump(out,f,indent=2);f.write('\n')
print(json.dumps(out,separators=(',',':')))
