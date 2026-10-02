import os,json,resource
from pathlib import Path
P=Path(__file__).parent;R=Path('/workspace/Roguelike-deckbuilder');C=R/'reviews/opening-cue-and-grounded-trial-2026-10-02';S=Path('/workspace/scratch/wording-development-source-selection-actual-root-r1')
def read(p):
 fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME)
 try:return b''.join(iter(lambda:os.read(fd,65536),b''))
 finally:os.close(fd)
a=read(R/'AGENTS.md').decode();print('AGENTS_CURRENT_PREFIX',a[:8500]);print('AGENTS_LENGTH',len(a))
for root,n in [(C,'PUBLICATION.json'),(S,'RESULT.json')]:
 v=json.loads(read(root/n));print(n,'KEYS',list(v));print('SAMPLES',str(v)[:4800])
print('SELECTION_FILES',[(x.name,x.stat().st_size)for x in S.iterdir()if x.is_file()]);print('COPY_README',read(C/'README.md').decode()[:4500]);print('RSS',resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024)
