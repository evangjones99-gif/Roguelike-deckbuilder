from pathlib import Path
import os,json,hashlib,stat,resource,tarfile,ast
resource.setrlimit(resource.RLIMIT_DATA,(24*1048576,24*1048576))
S=Path('/workspace/scratch');R=Path('/workspace/Roguelike-deckbuilder');P=S/'r3-two-raw-retirement-independent-r1';A=S/'r3-two-raw-retirement-source-author-r1'
KEYS=['st_dev','st_ino','st_mode','st_nlink','st_uid','st_gid','st_size','st_blocks','st_atime_ns','st_mtime_ns','st_ctime_ns']
def md(s):return {k:getattr(s,k) for k in KEYS}
def op(p,flags=os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME):
 p=Path(p);fd=os.open('/',os.O_PATH|os.O_DIRECTORY|os.O_NOFOLLOW)
 try:
  for part in p.parent.parts[1:]:
   assert part not in ('','.', '..');n=os.open(part,os.O_PATH|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd);os.close(fd);fd=n
  return os.open(p.name,flags,dir_fd=fd)
 finally:os.close(fd)
def pin(p,body=False):
 p=Path(p);before=md(os.lstat(p));fd=op(p);h=hashlib.sha256();parts=[];size=0
 try:
  assert stat.S_ISREG(before['st_mode']) and before==md(os.fstat(fd));attrs={n:os.getxattr(fd,n).hex() for n in os.listxattr(fd)}
  for b in iter(lambda:os.read(fd,65536),b''):
   h.update(b);size+=len(b)
   if body:parts.append(b);assert size<300*1024
  assert md(os.fstat(fd))==before==md(os.lstat(p))
 finally:os.close(fd)
 q={'path':str(p),'sha256':h.hexdigest(),'bytes':size,'metadata':before,'xattrs':attrs};return (q,b''.join(parts)) if body else q
def load(p):
 q,b=pin(p,True);return q,json.loads(b)
def simple(q):return {k:q[k] for k in ['path','sha256','bytes']}
def digest(f):
 h=hashlib.sha256();n=0
 for b in iter(lambda:f.read(65536),b''):h.update(b);n+=len(b)
 return h.hexdigest(),n
pp,e=load(A/'PROPOSAL.json');assert pp['sha256']=='46a18623e87d07c6840de918225d38ac9937e050ac546ab842973488bcd1a7c0'
sp,seal=load(A/'FINAL-SEAL.json');assert sp['sha256']=='0467271a3280f799965271cafbc6be6f8fa261d94593568ed0a14f2c2337c4df'
for rel,n,h in seal['files']:
 p=A/rel;assert p.is_relative_to(A);q=pin(p);assert (q['bytes'],q['sha256'])==(n,h)
_,author_guard=load(A/'SEAL-GUARD/RESULT.json');assert author_guard['exit_code']==0 and author_guard['failure'] is None
methods=[]
for name,h in seal['methods'].items():
 q,b=pin(A/name,True);assert q['sha256']==h;ast.parse(b);methods.append(q)
root=S/'target-clear-ghost-comparison-actual-r3';assert len(e['rawFiles'])==2 and {Path(q['path']).name for q in e['rawFiles']}=={'VISUAL-RESULT.json','VISUAL-PROGRESS.json'}
raw=[]
for old in e['rawFiles']:
 assert Path(old['path']).parent==root;q=pin(old['path']);assert (q['sha256'],q['bytes'],q['xattrs'])==(old['sha256'],old['bytes'],old['xattrs']) and q['xattrs']=={}
 assert all(q['metadata'][k]==v for k,v in old['fstat'].items() if k!='st_atime_ns') and q['metadata']['st_nlink']==1 and q['metadata']['st_dev']==27
 q['proposalMetadata']=old['fstat'];q['initialAtimeDifference']=q['metadata']['st_atime_ns']!=old['fstat']['st_atime_ns'];raw.append(q)
assert raw[0]['sha256']!=raw[1]['sha256']
cap=pin(e['capsule']['path']);assert (cap['sha256'],cap['bytes'],cap['xattrs'])==(e['capsule']['sha256'],e['capsule']['bytes'],{})
assert all(cap['metadata'][k]==v for k,v in e['capsule']['fstat'].items() if k!='st_atime_ns')
found={};manifest=None;count=0;mfbytes=None
fd=op(cap['path'])
with os.fdopen(fd,'rb') as stream,tarfile.open(fileobj=stream,mode='r|gz') as tar:
 for m in tar:
  count+=1;assert count<=800
  if m.name=='MANIFEST.json':
   assert manifest is None and m.isfile() and m.size<300*1024;b=tar.extractfile(m).read();assert hashlib.sha256(b).hexdigest()==e['manifestSHA256'];manifest=json.loads(b);mfbytes=len(b)
  if m.name in {x['blobMember'] for x in e['exactLogicalMapping']}:
   assert m.isfile() and m.name not in found
   with tar.extractfile(m) as f:h,n=digest(f)
   assert n==m.size;found[m.name]={'sha256':h,'bytes':n}
assert md(os.lstat(cap['path']))==cap['metadata'] and manifest is not None and len(found)==2
mapping=[]
for x in e['exactLogicalMapping']:
 assert x['blobMember']=='blobs/'+x['sha256'] and found[x['blobMember']]=={'sha256':x['sha256'],'bytes':x['bytes']}
 hits=[r for r in manifest['rows'] if str(Path(manifest['roots'][r[0]])/r[1])==x['originalPath']];assert len(hits)==1
 r=hits[0];assert (r[0]+'/'+r[1],r[2],r[3])==(x['logicalPath'],x['bytes'],x['sha256']);assert (x['sha256'],x['bytes']) in {(q['sha256'],q['bytes']) for q in raw};mapping.append(x)
assert {x['originalPath'] for x in mapping}=={q['path'] for q in raw}
controls=[]
for key in ['independentCompleteGate','selectedMap','currentHold','currentConfirmedHEADControl']:
 q=pin(e[key]['path']);assert (q['sha256'],q['bytes'])==(e[key]['sha256'],e[key]['bytes']);controls.append(q)
complete=json.loads(Path(e['independentCompleteGate']['path']).read_text());assert complete['completeCoverage'] and complete['all303BlobsRoundtripExact'] and complete['all318LogicalMappingsAndOriginalBodiesExact'] and complete['archiveSHA256']==cap['sha256'] and complete['manifestSHA256']==e['manifestSHA256']
suppp,supp=load(A/'CONSUMER-SUPPLEMENT.json');assert suppp['sha256']=='ea8a168bced976f97715eb86a65b1dd729bfdbae9d335bea5573ef6ced6f44a1'
consumers=[];rootliteral=str(root);historical=0
for row in e['consumerChecks']:
 if 'pin' not in row:continue
 old=row['pin'];q,b=pin(old['path'],True);assert q['sha256']==old['sha256'];text=b.decode();refs=[{'line':i,'text':line[:1000]} for i,line in enumerate(text.splitlines(),1) if any(x in line for x in [rootliteral,'VISUAL-RESULT.json','VISUAL-PROGRESS.json'])]
 if row['currentPendingConsumer']:assert rootliteral not in text
 if row['historicalRole']:assert rootliteral in text and "ACT/'VISUAL-RESULT.json'" in text;historical+=1
 consumers.append({**simple(q),'historicalRole':row['historicalRole'],'mappingRole':row['mappingRole'],'currentConsumer':row['currentPendingConsumer'],'references':refs})
assert historical==1
for old in supp['finalCallerAndCompletedPromotionPins']:
 q,b=pin(old['path'],True);assert q['sha256']==old['sha256'] and rootliteral.encode() not in b;consumers.append({**simple(q),'currentConsumer':True})
cg,caller=load(S/'target-clear-default-caller-independent-r1/GATE.json');assert cg['sha256']=='36ddead7bcd9647706f33c766952732dc3ff7b42455f2c678b125569bde2c31a' and caller['status']=='CLOSED' and caller['priorRawReaderNeeded'] is False
driver=Path(S/'target-clear-default-caller-author-r1/driver-paired-r1.mjs').read_text();assert "path.join(packet,'VISUAL-PROGRESS.json')" in driver and "path.join(packet,'VISUAL-RESULT.json')" in driver and "fs.readFileSync('/workspace/scratch/target-clear-default-caller-author-r1/EXPECTED-CANDIDATE.json')" in driver
protected=S/'retained-original-archives/preflight-bdf273-original-r4.zip';protected_before=md(os.lstat(protected));assert (protected_before['st_dev'],protected_before['st_ino'],protected_before['st_size'],protected_before['st_nlink'])==(27,678628,1856041104,1)
selected=json.loads(Path(e['selectedMap']['path']).read_text());assert len(selected['inputs'])==88 and len(selected['outputs'])==56
current=[]
for key,pathroot in [('inputs',R),('outputs',R/'dist')]:
 for rel,h in selected[key].items():
  q=pin(pathroot/rel);assert q['sha256']==h;current.append({'group':key,'relativePath':rel,'bytes':q['bytes'],'sha256':q['sha256']})
assert len(current)==144
parentrights=[]
for path,old in e['parentRights'].items():
 fd=op(Path(path)/'unused',os.O_PATH) if False else os.open(path,os.O_PATH|os.O_DIRECTORY|os.O_NOFOLLOW)
 try:z=md(os.fstat(fd));attrs={n:os.getxattr('/proc/self/fd/'+str(fd),n).hex() for n in os.listxattr('/proc/self/fd/'+str(fd))}
 finally:os.close(fd)
 assert all(z[k]==old['metadata'][k] for k in ['st_dev','st_ino','st_mode','st_uid','st_gid']) and attrs==old['xattrs'];parentrights.append({'path':path,'freshMetadata':z,'xattrs':attrs,'rightsFieldsExact':True})
base=sum(q.stat().st_size for q in A.rglob('*') if q.is_file())+sum(q['bytes'] for q in methods if not q['path'].endswith('/restore-r3-fresh.py'))+cg['bytes'];assert base+128*1024+48*1024<512*1024
protected_after=md(os.lstat(protected));assert protected_after==protected_before
rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024;assert rss<24*1048576
proof={'proposal':pp,'authorSeal':sp,'methods':methods,'rawFullBodies':raw,'capsuleFullEncoding':cap,'manifestSHA256':e['manifestSHA256'],'manifestBytes':mfbytes,'archiveMemberCount':count,'twoFullArchivedBlobBodies':found,'exactLogicalMapping':mapping,'completeExisting303_318ProofReusedNotReplayed':True,'controlPins':controls,'consumerSupplement':suppp,'knownConsumers':consumers,'latestCallerGate':cg,'currentFull144Bodies':current,'parentRights':parentrights,'protectedZipStatBefore':protected_before,'protectedZipStatAfter':protected_after,'protectedZipNeverOpened':True,'publisherOtherCopiedBodyBytes':base,'publisherConservativeTotalBodyAndGeneratedBound':base+128*1024+48*1024,'publisherCapBytes':524288,'grossAllocationBytes':sum(x['metadata']['st_blocks']*512 for x in raw),'logicalBytes':sum(x['bytes'] for x in raw),'ownMaxRSSBytes':rss,'allFDsClosed':True,'scope':'No raw JSON decoding, archive extraction, restoration, retirement, Git, Node, browser/image/build/native. Normal64+512 guard; memory/cgroup not exclusive attribution. Static current consumer evidence plus declared closed workflow, not global future/FD absence.'}
assert proof['grossAllocationBytes']==e['grossAllocationBytes']==5005312
with (P/'PROOF.json').open('x') as f:json.dump(proof,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
print(json.dumps({'normal':True,'fullRawBodies':2,'fullBlobBodies':2,'fullCurrentBodies':144,'manifestBytes':mfbytes,'gross':5005312,'publisherBase':base,'publisherUpperBound':base+128*1024+48*1024,'ownMaxRSSBytes':rss,'allFDsClosed':True}))
