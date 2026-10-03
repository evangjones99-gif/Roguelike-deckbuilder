import resource,subprocess
own=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024
print('finiteSealLauncherRSS',own,flush=True)
assert own<24*1048576
r=subprocess.run(['python3','/workspace/scratch/five-png-recovery-admission-independent-r1/seal.py'])
assert r.returncode==0
print('sealChildReturn',r.returncode)
