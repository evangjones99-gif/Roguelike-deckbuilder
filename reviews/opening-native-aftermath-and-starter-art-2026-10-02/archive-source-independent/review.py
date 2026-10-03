import ast,hashlib,json,os,pathlib,stat,time
P=pathlib.Path(__file__).parent
A=pathlib.Path('/workspace/scratch/native-aftermath-starter-checkpoint-source-author-r1')
def sha(p):
 h=hashlib.sha256()
 with pathlib.Path(p).open('rb') as f:
  for b in iter(lambda:f.read(65536),b''):h.update(b)
 return h.hexdigest()
def j(p):return json.loads(pathlib.Path(p).read_bytes())
def put(n,v):(P/n).write_text(json.dumps(v,indent=2)+'\n')
pins={'FINAL-SEAL.json':'44bdfd1eee375b6686e09cd40b38ad37d1c0be7c6aa9656c421b4ebcd227cbc3','MANIFEST.json':'51bf536706f7f0d3bce4fd3c049c5e1a4817a52bb16b4ce7e1c96a864b3391ff','preserve-direct-final.py':'5ad10c515b362ac6434ad6041565a13d74551f53e658c1f65c5ab4a08c10dd0f','preserve-direct-r2.py':'9818bfbbb52ff3f4ad173c6c29071c77531011c95bda404f61636f9b3fad0568','SOURCE-SPEC-final.json':'13d1c918f57c103929e098a03ce90ba7574161e1e0ae75e598960812e7ec6e0f','SOURCE-SPEC.json':'c433f479bf32a66beeb2696fb5a009be7746d9353641ea3caee7fbbd77bdcdaf'}
for n,h in pins.items():assert sha(A/n)==h
r2=(A/'preserve-direct-r2.py').read_text();r1=(A/'preserve-direct.py').read_text()
s=j(A/'METHOD-SUCCESSOR.json');restored=r2
for d in reversed(s['literalDeltas']):
 assert restored.count(d['after'])==1;restored=restored.replace(d['after'],d['before'],1)
assert restored==r1 and sha(A/'preserve-direct.py')==s['beforeMethodSHA256']
i=j(A/'METHOD-INVERSE.json');base=pathlib.Path(i['base']['path']);assert sha(base)==i['base']['sha256']
assert r1.count(i['addedAuthorizeBlock']+'\n')==1
restored=r1.replace(i['addedAuthorizeBlock']+'\n','',1)
for d in reversed(i['deltas']):
 assert restored.count(d['after'])==1;restored=restored.replace(d['after'],d['before'],1)
assert restored.encode()==base.read_bytes()
tree=ast.parse((A/'preserve-direct-final.py').read_text());vals={}
for n in tree.body:
 if isinstance(n,ast.Assign) and isinstance(n.value,ast.Constant):
  for t in n.targets:
   if isinstance(t,ast.Name):vals[t.id]=n.value.value
assert r2.count(vals['a'])==1
effective=r2.replace(vals['a'],vals['z'],1);ast.parse(effective)
assert effective.replace(vals['z'],vals['a'],1)==r2
patch=j(A/'SOURCE-SPEC-final.json');assert sha(patch['inherits']['path'])==patch['inherits']['sha256']
spec=j(patch['inherits']['path']);spec.update(patch['updates'])
for key,pkey in [('requiredRoots','appendRequiredRoots'),('fixedSingleFiles','appendFixedSingleFiles'),('requiredControlPins','appendControlPins')]:spec[key]+=patch[pkey]
assert spec['activeMethodSHA256']==pins['preserve-direct-final.py']
allowed={r['path'] for r in spec['fixedRoots']}|set(spec['fixedSingleFiles'])|{r['stage'] for r in spec['runtimeAuthorities']}
assert set(spec['requiredRoots'])<=allowed
assert not any('/.git/' in x or '/releases/' in x or x.endswith(('.tar.gz','.zip','.pack')) for x in allowed)
assert len(spec['existingCapsules'])==1
old=spec['existingCapsules'][0]
for k in ('index','complete'):assert sha(old[k]['path'])==old[k]['sha256']
st=os.stat(old['archive']['path'],follow_symlinks=False)
assert stat.S_ISREG(st.st_mode) and st.st_size==old['archive']['bytes']
index=j(old['index']['path']);assert index['newArchive']['sha256']==old['archive']['sha256']
cp=[]
for p in spec['requiredControlPins']:
 assert sha(p['path'])==p['sha256'];assert pathlib.Path(p['path']).stat().st_size==p['bytes'];cp.append(p['sha256'])
runtime=[]
for r in spec['runtimeAuthorities']:
 assert sha(r['freeze']['path'])==r['freeze']['sha256'];f=j(r['freeze']['path'])
 assert [len(f['inputs']),len(f['outputs'])]==r['mappedCounts']==[98,64]
 assert f['sourceDigest']==r['sourceDigest'] and f['outputsDigest']==r['outputsDigest']
 runtime.append({'stage':r['stage'],'freezeSHA256':r['freeze']['sha256'],'sourceDigest':r['sourceDigest'],'outputsDigest':r['outputsDigest'],'counts':r['mappedCounts']})
# Confirm critical actual predicates, without importing or executing the publisher.
need=['if not __debug__','O_NOFOLLOW','O_NOATIME','RootVerifiedCompleteFixedScopeAndOriginalFailures','RootVerifiedFreshCurrentCleanPush','ROOT-FINAL-INPUT-MANIFEST.json','ROOT-ARCHIVE-GRANT.json','PROCESS_STARTED','maxAllOutputLogicalAndAllocatedBytes','existingCapsules','runtimeCodeAllowedRelativePaths','NOT_RUN','assert len(inherited)==1']
for token in need:assert token in effective,token
rss={x.split(':')[0]:x.split(':')[1].strip() for x in pathlib.Path('/proc/self/status').read_text().splitlines() if x.startswith(('VmRSS:','VmHWM:'))}
assert int(rss['VmRSS'].split()[0])<24576 and int(rss['VmHWM'].split()[0])<24576
put('PROOF.json',{'scope':'Independent SOURCE review; helper reconstructed as text/AST only, not imported or executed','sourcePins':pins,'exactInverses':{'r2ToR1LiteralDeltas':len(s['literalDeltas']),'r1ToPriorLiteralDeltas':len(i['deltas']),'authorizeBlockRemovedExactlyOnce':True,'priorMethodSHA256':i['base']['sha256'],'wrapperSpecLoaderDelta':1},'effectiveContract':{'fixedRoots':len(spec['fixedRoots']),'singleFiles':len(spec['fixedSingleFiles']),'requiredRoots':len(spec['requiredRoots']),'requiredControlPins':len(cp),'futureOptionalRoots':spec['futureOptionalFixedRoots'],'runtimeAuthorities':runtime,'output':spec['canonicalOutputDirectory'],'futureBudget':spec['futureArchive']},'oldArchive':{'authority':old,'bodyAccess':'NONE; stat only; pinned INDEX/COMPLETE JSON read','stat':{'dev':st.st_dev,'ino':st.st_ino,'size':st.st_size,'mtime_ns':st.st_mtime_ns}},'trustedManifestBoundary':['Root must full-hash every logical regular row, including duplicate-body paths, before final closure','Root must compare every runtime row SHA/size against pinned full frozen input/output maps','Root must set manifest runtimeAuthorities literally equal to effective SPEC and verify held-media/installed-dependency bindings','Helper verifies chosen representative bytes for every NEW unique SHA and full streamed literal-original Tar readback, not every duplicate logical path independently','Final manifest/grant exact bodies are copied into the new archive directory; prior Tar body coverage is inherited from pinned COMPLETE/INDEX only','All now-closed required/optional Ash phases must be recorded truthfully; absent future phases NOT_RUN cannot become fabricated acceptance'],'resource':rss,'limitations':['No final Root input manifest or archive exists in this SOURCE gate','No archive COMPLETE, art/default/game quality/300-second/human-fun acceptance','Normal outer execution, terminal caps/time/resource/owned closure and independent COMPLETE review remain required','Source guard sparse shared-cgroup samples are qualified aggregate evidence, not exclusive full process ownership','Ordinary document reads may affect atime; no metadata reset or complete xattr preservation claim']})
print(json.dumps({'normal':True,'own':rss,'logicalBytesBeforeSeal':sum(p.stat().st_size for p in P.rglob('*') if p.is_file()),'helperExecuted':False}))
