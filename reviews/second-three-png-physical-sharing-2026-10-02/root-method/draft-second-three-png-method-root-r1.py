from pathlib import Path
import json,hashlib
S=Path('/workspace/scratch');R=Path('/workspace/Roguelike-deckbuilder')
p=S/'share-second-three-retained-pngs-root-r1.py';assert not p.exists()
b=(S/'share-three-retained-pngs-root-r2.py').read_text()
b=b.replace("E=read(proposal);pairs=E['pairs'];assert len(pairs)==3 and E['verification']=='EXACT_MATCH'", "E=read(proposal);pairs=E['pairs'];assert len(pairs)==3\nfor pair in pairs:\n for kind in ['candidate','canonical']:\n  assert pair[kind]['lstat']==pair[kind]['fstat']\n  pair[kind]['metadata']=pair[kind]['fstat']\nassert E['candidateGroup']=='/workspace/scratch/audio-host-independent-v08/independent/rebuilt-dist/art'")
b=b.replace("oldroot=S/'audio-host-independent-v08/candidate/dist/art'", "oldroot=S/'audio-host-independent-v08/independent/rebuilt-dist/art'")
b=b.replace("b['metadata']['st_nlink']==1 and a['metadata']['st_dev']", "b['metadata']['st_nlink']==1 and a['metadata']['st_nlink']==5 and a['metadata']['st_dev']")
b=b.replace('.root-share-r1.tmp','.root-share-second-r1.tmp').replace("P=S/'three-retained-png-sharing-actual-root-r1'", "P=S/'second-three-retained-png-sharing-actual-root-r1'")
p.write_text(b)
hold='The three historical `/workspace/scratch/audio-host-independent-v08/independent/rebuilt-dist/art/abbey-courtyard.png`, `tool-vignettes.png` and `hunter-portrait.png` leaves are also immutable and fresh-stage-only. Preserve their exact independent historical rebuild bodies and consumer evidence. Future reproduction uses fresh stages/inodes; no writes, truncation, chmod, xattr or timestamp changes through these leaves. A separately reviewed exact physical-sharing proposal requires producer judgment and confirmed current push; this coordinated hold grants no transaction, deletion or retirement authority and is not OS-enforced protection.\n\n'
a=R/'AGENTS.md';text=a.read_text();marker='## Immutable retained art aliases\n\n';assert text.count(marker)==1;a.write_text(text.replace(marker,marker+hold))
print(json.dumps({'method':str(p),'methodSHA256':hashlib.sha256(p.read_bytes()).hexdigest(),'holdSHA256':hashlib.sha256(a.read_bytes()).hexdigest(),'actionPerformed':False}))
