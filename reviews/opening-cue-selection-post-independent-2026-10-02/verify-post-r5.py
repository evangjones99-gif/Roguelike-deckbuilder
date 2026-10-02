import hashlib
from pathlib import Path
p=Path(__file__).with_name('verify-post-r4.py');b=p.read_bytes()
assert hashlib.sha256(b).hexdigest()=='f32816961d86280e4dadf1700e0abde651bcc0c3361ed6b47d89b56d816310db'
s=b.decode();assert s.count("terminal['terminalOutputBytes']")==1
s=s.replace("terminal['terminalOutputBytes']","terminal['terminalLogicalOutputBytes']")
exec(compile(s,str(Path(__file__))+' (corrected)','exec'),{'__file__':__file__,'__name__':'__main__'})
