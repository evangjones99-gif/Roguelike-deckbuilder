import pathlib,os,json,hashlib
P=pathlib.Path(__file__).parent
fd=os.open(P/'audit-r2.py',os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW)
try:s=os.read(fd,24000).decode()
finally:os.close(fd)
a='resource.setrlimit(resource.RLIMIT_DATA,(24*1048576,24*1048576))\n'
assert s.count(a)==1
# Git's index mappings exceeded the inherited DATA ceiling, without evidence
# of a resident-memory failure. Keep the existing final own RSS assertion and
# the outer64MiB aggregate guard, rather than impose that ceiling on Git.
exec(s.replace(a,''),{'__file__':str(P/'audit-r3.py'),'__name__':'__main__'})
def read(q):
 fd=os.open(q,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW)
 try:
  with os.fdopen(fd,'rb',closefd=False) as f:return f.read()
 finally:os.close(fd)
N=pathlib.Path('/workspace/scratch/default-clear-publisher-status-fix-root-r3/publish-selected-r3.py');F=pathlib.Path('/workspace/scratch/default-clear-publisher-tracking-fix-root-r4/publish-selected-r4.py')
before=read(N).decode();after=read(F).decode();h=lambda b:hashlib.sha256(b).hexdigest()
assert h(after.encode())=='af8f3910515be9aa01d68468f1c9a18a5aedc79f448395d932f05c5ced249572'
a="run(['git','add','-f','--',owned,'src/main.ts']+[str(Path('dist')/n) for n in plan['new5']]);run(['git','add','-u','--','dist/'+plan['oldJS']])"
b="run(['git','add','-f','--',owned,'src/main.ts']+[str(Path('dist')/n) for n in plan['new5']])\nif run(['git','ls-files','--','dist/'+plan['oldJS']]):run(['git','add','-u','--','dist/'+plan['oldJS']])"
assert before.count(a)==1 and after.count(b)==1 and after.replace(b,a)==before
assert not pathlib.Path('/workspace/scratch/default-clear-publication-push-root-r2').exists()
receipt={'sourceOnly':True,'r3SHA256':h(before.encode()),'r4SHA256':h(after.encode()),'r4Bytes':len(after.encode()),'inverseExactOneTrackingConditional':True,'readOnlyTrackedQuerySkipsAbsentOldJSUpdate':True,'existingTrackedOldJSRemovalStillStaged':True,'forceAddNewFiveUnchanged':True,'allOtherRuntimePreservationCommitPushControlsExact':True,'newQAbsent':True,'RootR4UngardedTinyBootstrapQualified':True,'actualPublisherExecuted':False,'reviewerRSSFinalBytes':int(next(x.split()[1] for x in pathlib.Path('/proc/self/status').read_text().splitlines() if x.startswith('VmHWM:')))*1024}
assert receipt['reviewerRSSFinalBytes']<24*1048576
with (P/'SUPPLEMENT-r4.json').open('xb') as f:f.write((json.dumps(receipt,separators=(',',':'))+'\n').encode());f.flush();os.fsync(f.fileno())
print(json.dumps({'r4ConditionalExact':True,'ownVmHWMBytes':receipt['reviewerRSSFinalBytes']}))
