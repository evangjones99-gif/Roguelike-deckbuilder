import os,json,pathlib,hashlib,resource,time,stat
resource.setrlimit(resource.RLIMIT_DATA,(24*1048576,24*1048576))
P=pathlib.Path('/workspace/scratch/second-three-png-sharing-post-independent-r4');S=pathlib.Path('/workspace/scratch');R=pathlib.Path('/workspace/Roguelike-deckbuilder');A=S/'second-three-retained-png-sharing-actual-root-r4'
KEYS=['st_dev','st_ino','st_mode','st_nlink','st_uid','st_gid','st_size','st_blocks','st_atime_ns','st_mtime_ns','st_ctime_ns']
def md(st):return {k:getattr(st,k) for k in KEYS}
def meta(p):return md(os.stat(p,follow_symlinks=False))
def op(p):return os.fdopen(os.open(p,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW),'rb')
def h(p):
 before=meta(p);z=hashlib.sha256();n=0
 with op(p) as f:
  assert md(os.fstat(f.fileno()))==before
  for b in iter(lambda:f.read(32768),b''):z.update(b);n+=len(b)
  assert md(os.fstat(f.fileno()))==before
 assert meta(p)==before
 return {'sha256':z.hexdigest(),'bytes':n}
def j(p):
 with op(p) as f:return json.load(f)
def chain(p):
 fd=os.open('/',os.O_PATH|os.O_DIRECTORY|os.O_NOFOLLOW)
 try:
  for part in p.parent.parts[1:]:
   q=os.open(part,os.O_PATH|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd);os.close(fd);fd=q
  return True
 finally:os.close(fd)
b=j(A/'BEFORE.json');r=j(A/'RESULT.json');proposalpath=S/'media-loose-png-recovery-proposal-author-r2/PROPOSAL.json';proposal=j(proposalpath);gatepath=S/'second-three-png-atime-rebind-independent-r1/GATE.json';gate=j(gatepath);judpath=S/'second-three-png-producer-judgment-root-r4.json';jud=j(judpath);pushpath=S/'atime-rebind-push-root-r1/PUSH-CONFIRMED.json';push=j(pushpath)
assert h(proposalpath)['sha256']==b['proposalSHA256']=='45ed75b5078c84e32981ba86b43f62826b00c53278ef8ea2f9888d661b8fd8d5'
assert h(gatepath)['sha256']==b['gateSHA256']==jud['independentGateSHA256']==push['gateSHA256']=='fedeb00dad977acbc770ae9614e5cc8ed350be4855713c9751eb28a22832e4f9'
assert h(judpath)['sha256']==b['judgmentSHA256']=='eca6c758ea9633c061570083362e63fdfd236ab1822132e4ce3a7b314533aba6'
assert h(pushpath)['sha256']==b['pushSHA256']==jud['pushSHA256']=='6c7fabe80faccd35098e73909c35e4f7134ad671f0ac5c2e021fadf6ebfa619e'
assert jud['decision']=='AUTHORIZE_EXACT_THREE_PATH_PHYSICAL_SHARING_ONCE' and jud['oneActionOnly'] and jud['noAutomaticRetry'] and push['confirmed'] and push['clean']
assert push['remote']==push['commit']==b['commit']==jud['commit']=='90d128934e5a86c66c4fa92d0eebb1906a3f2b37'
assert h(S/'share-second-three-retained-pngs-root-r4.py')['sha256']==jud['methodSHA256']==gate['method']['sha256']==push['methodSHA256']=='5c03ec5135584a2fc83ebff60bb4ee6f52b1451ebf79ae4125d16704530f3adc'
assert h(R/'AGENTS.md')['sha256']==jud['holdSHA256']==gate['currentHold']['sha256']==push['holdSHA256']=='69a82ce96a594a2b2a5244154de8758b200290ba9de46b40a221a52ba4a0cfb7'
assert r['normal'] and r['allPathsBodiesKept'] and r['allTempAbsent'] and r['noOtherActionAuthorized'] and len(b['pairs'])==len(r['pairs'])==len(proposal['pairs'])==3
with op(A/'JOURNAL.jsonl') as f:journal=[json.loads(line) for line in f]
assert len(journal)==9 and b['utcNs']<journal[0]['utcNs'] and all(x['utcNs']<y['utcNs'] for x,y in zip(journal,journal[1:]))
pairs=[];aliases=[];rebinding=[]
for i,(old,pr,new) in enumerate(zip(b['pairs'],proposal['pairs'],r['pairs'])):
 ap=pathlib.Path(new['canonical']);bp=pathlib.Path(new['candidate']);assert str(ap)==old['anchor']['path']==pr['anchor']['path'] and str(bp)==old['candidate']['path']==pr['candidate']['path']
 assert chain(ap) and chain(bp)
 for kind in ['anchor','candidate']:
  assert old[kind]['proposalMetadata']==pr[kind]['fstat'] and old[kind]['lstat']==old[kind]['fstat']
  for key in KEYS:
   if key!='st_atime_ns':assert old[kind]['fstat'][key]==pr[kind]['fstat'][key]
  rebinding.append({'path':old[kind]['path'],'proposalAtime':pr[kind]['fstat']['st_atime_ns'],'initialSnapshotAtime':old[kind]['fstat']['st_atime_ns'],'onlyAtimeRebound':True})
 assert old['anchor']['fstat']['st_nlink']==5 and old['candidate']['fstat']['st_nlink']==1
 am=meta(ap);cm=meta(bp);assert am==cm==new['canonicalMetadata']==new['candidateMetadata'] and am['st_nlink']==6 and stat.S_ISREG(am['st_mode']) and os.listxattr(ap,follow_symlinks=False)==os.listxattr(bp,follow_symlinks=False)==[]
 assert h(ap)==h(bp)=={'sha256':new['sha256'],'bytes':am['st_size']} and new['sha256']==old['anchor']['sha256']==old['candidate']['sha256']
 for key in KEYS:
  if key not in ['st_nlink','st_ctime_ns']:assert am[key]==old['anchor']['fstat'][key]
 assert am['st_ctime_ns']>old['anchor']['fstat']['st_ctime_ns'] and cm['st_ino']!=old['candidate']['fstat']['st_ino']
 temp=pathlib.Path(str(bp)+'.root-share-second-r4.tmp');assert not os.path.lexists(temp)
 for k,operation in enumerate(['PRE_LINK','LINK_DURABLE','REPLACED_DURABLE']):assert journal[3*i+k]['operation']==operation and journal[3*i+k]['target']==str(bp)
 assert journal[3*i]['source']==str(ap) and journal[3*i]['temp']==str(temp) and journal[3*i+2]['tempAbsent']
 observed=set()
 for v in proposal['knownAnchorAliases'][i]['knownPhysicalEntries']:
  q=pathlib.Path(v['path']);assert os.stat(q).st_ino==am['st_ino'] and os.stat(q).st_nlink==6 and h(q)['sha256']==new['sha256'];observed.add((str(q.parent.resolve()),q.name))
 observed.add((str(bp.parent.resolve()),bp.name));assert len(observed)==5
 aliases.append({'anchor':str(ap),'observedDistinctPhysicalEntries':5,'nlink':6,'unresolvedPhysicalEntries':1,'fullCurrentAnchorMetadata':am});pairs.append({'candidate':str(bp),'anchor':str(ap),'sha256':new['sha256'],'currentMetadata':am,'oldCandidateMetadata':old['candidate']['fstat'],'oldAnchorMetadata':old['anchor']['fstat']})
assert r['grossAllocationBytes']==8499200==proposal['grossOldAllocationBytes'] and r['windowFreeBefore']==b['initialFree']==64778240 and r['windowFreeAfterBeforeResultWrite']==73240576 and r['netWindowGainBytes']==8462336==r['windowFreeAfterBeforeResultWrite']-r['windowFreeBefore']
map_path=S/'target-wait-default-promotion-root-r1/RESULT.json';selected=j(map_path);assert h(map_path)['sha256']==jud['selectedMapSHA256']==gate['selectedMap']['sha256'];maps=[]
assert len(selected['canonicalInputs'])==87 and len(selected['canonicalOutputs'])==56
for kind,prefix in [('canonicalInputs',R),('canonicalOutputs',R/'dist')]:
 for rel,pin in selected[kind].items():v=h(prefix/rel);assert v['sha256']==pin;maps.append({'kind':kind,'path':rel,**v})
firstproof=j(S/'three-retained-png-sharing-post-independent-r1/PROOF.json');assert meta(S/'retained-original-archives/preflight-bdf273-original-r4.zip')==firstproof['protectedMetadataOnly']
# Historical66/51 aggregate ledgers are pinned historical evidence, not a new full replay.
H=S/'audio-host-independent-v08/candidate';assert h(H/'SOURCE-MANIFEST.json')['sha256']=='45cbbb65a1e76f2aec08fe2b217372104df3425f92daff15779651315c7a9917' and h(H/'BUILD-MANIFEST.json')['sha256']=='6799d13f41f2a62c3feb1546253ebf07f3e01ce4c56f5c06b1720712f4159e6c'
assert h(S/'three-retained-png-sharing-post-independent-r1/GATE.json')['sha256']=='014c9d26442bdc581783766d219905a377a99536ef03443bcbab29a9174775ef'
gpath=S/'second-three-png-sharing-actual-guard-root-r4';gr=j(gpath/'RESULT.json');ad=j(gpath/'ADMISSION.json');assert ad['admitted'] and ad['work']==64*1048576 and ad['reserve']==512*1048576 and gr['exit_code']==0 and gr['failure'] is None and gr['memory_events_before']==gr['memory_events_after'];pts=[gr['initial']]+gr['samples']+[gr['final']]
assert gr['initial']['headroom']>=576*1048576 and gr['initial']['free']>=56*1048576 and gr['initial']['free']<64*1048576
for q in pts:assert q['headroom']>=512*1048576 and q['current']-gr['initial']['current']<=64*1048576 and q['free']>=1048576
# Bind actual supervisor invocation to exact producer pins, not arbitrary payload eligibility.
assert ad['command']==['python',str(S/'share-second-three-retained-pngs-root-r4.py'),str(proposalpath),h(proposalpath)['sha256'],str(gatepath),h(gatepath)['sha256'],str(judpath),h(judpath)['sha256'],str(pushpath),h(pushpath)['sha256']]
vm=next(int(x.split()[1])*1024 for x in pathlib.Path('/proc/self/status').read_text().splitlines() if x.startswith('VmHWM:'));assert vm<24*1048576
proof={'decision':'ACCEPT_EXACT_SECOND_THREE_PNG_R4_POST_WITH_RECORDED_ATIME_REBIND_AND_ISOLATION_LOSSES','actualControls':{n:h(A/n) for n in ['BEFORE.json','JOURNAL.jsonl','RESULT.json']},'proposal':h(proposalpath),'beforeGate':h(gatepath),'judgment':h(judpath),'push':h(pushpath),'method':h(S/'share-second-three-retained-pngs-root-r4.py'),'hold':h(R/'AGENTS.md'),'selectedMap':h(map_path),'commit':b['commit'],'pairs':pairs,'knownAliases':aliases,'initialAtimeOnlyRebinding':rebinding,'allNineJournalEntriesOrderedExactly':True,'allTempAbsent':True,'allPathsExactBodiesRetained':True,'window':{'gross':8499200,'beforeFree':64778240,'afterBeforeResultWrite':73240576,'netBeforeResultWrite':8462336,'differenceFromGross':36864,'qualification':'Finite observed transaction window; proofs/publication/other actors consume capacity afterward. Not lasting free-space or exclusive actor attribution.'},'canonicalMaps':maps,'fullCurrent87Inputs56OutputsExact':True,'sourceDigest':selected['sourceDigest'],'outputsDigest':selected['outputsDigest'],'protectedFullStatUnchangedMetadataOnly':firstproof['protectedMetadataOnly'],'historical66Source51OutputLedgersPinnedNotNewReplay':True,'previous014cPOSTRetainedAsHistoricalNlink5':True,'rootActualGuard':{'result':h(gpath/'RESULT.json'),'admission':h(gpath/'ADMISSION.json'),'points':len(pts),'samples':len(gr['samples']),'minimumHeadroom':min(q['headroom'] for q in pts),'maximumAggregateDelta':max(q['current']-gr['initial']['current'] for q in pts),'eventsUnchanged':True,'normalRc0':True,'scoped56MiBDiskRecoveryProfileExplicitNotOrdinary64Disk':True,'qualification':'Separately reviewed exact pinned recovery-only56disk floor with64work+512reserve; ordinary build64/native70 thresholds unchanged. Guard finite normal-child-group closure assertion, no exhaustive PID/global/FD/mmap/backend attribution.'},'scope':'Only named3 historical independent rebuilt-dist recipients shared. Original privateinode/time/writeisolation lost by specific independent/producer judgment; bytes/paths/provenance/rights/oldnegativefindings/rollbackbytes stay needed. One unresolved alias peranchor has sharedctime/nlink implications. No originalinode rollback or oldinodebackup, no all3atomicity or automaticretry; durableprefix preserved. Holds not OS protection. Currentcleanpush is bound preactionmethod/receipt; no fresh Git inspection by reviewer. Original r3 preactionfailure and atime-onlyrebinding preserved, not silently rewritten. No extra cleanup/gamequality/art/defaultrelease authority.','reviewerMethodFailure':'Original verify.py SyntaxError unmatched list bracket before any execution/body read/proof write; new verify-r2.py adds missing closing bracket, original script/GUARD log retained unchanged.','ownVmHWM':vm,'CLOSED':'Finite NOATIME|NOFOLLOW regular reads/held O_PATH ancestor validation allFDsclosed; no Git/Node/build/browser/native/images/protectedarchivebody/action/source mutation. NEW proof only.','utcNs':time.time_ns()}
with (P/'PROOF.json').open('x') as f:json.dump(proof,f,indent=2);f.write('\n')
print(json.dumps({'proof':h(P/'PROOF.json'),'ownVmHWM':vm,'normal':True}))
