import os,json,hashlib,pathlib,tarfile,gzip,resource,time
resource.setrlimit(resource.RLIMIT_DATA,(24*1048576,24*1048576))
P=pathlib.Path('/workspace/scratch/target-clear-rejection-preservation-independent-r1');R=pathlib.Path('/workspace/Roguelike-deckbuilder');S=pathlib.Path('/workspace/scratch');D=R/'reviews/opening-target-clear-rejected-2026-10-02'
def op(p):return os.fdopen(os.open(p,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW),'rb')
def streamhash(f):
 h=hashlib.sha256();n=0
 for b in iter(lambda:f.read(32768),b''):h.update(b);n+=len(b)
 return {'sha256':h.hexdigest(),'bytes':n}
def h(p):
 with op(p) as f:return streamhash(f)
def j(p):
 with op(p) as f:return json.load(f)
def wr(n,o):
 with (P/n).open('x') as f:json.dump(o,f,indent=2);f.write('\n')
archive=h(D/'evidence.tar.gz');assert archive=={'sha256':'0871ec41c94e39313eb132aa1296385e3e6461e7be0a03e9ef333e4d8453b8a3','bytes':1336063}
summary=j(D/'PRESERVATION.json');assert summary['archiveSHA256']==archive['sha256'] and summary['logicalBodies']==264 and summary['uniqueBodies']==249 and summary['noCleanupOrPromotion'] and summary['neededFrozenStageExcluded']
selected={};seen={};roundtrips=[]
with op(D/'evidence.tar.gz') as f:
 with tarfile.open(fileobj=f,mode='r|gz') as t:
  first=next(iter(t));assert first.name=='MANIFEST.json' and first.isfile() and first.size<200000
  with t.extractfile(first) as mf:body=mf.read()
  manifestsha=hashlib.sha256(body).hexdigest();assert manifestsha==summary['manifestSHA256']=='c061f51137513fb0bb3553aa6e7d76b6750a2f4abe3a50aa2dea53fddc9e9181';m=json.loads(body);del body;entries=m['logicalBodies'];assert len(entries)==264
  byhash={}
  for n,row in entries.items():
   path=pathlib.PurePosixPath(n);assert not path.is_absolute() and not any(x in ['.','..'] for x in path.parts);assert row['originalPath']==str(S/n);byhash.setdefault(row['sha256'],[]).append(n)
  assert len(byhash)==249
  for member in t:
   if member.name=='MANIFEST.json':continue
   assert member.isfile() and member.name.startswith('blobs/') and member.name.count('/')==1 and member.name not in seen;digest=member.name[6:];assert digest in byhash
   with t.extractfile(member) as stream:got=streamhash(stream)
   assert got=={'sha256':digest,'bytes':member.size}
   for n in byhash[digest]:
    row=entries[n];assert got=={'sha256':row['sha256'],'bytes':row['bytes']}==h(pathlib.Path(row['originalPath']))
    if n.endswith(('/RUNTIME-FREEZE.json','/GATE.json','/FINAL-SEAL.json','/MANIFEST.json','/VISUAL-RESULT.json','-OPAQUE-SAVE.json','/PRESERVATION-CORRECTION.json','/RESTORED-METADATA-QUALIFICATION.json')):assert member.size<1048576;selected[n]=j(pathlib.Path(row['originalPath']))
   seen[member.name]=member.size;roundtrips.append({'sha256':digest,'bytes':member.size,'logicalAliases':len(byhash[digest])})
assert len(seen)==249 and set(n[6:] for n in seen)==set(byhash)
complete=[]
for root in sorted({n.split('/')[0] for n in entries if '/' in n}):
 original=S/root;actual={str(p.relative_to(original)) for p in original.rglob('*') if p.is_file()};mapped={n[len(root)+1:] for n in entries if n.startswith(root+'/')};assert actual==mapped;complete.append({'root':root,'completeBodies':len(actual)})
for n,man in selected.items():
 if n.endswith('/MANIFEST.json'):
  records=man.get('bodies',man.get('files',[]));rows=[{'name':key,**row} for key,row in records.items()] if isinstance(records,dict) else records
  for row in rows:
   logical=n[:-len('MANIFEST.json')]+row['name'] if 'name' in row else next(k for k,v in entries.items() if v['originalPath']==row['path']);assert entries[logical]['sha256']==row['sha256'] and entries[logical]['bytes']==row['bytes']
f=selected['target-clear-ghost-build-author-r1/RUNTIME-FREEZE.json'];assert entries['target-clear-ghost-build-author-r1/RUNTIME-FREEZE.json']['sha256']=='0410c268657184a5d02eb894076d2cd08d02ecc6e6e9de2ac370b08eefdca90c';assert len(f['inputs'])==88 and len(f['outputs'])==56 and f['sourceDigest']==m['sourceDigest']==summary['sourceDigest'] and f['outputsDigest']==m['outputsDigest']==summary['outputsDigest']
assert f['stage']==m['neededExcludedFrozenStage']=='/workspace/scratch/target-clear-ghost-stage-r1'
for phase in ['before','after']:
 audit=j(S/'target-clear-ghost-comparison-actual-r1'/('BYTE-AUDIT-'+phase+'.json'))
 for kind in ['inputs','outputs']:assert {v['path']:v['sha256'] for v in audit[kind]}==f[kind]
served=j(S/'target-clear-ghost-comparison-actual-r1/SERVED-BYTE-AUDIT.json');assert {v['path']:v['sha256'] for v in served['served']}==f['outputs']
gates={}
for n,pin in {'target-clear-ghost-actual-technical-independent-r1/GATE.json':'4cc1dc2d2ea2532c5d66a41e3c5778e4c757a321dcf633330f9a48b07b3f77e5','target-clear-ghost-actual-gameplay-independent-r1/FINAL-SEAL.json':'a79d25ed66bb17e3f882a3bea095c7dc4c8721bc1725f498b6bbdc8a3812fd83','target-clear-ghost-actual-visual-independent-r2/GATE.json':'851c1a5cbd3a0d3bf4216885aa89d162e42f9b6cbbc4abce569a56956edcb5e7'}.items():assert entries[n]['sha256']==pin;gates[n]={'sha256':pin,'decision':selected[n].get('decision',selected[n].get('status'))}
v=selected['target-clear-ghost-comparison-actual-r1/VISUAL-RESULT.json'];assert v['completed'] and len(v['canonicalComparisons'])==6 and len(v['contexts'])==2
saves={};pairs=[];caps=[]
for row in v['contexts']:
 assert row['holdOutcome']=='COMMITTED_ONCE' and row['holdTransitionCovered'] and row['noQueuedActionAfterRelease'];saves[row['name']]={}
 for label,cp in row['checkpoints'].items():
  logical=str(pathlib.Path(cp['path']).relative_to(S));opaque=selected[logical];assert opaque['raw']==cp['raw'] and opaque['observedOnly'] and hashlib.sha256(cp['raw'].encode()).hexdigest()==cp['sha256'];saves[row['name']][label]=cp['raw']
 assert row['actualSecondRaw']==row['normalizedRaw']==saves[row['name']]['C-secondOutcome']==saves[row['name']]['C-normalized']
for label in ['C0','C1','C2','C-firstDrop','C-secondOutcome','C-normalized']:
 assert saves['A-hold-release'][label]==saves['B-hold-release'][label];pairs.append({'label':label,'completeRawEqual':True,'sha256':hashlib.sha256(saves['A-hold-release'][label].encode()).hexdigest()})
for cap in v['captures']:
 n=str(pathlib.Path(cap['path']).relative_to(S));assert entries[n]['sha256']==cap['sha256'] and entries[n]['bytes']==cap['bytes'] and not cap['phaseCertified'];caps.append({'logical':n,**entries[n],'phaseCertified':False,'viewedOrDecoded':False})
assert len(caps)==4 and sum(x['bytes'] for x in caps)==784953
correction=selected['target-clear-ghost-actual-visual-independent-r2/PRESERVATION-CORRECTION.json'];qualification=selected['target-clear-ghost-actual-visual-independent-r2/RESTORED-METADATA-QUALIFICATION.json'];assert qualification['temporaryRemovalAndExactRestorationDisclosed'] and qualification['originalAndGzipBodiesBothRetained'] and not qualification['oldR1Meets192KiB']
restored=[]
for row in correction['exactOriginalPathsRestored']:
 p=pathlib.Path(row['path']);logical=str(p.relative_to(S));assert entries[logical]['sha256']==row['sha256'] and entries[logical]['bytes']==row['bytes'];gz=p.with_name(p.name+'.gz');assert str(gz.relative_to(S)) in entries
 with op(gz) as ff:
  with gzip.GzipFile(fileobj=ff,mode='rb') as zz:assert streamhash(zz)=={'sha256':row['sha256'],'bytes':row['bytes']}
 q=next(x for x in qualification['restored'] if x['path']==str(p));assert q['beforeTemporaryRemovalMetadata'] is None;restored.append({'original':row,'gzip':h(gz),'beforeRemovalFilesystemIdentityUnknown':True})
assert len(restored)==2
# Hash all copied post/transaction/push/producer controls against their immutable original bodies.
copydir=R/'reviews/three-png-physical-sharing-post-2026-10-02';copymap=j(copydir/'COPY-IDENTITIES.json');copies=[]
for name,row in copymap.items():
 dest=R/'reviews'/name;assert h(dest)==h(pathlib.Path(row['originalPath']))=={'sha256':row['sha256'],'bytes':row['bytes']};copies.append({'name':name,**row})
assert len(copies)==22 and copymap['three-png-physical-sharing-post-2026-10-02/three-retained-png-sharing-post-independent-r1/GATE.json']['sha256']=='014c9d26442bdc581783766d219905a377a99536ef03443bcbab29a9174775ef'
assert copymap['three-png-physical-sharing-post-2026-10-02/three-png-producer-judgment-root-r1.json']['sha256']=='b0da23550ac07c326f36380a1cd3bad02e1f9b1f06bc369437c8f0f6328e95bd'
required=['target-clear-ghost-native-grant-guard-root-r1/RESULT.json','target-clear-ghost-native-grant-guard-root-r2/RESULT.json','target-clear-ghost-native-grant-guard-root-r3/RESULT.json','inactive-build-media-cache-hint-root-r1/RESULT.json','retained-source-bundle-cache-hint-root-r1/RESULT.json','inactive-git-pack-cache-hint-root-r1/RESULT.json']
for n in required:assert n in entries
rootguard=D/'preservation-method/guard';rg=j(rootguard/'RESULT.json');assert rg['exit_code']==0 and rg['failure'] is None and rg['memory_events_before']==rg['memory_events_after'];pp=[rg['initial']]+rg['samples']+[rg['final']]
for x in pp:assert x['headroom']>=512*1048576 and x['current']-rg['initial']['current']<=64*1048576 and x['free']>=1048576
assert h(D/'evidence.tar.gz')==archive
vm=next(int(x.split()[1])*1024 for x in pathlib.Path('/proc/self/status').read_text().splitlines() if x.startswith('VmHWM:'));assert vm<24*1048576
wr('PROOF.json',{'decision':'ACCEPT_EXACT_REJECTED_GHOST_R1_PRESERVATION_AND_THREE_PNG_POST_COPIES_NO_CLEANUP','archive':archive,'manifestSHA256':manifestsha,'preservationSummary':h(D/'PRESERVATION.json'),'README':h(D/'README.md'),'counts':{'logicalBodies':264,'uniqueBlobs':249,'copiedControls':22,'runtimeInputs':88,'runtimeOutputs':56,'completeRawPairs':6,'originalJPEGs':4},'roundtripBlobs':roundtrips,'allLogicalOriginalBodiesEqual':True,'completeEvidenceDirectories':complete,'nestedControlManifestsExact':True,'sourceDigest':f['sourceDigest'],'outputsDigest':f['outputsDigest'],'maps':{'freeze':entries['target-clear-ghost-build-author-r1/RUNTIME-FREEZE.json'],'complete88Inputs56OutputsAgreeBeforeAfterServed':True,'neededExcludedFrozenStage':f['stage'],'qualification':'Entire frozen stage/media excluded, indispensable for reproduction. Capsule contains exact sources in prototype/build controls and complete source/output identities, not all runtime bodies; no self-contained release. Prior actual technical maps remain original byte-bound. No extra media/archive body hashing performed.'},'threeIndependentActualFindings':gates,'completeRawSavePairs':pairs,'fourOriginalJPEGs':caps,'visualOriginalRestoration':{'records':restored,'qualification':qualification,'correction':correction,'failedR1OriginalPacketRetainedStillNeeded':True,'sourceAndBodyIdentityOnlyNotOriginalMetadataRestoration':True},'refusedGrantCacheHintsIncluded':[{ 'logical':n,**entries[n]} for n in required],'copiedPostProducerPushTransaction':copies,'copyIdentities':h(copydir/'COPY-IDENTITIES.json'),'rootPreservationGuard':{'result':h(rootguard/'RESULT.json'),'points':len(pp),'maxAggregateDelta':max(x['current']-rg['initial']['current'] for x in pp),'minimumHeadroom':min(x['headroom'] for x in pp),'eventsUnchanged':True,'normalRc0':True},'ownMethodDiscoveryFailure':'Initial manifest inspection assumed all names have evidence/root prefix and tried split index1; top-level Root helper name caused IndexError after manifest read. Corrected discovery recognizes direct scratch-relative entries; no archive/runtime/source writes.','scope':'Preservation only. Gameplay and visual rejected default selection; technical identity/calculation acceptance remains narrow. Original failed visual methods/restored exact bytes with unknown pre-removal inode/time remain honestly retained. No broad cache causality, actualfit/humanfun, source R2 acceptance, release or retirement/cleanup authority. Copied PNG transaction scope/losses unchanged; previous packet immutable.','method':'O_NOATIME|NOFOLLOW stream tar/gzip and origin hashes, no extraction/large copies/image decode/views/Node/Git/build/browser/native/backend/protectedZIP/Gitpack/sourcebundle body reads. Only new proof written; all readers/FDs close.','ownVmHWM':vm,'utcNs':time.time_ns()})
print(json.dumps({'proof':h(P/'PROOF.json'),'ownVmHWM':vm,'normal':True}))
