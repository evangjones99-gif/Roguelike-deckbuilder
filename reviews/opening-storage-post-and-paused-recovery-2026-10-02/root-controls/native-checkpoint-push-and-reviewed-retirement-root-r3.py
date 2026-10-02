from pathlib import Path
import os,sys,json,hashlib,subprocess,time,resource
R=Path('/workspace/Roguelike-deckbuilder'); S=Path('/workspace/scratch'); start=time.monotonic()
def check():
 if time.monotonic()-start>125: raise RuntimeError('Finite125s phase exceeded; retained progress must be inspected')
 if resource.getrusage(resource.RUSAGE_SELF).ru_maxrss>24576: raise RuntimeError('Root helper24MiB ceiling')
def sha(p):
 h=hashlib.sha256()
 fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME)
 with os.fdopen(fd,'rb') as f:
  while b:=f.read(65536):check();h.update(b)
 return h.hexdigest()
def run(args,seconds):
 check(); q=subprocess.run(args,cwd=R,check=True,capture_output=True,text=True,timeout=seconds);check(); return q.stdout.rstrip(chr(10))
def write(p,v):
 with p.open('x') as f:json.dump(v,f,indent=2);f.write(chr(10));f.flush();os.fsync(f.fileno())
 check()
if not __debug__: raise RuntimeError('Optimized mode refused')
if len(sys.argv)!=3: raise RuntimeError('Independent publication gate and literal SHA required')
gp=Path(sys.argv[1]); assert sha(gp)==sys.argv[2]; gate=json.loads(gp.read_bytes()); assert gate.get('postPublicationAccepted') is True and gate.get('literalPublicationVerified') is True and gate.get('TOOL_GUARD_CLOSED') is True and gate.get('publicationSHA256')=='f2a737d6ff59cac3df8d5879e41d38888f2b4b4d54c0f914d99d1b89242ee6d2',gate
assert run(['git','branch','--show-current'],10)=='codex/lanternbound-production'
expected={'AGENTS.md','docs/CONTINUATION.md','docs/PRODUCTION.md','reviews/opening-native-aftermath-and-starter-art-2026-10-02/','reviews/reviewed-opening-capsule-duplicate-retirement-2026-10-02/'}
status=run(['git','status','--porcelain','--untracked-files=normal'],10)
paths={line[3:] for line in status.splitlines()};assert paths==expected,paths
run(['git','add','--','AGENTS.md','docs/CONTINUATION.md','docs/PRODUCTION.md','reviews/opening-native-aftermath-and-starter-art-2026-10-02','reviews/reviewed-opening-capsule-duplicate-retirement-2026-10-02'],20)
commit=run(['git','commit','-m','Preserve reviewed pixel aftermath and starter art trials'],20)
head=run(['git','rev-parse','HEAD'],10)
push=run(['git','push','origin','codex/lanternbound-production'],60)
remote=run(['git','ls-remote','--heads','origin','codex/lanternbound-production'],20).split()[0]
verified=time.time_ns();assert remote==head;assert not run(['git','status','--porcelain'],10)
receipt=S/'native-checkpoint-current-push-receipt-root-r1.json'
write(receipt,{'confirmedPush':True,'clean':True,'localHEAD':head,'remoteHEAD':remote,'remoteVerifiedAtNs':verified,'commitResult':commit,'pushStdout':push,'scope':'All five current canonical changes committed and confirmed pushed before exactly two approved private encoding retirements; Source actors closed and Root sole canonical writer. This receipt is not future cleanup authorization.'})
receiptSHA=sha(receipt); method=S/'retire-opening-capsule-duplicates-root-r2.py'; methodSHA=sha(method);assert methodSHA=='b1131f6cede49fceb01fcdfb87a251c95519561355acddd03045fba8e4fe7d71'
actionGate=S/'opening-capsule-duplicate-retirement-method-independent-r2/GATE.json';actionSHA='4408a05e44ebe6f6c678920b6359653aa0b154aa03b818b1288c6e2a767c00d8';assert sha(actionGate)==actionSHA
producer=R/'reviews/reviewed-opening-capsule-duplicate-retirement-2026-10-02/PRODUCER-DECISION.json';producerSHA=sha(producer);assert producerSHA=='67ee3cc4693359db655f1914a6507a0ae956afd497b6f70aec0f9dece5de2f61'
grant=S/'opening-capsule-duplicate-retirement-action-grant-root-r2.json';write(grant,{'authorized':True,'soleWriterConfirmed':True,'allSourceActorsPausedConfirmed':True,'methodSHA256':methodSHA,'independentMethodGateSHA256':actionSHA,'confirmedPushSHA256':receiptSHA,'producerDecisionSHA256':producerSHA,'publicationGateSHA256':sys.argv[2],'workMiB':128,'reserveMiB':512,'scope':'Exactly two approved scratch archive encodings after fresh confirmed clean push. No other deletion, canonical mutation, release or quality approval.'})
check();out=run(['python3','-B',str(method),str(actionGate),actionSHA,str(receipt),receiptSHA,str(grant),sha(grant)],45)
print(json.dumps({'confirmedHEAD':head,'pushReceiptSHA256':receiptSHA,'actionResult':out,'phaseElapsed':time.monotonic()-start}))
