from pathlib import Path
import os,json,hashlib,stat,resource
resource.setrlimit(resource.RLIMIT_DATA,(24*1048576,24*1048576))
P=Path('/workspace/scratch/five-rebuilt-png-sharing-independent-r1')
KEYS=['st_dev','st_ino','st_mode','st_nlink','st_uid','st_gid','st_size','st_blocks','st_atime_ns','st_mtime_ns','st_ctime_ns']
def md(s):return {k:getattr(s,k) for k in KEYS}
def op(p):
 p=Path(p);fd=os.open('/',os.O_PATH|os.O_DIRECTORY|os.O_NOFOLLOW)
 try:
  for part in p.parent.parts[1:]:
   n=os.open(part,os.O_PATH|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd);os.close(fd);fd=n
  return os.open(p.name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME,dir_fd=fd)
 finally:os.close(fd)
def pin(p):
 p=Path(p);before=md(os.lstat(p));fd=op(p);h=hashlib.sha256();size=0
 try:
  assert stat.S_ISREG(before['st_mode']) and md(os.fstat(fd))==before
  attrs={n:os.getxattr(fd,n).hex() for n in os.listxattr(fd)}
  for b in iter(lambda:os.read(fd,65536),b''):h.update(b);size+=len(b)
  assert md(os.fstat(fd))==before==md(os.lstat(p))
 finally:os.close(fd)
 return {'path':str(p),'sha256':h.hexdigest(),'bytes':size,'metadata':before,'xattrs':attrs}
old=json.loads((P/'PROOF.json').read_text());oldpin=pin(P/'PROOF.json')
zip_path=Path('/workspace/scratch/retained-original-archives/preflight-bdf273-original-r4.zip');zip_before=md(os.lstat(zip_path))
pins=[]
for q in [old['proposal'],old['authorSupplementSeal'],old['methodAuthorSeal'],old['selectedMap'],*old['methods'],*old['sourceControls'],*old['firstPOSTControls'],old['R3CompleteGate'],old['R3Preservation'],old['R3ExistingCapsuleFullEncodingSHA']]:
 fresh=pin(q['path']);assert (fresh['sha256'],fresh['bytes'])==(q['sha256'],q['bytes']);pins.append({k:fresh[k] for k in ['path','bytes','sha256']})
media=[]
for pair in old['fullTenMediaBodiesAndStableMetadata']:
 freshpair=[]
 for q in pair:
  f=pin(q['path']);assert (f['sha256'],f['bytes'],f['xattrs'])==(q['sha256'],q['bytes'],q['xattrs'])
  assert all(f['metadata'][k]==v for k,v in q['metadata'].items() if k!='st_atime_ns');freshpair.append(f)
 assert freshpair[1]['metadata']['st_nlink']==1 and freshpair[0]['metadata']['st_ino']!=freshpair[1]['metadata']['st_ino'];media.append(freshpair)
assert [a['metadata']['st_nlink'] for a,b in media]==[5,5,5,4,5]
selected=json.loads(Path(old['selectedMap']['path']).read_text());assert len(selected['canonicalInputs'])==87 and len(selected['canonicalOutputs'])==56
for a,b in media:
 n=Path(a['path']).name;assert selected['canonicalInputs']['public/art/'+n]==selected['canonicalOutputs']['art/'+n]==a['sha256']==b['sha256']
 assert not Path(b['path']+'.root-share-five-rebuilt-r1.tmp').exists()
zip_after=md(os.lstat(zip_path));assert zip_after==zip_before==old['protectedZipStatAfter']
rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024;assert rss<24*1048576
out={'oldProof':{k:oldpin[k] for k in ['path','bytes','sha256']},'freshPins':pins,'freshTenFullBodiesAndStableMetadata':media,'currentFiveMapEntriesMatch':True,'protectedZipStatBefore':zip_before,'protectedZipStatAfter':zip_after,'protectedZipBodyNeverOpened':True,'ownMaxRSSBytes':rss,'allFDsClosed':True,'outageQualification':'Prior editor completion unobserved at local isolate termination; Root fresh stage read found no REVIEW/seal/GATE. Same packet and original PROOF/guard preserved. This refresh source+full10/body/map/control proof runs in fresh original64+512 guard; no action/Git/native/image/build.'}
with (P/'REFRESH.json').open('x') as f:json.dump(out,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
print(json.dumps({'normal':True,'pins':len(pins),'fullBodies':10,'ownMaxRSSBytes':rss,'allFDsClosed':True}))
