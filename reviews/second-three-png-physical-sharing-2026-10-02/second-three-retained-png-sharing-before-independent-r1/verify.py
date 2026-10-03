import pathlib,os,json,hashlib,stat,resource,ast,time
out=pathlib.Path(__file__).parent;p=pathlib.Path('/workspace/scratch/media-loose-png-recovery-proposal-author-r2');repo=pathlib.Path('/workspace/Roguelike-deckbuilder')
fields=['st_dev','st_ino','st_mode','st_nlink','st_uid','st_gid','st_size','st_blocks','st_atime_ns','st_mtime_ns','st_ctime_ns']
def metadata(s):return {k:getattr(s,k) for k in fields}
def stream(path):
 path=pathlib.Path(path);parent=pathlib.Path('/');fds=[]
 try:
  fd=os.open('/',os.O_PATH|os.O_DIRECTORY|os.O_NOFOLLOW);fds.append(fd)
  for part in path.parts[1:-1]:fd=os.open(part,os.O_PATH|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd);fds.append(fd)
  fd=os.open(path.name,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW,dir_fd=fd);fds.append(fd);before=metadata(os.fstat(fd));assert stat.S_ISREG(before['st_mode'])
  h=hashlib.sha256();n=0
  while True:
   b=os.read(fd,65536)
   if not b:break
   h.update(b);n+=len(b)
  attrs={k:os.getxattr(fd,k).hex() for k in os.listxattr(fd)};after=metadata(os.fstat(fd));assert before==after
  return {'path':str(path),'sha256':h.hexdigest(),'bytes':n,'metadata':before,'xattrs':attrs,'readMetadataExact':True,'method':'O_PATH nofollow directory chain; regularbody O_NOATIME|O_NOFOLLOW65536B stream; FD xattrs/fstat; all FDs closed'}
 finally:
  for fd in reversed(fds):os.close(fd)
def small(path):
 fd=os.open(path,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW)
 with os.fdopen(fd,'rb') as f:return f.read()
def rec(path):
 b=small(path);return {'path':str(path),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
def obj(path):return json.loads(small(path))
assert rec(p/'PROPOSAL.json')['sha256']=='45ed75b5078c84e32981ba86b43f62826b00c53278ef8ea2f9888d661b8fd8d5'
assert rec(p/'FINAL-SEAL.json')['sha256']=='dad72be52657ee9538a209b9c1ac0e703dad6b57380463443f15916b8aae1fe7'
proposal=obj(p/'PROPOSAL.json');seal=obj(p/'FINAL-SEAL.json')
for r in seal['files']:assert rec(r['path'])=={k:r[k] for k in ['path','sha256','bytes']}
assert len(proposal['pairs'])==3
pairs=[];names={'abbey-courtyard.png','tool-vignettes.png','hunter-portrait.png'}
assert {pathlib.Path(r['candidate']['path']).name for r in proposal['pairs']}==names
for r in proposal['pairs']:
 assert set(r)=={'candidate','anchor','exactFullBodyAndRightsFieldsEqual'}
 c=stream(r['candidate']['path']);a=stream(r['anchor']['path'])
 for k,l in [(c,r['candidate']),(a,r['anchor'])]:
  assert k['sha256']==l['sha256'] and k['metadata']==l['lstat']==l['fstat'] and k['xattrs']==l['xattrs']=={}
 assert c['sha256']==a['sha256'] and c['metadata']['st_nlink']==1 and a['metadata']['st_nlink']==5 and c['metadata']['st_dev']==a['metadata']['st_dev']==27
 for k in ['st_mode','st_uid','st_gid','st_size']:assert c['metadata'][k]==a['metadata'][k]
 pairs.append({'candidate':c,'anchor':a})
assert sum(r['candidate']['metadata']['st_blocks']*512 for r in pairs)==proposal['grossOldAllocationBytes']==8499200
assert sum(r['candidate']['bytes'] for r in pairs)==proposal['logicalOldBytes']==8492116
aliases=[]
for group in proposal['knownAnchorAliases']:
 assert group['knownPhysicalEntryCount']==4 and group['anchorNlink']==5 and group['unresolvedPhysicalAliasCount']==1
 entries=[]
 for r in group['knownPhysicalEntries']:
  s=os.lstat(r['path']);assert metadata(s)==r['lstat'];entries.append({'path':r['path'],'metadata':metadata(s),'bodyIdentityInferredFromSameDevInode':True})
 aliases.append({'anchor':group['anchor'],'knownPhysicalEntries':entries,'unresolvedPhysicalAliasCount':1,'noUniversalLogicalOrProcessAliasProof':True})
agents=rec(repo/'AGENTS.md');assert agents['sha256']=='69a82ce96a594a2b2a5244154de8758b200290ba9de46b40a221a52ba4a0cfb7'
hold=next(line for line in small(repo/'AGENTS.md').decode().splitlines() if 'independent/rebuilt-dist/art/abbey-courtyard.png' in line)
assert 'immutable and fresh-stage-only' in hold and 'no writes, truncation, chmod, xattr or timestamp' in hold
consumer=obj(p/'HISTORICAL-CONSUMER.json');controls=[]
for r in proposal['sourceControls']:
 if pathlib.Path(r['path'])==repo/'AGENTS.md':continue
 now=rec(r['path']);assert now['sha256']==r['sha256'];controls.append(now)
historical=[]
for path,pin in [('/workspace/scratch/audio-host-independent-v08/candidate/SOURCE-MANIFEST.json',consumer['declaredSourceManifestSHA']),('/workspace/scratch/audio-host-independent-v08/candidate/BUILD-MANIFEST.json',consumer['declaredBuildManifestSHA'])]:
 now=rec(path);assert now['sha256']==pin;historical.append(now)
for path in ['/workspace/scratch/audio-host-independent-v08/independent/rebuilt-dist/art/PROVENANCE.json','/workspace/scratch/audio-host-independent-v08/candidate/public/art/PROVENANCE.json','/workspace/scratch/audio-host-independent-v08/independent/independent-rebuild.json','/workspace/scratch/audio-host-independent-v08/independent/vite-rebuild-r1.log']:
 historical.append(rec(path))
assert historical[2]['sha256']==historical[3]['sha256']
selectedpath=pathlib.Path('/workspace/scratch/target-wait-default-promotion-root-r1/RESULT.json');selected=obj(selectedpath)
assert len(selected['canonicalInputs'])==87 and len(selected['canonicalOutputs'])==56
maps={}
for key,prefix in [('canonicalInputs',repo),('canonicalOutputs',repo/'dist')]:
 rows=[]
 for path,pin in selected[key].items():
  now=stream(prefix/path);assert now['sha256']==pin;rows.append({'path':path,'bytes':now['bytes'],'sha256':now['sha256']})
 maps[key]=rows
protectedpath=pathlib.Path('/workspace/scratch/retained-original-archives/preflight-bdf273-original-r4.zip');protected=metadata(os.lstat(protectedpath));assert (protected['st_dev'],protected['st_ino'],protected['st_size'],protected['st_nlink'])==(27,678628,1856041104,1)
methodpath=pathlib.Path('/workspace/scratch/share-second-three-retained-pngs-root-r1.py');method=small(methodpath).decode();assert rec(methodpath)['sha256']=='c0ce34ca0ba7675d2dd3ed1a3f5d93548d7285f2b621fb267496aa484eeebbb0';ast.parse(method)
assert "for kind in ['candidate','canonical']:" in method and all('canonical' not in r for r in proposal['pairs'])
rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss;assert rss<24*1024
proof={'proposal':rec(p/'PROPOSAL.json'),'authorSeal':rec(p/'FINAL-SEAL.json'),'authorSealedBodiesAllVerified':True,'pairs':pairs,'knownAliases':aliases,'grossCandidateAllocationBytes':8499200,'logicalCandidateBytes':8492116,'currentHold':{'receipt':agents,'instruction':hold,'authorPinnedEarlierAGENTS':'f9bb313329762de931904873238474de8cfb209c30835856c5c83a7eaadbb463','currentHoldIndependentlyCheckedNotClaimedInAuthorSeal':True},'sourceControls':controls,'historicalControls':historical,'historicalAggregate':{'sourceDigest':consumer['historicalSourceDigest'],'sourceInputs':66,'builtOutputs':51,'basis':'Exact pinned oldindependentreview/manifest receipts; wholehistorical66/51 notfreshlyrehashed','consumerPurpose':consumer['consumerNeed']},'selectedMap':rec(selectedpath),'selectedMapsFreshVerified':maps,'protectedArchiveStatOnly':{'path':str(protectedpath),'metadata':protected,'bodyFreshlyHashed':False},'methodR1':rec(methodpath),'actionSourceDecision':'REJECT_EXACT_METHOD_R1_SCHEMA_AND_IDENTITY_RECHECK','blockers':['Proposal pairs use anchor, method reads canonical; deterministic KeyError beforelink','No held nofollow FD/parent identity controls and perrecipient body/stat revalidation atlink/replace boundary as proposed','Proposal describes retained oldinodebackups while Root exactmethod hasnone; immediate originalinode/time rollback unavailable, explicit independentjudgment needed'],'sharingPreference':'Exact logicalbits can be preserved more efficiently undercurrenthold, conditionally; independent writable privateinodes add no uniquepixels/rights/source, originalmetadata/consumerrecords remainneeded. No positive exactactiongate for brokenmethod.','producerAndFreshCurrentPush':'PENDING; not verifiedbyreviewer/noGitcalled','ownRSSKiB':rss,'resourceQualification':'64MiB coordinatedaggregate+512reserve/disk64 sourceadmission, ownRSS<24; sharedsampled deltas, noexclusive attribution. OnlyPNGstreams notdecode; noimages/Git/action.','utcNs':time.time_ns()}
(out/'PROOF.json').write_text(json.dumps(proof,indent=2)+'\n')
total=sum(x.stat().st_size for x in out.rglob('*') if x.is_file());assert total<=192*1024
print(json.dumps({'pairBodiesAndMetadataVerified':3,'knownAliasPaths':12,'unknownPhysicalAliasPerAnchor':1,'selectedFreshMaps':[87,56],'gross':8499200,'ownRSSKiB':rss,'packetBytes':total,'methodDecision':proof['actionSourceDecision'],'historicalControls':historical}))
