import os,pathlib,json,hashlib,time,resource,re
resource.setrlimit(resource.RLIMIT_DATA,(24*1048576,24*1048576))
r=pathlib.Path(__file__).parent;cg=pathlib.Path('/sys/fs/cgroup');base=int((cg/'memory.current').read_text());events=(cg/'memory.events').read_text();rows=[]
def sample():
 c=int((cg/'memory.current').read_text());m=int((cg/'memory.max').read_text());v=os.statvfs(r);row={'time_ns':time.time_ns(),'sharedDelta':c-base,'headroom':m-c,'free':v.f_bavail*v.f_frsize,'ownMaxRSS':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024};rows.append(row)
 assert row['sharedDelta']<=64*1048576 and row['headroom']>=512*1048576 and row['free']>=64*1048576 and row['ownMaxRSS']<24*1048576 and events==(cg/'memory.events').read_text();return row
sample();proof=json.loads((r/'PROPOSAL.json').read_text());rg=json.loads((r/'reader-guard-r2/RESULT.json').read_text());rs=json.loads((r/'RESOURCE.json').read_text())
assert rg['exit_code']==0 and rg['failure'] is None and rg['memory_events_before']==rg['memory_events_after']
assert len(proof['pairs'])==3 and all(p['exactFullBodyAndRightsFieldsEqual'] for p in proof['pairs'])
review='/workspace/scratch/audio-host-independent-v08/independent/REVIEW.md';fd=os.open(review,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME)
try:
 before=os.fstat(fd);body=b''
 while True:
  b=os.read(fd,65536)
  if not b:break
  body+=b;assert len(body)<32768
 after=os.fstat(fd);assert before==after
finally:os.close(fd)
known=next(c for c in proof['sourceControls'] if c['path']==review);assert hashlib.sha256(body).hexdigest()==known['sha256'];text=body.decode()
context={'retainedReview':known,'historicalSourceDigest':re.search(r'Exterior runtime identity is `([a-f0-9]{64})`',text).group(1),'declaredSourceManifestSHA':re.search(r'SOURCE-MANIFEST SHA256 `([a-f0-9]{64})`',text).group(1),'declaredBuildManifestSHA':re.search(r'BUILD-MANIFEST `([a-f0-9]{64})`',text).group(1),'sourceInputs':66,'declaredBuiltOutputs':51,'reviewReportedMethod':'Strict TypeScript and Vite with declared VITE_BUILD_ID; exact51-file reproduction into a new output directory, built host4195/dev4193 diagnostics.','qualification':'These aggregate source/output/method identities are preserved from the exact old independent review, not independently rehashed as a whole build in this three-PNG storage proposal. Exactly the proposed three current media bodies were freshly verified.','consumerNeed':'Preserve old diagnostics, source/manifest/review/failure provenance and all logical output paths/bytes. New reproduction must use fresh stages. Their exact pixels remain readable after separately approved sharing; their independent inode/time/writable isolation is the only proposed redundancy, conditionally unnecessary under explicit holds.','holdStatusAfterProposal':'Root reports adding the exact three-leaf immutable/fresh-stage-only hold and a new unexecuted transaction method after the author body-proof phase. PROPOSAL AGENTS pin predates that addition; no current-path hash immutability or independently verified postchange/push claim. Independent BEFORE review must pin the current hold/method.', 'beforeAction':'Root publishes r1POST/rejected-ghost evidence, records independent preference and producer judgment, installs exact fresh-stage-only hold and verifies current push. No action is authorized here.'}
with (r/'HISTORICAL-CONSUMER.json').open('x') as f:json.dump(context,f,indent=2);f.write('\n')
pins=[]
for p in sorted(r.rglob('*')):
 if not p.is_file() or 'seal-guard-r1' in p.parts:continue
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(65536),b''):h.update(b)
 pins.append({'path':str(p),'bytes':p.stat().st_size,'sha256':h.hexdigest()});sample()
s={'decision':proof['decision'],'files':pins,'grossCandidateAllocation':proof['grossOldAllocationBytes'],'candidate':proof['candidateGroup'],'sourceControls':proof['sourceControls'],'readerResource':{'maxOwnRSS':max(x['ownMaxRSS'] for x in rs['rows']),'final':rs['final'],'eventsEqual':rs['eventsBefore']==rs['eventsAfter']},'sealResource':{'rows':rows,'final':sample(),'eventsBefore':events,'eventsAfter':(cg/'memory.events').read_text(),'ownLimitMiB':24,'coordinatedAggregateMiB':64,'reserveMiB':512,'qualification':'Observed shared delta, not exclusive attribution; two other tiny readers may coexist. All FDs closed; no backend/heavy actor.'},'preservedFailure':'reader-guard-r1 rc1 root-owned directory O_NOATIME open failed before any input body read; exact original source/log and outer guard retained. reader-guard-r2 narrow O_PATH parent correction passed.','outerSealGuard':str(r/'seal-guard-r1/RESULT.json'),'outerSealGuardNote':'Completed exact outer RESULT is reported after return; not inside this body.','packetCapBytes':128*1024,'packetBytesBeforeSeal':sum(p['bytes'] for p in pins),'transactionStatus':'NONE; no link/unlink/body/metadata write/storage recovery.'}
with (r/'FINAL-SEAL.json').open('x') as f:json.dump(s,f,indent=2);f.write('\n')
total=sum(p.stat().st_size for p in r.rglob('*') if p.is_file());assert total<128*1024
print(json.dumps({'packetBytes':total,'grossCandidateAllocation':proof['grossOldAllocationBytes'],'grossMinusThisPacketOnly':proof['grossOldAllocationBytes']-total,'futureCostsExcluded':True,'final':sample()}))
