import os,json,hashlib,ast,resource
from pathlib import Path
P=Path(__file__).parent;A=Path('/workspace/scratch/git-immutable-pack-cache-hint-opening-root-r1');B=Path('/workspace/scratch/git-immutable-pack-cache-hint-ROOT-author-r3')
def read(p):
 fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME)
 try:
  assert os.fstat(fd).st_size<65536
  return b''.join(iter(lambda:os.read(fd,65536),b''))
 finally:os.close(fd)
def pin(p):
 b=read(p);return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
intake=json.loads(read(P/'SOURCE-INTAKE.json'));source=read(A/'immutable_pack_hint.py');old=read(B/'immutable_pack_hint.py')
changes=[(b"BASE='/workspace/scratch/git-immutable-pack-cache-hint-author-r1'",b"BASE='/workspace/scratch/git-immutable-pack-cache-hint-opening-root-r1'"),(b"OUTPUT='/workspace/scratch/git-immutable-pack-cache-hint-run-r3'",b"OUTPUT='/workspace/scratch/git-immutable-pack-cache-hint-opening-run-root-r1'")]
expected=old
for before,after in changes:assert expected.count(before)==1;expected=expected.replace(before,after)
assert expected==source
inverse=source
for before,after in changes:assert inverse.count(after)==1;inverse=inverse.replace(after,before)
assert inverse==old
tree=ast.parse(source);calls=[ast.unparse(x.func)for x in ast.walk(tree)if isinstance(x,ast.Call)];assert calls.count('os.posix_fadvise')==1
hint=next(x for x in ast.walk(tree)if isinstance(x,ast.Call)and ast.unparse(x.func)=='os.posix_fadvise');assert ast.unparse(hint)=='os.posix_fadvise(fd, 0, 0, os.POSIX_FADV_DONTNEED)'
for forbidden in ['os.unlink','os.remove','os.chmod','os.utime','os.setxattr','os.system','subprocess.run','os.ftruncate']:
 assert forbidden not in calls
history=[]
for root,names in [('/workspace/scratch/git-immutable-pack-cache-hint-source-independent-r3',['INDEPENDENT-ACCEPTANCE.json','REVIEW.md']),('/workspace/scratch/git-immutable-pack-cache-hint-source-independent-r4',['INDEPENDENT-ACCEPTANCE.json','REVIEW.md']),('/workspace/scratch/standard-sol-pc-immutable-pack-cache-advice-execution-independent-r3',['OUTCOME.json','INPUTS.json','FROZEN.json','REVIEW.md'])]:
 for name in names:
  p=Path(root)/name;b=read(p);entry=pin(p)
  if name.endswith('.json'):entry['historicalControl']=json.loads(b)
  else:entry['historicalReviewText']=b.decode()
  history.append(entry)
pinmeta=intake['controls']['METADATA-INTAKE.json'];path=Path(pinmeta['path']);current=os.lstat(path)
fields=['st_dev','st_ino','st_mode','st_uid','st_gid','st_size','st_blocks','st_nlink','st_atime_ns','st_mtime_ns','st_ctime_ns'];live={k:getattr(current,k)for k in fields};attrs={n:os.getxattr(path,n,follow_symlinks=False).hex()for n in sorted(os.listxattr(path,follow_symlinks=False))};assert live==pinmeta['metadata']and attrs==pinmeta['xattrs']
chain=[]
for part in list(path.parents)[:-1][::-1]:
 st=os.lstat(part);chain.append(dict(name=part.name,device=st.st_dev,inode=st.st_ino,mode=st.st_mode,uid=st.st_uid,gid=st.st_gid))
assert chain==pinmeta['parentChain']
scope=next(x.value.value for x in tree.body if isinstance(x,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='SCOPE'for t in x.targets));assert scope=='One immutable old Git pack FD cache hint; metadata-only preservation; no whole-pack SHA proof'
out=dict(exactSourceInverse=True,onlySourceChanges=2,newSource=intake['source'],oldSource=intake['oldSource'],pin=pin(A/'METADATA-INTAKE.json'),proposal=pin(A/'PROPOSAL.json'),scope=scope,history=history,historicalGrantsCurrentAuthorization=False,currentTargetMetadata=live,currentTargetXattrs=attrs,currentParentIdentityChain=chain,currentStatOnly=True,targetBodyOpenedOrRead=False,singleHintCall=ast.unparse(hint),apiCallCounts={k:calls.count(k)for k in ['os.posix_fadvise','os.read','os.write','os.pwrite','os.fsync','os.open','os.close']},conditions=['Root confirms fresh current push and independently verified acceptance before one actual attempt.','All known repository writers/maintenance/affected lock owners held; unknown writer/lock absence is declared within known scope, not OS/global proof.','Fresh immutable <=120second Root declaration, one exact-target hint, no retry and no automatic browser/build.','Future outer ordinary64MiB work+512reserve/disk64 finite20seconds; internal24+64 light-only profile is not permission to lower runtime/build thresholds.','Fresh native/runtime admission and separate disk recovery remain required; no causal reclaim guarantee.'],limitations=['Readonly mode0400/nlink1 and visible/proc/locks observation do not provide atomic writer exclusion.','Exact metadata/xattrs are rechecked; whole pack body hash is not established historically or freshly.','Receipt leaf files and output directory are fsynced; newly created output directory parent is not explicitly fsynced, so crash durability of the new path itself is not fully proven.','Armed without RETURNED receipt leaves hint outcome unknown; stop/no retry.','RLIMIT_AS bounds additional virtual memory; wrapper owns time/process-group stopping, not global backend accounting.'],ownRSSBytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024)
assert out['ownRSSBytes']<24*1048576
body=(json.dumps(out,indent=2,sort_keys=True)+'\n').encode();assert len(body)<24000
with(P/'PROOF.json').open('xb')as f:f.write(body);f.flush();os.fsync(f.fileno())
print(json.dumps(dict(exactTwoPathInverse=True,oneHintCall=True,metadataOnlyLiveMatch=True,proofBytes=len(body),ownRSSBytes=out['ownRSSBytes'])))
for x in history:
 if 'historicalReviewText'in x:print('HISTORICAL_REVIEW',x['path'],x['historicalReviewText'][:1800].replace('\n',' '))
 else:print('HISTORICAL_CONTROL',x['path'],json.dumps(x['historicalControl'])[:2200])
