from pathlib import Path
import os,json,hashlib,resource,stat,tarfile
resource.setrlimit(resource.RLIMIT_DATA,(24*1048576,24*1048576))
S=Path('/workspace/scratch');R=Path('/workspace/Roguelike-deckbuilder');P=S/'default-clear-preservation-independent-r1';M=S/'default-clear-publication-source-author-r1';D=R/'reviews/opening-default-target-clear-2026-10-02'
def pin(path):
 p=Path(path);h=hashlib.sha256()
 with os.fdopen(os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME),'rb') as f:
  s=os.fstat(f.fileno());assert stat.S_ISREG(s.st_mode)
  for b in iter(lambda:f.read(65536),b''):h.update(b)
  assert s==os.fstat(f.fileno())==os.lstat(p)
 return {'path':str(p),'sha256':h.hexdigest(),'bytes':s.st_size}
def load(p):
 with os.fdopen(os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME),'rb') as f:
  b=f.read(262145);assert len(b)<=262144;return json.loads(b)
def fullstat(p):
 s=os.lstat(p);return {k:getattr(s,k) for k in ['st_dev','st_ino','st_mode','st_nlink','st_uid','st_gid','st_size','st_blocks','st_atime_ns','st_mtime_ns','st_ctime_ns']}
protected=S/'retained-original-archives/preflight-bdf273-original-r4.zip';zbefore=fullstat(protected)
source=load(P/'SOURCE-PROOF.json');sg=load(P/'SOURCE-GATE.json');ss=load(P/'SOURCE-SEAL.json');assert sg['decision'].startswith('ACCEPT') and sg['completeCoverage'] is False
for rel,q in ss['files'].items():assert pin(P/rel)==q
assert zbefore==source['protectedZIPFullStat']
plan=load(M/'PLAN-r2.json');summary=load(D/'PRESERVATION.json');controls=load(M/'REVIEW-CONTROLS.json')
for q in source['methods']+[source['plan'],source['sourceSeal'],source['reviewControls'],source['beforeMap'],source['candidateFreeze'],source['currentHEADSourcePin']]+source['actualReviewGates']:assert pin(q['path'])=={k:q[k] for k in ['path','sha256','bytes']}
hold=pin(R/'AGENTS.md');assert hold['sha256']==sg['currentHold']['sha256']
for role,q in controls.items():assert pin(q['path'])['sha256']==q['sha256'] and load(q['path'])['decision'].startswith('ACCEPT')
before=load(plan['beforeMap']['path']);after=load(plan['candidateFreeze']['path']);stage=Path(after['stage'])
assert summary['logicalBodies']==370 and summary['uniqueBlobs']==320 and summary['neededDependencies']==204 and summary['actualFileCount']==28 and summary['roundtripVerified'] is True
assert summary['actualReviewGates']==controls and summary['beforeMapSHA256']==source['beforeMap']['sha256'] and summary['candidateFreezeSHA256']==source['candidateFreeze']['sha256']
assert summary['candidateSourceDigest']==after['sourceDigest']==plan['candidateSourceDigest'] and summary['candidateOutputsDigest']==after['outputsDigest']==plan['candidateOutputsDigest']
archive=D/summary['archive'];ap=pin(archive);assert ap['sha256']==summary['archiveSHA256']=='1f2d96c0b1419d209984e0990ebdd23cf0a1e7996099d11748c6ab5c1a303c1e' and ap['bytes']==summary['archiveBytes']==1672575
seen={};manifest=None;manifestHash=None
with os.fdopen(os.open(archive,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME),'rb') as f:
 astat=os.fstat(f.fileno())
 with tarfile.open(fileobj=f,mode='r|gz') as tar:
  for member in tar:
   assert member.isfile()
   with tar.extractfile(member) as body:
    if member.name=='MANIFEST.json':
     assert manifest is None and not seen and member.size<2*1048576
     raw=body.read(2*1048576);assert len(raw)==member.size
     manifestHash=hashlib.sha256(raw).hexdigest();manifest=json.loads(raw);del raw
    else:
     assert manifest is not None and member.name.startswith('blobs/')
     h=member.name[6:];assert len(h)==64 and h not in seen and member.size<=8*1048576
     digest=hashlib.sha256();n=0
     for b in iter(lambda:body.read(65536),b''):digest.update(b);n+=len(b)
     assert n==member.size and digest.hexdigest()==h;seen[h]=n
 assert astat==os.fstat(f.fileno())==os.lstat(archive)
assert manifestHash==summary['manifestSHA256']=='a8b162eb82f844e9656b8d0022c1575e70eb82e723395dde2b9ee3ef03ebd12e'
assert manifest['schema']=='default-clear-complete-content-addressed-capsule-r1'
expected={};deps=[];currentBodies=0
def record(logical,path,h=None):
 q=pin(path)
 if h is not None:assert q['sha256']==h
 row={'originalPath':str(path),'bytes':q['bytes'],'sha256':q['sha256']}
 assert logical not in expected;expected[logical]=row
def tree(root):
 for path in sorted(root.rglob('*')):
  assert not path.is_symlink()
  if path.is_file():yield path,str(path.relative_to(root))
for label,base,freeze in [('old-current',R,before),('candidate',stage,after)]:
 assert len(freeze['inputs'])==88 and len(freeze['outputs'])==56
 for scope,root,mapping in [('inputs',base,freeze['inputs']),('outputs',base/'dist',freeze['outputs'])]:
  for rel,h in mapping.items():
   path=root/rel;q=pin(path);assert q['sha256']==h;currentBodies+=1
   if rel.endswith(('.png','.wav')) or scope=='outputs' and rel.startswith(('art/','audio/')):deps.append({'logicalPath':label+'/'+scope+'/'+rel,'originalPath':str(path),'sha256':h,'bytes':q['bytes'],'externalRetainedNeeded':True})
   else:record(label+'/'+scope+'/'+rel,path,h)
 outputNames=set()
 for child in sorted((base/'dist').iterdir()):
  if child.is_symlink():
   assert base==stage and child.name in ['art','audio'] and os.readlink(child)==str(R/'dist'/child.name)
   outputNames.update(child.name+'/'+rel for path,rel in tree(R/'dist'/child.name))
  elif child.is_dir():outputNames.update(child.name+'/'+rel for path,rel in tree(child))
  else:outputNames.add(child.name)
 assert outputNames==set(freeze['outputs'])
roots=plan['roots']+[{'label':'publication-source','path':str(M)}]+[{'label':'actual-review-'+role,'path':str(Path(q['path']).parent)} for role,q in controls.items()]
for root in roots:
 for path,rel in tree(Path(root['path'])):record(root['label']+'/'+rel,path)
for q in plan['singleControls']+[source['reviewControls']]:record('single-controls/'+Path(q['path']).name,Path(q['path']),q['sha256'])
assert manifest['logicalBodies']==expected and len(expected)==370
assert manifest['neededDependencies']==deps and len(deps)==204
unique={q['sha256']:q['bytes'] for q in expected.values()};assert seen==unique and len(seen)==320
assert manifest['oldCurrent144Maps']=={'inputs':before['inputs'],'outputs':before['outputs']} and manifest['candidate144Maps']=={'inputs':after['inputs'],'outputs':after['outputs']}
assert manifest['actualReviewGates']==controls and manifest['sourceDigest']==after['sourceDigest'] and manifest['outputsDigest']==after['outputsDigest']
assert len(plan['unchanged51Media'])==51 and plan['unchanged51Media']=={r:h for r,h in before['outputs'].items() if r.startswith(('art/','audio/'))}=={r:h for r,h in after['outputs'].items() if r.startswith(('art/','audio/'))}
saved=[];actual=Path(plan['actual']['root']);assert len(list(tree(actual)))==28
for side in ['A','B']:
 for label in ['C0','C1','C2','C-firstDrop','C-secondOutcome','C-normalized']:
  path=actual/(side+'-hold-release-'+label+'-OPAQUE-SAVE.json');q=pin(path);raw=load(path)['raw'].encode('utf-8');saved.append({'originalPath':str(path),'wrapperSHA256':q['sha256'],'rawUTF8SHA256':hashlib.sha256(raw).hexdigest(),'rawUTF8Bytes':len(raw)})
assert saved==manifest['actualSavedStringIdentities'] and all(saved[i]['rawUTF8SHA256']==saved[i+6]['rawUTF8SHA256'] and saved[i]['rawUTF8Bytes']==saved[i+6]['rawUTF8Bytes'] for i in range(6))
rootguard=S/'default-clear-capsule-root-guard-r1/RESULT.json';rg=load(rootguard);assert rg['exit_code']==0 and rg['failure'] is None and rg['memory_events_before']==rg['memory_events_after']
assert pin(S/'default-clear-preservation-root-r1/RESULT.json')['sha256']==pin(D/'PRESERVATION.json')['sha256']
assert zbefore==fullstat(protected)
rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024;assert rss<24*1048576
proof={'archive':ap,'manifestSHA256':manifestHash,'summary':pin(D/'PRESERVATION.json'),'completeCoverage':True,'sourceGate':pin(P/'SOURCE-GATE.json'),'sourceSeal':pin(P/'SOURCE-SEAL.json'),'logicalBodies':len(expected),'uniqueBlobs':len(seen),'fullUniqueBodyBytes':sum(seen.values()),'externalNeededDependencies':len(deps),'fullOldCandidateBodyChecks':currentBodies,'oldAndCandidateInputCounts':[88,88],'oldAndCandidateOutputCounts':[56,56],'actualFileCount':28,'actualSavedStringPairCount':6,'rawUTF8SeparateFromWrapperSHA':True,'allLogicalOriginalBodiesExact':True,'allRetainedDependenciesExact':True,'unchangedHeldMedia':51,'actualReviewGates':controls,'RootCapsuleGuard':pin(rootguard),'RootGuardRC':0,'RootGuardSamples':len(rg['samples']),'protectedZIPFullStatBefore':zbefore,'protectedZIPFullStatAfter':fullstat(protected),'protectedZIPBodyNeverOpened':True,'currentHold':hold,'ownMaxRSSBytes':rss,'capsulePhaseBudget':'Root allocated256MiB work+512MiB reserve/disk64MiB; ownRSS24MiB','limits':'Complete declared preservation coverage and retained dependency equality, not a self-contained execution environment or whole-power-loss/allselection atomicity. No selection/Git/engine/native/media/cleanup action. Sampled shared cgroup evidence is not exclusive attribution. Later Root selection must use exact reviewed methods and COMPLETE gate.','allOwnFDsClosed':True}
with (P/'COMPLETE-PROOF.json').open('x') as f:json.dump(proof,f,separators=(',',':'));f.write('\n');f.flush();os.fsync(f.fileno())
print(json.dumps({'completeCoverage':True,'all320BlobsRoundtrip':True,'all370LogicalOriginals':True,'all204Dependencies':True,'fullMapBodies':288,'ownRSSBytes':rss,'bodyFDsClosed':True}))
