from pathlib import Path
import os,json,hashlib,stat,resource
resource.setrlimit(resource.RLIMIT_DATA,(24*1048576,24*1048576))
S=Path('/workspace/scratch');R=Path('/workspace/Roguelike-deckbuilder');P=S/'five-rebuilt-png-sharing-post-independent-r1';A=S/'five-rebuilt-png-sharing-actual-root-r1';G=S/'five-rebuilt-png-sharing-guard-root-r1'
KEYS=['st_dev','st_ino','st_mode','st_nlink','st_uid','st_gid','st_size','st_blocks','st_atime_ns','st_mtime_ns','st_ctime_ns']
def md(s):return {k:getattr(s,k) for k in KEYS}
def op(p,flags=os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME):
 p=Path(p);fd=os.open('/',os.O_PATH|os.O_DIRECTORY|os.O_NOFOLLOW)
 try:
  for part in p.parent.parts[1:]:
   assert part not in ('','.', '..');n=os.open(part,os.O_PATH|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd);os.close(fd);fd=n
  return os.open(p.name,flags,dir_fd=fd)
 finally:os.close(fd)
def pin(p,body=False):
 p=Path(p);before=md(os.lstat(p));fd=op(p);h=hashlib.sha256();parts=[];size=0
 try:
  assert stat.S_ISREG(before['st_mode']) and md(os.fstat(fd))==before
  attrs={n:os.getxattr(fd,n).hex() for n in os.listxattr(fd)}
  for b in iter(lambda:os.read(fd,65536),b''):
   h.update(b);size+=len(b)
   if body:parts.append(b);assert size<262144
  assert md(os.fstat(fd))==before==md(os.lstat(p))
 finally:os.close(fd)
 q={'path':str(p),'sha256':h.hexdigest(),'bytes':size,'metadata':before,'xattrs':attrs};return (q,b''.join(parts)) if body else q
def load(p):
 q,b=pin(p,True);return q,json.loads(b)
def save(n,j):
 with (P/n).open('x') as f:json.dump(j,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
protected=S/'retained-original-archives/preflight-bdf273-original-r4.zip';protected_before=md(os.lstat(protected));assert (protected_before['st_dev'],protected_before['st_ino'],protected_before['st_size'],protected_before['st_nlink'])==(27,678628,1856041104,1)
pp,e=load(S/'five-rebuilt-png-recovery-proposal-r1/PROPOSAL.json');assert pp['sha256']=='371c1e2df47f30e4abca9abece46864b53f4fb6f25e9a78926ee98a0d7a054c5'
gp,g=load(S/'five-rebuilt-png-sharing-independent-r1/GATE.json');assert gp['sha256']=='2d52158de3ff30d20f572ae35a5932d701ed728b709ce79daa58e79c5dfa8d8e'
jp,j=load(S/'five-rebuilt-png-producer-judgment-root-r1.json');assert jp['sha256']=='352679f2ada72839224df79e2a11c03716f878f87ae9ddcf5654f34cb01605c9'
pushp,push=load(S/'five-rebuilt-png-proposal-push-root-r1/PUSH-CONFIRMED.json');assert pushp['sha256']=='c80f1364c5246200a8db9c5c753b2c45b65bba180807917460f325eff5400e4a'
assert push['confirmed'] and push['clean'] and push['remote']==push['commit']==j['commit']=='cb0f9ebd907ba2f709b53af8190efe1d5bc84127'
assert j['independentGateSHA256']==push['gateSHA256']==gp['sha256'] and j['proposalSHA256']==pp['sha256'] and j['pushSHA256']==pushp['sha256']
assert j['decision']=='AUTHORIZE_EXACT_FIVE_PATH_PHYSICAL_SHARING_ONCE' and j['oneActionOnly'] and j['noAutomaticRetry']
sourcepins=[]
for key in ['method','publisher','producer','currentHold','selectedMap']:
 q=pin(g[key]['path']);assert q['sha256']==g[key]['sha256'];sourcepins.append(q)
method=sourcepins[0];assert method['sha256']==j['methodSHA256']==push['methodSHA256']=='77ec35c075e49d757985d7b6dc7ed93bd87eab6a3692604714f18a278f75fdd1'
assert sourcepins[3]['sha256']==j['holdSHA256']==push['holdSHA256'] and sourcepins[4]['sha256']==j['selectedMapSHA256']
for rel,h in [('five-rebuilt-png-sharing-independent-r1/GATE.json',gp['sha256']),('root-controls/share-five-rebuilt-pngs-root-r1.py',method['sha256'])]:assert pin(R/'reviews/five-rebuilt-png-physical-sharing-2026-10-02'/rel)['sha256']==h
priorp,prior=gp,g
priorproof=pin(g['proof']['path']);assert priorproof['sha256']==g['proof']['sha256']
preproof=json.loads(Path(g['proof']['path']).read_text());assert protected_before==preproof['protectedZipStatAfter']
bp,before=load(A/'BEFORE.json');rp,result=load(A/'RESULT.json');journalp,rawjournal=pin(A/'JOURNAL.jsonl',True);rows=[json.loads(l) for l in rawjournal.splitlines()]
assert result['normal'] and result['allPathsBodiesKept'] and result['allTempAbsent'] and result['noOtherActionAuthorized']
assert before['proposalSHA256']==pp['sha256'] and before['gateSHA256']==gp['sha256'] and before['judgmentSHA256']==jp['sha256'] and before['pushSHA256']==pushp['sha256'] and before['commit']==push['commit']
adp,ad=load(G/'ADMISSION.json');grp,gr=load(G/'RESULT.json');glp=pin(G/'EXECUTION.log')
assert ad['admitted'] and ad['work']==64*1048576 and ad['reserve']==512*1048576 and gr['exit_code']==0 and gr['failure'] is None and len(gr['samples'])>=1 and gr['memory_events_before']==gr['memory_events_after']
assert ad['command']==['python',method['path'],pp['path'],pp['sha256'],gp['path'],gp['sha256'],jp['path'],jp['sha256'],pushp['path'],pushp['sha256']]
assert pushp['metadata']['st_mtime_ns']<=jp['metadata']['st_mtime_ns']<=before['utcNs']<=rows[0]['utcNs']
assert ad['initial']['time_ns']<=before['utcNs'] and rows[-1]['utcNs']<=gr['final']['time_ns']
assert len(e['pairs'])==len(before['pairs'])==len(result['pairs'])==5 and len(rows)==15 and [r['utcNs'] for r in rows]==sorted(r['utcNs'] for r in rows)
media=[];original=[]
for idx,pair in enumerate(e['pairs']):
 a=pair['anchor'];b=pair['candidate'];pre=before['pairs'][idx];post=result['pairs'][idx]
 assert pre['anchor']['path']==a['path'] and pre['candidate']['path']==b['path'] and post['canonical']==a['path'] and post['candidate']==b['path'] and post['sha256']==a['sha256']==b['sha256']
 for kind,old in [('anchor',a),('candidate',b)]:
  z=pre[kind];assert z['proposalMetadata']==old['fstat'] and z['lstat']==z['fstat']
  assert all(z['fstat'][k]==v for k,v in old['fstat'].items() if k!='st_atime_ns') and z['sha256']==old['sha256']
 aa=pin(a['path']);bb=pin(b['path']);assert aa['sha256']==bb['sha256']==a['sha256'] and aa['bytes']==bb['bytes']==a['fstat']['st_size']
 assert aa['metadata']==bb['metadata'] and post['canonicalMetadata']==post['candidateMetadata'] and aa['xattrs']==bb['xattrs']=={}
 assert all(aa['metadata'][k]==val for k,val in post['canonicalMetadata'].items() if k!='st_atime_ns')
 assert aa['metadata']['st_ino']==a['fstat']['st_ino'] and aa['metadata']['st_nlink']==a['fstat']['st_nlink']+1 and aa['metadata']['st_ino']!=b['fstat']['st_ino']
 assert all(aa['metadata'][k]==v for k,v in pre['anchor']['fstat'].items() if k not in ('st_nlink','st_ctime_ns','st_atime_ns')) and aa['metadata']['st_ctime_ns']>=pre['anchor']['fstat']['st_ctime_ns']
 temp=b['path']+'.root-share-five-rebuilt-r1.tmp'
 assert not Path(temp).exists() and not Path(b['path']+'.root-share-five-r1.tmp').exists()
 rr=rows[idx*3:idx*3+3];assert [r['operation'] for r in rr]==['PRE_LINK','LINK_DURABLE','REPLACED_DURABLE'] and all(r['target']==b['path'] for r in rr)
 assert rr[0]['source']==a['path'] and rr[0]['temp']==rr[1]['temp']==temp and rr[2]['tempAbsent'] is True
 media.append({'canonical':aa,'retainedCandidateAlias':bb,'actionToPostAtimeNs':{'action':post['canonicalMetadata']['st_atime_ns'],'post':aa['metadata']['st_atime_ns']},'canonicalNlinkDelta':1,'oldCandidatePrivateNlink':pre['candidate']['fstat']['st_nlink'],'tempAbsent':True})
 original.append({'canonical':a['path'],'candidate':b['path'],'proposalAnchorMetadata':a['fstat'],'proposalCandidateMetadata':b['fstat'],'actualBeforeAnchorMetadata':pre['anchor']['fstat'],'actualBeforeCandidateMetadata':pre['candidate']['fstat']})
mp,selected=load(S/'target-wait-default-promotion-root-r1/RESULT.json');assert mp['sha256']==g['selectedMap']['sha256'] and len(selected['canonicalInputs'])==87 and len(selected['canonicalOutputs'])==56
current=[]
for group,root in [('canonicalInputs',R),('canonicalOutputs',R/'dist')]:
 for rel,h in selected[group].items():
  q=pin(root/rel);assert q['sha256']==h;current.append({'group':group,'relativePath':rel,'sha256':q['sha256'],'bytes':q['bytes'],'fullBodyVerifiedWithStableO_NOATIMEMetadata':True})
assert len(current)==143
aliases=[]
for z in e['knownAnchorAliases']:
 anchor=next(x['canonical'] for x in media if x['canonical']['path']==z['anchor']);known=[];count=0
 for old in z['knownEntries']:
  if 'lstat' not in old:known.append({'path':old['path'],'unresolvedHistoricalEntry':True});continue
  fd=op(old['path'],os.O_PATH|os.O_NOFOLLOW)
  try:st=md(os.fstat(fd))
  finally:os.close(fd)
  same=(st['st_dev'],st['st_ino'])==(anchor['metadata']['st_dev'],anchor['metadata']['st_ino']);assert same==(old['sameAnchorInode'] or old['path'] in {x['retainedCandidateAlias']['path'] for x in media})
  if same:assert st==anchor['metadata'];count+=1
  else:assert all(st[k]==v for k,v in old['lstat'].items() if k!='st_atime_ns')
  known.append({'path':old['path'],'sameAnchorInode':same,'metadata':st})
 assert anchor['metadata']['st_nlink']-count==z['unresolvedPhysicalAliasCount']
 aliases.append({'anchor':z['anchor'],'knownPhysicalCountIncludingNewCandidate':count,'unresolvedPhysicalAliasCount':z['unresolvedPhysicalAliasCount'],'knownMetadataOnly':known})
protected_after=md(os.lstat(protected));assert protected_after==protected_before
assert result['grossAllocationBytes']==sum(x['candidate']['fstat']['st_blocks']*512 for x in e['pairs'])==10170368
assert result['netWindowGainBytes']==result['windowFreeAfterBeforeResultWrite']-result['windowFreeBefore']==10137600
rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024;assert rss<24*1048576
save('PROOF.json',{'proposal':pp,'admissionGate':gp,'priorPhysicalGate':priorp,'priorTenBodyProof':priorproof,'producer':jp,'confirmedPush':pushp,'sourceHoldAndMapPins':sourcepins,'actionBefore':bp,'actionResult':rp,'actionJournal':journalp,'journalRows':rows,'durablePrefixQualification':'15 observed records + normal pinned method source/guard establish returned fsync per-leaf prefix; no crash injection/whole-five atomicity or universal filesystem durability','actionGuardPins':[adp,grp,glp],'actionGuardNormal':True,'fullTenBodiesAndStatsXattrs':media,'originalMetadataRetained':original,'fullCurrent143Bodies':current,'selectedMap':mp,'knownAliasMetadata':aliases,'protectedZipStatBefore':protected_before,'protectedZipStatAfter':protected_after,'protectedZipBodyNeverOpened':True,'grossAllocationBytes':10170368,'actionPreResultNetWindowGainBytes':10137600,'gainQualification':'Historical action window free-space difference, not reviewer exclusive allocation or exact end-to-end net gain after publication/POST','historicalFull66_51AggregateNotReplayed':True,'ownMaxRSSBytes':rss,'streamChunkBytes':65536,'allInputFDsClosed':True,'noGitActionNodeBrowserImageOrCleanup':True,'normal64PostGuardRequired':True})
print(json.dumps({'postNormal':True,'fullMediaBodies':10,'fullCurrentBodies':143,'journalRecords':15,'nlinks':[x['canonical']['metadata']['st_nlink'] for x in media],'gross':10170368,'actionWindowGain':10137600,'ownMaxRSSBytes':rss,'allFDsClosed':True}))
