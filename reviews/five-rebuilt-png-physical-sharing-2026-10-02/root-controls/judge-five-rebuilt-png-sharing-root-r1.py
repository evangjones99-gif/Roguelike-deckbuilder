from pathlib import Path
import os,json,hashlib,sys
S=Path('/workspace/scratch');R=Path('/workspace/Roguelike-deckbuilder')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
proposal=S/'five-rebuilt-png-recovery-proposal-r1/PROPOSAL.json';gate=S/'five-rebuilt-png-sharing-independent-r1/GATE.json';push=S/'five-rebuilt-png-proposal-push-root-r1/PUSH-CONFIRMED.json';method=Path(__file__).parent/'share-five-rebuilt-pngs-root-r1.py'
assert proposal.is_file() and sha(proposal)=='371c1e2df47f30e4abca9abece46864b53f4fb6f25e9a78926ee98a0d7a054c5'
assert sha(R/'AGENTS.md')=='6f76b3a724bcf4cd9db8587158a8bd454531c8a8b59fc8680bf7661d896ee2d8'
g=json.loads(gate.read_text());assert g['decision'].startswith('ACCEPT')
assert len(sys.argv)==2 and sha(gate)==sys.argv[1]
assert g['method']['sha256']==sha(method) and g['proposal']['sha256']==sha(proposal)
assert g['currentHold']['sha256']==sha(R/'AGENTS.md')
assert g['selectedMap']['sha256']==sha(S/'target-wait-default-promotion-root-r1/RESULT.json')
p=json.loads(push.read_text());assert p['confirmed'] and p['clean']
assert p['gateSHA256']==sha(gate) and p['methodSHA256']==sha(method) and p['proposalSHA256']==sha(proposal) and p['holdSHA256']==sha(R/'AGENTS.md')
assert p['R3CompleteGateSHA256']=='6ec96568886fbeede7c9abacd6365edffa9cb4a7401c9d143ca50a281fd6ac65'
assert sha(R/'reviews/five-rebuilt-png-physical-sharing-2026-10-02/root-controls/R3-PRESERVATION-COMPLETE-GATE.json')==p['R3CompleteGateSHA256']
assert (R/'.git/refs/heads/codex/lanternbound-production').read_text().strip()==p['commit']
assert (R/'reviews/five-rebuilt-png-physical-sharing-2026-10-02/five-rebuilt-png-sharing-independent-r1/GATE.json').read_bytes()==gate.read_bytes()
assert (R/'reviews/five-rebuilt-png-physical-sharing-2026-10-02/root-controls/share-five-rebuilt-pngs-root-r1.py').read_bytes()==method.read_bytes()
out=S/'five-rebuilt-png-producer-judgment-root-r1.json';assert not out.exists()
j={'decision':'AUTHORIZE_EXACT_FIVE_PATH_PHYSICAL_SHARING_ONCE','proposalSHA256':sha(proposal),'independentGateSHA256':sha(gate),'methodSHA256':sha(method),'holdSHA256':sha(R/'AGENTS.md'),'selectedMapSHA256':sha(S/'target-wait-default-promotion-root-r1/RESULT.json'),'pushSHA256':sha(push),'commit':p['commit'],'candidateGroup':'/workspace/scratch/audio-host-independent-v08/independent/rebuilt-dist/art','names':['adversaries-atlas.png','companions-atlas.png','hound-poses.png','pact-seal.png','warleader-poses.png'],'judgment':'Prefer reviewed exact-byte shared physical encoding only for these five retained immutable historical leaves. Keep every body/path/provenance/rights/source/review/rollback. Completed prior first-five sharing POST/control records, complete R3 opt-in preservation and this pre-action rebuilt-five proposal/method are confirmed pushed. No other cleanup or game promotion.','acceptedLosses':'Original private inode/time/write isolation replaced; each canonical nlink increases one and ctime changes; known/unresolved aliases remain qualified by the exact proposal. Metadata rollback impossible; bytes retained. No old-inode backups or all-five power-loss atomicity; durable per-leaf prefix requires diagnosis if interrupted. Coordinated no-writer holds are not OS protection or universal FDs/mmap proof.','recoveryAdmission':'Unchanged ordinary64MiB disk admission and64+512MiB source/action memory profile. Build64/native70 unchanged. Exact Root method and five paths only; no extra path or retry.', 'scopeLimits':'Wholehistorical66/51 aggregate remains pinned historical review, not newly fully replayed; commercialrights pending. Previous original methods and completed first action controls retained; this is a distinct rebuilt-five method. No oldreview rewritten; no version retired. Fresh method admission/currentclean/full87/56 identity and protected original fullstat before/after required.','atimeQualification':'Fresh initial atime-only rebinding preserves proposalMetadata; no timestamp reset, all other metadata and full body checks remain exact. Previous first-five method/action/POST remain untouched; this is a distinct rebuilt-five scope and one action only.','oneActionOnly':True,'noAutomaticRetry':True}
with out.open('x') as f:json.dump(j,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
fd=os.open(out.parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
try:os.fsync(fd)
finally:os.close(fd)
print(json.dumps({'judgment':str(out),'sha256':sha(out),'commit':p['commit'],'actionPerformed':False,'authorizationFileAndParentFsyncReturned':True}))
