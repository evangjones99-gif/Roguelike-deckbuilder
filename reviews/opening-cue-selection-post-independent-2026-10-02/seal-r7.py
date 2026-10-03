import os,json,hashlib,resource
from pathlib import Path
P=Path(__file__).parent;R=Path('/workspace/Roguelike-deckbuilder');C=R/'reviews/opening-cue-and-grounded-trial-2026-10-02'
def pin(p):
 h=hashlib.sha256();n=0
 with p.open('rb')as f:
  while b:=f.read(65536):h.update(b);n+=len(b)
 return {'path':str(p),'sha256':h.hexdigest(),'bytes':n}
def body(v):return(json.dumps(v,indent=2,sort_keys=True)+'\n').encode()
v=json.loads((P/'POST-CHECKS.json').read_bytes());guards=[]
for d in sorted(P.glob('*guard-*')):
 r=json.loads((d/'RESULT.json').read_bytes());assert r['memory_events_before']==r['memory_events_after']and 'all child group processes closed'in r['scope']
 guards.append({'path':str(d),'resultSHA256':pin(d/'RESULT.json')['sha256'],'exitCode':r['exit_code'],'samples':len(r['samples']),'observedChildGroupClosed':True})
assert sum(x['exitCode']==1 for x in guards)==2 and sum(x['exitCode']==0 for x in guards)==4
freeze=json.loads(Path('/workspace/scratch/opening-turn-payoff-wording-strict-build-root-r1/final-seal-r1/RUNTIME-FREEZE.json').read_bytes())
src={str(p.relative_to(R))for p in(R/'src').rglob('*')if p.is_file()};assert src=={p for p in freeze['inputs']if p.startswith('src/')}
review={'decision':'ACCEPT_LITERAL_CHECKPOINT_PUBLICATION_AND_DEVELOPMENT_SOURCE_SELECTION_POST_ONLY',
 'findings':['All 120 copied originals and destinations match complete SHA, length and literal bytes, totaling 9,298,292 bytes. The published folder contains exactly those 120 files plus its new README and PUBLICATION.json, with no symlink or unexpected file. README exactly reproduces publication scope. Full source-author, failed r1, accepted r2 and COMPLETE review families match source-folder membership and retain their original controls/failures.',
 'Canonical development inputs exactly match all 89 bodies of the reviewed frozen wording candidate64c2. The full canonical src tree matches that mapped membership. Compared with selected rollback c4fa inputs, only main changes to efecdc20 and a new 163-byte CSS a84a4a47 is added. Canonical dist has exact 56-file membership and all old8b bodies; reviewed82e output remains a separate frozen reference.',
 'Old main is exactly retained at OLD-main.ts and in preservation evidence. Current new main matches its recorded owner/mode/inode/stat/xattrs. Its old inode/time identity is surrendered rather than claimed restored. Six journal events are ordered through backup, fresh temporary, new CSS creation, main atomic replacement and full post-verification; the two source files are explicitly not atomic together.',
 'Four updated documents are prepend-only: every complete original archived document body remains as suffix. Their current status clearly distinguishes selected development source, held older preview/desktop dist and unselected pixel trials. README is exactly one authorized cue instruction insertion over Git d144, with full inverse verified. Historical INDEX original-path bodies need not equal later authorized canonical text.',
 'Root publication and source-selection guards are normal0 with unchanged events and observed child-group closure. Exact separate selection terminal envelope identifies normal completion and RESULT path, 0.24063163198297843 seconds, 11,904 KiB own RSS and 119,893 current output bytes. The gate-bound reviewed method/source grant and literal publication/control bodies match.'],
 'limitations':['This accepts the observed canonical copy and development-source selection scope. No dev server, game, build, desktop preview, release/tag or additional cleanup was run by this reviewer; current source execution is not newly demonstrated here. Canonical dist deliberately does not match the new source.',
 'The two-file selection was not globally atomic; individual fresh-file and journal durability is scoped to the reviewed method and Root sole-writer coordination, not OS compare-and-swap, universal process absence or full-prefix restoration. Publication bootstrap and supplemental generated-master metadata remain explicitly qualified tool-history derivatives, not literal prompt/rights proof.',
 'The publication copy method does not provide a directory-crash-durability transaction guarantee. Literal normal readback and exact membership are verified; no inode/timestamp/permission equivalence for copied evidence is asserted. O_NOATIME reads had no fallback in this audit, but tool/bootstrap resource use is unmetered.',
 'Both prior capsules, their exact indexes/COMPLETE proofs, external media/node_modules and baseline support remain required. COMPLETE byte preservation does not make a self-contained release or approve pixel depth, sustained corpse payoff, animation, first300 or human enjoyment. Original positive and negative reviews are unchanged.',
 'The read-only historical Git lookup verifies README inverse only. This gate does not verify the upcoming current push or authorize arbitrary further publication/runtime changes; Root must record the subsequent clean confirmed push.'],
 'reviewMethodFailures':[{'script':'verify-post-r4.py','guard':'post-guard-r4','exitCode':1,'reason':'Wrong terminal field terminalOutputBytes; actual envelope uses terminalLogicalOutputBytes. Byte/source/doc checks before the error were read-only.'},{'script':'verify-post-r5.py','guard':'post-guard-r5','exitCode':1,'reason':'Incorrectly treated terminal envelope as the RESULT body and indexed decision. Fresh r6 verifies its actual normal/result-path/measurement domain and passed.'}],
 'allFailedControlsPreserved':True,'checks':pin(P/'POST-CHECKS.json'),'resourceScope':{'profileMiB':[64,512,64],'ownVerifierRSSBytes':v['ownRSSBytes'],'guards':guards,'sparseSharedCgroupNotContinuousOrExclusive':True,'tinyBootstrapReadbacksAndFinalForkedSealerUnmetered':True},'ownObservedToolsAndGuardsClosed':True}
gate={'decision':review['decision'],'canonicalLiteralPublicationAccepted':True,'developmentSourceSelectionPostAccepted':True,'publication':pin(C/'PUBLICATION.json'),'sourceSelectionResult':v['sourceSelectionResult'],'copiedBodies':120,'copiedBytes':9298292,'exactPublishedFileMembership':122,'canonicalSourceDigest':'64c2a14ada2b24796535f9bb71d8a6acc534685365bcf4f5665b21bf18595353','canonicalInputCount':89,'canonicalHeldDistDigest':'8bbaea72d9cb3b9757a2b8cb10ead190495ef61e6496e1ace0f942f635e00cf7','canonicalHeldDistOutputCount':56,'reviewedCandidateBuildDigest':'82e049c9fee16e4a56d80520a0feb19c54546dc86f83953f27d703d53fec7042','completePreservationGateSHA256':'df8ef40e5409409f004d2a2c08d7ca20dfb519f31590c379459c29d2f6983a85','onlyMainAndNewCueCSSChangedInInputMap':True,'fourDocsFullOldBodyRetained':True,'readmeOneInsertionInverseToD144':True,'currentPushConfirmed':False,'gameArtReleaseFunApproval':False,'additionalCleanupAuthorized':False,'TOOL_GUARD_CLOSED':True}
pending={'REVIEW.json':body(review),'GATE.json':body(gate)}
existing=[dict(pin(x),relativePath:str(x.relative_to(P)))for x in []]
existing=[dict(pin(x),relativePath=str(x.relative_to(P)))for x in sorted(P.rglob('*'))if x.is_file()]
manifest={'familyLogicalCapBytes':98304,'failedMethodsRemainPreserved':True,'bodies':existing+[{'path':str(P/k),'relativePath':k,'bytes':len(v),'sha256':hashlib.sha256(v).hexdigest()}for k,v in pending.items()]}
pending['MANIFEST.json']=body(manifest);base=sum(x['bytes']for x in existing)+sum(len(v)for v in pending.values())
final={'sealed':True,'TOOL_GUARD_CLOSED':True,'gateSHA256':hashlib.sha256(pending['GATE.json']).hexdigest(),'reviewSHA256':hashlib.sha256(pending['REVIEW.json']).hexdigest(),'manifestSHA256':hashlib.sha256(pending['MANIFEST.json']).hexdigest(),'familyLogicalCapBytes':98304,'familyLogicalBytes':0,'finalSealerOwnRSSBytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,'finalSealerGuarded':False}
for _ in range(5):final['familyLogicalBytes']=base+len(body(final))
pending['FINAL-SEAL.json']=body(final);assert base+len(pending['FINAL-SEAL.json'])==final['familyLogicalBytes']<=98304;assert final['finalSealerOwnRSSBytes']<24*1048576
for k,b in pending.items():
 with(P/k).open('xb')as f:f.write(b);f.flush();os.fsync(f.fileno())
fd=os.open(P,os.O_DIRECTORY|os.O_RDONLY);os.fsync(fd);os.close(fd)
assert sum(x.stat().st_size for x in P.rglob('*')if x.is_file())==final['familyLogicalBytes']
print(json.dumps(final,sort_keys=True))
