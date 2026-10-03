import ast,gzip,hashlib,json,os,pathlib,re,resource,stat
resource.setrlimit(resource.RLIMIT_DATA,(24*1048576,24*1048576))
S=pathlib.Path('/workspace/scratch');A=S/'pixel-cue-evidence-preserver-source-author-r3';B=S/'pixel-cue-evidence-preserver-source-author-r2';P=pathlib.Path(__file__).parent
def encoded(x):return (json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode()
def sha(b):return hashlib.sha256(b).hexdigest()
def sm(s):return {k:getattr(s,'st_'+k) for k in ['dev','ino','mode','uid','gid','nlink','size','blocks','atime_ns','mtime_ns','ctime_ns']}
def noat(x):return {k:v for k,v in x.items() if k!='atime_ns'}
def attrs(p):return {n:os.getxattr(p,n,follow_symlinks=False).hex() for n in os.listxattr(p,follow_symlinks=False)}
def body(p):
 p=pathlib.Path(p);assert not str(p).startswith('/workspace/scratch/retained-original-archives/')
 fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME)
 try:
  s=os.fstat(fd);assert stat.S_ISREG(s.st_mode) and s.st_size<=2*1048576
  b=[]
  while True:
   x=os.read(fd,32768)
   if not x:break
   b.append(x)
  assert noat(sm(s))==noat(sm(os.fstat(fd)))
  return b''.join(b)
 finally:os.close(fd)
def pin(p):
 p=pathlib.Path(p);assert p.suffix.lower() not in ['.png','.jpg','.jpeg','.wav','.zip']
 b=body(p);return {'path':str(p),'sha256':sha(b),'bytes':len(b)}
def load(p):return json.loads(body(p))
def inventory(root):
 root=pathlib.Path(root);assert root.is_dir() and not root.is_symlink();rows=[]
 for base,ds,fs in os.walk(root,followlinks=False):
  ds[:]=sorted(x for x in ds if x not in ['__pycache__','node_modules','.git'])
  for d in ds:assert not pathlib.Path(base,d).is_symlink()
  for name in sorted(fs):
   p=pathlib.Path(base,name);z=p.lstat();assert stat.S_ISREG(z.st_mode);rows.append({'relative':str(p.relative_to(root)),'stat':sm(z)})
 return sorted(rows,key=lambda x:x['relative'])
expectedPins={'build-capsule.py':'e9568f2af3ac8248a5758eca90dc195200a1a7f78d16955d95fae29f4c072960','SUPPLEMENT.json':'999efb99ca48498754ef58543137fedcf0271c80543d34437f14a5d42dbd57ed','EXPECTED-INVENTORIES.json.gz':'e780cce6990d2034d9959c77ea5c33ca96b56dea557da3c750327f4ca871a451','MANIFEST.json':'6096be64fba0a6b89006e92c2e764c4bff5159d5a89ce1baa0d62b8ae9179e6e','FINAL-SEAL.json':'0404e41ef6768ab1d87417cca9941f84be42e74cd208f025dd600f8ef443efe3'}
for n,h in expectedPins.items():assert pin(A/n)['sha256']==h,n
m=load(A/'MANIFEST.json')
for r in m['bodies']:assert pin(A/r['path'])=={'path':str(A/r['path']),'sha256':r['sha256'],'bytes':r['bytes']}
helper=body(A/'build-capsule.py');ast.parse(helper)
# Independently apply the complete reviewed unified delta to the immutable R2.
old=body(B/'build-capsule.py').decode().splitlines(True);diff=body(A/'atime-only-successor.diff').decode().splitlines(True);out=[];pos=0;i=2
while i<len(diff):
 match=re.match(r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@',diff[i]);assert match,diff[i]
 start=int(match[1])-1;out.extend(old[pos:start]);pos=start;i+=1
 while i<len(diff) and not diff[i].startswith('@@ '):
  line=diff[i];tag=line[0];text=line[1:]
  if tag in ' -':assert old[pos]==text;pos+=1
  if tag in ' +':out.append(text)
  assert tag in ' +-';i+=1
out.extend(old[pos:]);assert ''.join(out).encode()==helper
supp=load(A/'SUPPLEMENT.json');assert pin(supp['originalPlanPath'])['sha256']==supp['originalPlanSHA256']=='56c1615aa9c7afb2b0f77e41825ba95f43fb0140e06b632fee1451441506661f'
plan=load(supp['originalPlanPath']);meta=json.loads(gzip.decompress(body(A/'EXPECTED-INVENTORIES.json.gz')));assert len(meta['roots'])==39 and len(plan['roots'])==38
groups={x['path']:x for x in plan['roots']};assert set(x['path'] for x in meta['roots'])==set(groups)|{str(B)}
rootProof=[];drifts=[]
for group in meta['roots']:
 rows=group['rows'];original=[{'relative':r['relative'],'stat':r['stat']} for r in rows];assert sha(encoded(original))==group['originalFullStatInventorySHA256']
 if group['path'] in groups:assert groups[group['path']]['inventorySHA256']==group['originalFullStatInventorySHA256']
 projected=[{'relative':r['relative'],'stat':noat(r['stat'])} for r in rows];assert sha(encoded(projected))==group['nonAtimeInventorySHA256']
 current=inventory(group['path']);assert sha(encoded([{'relative':r['relative'],'stat':noat(r['stat'])} for r in current]))==group['nonAtimeInventorySHA256'];assert len(current)==len(rows)
 for a,b in zip(current,rows):
  p=pathlib.Path(group['path'])/b['relative'];assert a['relative']==b['relative'] and noat(a['stat'])==noat(b['stat']) and attrs(p)==b['xattrs']
  if a['stat']['atime_ns']!=b['stat']['atime_ns']:drifts.append({'path':str(p),'expectedAtimeNs':b['stat']['atime_ns'],'currentAtimeNs':a['stat']['atime_ns'],'domain':'namedroot','nonAtimeAndXattrsExact':True})
 rootProof.append({'path':group['path'],'bodies':len(rows),'originalFullStatSHA256':group['originalFullStatInventorySHA256'],'nonAtimeSHA256':group['nonAtimeInventorySHA256']})
files={x['path']:x for x in meta['files']};assert set(files)==set(x['path'] for x in plan['files']) and len(files)==13
for item in plan['files']:
 x=files[item['path']];current=sm(os.lstat(item['path']));assert x['expectedOriginalStat']==item['stat'] and noat(current)==noat(item['stat']) and attrs(item['path'])==x['xattrs']
 if current['atime_ns']!=item['stat']['atime_ns']:drifts.append({'path':item['path'],'expectedAtimeNs':item['stat']['atime_ns'],'currentAtimeNs':current['atime_ns'],'domain':'planfile','nonAtimeAndXattrsExact':True})
 if 'sha256' in item:assert pin(item['path'])['sha256']==item['sha256']
actual=S/'coherent-native128-pixel-comparison-actual-r6';audit=load(actual/'BYTE-AUDIT-before.json');assert pin(actual/'BYTE-AUDIT-before.json')['sha256']==plan['sourceCorrection']['actualBeforeAuditSHA256']
controls=[{'logicalPath':str(pathlib.Path(x['root'])/x['name']),'resolvedPath':x['resolvedPath'],'sha256':x['sha256'],'bytes':x['bytes'],'aliasChain':x['aliasChain']} for x in audit['controls']];assert controls==plan['actualAuditedControls'] and len(controls)==40
new=[]
for x in controls:
 q=pin(x['resolvedPath']);assert (q['sha256'],q['bytes'])==(x['sha256'],x['bytes'])
 if x['resolvedPath'] not in plan['auditedCallerControls']:new.append(q)
assert len(new)==37 and sum(x['bytes'] for x in new)==234807 and len(plan['auditedCallerControls'])==59
for path,x in plan['auditedCallerControls'].items():assert pin(path)['sha256']==x['sha256']
binary={'.png','.jpg','.jpeg','.wav','.ogg','.mp3','.ico','.woff','.woff2'};code=0;deps=0;newart=0;freezeProof=[]
for desc in plan['freezes']:
 assert pin(desc['path'])['sha256']==desc['sha256'];f=load(desc['path']);assert [len(f['inputs']),len(f['outputs'])]==desc['counts'];freezeProof.append({'path':desc['path'],'sha256':desc['sha256'],'counts':desc['counts']})
 for fam in ['inputs','outputs']:
  assert sha(encoded(f[fam]).rstrip(b'\n'))==desc[fam+'MapSHA256']
  for rel,h in f[fam].items():
   p=pathlib.Path(f['stage'])/('dist/'+rel if fam=='outputs' else rel);target=p.resolve(strict=True)
   if p.suffix.lower() in binary:
    assert target.is_file();newart+=pathlib.Path(rel).name in plan['newArtNames'];deps+=pathlib.Path(rel).name not in plan['newArtNames']
   else:assert pin(target)['sha256']==h;code+=1
support=load(plan['supportMap']['path']);mapping=support.get('supportBodies',support.get('support30Bodies',{}));assert len(mapping)==30
for rel,h in mapping.items():assert pin(pathlib.Path(load(plan['freezes'][0]['path'])['stage'])/rel)['sha256']==(h if isinstance(h,str) else h['sha256'])
reviewRoots=plan['pendingActivation']['requiredReviewRoots'];reviews=[]
for root in reviewRoots:
 g=pathlib.Path(root)/'GATE.json';reviews.append({**pin(g),'decision':load(g)['decision'],'nonAtimeInventorySHA256':sha(encoded([{'relative':r['relative'],'stat':noat(r['stat'])} for r in inventory(root)]))})
assert len(reviews)==3 and next(x['decision'] for x in reviews if 'actual-gameplay-' in x['path']).startswith('REJECT')
assert plan['futureRootResourceScope']['workMiB']==256 and plan['futureRootResourceScope']['reserveMiB']==512 and plan['futureRootResourceScope']['initialDiskMiB']==74 and plan['futureRootResourceScope']['maximumOutputAllocatedBytes']==16*1048576
for name in ['PREPARE-GUARD','SEAL-GUARD']:
 r=load(A/name/'RESULT.json');assert r['exit_code']==0 and r['failure'] is None and r['memory_events_before']==r['memory_events_after']
assert not (S/'pixel-cue-evidence-preserver-source-independent-r2/GATE.json').exists(),'Original R2 never issued a filesystem gate'
rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss;assert rss<=24576
proof={'decision':'ACCEPT_R3_ATIME_RECORDED_PRESERVATION_METHOD_SOURCE_ONLY','pins':expectedPins,'plan':pin(supp['originalPlanPath']),'helperDiffExactApplied':True,'original38FullStatInventoryDigestsReconstructed':True,'roots':rootProof,'all39CurrentNonAtimeAndXattrsExact':True,'currentAtimeOnlyDifferences':drifts,'ordinaryAtimeCauseUnconfirmed':True,'actualControlDomain':40,'separateSourceDomain':59,'new37FullBodiesBytes':234807,'freezes':freezeProof,'codeBodiesFreshlyHashed':code,'mediaBodiesNotOpened':True,'newArtLogicalOccurrencesMetadataOnly':newart,'externalHeldDependencyOccurrences':deps,'supportBodies':30,'closedPixelReviewPins':reviews,'RootFinalThreeDocActivationRequired':plan['pendingActivation']['metadata'],'newUIActual12_89MBAndNewCueActualNotInScope':True,'ownMaxRSSKiB':rss,'futureArgv':['python3',str(A/'build-capsule.py'),'--plan',supp['originalPlanPath'],'--plan-sha256',supp['originalPlanSHA256'],'--supplement-sha256',expectedPins['SUPPLEMENT.json'],'--activation','FRESH_ROOT_ACTIVATION_ABSOLUTE.json','--activation-sha256','EXACT_ACTIVATION_SHA256','--output','/workspace/scratch/pixel-cue-evidence-capsule-root-r1'],'limits':['SOURCE only; no archive built or roundtrip executed','Root256+512/disk74 streaming cap16MiB only after fresh metadata activation','Masters/JPEG/raw/sprite/archive bodies unopened; unchanged dependencies externally retained, not self-contained release','Atime-only drift observed/recorded, no reset; content/otherstats/xattrs strict; protectedZIP excluded','R1 omitted37 rejection and R2 staleINDEX communication/noGATE remain preserved','Archivefile fsync only, no wholepowerloss atomic or directory-durability claim','Postwrite allocated cap/failstop retains failed output; no cleanup/selection/default/fun claim']}
(P/'PROOF.json').write_text(json.dumps(proof,separators=(',',':'))+'\n');print(json.dumps({'status':proof['decision'],'roots':39,'currentAtimeOnlyDifferences':len(drifts),'actualControls':40,'sourceControls':59,'ownMaxRSSKiB':rss,'proofSHA256':sha(body(P/'PROOF.json'))}))
