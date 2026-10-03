import pathlib,os,json,hashlib,resource
p=pathlib.Path('/workspace/scratch/media-loose-png-recovery-proposal-author-r2')
def read(path):
 fd=os.open(path,os.O_RDONLY|os.O_NOATIME)
 with os.fdopen(fd,'rb') as f:return f.read()
for name in ['PROPOSAL.json','FINAL-SEAL.json','MANIFEST.json']:
 path=p/name
 if path.exists():
  b=read(path);print(name,len(b),hashlib.sha256(b).hexdigest(),b.decode())
print('METHOD',len(read('/workspace/scratch/share-second-three-retained-pngs-root-r1.py')),hashlib.sha256(read('/workspace/scratch/share-second-three-retained-pngs-root-r1.py')).hexdigest())
print('OWN_RSS_KIB',resource.getrusage(resource.RUSAGE_SELF).ru_maxrss);assert resource.getrusage(resource.RUSAGE_SELF).ru_maxrss<24*1024
