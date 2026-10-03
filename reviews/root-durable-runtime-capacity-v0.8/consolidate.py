"""Preserve every durable comparison path while sharing exact immutable stock bytes."""
from pathlib import Path
from collections import Counter
import hashlib,json,os,stat,uuid

ROOT=Path('/workspace/Roguelike-deckbuilder/reviews/root-durable-runtime-capacity-v0.8')
AUDIT=Path('/workspace/scratch/durable-runtime-capacity-independent-v08-r1/AUDIT.json')
EXPECTED='baa73b3df3105de3a10b4da3a894f4ee59349eb59d3966c9af98ac3545adbc06'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(1024*1024): h.update(b)
 return h.hexdigest()
def metadata(p):
 s=p.lstat()
 return {'type':'file' if stat.S_ISREG(s.st_mode) else 'directory' if stat.S_ISDIR(s.st_mode) else 'other',
  'size':s.st_size,'mode':oct(s.st_mode&0o7777),'device':s.st_dev,'inode':s.st_ino,'nlink':s.st_nlink,
  'mtime_ns':s.st_mtime_ns,'atime_ns':s.st_atime_ns,'ctime_ns':s.st_ctime_ns,'blocks':s.st_blocks,'uid':s.st_uid,'gid':s.st_gid,'xattrs':{key:os.getxattr(p,key,follow_symlinks=False).hex() for key in os.listxattr(p,follow_symlinks=False)}}
assert sha(AUDIT)==EXPECTED
audit=json.loads(AUDIT.read_text()); assert audit['regular_files_hashed']==432 and len(audit['roots'])==6
assert not audit['outside_inventory_aliases'] and not audit['mutations_performed']
roots=[Path(r) for r in audit['roots']]
assert len(set(roots))==6 and all(r.is_dir() and r.resolve().is_relative_to('/workspace/scratch') for r in roots)
rows={}; directories={}; memberships={}; before={}
stable=['type','size','mode','device','inode','nlink','mtime_ns','ctime_ns','uid','gid','xattrs']
for inventory in audit['complete_inventories']:
 r=Path(inventory['root']); expected=set()
 for row in inventory['rows']:
  p=Path(row['path']); assert p.is_relative_to(r) and p.resolve().is_relative_to('/workspace/scratch')
  m=metadata(p); assert all(m[k]==row['after_hash'][k] for k in stable),(str(p),'stale metadata')
  before[str(p)]=m; expected.add(str(p)); rows[str(p)]=row
  if m['type']=='file': assert sha(p)==row['sha256'],str(p)
  else: assert m['type']=='directory'; directories[str(p)]=m
 actual={str(r)}|{str(p) for p in r.rglob('*')}; assert actual==expected,str(r)
 memberships[str(r)]=sorted(actual)
assert len(rows)==450 and len(directories)==18
inodeAliases=Counter((m['device'],m['inode']) for m in before.values() if m['type']=='file')
for m in before.values():
 if m['type']=='file': assert inodeAliases[(m['device'],m['inode'])]==m['nlink']
groups=audit['runtime_candidate_duplicate_groups']; assert len(groups)==141
seen=set()
for group in groups:
 ownerRoots=[]
 for name in group['paths']:
  assert name not in seen; seen.add(name); row=rows[name]; assert row['eligible_runtime_only']
  assert row['sha256']==group['sha256'] and row['after_hash']['size']==group['bytes'] and row['after_hash']['mode']==group['mode']
  assert all(row['after_hash'][k]==group[k] for k in ['uid','gid','xattrs'])
  p=Path(name); owners=[r for r in roots if p.is_relative_to(r)]; assert len(owners)==1
  ownerRoots.append(str(owners[0])); relative=p.relative_to(owners[0])
  assert 'resources' not in relative.parts and 'app.asar' not in name and 'default_app.asar' not in name
 assert len(set(ownerRoots))==len(ownerRoots),'Do not introduce within-package archive hardlink members'
 assert group['canonical_path_forecast_only']==group['paths'][0]

free_before=os.statvfs('/workspace').f_bavail*os.statvfs('/workspace').f_frsize
snapshot={'auditSHA256':EXPECTED,'scope':'Fresh full432-byte/mode/ownership/xattrs and18-directory membership gate after explicit native reader release. Recorded timestamps follow independent/root reads; all resources/ASAR/game/media/profiles/archives/data excluded from sharing.',
 'before':before,'memberships':memberships,'freeBefore':free_before,'readerRelease':'23477 native technical, visual and gameplay reviewers explicitly closed native hosts/readers. These historical comparison roots have no active native host/build writer; current scene tests and UI playtest use separate web assets.'}
with (ROOT/'BEFORE.json').open('x') as f: json.dump(snapshot,f,indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
transaction=uuid.uuid4().hex; operations=[]
with (ROOT/'JOURNAL.jsonl').open('x') as journal:
 try:
  for group in groups:
   canonical=Path(group['paths'][0]); cm=metadata(canonical); assert sha(canonical)==group['sha256']
   for name in group['paths'][1:]:
    p=Path(name); m=metadata(p)
    if (m['device'],m['inode'])==(cm['device'],cm['inode']): continue
    assert m['inode']==before[name]['inode'] and m['mode']==group['mode'] and m['size']==group['bytes']
    assert sha(p)==group['sha256']; temporary=p.with_name(p.name+'.hollowpact-share-'+transaction)
    assert not temporary.exists(); os.link(canonical,temporary)
    try: os.replace(temporary,p)
    finally:
     if temporary.exists(): temporary.unlink()
    receipt={'path':name,'canonical':str(canonical),'originalInode':m['inode'],'sharedInode':cm['inode'],'sha256':group['sha256']}
    operations.append(receipt); journal.write(json.dumps(receipt)+'\n'); journal.flush(); os.fsync(journal.fileno())
 finally:
  for name,m in sorted(directories.items(),key=lambda pair:len(Path(pair[0]).parts),reverse=True):
   os.utime(name,ns=(m['atime_ns'],m['mtime_ns']),follow_symlinks=False)

after={}
for name,row in rows.items():
 p=Path(name); m=metadata(p); after[name]=m
 assert all(m[k]==before[name][k] for k in ['type','mode','uid','gid','xattrs'])
 if m['type']=='file': assert m['size']==before[name]['size'] and sha(p)==row['sha256'],name
for r in roots: assert {str(r)}|{str(p) for p in r.rglob('*')}==set(memberships[str(r)])
for group in groups: assert len({(metadata(Path(n))['device'],metadata(Path(n))['inode']) for n in group['paths']})==1
free_after=os.statvfs('/workspace').f_bavail*os.statvfs('/workspace').f_frsize
result={'auditSHA256':EXPECTED,'all432FilesExactSizeModeSHA':True,'all18DirectoryModesAndMembershipsExact':True,'operations':len(operations),'groups':len(groups),'freeBefore':free_before,'freeAfter':free_after,'observedFreeDelta':free_after-free_before,'after':after,
 'qualification':'Free delta includes unrelated concurrent workspace use. All paths/bytes/modes/ownership/xattrs preserved, unique resources/ASAR untouched. Stock aliases immutable by usage contract, not chmod enforcement; inode/nlink/ctime and merged per-file timestamps change. Original per-path metadata retained. These durable historical package paths remain, but shared stock bytes are one storage copy; every original official archive remains untouched. Fresh builds must use independent files.'}
with (ROOT/'AFTER.json').open('x') as f: json.dump(result,f,indent=2); f.write('\n')
print(json.dumps({k:v for k,v in result.items() if k!='after'}))
