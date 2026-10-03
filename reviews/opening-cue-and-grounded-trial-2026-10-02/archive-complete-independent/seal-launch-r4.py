import os,sys
from pathlib import Path
p=Path(__file__).with_name('seal-r4.py');s=p.read_text();pid=os.fork()
if pid:
 _,status=os.waitpid(pid,0);sys.exit(os.waitstatus_to_exitcode(status))
exec(compile(s,str(p),'exec'),{'__file__':str(p),'__name__':'__main__'})
