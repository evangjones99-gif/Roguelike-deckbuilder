from pathlib import Path
import subprocess,json,time,hashlib,os
R=Path('/workspace/Roguelike-deckbuilder'); S=Path('/workspace/scratch'); start=time.monotonic()
def run(args,t=15):
 if time.monotonic()-start>80:raise RuntimeError('Finite80s phase exceeded')
 return subprocess.check_output(args,cwd=R,text=True,timeout=t).rstrip(chr(10))
assert not run(['git','status','--porcelain'])
tracked=set(run(['git','ls-files','-z']).split(chr(0)));missing=[]
for n,count in [('opening-native-aftermath-and-starter-art-2026-10-02',87),('reviewed-opening-capsule-duplicate-retirement-2026-10-02',77)]:
 p=R/'reviews'/n; files=[x for x in p.rglob('*') if x.is_file()];assert len(files)==count
 missing.extend(x for x in files if str(x.relative_to(R)) not in tracked)
assert len(missing)==25 and all(x.name=='EXECUTION.log' and not x.is_symlink() for x in missing)
rows=[{'path':str(x.relative_to(R)),'bytes':x.stat().st_size,'sha256':hashlib.sha256(x.read_bytes()).hexdigest()} for x in missing]
run(['git','add','-f','--']+[x['path'] for x in rows])
run(['git','commit','-m','Preserve supporting execution logs omitted by ignore rule'])
head=run(['git','rev-parse','HEAD']);run(['git','push','origin','codex/lanternbound-production'],45)
remote=run(['git','ls-remote','--heads','origin','codex/lanternbound-production']).split()[0];verified=time.time_ns();assert remote==head and not run(['git','status','--porcelain'])
tracked=set(run(['git','ls-files','-z']).split(chr(0)))
assert all(str(x.relative_to(R)) in tracked for n in ['opening-native-aftermath-and-starter-art-2026-10-02','reviewed-opening-capsule-duplicate-retirement-2026-10-02'] for x in (R/'reviews'/n).rglob('*') if x.is_file())
out=S/'native-checkpoint-ignored-logs-current-push-receipt-root-r1.json'
with out.open('x') as f:json.dump({'confirmedPush':True,'clean':True,'localHEAD':head,'remoteHEAD':remote,'remoteVerifiedAtNs':verified,'exactNewForcedRows':rows,'native87AndRetirement77AllTracked':True,'priorActionHEAD':'8a19a23d7dbfc65ff9b4475d72cee3d661687b44','qualification':'25 execution logs totaling14460B were ignored during prior confirmed push; caught after two duplicate encodings retired. Existing compressed evidence canonical bodies, mapping, producer, method gates and all uniquely required data were already committed. No lost bytes or other cleanup; complete supporting log publication repaired in this later push, not falsely asserted as pre-deletion complete publication.'},f,indent=2);f.write(chr(10));f.flush();os.fsync(f.fileno())
print(json.dumps({'confirmedHEAD':head,'receipt':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'forcedLogs':len(rows),'elapsed':time.monotonic()-start}))
