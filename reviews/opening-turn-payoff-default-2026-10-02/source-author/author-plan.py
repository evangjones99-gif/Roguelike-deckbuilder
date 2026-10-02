import ast,errno,hashlib,io,json,os,pathlib,resource,stat,zlib
P=pathlib.Path(__file__).parent;S=pathlib.Path('/workspace/scratch');R=pathlib.Path('/workspace/Roguelike-deckbuilder');C=R/'reviews/coherent-native128-actual-trial-2026-10-02';roots=[];roles=[];rows=[];seenPaths=set();observations=[]
def sha(b):return hashlib.sha256(b).hexdigest()
def idx(xs,x):
 if x not in xs:xs.append(x)
 return xs.index(x)
def stream_hash(path):
 flags=os.O_RDONLY|os.O_NOFOLLOW;fallback=False
 try:fd=os.open(path,flags|getattr(os,'O_NOATIME',0))
 except OSError as e:
  if e.errno!=errno.EPERM:raise
  fd=os.open(path,flags);fallback=True
 with os.fdopen(fd,'rb') as f:
  before=os.fstat(f.fileno());assert stat.S_ISREG(before.st_mode);h=hashlib.sha256()
  while b:=f.read(65536):h.update(b)
  after=os.fstat(f.fileno());assert (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns)
 observations.append({'path':str(path),'noAtimeRequested':True,'permissionFallback':fallback});return h.hexdigest(),before.st_size
archive=C/'evidence-ce0f8f40bcf0f0b22e5e4d93eef3d4660662826e617900aba09ac208c148dc13.tar.gz';assert stream_hash(archive)[0]=='ce0f8f40bcf0f0b22e5e4d93eef3d4660662826e617900aba09ac208c148dc13';assert stream_hash(C/'INDEX.json')[0]=='115bbdb35d9cdff98503a3a5c63ced87e49a48d198194c9caa45268254bec0cf'
def capsule_members():
 # Incremental decoding of the logicalBodies array; no TAR/archive body reads.
 decoder=json.JSONDecoder();buf='';members={}
 with (C/'INDEX.json').open('r') as f:
  while '"logicalBodies":[' not in buf:
   b=f.read(65536);assert b;buf=(buf+b)[-131072:]
  buf=buf.split('"logicalBodies":[',1)[1]
  while True:
   buf=buf.lstrip(' \r\n\t,')
   if buf.startswith(']'):break
   try:row,end=decoder.raw_decode(buf)
   except json.JSONDecodeError:
    b=f.read(65536);assert b;buf+=b;assert len(buf)<=131072;continue
   assert row['blob']=='blobs/'+row['sha256'];members.setdefault(row['sha256'],{'blob':row['blob'],'bytes':row['bytes'],'originalPath':row['originalPath']});buf=buf[end:]
 return members
members=capsule_members()
def add(path,role,expected=None,preferExternal=True):
 path=pathlib.Path(path);key=str(path)
 if key in seenPaths:return
 seenPaths.add(key);st=path.lstat()
 if expected and expected in members and preferExternal:
  h=expected;n=members[h]['bytes'];storage='existingCapsule';assert st.st_size==n or stat.S_ISLNK(st.st_mode)
 else:
  assert not stat.S_ISLNK(st.st_mode);h,n=stream_hash(path);assert expected is None or h==expected;storage='existingCapsule' if preferExternal and h in members else 'newBlob'
 if storage=='existingCapsule':assert members[h]['bytes']==n
 root=path.parent;rows.append([idx(roots,str(root)),path.name,h,n,idx(roles,role),storage])
def folder(name,role):
 root=S/name;assert root.is_dir() and not root.is_symlink()
 for p in sorted(root.rglob('*')):
  if p.is_file():assert not p.is_symlink();add(p,role)
actualNames=['opening-turn-payoff-actual-comparison-root-r1','opening-turn-payoff-on-actual-comparison-root-r1'];reviewNames=['opening-turn-payoff-actual-technical-independent-r1','opening-turn-payoff-actual-gameplay-independent-r1','opening-turn-payoff-actual-visual-independent-r1','opening-turn-payoff-actual-visual-independent-r2','opening-turn-payoff-on-actual-technical-independent-r1','opening-turn-payoff-on-actual-gameplay-independent-r1','opening-turn-payoff-on-actual-visual-independent-r1']
for name in actualNames:folder(name,'original actual (all files including8 JPEG)')
for name in reviewNames:folder(name,'original independent actual review including failures')
vp=S/'opening-turn-payoff-on-actual-visual-independent-r1';visualPins={'GATE.json':'da16104f55c57d367e6e0c5f0d34b2d500da89f0e0b25da5898f04f0f5466aa7','REVIEW.md':'97de95d034bc616ab210bdfddeaac86c74a55b16907bfe5342372beb4e6a9339','MANIFEST.json':'18a7c1d97b532d5d66bf5bbef8f0fd51829f5d61e9cc52a0b9b342c077df1570','FINAL-SEAL.json':'89f743aa85d84e0e6fa58c9edb7a308d2b8c471b8eabba293afbdd9a3c087814'}
for n,h in visualPins.items():assert stream_hash(vp/n)[0]==h
defaultFolders=['opening-turn-payoff-on-source-root-r1','opening-turn-payoff-on-source-independent-r1','opening-turn-payoff-on-build-controls-author-r1','opening-turn-payoff-on-build-controls-independent-r1','opening-turn-payoff-on-build-independent-r1','opening-turn-payoff-on-build-independent-r2','opening-turn-payoff-on-strict-build-root-r1','opening-turn-payoff-on-assembly-guard-root-r1','opening-turn-payoff-on-freeze-guard-root-r1','opening-turn-payoff-on-actual-caller-source-author-r1','opening-turn-payoff-on-actual-caller-source-final-r2','opening-turn-payoff-on-actual-caller-source-independent-r1','opening-turn-payoff-on-actual-caller-source-independent-r2','opening-turn-payoff-on-caller-grammar-root-r1']
for name in defaultFolders:folder(name,'exact default source/build/caller proof and failed originals')
for name in ['opening-turn-payoff-on-activation-root-r1.json','opening-turn-payoff-on-native-grant-root-r1.json']:add(S/name,'Root exact activation/grant')
defaultFreeze=S/'opening-turn-payoff-on-strict-build-root-r1/final-seal-r1/RUNTIME-FREEZE.json';optinFreeze=S/'opening-turn-payoff-default-freeze-root-r3/RUNTIME-FREEZE.json';rollbackFreeze=S/'target-clear-default-build-author-r1/RUNTIME-FREEZE.json';freezePins=[(defaultFreeze,'60de8d2725b74e1ffe09f3a7af1b12310e8e6806a590b953abf62e6f4e286e1b'),(optinFreeze,'af126a8258f9c9f6a1320ba6c7d4fc0dd25b3c78567414ccef8ea1b548174e43'),(rollbackFreeze,'739f5e87f95f2ca2ad4e60f7b90ea00aa6384d74c1ae2fc8a4e60266e705ce62')];authorities=[];dependencyRows=[]
for path,h in freezePins:
 assert stream_hash(path)[0]==h;add(path,'exact complete runtime maps',h);f=json.loads(path.read_bytes());stage=pathlib.Path(f['stage']);authorities.append({'freezePath':str(path),'freezeSHA256':h,'stage':str(stage),'sourceDigest':f['sourceDigest'],'outputsDigest':f['outputsDigest'],'inputCount':len(f['inputs']),'outputCount':len(f['outputs'])})
 for scope,m in [('inputs',f['inputs']),('outputs',f['outputs'])]:
  for rel,bodySHA in m.items():
   p=stage/rel if scope=='inputs' else stage/'dist'/rel
   if p.suffix.lower() in {'.png','.wav','.ogg','.mp3','.jpg','.webp'}:dependencyRows.append([idx(roots,str(p.parent)),p.name,bodySHA,idx(roles,'held game media; body excluded')]);continue
   add(p,'default runtime code/support or exact capsule rollback reference',bodySHA)
 if path==defaultFreeze:
  assert f['inputs']['src/main.ts'].startswith('4a5');css=[rel for rel,h in f['inputs'].items() if rel.endswith('.css') and h.startswith('a84')];assert len(css)==1
  code=[rel for rel in f['outputs'] if not rel.startswith(('art/','audio/'))];assert len(code)==5
  authorities[-1]['defaultMainSHA256']=f['inputs']['src/main.ts'];authorities[-1]['defaultCueCSSPath']=css[0];authorities[-1]['defaultCueCSSSHA256']=f['inputs'][css[0]];authorities[-1]['fiveBuiltCodeBodies']={rel:f['outputs'][rel] for rel in code}
 if path==rollbackFreeze:
  for rel in ['src/main.ts','src/style.css','src/art.ts','src/arena.ts']:assert f['inputs'][rel] in members
  for rel,h in f['outputs'].items():
   if not rel.startswith(('art/','audio/')):assert h in members
  authorities[-1]['rollbackCodeAlreadyInExactCanonicalCe0fCapsule']=True
controlManifests=[(S/'target-clear-default-caller-author-r1/MANIFEST.json','5de445351d0849ae37ac3e8b91538219db1e3ad29fee980570a08aa206d5d782'),(S/'target-clear-default-compact-caller-author-r2/MANIFEST.json','e91d747bef6e88f475aee26d64b69ae9b679526d137c5476ca9d0731d2e6d766'),(S/'opening-turn-payoff-on-actual-caller-source-final-r2/MANIFEST.json','be3f1e7d5d1af0de51faa1f749075faee03aa0b282c2a14908307eb969bf0edc')];controls=[]
for path,h in controlManifests:
 assert stream_hash(path)[0]==h;add(path,'exact40-control authority manifest',h);m=json.loads(path.read_bytes())
 for b in m['bodies']:add(path.parent/b['name'],'exact actual40 controls',b['sha256']);controls.append({'path':str(path.parent/b['name']),'sha256':b['sha256']})
assert len(controls)==40
comparisons=[]
for name in actualNames:
 d=S/name;assert len(list(d.glob('*.jpg')))==8;pairs=[]
 for label in ['C0','C1','C2','C-cancelled','C-released','C-endTurn']:
  a=json.loads((d/('A-cue-'+label+'-OPAQUE-SAVE.json')).read_bytes())['raw'];b=json.loads((d/('B-cue-'+label+'-OPAQUE-SAVE.json')).read_bytes())['raw'];assert a==b;pairs.append({'label':label,'rawSHA256':sha(a.encode()),'rawBytes':len(a.encode())})
 comparisons.append({'originalRoot':str(d),'originalJPEGCount':8,'sixCompleteRawPairs':pairs})
assert comparisons[0]['sixCompleteRawPairs']==comparisons[1]['sixCompleteRawPairs']
unique={}
for root,rel,h,n,role,storage in rows:
 if storage=='newBlob':unique.setdefault(h,(pathlib.Path(roots[root])/rel,n))
gzipEstimate=0
for h,(path,n) in unique.items():
 encoder=zlib.compressobj(6,zlib.DEFLATED,31);decoder=zlib.decompressobj(31);original=hashlib.sha256();readback=hashlib.sha256();encodedBytes=0;readbackBytes=0
 with path.open('rb') as f:
  while b:=f.read(65536):
   original.update(b);c=encoder.compress(b);encodedBytes+=len(c);plain=decoder.decompress(c);readback.update(plain);readbackBytes+=len(plain)
 c=encoder.flush();encodedBytes+=len(c);plain=decoder.decompress(c)+decoder.flush();readback.update(plain);readbackBytes+=len(plain);assert decoder.eof and readbackBytes==n and original.hexdigest()==readback.hexdigest()==h;gzipEstimate+=encodedBytes
gatePaths=[S/(name+'/GATE.json') for name in reviewNames if (S/(name+'/GATE.json')).exists()]+[S/'opening-turn-payoff-on-source-independent-r1/GATE.json',S/'opening-turn-payoff-on-build-independent-r2/GATE.json',S/'opening-turn-payoff-on-actual-caller-source-independent-r2/GATE.json'];gates=[{'path':str(path),'sha256':stream_hash(path)[0]} for path in gatePaths]
plan={'status':'FINAL_SOURCE_PLAN_REQUIRES_ROOT_ARCHIVE_GRANT','scope':'Immutable default+prior opt-in spent-command cue actual/source/build/failed reviews and selected c4 rollback identity only. Evidence preservation; canonical runtime promotion deferred to future literal-clarity successor.','roots':roots,'roles':roles,'rowColumns':['rootIndex','relativeLeaf','sha256','originalBytes','roleIndex','storage'],'rows':rows,'existingCapsule':{'archive':{'path':str(archive),'sha256':'ce0f8f40bcf0f0b22e5e4d93eef3d4660662826e617900aba09ac208c148dc13'},'index':{'path':str(C/'INDEX.json'),'sha256':'115bbdb35d9cdff98503a3a5c63ced87e49a48d198194c9caa45268254bec0cf'},'externalBlobMemberRule':'blobs/<exact row SHA256> in exact canonical ce0f archive; validated against its pinned logical body index','noArchiveDuplication':True},'runtimeAuthorities':authorities,'exact40Controls':{'count':len(controls),'manifests':[{'path':str(p),'sha256':h,'bodies':len(json.loads(p.read_bytes())['bodies'])} for p,h in controlManifests],'bodyIdentityAuthority':'All40 original path/fullSHA identities remain in logical rows; complete original manifests and before/after audits retained.'},'actualComparisons':comparisons,'independentGateIdentities':gates,'finalDefaultVisualPins':visualPins,'externalDependencies':{'gameMediaColumns':['rootIndex','relativeLeaf','sha256','roleIndex'],'gameMediaRows':dependencyRows,'bodyReadOrCopied':False,'nodeModules':{'path':str(R/'node_modules'),'bodyExcluded':True,'authority':'Preserved frozen package-lock.json SHA in runtime maps, actual strict build gate; installed tree remains an external workflow dependency.'},'selfContainedRelease':False,'artHold':'Generated masters/native128 studies/tools/trials and other capsules remain in place and unselected; this cue evidence checkpoint does not select/promote art or runtime.'},'proposedArchive':{'workMiB':128,'reserveMiB':512,'physicalOutputCapBytes':16*1048576,'logicalOutputCapBytes':16*1048576,'freshFreeDiskMinimumBytes':17*1048576,'ownRSSCapBytes':24*1048576,'methodWholeCeilingSeconds':60,'newUniqueBodyCount':len(unique),'newUniqueOriginalBytes':sum(n for _,n in unique.values()),'perBodyGzipSumEstimateBytes':gzipEstimate,'estimateQualification':'Memory-only gzip original-byte readback estimate, excludes TAR/index/receipt overhead; actual full archive/hash/roundtrip/outputcap requires separate Root grant and independent review.'},'publicationPlan':{'candidateDestination':str(R/'reviews/opening-turn-payoff-default-2026-10-02'),'rootMayPublishOnlyAfterActualPreservationIndependentReview':True,'runtimeOrGitWritesAuthorizedByHelper':False,'noDeletionOrOriginalOverwrite':True},'sourceReadQualifications':{'noAtimeRequested':True,'permissionFallbackCount':sum(x['permissionFallback'] for x in observations),'capsuleIndexAndGzipEstimateAdditionalReadsMayUpdateAtime':'Metadata stream and estimate reads use standard read opens; atime preservation not claimed for them. File bytes/mtime not rewritten.'}}
out=(json.dumps(plan,separators=(',',':'))+'\n').encode();size=sum(p.stat().st_size for p in P.rglob('*') if p.is_file())+len(out);assert size+8192<=192*1024,(size,'Stop BEFORE plan writes; explicit cap needed');assert resource.getrusage(resource.RUSAGE_SELF).ru_maxrss<=24576;(P/'PLAN.json').write_bytes(out)
print(json.dumps({'sourceOnly':True,'planSHA256':sha(out),'planBytes':len(out),'logicalBeforeClosure':size,'originalLogicalRows':len(rows),'newUniqueBodies':len(unique),'existingCapsuleReferencedRows':sum(r[-1]=='existingCapsule' for r in rows),'gzipEstimateBytes':gzipEstimate,'ownMaxRSSKiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}))
