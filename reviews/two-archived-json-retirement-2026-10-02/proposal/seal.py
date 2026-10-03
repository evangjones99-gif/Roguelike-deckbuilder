import pathlib,os,json,hashlib,time,resource
resource.setrlimit(resource.RLIMIT_DATA,(24*1048576,24*1048576))
r=pathlib.Path(__file__).parent;cg=pathlib.Path('/sys/fs/cgroup');base=int((cg/'memory.current').read_text());events=(cg/'memory.events').read_text();rows=[]
def sample():
 c=int((cg/'memory.current').read_text());m=int((cg/'memory.max').read_text());v=os.statvfs(r);x={'time_ns':time.time_ns(),'sharedDelta':c-base,'headroom':m-c,'free':v.f_bavail*v.f_frsize,'ownMaxRSS':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024};rows.append(x)
 assert x['sharedDelta']<=64*1048576 and x['headroom']>=512*1048576 and x['free']>=64*1048576 and x['ownMaxRSS']<=24*1048576 and events==(cg/'memory.events').read_text();return x
sample();pins=[]
for p in sorted(r.rglob('*')):
 if not p.is_file() or 'seal-guard-r1' in p.parts:continue
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(65536),b''):h.update(b)
 pins.append({'path':str(p),'bytes':p.stat().st_size,'sha256':h.hexdigest()});sample()
p=json.loads((r/'PROPOSAL.json').read_text());g=json.loads((r/'reader-guard-r2/RESULT.json').read_text());rs=json.loads((r/'RESOURCE.json').read_text())
assert g['exit_code']==0 and g['failure'] is None and g['memory_events_before']==g['memory_events_after'] and len(p['rawFiles'])==len(p['exactLogicalMapping'])==len(p['freshBlobRoundtrip'])==2
s={'decision':p['decision'],'files':pins,'grossRawAllocation':p['grossRawAllocationBytes'],'readerMaxRSS':max(x['ownMaxRSS'] for x in rs['rows']),'sealResource':{'rows':rows,'final':sample(),'eventsBefore':events,'eventsAfter':(cg/'memory.events').read_text(),'scope':'Observed shared64MiB work+512reserve; own24MiB/RLIMIT_DATA. All handles closed.'},'retainedFailure':'reader-guard-r1 rc1 unverified short-name consumer locator; original source/log kept; finite corrected reader-guard-r2 rc0. No runtime failure/retry.','restoreHelper':'Source only; never executed. Fresh body reproduction does not preserve original raw inode/time/metadata.','outerGuard':str(r/'seal-guard-r1/RESULT.json'),'outerGuardNote':'Produced after this seal; completed exact hash reported separately.','packetCap':65536,'bodyBytesBeforeSeal':sum(x['bytes'] for x in pins),'storageAction':'NONE'}
with (r/'FINAL-SEAL.json').open('x') as f:json.dump(s,f,separators=(',',':'));f.write('\n')
total=sum(p.stat().st_size for p in r.rglob('*') if p.is_file());assert total<=65536
print(json.dumps({'packetBytes':total,'final':sample(),'allFDsClosed':True}))
