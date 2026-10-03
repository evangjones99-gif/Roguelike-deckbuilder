import os,stat,time,json,hashlib,resource,pathlib
root=pathlib.Path(__file__).parent
cg=pathlib.Path('/sys/fs/cgroup');base=int((cg/'memory.current').read_text());events=(cg/'memory.events').read_text();rows=[]
def guard(label):
 c=int((cg/'memory.current').read_text());m=int((cg/'memory.max').read_text());v=os.statvfs(root);rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024
 row={'label':label,'time_ns':time.time_ns(),'sharedDelta':c-base,'headroom':m-c,'workspaceFree':v.f_bavail*v.f_frsize,'ownMaxRSS':rss};rows.append(row)
 assert row['sharedDelta']<=64*1048576 and row['headroom']>=512*1048576 and row['workspaceFree']>=64*1048576 and rss<24*1048576
 assert events==(cg/'memory.events').read_text();return row
def metadata(s):
 return {k:getattr(s,k) for k in ['st_dev','st_ino','st_mode','st_nlink','st_uid','st_gid','st_size','st_blocks','st_atime_ns','st_mtime_ns','st_ctime_ns']}
def pin(path):
 fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME)
 try:
  before=os.fstat(fd);x={n:os.getxattr(fd,n).hex() for n in os.listxattr(fd)};h=hashlib.sha256()
  while True:
   body=os.read(fd,65536)
   if not body:break
   h.update(body);guard('64KiB body')
  after=os.fstat(fd);y={n:os.getxattr(fd,n).hex() for n in os.listxattr(fd)}
  assert metadata(before)==metadata(after) and x==y and stat.S_ISREG(before.st_mode)
  return {'path':path,'sha256':h.hexdigest(),'metadata':metadata(before),'xattrs':x,'duringReadMetadataExact':True,'O_NOATIME':True}
 finally:os.close(fd)
initial=guard('initial')
controls=[pin('/workspace/Roguelike-deckbuilder/AGENTS.md'),pin('/workspace/scratch/standard-sol-historical-dist-media-dedup-proposal-r1/PROPOSAL.md'),pin('/workspace/scratch/root-dist-media-hardlink-plan-independent-v09-r1/PLAN.md')]
names=['abbey-courtyard.png','tool-vignettes.png','hunter-portrait.png']
historical='/dev/shm/hollowpact-owner-tactile-pc-root-r4/public/art'
canonical='/workspace/Roguelike-deckbuilder/public/art'
pairs=[]
for name in names:
 old=pin(historical+'/'+name);retained=pin(canonical+'/'+name)
 assert old['sha256']==retained['sha256'] and old['metadata']['st_size']==retained['metadata']['st_size']
 pairs.append({'historical':old,'retainedCanonical':retained,'exactBodyEqual':True,'sameDevice':old['metadata']['st_dev']==retained['metadata']['st_dev']})
aliases=[]
for name in ['first-five-opening-stage-r2','first-five-opening-hand-cue-stage-r1','first-five-opening-hand-cue-terminal-stage-r1','first-five-opening-readout-stage-r1']:
 p='/workspace/scratch/'+name+'/public';s=os.lstat(p)
 assert stat.S_ISLNK(s.st_mode)
 aliases.append({'publicAlias':p,'symlinkLstat':metadata(s),'previousReadlinkObservedTarget':'/dev/shm/hollowpact-owner-tactile-pc-root-r4/public','selectedLeafIdentities':[{'path':p+'/art/'+n,'metadata':metadata(os.stat(p+'/art/'+n))} for n in names]})
filesystems=[]
for p in ['/workspace','/dev/shm/hollowpact-owner-tactile-pc-root-r4/public']:
 s=os.stat(p);v=os.statvfs(p);filesystems.append({'path':p,'device':s.st_dev,'statvfs':{'blockSize':v.f_frsize,'freeBytes':v.f_bavail*v.f_frsize,'totalBytes':v.f_blocks*v.f_frsize}})
logical=sum(x['historical']['metadata']['st_size'] for x in pairs);allocated=sum(x['historical']['metadata']['st_blocks']*512 for x in pairs)
evidence={'decision':'REJECT this candidate as workspace admission recovery; no storage action proposed or authorized.','controls':controls,'exactCandidatePairs':pairs,'knownHistoricalAliases':aliases,'filesystems':filesystems,'onePhysicalHistoricalGroup':True,'selectedLogicalBytes':logical,'selectedAllocatedBytesOnDevShm':allocated,'workspaceRecoveryBytes':0,'crossDeviceHardlinksPossible':False,'coverage':'Exactly three media leaves and their four known historical public symlink aliases. Canonical inode link counts are recorded, but additional aliases are not exhaustively inventoried because the candidate already fails the required filesystem benefit. No broader path/action proposal.','holdFinding':'AGENTS explicitly freezes the four historical dist media trees, not these old public symlink targets. Canonical public has a hold. A future action involving this historical public tree would require exact public-target and all known alias write holds, independent review and producer judgment; existing dist holds do not supply that designation.','historicalNeed':'Keep old tree untouched. It remains the media source for all four public aliases and retains independent physical isolation on another device; no claim that this representation is no longer needed follows. The old dist transaction excluded source/public and required reproductions in fresh stages.','lossAndRollback':'No byte/path/inode/xattr/timestamp changes, relocation, hardlink, unlink or backup retirement intentionally performed. Cross-device sharing would require a different representation and could surrender filesystem placement and writable isolation; not reviewed or recommended. Existing paths/rights/provenance remain.','discoveryQualification':'Initial small AGENTS/body reads used O_NOATIME; exploratory directory reads used O_DIRECTORY|O_NOATIME. Discovery output listing was truncated, then the focused exact candidate was reread under this guard. Initial readlink/realpath discovery had no prior symlink metadata snapshot, so any incidental symlink-access-time change is unknown and is not claimed absent. No timestamp setter, chmod, xattr write or source body write was used.','protectedArchive':'Excluded; not read or scanned.','resourceScope':'Own RSS below24MiB; observed shared delta64MiB plus512MiB reserve and64MiB initial workspace disk. Tiny Root/independent reads may coexist; no exclusive system attribution or complete resource accounting of preliminary discovery calls.'}
with (root/'EVIDENCE.json').open('x') as f:json.dump(evidence,f,indent=2);f.write('\n')
final=guard('final')
with (root/'RESOURCE.json').open('x') as f:json.dump({'initial':initial,'rows':rows,'final':final,'eventsBefore':events,'eventsAfter':(cg/'memory.events').read_text(),'allInputFDsClosed':True},f,indent=2);f.write('\n')
print(json.dumps({'decision':evidence['decision'],'logicalBytes':logical,'allocatedOnDevShm':allocated,'workspaceRecovery':0,'final':final}))
