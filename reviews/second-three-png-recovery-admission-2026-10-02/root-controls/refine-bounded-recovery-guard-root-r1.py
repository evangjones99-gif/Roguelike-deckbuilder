from pathlib import Path
import json,hashlib
S=Path('/workspace/scratch');old=S/'guard-source-recovery-56m-root-r1.py';new=S/'guard-source-recovery-56m-root-r2.py';assert not new.exists()
b=old.read_text();assert b.count('assert PathlessScope if False else True\n')==1
new.write_text(b.replace('assert PathlessScope if False else True\n',''))
note=json.loads((S/'bounded-source-recovery-admission-proposal-root-r1.json').read_text())
note.update({'guardPath':str(new),'guardSHA256':hashlib.sha256(new.read_bytes()).hexdigest(),'guardRefinement':'Removed pointless always-true bootstrap assertion in fresh r2 wrapper; original r1 retained and never executed. Both bootstrap drafts were finite unguarded source-only preparation after oldsource64 admission refused, not certified guarded executions.'})
(S/'bounded-source-recovery-admission-proposal-root-r2.json').write_text(json.dumps(note,indent=2)+'\n')
print(json.dumps({'guard':str(new),'sha256':note['guardSHA256'],'noAction':True}))
