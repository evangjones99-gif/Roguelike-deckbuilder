import os,sys
from pathlib import Path
s=Path(__file__).with_name('seal-r6.py').read_text()
pid=os.fork()
if pid:
 _,status=os.waitpid(pid,0)
 sys.exit(os.waitstatus_to_exitcode(status))
exec(compile(s,str(Path(__file__).with_name('seal-r6.py')),'exec'),{'__file__':str(Path(__file__).with_name('seal-r6.py')),'__name__':'__main__'})
