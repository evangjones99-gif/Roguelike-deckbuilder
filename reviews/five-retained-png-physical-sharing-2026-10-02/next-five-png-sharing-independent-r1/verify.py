from pathlib import Path
import os,json,hashlib,stat,resource,ast
resource.setrlimit(resource.RLIMIT_DATA,(24*1048576,24*1048576))
S=Path('/workspace/scratch');R=Path('/workspace/Roguelike-deckbuilder');P=S/'next-five-png-sharing-independent-r1';A=S/'five-retained-png-recovery-proposal-r1'
KEYS=['st_dev','st_ino','st_mode','st_nlink','st_uid','st_gid','st_size','st_blocks','st_atime_ns','st_mtime_ns','st_ctime_ns']
def md(s):return {k:getattr(s,k) for k in KEYS}
def op(p,flags=os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME):
 p=Path(p);fd=os.open('/',os.O_PATH|os.O_NOFOLLOW|os.O_DIRECTORY)
 try:
  for c in p.parent.parts[1:]:
   assert c not in ('','.', '..');n=os.open(c,os.O_PATH|os.O_NOFOLLOW|os.O_DIRECTORY,dir_fd=fd);os.close(fd);fd=n
  return os.open(p.name,flags,dir_fd=fd)
 finally:os.close(fd)
def pin(p,body=False):
 p=Path(p);before=md(os.lstat(p));fd=op(p);parts=[];h=hashlib.sha256()
 try:
  assert stat.S_ISREG(before['st_mode']) and md(os.fstat(fd))==before
  attrs={k:os.getxattr(fd,k).hex() for k in os.listxattr(fd)}
  for b in iter(lambda:os.read(fd,65536),b''):
   h.update(b)
   if body:parts.append(b);assert sum(map(len,parts))<262144
  assert md(os.fstat(fd))==before==md(os.lstat(p))
 finally:os.close(fd)
 out={'path':str(p),'sha256':h.hexdigest(),'bytes':before['st_size'],'metadata':before,'xattrs':attrs}
 return (out,b''.join(parts)) if body else out
def load(p):
 a,b=pin(p,True);return a,json.loads(b)
def save(n,j):
 with (P/n).open('x') as f:json.dump(j,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
pp,e=load(A/'PROPOSAL.json');assert pp['sha256']=='b4e8803f2411e932c994b01aa50152fee4b4bd9d2c8757258ae7c686b75745bc'
sp,se=load(A/'FINAL-SEAL.json');assert sp['sha256']=='6399e7b0e90374adc8872f1e1decfdc74989e8e506b77034e68e8aba14a0633b'
author_members=[]
for row in se['files']:
 path=Path(row['path']);assert path.is_relative_to(A);q=pin(path)
 assert (q['sha256'],q['bytes'])==(row['sha256'],row['bytes']);author_members.append({'path':str(path),'bytes':q['bytes'],'sha256':q['sha256']})
for gd in ['GUARD','MAP-GUARD','SEAL-GUARD']:
 _,g=load(A/gd/'RESULT.json');assert g['exit_code']==0 and g['failure'] is None and g['memory_events_before']==g['memory_events_after']
names={'adversaries-atlas.png','companions-atlas.png','hound-poses.png','pact-seal.png','warleader-poses.png'}
assert len(e['pairs'])==5 and {Path(x['candidate']['path']).name for x in e['pairs']}==names
media=[];atime=[]
for pair in e['pairs']:
 a=pair['anchor'];b=pair['candidate'];assert Path(a['path']).parent==R/'public/art' and Path(b['path']).parent==S/'audio-host-independent-v08/candidate/dist/art'
 assert Path(a['path']).name==Path(b['path']).name
 fresh=[]
 for old in [a,b]:
  q=pin(old['path']);assert q['sha256']==old['sha256'] and q['bytes']==old['fstat']['st_size'] and q['xattrs']==old['xattrs']=={}
  assert all(q['metadata'][k]==v for k,v in old['fstat'].items() if k!='st_atime_ns')
  if q['metadata']['st_atime_ns']!=old['fstat']['st_atime_ns']:atime.append({'path':old['path'],'proposalAtime':old['fstat']['st_atime_ns'],'freshAtime':q['metadata']['st_atime_ns']})
  fresh.append(q)
 assert fresh[0]['sha256']==fresh[1]['sha256'] and fresh[0]['metadata']['st_dev']==fresh[1]['metadata']['st_dev']==27
 assert fresh[1]['metadata']['st_nlink']==1 and fresh[0]['metadata']['st_ino']!=fresh[1]['metadata']['st_ino'];media.append(fresh)
controls=[];bodies={}
for old in e['sourceControls']:
 q,b=pin(old['path'],True);assert q['sha256']==old['sha256'];controls.append(q);bodies[old['path']]=b
source=json.loads(bodies[str(S/'audio-host-independent-v08/candidate/SOURCE-MANIFEST.json')]);build=json.loads(bodies[str(S/'audio-host-independent-v08/candidate/BUILD-MANIFEST.json')]);rebuild=json.loads(bodies[str(S/'audio-host-independent-v08/independent/independent-rebuild.json')])
assert len(source['files'])==66 and len(build['files'])==51 and source['sourceDigest']==build['sourceDigest']=='eb1e4fcadd0b166092484bf9e7ebddfc4e51f3811e3154a24c8b42663273b1fd'
assert rebuild['independentViteOutputMatchesEveryAuthorBuildFile'] is True
review=bodies[str(S/'audio-host-independent-v08/independent/REVIEW.md')]
assert b'not approved for production promotion' in review and b'NEW output directory' in review
hold=bodies[str(R/'AGENTS.md')];assert b'The five historical' in hold and b'fresh-stage-only' in hold and all(n.encode() in hold for n in names)
hp=next(x for x in controls if x['path']==str(R/'AGENTS.md'));assert hp['sha256']=='b674fd4456ad4332c97ad4538fbf8c008842c708964a16e1acde77790bea0906'
mp,m=load(S/'target-wait-default-promotion-root-r1/RESULT.json');assert mp['sha256']=='31a221091d2ffbc6d58dfc1385962c441df9789c66729ef64d20b95208a8fabd' and len(m['canonicalInputs'])==87 and len(m['canonicalOutputs'])==56
for a,b in media:
 n=Path(a['path']).name;h=a['sha256']
 assert source['files']['public/art/'+n]==build['files']['dist/art/'+n]==h
 assert len([x for x in rebuild['files'] if x['path']=='dist/art/'+n and x['sha256']==h])==1
 assert m['canonicalInputs']['public/art/'+n]==m['canonicalOutputs']['art/'+n]==h
alias=[]
for group in e['knownAnchorAliases']:
 count=0;rows=[]
 a=next(x[0] for x in media if x[0]['path']==group['anchor'])
 for old in group['knownEntries']:
  if 'lstat' not in old:
   rows.append({'path':old['path'],'qualification':'author unresolved path, no fresh traversal'});continue
  fd=op(old['path'],os.O_PATH|os.O_NOFOLLOW)
  try:
   z=md(os.fstat(fd));attrs={k:os.getxattr('/proc/self/fd/'+str(fd),k).hex() for k in os.listxattr('/proc/self/fd/'+str(fd))}
  finally:os.close(fd)
  assert all(z[k]==v for k,v in old['lstat'].items() if k!='st_atime_ns') and attrs==old['xattrs']
  same=(z['st_dev'],z['st_ino'])==(a['metadata']['st_dev'],a['metadata']['st_ino']);assert same==old['sameAnchorInode'];count+=int(same);rows.append({'path':old['path'],'sameAnchorInode':same,'metadata':z})
 assert count==group['knownPhysicalCount'] and a['metadata']['st_nlink']-count==group['unresolvedPhysicalAliasCount']
 alias.append({'anchor':group['anchor'],'knownPhysicalCount':count,'unresolvedPhysicalAliasCount':a['metadata']['st_nlink']-count,'rows':rows})
methods=[]
for name,h in [('share-five-retained-pngs-root-r1.py','55cc724ef39fd38ef1c56bedcbf4c7a5e870e3c3f119dbe8a478c234658e5e97'),('publish-five-png-proposal-root-r1.py','29616f1a4ed5fdfc40b193b77b3811132522f54f395b4238ae8bde03f7832212'),('judge-five-png-sharing-root-r1.py','d44355995e72305943603adef0c6604ffd63aeb2558eecbffeb9a5f8a830d0b4')]:
 q,b=pin(S/name,True);assert q['sha256']==h;ast.parse(b);methods.append(q)
payload=[]
for folder in [A,S/'two-json-retirement-post-independent-r1',S/'two-json-retirement-post-independent-r2']:
 for p in sorted(folder.rglob('*')):
  if p.is_file():
   q=pin(p);assert q['bytes']<262144;payload.append({'path':str(p),'bytes':q['bytes'],'sha256':q['sha256']})
base=sum(x['bytes'] for x in payload)+sum(x['bytes'] for x in methods)
assert base+96*1024<512*1024
gross=sum(b['metadata']['st_blocks']*512 for a,b in media);assert gross==e['grossOldAllocationBytes']==10170368
rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024;assert rss<24*1048576
save('PROOF.json',{'proposal':pp,'authorSeal':sp,'authorMembers':author_members,'mediaFullBodies':media,'atimeOnlyDifferences':atime,'sourceControls':controls,'selectedMap':mp,'fiveHistoricalAndSelectedEntriesMatch':True,'historical66_51AndCurrent87_56NotFullyRehashed':True,'knownAliasMetadata':alias,'methodsFullPinnedASTParsedUnexecuted':methods,'payloadOtherFiles':payload,'publicationBaseCopiedBodyBytes':base,'publicationConservativeCopiedBodyUpperBound':base+96*1024,'copiedBodyLimit':512*1024,'grossAllocationBytes':gross,'ownMaxRSSBytes':rss,'streamChunkBytes':65536,'allInputFDsClosed':True,'scope':'No action, Git, archives, Node, build, browser, image decoding, restoration or other cleanup. Known aliases metadata only; global aliases/Fds/mmap/future consumers not disproved. All meaningful control and media reads in normal64+512 guard; bootstrap empty own mkdir/source editor and earlier bounded source displays outside guard.'})
print(json.dumps({'proofNormal':True,'gross':gross,'baseCopiedBytes':base,'upperBound':base+96*1024,'ownMaxRSSBytes':rss,'allFDsClosed':True}))
