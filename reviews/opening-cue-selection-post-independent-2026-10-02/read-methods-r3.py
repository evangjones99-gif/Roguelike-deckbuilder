import os
from pathlib import Path
C=Path('/workspace/Roguelike-deckbuilder/reviews/opening-cue-and-grounded-trial-2026-10-02')
for n in ['ROOT-SELECTION-LAUNCHER.py','ROOT-PUBLICATION-SOURCE.py']:
 fd=os.open(C/n,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME)
 try:b=b''.join(iter(lambda:os.read(fd,65536),b''))
 finally:os.close(fd)
 print(n,b.decode())
