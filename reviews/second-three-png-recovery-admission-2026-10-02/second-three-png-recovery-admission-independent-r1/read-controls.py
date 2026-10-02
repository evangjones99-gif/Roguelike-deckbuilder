import pathlib,os,hashlib,resource
for name in ['publish-reviewed-recovery-admission-root-r1.py','judge-second-three-png-sharing-root-r2.py']:
 path=pathlib.Path('/workspace/scratch')/name;fd=os.open(path,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW)
 with os.fdopen(fd,'rb') as f:b=f.read()
 print(name,len(b),hashlib.sha256(b).hexdigest())
 for n,line in enumerate(b.decode().splitlines(),1):print(str(n)+': '+line)
print('OWN_RSS_KIB',resource.getrusage(resource.RUSAGE_SELF).ru_maxrss);assert resource.getrusage(resource.RUSAGE_SELF).ru_maxrss<24*1024
