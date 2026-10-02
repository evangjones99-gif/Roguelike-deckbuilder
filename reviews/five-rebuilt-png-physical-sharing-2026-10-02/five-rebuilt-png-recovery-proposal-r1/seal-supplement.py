import os,json,hashlib,resource
resource.setrlimit(resource.RLIMIT_DATA,(24*1048576,24*1048576))
ROOT='/workspace/scratch/five-rebuilt-png-recovery-proposal-r1'
def read(p):
 f=os.open(p,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW)
 with os.fdopen(f,'rb') as r:return r.read()
files=[]
for d,dirs,names in os.walk(ROOT):
 dirs[:]=[x for x in dirs if x!='SUPPLEMENT-SEAL-GUARD']
 for n in sorted(names):
  p=d+'/'+n;b=read(p);files.append({'path':p,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
for n in ['GUARD','MAP-GUARD','SEAL-GUARD','POST-CONTROL-GUARD']:
 g=json.loads(read(ROOT+'/'+n+'/RESULT.json'));assert g['exit_code']==0 and g['failure'] is None and g['memory_events_before']==g['memory_events_after']
total=sum(x['bytes'] for x in files)
j={'decision':'SUPPLEMENT_SEALED_CONDITIONAL_PROPOSAL_ONLY_NO_ACTION','scope':'Freshly pin exact first independent POST controls supplied after initial seal; original proposal and seal remain untouched. Includes all source evidence and guard receipts.','files':files,'packetBytesBeforeSupplementSeal':total,'capBytes':128*1024,'ownMaxRSSBytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,'closure':'Every previous guard has returned; this source process exits and its guard completion remains separately pinned at readback.'}
b=(json.dumps(j,indent=2)+'\n').encode();assert total+len(b)+5000<128*1024
with open(ROOT+'/SUPPLEMENT-SEAL.json','xb') as o:o.write(b)
print(json.dumps({'proposalSHA256':hashlib.sha256(read(ROOT+'/PROPOSAL.json')).hexdigest(),'currentMapProofSHA256':hashlib.sha256(read(ROOT+'/CURRENT-MAP-PROOF.json')).hexdigest(),'initialSealSHA256':hashlib.sha256(read(ROOT+'/FINAL-SEAL.json')).hexdigest(),'firstPostControlSHA256':hashlib.sha256(read(ROOT+'/FIRST-POST-CONTROL.json')).hexdigest(),'supplementSealSHA256':hashlib.sha256(b).hexdigest(),'packetBytesExcludingActiveGuard':total+len(b),'ownMaxRSSBytes':j['ownMaxRSSBytes']}))
