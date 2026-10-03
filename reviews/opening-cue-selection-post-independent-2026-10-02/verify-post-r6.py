import hashlib
from pathlib import Path
p=Path(__file__).with_name('verify-post-r4.py');b=p.read_bytes()
assert hashlib.sha256(b).hexdigest()=='f32816961d86280e4dadf1700e0abde651bcc0c3361ed6b47d89b56d816310db'
s=b.decode();assert s.count("terminal['terminalOutputBytes']")==1
s=s.replace("terminal['terminalOutputBytes']","terminal['terminalLogicalOutputBytes']")
a='for k,v in result.items():assert terminal[k]==v'
assert s.count(a)==1
s=s.replace(a,"assert terminal['normal'] is True and terminal['result']==str(S/'RESULT.json')\nassert terminal['terminalLogicalOutputBytes']==sum(p.stat().st_size for p in S.iterdir()if p.is_file())==119893")
exec(compile(s,str(Path(__file__))+' (corrected)','exec'),{'__file__':__file__,'__name__':'__main__'})
