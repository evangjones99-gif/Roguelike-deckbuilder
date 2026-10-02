import os,json,hashlib,pathlib,resource,time
resource.setrlimit(resource.RLIMIT_DATA,(24*1048576,24*1048576))
P=pathlib.Path('/workspace/scratch/three-retained-png-sharing-post-independent-r1');S=pathlib.Path('/workspace/scratch');R=pathlib.Path('/workspace/Roguelike-deckbuilder');A=S/'three-retained-png-sharing-actual-root-r1';B=S/'three-retained-png-sharing-before-independent-r1'
keys=['st_dev','st_ino','st_mode','st_nlink','st_uid','st_gid','st_size','st_blocks','st_atime_ns','st_mtime_ns','st_ctime_ns']
def meta(p):return {k:getattr(os.stat(p),k) for k in keys}
def body(p,keep=False):
 before=meta(p);h=hashlib.sha256();n=0;parts=[];fd=os.open(p,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW)
 with os.fdopen(fd,'rb') as f:
  for b in iter(lambda:f.read(32768),b''):
   h.update(b);n+=len(b)
   if keep:assert n<=1048576;parts.append(b)
 assert meta(p)==before,p
 return {'sha256':h.hexdigest(),'bytes':n},b''.join(parts) if keep else None
def h(p):return body(p)[0]
def j(p):return json.loads(body(p,True)[1])
def wr(n,o):
 with (P/n).open('x') as f:json.dump(o,f,indent=2);f.write('\n')
old=j(B/'PROOF.json');gate=j(B/'GATE.json');assert h(B/'GATE.json')['sha256']=='65f9d3be496ab370c3c0a72aaf2f2f22724c318a0f2b6c78b4ac0414e9e80e02'
before=j(A/'BEFORE.json');post=j(A/'RESULT.json');journal=[json.loads(v) for v in body(A/'JOURNAL.jsonl',True)[1].decode().splitlines()]
assert before['pairs']==old['pairs'] and post['normal'] and post['allPathsBodiesKept'] and post['allTempAbsent'] and post['noOtherActionAuthorized']
judgment=S/'three-png-producer-judgment-root-r1.json';push=S/'three-png-preaction-push-root-r1/PUSH-CONFIRMED.json';jud=j(judgment);pr=j(push)
assert h(judgment)['sha256']==before['judgmentSHA256']=='b0da23550ac07c326f36380a1cd3bad02e1f9b1f06bc369437c8f0f6328e95bd'
assert h(push)['sha256']==before['pushSHA256']=='aacb9cd5983c53634822ec8f4033417d1bffd618dc7e710560bd484c71a97472'
assert jud['decision']=='AUTHORIZE_EXACT_THREE_PATH_PHYSICAL_SHARING_ONCE' and jud['independentGateSHA256']==before['gateSHA256']==h(B/'GATE.json')['sha256'] and jud['proposalSHA256']==before['proposalSHA256']==old['proposalPins']['EVIDENCE.json']['sha256']
assert pr['confirmed'] and pr['clean'] and pr['remote']==pr['commit']==jud['commit']==before['commit']=='34f0a2a4c4b19191efd56277e57b25ba0cf3788e'
assert h(S/'share-three-retained-pngs-root-r2.py')['sha256']==jud['methodSHA256']==gate['methodSHA256'] and h(R/'AGENTS.md')['sha256']==jud['holdSHA256']==gate['holdSHA256']
assert len(journal)==9 and len(post['pairs'])==3 and all(journal[i]['utcNs']<journal[i+1]['utcNs'] for i in range(8)) and jud['utcNs']<before['utcNs']<journal[0]['utcNs']
pairs=[];alias=[]
for i,x in enumerate(before['pairs']):
 row=post['pairs'][i];ap=pathlib.Path(row['canonical']);bp=pathlib.Path(row['candidate']);assert str(ap)==x['canonical']['path'] and str(bp)==x['candidate']['path'] and row['sha256']==x['canonical']['sha256']
 assert not ap.is_symlink() and not bp.is_symlink() and meta(ap)==row['canonicalMetadata']==row['candidateMetadata']==meta(bp) and os.listxattr(ap)==os.listxattr(bp)==[]
 assert h(ap)==h(bp)=={'sha256':row['sha256'],'bytes':x['canonical']['metadata']['st_size']}
 am=row['canonicalMetadata'];om=x['canonical']['metadata'];assert am['st_nlink']==5 and om['st_nlink']==4 and am['st_ctime_ns']>om['st_ctime_ns']
 for k in keys:
  if k not in ['st_nlink','st_ctime_ns']:assert am[k]==om[k]
 assert not pathlib.Path(str(bp)+'.root-share-r1.tmp').exists() and x['candidate']['metadata']['st_ino']!=am['st_ino']
 for k,operation in enumerate(['PRE_LINK','LINK_DURABLE','REPLACED_DURABLE']):assert journal[3*i+k]['operation']==operation and journal[3*i+k]['target']==str(bp)
 assert journal[3*i]['source']==str(ap) and journal[3*i+2]['tempAbsent']
 known=(S/'media-loose-png-recovery-proposal-author-r1/CONTEXT.json');ctx=j(known)['knownCanonicalAliases'][i];distinct=set()
 for v in ctx['individuallyCheckedKnownPaths']:
  q=pathlib.Path(v['path'])
  if v['matchesCanonicalPhysicalInode']:
   assert meta(q)==am and os.listxattr(q)==[] and h(q)==h(ap);distinct.add((str(q.parent.resolve()),q.name))
  else:assert meta(q)==v['metadata'] and h(q)==h(ap)
 distinct.add((str(bp.parent.resolve()),bp.name));assert len(distinct)==4
 pairs.append(row);alias.append({'canonical':str(ap),'nlinkBefore':4,'nlinkAfter':5,'observedDistinctPhysicalEntries':4,'unresolvedEntries':1,'ctimeBefore':om['st_ctime_ns'],'ctimeAfter':am['st_ctime_ns'],'knownAliasBodiesMatch':True})
assert post['grossAllocationBytes']==8499200 and post['windowFreeBefore']==before['initialFree']==67526656 and post['windowFreeAfterBeforeResultWrite']==76009472 and post['netWindowGainBytes']==8482816==post['windowFreeAfterBeforeResultWrite']-post['windowFreeBefore']
assert 8499200-8482816==16384
map_path=S/'target-wait-default-promotion-root-r1/RESULT.json';selected=j(map_path);assert h(map_path)['sha256']==jud['selectedMapSHA256']==old['selectedMap']['sha256'];assert len(selected['canonicalInputs'])==87 and len(selected['canonicalOutputs'])==56
maps=[]
for kind,prefix in [('canonicalInputs',R),('canonicalOutputs',R/'dist')]:
 for rel,sha in selected[kind].items():v=h(prefix/rel);assert v['sha256']==sha;maps.append({'kind':kind,'path':rel,**v})
H=S/'audio-host-independent-v08/candidate';hist=[]
for n in ['SOURCE-MANIFEST.json','BUILD-MANIFEST.json']:
 data=j(H/n);expected=old['historical51Build66SourceLedgers']['source' if n.startswith('SOURCE') else 'build'];assert h(H/n)==expected
 for rel,sha in data['files'].items():v=h(H/rel);assert v['sha256']==sha;hist.append({'ledger':n,'path':rel,**v})
assert len(hist)==117 and h(H/'dist/art/PROVENANCE.json')==old['retainedRightsProvenance']['body']
protected=meta(S/'retained-original-archives/preflight-bdf273-original-r4.zip');assert protected==old['protectedMetadataOnly'];gpath=S/'three-png-sharing-actual-guard-root-r1';g=j(gpath/'RESULT.json');assert j(gpath/'ADMISSION.json')['admitted'] and g['exit_code']==0 and g['failure'] is None and g['memory_events_before']==g['memory_events_after']
pts=[g['initial']]+g['samples']+[g['final']]
for v in pts:assert v['headroom']>=512*1048576 and v['current']-g['initial']['current']<=64*1048576 and v['free']>=1048576
vm=next(int(v.split()[1])*1024 for v in pathlib.Path('/proc/self/status').read_text().splitlines() if v.startswith('VmHWM:'));assert vm<24*1048576
wr('PROOF.json',{'decision':'ACCEPT_EXACT_THREE_PNG_POST_TRANSACTION_WITH_RECORDED_PHYSICAL_ISOLATION_LOSSES','actualControls':{n:h(A/n) for n in ['BEFORE.json','JOURNAL.jsonl','RESULT.json']},'beforeGate':h(B/'GATE.json'),'judgment':h(judgment),'push':h(push),'rootMethod':h(S/'share-three-retained-pngs-root-r2.py'),'hold':h(R/'AGENTS.md'),'selectedMap':h(map_path),'commit':before['commit'],'exactPairs':pairs,'originalMetadataRetained':before['pairs'],'knownAliases':alias,'journalExactNineEntriesAndPrefixOrder':True,'grossAllocationBytes':8499200,'measuredWindow':{'before':67526656,'afterBeforeResultWrite':76009472,'netGainBeforeResultWrite':8482816,'differenceFromGross':16384,'qualification':'Observed finite transaction window and before/journal allocation; not enduring free-space guarantee or exclusive global attribution. RESULT/independent report/push footprints follow.'},'currentRuntimeMaps':maps,'current87Inputs56OutputsExact':True,'selectedSourceDigest':selected['sourceDigest'],'selectedOutputsDigest':selected['outputsDigest'],'historicalMaps':hist,'historical66Source51BuildExact':True,'rightsProvenancePreserved':old['retainedRightsProvenance'],'protectedMetadataOnly':protected,'rootActualGuard':{'result':h(gpath/'RESULT.json'),'points':len(pts),'liveRows':len(g['samples']),'maxAggregateDelta':max(v['current']-g['initial']['current'] for v in pts),'minHeadroom':min(v['headroom'] for v in pts),'eventsUnchanged':True,'normalRc0':True,'closureQualification':'Finite generic guard normal completion/child group closure assertion; no independent exhaustive PID/start ledger or unknown FD/mmap/backend/global attribution.'},'onlyExactThreeScope':'Journal and current identities match named three; no broad filesystem mutation audit or new cleanup authority. All logical source/review/provenance/runtime bodies checked remain unchanged. Unknown aliases observe shared metadata effects; no universal hold claim. Original private nlink1 inode/ctime/time/write isolation gone by accepted judgment; byte/path rollback remains, original inode rollback impossible. Holds not OS isolation.','ownVmHWM':vm,'noReviewerNodeGitBrowserImageNativeArchiveBodyOrAction':True,'CLOSED':'All finite source/media NOATIME streams and metadata FDs closed; new proof only.','utcNs':time.time_ns()})
print(json.dumps({'proof':h(P/'PROOF.json'),'ownVmHWM':vm,'normal':True}))
