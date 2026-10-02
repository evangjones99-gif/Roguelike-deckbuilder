import os,json,hashlib,resource
resource.setrlimit(resource.RLIMIT_DATA,(24*1048576,24*1048576))
ROOT='/workspace/scratch/five-rebuilt-png-recovery-proposal-r1'
def sd(s):return {'st_'+k:getattr(s,'st_'+k) for k in ['dev','ino','mode','uid','gid','nlink','size','blocks','atime_ns','mtime_ns','ctime_ns']}
def read(p):
 before=sd(os.lstat(p));f=os.open(p,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW);assert before==sd(os.fstat(f));attrs={n:os.getxattr(f,n).hex() for n in os.listxattr(f)};b=b''
 while True:
  c=os.read(f,65536)
  if not c:break
  b+=c;assert len(b)<262144
 assert before==sd(os.fstat(f));os.close(f);assert before==sd(os.lstat(p))
 return {'path':p,'lstat':before,'fstat':before,'xattrs':attrs,'sha256':hashlib.sha256(b).hexdigest()},json.loads(b)
pin,maps=read('/workspace/scratch/target-wait-default-promotion-root-r1/RESULT.json')
assert pin['sha256']=='31a221091d2ffbc6d58dfc1385962c441df9789c66729ef64d20b95208a8fabd'
_,p=read(ROOT+'/PROPOSAL.json')
proof=[]
for pair in p['pairs']:
 name=pair['anchor']['path'].split('/')[-1];rows={}
 for scope in ['canonicalInputs','canonicalOutputs']:
  table=maps[scope]
  if isinstance(table,dict):matches=[{'path':k,'sha256':v} if isinstance(v,str) else dict(v,path=k) for k,v in table.items() if ('/'+k).endswith('/art/'+name)]
  else:matches=[x for x in table if ('/'+x['path']).endswith('/art/'+name)]
  assert len(matches)==1,(scope,name,matches)
  assert matches[0]['sha256']==pair['anchor']['sha256'];rows[scope]=matches[0]
 proof.append({'name':name,'sha256':pair['anchor']['sha256'],'exactSelectedMapEntries':rows})
j={'selectedMapPin':pin,'selectedInputsCount':len(maps['canonicalInputs']),'selectedOutputsCount':len(maps['canonicalOutputs']),'fiveEntries':proof,'allFiveMatchExactSelectedMaps':True,'scope':'Five entries compared only; existing current full87/56 map receipt pinned, not all87/56 bodies rehashed. No canonical or historical media writes.','ownMaxRSSBytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024}
assert j['selectedInputsCount']==87 and j['selectedOutputsCount']==56 and j['ownMaxRSSBytes']<24*1048576
with open(ROOT+'/CURRENT-MAP-PROOF.json','x') as o:json.dump(j,o,indent=2);o.write('\n')
print(json.dumps({'selectedMapSHA256':pin['sha256'],'allFiveEntriesMatch':True,'ownMaxRSSBytes':j['ownMaxRSSBytes']}))
