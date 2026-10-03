import os,sys,time,json,pathlib,subprocess,signal,gzip,hashlib
entry_start=time.monotonic()
from runtime_guard_cue import qualify,regular
caller_root='/workspace/scratch/opening-cue-late-binding-caller-source-r4'
expected_bytes=regular(caller_root+'/EXPECTED.json');expected=json.loads(expected_bytes)
method_grant=qualify(expected,expected_bytes,caller_root) # before arguments, mkdir or Popen
stage,freeze,packet,port=sys.argv[1:]
assert (stage,freeze,packet,int(port))==(expected['stage'],expected['freezePath'],expected['actualPacket'],expected['port'])
p=pathlib.Path(packet);p.mkdir(exist_ok=False)
work=896*1048576;reserve=512*1048576;cgroup=pathlib.Path('/sys/fs/cgroup')
def sample():
 c=int((cgroup/'memory.current').read_text());m=int((cgroup/'memory.max').read_text());return {'time_ns':time.time_ns(),'current':c,'maximum':m,'headroom':m-c,'free':os.statvfs(stage).f_bavail*os.statvfs(stage).f_frsize}
def read_identity(pid):
 d=pathlib.Path('/proc',str(pid));raw=(d/'stat').read_text();f=raw[raw.rindex(')')+2:].split()
 return {'starttime':f[19],'state':f[0],'ppid':int(f[1]),'pgrp':int(f[2]),'uid':d.stat().st_uid}

def admit_snapshot(allp,root_pid,root_start,pairs,current_child):
 # Never seed membership from a numeric PGID or a recycled original-root PID.
 result={pid:v for pid,v in allp.items() if
  ((pid==root_pid and v['starttime']==root_start) or
   (pid!=root_pid and (pid,v['starttime']) in pairs))}
 changed=True
 while changed:
  changed=False
  for pid,v in allp.items():
   if pid in result or pid==root_pid:continue
   parent=str(v['ppid']);pv=result.get(parent)
   if pv is not None and current_child(pid,v,parent,pv):result[pid]=v;changed=True
 return result

def current_child(pid,v,parent,pv):
 try:
  first=read_identity(pid);owner=read_identity(parent);last=read_identity(pid)
  return first['starttime']==v['starttime']==last['starttime'] and first['ppid']==int(parent)==last['ppid'] and owner['starttime']==pv['starttime']
 except (OSError,ValueError,IndexError):return False

def remember(now):
 # Compound pairs preserve first observations when a non-root PID later recurs.
 for pid,v in now.items():
  if pid==str(proc.pid) and v['starttime']!=root_start:raise RuntimeError('Original root identity changed')
  key=(pid,v['starttime']);owned_pairs.setdefault(key,{'pid':pid,**v});owned[pid]=v

def identities():
 if root_start is None:raise RuntimeError('Original root starttime was not captured')
 allp={}
 for d in pathlib.Path('/proc').iterdir():
  if not d.name.isdigit():continue
  try:allp[d.name]=read_identity(d.name)
  except (OSError,ValueError,IndexError):pass
 now=admit_snapshot(allp,str(proc.pid),root_start,owned_pairs,current_child)
 remember(now);return now

def stop_owned(sig):
 now=identities();receipt=[]
 for pid,v in sorted(now.items(),key=lambda x:int(x[0]),reverse=True):
  if v['state']=='Z':continue
  try:
   raw=pathlib.Path('/proc',pid,'stat').read_text();f=raw[raw.rindex(')')+2:].split()
   if f[19]!=v['starttime'] or int(f[2])!=v['pgrp']:continue
   if pathlib.Path('/proc',pid).stat().st_uid!=os.getuid():continue
   fd=os.pidfd_open(int(pid))
   try:
    check=pathlib.Path('/proc',pid,'stat').read_text();check=check[check.rindex(')')+2:].split()
    if check[19]!=v['starttime']:continue
    signal.pidfd_send_signal(fd,sig)
   finally:os.close(fd)
   receipt.append({'pid':pid,'starttime':v['starttime'],'signal':int(sig)})
  except (OSError,ValueError,IndexError):pass
 with (p/'STOP-IDENTITIES.jsonl').open('a') as log:log.write(json.dumps({'time_ns':time.time_ns(),'signals':receipt})+'\n')
initial=sample();before=(cgroup/'memory.events').read_text();admitted=initial['headroom']>=work+reserve and initial['free']>=71*1048576
(p/'ADMISSION.json').write_text(json.dumps({'admitted':admitted,'initial':initial,'work':work,'reserve':reserve,'stage':stage,'freeze':freeze,'whole_wall_ceiling_seconds':90},indent=2)+'\n')
if not admitted:print('REFUSED',json.dumps(initial));sys.exit(75)
rows=[];owned={};owned_pairs={};root_start=None;failure=None;cleanup_errors=[];proc=None;rootfd=None;rc=None;remaining={};start=entry_start;log=None

def error(where,e):
 cleanup_errors.append({'where':where,'error':repr(e)})

def observe():
 return identities()

def safe_poll():
 try:return proc.poll()
 except BaseException as e:error('child poll',e);return None

def root_signal(sig):
 # A pidfd holds our exact launched child. Before wait/reap, Popen's own
 # unreaped child is also non-reusable if acquiring a pidfd itself failed.
 if proc is None:return
 try:
  if rootfd is not None:signal.pidfd_send_signal(rootfd,sig)
  else:proc.send_signal(sig)
 except ProcessLookupError:pass

try:
 log=(p/'EXECUTION.log').open('xb')
 proc=subprocess.Popen([expected['dependencies']['nodePath'],'/workspace/scratch/opening-cue-late-binding-caller-source-r4/driver-cue.mjs',stage,freeze,packet,port],cwd=stage,env={**os.environ,'NODE_OPTIONS':'--max-old-space-size=256'},stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 # Capture once while our child is unreaped, BEFORE any poll/wait.
 root_initial=read_identity(proc.pid);root_start=root_initial['starttime']
 if root_initial['uid']!=os.getuid():raise RuntimeError('Launched root UID mismatch')
 remember({str(proc.pid):root_initial})
 rootfd=os.pidfd_open(proc.pid)
 root_after_fd=read_identity(proc.pid)
 if root_after_fd['starttime']!=root_start or root_after_fd['uid']!=os.getuid():raise RuntimeError('Root identity changed after pidfd acquisition')
 launch=observe()
 (p/'OWNED-LAUNCH.json').write_text(json.dumps({'pid':proc.pid,'pgrp':proc.pid,'original_root_starttime':root_start,'identities':launch,'utc_ns':time.time_ns()})+'\n')
 while safe_poll() is None:
  if cleanup_errors:failure={'kind':'child poll failed','errors':cleanup_errors.copy()};break
  row=sample();row['delta']=row['current']-initial['current'];row['elapsed']=time.monotonic()-start;rows.append(row);observe()
  if row['headroom']<reserve or row['delta']>work or row['free']<1048576 or row['elapsed']>=80:
   failure={'kind':'resource or 80s cancellation','sample':row};break
  time.sleep(.1)
except BaseException as e:
 failure={'kind':'post-admission lifecycle exception','error':repr(e)}
finally:
 # This path also runs for launch-receipt, sampling, identity, signal-log,
 # wait or execution-log errors. It never signals historical/global zombies.
 if proc is not None:
  try:
   now=observe();live={k:v for k,v in now.items() if v['state']!='Z'}
  except BaseException as e:
   error('initial cleanup observation',e);live=None
  if safe_poll() is None or live or live is None:
   if failure is None:failure={'kind':'live descendants or driver still active at cleanup'}
   try:stop_owned(signal.SIGTERM)
   except BaseException as e:error('scoped TERM',e)
   try:root_signal(signal.SIGTERM)
   except BaseException as e:error('exact launched-child TERM',e)
   term_end=min(time.monotonic()+5,start+85)
   while time.monotonic()<term_end:
    try:
     now=observe();live={k:v for k,v in now.items() if v['state']!='Z'}
     if safe_poll() is not None and not live:break
    except BaseException as e:
     error('TERM observation',e);break
    time.sleep(.1)
   try:stop_owned(signal.SIGKILL)
   except BaseException as e:error('scoped KILL',e)
   try:root_signal(signal.SIGKILL)
   except BaseException as e:error('exact launched-child KILL',e)
  try:
   if safe_poll() is None:
    seconds=min(2,max(0,start+89-time.monotonic()))
    if seconds:rc=proc.wait(timeout=seconds)
    else:rc=safe_poll();error('wait','no deadline margin; child status unresolved')
   else:rc=proc.wait(timeout=0)
  except BaseException as e:
   error('bounded child wait',e)
   try:root_signal(signal.SIGKILL)
   except BaseException as kill_error:error('fallback launched-child KILL',kill_error)
   rc=safe_poll()
  try:remaining=observe()
  except BaseException as e:error('final descendant observation',e);remaining=None
 if rootfd is not None:
  try:os.close(rootfd)
  except BaseException as e:error('pidfd close',e)
 if log is not None:
  try:log.flush();os.fsync(log.fileno())
  except BaseException as e:error('execution log fsync',e)
  try:log.close()
  except BaseException as e:error('execution log close',e)

# Final proof readback is inside the same90s/resource/event window, not after closure.
def proof_sample(label):
 row=sample();row['delta']=row['current']-initial['current'];row['elapsed']=time.monotonic()-start;row['phase']=label;rows.append(row)
 if row['maximum']!=initial['maximum'] or row['headroom']<reserve or row['delta']>work or row['free']<1048576 or row['elapsed']>=90:raise RuntimeError('Post-driver resource/time bound '+label)
 if (cgroup/'memory.events').read_text()!=before:raise RuntimeError('Post-driver memory.events changed '+label)
 return row
compression=[];capfailure=None
try:
 proof_sample('before-gzip-readback');index=json.loads((p/'EVIDENCE-FORMAT.json').read_text());assert index['format']=='lossless-original-compact-json-gzip-v1';assert set(index['files'])=={'VISUAL-PROGRESS.json','VISUAL-RESULT.json'}
 for leaf,row in index['files'].items():
  file=p/row['storedLeaf'];assert row['storedLeaf']==leaf+'.gz' and file.is_file() and not file.is_symlink();stored=file.stat().st_size;h=hashlib.sha256()
  with file.open('rb') as body:
   while chunk:=body.read(65536):h.update(chunk);proof_sample('stored-gzip-hash')
  assert h.hexdigest()==row['storedSHA256'] and stored==row['storedBytes'];decoded=hashlib.sha256();decodedBytes=0
  with gzip.open(file,'rb') as body:
   while chunk:=body.read(65536):decoded.update(chunk);decodedBytes+=len(chunk);proof_sample('full-original-gzip-readback')
  assert decodedBytes==row['originalBytes'] and decoded.hexdigest()==row['originalSHA256'];compression.append({**row,'postLifecycleFullReadbackVerified':True})
except BaseException as e:capfailure=repr(e)
def sync_json(name,value):
 with (p/name).open('w') as f:json.dump(value,f,separators=(',',':'));f.write('\n');f.flush();os.fsync(f.fileno())
def seal_caps():
 files=[f for f in p.iterdir() if f.is_file() and f.name!='FINAL-PACKET-CAPS.json'];jpg=sum(f.stat().st_size for f in files if f.suffix=='.jpg');stored=sum(f.stat().st_size for f in files if f.suffix!='.jpg');logical=stored+sum(x['originalBytes']-x['storedBytes'] for x in compression)
 caps={'scope':'full original logical bodies retained;5MiB cap is physical storage; logical bytes separate','jpegBytes':jpg,'storedProofBytesTotal':stored,'logicalProofBytesTotal':logical,'jpegCapBytes':2*1048576,'storedProofCapBytes':5*1048576,'proofCapBasis':'physical retained files only','compression':compression,'receiptIncludesItself':True}
 for _ in range(6):
  caps['pass']=jpg<=2*1048576 and caps['storedProofBytesTotal']<=5*1048576 and capfailure is None;body=(json.dumps(caps,separators=(',',':'))+'\n').encode();caps['storedProofBytesTotal']=stored+len(body);caps['logicalProofBytesTotal']=logical+len(body)
 body=(json.dumps(caps,separators=(',',':'))+'\n').encode();assert caps['storedProofBytesTotal']==stored+len(body)
 with (p/'FINAL-PACKET-CAPS.json').open('wb') as f:f.write(body);f.flush();os.fsync(f.fileno())
 return caps
live_remaining=None if remaining is None else {k:v for k,v in remaining.items() if v['state']!='Z'};zombies=None if remaining is None else {k:v for k,v in remaining.items() if v['state']=='Z'}
result={'exit_code':rc,'failure':failure,'cleanup_errors':cleanup_errors,'initial':initial,'samples':rows,'memory_events_before':before,'owned_observed':owned,'owned_observed_pairs':list(owned_pairs.values()),'original_root_starttime':root_start,'post_wait_descendants':remaining,'tracked_zombies':zombies,'live_remaining':live_remaining,'packet_cap_observation_failure':capfailure,'scope':'same896+512 aggregate phase includes gzip/readback/caps. Observed PID/start ownership only; no universal escape claim. Terminal stdout/exit check is after all packet writes; receipt tail itself qualified.'}
normal=False;caps=None
try:
 # First seal creates Result/caps; second final resource marker is after their fsync.
 for iteration in range(2):
  final=proof_sample('after-readback-before-seal' if iteration==0 else 'after-first-result-and-caps-fsync');after=(cgroup/'memory.events').read_text();whole=time.monotonic()-start
  checks={'sampled_resources':all(x['maximum']==initial['maximum'] and x['headroom']>=reserve and x['delta']<=work and x['free']>=1048576 for x in rows),'final_resources':final['headroom']>=reserve and final['delta']<=work,'memory_events_unchanged':after==before,'whole_within90':whole<90,'no_observed_tracked_live_descendants':live_remaining=={},'driver_rc0':rc==0,'no_lifecycle_or_cleanup_failure':failure is None and not cleanup_errors,'full_gzip_readback':capfailure is None and len(compression)==2}
  normal=all(checks.values());result.update(final=final,memory_events_after=after,whole_seconds=whole,checks=checks,normal_wait=normal,resourcesAndTimeAfterCompression=True,capsSampledAfterFsync=iteration==1);sync_json('RESULT.json',result);caps=seal_caps();normal=normal and caps['pass']
  directory=os.open(p,os.O_RDONLY)
  try:os.fsync(directory)
  finally:os.close(directory)
 closed=proof_sample('after-all-data-and-cap-seals');sync_json('POST-COMPRESSION-CLOSURE.json',{'phase':'after complete gzip readback, two Result/cap fsyncs and directory fsync','sample':closed,'memory_events_after':(cgroup/'memory.events').read_text(),'normalSoFar':normal,'storedLogicalDomainsSeparate':True,'terminalCheckStillRequired':True,'qualification':'This small receipt and its last cap-accounting rewrite precede terminal stdout/exit check; no further gzip or data writes.'});caps=seal_caps();normal=normal and caps['pass']
 terminal=proof_sample('terminal-after-every-owned-packet-write');normal=normal and terminal['elapsed']<90
except BaseException as e:
 normal=False;result['final_phase_failure']=repr(e);terminal={'elapsed':time.monotonic()-start,'qualification':'terminal resource observation failed; not accepted'}
print(json.dumps({'normal_wait_with_packet_caps':normal,'terminalAfterAllPacketWrites':terminal,'memory_events_after':(cgroup/'memory.events').read_text(),'driver_rc':rc,'failure':failure,'cleanup_errors':cleanup_errors,'packet_cap_observation_failure':capfailure,'final_phase_failure':result.get('final_phase_failure'),'packetCaps':caps,'qualification':'terminal stdout/exit follows complete compressed data/caps. Tiny stdout/exit cost not independently metered.'}));sys.exit(0 if normal else 76)
