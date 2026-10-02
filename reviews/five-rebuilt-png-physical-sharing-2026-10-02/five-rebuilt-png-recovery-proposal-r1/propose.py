import os,json,hashlib,stat,resource
resource.setrlimit(resource.RLIMIT_DATA,(24*1048576,24*1048576))
ROOT='/workspace/scratch/five-rebuilt-png-recovery-proposal-r1'
CAND='/workspace/scratch/audio-host-independent-v08/independent/rebuilt-dist/art'
ANCH='/workspace/Roguelike-deckbuilder/public/art'
NAMES=['adversaries-atlas.png','companions-atlas.png','hound-poses.png','pact-seal.png','warleader-poses.png']
EXPECTED_INOS=[544873,544874,544875,544877,544879]
parents={}
def sd(s):return {'st_'+k:getattr(s,'st_'+k) for k in ['dev','ino','mode','uid','gid','nlink','size','blocks','atime_ns','mtime_ns','ctime_ns']}
def op(path, flags=os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW):
 fd=os.open('/',os.O_PATH|os.O_DIRECTORY|os.O_NOFOLLOW);cur=''
 try:
  parts=path.split('/')[1:]
  for part in parts[:-1]:
   n=os.open(part,os.O_PATH|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd);os.close(fd);fd=n;cur+='/'+part
   if cur not in parents:parents[cur]={'lstat':sd(os.fstat(fd)),'xattrs':{n:os.getxattr('/proc/self/fd/'+str(fd),n).hex() for n in os.listxattr('/proc/self/fd/'+str(fd))}}
  return os.open(parts[-1],flags,dir_fd=fd)
 finally:os.close(fd)
def pin(path,ret=False):
 before=sd(os.lstat(path));f=op(path);fs=sd(os.fstat(f));assert before==fs and stat.S_ISREG(fs['st_mode']);attrs={n:os.getxattr(f,n).hex() for n in os.listxattr(f)}
 h=hashlib.sha256();parts=[]
 while True:
  b=os.read(f,65536)
  if not b:break
  h.update(b)
  if ret:parts.append(b)
 after=sd(os.fstat(f));os.close(f);assert before==after==sd(os.lstat(path))
 j={'path':path,'lstat':before,'fstat':fs,'after':after,'xattrs':attrs,'sha256':h.hexdigest(),'O_NOATIME':True,'duringReadMetadataExact':True}
 return (j,b''.join(parts)) if ret else j
def load(path):
 p,b=pin(path,True);assert len(b)<262144;return p,json.loads(b)
controls=[]
sp,source=load('/workspace/scratch/audio-host-independent-v08/candidate/SOURCE-MANIFEST.json');controls.append(sp)
bp,built=load('/workspace/scratch/audio-host-independent-v08/candidate/BUILD-MANIFEST.json');controls.append(bp)
rp,rebuild=load('/workspace/scratch/audio-host-independent-v08/independent/independent-rebuild.json');controls.append(rp)
review,reviewbody=pin('/workspace/scratch/audio-host-independent-v08/independent/REVIEW.md',True);controls.append(review)
assert b'not approved for production promotion' in reviewbody and b'NEW output directory' in reviewbody
ap,agents=pin('/workspace/Roguelike-deckbuilder/AGENTS.md',True);controls.append(ap)
assert all(n.encode() in agents for n in NAMES) and b'/workspace/scratch/audio-host-independent-v08/independent/rebuilt-dist/art/adversaries-atlas.png' in agents and b'fresh-stage-only' in agents
fp,frozen=load('/workspace/scratch/frozen128-canonical-media-sharing-proposal-root-r1/PROPOSAL.json');controls.append(fp)
oldp,oldproposal=load('/workspace/scratch/five-retained-png-recovery-proposal-r1/PROPOSAL.json');controls.append(oldp)
assert oldp['sha256']=='b4e8803f2411e932c994b01aa50152fee4b4bd9d2c8757258ae7c686b75745bc'
assert source['sourceDigest']==built['sourceDigest']=='eb1e4fcadd0b166092484bf9e7ebddfc4e51f3811e3154a24c8b42663273b1fd'
pairs=[]
for name,ino in zip(NAMES,EXPECTED_INOS):
 c=pin(CAND+'/'+name);a=pin(ANCH+'/'+name)
 assert c['lstat']['st_dev']==a['lstat']['st_dev']==27 and c['lstat']['st_ino']==ino and c['lstat']['st_nlink']==1
 assert c['lstat']['st_ino']!=a['lstat']['st_ino'] and c['sha256']==a['sha256'] and c['lstat']['st_size']==a['lstat']['st_size']
 assert source['files']['public/art/'+name]==built['files']['dist/art/'+name]==c['sha256']
 assert any(x['path']=='dist/art/'+name and x['sha256']==c['sha256'] for x in rebuild['files'])
 assert a['lstat']['st_nlink']==[5,5,5,4,5][NAMES.index(name)]
 pairs.append({'anchor':a,'candidate':c,'historicalSourceBuildRebuildEntriesMatch':True})
def strings(j):
 if isinstance(j,str):yield j
 elif isinstance(j,list):
  for x in j:yield from strings(x)
 elif isinstance(j,dict):
  for k,v in j.items():yield from strings(k);yield from strings(v)
alias=[]
for pair in pairs:
 name=pair['anchor']['path'].split('/')[-1];a=pair['anchor']['lstat'];known={ANCH+'/'+name,'/workspace/Roguelike-deckbuilder/dist/art/'+name,'/workspace/scratch/first-five-opening-cairn128-ready-stage-r1/public/art/'+name,'/workspace/scratch/first-five-opening-cairn128-ready-stage-r1/dist/art/'+name,'/workspace/scratch/audio-host-independent-v08/independent/rebuilt-dist/art/'+name,'/workspace/scratch/audio-host-independent-v08/candidate/dist/art/'+name}
 known.update(s for s in strings(frozen) if s.startswith('/workspace/') and s.endswith('/'+name) and 'retained-original-archives' not in s)
 assert len(known)<=40
 rows=[]
 for p in sorted(known):
  try:
   f=op(p,os.O_PATH|os.O_NOFOLLOW);s=sd(os.fstat(f));attrs={n:os.getxattr('/proc/self/fd/'+str(f),n).hex() for n in os.listxattr('/proc/self/fd/'+str(f))};os.close(f)
   rows.append({'path':p,'lstat':s,'xattrs':attrs,'sameAnchorInode':s['st_dev']==a['st_dev'] and s['st_ino']==a['st_ino']})
  except OSError as e:rows.append({'path':p,'unresolvedNoSymlinkTraversal':str(e)})
 count=sum(x.get('sameAnchorInode',False) for x in rows);assert count<=a['st_nlink']
 alias.append({'anchor':pair['anchor']['path'],'knownEntries':rows,'knownPhysicalCount':count,'anchorNlink':a['st_nlink'],'unresolvedPhysicalAliasCount':a['st_nlink']-count,'qualification':'Exact named known paths from old sharing controls and explicit frozen/current locations only; unknown physical/logical aliases, processes, mmap and future consumers not universally inventoried. Shared ctime/nlink effects apply to unknown existing hardlinks.'})
gross=sum(p['candidate']['lstat']['st_blocks']*512 for p in pairs)
proposal={'decision':'CONDITIONAL_EXACT_FIVE_PNG_SHARED_ENCODING_PROPOSAL_ONLY_NO_ACTION','candidateGroup':CAND,'pairs':pairs,'knownAnchorAliases':alias,'parentMetadata':parents,'grossOldAllocationBytes':gross,'logicalOldBytes':sum(p['candidate']['lstat']['st_size'] for p in pairs),'sourceControls':controls,'historicalMaps':{'sourceDigest':source['sourceDigest'],'sourceFiles':len(source['files']),'buildFiles':len(built['files']),'independentRebuildMatchDeclared':rebuild['independentViteOutputMatchesEveryAuthorBuildFile'],'fiveEntriesIndependentlyMatchedToBothMapsAndRebuild':True,'notWholeTreeRehashed':True},'historicalConsumer':'Retained old exterior audio host built/development diagnostics and independent reproduction66/51 remain. Engineering review rejected production promotion because automatic resize removed binding visuals while contact sounds continued. These are historical independently reproduced output pixels, not current selected output source. Useful exact historical HTTP/art bodies and rollback remain at ALL five logical paths after proposed sharing. All source, reviews, manifests, rights and failure methods remain untouched.','oldPhysicalEncodingNeed':'Conditional author preference: five source/build/rebuild-proven exact PNG bytes add no distinct historical art/source data through separate private inodes. Under published exact immutable/fresh-stage holds, retained shared bytes at every old name serve historical reads/reproduction; future reproduction uses NEW stages/inodes. Independent reviewer must specifically prefer the replacement and old private writable/time isolation no longer needed; Root must judge knowingly before any action.','futureHold':{'AGENTSPinnedExact':ap['sha256'],'fiveNamedFreshStageHoldObserved':True,'currentlyRootReportsUnpushed':True,'mustConfirmCurrentPushBeforeAction':True,'notOSEnforced':True},'metadataIsolationLosses':['Five candidate original inode identities cease; their atime/mtime/mode/uid/gid/xattrs become anchor properties. Record original ledger; do not equalize metadata silently.','Each canonical anchor nlink increases by1 and ctime changes, visible through ALL existing hardlinks including unresolved ones. Byte-equivalence is not universal unchanged metadata proof.','Candidate parent directory entry/times change; old private write isolation is surrendered. Writes through any linked alias could affect all consumers; fresh-stage-only holds are required and no OS readonly claim follows.','Exact old kernel inode/ctime history cannot be recreated after retirement of old redundant allocation; byte/path rollback remains possible with NEW separate copies if future approved.'],'prospectiveTransaction':'Root-owned exact-five-only method, fresh full O_NOATIME body/meta preflight, current proposal/gate/judgment/push pins, durable before/journal/fsync, unique temporary hardlinks and atomic replacement. No helper action executed here; producer must explicitly accept isolation/metadata losses and bounded unknown-alias gap.','preservation':'Every logical path/body retained; no delete of source/art/reviews/archives or unique input. Protected ZIP/retained-original archives not opened. Only five matching loose recipient PNG bodies and anchors were hashed; aliases metadata-only.','capacity':{'grossAllocatedBytes':gross,'netQualified':'Gross only; future packets/journal/publication/temp filesystem allocations reduce final recovery. No exact net promise.'},'bootstrapQualification':'Tiny source preparation reused the pinned first-five author method with fresh owned paths and explicit new recipient inodes/hold/known aliases. No prior metadata reused for proof. All relied bodies/controls reread under normal64MiB work+512reserve/disk64 guard. No old source modified.','resources':{'ownMaxRSSBytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,'rlimitDataBytes':24*1048576,'streamChunkBytes':65536},'allInputFDsClosed':True}
assert proposal['resources']['ownMaxRSSBytes']<24*1048576
with open(ROOT+'/PROPOSAL.json','x') as o:json.dump(proposal,o,indent=2);o.write('\n')
print(json.dumps({'grossOldAllocationBytes':gross,'logicalOldBytes':proposal['logicalOldBytes'],'pairHashes':[p['candidate']['sha256'] for p in pairs],'anchorNlinks':[p['anchor']['lstat']['st_nlink'] for p in pairs],'aliasGaps':[x['unresolvedPhysicalAliasCount'] for x in alias],'ownMaxRSSBytes':proposal['resources']['ownMaxRSSBytes']}))
