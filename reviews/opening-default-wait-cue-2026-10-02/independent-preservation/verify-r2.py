import os,json,hashlib,pathlib,tarfile,resource,time
resource.setrlimit(resource.RLIMIT_DATA,(24*1048576,24*1048576))
P=pathlib.Path('/workspace/scratch/default-wait-cue-preservation-independent-r1');D=pathlib.Path('/workspace/Roguelike-deckbuilder/reviews/opening-default-wait-cue-2026-10-02');S=pathlib.Path('/workspace/scratch/target-wait-default-stage-r1')
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
archive=h(D/'evidence.tar.gz');assert archive=={'sha256':'dd9003b676ae49b8a81441f73dfaec51b4309206a3ce32716cb2c8c1fcda169f','bytes':1470640}
selected={};seen={};roundtrips=[]
with op(D/'evidence.tar.gz') as stream:
 with tarfile.open(fileobj=stream,mode='r|gz') as tf:
  first=next(iter(tf));assert first.name=='MANIFEST.json' and first.isfile() and first.size<150000
  with tf.extractfile(first) as f:body=f.read()
  manifestSHA=hashlib.sha256(body).hexdigest();assert manifestSHA=='bfc53a7026de9e48aeeac0c8e162577c7ee93e255b4205424a364083428a1849';m=json.loads(body);del body
  entries=m['logicalBodies'];excluded=m['excludedRetainedRuntimeMedia'];assert len(entries)==226 and len(excluded)==101 and not(set(entries)&set(excluded))
  hashNames={}
  for name,row in entries.items():
   path=pathlib.PurePosixPath(name);assert not path.is_absolute() and all(p not in ['..','.'] for p in path.parts) and pathlib.Path(row['originalPath']).is_absolute()
   hashNames.setdefault(row['sha256'],[]).append(name)
  assert len(hashNames)==209
  for member in tf:
   if member.name=='MANIFEST.json':continue
   assert member.isfile() and member.name.startswith('blobs/') and member.name.count('/')==1 and member.name not in seen and member.size<1048576
   digest=member.name[6:];assert digest in hashNames
   with tf.extractfile(member) as f:body=f.read()
   assert len(body)==member.size and hashlib.sha256(body).hexdigest()==digest
   for name in hashNames[digest]:
    row=entries[name];assert row['bytes']==member.size and h(pathlib.Path(row['originalPath']))=={'sha256':digest,'bytes':member.size}
    if name.endswith('/RUNTIME-FREEZE.json') or name.endswith('/GATE.json') or name.endswith('/FINAL-SEAL.json') or name.endswith('/EVIDENCE.json') or name.endswith('/VISUAL-RESULT.json') or name.endswith('-OPAQUE-SAVE.json') or name.endswith('/MANIFEST.json') or name.endswith('/SELECTED-READY-IDENTITIES.json') or name.endswith('/PRODUCER-JUDGMENT.json') or name=='evidence/target-wait-default-promotion-root-r1/RESULT.json':selected[name]=json.loads(body)
   seen[member.name]=member.size;roundtrips.append({'sha256':digest,'bytes':member.size,'logicalAliases':len(hashNames[digest])})
assert len(seen)==209 and set(n[6:] for n in seen)==set(hashNames)
f=selected['evidence/target-wait-default-author-r1/RUNTIME-FREEZE.json'];assert entries['evidence/target-wait-default-author-r1/RUNTIME-FREEZE.json']['sha256']=='e11a8295fe37dfbeb944d5943aeb109540371a376e5fd053b6adb6606c85f21e' and f['sourceDigest']==m['sourceDigest']=='1d5bf40a5f62c8ce3de1d087956e9190e98b3011cca1b1b7a5488fc8240bd4d3' and f['outputsDigest']==m['outputsDigest']=='30ddc549433f7b0b7611e41c0d4fd67e00a3aaa07dd61ba886cc43094f1e5464'
assert len(f['inputs'])==87 and len(f['outputs'])==56
runtime=[];omissions=[]
for kind,base in [('inputs',S),('outputs',S/'dist')]:
 for rel,digest in f[kind].items():
  logical='runtime/'+kind+'/'+rel;row=(entries|excluded)[logical];assert row['originalPath']==str(base/rel) and row['sha256']==digest
  media=pathlib.PurePosixPath(rel).suffix.lower() in ['.png','.wav'];assert (logical in excluded)==media
  got=h(base/rel);assert got=={'sha256':digest,'bytes':row['bytes']};runtime.append({'kind':kind,'path':rel,**got,'included':not media})
  if media:omissions.append({'logical':logical,**row,'originalBodyVerified':True,'stillNeeded':True})
assert len(runtime)==143 and len(omissions)==101 and sum(x['included'] for x in runtime)==42 and len(set(entries|excluded))==327
# All selected evidence directories are complete; no retained originals disappear from the capsule mapping.
roots=sorted({name.split('/')[1] for name in entries if name.startswith('evidence/')});completeness=[]
for root in roots:
 actual={str(p.relative_to(pathlib.Path('/workspace/scratch')/root)) for p in (pathlib.Path('/workspace/scratch')/root).rglob('*') if p.is_file()};mapped={name[len('evidence/'+root+'/'):] for name in entries if name.startswith('evidence/'+root+'/')};assert actual==mapped;completeness.append({'root':root,'allOriginalFilesIncluded':len(actual)})
# Archived nested control manifests bind their complete original packet bodies.
for name,man in selected.items():
 if name.endswith('/MANIFEST.json') and ('bodies' in man or 'files' in man):
  prefix=name[:-len('MANIFEST.json')]
  records=man['bodies'] if 'bodies' in man else man['files']
  rows=[{'name':n,**row} for n,row in records.items()] if isinstance(records,dict) else records
  for row in rows:
   logical=prefix+row['name'] if 'name' in row else next(n for n,ent in entries.items() if ent['originalPath']==row['path'])
   ent=entries[logical];assert row['sha256']==ent['sha256'] and row['bytes']==ent['bytes']
gates={}
expected={'evidence/target-wait-default-independent-r1/GATE.json':'40e9f31f57e0b25dae0928021adbc6a8e11f0851713c331f07baa15a2e9bbb77','evidence/target-wait-default-caller-independent-r1/GATE.json':'e9985fb56119d0ff74fee645ee87e6c88efed656b286b0ece778f55c908ef3f9','evidence/target-wait-default-actual-technical-independent-r1/GATE.json':'cd053fbdb084cd4f7a0b26962263d246e91a19319db325a97fcae25a90947a27','evidence/target-wait-default-actual-visual-independent-r1/GATE.json':'6767ff32bc264f04a495774766f2e539486bf0924c1d61ea1f4d07504b13a44b'}
for name,digest in expected.items():assert entries[name]['sha256']==digest;gates[name]={'sha256':digest,'decision':selected[name].get('decision',selected[name].get('status'))}
for name in ['evidence/target-wait-default-actual-gameplay-independent-r1/FINAL-SEAL.json','evidence/target-wait-default-actual-gameplay-independent-r1/EVIDENCE.json']:assert name in selected;gates[name]={'sha256':entries[name]['sha256'],'keys':sorted(selected[name])}
v=selected['evidence/target-wait-default-comparison-actual-r1/VISUAL-RESULT.json'];assert v['completed'] and v['coverageComplete'] and len(v['contexts'])==2 and len(v['canonicalComparisons'])==6
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
assert len(jpeg)==4 and sum(x['bytes'] for x in jpeg)==776612
rollback=selected['evidence/target-wait-default-promotion-root-r1/SELECTED-READY-IDENTITIES.json'];judgment=selected['evidence/target-wait-default-promotion-root-r1/PRODUCER-JUDGMENT.json'];promotion=selected['evidence/target-wait-default-promotion-root-r1/RESULT.json'];oldFreeze=j(pathlib.Path('/workspace/scratch/ready-default-build-root-r1/RUNTIME-FREEZE.json'))
assert rollback['inputs']==oldFreeze['inputs'] and rollback['outputs']==oldFreeze['outputs'] and rollback['sourceDigest']==oldFreeze['sourceDigest']=='251c4fd4fdcce5bbbc39bf438155277ea440c724bd803adf10cd07b5ffa89a65' and rollback['outputsDigest']==oldFreeze['outputsDigest']=='2c664aa389221f8570e1f6cebd1ae63f0784d2cba95a7fcc267c3743096a823c'
assert judgment['decision']=='SELECT_ONLY_DEFAULT_NAMED_TARGET_WAIT_CUE' and judgment['newSourceDigest']==f['sourceDigest'] and judgment['newOutputsDigest']==f['outputsDigest'] and promotion['normal'] and promotion['canonicalInputs']==f['inputs'] and promotion['canonicalOutputs']==f['outputs'] and promotion['sourceDigest']==f['sourceDigest'] and promotion['outputsDigest']==f['outputsDigest'] and not promotion['mediaBodyWrites'] and not promotion['retirement']
rollbackBodies=[]
for rel,pin in promotion['retainedOldSources'].items():
 logical='evidence/target-wait-default-promotion-root-r1/selected-ready-baseline/'+rel;assert entries[logical]['sha256']==pin==rollback['inputs'][rel];rollbackBodies.append({'logical':logical,**entries[logical]})
for rel,pin in promotion['retainedOldNonmedia'].items():
 logical='evidence/target-wait-default-promotion-root-r1/selected-ready-outputs/'+rel;assert entries[logical]['sha256']==pin==rollback['outputs'][rel];rollbackBodies.append({'logical':logical,**entries[logical]})
assert len(promotion['retainedOldSources'])==2 and len(promotion['retainedOldNonmedia'])==5
for path,pin in judgment['reviewPins'].items():
 logical=next(n for n,row in entries.items() if row['originalPath']==path);assert entries[logical]['sha256']==pin
assert entries['evidence/target-wait-default-actual-gameplay-independent-r1/FINAL-SEAL.json']['sha256']=='ae59e2f2c526fb084fdebd09c913b4b7eeb971e5a64bcd0e643332f4d83ea875'
mutablePaths=[]
for rel in ['src/main.ts','src/tactile-hand.ts']:
 row=entries['selected-baseline/'+rel];assert row['originalPath']=='/workspace/Roguelike-deckbuilder/'+rel and row['sha256']==f['inputs'][rel] and h(S/rel)=={'sha256':row['sha256'],'bytes':row['bytes']};mutablePaths.append({'logical':'selected-baseline/'+rel,**row,'fixedFrozenCheckpointPath':str(S/rel),'qualification':'OriginalPath is mutable working copy after this checkpoint. Exact blob and fixed frozen stage retain these bytes; future authorized edits do not retroactively invalidate checkpoint identity.'})
# Current canonical bodies already selected by Root match this exact frozen checkpoint.
for kind,base in [('inputs',pathlib.Path('/workspace/Roguelike-deckbuilder')),('outputs',pathlib.Path('/workspace/Roguelike-deckbuilder/dist'))]:
 for rel,pin in f[kind].items():assert h(base/rel)['sha256']==pin
olderCapsule=h(pathlib.Path('/workspace/Roguelike-deckbuilder/reviews/opening-target-wait-cue-2026-10-02/evidence.tar.gz'));assert olderCapsule=={'sha256':'33a7d665c213e7710e19aa4710e4c71788e614e6034911ab6ea4dbfbef170abf','bytes':1452213}
summary=j(D/'PRESERVATION.json');assert summary['archiveSHA256']==archive['sha256'] and summary['manifestSHA256']==manifestSHA and summary['logicalBodies']==226 and summary['uniqueBodies']==209 and summary['excludedNeededMediaBodies']==101 and summary['noRetirement'] and summary['defaultCueSelected']
rootGuard=pathlib.Path('/workspace/scratch/default-wait-cue-preservation-guard-root-r1');rg=j(rootGuard/'RESULT.json');ra=j(rootGuard/'ADMISSION.json');assert ra['admitted'] and ra['work']==64*1048576 and ra['reserve']==512*1048576 and rg['exit_code']==0 and rg['failure'] is None and rg['memory_events_before']==rg['memory_events_after']
rpts=[rg['initial']]+rg['samples']+[rg['final']]
for x in rpts:assert x['headroom']>=512*1048576 and x['current']-rg['initial']['current']<=64*1048576 and x['free']>=1048576
assert h(D/'evidence.tar.gz')==archive
vm=next(int(x.split()[1])*1024 for x in pathlib.Path('/proc/self/status').read_text().splitlines() if x.startswith('VmHWM:'));assert vm<=24*1048576
proof={'decision':'ACCEPT_EXACT_SELECTED_DEFAULT_CHECKPOINT_PRESERVATION_WITH_NEEDED_MEDIA_OMISSIONS','archive':archive,'manifestSHA256':manifestSHA,'counts':{'logical':226,'uniqueBlobs':209,'excludedNeededMedia':101,'runtimeInputs':87,'runtimeOutputs':56,'includedRuntimeCode':42,'actualRawPairs':6,'originalCaptures':4},'roundtripBlobs':roundtrips,'allLogicalOriginalBytesEqual':True,'logicalPathsUniqueAndSafe':True,'completeSelectedEvidenceDirectories':completeness,'nestedControlManifestsExact':True,'runtimeMaps':runtime,'excludedNeededOriginals':omissions,'reviewGates':gates,'completeActualRawPairs':pairs,'includedOriginalCaptures':jpeg,'sourceDigest':f['sourceDigest'],'outputsDigest':f['outputsDigest'],'currentCanonical87Inputs56OutputsMatchCheckpoint':True,'rollback':{'oldSourceDigest':rollback['sourceDigest'],'oldOutputsDigest':rollback['outputsDigest'],'completeOldMapsMatchFrozenReady':True,'retainedTwoSourcesFiveNonmediaOutputs':rollbackBodies,'producerJudgmentReviewPinsExact':True,'noRetirement':True},'mutableWorkingCopyOriginalPaths':mutablePaths,'previousOptInCapsuleUnchanged':olderCapsule,'rootPreservationGuard':{'result':h(rootGuard/'RESULT.json'),'admission':h(rootGuard/'ADMISSION.json'),'points':len(rpts),'maxAggregateDelta':max(x['current']-rg['initial']['current'] for x in rpts),'minHeadroom':min(x['headroom'] for x in rpts),'eventsUnchanged':True,'normalRc0':True},'preservationSummary':h(D/'PRESERVATION.json'),'README':h(D/'README.md'),'scope':'Exact preservation only. Selected default named-wait source/build/caller/actual and three separate actual reviews plus Root producer/rollback records retained with original method failures. This archives the already selected checkpoint; no new art, human-fun, repair, release, retirement or cleanup acceptance. Needed PNG/WAV original paths remain indispensable; not a self-contained release. Full binary hashes are identity checks, no image decoding/viewing. Root workflow guard closes finite child group but does not prove global backend/unknown actor absence.','preservedReviewerMethodFailure':'Original GUARD rc1 before proof assumed all nested manifest files fields were dictionaries; visual review uses an absolute-path array. Corrected verifier-r2 normalizes dictionary/array forms and binds both to exact original archive mappings. No archive/source/runtime change.', 'method':'NOATIME|NOFOLLOW streaming tar reader, no extraction or large copies, stream32KiB original hashes, readonly sources/media/archive. No Node/Git/browser/build/backend/images/native action. Only new proof packet written.','ownVmHWM':vm,'utcNs':time.time_ns()}
wr('PROOF.json',proof)
print(json.dumps({'decision':proof['decision'],'proof':h(P/'PROOF.json'),'ownVmHWM':vm,'counts':proof['counts']}))
