from pathlib import Path
p=Path(__file__).parent;s=(p/'audit.py').read_text()
a="hr[0]['exit_code']==1 and hr[1]['exit_code']==1";b="hr[0]['exit_code']==0 and hr[1]['exit_code']==1";assert s.count(a)==1
exec(compile(s.replace(a,b),str(p/'audit.py')+'+invalid-manifest-vs-exit','exec'))
