import os,json,hashlib,pathlib,resource,time,difflib
resource.setrlimit(resource.RLIMIT_DATA,(24*1048576,24*1048576))
P=pathlib.Path('/workspace/scratch/three-retained-png-sharing-before-independent-r1');A=pathlib.Path('/workspace/scratch/media-loose-png-recovery-proposal-author-r1');R=pathlib.Path('/workspace/Roguelike-deckbuilder');S=pathlib.Path('/workspace/scratch')
keys=['st_dev','st_ino','st_mode','st_nlink','st_uid','st_gid','st_size','st_blocks','st_atime_ns','st_mtime_ns','st_ctime_ns']
def meta(p):return {k:getattr(os.stat(p),k) for k in keys}
def body(p,keep=False):
 before=meta(p);z=hashlib.sha256();n=0;parts=[]
 fd=os.open(p,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW)
 with os.fdopen(fd,'rb') as f:
  for b in iter(lambda:f.read(32768),b''):
   z.update(b);n+=len(b)
   if keep:assert n<=1048576;parts.append(b)
 assert meta(p)==before,p
 return {'sha256':z.hexdigest(),'bytes':n},b''.join(parts) if keep else None
def h(p):return body(p)[0]
def j(p):return json.loads(body(p,True)[1])
def text(p):return body(p,True)[1].decode()
def wr(n,o):
 with (P/n).open('x') as f:json.dump(o,f,indent=2);f.write('\n')
pins={'EVIDENCE.json':'02bc18528c9146cfd9c32c42cc0d28b75a6d7cc387854507f6c369fb80dcb7f2','CONTEXT.json':'16861ca05b7f2125bf67c20dee18f16e29482fc92fa2053afe8c2e7c7fedb5be','PROPOSAL.md':'b233919941d0205905f83812ba586af927de4479ff2468a798775cf2dadd358a','FINAL-SEAL.json':'cbaab421'}
for n,sha in pins.items():assert h(A/n)['sha256'].startswith(sha),(n,h(A/n))
f=j(A/'FINAL-SEAL.json');e=j(A/'EVIDENCE.json');c=j(A/'CONTEXT.json');controls=[]
for row in f['files']+f['sourceControls']:
 q=pathlib.Path(row['path']);v=h(q);assert v=={'sha256':row['sha256'],'bytes':row['bytes']};controls.append({'path':str(q),**v})
assert len(e['pairs'])==3 and e['verification']=='EXACT_MATCH' and e['allocatedCandidateBytes']==8499200
assert {pathlib.Path(x['candidate']['path']).name for x in e['pairs']}=={'abbey-courtyard.png','tool-vignettes.png','hunter-portrait.png'}
pairs=[]
for x in e['pairs']:
 for kind in ['candidate','canonical']:
  v=x[kind];q=pathlib.Path(v['path']);assert not q.is_symlink();assert meta(q)==v['metadata'];assert os.listxattr(q)==[];assert h(q)=={'sha256':v['sha256'],'bytes':v['metadata']['st_size']}
 assert x['candidate']['sha256']==x['canonical']['sha256'];assert x['candidate']['metadata']['st_nlink']==1 and x['canonical']['metadata']['st_nlink']==4
 pairs.append(x)
assert sum(x['candidate']['metadata']['st_blocks']*512 for x in pairs)==8499200
alias=[]
for row in c['knownCanonicalAliases']:
 matches=set()
 for v in row['individuallyCheckedKnownPaths']:
  q=pathlib.Path(v['path']);assert meta(q)==v['metadata'] and os.listxattr(q)==[]
  if v['matchesCanonicalPhysicalInode']:matches.add((str(q.parent.resolve()),q.name))
 assert len(matches)==3 and row['currentCanonicalNlink']==4
 alias.append({'canonical':row['canonical'],'observedDistinctMatchingEntries':3,'nlink':4,'unresolvedPhysicalEntries':1,'canonicalDistSeparate':True})
for row in c['heldParentsMetadata']:assert meta(pathlib.Path(row['path']))==row['metadata']
map_path=S/'target-wait-default-promotion-root-r1/RESULT.json';selected=j(map_path);assert len(selected['canonicalInputs'])==87 and len(selected['canonicalOutputs'])==56
runtime=[]
for kind,prefix in [('canonicalInputs',R),('canonicalOutputs',R/'dist')]:
 for rel,sha in selected[kind].items():v=h(prefix/rel);assert v['sha256']==sha;runtime.append({'kind':kind,'path':rel,**v})
assert selected['sourceDigest']=='1d5bf40a5f62c8ce3de1d087956e9190e98b3011cca1b1b7a5488fc8240bd4d3' and selected['outputsDigest']=='30ddc549433f7b0b7611e41c0d4fd67e00a3aaa07dd61ba886cc43094f1e5464'
B=S/'audio-host-independent-v08/candidate';oldbuild=j(B/'BUILD-MANIFEST.json');oldsource=j(B/'SOURCE-MANIFEST.json');assert len(oldbuild['files'])==51 and len(oldsource['files'])==66
assert h(B/'BUILD-MANIFEST.json')['sha256']=='6799d13f41f2a62c3feb1546253ebf07f3e01ce4c56f5c06b1720712f4159e6c'
assert h(B/'SOURCE-MANIFEST.json')['sha256']=='45cbbb65a1e76f2aec08fe2b217372104df3425f92daff15779651315c7a9917'
prov=j(B/'dist/art/PROVENANCE.json');assert h(B/'dist/art/PROVENANCE.json')['sha256']==oldbuild['files']['dist/art/PROVENANCE.json'];rights=[]
for x in pairs:
 name=pathlib.Path(x['candidate']['path']).name;sha=x['candidate']['sha256'];assert oldbuild['files']['dist/art/'+name]==oldsource['files']['public/art/'+name]==sha
 row=next(v for v in prov['images'] if v['file']==name);assert row['sha256']==sha;rights.append(row)
hold=text(R/'AGENTS.md');assert '/workspace/scratch/audio-host-independent-v08/candidate/dist/art/abbey-courtyard.png' in hold and 'tool-vignettes.png' in hold and 'hunter-portrait.png' in hold and 'immutable and fresh-stage-only' in hold
protected=S/'retained-original-archives/preflight-bdf273-original-r4.zip';ps=meta(protected);assert (ps['st_dev'],ps['st_ino'],ps['st_size'],ps['st_nlink'])==(27,678628,1856041104,1)
r1=text(S/'share-three-retained-pngs-root-r1.py');r2=text(S/'share-three-retained-pngs-root-r2.py');delta=''.join(difflib.unified_diff(r1.splitlines(True),r2.splitlines(True),fromfile='r1',tofile='r2'));(P/'METHOD-DELTA.diff').write_text(delta)
add="""assert sha(Path(__file__))==j['methodSHA256'] and sha(R/'AGENTS.md')==j['holdSHA256']
map_path=S/'target-wait-default-promotion-root-r1/RESULT.json'
assert sha(map_path)==j['selectedMapSHA256']
selected=read(map_path)
def verify_selected():
 for rel,h in selected['canonicalInputs'].items():assert sha(R/rel)==h,rel
 for rel,h in selected['canonicalOutputs'].items():assert sha(R/'dist'/rel)==h,rel
verify_selected()
protected=S/'retained-original-archives/preflight-bdf273-original-r4.zip'
protected_before=meta(protected)
assert (protected_before['st_dev'],protected_before['st_ino'],protected_before['st_size'],protected_before['st_nlink'])==(27,678628,1856041104,1)
"""
assert r2==r1.replace("assert read(gate)['decision'].startswith('ACCEPT')\n","assert read(gate)['decision'].startswith('ACCEPT')\n"+add).replace('final_free=os.statvfs(R)', 'verify_selected();assert meta(protected)==protected_before\nfinal_free=os.statvfs(R)')
assert not (S/'three-retained-png-sharing-actual-root-r1').exists()
for x in pairs:assert not pathlib.Path(x['candidate']['path']+'.root-share-r1.tmp').exists()
groups=[]
for name,rc in [('reader-guard-r1',0),('seal-guard-r1',1),('seal-guard-r2',0)]:
 g=j(A/name/'RESULT.json');assert g['exit_code']==rc and g['failure'] is None and g['memory_events_before']==g['memory_events_after'];pts=[g['initial']]+g['samples']+[g['final']]
 for v in pts:assert v['headroom']>=512*1048576 and v['current']-g['initial']['current']<=64*1048576 and v['free']>=1048576
 groups.append({'name':name,'exitCode':rc,'result':h(A/name/'RESULT.json'),'points':len(pts),'maxAggregateDelta':max(v['current']-g['initial']['current'] for v in pts),'minHeadroom':min(v['headroom'] for v in pts),'eventsUnchanged':True})
for data in [j(A/'RESOURCE.json'),f['resource']]:
 assert data['eventsBefore']==data['eventsAfter']
 for v in data['rows']:assert v['sharedDelta']<=64*1048576 and v['headroom']>=512*1048576 and v['free']>=1048576 and v['ownMaxRSS']<24*1048576
vm=next(int(v.split()[1])*1024 for v in pathlib.Path('/proc/self/status').read_text().splitlines() if v.startswith('VmHWM:'));assert vm<24*1048576
wr('PROOF.json',{'decision':'ACCEPT_EXACT_THREE_PNG_BEFORE_PROPOSAL_AND_ROOT_R2_METHOD_CONDITIONAL_ON_PRODUCER_JUDGMENT_AND_FRESH_PUSH','proposalPins':{n:h(A/n) for n in pins},'allSealedControlsExact':controls,'pairs':pairs,'grossAllocationBytes':8499200,'logicalBytes':8492116,'knownAliases':alias,'selectedMap':h(map_path),'selectedSourceDigest':selected['sourceDigest'],'selectedOutputsDigest':selected['outputsDigest'],'runtimeBodies':runtime,'current87Inputs56OutputsExact':True,'historical51Build66SourceLedgers':{'build':h(B/'BUILD-MANIFEST.json'),'source':h(B/'SOURCE-MANIFEST.json')},'retainedRightsProvenance':{'body':h(B/'dist/art/PROVENANCE.json'),'selectedRecords':rights,'commercialRightsPendingNotReapproved':True},'hold':h(R/'AGENTS.md'),'rootMethodR1':h(S/'share-three-retained-pngs-root-r1.py'),'rootMethodR2':h(S/'share-three-retained-pngs-root-r2.py'),'r2OnlySelfHoldMapProtectedStatAdditions':True,'protectedMetadataOnly':ps,'authorGuardGroups':groups,'retainedAuthorFailure':f['retainedFailure'],'ownMethodDiscoveryFailure':'Tried BUILD/SOURCE-MANIFEST under independent rather than candidate; ls/read FileNotFound before verifier. Correct candidate controls found with rg; no original source/runtime modified. Initial ordinary source JSON/readme reads may change source atime, not body. All PNG/fullruntime media verifier reads O_NOATIME with fullstat preserved.','judgment':'Prefer exact shared byte encoding for these three retained immutable leaves because old private physical encoding is unnecessary for reproduction, rollback bytes, rights or historical consumer findings. Original inode/ctime and private write isolation are intentionally lost, not recreated. No old body/path/provenance/review/dataset/source retired. Preference conditional on exact producer acceptance of losses and currently pushed preservation controls.','methodLimits':'r2 creates no old inode backups and is sequential per-leaf atomic with durable prefix journal, not all-three atomic. It differs from unchanged author CONTEXT backup suggestion. Byte/path rollback available from held canonical/checkpoint bytes; exact original inode/ctime rollback impossible. Unknown fourth canonical entry shares body and link/ctime effects, but metadata holds for it not universally independently verified. No absence proof of FDs/mmap/global/future writers. Workflow coordination required. No action/retry/extra path authority from this review; partial interruption must preserve journal/temp/prefix and receive fresh diagnosis before continuation.','methodSafety':'Hashes supplied proposal/gate/judgment/push, ties producer judgment to exact proposal/gate/selfmethod/hold/map, requires decision, matching commit/clean recorded confirmed push and local status; current full maps before/after. All three exact old/canonical metadata/body/xattr/temp preflight, durable BEFORE before first link, PRE_LINK/link-dirfsync/LINK_DURABLE/replace-dirfsync/REPLACED_DURABLE journal, per-body identity and full postmap/protected-stat checks. No existing file body/chmod/xattr/timestamp writes. Root method uses Git read-only checks when separately executed; reviewer uses none. No automatic cleanup/fallback/retry or all-path rollback.','noActionOccurred':True,'ownVmHWM':vm,'CLOSED':'Finite NOATIME body reads and metadata FDs closed; no Node/browser/images/native/Git/archivebody/action/source mutation. Only NEW proof writes.','utcNs':time.time_ns()})
print(json.dumps({'normal':True,'proof':h(P/'PROOF.json'),'ownVmHWM':vm}))
