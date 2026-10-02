from pathlib import Path
p=Path(__file__).parent/'audit.py'
s=p.read_text();old="['git','--no-optional-locks',*args]"
assert s.count(old)==1
# Command-local settings disable threaded stat preload; no Git config mutation.
exec(compile(s.replace(old,"['git','--no-optional-locks','-c','core.preloadIndex=false','-c','index.threads=1',*args]"),str(p),'exec'))
