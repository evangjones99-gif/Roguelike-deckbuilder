from pathlib import Path
import subprocess,os,json,hashlib,time
R=Path('/workspace/Roguelike-deckbuilder'); S=Path('/workspace/scratch'); O=S/'pixel-cue-evidence-push-receipt-root-r1.json'; rows=[]
def git(*args):
 cmd=['git','-c','gc.auto=0','-c','pack.threads=1',*args]
 v=subprocess.run(cmd,cwd=R,env={**os.environ,'GIT_TERMINAL_PROMPT':'0'},capture_output=True,timeout=90)
 rows.append({'argv':cmd,'exitCode':v.returncode,'stdout':v.stdout.decode('utf8','replace'),'stderr':v.stderr.decode('utf8','replace')})
 if v.returncode:raise RuntimeError('Git command failed; exact receipts retained')
 return v.stdout
try:
 before=git('rev-parse','HEAD').decode().strip(); assert before=='5bddeb1dd46feeef3747eabb7f87512c2a38ea83'
 assert git('symbolic-ref','--short','HEAD').decode().strip()=='codex/lanternbound-production'
 allowed=['AGENTS.md','docs/CONTINUATION.md','docs/PRODUCTION.md']; roots=['reviews/coherent-native128-prebrowser-audit-2026-10-02','reviews/default-target-clear-publication-repair-2026-10-02','reviews/coherent-native128-actual-trial-2026-10-02']
 status=git('status','--porcelain=v1','-z','--untracked-files=all')
 entries=[x.decode() for x in status.split(bytes([0])) if x]
 assert entries and all(x[:2] in [' M','??'] and (x[3:] in allowed or any(x[3:].startswith(t+'/') for t in roots)) for x in entries),'Unexpected user/staged changes; preserve and stop'
 publication=json.loads((R/roots[2]/'PUBLICATION.json').read_text())
 for x in publication['records']:
  p=R/x['destination'];assert hashlib.sha256(p.read_bytes()).hexdigest()==x['sha256']
 git('add',*allowed);git('add','-f',*roots)
 staged=[x.decode() for x in git('diff','--cached','--name-only','-z').split(bytes([0])) if x]
 assert staged and all(x in allowed or any(x.startswith(t+'/') for t in roots) for x in staged)
 git('-c','commit.gpgsign=false','commit','-m','Preserve rejected pixel trial and record opening cue comparisons')
 head=git('rev-parse','HEAD').decode().strip()
 git('push','origin','HEAD:refs/heads/codex/lanternbound-production')
 remote=git('ls-remote','--heads','origin','refs/heads/codex/lanternbound-production').decode().split()[0]
 assert remote==head
 final=git('status','--porcelain=v1','-z','--untracked-files=all');assert final==b''
 receipt={'utcNs':time.time_ns(),'before':before,'head':head,'remote':remote,'confirmedPush':True,'clean':True,'stagedFiles':len(staged),'rows':rows,'scope':'Evidence and metadata only; selected runtime remains c4fa7d2b/8bbaea72. No cleanup, version tag or pixel/default cue promotion.'}
 O.open('x').write(json.dumps(receipt,indent=2)+chr(10));print(json.dumps({k:receipt[k] for k in ['head','remote','confirmedPush','clean','stagedFiles']}))
except BaseException as e:
 if not O.exists():O.open('x').write(json.dumps({'utcNs':time.time_ns(),'failed':repr(e),'rows':rows,'originalsRetained':True},indent=2)+chr(10))
 raise
