import resource
resource.setrlimit(resource.RLIMIT_DATA,(24*1048576,24*1048576))
import os,pathlib,json,hashlib,subprocess
P=pathlib.Path(__file__).parent;B=pathlib.Path('/workspace/scratch/default-clear-publication-source-author-r1');N=pathlib.Path('/workspace/scratch/default-clear-publisher-status-fix-root-r3');R=pathlib.Path('/workspace/Roguelike-deckbuilder');pins={}
def read(q):
 fd=os.open(q,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW)
 try:
  with os.fdopen(fd,'rb',closefd=False) as f:return f.read()
 finally:os.close(fd)
def sha(q):return hashlib.sha256(read(q)).hexdigest()
def pin(q,expected=None):
 h=sha(q)
 if expected:assert h==expected
 pins[str(q)]={'sha256':h,'bytes':q.stat().st_size};return h
pin(B/'publish-selected-r2.py','2fb2771bc7d9fd85334cb35498347cbea0e32d0409d031fbdc9e3076f7806d9a');pin(N/'publish-selected-r3.py','636303f3d2b9135c9967d367d9f8a40a28db58cfccabe34004aa68563fb0ed6f')
old=read(B/'publish-selected-r2.py').decode();new=read(N/'publish-selected-r3.py').decode();inverse=new
changes=[("import sys\nsys.dont_write_bytecode=True\nsys.path.insert(0, '/workspace/scratch/default-clear-publication-source-author-r1')\nfrom common import *",'from common import *'),("Q=S/'default-clear-publication-push-root-r2'","Q=S/'default-clear-publication-push-root-r1'"),("return p.stdout.rstrip('\\r\\n')","return p.stdout.strip()")]
for a,b in changes:assert inverse.count(a)==1;inverse=inverse.replace(a,b)
assert inverse==old
pin(B/'common.py','088c08e787ecfaaf7f2cb448b9736a0cdc1a605e647ea4b598ef2c45c7bd03a8');pin(B/'PLAN-r2.json');plan=json.loads(read(B/'PLAN-r2.json'))
rootguard=pathlib.Path('/workspace/scratch/default-clear-publication-root-guard-r1');pin(rootguard/'RESULT.json');pin(rootguard/'EXECUTION.log');gr=json.loads(read(rootguard/'RESULT.json'))
assert gr['exit_code']==1 and gr['failure'] is None and gr['memory_events_before']==gr['memory_events_after']
assert 'AssertionError: M src/main.ts' in read(rootguard/'EXECUTION.log').decode()
q1=pathlib.Path('/workspace/scratch/default-clear-publication-push-root-r1');assert sorted(x.name for x in q1.iterdir())==['COMMANDS.jsonl'];pin(q1/'COMMANDS.jsonl');commands=[json.loads(x) for x in read(q1/'COMMANDS.jsonl').decode().splitlines()]
assert len(commands)==1 and commands[0]['args']==['git','status','--porcelain','--untracked-files=all'] and commands[0]['rc']==0
assert not pathlib.Path('/workspace/scratch/default-clear-publication-push-root-r2').exists()
selectionPath=pathlib.Path('/workspace/scratch/default-clear-promotion-root-r1/RESULT.json');pin(selectionPath);selection=json.loads(read(selectionPath));assert selection['normal'] and selection['defaultEnabled'] and selection['oldSourceAnd5OutputsRetainedExact']
assert len(selection['inputs'])==88 and len(selection['outputs'])==56
coveragePath=pathlib.Path('/workspace/scratch/default-clear-preservation-independent-r1/GATE.json');pin(coveragePath);coverage=json.loads(read(coveragePath));assert coverage['decision']=='ACCEPT_COMPLETE_DECLARED_CAPSULE_FOR_EXACT_ROOT_SELECTION' and coverage['completeCoverage']
for row in coverage['methods']:
 q=pathlib.Path(row['path'])
 if q==B/'common.py' or q==B/'PLAN-r2.json' or q==B/'publish-selected-r2.py':assert sha(q)==row['sha256']
def git(args):
 x=subprocess.run(['git','--no-optional-locks',*args],cwd=R,capture_output=True,text=True,timeout=10);assert x.returncode==0;return x.stdout
status=git(['status','--porcelain','--untracked-files=all']);head=git(['rev-parse','HEAD']).rstrip('\r\n');assert head==plan['currentHEADAtSourcePreparation']
owned='reviews/opening-default-target-clear-2026-10-02';allowed={'src/main.ts'}|{'dist/'+x for x in set(plan['old5'])|set(plan['new5'])}
for line in status.splitlines():assert line[3:] in allowed or line[3:].startswith(owned+'/')
oldTracked=git(['ls-files','--stage','--','dist/'+plan['oldJS']]);assert oldTracked==''
assert "run(['git','add','-u','--','dist/'+plan['oldJS']])" in new
archive=pathlib.Path(coverage['archive']['path']);archiveStat=archive.stat()
rss=int(next(x.split()[1] for x in pathlib.Path('/proc/self/status').read_text().splitlines() if x.startswith('VmHWM:')))*1024;assert rss<24*1048576
proof={'sourceOnly':True,'inverseExactlyThreeReplacements':True,'statusLeadingSpacePreserved':True,'originalImportAndPlanRootUnchanged':True,'newReceiptRootAbsent':True,'firstReceiptOnlyOneReadOnlyGitStatus':True,'firstGuardExit1FailureNullEventsStable':True,'selectionNormalAndRetainedRollbackReceipt':True,'selectionMapCounts':[88,56],'completePreservationGateSHA256':sha(coveragePath),'capsuleMetadataOnly':{'path':str(archive),'bytes':archiveStat.st_size,'bodyNotRead':True},'HEAD':head,'gitPorcelainExact':status,'oldJSIndexedEntries':oldTracked,'blocker':'Unconditional git add -u targets the absent/untracked old JS path after force-adding new5; Git pathspec update cannot stage a removal absent from its index.','pins':pins,'ownVmHWMBytes':rss,'scope':'Small source/stat/JSON and read-only Git status/ls-files/rev-parse only; no Git write, publisher import/execution, runtime/media/ZIP hashing or canonical mutation; shared cgroup source accounting qualified'}
with (P/'PROOF.json').open('xb') as f:f.write((json.dumps(proof,separators=(',',':'))+'\n').encode());f.flush();os.fsync(f.fileno())
print(json.dumps({'inverseExact':True,'blockerOldJSUntracked':True,'ownVmHWMBytes':rss}))
