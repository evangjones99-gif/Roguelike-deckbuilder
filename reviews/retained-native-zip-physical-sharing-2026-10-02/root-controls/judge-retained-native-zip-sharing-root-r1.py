from pathlib import Path
import os,json,hashlib,sys
S=Path('/workspace/scratch');R=Path('/workspace/Roguelike-deckbuilder');M=Path(__file__).parent
def body(p):
 fd=os.open(p,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW)
 with os.fdopen(fd,'rb') as f:return f.read(262145)
def sha(p):return hashlib.sha256(body(p)).hexdigest()
proposal=M/'PROPOSAL.json';method=M/'share-retained-native-zip-root-r1.py';gate=S/'retained-native-zip-sharing-independent-r1/GATE.json';push=S/'retained-native-zip-sharing-push-root-r1/PUSH-CONFIRMED.json'
assert len(sys.argv)==2 and sha(gate)==sys.argv[1];g=json.loads(body(gate));p=json.loads(body(push));e=json.loads(body(proposal))
assert g['decision'].startswith('ACCEPT') and g['replacementBetter'] and g['oldIndependentEncodingNoLongerNeeded']
assert g['proposal']['sha256']==sha(proposal) and g['method']['sha256']==sha(method)
assert g['currentHold']['sha256']==e['currentHold']['sha256'] and g['plannedHold']['sha256']==e['plannedHold']['sha256']==p['holdSHA256']==sha(R/'AGENTS.md')
assert p['confirmed'] and p['clean'] and p['gateSHA256']==sha(gate) and p['methodSHA256']==sha(method) and p['proposalSHA256']==sha(proposal)
assert body(R/'.git/refs/heads/codex/lanternbound-production').decode().strip()==p['commit']
assert p['selectedMapSHA256']==e['selectedMap']['sha256']==sha(S/'target-clear-ghost-promotion-root-r3/RESULT.json')
D=R/'reviews/retained-native-zip-physical-sharing-2026-10-02';assert sha(D/'independent/GATE.json')==sha(gate) and sha(D/'root-controls'/method.name)==sha(method)
assert p['supportBundle']['roundtripExact']
def streamsha(p):
 h=hashlib.sha256();fd=os.open(p,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW)
 with os.fdopen(fd,'rb') as f:
  for b in iter(lambda:f.read(65536),b''):h.update(b)
 return h.hexdigest()
assert streamsha(D/'source-support.tar.gz')==p['supportBundle']['sha256']
assert sha(D/'previous-four-POST-GATE.json')==p['priorPostGateSHA256']=='57ac409802290271a2b6ef32f6f8aa5e08738ddb03f17c9750c325cba5dde5b7'
j={'decision':'AUTHORIZE_EXACT_ONE_RETAINED_ZIP_PHYSICAL_SHARE_ONCE','proposalSHA256':sha(proposal),'independentGateSHA256':sha(gate),'methodSHA256':sha(method),'pushSHA256':sha(push),'commit':p['commit'],'holdSHA256':p['holdSHA256'],'selectedMapSHA256':p['selectedMapSHA256'],'candidateGroup':e['candidateGroup'],'judgment':'Prefer one byte-exact held canonical native0.6.1 container backing both retained logical paths. Fresh independent review finds old scratch private physical encoding unnecessary under explicit immutable/fresh-stage-only hold. Container/release/source/rights/provenance and all historical files remain. One explicit ZIP alias only.','losses':'Scratch inode/time/write isolation lost, canonical nlink1→2/ctime change; no original-inode backup, metadata rollback, automatic cleanup or retry. Hold is coordinated workflow, not OS enforcement.','admission':'Action512MiB work+512reserve/disk64 for file-cache streams. Native70/70.5 unchanged. Full current144 before/after; protected1.8GB ZIP fullstat only.','oneActionOnly':True}
out=S/'retained-native-zip-sharing-producer-root-r1.json'
with out.open('x') as f:json.dump(j,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
fd=os.open(out.parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
try:os.fsync(fd)
finally:os.close(fd)
print(json.dumps({'judgmentSHA256':sha(out),'actionPerformed':False}))
