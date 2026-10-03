from pathlib import Path
import os,json,hashlib,sys
S=Path('/workspace/scratch');R=Path('/workspace/Roguelike-deckbuilder');M=Path(__file__).parent
def sha(p):
 h=hashlib.sha256();fd=os.open(p,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW)
 with os.fdopen(fd,'rb') as f:
  for b in iter(lambda:f.read(65536),b''):h.update(b)
 return h.hexdigest()
proposal=M/'PROPOSAL.json';method=M/'retire-four-archived-json-root-r2.py';gate=S/'four-archived-raw-retirement-independent-r2/GATE.json';push=S/'four-archived-raw-retirement-push-root-r2/PUSH-CONFIRMED.json'
assert len(sys.argv)==2 and sha(gate)==sys.argv[1];g=json.loads(gate.read_text());p=json.loads(push.read_text())
assert g['decision'].startswith('ACCEPT') and g['replacementBetter'] and g['oldLooseCopiesNoLongerNeeded'] and g['proposal']['sha256']==sha(proposal) and g['method']['sha256']==sha(method)
assert g['currentHold']['sha256']==sha(R/'AGENTS.md') and p['confirmed'] and p['clean'] and p['gateSHA256']==sha(gate) and p['methodSHA256']==sha(method) and p['proposalSHA256']==sha(proposal)
assert (R/'.git/refs/heads/codex/lanternbound-production').read_text().strip()==p['commit']
D=R/'reviews/four-archived-json-retirement-2026-10-02';assert sha(D/'independent/GATE.json')==sha(gate) and sha(D/'root-controls'/method.name)==sha(method)
assert p['callerGateSHA256']==sha(D/'root-controls/DEFAULT-CALLER-GATE.json')==sha(S/'target-clear-default-caller-independent-r1/GATE.json')=='36ddead7bcd9647706f33c766952732dc3ff7b42455f2c678b125569bde2c31a'
assert p['supportBundle']['roundtripExact'] and sha(D/'source-support.tar.gz')==p['supportBundle']['sha256']
assert sha(D/'previous-R3-POST-GATE.json')==p['priorPostGateSHA256']=='2e8735abe975b28e42a1ce9d3a178ad6db9c251ca4f1de6acee3a979a361ec97'
j={'decision':'AUTHORIZE_EXACT_FOUR_ARCHIVED_RAW_RETIREMENTS_ONCE','proposalSHA256':sha(proposal),'gateSHA256':sha(gate),'methodSHA256':sha(method),'pushSHA256':sha(push),'commit':p['commit'],'callerGateSHA256':p['callerGateSHA256'],'judgment':'Prefer unchanged complete published byte-exact compressed successor; these four continuously loose copies add no unique body. Independent preference/no-longer-needed review plus current caller controls accepted. Only the four explicit historical wait/rejected-R1 rich JSON paths; keep every archive/JPEG/save/event/source/review/control/rights artifact.','losses':'Raw paths/inodes/time identity cease; historical direct readers require exact reconstruction into new paths and new adapted reader copies. No metadata rollback or four-leaf atomicity; durable prefix only. No backup/automatic retry/extra cleanup.','ordinaryAdmission':'64MiB work+512reserve/disk64 unchanged; native70/70.5 unchanged. Full current88/56 before/after and protectedZIPstat only.','oneActionOnly':True}
out=S/'four-archived-raw-retirement-producer-root-r2.json'
with out.open('x') as f:json.dump(j,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
fd=os.open(out.parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
try:os.fsync(fd)
finally:os.close(fd)
print(json.dumps({'judgmentSHA256':sha(out),'actionPerformed':False}))
