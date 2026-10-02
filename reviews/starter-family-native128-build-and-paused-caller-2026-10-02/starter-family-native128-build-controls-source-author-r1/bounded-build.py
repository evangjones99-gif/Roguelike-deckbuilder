import os,sys,time,json,pathlib,subprocess,signal,hashlib
P=pathlib.Path(__file__).parent;S=pathlib.Path('/workspace/scratch/starter-family-native128-stage-r1');E=pathlib.Path(sys.argv[1]);E.mkdir(exist_ok=False);D=E/'build-outer-r1';D.mkdir(exist_ok=False)
G=pathlib.Path('/workspace/scratch/guard-node-phase-r1.py');work=384*1048576;reserve=512*1048576;C=pathlib.Path('/sys/fs/cgroup');start=time.monotonic();owned={};observed_pairs={};rows=[];proc=None;rootfd=None;launched_starttime=None;rc=None;failure=None;errors=[];remaining={}
def sample():
 cur=int((C/'memory.current').read_text());mx=int((C/'memory.max').read_text());return {'elapsed':time.monotonic()-start,'current':cur,'maximum':mx,'headroom':mx-cur,'free':os.statvfs(S).f_bavail*os.statvfs(S).f_frsize}
def identities():
 allp={}
 for d in pathlib.Path('/proc').iterdir():
  if not d.name.isdigit():continue
  try:
   s=(d/'stat').read_text();f=s[s.rindex(')')+2:].split();allp[d.name]={'starttime':f[19],'state':f[0],'ppid':int(f[1]),'pgrp':int(f[2])}
  except (OSError,ValueError,IndexError):pass
 now={pid:v for pid,v in allp.items() if (int(pid)==proc.pid and v['starttime']==launched_starttime) or (pid in owned and v['starttime']==owned[pid]['starttime'])}
 changed=True
 while changed:
  changed=False
  for pid,v in allp.items():
   if pid not in now and str(v['ppid']) in now:now[pid]=v;changed=True
 owned.update(now)
 for pid,v in now.items():observed_pairs[pid+':'+v['starttime']]={'pid':pid,**v}
 return now

def signal_owned(sig):
 receipts=[]
 for pid,v in sorted(identities().items(),key=lambda x:int(x[0]),reverse=True):
  if v['state']=='Z':continue
  try:
   d=pathlib.Path('/proc')/pid;raw=(d/'stat').read_text();f=raw[raw.rindex(')')+2:].split()
   if f[19]!=v['starttime'] or d.stat().st_uid!=os.getuid():continue
   fd=os.pidfd_open(int(pid))
   try:
    check=(d/'stat').read_text();check=check[check.rindex(')')+2:].split()
    if check[19]!=v['starttime']:continue
    signal.pidfd_send_signal(fd,sig)
   finally:os.close(fd)
   receipts.append({'pid':pid,'starttime':v['starttime'],'signal':int(sig)})
  except ProcessLookupError:pass
 with (D/'STOP-IDENTITIES.jsonl').open('a') as log:log.write(json.dumps(receipts)+'\n')
initial=sample();before=(C/'memory.events').read_text();guardSHA=hashlib.sha256(G.read_bytes()).hexdigest();admitted=initial['headroom']>=work+reserve and initial['free']>=64*1048576
(D/'ADMISSION.json').write_text(json.dumps({'admitted':admitted,'initial':initial,'work':work,'reserve':reserve,'wholeLimit':60,'stopAt':55,'genericGuardPath':str(G),'genericGuardSHA256':guardSHA},indent=2)+'\n')
if not admitted:print(json.dumps({'admitted':False,'initial':initial}));sys.exit(75)
try:
 with (D/'EXECUTION.log').open('xb') as log:
  proc=subprocess.Popen([sys.executable,str(G),str(S),str(E/'build-inner-r1'),'384','node',str(P/'strict-build-runner.mjs')],cwd=S,env={**os.environ,'NODE_OPTIONS':'--max-old-space-size=256'},stdout=log,stderr=subprocess.STDOUT,start_new_session=True);rootfd=os.pidfd_open(proc.pid)
  # Popen's child is unreaped: this PID cannot be reused before its first poll.
  launched_raw=pathlib.Path('/proc',str(proc.pid),'stat').read_text();launched_fields=launched_raw[launched_raw.rindex(')')+2:].split();launched_starttime=launched_fields[19]
  (D/'OWNED-LAUNCH.json').write_text(json.dumps({'pid':proc.pid,'originalStarttime':launched_starttime,'startIdentities':identities()})+'\n')
  while proc.poll() is None:
   r=sample();r['delta']=r['current']-initial['current'];rows.append(r);identities()
   if r['headroom']<reserve or r['delta']>work or r['free']<1048576 or r['elapsed']>=55 or (C/'memory.events').read_text()!=before:failure={'kind':'outer resource/event/55s stop','sample':r};break
   time.sleep(.1)
  if failure is None:rc=proc.wait(timeout=0)
  log.flush();os.fsync(log.fileno())
except BaseException as e:failure={'kind':'outer exception','error':repr(e)}
finally:
 if proc is not None:
  try:
   now=identities()
   if proc.poll() is None or any(v['state']!='Z' for v in now.values()):
    if failure is None:failure={'kind':'live owned process at cleanup'}
    signal_owned(signal.SIGTERM);deadline=min(time.monotonic()+3,start+58)
    while time.monotonic()<deadline and any(v['state']!='Z' for v in identities().values()):time.sleep(.1)
    if any(v['state']!='Z' for v in identities().values()):signal_owned(signal.SIGKILL)
   rc=proc.wait(timeout=max(.01,min(1,start+59-time.monotonic())));remaining=identities()
  except BaseException as e:
   errors.append(repr(e))
   # The exact launched-root pidfd remains authoritative when descendant
   # observation fails. This fallback is a failure, never normal closure proof.
   try:
    if rootfd is not None:signal.pidfd_send_signal(rootfd,signal.SIGKILL)
    if proc.poll() is None:proc.wait(timeout=max(.01,min(1,start+59-time.monotonic())))
   except BaseException as cleanup_error:errors.append(repr(cleanup_error))
 if rootfd is not None:os.close(rootfd)
final=sample();after=(C/'memory.events').read_text();generic=json.loads((E/'build-inner-r1/RESULT.json').read_text()) if (E/'build-inner-r1/RESULT.json').exists() else None
checks={'outerAdmission':admitted,'allOuterRows':bool(rows) and all(r['maximum']==initial['maximum'] and r['headroom']>=reserve and r['delta']<=work and r['free']>=1048576 for r in rows),'outerFinal':final['maximum']==initial['maximum'] and final['headroom']>=reserve and final['current']-initial['current']<=work and final['free']>=1048576,'eventsUnchanged':before==after,'wholeWithin60':final['elapsed']<=60,'noOwnedLive':not any(v['state']!='Z' for v in remaining.values()),'rc0':rc==0,'noFailure':failure is None and not errors,'genericResult':generic is not None and generic['exit_code']==0 and generic['failure'] is None,'genericEveryRow':generic is not None and all(r['maximum']==generic['initial']['maximum'] and r['headroom']>=reserve and r['delta']<=work and r['free']>=1048576 for r in generic['samples']),'genericFinal':generic is not None and generic['final']['maximum']==generic['initial']['maximum'] and generic['final']['headroom']>=reserve and generic['final']['current']-generic['initial']['current']<=work and generic['final']['free']>=1048576,'genericEvents':generic is not None and generic['memory_events_before']==generic['memory_events_after'],'genericSourceUnchanged':hashlib.sha256(G.read_bytes()).hexdigest()==guardSHA}
result={'normal':all(checks.values()),'checks':checks,'initial':initial,'final':final,'rows':rows,'maxDelta':max([r['delta'] for r in rows]+[final['current']-initial['current']]),'minHeadroom':min([r['headroom'] for r in rows]+[final['headroom']]),'eventsBefore':before,'eventsAfter':after,'ownedObserved':owned,'allObservedPIDStartPairs':observed_pairs,'originalRootStarttime':launched_starttime,'remaining':remaining,'trackedZombies':{pid:v for pid,v in remaining.items() if v['state']=='Z'},'exitCode':rc,'failure':failure,'errors':errors,'scope':'One generic384MiB+512 strict build with finite outer deadline/owned PID-starttime closure; point samples not continuous peaks, metadata/sharing qualified, no browser'}
(D/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'normal':result['normal'],'checks':checks,'wholeSeconds':final['elapsed'],'samples':len(rows),'maxDelta':result['maxDelta'],'minHeadroom':result['minHeadroom'],'failure':failure}));sys.exit(0 if result['normal'] else 76)
