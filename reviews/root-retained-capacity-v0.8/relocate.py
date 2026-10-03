"""Root-owned relocation of proven redundant historical QA copies only."""
from pathlib import Path
import json,hashlib,shutil,os,stat
proof=Path('/workspace/scratch/retained-capacity-independent-v08-r1')
out=Path('/workspace/Roguelike-deckbuilder/reviews/root-retained-capacity-v0.8');targetroot=Path('/tmp/hollowpact-retained-working-v08');assert not targetroot.exists()
cases=[json.loads((proof/('case-%02d.json'%i)).read_text()) for i in range(1,8)]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(1024*1024):h.update(b)
 return h.hexdigest()
def check(root,inv):
 assert root.is_dir()
 actual={'.'}|{str(p.relative_to(root)) for p in root.rglob('*')};assert actual==set(inv)
 for rel,v in inv.items():
  p=root/rel;s=p.stat();assert stat.S_IMODE(s.st_mode)==int(v['mode'],8),(p,'mode')
  if v['type']=='file':assert p.is_file() and not p.is_symlink() and s.st_size==v['size'] and sha(p)==v['sha256'],p
  else:assert p.is_dir() and not p.is_symlink(),p
archives={c['official_archive']:c['archive_sha256_before'] for c in cases}
for name,expected in archives.items():assert sha(Path(name))==expected
originalmeta=[];unique={}
for c in cases:
 source=Path(c['working_directory']);assert not source.is_symlink();check(source,c['working_inventory'])
 for rel,v in c['working_inventory'].items():
  if v['type']=='file':
   p=source/rel;s=p.stat();originalmeta.append({'path':str(p),'mtime_ns':s.st_mtime_ns,'atime_ns':s.st_atime_ns,'inode':s.st_ino,'device':s.st_dev,'nlink':s.st_nlink})
   unique.setdefault((v['size'],v['sha256'],v['mode']),v['size'])
pre={'originalFiles':504,'logicalBytes':sum(c['working_file_bytes'] for c in cases),'temporaryUniqueContentModeBytes':sum(unique.values()),'durableFreeBytes':shutil.disk_usage(out).free,'temporaryFreeBytes':shutil.disk_usage('/tmp').free,'sharedCopiesAreImmutable':True,'metadataChanges':'Original paths become symlinks; device/inodes/nlinks/location and shared file mtimes can change. Full original timestamp/inode sidecar is retained. Bytes/file modes/directory modes must match; official release archives unchanged.'}
assert shutil.disk_usage('/tmp').free > pre['logicalBytes']+64*1024*1024
(out/'PRE-TRANSFER.json').write_text(json.dumps(pre,indent=2)+'\n');(out/'ORIGINAL-METADATA.json').write_text(json.dumps(originalmeta,indent=2)+'\n')
targetroot.mkdir();moves=[]
for i,c in enumerate(cases,1):
 source=Path(c['working_directory']);target=targetroot/('case-%02d'%i);assert not target.exists()
 shutil.move(str(source),str(target));source.symlink_to(target,target_is_directory=True);check(target,c['working_inventory'])
 assert source.resolve()==target;moves.append({'sourcePath':str(source),'temporaryTarget':str(target),'files':c['working_file_count'],'bytes':c['working_file_bytes']})
 print('Transferred and byte/mode verified',i,flush=True)
# All new targets are exclusively owned comparison copies. Share only independently
# verified identical regular bytes AND modes; never link to a release archive/source.
seen={};links=[]
for i,c in enumerate(cases,1):
 target=targetroot/('case-%02d'%i)
 for rel,v in c['working_inventory'].items():
  if v['type']!='file':continue
  p=target/rel;k=(v['size'],v['sha256'],v['mode'])
  if k not in seen:seen[k]=p;continue
  prior=seen[k];assert sha(prior)==v['sha256'] and sha(p)==v['sha256'];swap=p.with_name(p.name+'.root-share-tmp');assert not swap.exists();os.link(prior,swap);os.replace(swap,p);links.append({'path':str(p),'shares':str(prior),'bytes':v['size'],'sha256':v['sha256'],'mode':v['mode']})
for c in cases:check(Path(c['working_directory']).resolve(),c['working_inventory'])
for name,expected in archives.items():assert sha(Path(name))==expected
post={'scope':'Redundant immutable unpacked QA comparisons moved, not official versions/archives. Original paths resolve to exact byte/mode copies. TMP is not durable backup; exact official archives and original mode inventory remain durable. Do not edit linked comparison copies. No unique research/data/art/transfer input relocated.','moves':moves,'sharedTemporaryFiles':links,'all504SHABytesFileModesAndDirectoryModesPass':True,'allOriginalOfficialArchivesUnchanged':True,'durableFreeBytes':shutil.disk_usage(out).free,'temporaryFreeBytes':shutil.disk_usage('/tmp').free}
(out/'POST-TRANSFER.json').write_text(json.dumps(post,indent=2)+'\n');print(json.dumps({k:v for k,v in post.items() if k not in ('moves','sharedTemporaryFiles')},indent=2))
