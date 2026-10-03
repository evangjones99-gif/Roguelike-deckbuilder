from pathlib import Path
import hashlib, json, os, subprocess, time
S = Path('/workspace/scratch')
A = S/'wording-grounded-trials-checkpoint-source-author-r1'
G = Path(os.environ['HOLLOWPACT_ARCHIVE_SOURCE_GATE'])
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(65536): h.update(b)
 return h.hexdigest()
assert sha(G)==os.environ['HOLLOWPACT_ARCHIVE_SOURCE_GATE_SHA256']
gate=json.loads(G.read_text())
assert gate.get('sourceOnly') is True or 'SOURCE' in gate.get('decision','')
assert 'ACCEPT' in gate.get('decision','')
assert sha(A/'PLAN.json')=='0998d948c57e2fb3d1e01f34e61028d5c80db299df308d3b1e83ab902d4281b7'
assert sha(A/'preserve-checkpoint.py')=='5ee7a0a37946e3afcdf1d355cdfbc929ccf37b39edb1b4654e61e14250fb3f1a'
c=Path('/sys/fs/cgroup')
head=int((c/'memory.max').read_text())-int((c/'memory.current').read_text())
free=os.statvfs('/workspace').f_bavail*os.statvfs('/workspace').f_frsize
assert head >= 640*1048576 and free >=64*1048576
out=S/'wording-grounded-trials-checkpoint-output-root-r1'
assert not out.exists()
grant={'utcNs':time.time_ns(),'sourceGatePath':str(G),'sourceGateSHA256':sha(G),
 'planSHA256':sha(A/'PLAN.json'),'helperSHA256':sha(A/'preserve-checkpoint.py'),
 'freshHeadroomBytes':head,'freshFreeDiskBytes':free,'workMiB':128,'reserveMiB':512,
 'outputLogicalAndAllocatedCapBytes':16*1048576,'ownRSSCapBytes':24*1048576,
 'helperFiniteSeconds':60,'outputPath':str(out),
 'scope':'Preservation only. No publication, source selection, cleanup, version or art/fun acceptance.',
 'bootstrapWriteAndAdmissionReadUnmetered':True}
with (S/'wording-grounded-trials-checkpoint-archive-grant-root-r1.json').open('x') as f:
 json.dump(grant,f,indent=2);f.write(chr(10));f.flush();os.fsync(f.fileno())
v=subprocess.run(['python',str(A/'preserve-checkpoint.py'),str(A/'PLAN.json'),grant['planSHA256'],str(out)],timeout=62)
assert v.returncode==0, 'Archive attempt failed; retain entire output and guard'
