import os,stat,pathlib,json,hashlib,time,resource
r=pathlib.Path(__file__).parent;cg=pathlib.Path('/sys/fs/cgroup');base=int((cg/'memory.current').read_text());events=(cg/'memory.events').read_text();start=time.monotonic();rows=[]
NAMES=['abbey-courtyard.png','tool-vignettes.png','hunter-portrait.png'];canonical='/workspace/Roguelike-deckbuilder/public/art'
def guard(label):
 c=int((cg/'memory.current').read_text());m=int((cg/'memory.max').read_text());v=os.statvfs(r);rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024
 row={'label':label,'elapsed':time.monotonic()-start,'sharedDelta':c-base,'headroom':m-c,'free':v.f_bavail*v.f_frsize,'ownMaxRSS':rss};rows.append(row)
 assert row['sharedDelta']<=64*1048576 and row['headroom']>=512*1048576 and row['free']>=64*1048576 and rss<24*1048576 and row['elapsed']<60 and events==(cg/'memory.events').read_text()
 return row
def meta(s):return {k:getattr(s,k) for k in ['st_dev','st_ino','st_mode','st_nlink','st_uid','st_gid','st_size','st_blocks','st_atime_ns','st_mtime_ns','st_ctime_ns']}
initial=guard('initial');cs={n:os.stat(canonical+'/'+n,follow_symlinks=False) for n in NAMES};assert all(stat.S_ISREG(s.st_mode) and s.st_dev==27 for s in cs.values())
stack=['/workspace/scratch'];groups={};aliases=[];excluded=[];errors=[];directories=0;entries=0
while stack:
 p=stack.pop();directories+=1;assert directories<=20000
 try:
  fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_NOATIME)
  try:
   before=os.fstat(fd)
   with os.scandir(fd) as scan:
    for e in scan:
     entries+=1;assert entries<=250000
     ep=p+'/'+e.name
     if e.is_symlink():continue
     if e.is_dir(follow_symlinks=False):
      if e.name in ['retained-original-archives','protected','.git','node_modules'] or e.name.startswith('protected-'):
       if len(excluded)<100:excluded.append(ep)
      else:stack.append(ep)
     elif e.name in NAMES and e.is_file(follow_symlinks=False):
      s=e.stat(follow_symlinks=False)
      aliases.append({'path':ep,'metadata':meta(s)})
      if s.st_dev==27 and s.st_size==cs[e.name].st_size:groups.setdefault(p,{})[e.name]=meta(s)
   after=os.fstat(fd)
   assert before.st_atime_ns==after.st_atime_ns,'directory access-time change'
  finally:os.close(fd)
 except OSError as ex:
  errors.append({'path':p,'error':repr(ex)})
 if directories%128==0:guard('metadata128dirs')
guard('walk-closed')
eligible=[]
for p,g in groups.items():
 if all(n in g and g[n]['st_nlink']==1 and g[n]['st_ino']!=cs[n].st_ino for n in NAMES):eligible.append(p)
eligible.sort()
summary={'directories':directories,'entries':entries,'excluded':excluded,'errors':errors,'noSymlinkDirectoryFollow':True,'metadataOnlyWalk':True,'completeWithinDeclaredScope':not errors,'matchingSizeGroupCount':sum(all(n in g for n in NAMES) for g in groups.values()),'independentNlink1GroupCount':len(eligible)}
def pin(p):
 fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME)
 try:
  s=os.fstat(fd);x={n:os.getxattr(fd,n).hex() for n in os.listxattr(fd)};h=hashlib.sha256()
  while True:
   b=os.read(fd,65536)
   if not b:break
   h.update(b)
  assert meta(s)==meta(os.fstat(fd)) and x=={n:os.getxattr(fd,n).hex() for n in os.listxattr(fd)}
  guard('body-closed')
  return {'path':p,'sha256':h.hexdigest(),'metadata':meta(s),'xattrs':x,'O_NOATIME':True,'duringReadMetadataExact':True}
 finally:os.close(fd)
selected=eligible[0] if eligible else None;pairs=[];verification='NO_ELIGIBLE_GROUP'
if selected:
 for n in NAMES:
  old=pin(selected+'/'+n);retained=pin(canonical+'/'+n)
  pairs.append({'candidate':old,'canonical':retained,'exactBodyEqual':old['sha256']==retained['sha256']})
 verification='EXACT_MATCH' if all(x['exactBodyEqual'] for x in pairs) else 'REJECT_BODY_MISMATCH_NO_SECOND_CANDIDATE'
knownAliases=[]
for a in aliases:
 if any(a['metadata']['st_dev']==x['candidate']['metadata']['st_dev'] and a['metadata']['st_ino']==x['candidate']['metadata']['st_ino'] for x in pairs):knownAliases.append(a)
allocated=sum(x['candidate']['metadata']['st_blocks']*512 for x in pairs);logical=sum(x['candidate']['metadata']['st_size'] for x in pairs)
evidence={'walk':summary,'selectedGroup':selected,'verification':verification,'pairs':pairs,'knownScratchPhysicalAliases':knownAliases,'allocatedCandidateBytes':allocated,'logicalCandidateBytes':logical,'conservativeNetAfter128KiBPacket':allocated-128*1024 if pairs else 0,'canonicalAliasQualification':'Canonical nlinks recorded but existing aliases outside this exact metadata walk are not exhaustively inventoried; all remain under existing canonical media holds.','decision':'Conditional source proposal only; no action/independent approval/producer judgment/push verification.','futureHoldRequired':'Exact selected directory and all three existing PNG leaves require explicit immutable/fresh-stage-only designation before any storage action. Existing unrelated dist/public holds cannot be inherited. Also freeze any known reproduction/build/consumer and require future revisions with new names/inodes or fresh stages.','metadataLoss':'Sharing would remove each independent recipient inode after separately reviewed backup retirement, inherit canonical metadata and introduce shared mutable state. Canonical nlink/ctime and directory metadata would change. Original stat/xattr records remain in this packet; original inode/ctime history cannot be recreated after retirement.','oldRepresentationNeed':'Not established by byte equality. Independent review must decide whether preserving exact bytes/paths/source/rights/rollback but losing old physical isolation is preferable; producer must explicitly judge it before any transaction.','rollback':'Keep all old inodes/path bodies until a separately authorized journalled transaction and independent postcheck. This script makes no link/unlink/write/chmod/xattr/timestamp-setting mutation.','protectedArchive':'Excluded; no archive body scanned. Only three named loose PNGs are considered; no JS/JSON/audio investigation.','readOnlyScope':'O_NOATIME directory/body reads; symlink directories skipped; preliminary source-file creation is privately owned output only.','allInputFDsClosed':True}
with (r/'EVIDENCE.json').open('x') as f:json.dump(evidence,f,indent=2);f.write('\n')
final=guard('final')
with (r/'RESOURCE.json').open('x') as f:json.dump({'initial':initial,'rows':rows,'final':final,'eventsBefore':events,'eventsAfter':(cg/'memory.events').read_text(),'scope':'Own maxRSS and observed shared64MiB delta plus512MiB reserve; coordinated tiny readers may coexist, not exclusive attribution.'},f,indent=2);f.write('\n')
print(json.dumps({'selected':selected,'verification':verification,'walk':summary,'allocated':allocated,'conservativeNet':evidence['conservativeNetAfter128KiBPacket'],'final':final}))
