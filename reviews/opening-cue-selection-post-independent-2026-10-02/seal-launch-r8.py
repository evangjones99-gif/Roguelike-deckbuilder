import os,sys,hashlib
from pathlib import Path
p=Path(__file__).with_name('seal-r7.py');b=p.read_bytes()
assert hashlib.sha256(b).hexdigest()=='89b2d8e47f5fb54e02e8859dac9f8aa0a3bf3c21e50105a447143930f220552e'
s=b.decode();a='existing=[dict(pin(x),relativePath:str(x.relative_to(P)))for x in []]\n';assert s.count(a)==1;s=s.replace(a,'')
needle="gate={'decision':review['decision']"
assert s.count(needle)==1
s=s.replace(needle,"review['reviewMethodFailures'].append({'script':'seal-r7.py','executed':False,'reason':'Unexecuted redundant manifest draft line had a syntax typo, identified before launch. Original draft retained; exact pinned r8 correction removes only that line before compilation.'})\n"+needle)
pid=os.fork()
if pid:
 _,status=os.waitpid(pid,0);sys.exit(os.waitstatus_to_exitcode(status))
exec(compile(s,str(p)+' (corrected)','exec'),{'__file__':str(p),'__name__':'__main__'})
