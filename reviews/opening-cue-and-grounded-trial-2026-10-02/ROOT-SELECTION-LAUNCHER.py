from pathlib import Path
import hashlib,json,os,subprocess,time
R=Path('/workspace/Roguelike-deckbuilder');S=Path('/workspace/scratch')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(65536):h.update(b)
 return h.hexdigest()
def git(*a):
 p=subprocess.run(['git','-c','gc.auto=0',*a],cwd=R,capture_output=True,timeout=30)
 assert p.returncode==0,'Fresh Git precondition failed; do not select source'
 return p.stdout
head=git('rev-parse','HEAD').decode().strip();assert head=='d144368d04b5af55abc7c81927417eb88ee47e16'
assert git('symbolic-ref','--short','HEAD').decode().strip()=='codex/lanternbound-production'
assert git('status','--porcelain=v1','-z','--untracked-files=all')==b''
assert git('ls-remote','--heads','origin','refs/heads/codex/lanternbound-production').decode().split()[0]==head
G=S/'wording-development-source-selection-independent-r1/GATE.json'
assert sha(G)=='54dbe0760eb34634e79f6402e5a8dbaba79d8b5a5a91ce6c6a26fc9526320e40'
g=json.loads(G.read_text());assert 'ACCEPT' in g['decision']
complete=S/'wording-grounded-trials-checkpoint-complete-independent-r1/GATE.json'
assert sha(complete)=='df8ef40e5409409f004d2a2c08d7ca20dfb519f31590c379459c29d2f6983a85'
assert json.loads(complete.read_text())['decision']=='ACCEPT_COMPLETE_WORDING_AND_GROUNDED_TRIALS_BYTE_PRESERVATION_ONLY'
assert sha(R/'AGENTS.md')=='19e35b29256309ef3fbded5d57ae4e3a582b07dfd0e18f7e8497341e0fe3378e'
observed=[]
for p in Path('/proc').iterdir():
 if not p.name.isdigit():continue
 try:args=(p/'cmdline').read_bytes().split(bytes([0]));label=b' '.join(args)
 except OSError:continue
 if any(x in label for x in [b'vite/bin/vite',b'electron/dist/electron',b'npm run dev']):observed.append(p.name)
assert not observed,'Observed development server/desktop launch: preserve and coordinate before selection'
c=Path('/sys/fs/cgroup');headroom=int((c/'memory.max').read_text())-int((c/'memory.current').read_text())
free=os.statvfs(R).f_bavail*os.statvfs(R).f_frsize;assert headroom>=576*1048576 and free>=64*1048576+512*1024
grant={'authorized':True,'developmentSourceSelectionOnly':True,'soleCanonicalWriterConfirmed':True,
 'noDevServerOrOtherCanonicalSourceWriterConfirmed':True,
 'writerQualification':'Root is sole coordinated canonical writer; agents own private SOURCE/review folders only. Observed launch-process snapshot does not prove absence of every unknown process.',
 'canonicalPaths':['src/main.ts','src/opening-turn-payoff.css'],
 'methodSHA256':'9c3c231b71c03ce23b5515f2cca5dcc3b341af418216000bc1edab0dc2a3b788',
 'checkpointSourcePlanSHA256':'0998d948c57e2fb3d1e01f34e61028d5c80db299df308d3b1e83ab902d4281b7',
 'currentHold':{'path':str(R/'AGENTS.md'),'sha256':sha(R/'AGENTS.md'),'RootVerifiedPrependOnlySameHolds':True},
 'independentSourceGate':{'path':str(G),'sha256':sha(G),'RootVerifiedExactMethodSourceEligibility':True},
 'completePreservation':{'RootVerifiedCompleteScopeAndSourcePlan':True,'sourcePlanSHA256':'0998d948c57e2fb3d1e01f34e61028d5c80db299df308d3b1e83ab902d4281b7',
  'gate':{'path':str(complete),'sha256':sha(complete)},
  'archive':{'path':str(S/'wording-grounded-trials-checkpoint-output-root-r1/evidence-451347c174a3fe78e5f7b6ef22736b7cfbbd33b39fd04ea20556730bb3b15a8b.tar.gz'),'sha256':'451347c174a3fe78e5f7b6ef22736b7cfbbd33b39fd04ea20556730bb3b15a8b'},
  'index':{'path':str(S/'wording-grounded-trials-checkpoint-output-root-r1/INDEX.json'),'sha256':'64fe0a3ea9e523e6a63c9b7e60cd4ae3df8c88ef15cfba858a86187e21e98d58'}},
 'confirmedPush':{'RootVerifiedCurrentCleanAndPushed':True,'head':head,'receipt':{'path':str(S/'opening-cue-checkpoint-push-receipt-root-r1.json'),'sha256':sha(S/'opening-cue-checkpoint-push-receipt-root-r1.json')}},
 'producerDecision':'Select the independently accepted opening guidance in development source. Keep all rollback/review material and reject pixel-scene promotion. Narrow evidence does not prove human enjoyment or completed300 seconds.',
 'freshHeadroomBytes':headroom,'freshFreeDiskBytes':free,'utcNs':time.time_ns(),
 'workMiB':64,'reserveMiB':512,'bootstrapSourceWriteUnmetered':True,
 'retainedDistQualification':'Canonical preview/desktop dist remains8b; reviewed candidate artifact82e remains a frozen private reference. No archive/tag/version or cleanup.'}
out=S/'wording-development-source-selection-grant-root-r1.json'
with out.open('x') as f:json.dump(grant,f,indent=2);f.write(chr(10));f.flush();os.fsync(f.fileno())
v=subprocess.run(['python3','-B',str(S/'wording-development-source-selection-author-r1/select-development-source.py'),str(out),sha(out),str(S/'wording-development-source-selection-actual-root-r1')],timeout=62)
assert v.returncode==0,'Source selection failed; preserve exact partial-prefix receipt and original backups'
