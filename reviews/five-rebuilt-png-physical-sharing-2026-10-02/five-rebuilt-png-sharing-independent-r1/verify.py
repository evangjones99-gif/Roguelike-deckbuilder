from pathlib import Path
import os,json,hashlib,stat,resource,ast
resource.setrlimit(resource.RLIMIT_DATA,(24*1048576,24*1048576))
S=Path('/workspace/scratch');R=Path('/workspace/Roguelike-deckbuilder');P=S/'five-rebuilt-png-sharing-independent-r1';A=S/'five-rebuilt-png-recovery-proposal-r1';M=S/'five-rebuilt-png-root-method-author-r1'
KEYS=['st_dev','st_ino','st_mode','st_nlink','st_uid','st_gid','st_size','st_blocks','st_atime_ns','st_mtime_ns','st_ctime_ns']
def md(s):return {k:getattr(s,k) for k in KEYS}
def op(p,flags=os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME):
 p=Path(p);fd=os.open('/',os.O_PATH|os.O_NOFOLLOW|os.O_DIRECTORY)
 try:
  for part in p.parent.parts[1:]:
   assert part not in ('','.', '..');n=os.open(part,os.O_PATH|os.O_NOFOLLOW|os.O_DIRECTORY,dir_fd=fd);os.close(fd);fd=n
  return os.open(p.name,flags,dir_fd=fd)
 finally:os.close(fd)
def pin(p,body=False):
 p=Path(p);before=md(os.lstat(p));fd=op(p);h=hashlib.sha256();parts=[];size=0
 try:
  assert stat.S_ISREG(before['st_mode']) and before==md(os.fstat(fd));attrs={n:os.getxattr(fd,n).hex() for n in os.listxattr(fd)}
  for b in iter(lambda:os.read(fd,65536),b''):
   h.update(b);size+=len(b)
   if body:parts.append(b);assert size<262144
  assert md(os.fstat(fd))==before==md(os.lstat(p))
 finally:os.close(fd)
 q={'path':str(p),'sha256':h.hexdigest(),'bytes':size,'metadata':before,'xattrs':attrs};return (q,b''.join(parts)) if body else q
def load(p):
 q,b=pin(p,True);return q,json.loads(b)
def simple(q):return {k:q[k] for k in ['path','bytes','sha256']}
def save(n,j):
 with (P/n).open('x') as f:json.dump(j,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
protected=S/'retained-original-archives/preflight-bdf273-original-r4.zip';protected_before=md(os.lstat(protected))
pp,e=load(A/'PROPOSAL.json');assert pp['sha256']=='371c1e2df47f30e4abca9abece46864b53f4fb6f25e9a78926ee98a0d7a054c5'
ss,sup=load(A/'SUPPLEMENT-SEAL.json');assert ss['sha256']=='d9281e1d5264fe34b44f8fed40446ec99d402b9a364c76b9885aeb2cf995b29f'
ms,manifest=load(M/'FINAL-SEAL.json');assert ms['sha256']=='02ad809089fc69438277e187cf474f53effb6948cdb52740051e97e34a34cc8d'
for seal,root in [(sup,A),(manifest,M)]:
 for old in seal['files']:
  assert Path(old['path']).is_relative_to(root);q=pin(old['path']);assert (q['sha256'],q['bytes'])==(old['sha256'],old['bytes'])
methods=[]
for name,h in [('share-five-rebuilt-pngs-root-r1.py','77ec35c075e49d757985d7b6dc7ed93bd87eab6a3692604714f18a278f75fdd1'),('publish-five-rebuilt-png-proposal-root-r1.py','f419e4d963a9aed65fa8b739e772eea6fdc1072dc6d454828ced48032004c800'),('judge-five-rebuilt-png-sharing-root-r1.py','9f380ad49fb64e1cb62e18e2c12e9028a583ff5f25f90a4d9e84c9e423a5bf17')]:
 q,b=pin(M/name,True);assert q['sha256']==h;ast.parse(b);methods.append(q)
names={'adversaries-atlas.png','companions-atlas.png','hound-poses.png','pact-seal.png','warleader-poses.png'}
assert len(e['pairs'])==5 and {Path(x['candidate']['path']).name for x in e['pairs']}==names and e['candidateGroup']==str(S/'audio-host-independent-v08/independent/rebuilt-dist/art')
media=[]
for pair in e['pairs']:
 a,b=pair['anchor'],pair['candidate'];assert Path(a['path']).parent==R/'public/art' and Path(b['path']).parent==Path(e['candidateGroup']) and Path(a['path']).name==Path(b['path']).name
 row=[]
 for old in [a,b]:
  q=pin(old['path']);assert q['sha256']==old['sha256'] and q['bytes']==old['fstat']['st_size'] and q['xattrs']==old['xattrs']=={}
  assert all(q['metadata'][k]==v for k,v in old['fstat'].items() if k!='st_atime_ns');q['proposalMetadata']=old['fstat'];q['initialAtimeDifference']=q['metadata']['st_atime_ns']!=old['fstat']['st_atime_ns'];row.append(q)
 assert row[1]['metadata']['st_nlink']==1 and row[0]['metadata']['st_ino']!=row[1]['metadata']['st_ino'] and row[0]['metadata']['st_dev']==row[1]['metadata']['st_dev']==27
 assert row[0]['sha256']==row[1]['sha256'];media.append(row)
 assert not Path(b['path']+'.root-share-five-rebuilt-r1.tmp').exists()
assert [a['metadata']['st_nlink'] for a,b in media]==[5,5,5,4,5]
controls=[];data={}
for old in e['sourceControls']:
 q,b=pin(old['path'],True);assert q['sha256']==old['sha256'];controls.append(q);data[old['path']]=b
src=json.loads(data[str(S/'audio-host-independent-v08/candidate/SOURCE-MANIFEST.json')]);build=json.loads(data[str(S/'audio-host-independent-v08/candidate/BUILD-MANIFEST.json')]);reb=json.loads(data[str(S/'audio-host-independent-v08/independent/independent-rebuild.json')])
assert len(src['files'])==66 and len(build['files'])==51 and src['sourceDigest']==build['sourceDigest']=='eb1e4fcadd0b166092484bf9e7ebddfc4e51f3811e3154a24c8b42663273b1fd'
assert reb['independentViteOutputMatchesEveryAuthorBuildFile'] and b'not approved for production promotion' in data[str(S/'audio-host-independent-v08/independent/REVIEW.md')] and b'NEW output directory' in data[str(S/'audio-host-independent-v08/independent/REVIEW.md')]
hp=next(q for q in controls if q['path']==str(R/'AGENTS.md'));assert hp['sha256']=='6f76b3a724bcf4cd9db8587158a8bd454531c8a8b59fc8680bf7661d896ee2d8'
mp,current=load(S/'target-wait-default-promotion-root-r1/RESULT.json');assert mp['sha256']=='31a221091d2ffbc6d58dfc1385962c441df9789c66729ef64d20b95208a8fabd' and len(current['canonicalInputs'])==87 and len(current['canonicalOutputs'])==56
for a,b in media:
 n=Path(a['path']).name;h=a['sha256'];assert src['files']['public/art/'+n]==build['files']['dist/art/'+n]==current['canonicalInputs']['public/art/'+n]==current['canonicalOutputs']['art/'+n]==h
 assert len([x for x in reb['files'] if x['path']=='dist/art/'+n and x['sha256']==h])==1
alias=[]
for group in e['knownAnchorAliases']:
 anchor=next(a for a,b in media if a['path']==group['anchor']);count=0;rows=[]
 for old in group['knownEntries']:
  if 'lstat' not in old:rows.append({'path':old['path'],'unresolvedHistoricalEntry':True});continue
  fd=op(old['path'],os.O_PATH|os.O_NOFOLLOW)
  try:
   z=md(os.fstat(fd));attrs={n:os.getxattr('/proc/self/fd/'+str(fd),n).hex() for n in os.listxattr('/proc/self/fd/'+str(fd))}
  finally:os.close(fd)
  assert all(z[k]==v for k,v in old['lstat'].items() if k!='st_atime_ns') and attrs==old['xattrs'];same=(z['st_dev'],z['st_ino'])==(anchor['metadata']['st_dev'],anchor['metadata']['st_ino']);assert same==old['sameAnchorInode'];count+=int(same)
  rows.append({'path':old['path'],'sameAnchorInode':same,'metadata':z})
 assert count==group['knownPhysicalCount'] and anchor['metadata']['st_nlink']-count==group['unresolvedPhysicalAliasCount'];alias.append({'anchor':group['anchor'],'knownPhysicalCount':count,'unresolvedPhysicalAliasCount':group['unresolvedPhysicalAliasCount'],'metadataOnlyRows':rows})
post=[]
for name,h in [('GATE.json','3fc19d79046140b365614cda936e4e0875a2c41a97952d4e6ccc93c2c9a532dc'),('FINAL-SEAL.json','35f4966518f4787a4ee34e7dbaa3a3d09c5e2b388df0904f1faaee3ae8cbaa92')]:
 q=pin(S/'five-png-sharing-post-independent-r2'/name);assert q['sha256']==h;post.append(q)
r3=S/'target-clear-ghost-preservation-independent-r1/GATE.json';r3p,r3gate=load(r3);assert r3p['sha256']=='6ec96568886fbeede7c9abacd6365edffa9cb4a7401c9d143ca50a281fd6ac65' and r3gate['completeCoverage'] and r3gate['status']=='CLOSED'
r3dir=R/'reviews/opening-target-clear-ghost-opt-in-2026-10-02';summary=pin(r3dir/'PRESERVATION.json');assert summary['sha256']=='b33053ab9a070a4f8da8b059cf984256eb204a4c2de690b4ff794b622334a046'
capsule=pin(r3dir/('evidence-'+r3gate['archiveSHA256']+'.tar.gz'));assert capsule['sha256']==r3gate['archiveSHA256'] and capsule['bytes']==r3gate['archiveBytes']==1981882
plan=[];destination=R/'reviews/five-rebuilt-png-physical-sharing-2026-10-02'
def add(a,rel):
 q=pin(a);assert q['bytes']<262144;plan.append((q,rel))
for folder in [A,S/'five-png-sharing-post-independent-r2']:
 for p in sorted(folder.rglob('*')):
  if p.is_file():add(p,str(Path(folder.name)/p.relative_to(folder)))
for q in methods:add(q['path'],str(Path('root-controls')/Path(q['path']).name))
add(r3,'root-controls/R3-PRESERVATION-COMPLETE-GATE.json')
for n in ['BEFORE.json','JOURNAL.jsonl','RESULT.json']:add(S/'five-retained-png-sharing-actual-root-r2'/n,'previous-first-five-actual/'+n)
add(S/'five-png-producer-judgment-root-r2.json','previous-first-five-controls/PRODUCER-JUDGMENT.json');add(S/'five-png-recovery-push-root-r1/PUSH-CONFIRMED.json','previous-first-five-controls/PUSH-CONFIRMED.json')
records={rel:{'originalPath':q['path'],'bytes':q['bytes'],'sha256':q['sha256'],'sourceMetadata':q['metadata']} for q,rel in plan}
base=sum(q['bytes'] for q,rel in plan);identitybase=len((json.dumps(records,indent=2)+'\n').encode());assert base==294650
# Future <=96KiB review target/<=16 source leaves, with a conservative900B identity allowance per leaf.
bound=base+96*1024+identitybase+16*900+2048;assert bound<512*1024
protected_after=md(os.lstat(protected));assert protected_after==protected_before
gross=sum(b['metadata']['st_blocks']*512 for a,b in media);assert gross==e['grossOldAllocationBytes']==10170368
rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024;assert rss<24*1048576
save('PROOF.json',{'proposal':pp,'authorSupplementSeal':ss,'methodAuthorSeal':ms,'fullTenMediaBodiesAndStableMetadata':media,'sourceControls':controls,'methods':methods,'selectedMap':mp,'fiveHistoricalAndCurrentEntriesMatch':True,'knownAliasMetadata':alias,'firstPOSTControls':post,'R3CompleteGate':r3p,'R3Preservation':summary,'R3ExistingCapsuleFullEncodingSHA':capsule,'R3LogicalProofReusedNotReplayed':True,'publisherOtherPlan':[{**simple(q),'destinationRelative':rel} for q,rel in plan],'publisherOtherCopiedBytes':base,'publisherOtherIdentityBytes':identitybase,'publisherConservative96KiB16LeafUpperBound':bound,'publisherCapBytes':524288,'publisherMinimumDiskBytes':70254592,'publisherReserveEstimate':'64MiB floor+3MiB total; at most512KiB publications+2.5MiB Git object estimate. Not hard filesystem/object/log/cost bound; ordinary producer/action64 fresh admission can refuse.','grossAllocationBytes':gross,'protectedZipStatBefore':protected_before,'protectedZipStatAfter':protected_after,'protectedZipNeverBodyOpened':True,'historical66_51AndCurrent87_56AggregatesNotFullyRehashed':True,'ownMaxRSSBytes':rss,'allFDsClosed':True,'scope':'Normal64+512 finite readonly proof; no action/Git/image/Node/build/browser/cleanup; other private source guards may co-live, cgroup not exclusive attribution.'})
print(json.dumps({'normal':True,'fullMediaBodies':10,'gross':gross,'baseCopiedBytes':base,'baseIdentityBytes':identitybase,'publisherBound':bound,'ownMaxRSSBytes':rss,'allFDsClosed':True}))
