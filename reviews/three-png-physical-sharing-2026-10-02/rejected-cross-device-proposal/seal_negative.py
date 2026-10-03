import pathlib,hashlib,json,os,resource,time
r=pathlib.Path(__file__).parent;cg=pathlib.Path('/sys/fs/cgroup');base=int((cg/'memory.current').read_text());events=(cg/'memory.events').read_text()
def sample():
 c=int((cg/'memory.current').read_text());m=int((cg/'memory.max').read_text());v=os.statvfs(r);row={'time_ns':time.time_ns(),'sharedDelta':c-base,'headroom':m-c,'free':v.f_bavail*v.f_frsize,'ownMaxRSS':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024}
 assert row['sharedDelta']<=64*1048576 and row['headroom']>=512*1048576 and row['free']>=64*1048576 and row['ownMaxRSS']<24*1048576 and events==(cg/'memory.events').read_text()
 return row
initial=sample();pins=[]
for p in sorted(r.rglob('*')):
 if not p.is_file() or 'seal-guard-r1' in p.parts:continue
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(65536),b''):h.update(b)
 pins.append({'path':str(p),'bytes':p.stat().st_size,'sha256':h.hexdigest()});sample()
g=json.loads((r/'reader-guard-r1/RESULT.json').read_text());assert g['exit_code']==0 and g['failure'] is None and g['memory_events_before']==g['memory_events_after']
e=json.loads((r/'EVIDENCE.json').read_text());assert e['workspaceRecoveryBytes']==0 and len(e['exactCandidatePairs'])==3
s={'decision':e['decision'],'files':pins,'sourceControls':e['controls'],'resource':{'initial':initial,'final':sample(),'eventsBefore':events,'eventsAfter':(cg/'memory.events').read_text(),'qualifiedSharedWorkMiB':64,'ownRSSLimitMiB':24,'allInputFDsClosed':True},'outerGuard':str(r/'seal-guard-r1/RESULT.json'),'outerGuardNote':'Exact completed outer guard is reported after its return; not included in this body.','scope':'Negative proposal only; no action/independent approval/push verification.','packetCap':128*1024}
with (r/'FINAL-SEAL.json').open('x') as f:json.dump(s,f,indent=2);f.write('\n')
total=sum(p.stat().st_size for p in r.rglob('*') if p.is_file());assert total<=128*1024
print(json.dumps({'packetBytes':total,'final':sample()}))
