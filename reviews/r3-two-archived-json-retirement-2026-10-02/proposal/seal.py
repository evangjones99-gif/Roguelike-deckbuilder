import os,json,hashlib,resource
from pathlib import Path
resource.setrlimit(resource.RLIMIT_DATA,(24*1048576,24*1048576));P=Path(__file__).parent
def read(p):
 f=os.open(p,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW)
 with os.fdopen(f,'rb') as r:return r.read()
methods={}
for n in ['retire-r3-two-archived-json-root-r1.py','publish-r3-two-raw-retirement-root-r1.py','judge-r3-two-raw-retirement-root-r1.py','restore-r3-fresh.py']:
 b=read(P/n);compile(b.decode(),n,'exec');methods[n]=hashlib.sha256(b).hexdigest()
caller=Path('/workspace/scratch/target-clear-default-caller-independent-r1/GATE.json');cb=read(caller);assert hashlib.sha256(cb).hexdigest()=='36ddead7bcd9647706f33c766952732dc3ff7b42455f2c678b125569bde2c31a' and json.loads(cb)['decision'].startswith('ACCEPT')
guards=[]
for name,rc in [('PROPOSAL-GUARD',1),('SHAPE-GUARD',0),('PROPOSAL-GUARD-r2',0),('CONSUMER-GUARD',1),('CONSUMER-GUARD-r2',0),('METHOD-GUARD',1),('METHOD-GUARD-r2',0)]:
 b=read(P/name/'RESULT.json');g=json.loads(b);assert g['exit_code']==rc and g['failure'] is None and g['memory_events_before']==g['memory_events_after'];guards.append([name,rc,hashlib.sha256(b).hexdigest()])
files=[]
for d,dirs,names in os.walk(P):
 dirs[:]=[x for x in dirs if x!='SEAL-GUARD']
 for n in sorted(names):
  p=Path(d)/n;b=read(p);files.append([str(p.relative_to(P)),len(b),hashlib.sha256(b).hexdigest()])
j={'decision':'SEALED_CONDITIONAL_SOURCE_PROPOSAL_AND_UNEXECUTED_ROOT_METHODS','files':files,'methods':methods,'proposalSHA256':hashlib.sha256(read(P/'PROPOSAL.json')).hexdigest(),'consumerSupplementSHA256':hashlib.sha256(read(P/'CONSUMER-SUPPLEMENT.json')).hexdigest(),'latestCallerGate':{'path':str(caller),'sha256':hashlib.sha256(cb).hexdigest()},'guards':guards,'grossAllocationBytes':5005312,'limits':'Distinct full bodies archive exact; finite current builder/caller consumer evidence only. Historical direct readers need fresh restore/adapted new source; all old reviews and failed recipes/locator logs remain. Publisher/newGateSHA, then judge/sameGateSHA, then action/eight path+SHA pins; Root only. Restore/name NEWdest source only. No action, Git, Node, media decode or restore executed. Ordinary64+512/disk64; publisher estimated64+1MiB bounded text overhead, native70/70.5 unchanged. Full selected88/56 pre/post and protected ZIPstat only in future action. Atime-only preflight rebind explicit; no metadata restoration/two-unlink atomicity/retry.','ownMaxRSSBytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,'readerOwnMaxRSSBytes':12247040,'capBytes':128*1024,'closure':'This finite source sealer exits; await separate SEAL-GUARD receipt before subsequent tools.'}
b=(json.dumps(j,separators=(',',':'))+'\n').encode();total=sum(x[1] for x in files);assert total+len(b)+3500<128*1024 and j['ownMaxRSSBytes']<24*1048576
with (P/'FINAL-SEAL.json').open('xb') as out:out.write(b)
print(json.dumps({'proposalSHA256':j['proposalSHA256'],'methods':methods,'sealSHA256':hashlib.sha256(b).hexdigest(),'packetBytesExcludingActiveGuard':total+len(b),'sealerRSS':j['ownMaxRSSBytes']}))
