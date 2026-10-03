import resource,subprocess
print('finiteLauncherRSS',resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,flush=True)
r=subprocess.run(['python3','/workspace/scratch/five-png-recovery-admission-independent-r1/verify-r3.py'])
print('childReturn',r.returncode)
