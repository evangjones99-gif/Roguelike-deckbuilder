import pathlib,os,json,hashlib,resource,stat,ast,time
p=pathlib.Path(__file__).parent;r1=pathlib.Path('/workspace/scratch/second-three-retained-png-sharing-before-independent-r1');repo=pathlib.Path('/workspace/Roguelike-deckbuilder')
def read(path):
 fd=os.open(path,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW)
 with os.fdopen(fd,'rb') as f:return f.read()
def rec(path):
 b=read(path);return {'path':str(path),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
old=json.loads(read(r1/'PROOF.json'));fields=list(old['pairs'][0]['candidate']['metadata'])
def md(t):return {k:getattr(t,k) for k in fields}
def leafmeta(path):
 path=pathlib.Path(path);fd=os.open('/',os.O_PATH|os.O_DIRECTORY|os.O_NOFOLLOW)
 try:
  for part in path.parts[1:-1]:
   nextfd=os.open(part,os.O_PATH|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd);os.close(fd);fd=nextfd
  before=md(os.stat(path.name,dir_fd=fd,follow_symlinks=False));assert stat.S_ISREG(before['st_mode'])
  f=os.open(path.name,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW,dir_fd=fd)
  try:assert md(os.fstat(f))==before;attrs={k:os.getxattr(f,k).hex() for k in os.listxattr(f)}
  finally:os.close(f)
  assert md(os.stat(path.name,dir_fd=fd,follow_symlinks=False))==before
  return {'path':str(path),'metadata':before,'xattrs':attrs,'bodyIdentityBasis':'Prior fullbody stream in pinnedr1proof plus freshcomplete dev/inode/ctime/mtime/size/stat equality; no freshbody stream inr2.'}
 finally:os.close(fd)
assert rec(r1/'R1-GATE.json')['sha256']=='7a2d1d45958e8f280356e7e10606f507392d4a85c9ed12a4a20961e6868ad831'
assert json.loads(read(r1/'R1-GATE.json'))['decision']=='REJECT_EXACT_METHOD_R1_SCHEMA_AND_IDENTITY_RECHECK'
for entry in json.loads(read(r1/'R1-MANIFEST.json'))['files']:assert rec(entry['path'])==entry
assert rec(old['proposal']['path'])==old['proposal'] and rec(old['authorSeal']['path'])==old['authorSeal']
assert rec(old['selectedMap']['path'])==old['selectedMap']
assert rec(old['currentHold']['receipt']['path'])==old['currentHold']['receipt']
fresh=[]
for pair in old['pairs']:
 for key in ['candidate','anchor']:
  now=leafmeta(pair[key]['path']);assert now['metadata']==pair[key]['metadata'] and now['xattrs']==pair[key]['xattrs'];fresh.append(now)
aliases=[]
for group in old['knownAliases']:
 for entry in group['knownPhysicalEntries']:
  now=md(os.lstat(entry['path']));assert now==entry['metadata'];aliases.append({'path':entry['path'],'metadata':now})
assert md(os.lstat(old['protectedArchiveStatOnly']['path']))==old['protectedArchiveStatOnly']['metadata']
for control in old['sourceControls']+old['historicalControls']:assert rec(control['path'])==control
method=pathlib.Path('/workspace/scratch/share-second-three-retained-pngs-root-r2.py');body=read(method).decode();pin=rec(method);assert pin['sha256']=='3ac77cbd683f43b00910066dc8248d6a77e2576df9111f30c856558555e62d99';ast.parse(body)
for fragment in ["a=x['anchor'];b=x['candidate']",'os.O_PATH|os.O_DIRECTORY|os.O_NOFOLLOW','os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME','src_dir_fd=af,dst_dir_fd=bf,follow_symlinks=False','os.replace(tmp,bp.name,src_dir_fd=bf,dst_dir_fd=bf)','leafcheck(af,ap.name,now',"assert md(os.stat(bp.name,dir_fd=bf,follow_symlinks=False))==x['candidate']['fstat']","'PRE_LINK'","'LINK_DURABLE'","'REPLACED_DURABLE'",'finally:\n    for x,af,bf,ap,bp in handles:os.close(af);os.close(bf)']:assert fragment in body
assert 'backup' in body and "'canonical'" not in body
rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss;assert rss<24*1024
proof={'sourceDecision':'ACCEPT_EXACT_THREE_PATH_SHARING_AND_R2_ACTION_SOURCE_CONDITIONAL_PUSH_PRODUCER','methodR2':pin,'proposal':old['proposal'],'authorSeal':old['authorSeal'],'currentHold':old['currentHold']['receipt'],'priorR1Proof':rec(r1/'PROOF.json'),'priorR1GateRejection':rec(r1/'R1-GATE.json'),'priorR1Review':rec(r1/'R1-REVIEW.md'),'priorR1Manifest':rec(r1/'R1-MANIFEST.json'),'priorR1FinalSeal':rec(r1/'R1-FINAL-SEAL.json'),'freshSixLeafMetadata':fresh,'freshKnownAliasStats':aliases,'freshProtectedStatMatchesR1':True,'oldConsumerAndProvenanceControlPinsStillMatch':True,'selectedMap':old['selectedMap'],'selectedBodyVerificationBasis':'Prior pinnedr1 fresh87/56 full streams; r2 verifies map control identity only; method itself independently fullchecks selectedmaps before andafter action. Wholehistorical66/51 stillnotfreshlyrehashed.','sharingPreference':'Exact three privateoutput PNG encodings carry no unique pixels/source/rights/provenance; under exactcurrentheldfreshstagepaths, canonicalshared physicalencoding is preferred for potentialallocation recovery. Alllogicalpaths/bodies/consumerrecords stillneeded. Independentwritableinode/time isolation is no longerneeded as productionproperty for these frozenoutputs, acceptedlosses explicit.','grossPotentialBytes':8499200,'logicalThreeBytes':8492116,'oldPhysicalInodesNeeded':False,'originalMetadataConsumerProvenanceRecordsNeeded':True,'unknownAliases':'Exactly4known physicalentries peranchor verified againstnlink5; onephysicalalias peranchor unresolved; no symlink/FD/mmap/futurewriter absence proof. Accept disclosedshared nlink/ctime effects includingunknownalias, not universalaliasaccounting.','durabilityReview':'Allthree preflight beforeevidencedir/mutation; BEFORE file+parentfsync; PRE_LINK durablefile/dir prefix; temp hardlink+recipientdirfsync; LINK_DURABLE journal; atomicreplace+recipientdirfsync; REPLACED_DURABLE journal; postbody/stat checks; RESULT durable. Perpathatomic durableprefix, notallthreeatomic. Heldnofollow parentFDs and boundedregularbody rechecks, allheldFDs finallyclosed.','noBackupVariant':'Root explicitno-oldinodebackup scope supersedes author backup suggestion without rewritingit; exactoldprivateinodes lostimmediately atreplace, no originalkernelinode/ctime rollback, logicalbyte/rights reconstruction only.','losses':['recipientoriginalinode/atime/mtime/ctime identity andindependentwrite/metaisolation lost','anchorsnlink5to6/ctime changes acrossall oldaliases includingunknownone','candidateparentmtime/ctime changes','originalprivateFD/mmap consumers notexcluded andcoulddelaygrossreclamation','postRESULT/review/push costs outside reportedfreewindow; noguaranteed8MiBnetgain'],'producerAndFreshCurrentPush':'PENDING atreview; method requires pinnedproducer decision/proposal/gate/self/hold/selectedmap/pushcommit+cleanbranchcurrentcommit beforemutation. Root soleactualgrant stillrequired; no transaction performed byreviewer.','ownRSSKiB':rss,'resourceQualification':'64MiB coordinatedaggregate+512reserve/disk64 sourceadmission, ownRSS<24; no image/decode/Node/browser/Git/action; aggregate sampled notexclusive attribution.','utcNs':time.time_ns()}
(p/'PROOF.json').write_text(json.dumps(proof,indent=2)+'\n')
print(json.dumps({'method':pin,'freshSixLeafStats':6,'freshKnownAliasStats':12,'ownRSSKiB':rss,'decision':proof['sourceDecision'],'grossPotentialBytes':8499200}))
