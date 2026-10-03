import os,json,hashlib,pathlib,tarfile,resource,time
resource.setrlimit(resource.RLIMIT_DATA,(24*1048576,24*1048576))
P=pathlib.Path('/workspace/scratch/target-wait-cue-preservation-independent-r1');D=pathlib.Path('/workspace/Roguelike-deckbuilder/reviews/opening-target-wait-cue-2026-10-02');S=pathlib.Path('/workspace/scratch/target-wait-cue-stage-r1')
def op(p):return os.fdopen(os.open(p,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW),'rb')
def h(p):
 z=hashlib.sha256();n=0
 with op(p) as f:
  for b in iter(lambda:f.read(32768),b''):z.update(b);n+=len(b)
 return {'sha256':z.hexdigest(),'bytes':n}
def j(p):
 with op(p) as f:return json.load(f)
def wr(name,data):
 with (P/name).open('x') as f:json.dump(data,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
archive=h(D/'evidence.tar.gz');assert archive=={'sha256':'33a7d665c213e7710e19aa4710e4c71788e614e6034911ab6ea4dbfbef170abf','bytes':1452213}
selected={};seen={};roundtrips=[]
with op(D/'evidence.tar.gz') as stream:
 with tarfile.open(fileobj=stream,mode='r|gz') as tf:
  first=next(iter(tf));assert first.name=='MANIFEST.json' and first.isfile() and first.size<150000
  with tf.extractfile(first) as f:body=f.read()
  manifestSHA=hashlib.sha256(body).hexdigest();assert manifestSHA=='417460625edb417b9be0a792f58adb4112a88cad869694e3f4c17d313fab4eef';m=json.loads(body);del body
  entries=m['logicalBodies'];excluded=m['excludedRetainedRuntimeMedia'];assert len(entries)==253 and len(excluded)==101 and not(set(entries)&set(excluded))
  hashNames={}
  for name,row in entries.items():
   path=pathlib.PurePosixPath(name);assert not path.is_absolute() and all(p not in ['..','.'] for p in path.parts) and pathlib.Path(row['originalPath']).is_absolute()
   hashNames.setdefault(row['sha256'],[]).append(name)
  assert len(hashNames)==236
  for member in tf:
   if member.name=='MANIFEST.json':continue
   assert member.isfile() and member.name.startswith('blobs/') and member.name.count('/')==1 and member.name not in seen and member.size<1048576
   digest=member.name[6:];assert digest in hashNames
   with tf.extractfile(member) as f:body=f.read()
   assert len(body)==member.size and hashlib.sha256(body).hexdigest()==digest
   for name in hashNames[digest]:
    row=entries[name];assert row['bytes']==member.size and h(pathlib.Path(row['originalPath']))=={'sha256':digest,'bytes':member.size}
    if name.endswith('/RUNTIME-FREEZE.json') or name.endswith('/GATE.json') or name.endswith('/FINAL-SEAL.json') or name.endswith('/EVIDENCE.json') or name.endswith('/VISUAL-RESULT.json') or '/OPAQUE-SAVE-' in name or name.endswith('/MANIFEST.json'):selected[name]=json.loads(body)
   seen[member.name]=member.size;roundtrips.append({'sha256':digest,'bytes':member.size,'logicalAliases':len(hashNames[digest])})
assert len(seen)==236 and set(n[6:] for n in seen)==set(hashNames)
f=selected['evidence/target-wait-cue-build-author-r1/RUNTIME-FREEZE.json'];assert entries['evidence/target-wait-cue-build-author-r1/RUNTIME-FREEZE.json']['sha256']=='255d83b8d48c234e81148c53475d8bf3b6f0969670983bcd5debdcb7775d0aa4' and f['sourceDigest']==m['sourceDigest']=='df26eacd3988cb8aacebd95747e07edc3f1659bd1bc3b4baa39e5a0ebbcc5aa9' and f['outputsDigest']==m['outputsDigest']=='b30f08787905fc59acc2f44277e352b879362e4aa0bff50a5f76929e5f8dbf6a'
assert len(f['inputs'])==87 and len(f['outputs'])==56
runtime=[];omissions=[]
for kind,base in [('inputs',S),('outputs',S/'dist')]:
 for rel,digest in f[kind].items():
  logical='runtime/'+kind+'/'+rel;row=(entries|excluded)[logical];assert row['originalPath']==str(base/rel) and row['sha256']==digest
  media=pathlib.PurePosixPath(rel).suffix.lower() in ['.png','.wav'];assert (logical in excluded)==media
  got=h(base/rel);assert got=={'sha256':digest,'bytes':row['bytes']};runtime.append({'kind':kind,'path':rel,**got,'included':not media})
  if media:omissions.append({'logical':logical,**row,'originalBodyVerified':True,'stillNeeded':True})
assert len(runtime)==143 and len(omissions)==101 and sum(x['included'] for x in runtime)==42 and len(set(entries|excluded))==354
# All selected evidence directories are complete; no retained originals disappear from the capsule mapping.
roots=['blocked-target-feedback-source-author-r1','blocked-target-feedback-source-independent-r1','target-wait-cue-build-author-r1','target-wait-cue-build-independent-r1','target-wait-cue-caller-author-r1','target-wait-cue-caller-independent-r1','target-wait-cue-comparison-actual-r1','target-wait-cue-actual-technical-independent-r1','target-wait-cue-actual-gameplay-independent-r1','target-wait-cue-actual-visual-independent-r1','target-wait-cue-native-grant-guard-root-r1'];completeness=[]
for root in roots:
 actual={str(p.relative_to(pathlib.Path('/workspace/scratch')/root)) for p in (pathlib.Path('/workspace/scratch')/root).rglob('*') if p.is_file()};mapped={name[len('evidence/'+root+'/'):] for name in entries if name.startswith('evidence/'+root+'/')};assert actual==mapped;completeness.append({'root':root,'allOriginalFilesIncluded':len(actual)})
# Archived nested control manifests bind their complete original packet bodies.
for name,man in selected.items():
 if name.endswith('/MANIFEST.json') and 'bodies' in man:
  prefix=name[:-len('MANIFEST.json')]
  for row in man['bodies']:
   ent=entries[prefix+row['name']];assert row['sha256']==ent['sha256'] and row['bytes']==ent['bytes']
gates={}
expected={'evidence/blocked-target-feedback-source-independent-r1/GATE.json':'65c7b5f3c9ef4239e79f44fa384a08ecd7d4777954a0999c2ad0ff36284ac450','evidence/target-wait-cue-build-independent-r1/GATE.json':'98b9fbb4d79bf77b154dd8e7908ee2375b992ae7901b921b179702b89c409ff5','evidence/target-wait-cue-caller-independent-r1/GATE.json':'0dc899c2326849a1e0af9b1a3e6b5b37ab182dabe0c576c2d92d947e0dac2a53','evidence/target-wait-cue-actual-technical-independent-r1/GATE.json':'9a5cf21cf8cea4ee05b8bd268e3c31bf46cb13e4939da0d68c538015b5bb3126','evidence/target-wait-cue-actual-visual-independent-r1/GATE.json':'e687bd8afb2c6321ecd069ee9ef68ee8c042c6d74757af4398de0e4ada264f25'}
for name,digest in expected.items():assert entries[name]['sha256']==digest;gates[name]={'sha256':digest,'decision':selected[name]['decision']}
for name in ['evidence/target-wait-cue-actual-gameplay-independent-r1/FINAL-SEAL.json','evidence/target-wait-cue-actual-gameplay-independent-r1/EVIDENCE.json']:assert name in selected;gates[name]={'sha256':entries[name]['sha256'],'keys':sorted(selected[name])}
v=selected['evidence/target-wait-cue-comparison-actual-r1/VISUAL-RESULT.json'];assert v['completed'] and v['coverageComplete'] and len(v['contexts'])==2 and len(v['canonicalComparisons'])==6
pairs=[];saved={};jpeg=[]
for ctx in v['contexts']:
 assert ctx['holdOutcome']=='COMMITTED_ONCE' and ctx['noQueuedActionAfterRelease'] and ctx['holdTransitionCovered'] and ctx['context']=='CLOSED'
 saved[ctx['name']]={}
 for label,cp in ctx['checkpoints'].items():
  original=cp['path'];logical=next(n for n,row in entries.items() if row['originalPath']==original);opaque=selected[logical];assert opaque['raw']==cp['raw'] and opaque['observedOnly'] and hashlib.sha256(cp['raw'].encode()).hexdigest()==cp['sha256'];saved[ctx['name']][label]=cp['raw']
for label in ['C0','C1','C2','C-firstDrop','C-secondOutcome','C-normalized']:
 assert saved['A-hold-release'][label]==saved['B-hold-release'][label];pairs.append({'label':label,'completeRawEqual':True,'sha256':hashlib.sha256(saved['A-hold-release'][label].encode()).hexdigest()})
for cap in v['captures']:
 logical=next(n for n,row in entries.items() if row['originalPath']==cap['path']);row=entries[logical];assert row['sha256']==cap['sha256'] and row['bytes']==cap['bytes'] and cap['format']=='jpeg' and cap['quality']==80 and not cap['phaseCertified'];jpeg.append({'logical':logical,**row,'phaseCertified':False})
assert len(jpeg)==4 and sum(x['bytes'] for x in jpeg)==776624
summary=j(D/'PRESERVATION.json');assert summary['archiveSHA256']==archive['sha256'] and summary['manifestSHA256']==manifestSHA and summary['logicalBodies']==253 and summary['uniqueBodies']==236 and summary['excludedNeededMediaBodies']==101 and summary['noDefaultPromotionOrRetirement']
rootGuard=pathlib.Path('/workspace/scratch/target-wait-cue-preservation-guard-root-r1');rg=j(rootGuard/'RESULT.json');ra=j(rootGuard/'ADMISSION.json');assert ra['admitted'] and ra['work']==64*1048576 and ra['reserve']==512*1048576 and rg['exit_code']==0 and rg['failure'] is None and rg['memory_events_before']==rg['memory_events_after']
rpts=[rg['initial']]+rg['samples']+[rg['final']]
for x in rpts:assert x['headroom']>=512*1048576 and x['current']-rg['initial']['current']<=64*1048576 and x['free']>=1048576
assert h(D/'evidence.tar.gz')==archive
vm=next(int(x.split()[1])*1024 for x in pathlib.Path('/proc/self/status').read_text().splitlines() if x.startswith('VmHWM:'));assert vm<=24*1048576
proof={'decision':'ACCEPT_EXACT_OPT_IN_CUE_PRESERVATION_WITH_NEEDED_MEDIA_OMISSIONS','archive':archive,'manifestSHA256':manifestSHA,'counts':{'logical':253,'uniqueBlobs':236,'excludedNeededMedia':101,'runtimeInputs':87,'runtimeOutputs':56,'includedRuntimeCode':42,'actualRawPairs':6,'originalCaptures':4},'roundtripBlobs':roundtrips,'allLogicalOriginalBytesEqual':True,'logicalPathsUniqueAndSafe':True,'completeSelectedEvidenceDirectories':completeness,'nestedControlManifestsExact':True,'runtimeMaps':runtime,'excludedNeededOriginals':omissions,'reviewGates':gates,'completeActualRawPairs':pairs,'includedOriginalCaptures':jpeg,'sourceDigest':f['sourceDigest'],'outputsDigest':f['outputsDigest'],'rootPreservationGuard':{'result':h(rootGuard/'RESULT.json'),'admission':h(rootGuard/'ADMISSION.json'),'points':len(rpts),'maxAggregateDelta':max(x['current']-rg['initial']['current'] for x in rpts),'minHeadroom':min(x['headroom'] for x in rpts),'eventsUnchanged':True,'normalRc0':True},'preservationSummary':h(D/'PRESERVATION.json'),'README':h(D/'README.md'),'scope':'Exact preservation only. Opt-in named-wait source/build/caller/actual and three separate actual reviews retained with original method failures; no new default, art, runtime, human-fun, repair, release, retirement or cleanup acceptance. Needed PNG/WAV original paths remain indispensable; not a self-contained release. Full binary hashes are identity checks, no image decoding/viewing. Root workflow guard closes finite child group but does not prove global backend/unknown actor absence.','method':'NOATIME|NOFOLLOW streaming tar reader, no extraction or large copies, stream32KiB original hashes, readonly sources/media/archive. No Node/Git/browser/build/backend/images/native action. Only new proof packet written.','ownVmHWM':vm,'utcNs':time.time_ns()}
wr('PROOF.json',proof)
print(json.dumps({'decision':proof['decision'],'proof':h(P/'PROOF.json'),'ownVmHWM':vm,'counts':proof['counts']}))
