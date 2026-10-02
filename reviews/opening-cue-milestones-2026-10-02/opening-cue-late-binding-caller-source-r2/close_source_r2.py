"""Offline SOURCE closure: exact family inverse and byte-inclusive seal; never runtime."""
import pathlib,json,gzip,hashlib,base64,difflib,time,resource,os,sys
P=pathlib.Path(__file__).parent
artifacts={f.name:f.read_bytes() for f in P.iterdir()}
def sha(b):return hashlib.sha256(b).hexdigest()
def encode(v):return (json.dumps(v,separators=(',',':'))+'\n').encode()
def body(name,v):artifacts[name]=encode(v)
def raw(v):return base64.b64decode(v['base64'],validate=True) if isinstance(v,dict) else v.encode()
origin=json.loads(gzip.decompress((P/'R1-SNAPSHOT.json.gz').read_bytes()))
oldseal=json.loads(origin['SOURCE-SEAL.json']);assert oldseal['familyBytesIncludingSeal']==100761
for ref in oldseal['files']:b=raw(origin[ref['name']]);assert len(b)==ref['bytes'] and sha(b)==ref['sha256']
assert sum(len(raw(x)) for x in origin.values())==100761
reviews=[]
for role in ['visual','gameplay','technical']:
 directory=pathlib.Path('/workspace/scratch/opening-cue-late-binding-'+role+'-source-review-r1')
 files=[]
 for name in ['REVIEW.md','GATE.json']:
  f=directory/name
  if f.exists():files.append({'path':str(f),'bytes':f.stat().st_size,'sha256':sha(f.read_bytes())})
 assert files;reviews.append({'role':role,'files':files})
addendum=pathlib.Path('/workspace/scratch/opening-cue-late-binding-technical-terminal-addendum-r1')
addendum_refs=[{'path':str(addendum/n),'bytes':(addendum/n).stat().st_size,'sha256':sha((addendum/n).read_bytes())} for n in ['REVIEW.md','GATE.json']]
assert addendum_refs[1]['sha256']=='c654030bd9f1817c1a0875b93d7bf894d0b0ad84eafdc933a194ef38022fa9d8'
body('R1-REVIEW-COLLECTION.json',{'sourceOnly':True,'originalSourceSealSHA256':sha(raw(origin['SOURCE-SEAL.json'])),'allThreeR1RolesCollectedBeforeR2Seal':True,'reviews':reviews,'technicalTerminalAddendum':addendum_refs,'findings':'Gameplay rejects unconditional terminal DOM removal; visual final report retracts preliminary missing-disclosure finding after complete hunt-entry closure tracing; technical original accepts ineligible template, separate addendum corrects missed terminal assertion defect. All R1 bytes and findings remain retained.'})
resource_receipt={'sourceOnly':True,'runtimeEligible':False,'workBytes':64*1048576,'reserveBytes':512*1048576,'ownDiskCapBytes':24*1048576,'sampleUTCNS':time.time_ns(),'currentSharedCgroupBytes':int(pathlib.Path('/sys/fs/cgroup/memory.current').read_text()),'maximumBytes':int(pathlib.Path('/sys/fs/cgroup/memory.max').read_text()),'freeDiskBytes':os.statvfs(P).f_bavail*os.statvfs(P).f_frsize,'memoryEvents':pathlib.Path('/sys/fs/cgroup/memory.events').read_text(),'sourceOwnPeakRSSKiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'callerHelperBrowserServerBuildExecuted':False,'qualification':'SOURCE point samples and per-method peak RSS; shared samples neither continuous nor exclusive. Driver60/supervisor90 and all runtime caps unchanged.'}
assert resource_receipt['maximumBytes']-resource_receipt['currentSharedCgroupBytes']>=576*1048576
assert resource_receipt['freeDiskBytes']>=24*1048576
body('SOURCE-RESOURCE-RECEIPT.json',resource_receipt)
manifest=json.loads(raw(origin['MANIFEST.json']));manifest['bodies']=[{'name':name,'bytes':(P/name).stat().st_size,'sha256':sha((P/name).read_bytes())} for name in ['driver-cue.mjs','supervise-cue.py','runtime-guard-cue.mjs','runtime_guard_cue.py','EXPECTED.json','PROTOCOL.json']]
manifest.update({'sourceRevision':'R2','retainedR1SourceSealSHA256':sha(raw(origin['SOURCE-SEAL.json'])),'exactEntireR1Snapshot':'R1-SNAPSHOT.json.gz','testedR1ForwardInverse':'R2-INVERSE.json.gz','R1ReviewCollection':'R1-REVIEW-COLLECTION.json','UIControlTrace':'UI-SOURCE-TRACE.json','terminalCuePhaseQualified':True,'allOldSourcesReviewsUntouched':True})
body('MANIFEST.json',manifest)
after={n:b for n,b in sorted(artifacts.items()) if n not in ['SOURCE-SEAL.json','R2-INVERSE.json.gz','R1-SNAPSHOT.json.gz']}
def transform(text,hunks,side):
 lines=text.splitlines(keepends=True);out=[];cursor=0
 for h in hunks:
  start=h[side+'LineStart'];old=h[side].splitlines(keepends=True);assert start>=cursor and ''.join(lines[start:start+len(old)])==h[side];out.extend([''.join(lines[cursor:start]),h['after' if side=='before' else 'before']]);cursor=start+len(old)
 out.append(''.join(lines[cursor:]));return ''.join(out)
deltas=[]
for name in sorted(set(origin)|set(after)):
 a=raw(origin[name]) if name in origin else None;b=after.get(name)
 if a==b:continue
 if a is not None and b is not None and not name.endswith('.gz'):
  A=a.decode().splitlines(keepends=True);B=b.decode().splitlines(keepends=True);hunks=[]
  for tag,i,j,k,l in difflib.SequenceMatcher(None,A,B,autojunk=False).get_opcodes():
   if tag!='equal':hunks.append({'beforeLineStart':i,'afterLineStart':k,'before':''.join(A[i:j]),'after':''.join(B[k:l])})
  assert transform(a.decode(),hunks,'before').encode()==b and transform(b.decode(),hunks,'after').encode()==a
  change={'hunks':hunks}
 else:change={'beforeLiteral':({'base64':base64.b64encode(a).decode()} if name.endswith('.gz') else a.decode()) if a is not None else None,'afterLiteral':({'base64':base64.b64encode(b).decode()} if name.endswith('.gz') else b.decode()) if b is not None else None}
 deltas.append({'name':name,'beforeSHA256':sha(a) if a is not None else None,'afterSHA256':sha(b) if b is not None else None,**change})
forward={n:raw(v) for n,v in origin.items()};inverse=dict(after)
for d in deltas:
 n=d['name']
 for target,side in [(forward,'before'),(inverse,'after')]:
  other='after' if side=='before' else 'before';old=target.get(n);assert (sha(old) if old is not None else None)==d[side+'SHA256']
  if d[other+'SHA256'] is None:target.pop(n,None)
  else:target[n]=transform(old.decode(),d['hunks'],side).encode() if 'hunks' in d else raw(d[other+'Literal'])
assert forward==after and inverse=={n:raw(v) for n,v in origin.items()}
inverse_record={'schema':'complete-source-forward-inverse-v1','origin':'R1-SNAPSHOT.json.gz','oldRoot':'/workspace/scratch/opening-cue-late-binding-caller-source-r1','newRoot':str(P),'originSourceSealSHA256':sha(raw(origin['SOURCE-SEAL.json'])),'qualification':'Exact entire R1↔R2 preseal transformation. R1-SNAPSHOT is the literal origin sidecar; this inverse and new SOURCE-SEAL are closure sidecars excluded from recursive self-reference. New seal independently binds every sidecar byte. Original R1 paths are not removed or mutated.','before':{n:{'bytes':len(raw(v)),'sha256':sha(raw(v))} for n,v in origin.items()},'after':{n:{'bytes':len(b),'sha256':sha(b)} for n,b in after.items()},'deltas':deltas,'forwardExact':True,'inverseExact':True}
artifacts['R2-INVERSE.json.gz']=gzip.compress(encode(inverse_record),mtime=0)
files=[{'name':n,'bytes':len(b),'sha256':sha(b)} for n,b in sorted(artifacts.items()) if n!='SOURCE-SEAL.json']
seal={'schema':'source-family-seal-v1','sourceOnly':True,'runtimeEligible':False,'sealedForSourceReviewOnly':True,'candidateCBindingsComplete':False,'sourceFamilyCapBytes':196608,'familyBytesIncludingSeal':0,'files':files,'RootMethodGrantPresent':False,'callerOrRuntimeExecuted':False,'qualification':'Exact ineligible focused R2 SOURCE template, preserving rejected R1. C outputs/current metadata/engineering authority absent; rebinding requires another NEW reviewed source revision.'}
while True:
 n=sum(x['bytes'] for x in files)+len(encode(seal))
 if n==seal['familyBytesIncludingSeal']:break
 seal['familyBytesIncludingSeal']=n
assert n<=196608 and n<=24*1048576
body('SOURCE-SEAL.json',seal)
assert sum(len(b) for b in artifacts.values())==n
if '--preview' not in sys.argv:
 assert not (P/'SOURCE-SEAL.json').exists(),'Already sealed: author a NEW revision'
 for name,b in artifacts.items():(P/name).write_bytes(b)
 assert sum(f.stat().st_size for f in P.iterdir())==n
print(json.dumps({'previewOnly':'--preview' in sys.argv,'familyBytesIncludingSeal':n,'capBytes':196608,'sourceSealSHA256':sha(artifacts['SOURCE-SEAL.json']),'manifestSHA256':sha(artifacts['MANIFEST.json']),'driverSHA256':sha(artifacts['driver-cue.mjs']),'expectedSHA256':sha(artifacts['EXPECTED.json']),'R1ForwardInverseExact':True,'noRuntime':True}))
