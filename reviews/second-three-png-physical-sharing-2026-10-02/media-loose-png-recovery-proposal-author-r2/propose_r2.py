import os,stat,pathlib,json,hashlib,time,resource
resource.setrlimit(resource.RLIMIT_DATA,(24*1048576,24*1048576))
R=pathlib.Path(__file__).parent;CG=pathlib.Path('/sys/fs/cgroup');BASE=int((CG/'memory.current').read_text());EVENTS=(CG/'memory.events').read_text();START=time.monotonic();ROWS=[]
NAMES=['abbey-courtyard.png','tool-vignettes.png','hunter-portrait.png']
CAND='/workspace/scratch/audio-host-independent-v08/independent/rebuilt-dist/art'
ANCH='/workspace/Roguelike-deckbuilder/public/art'
def guard(label):
 c=int((CG/'memory.current').read_text());m=int((CG/'memory.max').read_text());v=os.statvfs(R);rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024
 row={'label':label,'elapsed':time.monotonic()-START,'sharedDelta':c-BASE,'headroom':m-c,'free':v.f_bavail*v.f_frsize,'ownMaxRSS':rss};ROWS.append(row)
 assert row['sharedDelta']<=64*1048576 and row['headroom']>=512*1048576 and row['free']>=64*1048576 and rss<24*1048576 and row['elapsed']<60 and EVENTS==(CG/'memory.events').read_text()
 return row
def meta(s):return {k:getattr(s,k) for k in ['st_dev','st_ino','st_mode','st_nlink','st_uid','st_gid','st_size','st_blocks','st_atime_ns','st_mtime_ns','st_ctime_ns']}
def parent_hold(path):
 fd=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_NOATIME)
 observed=[]
 try:
  for part in pathlib.Path(path).parts[1:]:
   nxt=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_NOATIME,dir_fd=fd)
   os.close(fd);fd=nxt;observed.append({'component':part,'metadata':meta(os.fstat(fd))})
  return fd,observed
 except BaseException:os.close(fd);raise
def pin(path,body=False):
 parent,name=os.path.split(path);pfd,ancestors=parent_hold(parent)
 fd=None
 try:
  lstat=os.stat(name,dir_fd=pfd,follow_symlinks=False)
  fd=os.open(name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME,dir_fd=pfd);before=os.fstat(fd)
  assert stat.S_ISREG(before.st_mode) and meta(lstat)==meta(before)
  xs={n:os.getxattr(fd,n).hex() for n in os.listxattr(fd)};h=hashlib.sha256();buf=b''
  while True:
   b=os.read(fd,65536)
   if not b:break
   h.update(b)
   if body:buf+=b;assert len(buf)<128*1024
  assert meta(before)==meta(os.fstat(fd)) and xs=={n:os.getxattr(fd,n).hex() for n in os.listxattr(fd)} and meta(before)==meta(os.stat(name,dir_fd=pfd,follow_symlinks=False))
  guard('stream-closed')
  return {'path':path,'sha256':h.hexdigest(),'lstat':meta(lstat),'fstat':meta(before),'xattrs':xs,'ancestorsNoSymlink':ancestors,'O_NOATIME':True,'duringReadMetadataExact':True},buf
 finally:
  if fd is not None:os.close(fd)
  os.close(pfd)
def write(name,body):
 with (R/name).open('x') as f:json.dump(body,f,indent=2);f.write('\n')
initial=guard('initial')
r1pin,r1body=pin('/workspace/scratch/media-loose-png-recovery-proposal-author-r1/EVIDENCE.json',True)
r1=json.loads(r1body);assert r1['selectedGroup']!=CAND and r1['verification']=='EXACT_MATCH'
oldpin,oldbody=pin('/workspace/scratch/audio-host-independent-v08/independent/REVIEW.md',True)
old=oldbody.decode();assert 'new output directory' in old and 'every51 author build file byte-for-byte' in old and 'not approved for production promotion' in old
agpin,agbody=pin('/workspace/Roguelike-deckbuilder/AGENTS.md',True)
pairs=[];alias=[];parents=[]
for name in NAMES:
 cp,_=pin(CAND+'/'+name);ap,_=pin(ANCH+'/'+name)
 assert cp['fstat']['st_dev']==ap['fstat']['st_dev']==27 and cp['fstat']['st_nlink']==1 and ap['fstat']['st_nlink']==5 and cp['fstat']['st_ino']!=ap['fstat']['st_ino']
 assert cp['sha256']==ap['sha256'] and cp['fstat']['st_size']==ap['fstat']['st_size']
 assert all(cp['fstat'][k]==ap['fstat'][k] for k in ['st_mode','st_uid','st_gid']) and cp['xattrs']==ap['xattrs']
 pairs.append({'candidate':cp,'anchor':ap,'exactFullBodyAndRightsFieldsEqual':True})
 known=[ANCH+'/'+name,'/workspace/scratch/first-five-opening-cairn128-ready-stage-r1/public/art/'+name,'/workspace/scratch/first-five-opening-cairn128-ready-stage-r1/dist/art/'+name,'/workspace/scratch/audio-host-independent-v08/candidate/dist/art/'+name]
 entry=[]
 for p in known:
  s=os.stat(p,follow_symlinks=False);assert s.st_dev==ap['fstat']['st_dev'] and s.st_ino==ap['fstat']['st_ino']
  entry.append({'path':p,'lstat':meta(s)})
 alias.append({'anchor':ap['path'],'knownPhysicalEntries':entry,'knownPhysicalEntryCount':4,'anchorNlink':5,'unresolvedPhysicalAliasCount':1,'qualification':'Known physical entries only; no universal logical-symlink/process/mmap/future-writer absence proof. All existing canonical/frozen holds remain applicable; sharing implies unchanged bytes, not unchanged shared metadata.'})
for path in [CAND,ANCH]:
 fd,parts=parent_hold(path)
 try:parents.append({'path':path,'fstat':meta(os.fstat(fd)),'xattrs':{n:os.getxattr(fd,n).hex() for n in os.listxattr(fd)}})
 finally:os.close(fd)
gross=sum(x['candidate']['fstat']['st_blocks']*512 for x in pairs);logical=sum(x['candidate']['fstat']['st_size'] for x in pairs)
assert gross>=8*1048576
proof={'decision':'Conditional second historical exact-three-PNG encoding proposal only; no action/recovery/independent approval/producer judgment.','candidateGroup':CAND,'pairs':pairs,'knownAnchorAliases':alias,'parentMetadata':parents,'grossOldAllocationBytes':gross,'logicalOldBytes':logical,'sourceControls':[r1pin,oldpin,agpin],'selection':'Exactly one different historical independent rebuild group; no inventory walk or second body group. Not selected currentdist/frozen protected/release/original archive. R1 retained unchanged.','historicalConsumer':'Old independent REVIEW records exterior source eb1e4fcadd0b166092484bf9e7ebddfc4e51f3811e3154a24c8b42663273b1fd,66 inputs/51 outputs and exact rebuild with declared VITE_BUILD_ID into a new output directory. Dev4193/built4195 diagnostics remain retained; host was rejected for production promotion because automatic resize removed binding visuals while sounds stayed scheduled. This group is the historical reproduced output, not current production.','oldPhysicalEncodingNeed':'Byte-for-byte reconstruction and the original method/result/source/manifests are still useful and must remain. Separate writable copies of these three output media add no different source/rights/diagnostic pixels. Under exact immutable/fresh-stage-only holds, shared storage can preserve every historical path/body/result while recovering only redundant allocation. That is a conditional author preference; independent review must verify and prefer the replacement, then producer judge old independent physical isolation unnecessary.','futureHold':'Root must designate exactly CAND plus the three named existing leaves immutable/fresh-stage-only, forbid rebuild/in-place copy/chmod/xattrs/timestamp writes through these or any anchor aliases, and use fresh stages/new inodes for reproductions. This packet does not claim that new hold already exists or is OS enforced. Existing canonical/public/frozen/trace media holds do not imply a hold on this rebuild.','metadataIsolationLosses':'Candidate inode identities ultimately disappear after separately reviewed backup retirement. Shared recipients inherit anchor atime/mtime; anchor nlink5→6 and ctime change through all five existing physical aliases, including one unresolved alias. Parent mtime/ctime change. Independent writable/per-path metadata isolation is lost. Do not equalize shared timestamps/modes/xattrs. Original stat/xattr ledgers are retained; no exact kernel inode/ctime rollback after original retirement.','knownAliasGap':'Candidate nlink1 records one physical entry per image, but consumers via symlinks/FD/mmap/future code are not excluded. Four anchor physical entries match current stat; one of nlink5 remains unidentified. Independent action review must accept or resolve that exact gap and validate byte maps before/post; no universal alias metadata proof.','prospectiveTransaction':'Root-only separately authored finite durable before/journal/fsync transaction with nofollow held identity rechecks, three unique sibling temp hardlinks/atomic replacements, retained old inode backups until independent postchecks/producer retirement judgment. No implementation or authorization supplied here.','preservation':'All historical source/art inputs, unique files, review/failures/manifests/rights/provenance, paths and exact bodies remain; original aggregate identities remain truthful historical byte maps. Supplemental inode/time differences must be preserved explicitly. No whole-tree retirement or placeholder.','capacity':'Gross allocation is prospective. Current packet, independent review, journal/backups/push footprints reduce net and backups delay actual recovery. Fresh resource admission after authorized recovery is mandatory; no8MiB net guarantee. Root must publish r1 POST/rejected-ghost evidence and current push before any new action.','scope':'Only six PNG body streams (candidate3 + anchor3) and small text/JSON control streams. No metadata broad walk, archives, release bodies, decode, Node/imported application/browser/native/Git/build/canonical mutation/storage action. All source FDs closed.'}
write('PROPOSAL.json',proof)
report='Propose only the three existing PNGs abbey-courtyard.png, tool-vignettes.png and hunter-portrait.png in '+CAND+' for separately reviewed exact-byte physical sharing. They are a different historical output group from r1: independent device27/nlink1 files, fully SHA-equal to held canonical anchors now nlink5, with matching0600/uid1000/gid1000/empty xattrs. Gross allocation is '+str(gross)+' bytes. No space was recovered.\n\nThis is the preserved old independent audio-host rebuild, whose original review/source/output/method remain useful even though that host was rejected for production promotion. Keep every path/body/provenance/rights/review and exact reproduction identity. Independent physical copies of these three immutable output pixels contain no unique information; sharing is preferable only after a named immutable/fresh-stage-only hold and independent judgment accept the loss of inode/time/write isolation. New reproduction uses fresh stages. The new hold is proposed, not claimed published or OS-enforced.\n\nFour known existing anchor directory entries are pinned; anchor nlink5 leaves one unresolved existing physical alias per image. Candidate nlink1 does not prove absence of symlink/FD/mmap/future consumers. Sharing would preserve bytes but change anchor nlink to6 and ctime for all existing aliases; recipients inherit anchor metadata and lose independent inodes after separately reviewed retirement. Preserve original metadata and backups/rollback; exact original inode/ctime history cannot be recreated afterward. Gross allocation is not an8MiB net guarantee. Current push, r1POST/rejected-ghost preservation, independent preference, producer judgment, exact journalled method and fresh capacity precede any action.\n\nNo source/media/path/metadata mutation, decode, build, Node, browser/native, Git, archive scan or second group search was performed. O_NOATIME full streams held nofollow parents and captured stable lstat/fstat/xattrs. Prior r1 proof/failure packets stay unchanged.\n'
with (R/'PROPOSAL.md').open('x') as f:f.write(report)
final=guard('final')
write('RESOURCE.json',{'initial':initial,'rows':ROWS,'final':final,'eventsBefore':EVENTS,'eventsAfter':(CG/'memory.events').read_text(),'ownRSSHardLimitMiB':24,'qualifiedAggregateMiB':64,'reserveMiB':512,'qualification':'Own sampled maxRSS plus RLIMIT_DATA24; observed shared cgroup delta is not exclusive attribution. Two other tiny source readers may coexist; no heavy actor. All FDs closed.'})
print(json.dumps({'candidate':CAND,'gross':gross,'logical':logical,'final':final}))
