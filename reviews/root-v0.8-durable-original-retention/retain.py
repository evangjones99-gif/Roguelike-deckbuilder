"""Preserve one duplicate archive path through its untouched official bytes."""
from pathlib import Path
import json,hashlib,os,stat,time
ROOT=Path(__file__).parent
ELIGIBILITY=Path('/workspace/scratch/durable-official-archive-duplicate-independent-v08-r1/ELIGIBILITY.json')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(1048576):h.update(b)
 return h.hexdigest()
def meta(p):
 s=p.lstat()
 return {'type':'file' if stat.S_ISREG(s.st_mode) else 'directory' if stat.S_ISDIR(s.st_mode) else 'link','bytes':s.st_size,'mode':oct(stat.S_IMODE(s.st_mode)),'uid':s.st_uid,'gid':s.st_gid,'device':s.st_dev,'inode':s.st_ino,'nlink':s.st_nlink,'atime_ns':s.st_atime_ns,'mtime_ns':s.st_mtime_ns,'ctime_ns':s.st_ctime_ns,'blocks':s.st_blocks,'xattrs':{k:os.getxattr(p,k,follow_symlinks=False).hex() for k in os.listxattr(p,follow_symlinks=False)}}
audit=json.loads(ELIGIBILITY.read_text());before={}
for key in ('duplicateOriginal','officialRetained','duplicateParent','officialParent'):
 row=audit["before"][key];p=Path(row['path']);actual=meta(p)
 for field,value in row['metadata'].items():
  if field!='atime_ns':assert actual[field]==value,(key,field,actual[field],value)
 if 'sha256' in row:assert sha(p)==row['sha256']
 if 'members' in row:assert sorted(str(q) for q in p.iterdir())==row['members']
 before[key]={'path':str(p),'metadata':meta(p),'sha256':row.get('sha256'),'members':row.get('members')}
def stable(row):
 p=Path(row['path']);actual=meta(p)
 for field,value in row['metadata'].items():
  if field=='atime_ns':continue
  if field=='linkTarget':assert os.readlink(p)==value,(str(p),field)
  else:assert actual[field]==value,(str(p),field,actual.get(field),value)
for row in audit['sidecars']+audit['wrappers']:
 stable(row);assert sha(Path(row['path']))==row['sha256'],row['path']
for row in audit['excludedInputs']:stable(row)
src=Path(before['duplicateOriginal']['path']);target=Path(before['officialRetained']['path']);parent=src.parent
assert not src.is_symlink() and not target.is_symlink() and src.stat().st_nlink==target.stat().st_nlink==1
free=lambda:os.statvfs('/workspace').f_bavail*os.statvfs('/workspace').f_frsize
record={'eligibilitySHA256':sha(ELIGIBILITY),'before':before,'freeBeforeBytes':free(),'coordination':'Root and all current agents explicitly freeze these historical paths. FD inspection is incomplete and is not treated as a lock. Current browsers use other23477 files.','qualification':'Original path/bytes/access metadata retained via unchanged official archive; original inode/type/timestamps change and are retained here. Duplicate-parentctime changes; sourcearchive immutable by usage contract.'}
with (ROOT/'BEFORE.json').open('x') as f:json.dump(record,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
fd=os.open(ROOT,os.O_DIRECTORY);os.fsync(fd);os.close(fd)
temp=parent/'.hollowpact-retained-0.8.0-original-alias'
assert not temp.exists() and not temp.is_symlink();os.symlink(str(target),temp)
with (ROOT/'JOURNAL.jsonl').open('x') as f:
 f.write(json.dumps({'phase':'ready','original':str(src),'temporaryAlias':str(temp),'target':str(target)})+'\n');f.flush();os.fsync(f.fileno())
 os.replace(temp,src)
 f.write(json.dumps({'phase':'replaced','linkTarget':os.readlink(src)})+'\n');f.flush();os.fsync(f.fileno())
fd=os.open(parent,os.O_DIRECTORY);os.fsync(fd);os.close(fd)
os.utime(parent,ns=(before['duplicateParent']['metadata']['atime_ns'],before['duplicateParent']['metadata']['mtime_ns']))
assert src.is_symlink() and os.readlink(src)==str(target) and src.resolve()==target
assert sha(src)==sha(target)==before['officialRetained']['sha256']
for field,value in before['officialRetained']['metadata'].items():
 if field!='atime_ns':assert meta(target)[field]==value,field
assert sorted(str(q) for q in parent.iterdir())==before['duplicateParent']['members']
for field in ('mode','uid','gid','inode','mtime_ns','xattrs'):assert meta(parent)[field]==before['duplicateParent']['metadata'][field],field
for row in audit['sidecars']+audit['wrappers']:
 stable(row);assert sha(Path(row['path']))==row['sha256'],row['path']
for row in audit['excludedInputs']:stable(row)
for field,value in before['officialParent']['metadata'].items():
 if field!='atime_ns':assert meta(target.parent)[field]==value,('officialParent',field)
assert sorted(str(q) for q in target.parent.iterdir())==before['officialParent']['members']
after={'status':'PASS-root-retention','originalPath':str(src),'target':str(target),'sourceSHA256':sha(target),'followedMode':oct(stat.S_IMODE(src.stat().st_mode)),'originalParent':meta(parent),'officialRetained':meta(target),'freeAfterBytes':free(),'observedFreeDelta':free()-record['freeBeforeBytes'],'independentPostgate':'pending'}
with (ROOT/'AFTER.json').open('x') as f:json.dump(after,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
print(json.dumps(after))
