from pathlib import Path
import os,json,hashlib,sys
S=Path('/workspace/scratch');R=Path('/workspace/Roguelike-deckbuilder')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
proposal=S/'media-loose-png-recovery-proposal-author-r2/PROPOSAL.json';gate=S/'second-three-png-recovery-admission-independent-r1/GATE.json';push=S/'recovery-admission-push-root-r1/PUSH-CONFIRMED.json';method=S/'share-second-three-retained-pngs-root-r3.py'
assert sha(proposal)=='45ed75b5078c84e32981ba86b43f62826b00c53278ef8ea2f9888d661b8fd8d5'
g=json.loads(gate.read_text());assert g['decision'].startswith('ACCEPT')
assert len(sys.argv)==2 and sha(gate)==sys.argv[1]
assert g['method']['sha256']==sha(method) and g['proposal']['sha256']==sha(proposal)
assert g['currentHold']['sha256']==sha(R/'AGENTS.md')
assert g['selectedMap']['sha256']==sha(S/'target-wait-default-promotion-root-r1/RESULT.json')
p=json.loads(push.read_text());assert p['confirmed'] and p['clean']
assert (R/'.git/refs/heads/codex/lanternbound-production').read_text().strip()==p['commit']
assert (R/'reviews/second-three-png-recovery-admission-2026-10-02/second-three-png-recovery-admission-independent-r1/GATE.json').read_bytes()==gate.read_bytes()
assert (R/'reviews/second-three-png-recovery-admission-2026-10-02/root-controls/share-second-three-retained-pngs-root-r3.py').read_bytes()==method.read_bytes()
out=S/'second-three-png-producer-judgment-root-r2.json';assert not out.exists()
j={'decision':'AUTHORIZE_EXACT_THREE_PATH_PHYSICAL_SHARING_ONCE','proposalSHA256':sha(proposal),'independentGateSHA256':sha(gate),'methodSHA256':sha(method),'holdSHA256':sha(R/'AGENTS.md'),'selectedMapSHA256':sha(S/'target-wait-default-promotion-root-r1/RESULT.json'),'pushSHA256':sha(push),'commit':p['commit'],'candidateGroup':'/workspace/scratch/audio-host-independent-v08/independent/rebuilt-dist/art','names':['abbey-courtyard.png','tool-vignettes.png','hunter-portrait.png'],'judgment':'Prefer reviewed exact-byte shared physical encoding only for these three retained immutable historical leaves. Keep every body/path/provenance/rights/source/review/rollback. Current completed prior POST/rejected ghost and this pre-action proposal/method are confirmed pushed. No other cleanup or game promotion.','acceptedLosses':'Original private inode/time/write isolation replaced; canonical nlink5 to6 and ctime change, four known previous entries plus one unresolved alias each. Metadata rollback impossible; bytes retained. No old-inode backups or all-three power-loss atomicity; durable per-leaf prefix requires diagnosis if interrupted. Coordinated no-writer holds are not OS protection or universal FDs/mmap proof.','recoveryAdmission':'Separately reviewed56MiB source/recovery-only bounded profile after old64MiB refusal; build64/native70 unchanged. Wrapper filename filter isnotworkloadisolation; Root exactpinned scripts/scope only. No extra path or retry.', 'scopeLimits':'Wholehistorical66/51 aggregate remains pinned historical review, not newly fully replayed; commercialrights pending. Rejected unexecuted r1method retained. No oldreview rewritten; no version retired. Fresh method admission/currentclean/full87/56 identity and protected original fullstat before/after required.','oneActionOnly':True,'noAutomaticRetry':True}
out.write_text(json.dumps(j,indent=2)+'\n');print(json.dumps({'judgment':str(out),'sha256':sha(out),'commit':p['commit'],'actionPerformed':False}))
