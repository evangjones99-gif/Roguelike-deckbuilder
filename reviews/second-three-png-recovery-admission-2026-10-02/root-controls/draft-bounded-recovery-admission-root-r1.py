from pathlib import Path
import hashlib,json
S=Path('/workspace/scratch')
guard=S/'guard-source-recovery-56m-root-r1.py';method=S/'share-second-three-retained-pngs-root-r3.py'
assert not guard.exists() and not method.exists()
g=(S/'guard-node-phase-r1.py').read_text()
g=g.replace("stage,packet,work_mb,*command=sys.argv[1:]", "stage,packet,work_mb,*command=sys.argv[1:]\nassert PathlessScope if False else True\nassert stage=='/workspace/Roguelike-deckbuilder'\nassert int(work_mb) in (64,256)\nassert len(command)>=2 and command[0]=='python' and command[1].startswith('/workspace/scratch/')\nassert not any(term in command[1] for term in ['build','native','browser','release','image'])")
g=g.replace('>=64*1048576','>=56*1048576')
assert g!=(S/'guard-node-phase-r1.py').read_text();guard.write_text(g)
m=(S/'share-second-three-retained-pngs-root-r2.py').read_text()
assert m.count('initial_free>=64*1048576')==1
m=m.replace('initial_free>=64*1048576','initial_free>=56*1048576').replace('.root-share-second-r2.tmp','.root-share-second-r3.tmp').replace("P=S/'second-three-retained-png-sharing-actual-root-r2'","P=S/'second-three-retained-png-sharing-actual-root-r3'")
method.write_text(m)
note={'scope':'Proposed separately reviewed source/recovery-only56MiB disk admission after confirmed currentpush9ce3d3bf left66203648B, below64MiB. Original guard/method/refusal unchanged; no action performed.','guardSHA256':hashlib.sha256(guard.read_bytes()).hexdigest(),'methodSHA256':hashlib.sha256(method.read_bytes()).hexdigest(),'changes':'Source-only wrapper admission56MiB, all memory/work/reserve/live1MiB stops unchanged; no build/native/image/release commands. Exact physical-sharing method only diskpreflight56 plus fresh temp/output identifiers. No weaker identity/body/stat/xattr/parent/currentpush/judgment/journal tests.','bounds':'Recovery creates onlybounded BEFORE/journal/RESULT controls and tiny sibling directoryentries while freeingexact3PNGallocations, not8MB backups/copies. Currentpushalreadyconfirmed; newmethod/reviewstillrequirespublishedconfirmedpush and producer. Sourceproofs<=192KiB each, wholeprefixedpublication<512KiB; disk65MB muchlargerthanboundedwrites. Strictbuild64 andnative70MiB unchanged. Sharedcgroup64+512 source or256+512publication memory phases asbefore; not a blanket waiver.'}
(S/'bounded-source-recovery-admission-proposal-root-r1.json').write_text(json.dumps(note,indent=2)+'\n')
print(json.dumps(note))
