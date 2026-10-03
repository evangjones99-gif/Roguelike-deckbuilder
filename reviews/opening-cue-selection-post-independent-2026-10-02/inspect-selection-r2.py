import os,json
from pathlib import Path
P=Path(__file__).parent;R=Path('/workspace/Roguelike-deckbuilder');C=R/'reviews/opening-cue-and-grounded-trial-2026-10-02';S=Path('/workspace/scratch/wording-development-source-selection-actual-root-r1')
def read(p):
 fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME)
 try:return b''.join(iter(lambda:os.read(fd,65536),b''))
 finally:os.close(fd)
v=json.loads(read(C/'PUBLICATION.json'));print('METHODRECORDS',[x for x in v['records']if x['originalPath'].endswith('.py') and '/workspace/scratch/'in x['originalPath'] and '/'not in x['originalPath'][len('/workspace/scratch/'):]])
for n in ['BEFORE.json','JOURNAL.jsonl']:print(n,read(S/n).decode())
print('README_CURRENT',read(R/'README.md').decode()[-2500:])
i=json.loads(read(C/'archive/INDEX.json'));matches=[x for x in i['rows']if str(Path(i['roots'][x[0]])/x[1])==str(R/'README.md')];print('README_ROWS',matches);print('ACTUAL_RECORDCOUNT',len(v['records']))
