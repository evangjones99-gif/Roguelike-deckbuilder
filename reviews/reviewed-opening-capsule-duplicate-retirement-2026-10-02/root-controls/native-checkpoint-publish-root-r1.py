from pathlib import Path
import os,json,hashlib,time
S=Path('/workspace/scratch');R=Path('/workspace/Roguelike-deckbuilder');O=R/'reviews/opening-native-aftermath-and-starter-art-2026-10-02'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(65536):h.update(b)
 return h.hexdigest()
g=S/'native-checkpoint-archive-complete-independent-r1/GATE.json';assert sha(g)=='08d09c6abe9886a0c52590c4f519fb0a9c6f113aa8b9be62b4b594e517419078';gate=json.loads(g.read_bytes());assert gate['accepted'] and gate['COMPLETE'] and gate['preservationOnly']
assert sha(Path(gate['archivePath']))==gate['archiveSHA256'];assert sha(O/'archive/INDEX.json')==gate['indexSHA256']
rows=[]
def copy(p,q):
 assert p.is_file() and not p.is_symlink();q.parent.mkdir(parents=True,exist_ok=True);b=p.read_bytes();h=hashlib.sha256(b).hexdigest()
 with q.open('xb') as f:f.write(b);f.flush();os.fsync(f.fileno())
 assert sha(q)==h;rows.append({'originalPath':str(p),'canonicalPath':str(q),'sha256':h,'bytes':len(b)})
for folder,target in [('native-checkpoint-archive-complete-independent-r1','archive-complete-independent'),('native-checkpoint-root-manifest-independent-r1','root-manifest-independent'),('native-aftermath-starter-checkpoint-source-independent-r1','archive-source-independent'),('native-checkpoint-archive-guard-root-r1','archive-resource-closure')]:
 base=S/folder
 for p in sorted(base.rglob('*')):
  if p.is_file() and not p.is_symlink():copy(p,O/target/p.relative_to(base))
for folder,target in [('native128-defeat-aftermath-actual-technical-independent-r2','corpse-technical'),('native128-defeat-aftermath-actual-visual-independent-r1','corpse-visual'),('native128-defeat-aftermath-actual-gameplay-independent-r2','corpse-gameplay'),('native128-floor-perspective-actual-technical-independent-r1','floor-technical'),('native128-floor-perspective-actual-visual-independent-r1','floor-visual'),('native128-floor-perspective-actual-gameplay-independent-r1','floor-gameplay'),('starter-family-native128-final-output-engineering-independent-r3','starter-engineering'),('starter-family-native128-assets-visual-independent-r3','starter-art-rejected'),('ash-widow-correction-native128-final-engineering-independent-r2','ash-engineering'),('ash-widow-correction-native128-native-visual-independent-r2','ash-art-private-fit')]:copy(S/folder/'GATE.json',O/'gates'/target/'GATE.json')
for name in ['native-checkpoint-root-manifest-r1.py','native-checkpoint-root-manifest-r2.py','native-checkpoint-root-manifest-r3.py','native-checkpoint-final-input-manifest-root-r1.json'] :copy(S/name,O/'root-manifest-history'/name)
for folder in ['native-checkpoint-manifest-guard-root-r1','native-checkpoint-manifest-guard-root-r2','native-checkpoint-manifest-guard-root-r3']:
 for p in sorted((S/folder).rglob('*')):
  if p.is_file() and not p.is_symlink():copy(p,O/'root-manifest-history'/folder/p.relative_to(S/folder))
readme='''# Native pixel opening: aftermath and starter-art checkpoint

This checkpoint preserves two played comparisons. The corrected Reaver defeat remains visible briefly and then disappears; the receding floor makes the battlefield read more clearly as ground. Independent gameplay and visual reviewers accept those narrow improvements and **reject default pixel-scene quality and complete combat payoff**. The scene still lacks crafted environment detail, strong ground contact and articulated creature animation. No game source or release is selected by this archive.

| Trial | Exact source | Exact outputs | Observed duration |
| --- | --- | --- | --- |
| Corpse retention | `10faa229984f1e2d30fe5f715301d52c31066b7849c3a7220e019a3f81694950` | `abb1a6411776a2d15995edc523de7b72b6ad735348590173dbe8cbeb3c3c555c` | 53.707813 seconds, two contexts |
| Floor perspective | `a8913c85dd6dc0c009e7c5de10a3095a4a4f8336e9944eb68f3979371b63305b` | `c9cd8c8ce61064901e908446a6cefecfc3742657fee39ecdd6d78ba7e1150880` | 54.949869 seconds, two contexts |

Each trial retains four original screenshots and six complete equal saved-string pairs. Ordinary binding, free Order, held Escape cancellation and two distinct Scours were observed. The requested illegal-held transition was not observed. Sampled early/expired defeat receipts do not certify continuous contact timing, the final enemy kill, reduced motion, an enemy turn, a complete 300-second session or human enjoyment. The floor supervisor's final 54.954884-second terminal value was reported by Root tool history; the saved post-closure receipt independently records 54.953892 seconds.

The first six new starter sprites passed saved-output engineering, but independent art review rejected the original spider pair. Fen Stalker and Briar Colossus are eligible only for private scene fitting. The revised Ash Widow pair passes engineering and private-fit art review: its head/fangs read more clearly, while overlapping legs and edge noise still need battlefield inspection. Eight visible legs are not certified. These are native 128×128, shared 15-colour, binary-alpha drafts with literal nearest-neighbour previews. The conversion recorded an empty manual-cleanup recipe; it is not hand-authored cleanup or animation. No new starter-family sprite has been integrated into the selected game by this checkpoint.

Archive `8cdf546a8429e949fe88611d781aca341566f473135fbcbe44b5373beabd7aa8` is 5,085,419 bytes. [INDEX.json](archive/INDEX.json) maps 1,278 exact logical identities to 1,116 new unique bodies and explicit prior4513 inheritance. [Independent COMPLETE gate](archive-complete-independent/GATE.json) `08d09c6a…` verifies new decoded-original byte equality, eight JPEGs, twelve full saved pairs and four gzip evidence domains. Earlier Source verification hashed every logical row; the final archive review renewed representative new bodies, with duplicate/inherited authority explicit. All original files remain. Frozen media, installed tools and prior capsules remain external; this is not a self-contained release.

The archive includes complete fixed source/control/review trees and original failures, six original actual gates, both generated masters, old rejected spider art, the revised spider, and 86 frozen runtime code rows. CSS source/control proposals are included; their later strict build and failed actual comparison are outside this fixed archive. Root manifest R1 omitted runtime stages; R2 stopped on a nonexistent guessed Vitest package. Their original methods, the invalid R1 manifest and guard receipts are preserved separately in `root-manifest-history`. Corrected R3 includes both exact 43-code-path maps and actually installed tool metadata. Original review decisions were not rewritten.

Continue the empty-intent repair comparison and starter-family coverage. Development source remains `64c2a14a…`: start `npm run dev -- --host 0.0.0.0` and open the printed port, normally 5173. Preview/desktop still use the held older `8bbaea72…` dist. No server was launched for publication; no tag, version increment, cleanup, native platform qualification or human-fun claim follows.
'''
(O/'README.md').open('x').write(readme)
common='''## Pixel aftermath and starter-art evidence preserved — 2 October 2026

New evidence checkpoint: [native aftermath and starter art](LINK). Archive `8cdf546a8429e949fe88611d781aca341566f473135fbcbe44b5373beabd7aa8` preserves 1,278 logical identities, 1,116 new unique bodies, eight original screenshots, twelve full saved-string pairs, four original gzip evidence domains and original positive/negative reviews. Independent COMPLETE gate `08d09c6abe9886a0c52590c4f519fb0a9c6f113aa8b9be62b4b594e517419078` verifies preservation only; prior4513 proof inheritance and external media/dependencies remain explicit. All original paths remain; no cleanup or release/tag occurred.

Corpse retention (`10faa229…` / `abb1a641…`) and receding floor (`a8913c85…` / `c9cd8c8c…`) completed actual comparisons with separate gameplay, visual and technical reviews. Narrow sampled defeat feedback and ground readability improve; default pixel scene and complete payoff remain rejected. Illegal-held readiness was unobserved; these are short source-informed runs, not human enjoyment or completed 300-second sessions.

The six starter sprites passed engineering but the old spider pair was rejected. A revised native128 spider (`e02e10cb…` rear, `21bead97…` front) passes engineering and private scene-fit eligibility only. No deliberate manual cleanup, eight-leg certification, animation or actual battlefield approval is claimed. Fen/Briar and the revised spider still need gameplay integration and review. The empty-intent CSS repair is strict-built privately at source `76e5ba02635900ad242b047f9aa5e11adbc67b9e99f9cb67b35884405d21bc40`, outputs `2547c159b14f634a2ec17473bded94af60c38e6f4aba8ea208f32dba9875f3a8`. Its first actual comparison exceeded the 896 MiB aggregate work cap, preserved two baseline originals and closed all owned processes; no CSS acceptance or game-performance causality follows. A narrower independently reviewed diagnostic caller has passed grammar checks; fresh actual admission and separate reviews remain required.

Selected development source remains `64c2a14a…` (89 inputs), with the clearer spent-command cue ON. Held canonical dist remains `8bbaea72…` (56 outputs). Continue the empty-intent comparison and four-starter pixel coverage; broader scene craft remains open. Older entries below are historical, with their exact freeze/alias holds still active.

'''
expected={'AGENTS.md':'8bc4786d1b87df687f2e94597a0b23a7686548215f31519041e439ecf383ce87','docs/CONTINUATION.md':'dc167c7ab5c5af1cf96b4f521b0a12615e7de703f0cbd047aaaa225897ac653e','docs/PRODUCTION.md':'ec40d38d418355631d5b3e60be99f9167bfe35ad66cb88e87b5107d021d2c86a'}
docs=[]
for rel,h in expected.items():
 p=R/rel;assert sha(p)==h;old=p.read_bytes();link='reviews/opening-native-aftermath-and-starter-art-2026-10-02/README.md' if rel=='AGENTS.md' else '../reviews/opening-native-aftermath-and-starter-art-2026-10-02/README.md';prefix=common.replace('LINK',link).encode();new=prefix+old;p.write_bytes(new);assert p.read_bytes()[len(prefix):]==old;docs.append({'path':str(p),'previousSHA256':h,'newSHA256':sha(p),'prefixBytes':len(prefix),'oldLiteralSuffixPreserved':True})
receipt={'scope':'Root literal publication after independent COMPLETE; current source/held dist unchanged, no cleanup/release','completeGateSHA256':sha(g),'copyRows':rows,'documentPrefixRows':docs,'archiveImmutableAfterCOMPLETE':True,'originalFailuresPreserved':True,'soleCanonicalWriter':'Root','utcNs':time.time_ns()};(O/'PUBLICATION.json').open('x').write(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'literalCopies':len(rows),'copiedBytes':sum(x['bytes'] for x in rows),'documentPrefixes':len(docs),'publicationSHA256':sha(O/'PUBLICATION.json'),'selectedRuntimeUnchanged':True}))
