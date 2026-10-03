"""ROOT ONLY: publish selected controls, complete archive and exact canonical changes."""
import sys
sys.dont_write_bytecode=True
sys.path.insert(0, '/workspace/scratch/default-clear-publication-source-author-r1')
from common import *
import subprocess
ordinary(256);plan=load(M/'PLAN-r2.json');selected=load(T/'RESULT.json');assert selected['normal'] and selected['defaultEnabled'] and selected['oldSourceAnd5OutputsRetainedExact']
after=load(Path(plan['candidateFreeze']['path']));audit(R,after['inputs']);assert outputmap(R/'dist')==after['outputs'];summary=load(D/'PRESERVATION.json');assert digest(D/summary['archive'])==summary['archiveSHA256'] and summary['roundtripVerified']
Q=S/'default-clear-publication-push-root-r2';assert not Q.exists();Q.mkdir()
def run(args):
 p=subprocess.run(args,cwd=R,text=True,capture_output=True,timeout=60)
 with (Q/'COMMANDS.jsonl').open('a') as f:f.write(json.dumps({'args':args,'rc':p.returncode,'stdout':p.stdout,'stderr':p.stderr})+'\n');f.flush();os.fsync(f.fileno())
 assert p.returncode==0,(args,p.stderr);return p.stdout.rstrip('\r\n')
owned=str(D.relative_to(R));changed=['src/main.ts']+[str(Path('dist')/n) for n in set(plan['old5'])|set(plan['new5'])]
for line in run(['git','status','--porcelain','--untracked-files=all']).splitlines():assert line[3:] in changed or line[3:].startswith(owned+'/'),line
assert run(['git','rev-parse','HEAD'])==plan['currentHEADAtSourcePreparation']
copy=[(Path(pin['path']),D/'actual-review-gates'/(role+'-GATE.json')) for role,pin in summary['actualReviewGates'].items()]
copy += [(T/n,D/'selection'/n) for n in ('PRODUCER-JUDGMENT.json','RESULT.json','JOURNAL.jsonl','BEFORE-88-56-MAPS.json','AFTER-88-56-MAPS.json')]
judgment=load(T/'PRODUCER-JUDGMENT.json');coverage=Path(judgment['coverageGate']['path']);assert digest(coverage)==judgment['coverageGate']['sha256']
for path,rel,s in tree(coverage.parent):
 assert not path.name.endswith(('.zip','.tar.gz','.tgz','.png','.wav'));copy.append((path,D/'independent-preservation'/rel))
for source,target in copy:
 target.parent.mkdir(parents=True,exist_ok=True);v=body(source)
 with target.open('xb') as f:f.write(v);f.flush();os.fsync(f.fileno())
 assert digest(target)==digest(source)
run(['git','add','-f','--',owned,'src/main.ts']+[str(Path('dist')/n) for n in plan['new5']]);run(['git','add','-u','--','dist/'+plan['oldJS']])
run(['git','-c','gc.auto=0','commit','-m','Enable tested default target-clear card placement'])
head=run(['git','rev-parse','HEAD']);run(['git','-c','gc.auto=0','push','origin','HEAD:codex/lanternbound-production']);remote=run(['git','ls-remote','origin','refs/heads/codex/lanternbound-production']).split()[0];assert head==remote and not run(['git','status','--porcelain'])
save(Q/'PUSH-CONFIRMED.json',{'confirmed':True,'clean':True,'commit':head,'remote':remote,'sourceDigest':after['sourceDigest'],'outputsDigest':after['outputsDigest'],'archiveSHA256':summary['archiveSHA256'],'canonicalOutputCount':56,'privateRollbackRetained':str(T),'versionTagReleaseChange':False,'noMediaOrHistoricalBodyDeletion':True})
print(json.dumps({'confirmed':True,'clean':True,'commit':head}))
