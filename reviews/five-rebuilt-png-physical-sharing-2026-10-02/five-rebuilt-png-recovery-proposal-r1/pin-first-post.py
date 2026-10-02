import os,json,hashlib,resource
resource.setrlimit(resource.RLIMIT_DATA,(24*1048576,24*1048576))
ROOT='/workspace/scratch/five-rebuilt-png-recovery-proposal-r1'
def sd(s):return {'st_'+k:getattr(s,'st_'+k) for k in ['dev','ino','mode','uid','gid','nlink','size','blocks','atime_ns','mtime_ns','ctime_ns']}
pins=[]
for name,expected in [('GATE.json','3fc19d79046140b365614cda936e4e0875a2c41a97952d4e6ccc93c2c9a532dc'),('FINAL-SEAL.json','35f4966518f4787a4ee34e7dbaa3a3d09c5e2b388df0904f1faaee3ae8cbaa92')]:
 p='/workspace/scratch/five-png-sharing-post-independent-r2/'+name
 before=sd(os.lstat(p));f=os.open(p,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW);assert before==sd(os.fstat(f));attrs={n:os.getxattr(f,n).hex() for n in os.listxattr(f)};b=b''
 while True:
  c=os.read(f,65536)
  if not c:break
  b+=c;assert len(b)<65536
 assert before==sd(os.fstat(f));os.close(f);assert before==sd(os.lstat(p));sha=hashlib.sha256(b).hexdigest();assert sha==expected
 body=json.loads(b)
 if name=='GATE.json':assert 'ACCEPT' in json.dumps(body).upper()
 pins.append({'path':p,'sha256':sha,'bytes':len(b),'lstat':before,'fstat':before,'xattrs':attrs,'duringReadMetadataExact':True})
j={'firstPOSTControls':pins,'scope':'Exact first-sharing independent POST and seal body/hash/control metadata pins verified after initial second-proposal seal. No first transaction or all143 runtime bodies rerun. This supplements the earlier accurately qualified Root short-prefix report without modifying its receipt.','ownMaxRSSBytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024}
assert j['ownMaxRSSBytes']<24*1048576
with open(ROOT+'/FIRST-POST-CONTROL.json','x') as o:json.dump(j,o,indent=2);o.write('\n')
print(json.dumps({'firstPostGATESHA256':pins[0]['sha256'],'firstPostFinalSealSHA256':pins[1]['sha256'],'ownMaxRSSBytes':j['ownMaxRSSBytes']}))
