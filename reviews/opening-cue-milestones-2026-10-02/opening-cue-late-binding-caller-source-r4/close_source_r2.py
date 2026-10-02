"""Offline SOURCE closure: exact family inverse and byte-inclusive seal; never runtime."""
import pathlib,json,gzip,hashlib,base64,difflib,time,resource,os,sys
P=pathlib.Path(__file__).parent
artifacts={f.name:f.read_bytes() for f in P.iterdir()}
def sha(b):return hashlib.sha256(b).hexdigest()
def encode(v):return (json.dumps(v,separators=(',',':'))+'\n').encode()
def body(name,v):artifacts[name]=encode(v)
def line_patch(text,hunks,side):
 lines=text.splitlines(keepends=True);out=[];cursor=0
 for h in hunks:
  start=h[side+'LineStart'];old=h[side].splitlines(keepends=True);assert start>=cursor and ''.join(lines[start:start+len(old)])==h[side];out.extend([''.join(lines[cursor:start]),h['after' if side=='before' else 'before']]);cursor=start+len(old)
 return ''.join(out+[''.join(lines[cursor:])])
def raw(v):
 if not isinstance(v,dict):return v.encode()
 if 'base64' in v:return base64.b64decode(v['base64'],validate=True)
 b=artifacts[v['bodyRef']]
 if 'truncateBytes' in v:b=b[:v['truncateBytes']]
 if 'replacements' in v:
  for a,z in v['replacements']:b=b.replace(a.encode(),z.encode())
 if 'hunks' in v:b=line_patch(b.decode(),v['hunks'],'before').encode()
 assert len(b)==v['bytes'] and sha(b)==v['sha256'];return b
# Lossless origin coding reuses literal SOURCE bodies inside this same family.
# Complete logical R1 remains reconstructible without external origin bytes.
oldroot=pathlib.Path('/workspace/scratch/opening-cue-late-binding-caller-source-r1')
origin={f.name:({'base64':base64.b64encode(f.read_bytes()).decode()} if f.suffix=='.gz' else f.read_text()) for f in sorted(oldroot.iterdir())}
for name,value in list(origin.items()):
 original=raw(value);current=artifacts.get(name)
 if current is None:continue
 ref={'bodyRef':name,'bytes':len(original),'sha256':sha(original),'originalRepresentation':'base64' if isinstance(value,dict) else 'UTF8'}
 if current==original:pass
 elif current.startswith(original):ref['truncateBytes']=len(original)
 elif original==current.replace(b'opening-cue-late-binding-caller-source-r4',b'opening-cue-late-binding-caller-source-r1').replace(b'opening-cue-late-binding-caller-root-grant-r4',b'opening-cue-late-binding-caller-root-grant-r1').replace(b'opening-cue-late-binding-comparison-actual-r4',b'opening-cue-late-binding-comparison-actual-r1'):
  ref['replacements']=[[a+'r4',a+'r1'] for a in ['opening-cue-late-binding-caller-source-','opening-cue-late-binding-caller-root-grant-','opening-cue-late-binding-comparison-actual-']]
 elif not name.endswith('.gz'):
  A=current.decode().splitlines(keepends=True);B=original.decode().splitlines(keepends=True);h=[]
  for tag,i,j,k,l in difflib.SequenceMatcher(None,A,B,autojunk=False).get_opcodes():
   if tag!='equal':h.append({'beforeLineStart':i,'afterLineStart':k,'before':''.join(A[i:j]),'after':''.join(B[k:l])})
  ref['hunks']=h
 else:continue
 assert raw(ref)==original
 if len(gzip.compress(encode(ref),mtime=0))<len(gzip.compress(encode(value),mtime=0)):origin[name]=ref
body_bytes=gzip.compress(encode(origin),mtime=0);artifacts['R1-SNAPSHOT.json.gz']=body_bytes
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
manifest.update({'sourceRevision':'R4','sourceFamilyCapBytes':262144,'priorR2PendingClosureBytes':197543,'priorR3PendingClosureBytes':201302,'prior192KiBSizingFailuresRemainFailed':True,'retainedR1SourceSealSHA256':sha(raw(origin['SOURCE-SEAL.json'])),'exactEntireR1Snapshot':'R1-SNAPSHOT.json.gz','testedR1ForwardInverse':'R1-INVERSE.json.gz','testedFailedR2ForwardInverse':'R3-INVERSE.json.gz','failedR2Origin':'R2-ORIGIN-PINS.json','R1ReviewCollection':'R1-REVIEW-COLLECTION.json','UIControlTrace':'UI-SOURCE-TRACE.json','terminalCuePhaseQualified':True,'allOldSourcesReviewsUntouched':True,'originEncoding':'Lossless literal/body reference/truncation/exact line hunks; every resolved original body byte/hash verified; every literal source method remains counted'})
body('MANIFEST.json',manifest)
after={n:b for n,b in sorted(artifacts.items()) if n not in ['SOURCE-SEAL.json','R1-INVERSE.json.gz','R3-INVERSE.json.gz','R1-SNAPSHOT.json.gz']}
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
artifacts['R1-INVERSE.json.gz']=gzip.compress(encode(inverse_record),mtime=0)
# Exact failed R2→R4 domain, retaining every R2 source body. Closure sidecars
# are separately sealed to avoid recursive self-reference.
pins=json.loads(artifacts['R2-ORIGIN-PINS.json']);R2=pathlib.Path(pins['sourceRoot']);before2={r['name']:(R2/r['name']).read_bytes() for r in pins['files']}
for r in pins['files']:assert len(before2[r['name']])==r['bytes'] and sha(before2[r['name']])==r['sha256']
after2={**after,'R1-SNAPSHOT.json.gz':body_bytes};delta2=[]
for name in sorted(set(before2)|set(after2)):
 a=before2.get(name);b=after2.get(name)
 if a==b:continue
 row={'name':name,'beforeSHA256':sha(a) if a is not None else None,'afterSHA256':sha(b) if b is not None else None}
 if name=='R1-SNAPSHOT.json.gz':
  expanded={n:({'base64':base64.b64encode(raw(v)).decode()} if isinstance(v,dict) and v.get('originalRepresentation','base64')=='base64' else raw(v).decode()) for n,v in origin.items()}
  restored=gzip.compress(encode(expanded),mtime=0);assert restored==a
  replacements={n:v for n,v in origin.items() if isinstance(v,dict) and 'bodyRef' in v}
  encoded_from_before=json.loads(gzip.decompress(a));encoded_from_before.update(replacements);assert gzip.compress(encode(encoded_from_before),mtime=0)==b
  row['losslessOriginCodec']={'expandedCanonicalJSONSHA256':sha(encode(expanded)),'compressionLevel':9,'mtime':0,'replacementReferences':replacements}
 elif a is not None and b is not None and not name.endswith('.gz'):
  A=a.decode().splitlines(keepends=True);B=b.decode().splitlines(keepends=True);h=[]
  for tag,i,j,k,l in difflib.SequenceMatcher(None,A,B,autojunk=False).get_opcodes():
   if tag!='equal':h.append({'beforeLineStart':i,'afterLineStart':k,'before':''.join(A[i:j]),'after':''.join(B[k:l])})
  assert line_patch(a.decode(),h,'before').encode()==b and line_patch(b.decode(),h,'after').encode()==a;row['hunks']=h
 else:row.update({'beforeLiteral':({'base64':base64.b64encode(a).decode()} if name.endswith('.gz') else a.decode()) if a is not None else None,'afterLiteral':({'base64':base64.b64encode(b).decode()} if name.endswith('.gz') else b.decode()) if b is not None else None})
 delta2.append(row)
forward2=dict(before2);inverse2=dict(after2)
for row in delta2:
 name=row['name']
 for target,side in [(forward2,'before'),(inverse2,'after')]:
  other='after' if side=='before' else 'before';old=target.get(name);assert (sha(old) if old is not None else None)==row[side+'SHA256']
  if row[other+'SHA256'] is None:target.pop(name,None)
  elif 'losslessOriginCodec' in row:target[name]=body_bytes if side=='before' else restored
  else:target[name]=line_patch(old.decode(),row['hunks'],side).encode() if 'hunks' in row else raw(row[other+'Literal'])
assert forward2==after2 and inverse2==before2
artifacts['R3-INVERSE.json.gz']=gzip.compress(encode({'schema':'complete-failed-R2-source-forward-inverse-v1','originPins':'R2-ORIGIN-PINS.json','before':{n:{'bytes':len(b),'sha256':sha(b)} for n,b in before2.items()},'after':{n:{'bytes':len(b),'sha256':sha(b)} for n,b in after2.items()},'deltas':delta2,'forwardExact':True,'inverseExact':True,'qualification':'All failed R2 bodies roundtrip exactly. New R1/R3 inverse and source seal are closure sidecars, independently bound by the final inclusive seal. Origin compression is lossless, without source/body/cap exclusions.'}),mtime=0)
files=[{'name':n,'bytes':len(b),'sha256':sha(b)} for n,b in sorted(artifacts.items()) if n!='SOURCE-SEAL.json']
own_peak=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss;assert own_peak<=64*1024
seal={'schema':'source-family-seal-v1','sourceOnly':True,'runtimeEligible':False,'sealedForSourceReviewOnly':True,'candidateCBindingsComplete':False,'sourceFamilyCapBytes':262144,'familyBytesIncludingSeal':0,'files':files,'RootMethodGrantPresent':False,'callerOrRuntimeExecuted':False,'sourceClosureMethodOwnPeakRSSKiB':own_peak,'sourceClosureOwn64MiBPeakPassed':True,'qualification':'Exact ineligible focused R4 SOURCE template, preserving rejected R1 and sizing-failed unsealed R2/R3. C outputs/current metadata/engineering authority absent; rebinding requires another NEW reviewed source revision.'}
while True:
 n=sum(x['bytes'] for x in files)+len(encode(seal))
 if n==seal['familyBytesIncludingSeal']:break
 seal['familyBytesIncludingSeal']=n
assert n<=262144 and n<=24*1048576
body('SOURCE-SEAL.json',seal)
assert sum(len(b) for b in artifacts.values())==n
if '--preview' not in sys.argv:
 assert not (P/'SOURCE-SEAL.json').exists(),'Already sealed: author a NEW revision'
 for name,b in artifacts.items():(P/name).write_bytes(b)
 assert sum(f.stat().st_size for f in P.iterdir())==n
print(json.dumps({'previewOnly':'--preview' in sys.argv,'familyBytesIncludingSeal':n,'capBytes':262144,'sourceSealSHA256':sha(artifacts['SOURCE-SEAL.json']),'manifestSHA256':sha(artifacts['MANIFEST.json']),'driverSHA256':sha(artifacts['driver-cue.mjs']),'expectedSHA256':sha(artifacts['EXPECTED.json']),'R1ForwardInverseExact':True,'noRuntime':True}))
