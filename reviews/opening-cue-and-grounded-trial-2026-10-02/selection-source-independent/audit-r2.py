from pathlib import Path
p=Path(__file__).parent;s=(p/'audit.py').read_text()
a="for row in j(A/'MANIFEST.json')['files']:assert pin(Path(row['path']))==row"
b="for name,row in j(A/'MANIFEST.json')['files'].items():\n q=pin(A/name);assert {k:q[k] for k in ('bytes','sha256')}==row"
assert s.count(a)==1
exec(compile(s.replace(a,b),str(p/'audit.py'),'exec'))
