import os,json,pathlib,hashlib,time,resource
r=pathlib.Path(__file__).parent;cg=pathlib.Path('/sys/fs/cgroup');base=int((cg/'memory.current').read_text());events=(cg/'memory.events').read_text();rows=[]
def guard():
 c=int((cg/'memory.current').read_text());m=int((cg/'memory.max').read_text());v=os.statvfs(r);rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024;row={'time_ns':time.time_ns(),'sharedDelta':c-base,'headroom':m-c,'free':v.f_bavail*v.f_frsize,'ownMaxRSS':rss};rows.append(row)
 assert row['sharedDelta']<=64*1048576 and row['headroom']>=512*1048576 and row['free']>=64*1048576 and rss<24*1048576 and events==(cg/'memory.events').read_text();return row
def meta(s):return {k:getattr(s,k) for k in ['st_dev','st_ino','st_mode','st_nlink','st_uid','st_gid','st_size','st_blocks','st_atime_ns','st_mtime_ns','st_ctime_ns']}
def control(p):
 fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME)
 try:
  before=os.fstat(fd);h=hashlib.sha256();body=b''
  while True:
   b=os.read(fd,65536)
   if not b:break
   h.update(b);body+=b;assert len(body)<128*1024
  assert meta(before)==meta(os.fstat(fd));guard();return {'path':p,'bytes':before.st_size,'sha256':h.hexdigest(),'O_NOATIME':True,'duringReadMetadataExact':True},body
 finally:os.close(fd)
guard();e=json.loads((r/'EVIDENCE.json').read_text());assert e['verification']=='EXACT_MATCH'
oldpin,oldbody=control('/workspace/scratch/audio-host-independent-v08/independent/REVIEW.md')
sharepin,sharebody=control('/workspace/scratch/frozen128-canonical-media-sharing-proposal-root-r1/PROPOSAL.json')
old=oldbody.decode();assert 'new output directory' in old and 'production promotion' in old and 'eb1e4fcadd0b166092484bf9e7ebddfc4e51f3811e3154a24c8b42663273b1fd' in old
sharing=json.loads(sharebody);aliases=[];parents=[]
for pair in e['pairs']:
 p=pair['canonical']['path'];name=os.path.basename(p)
 prior=next(g for g in sharing['groups'] if g['anchor']==p)
 paths=[p,'/workspace/Roguelike-deckbuilder/dist/art/'+name]+[x['path'] for x in prior['recipients']]
 current=[]
 for a in paths:
  s=os.stat(a,follow_symlinks=False);assert s.st_dev==pair['canonical']['metadata']['st_dev'] and s.st_ino==pair['canonical']['metadata']['st_ino']
  current.append({'path':a,'metadata':meta(s),'xattrs':{n:os.getxattr(a,n,follow_symlinks=False).hex() for n in os.listxattr(a,follow_symlinks=False)}})
 assert len(current)==pair['canonical']['metadata']['st_nlink']==4
 aliases.append({'canonical':p,'fourKnownPhysicalDirectoryEntries':current,'observedEntryCountEqualsNlink':True,'qualification':'Physical hardlink count only; not a universal symlink/process/mmap/future-consumer inventory.'})
for p in [e['selectedGroup'],'/workspace/Roguelike-deckbuilder/public/art']:
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_NOATIME)
 try:parents.append({'path':p,'metadata':meta(os.fstat(fd)),'xattrs':{n:os.getxattr(fd,n).hex() for n in os.listxattr(fd)}})
 finally:os.close(fd)
context={'sourceControls':[oldpin,sharepin],'knownCanonicalAliases':aliases,'heldParentsMetadata':parents,'historicalConsumer':'Retained audio host independent review records candidate source eb1e4fc... /66 inputs and51 built outputs, exact independent reproduction into a new output directory and built-host diagnostics. Host was explicitly not approved for production promotion because resize removed binding visuals while scheduled audio continued. No historical report is overwritten or invalidated by retaining exact media bytes/paths.','consumerQualification':'These controls identify a historical reproduction/HTTP consumer, not proof that no process or future build can reopen it. Root must explicitly freeze all three candidate dist leaves and reproduce only into fresh stages before transaction. No runtime/FD scan here.','rootHoldStatus':'Root states it will add the exact three-leaf immutable/fresh-stage-only workflow hold. This packet does not claim that designation is already published, OS-enforced, or transaction authorization.','physicalEncodingPreference':'Conditional only: same PNG bytes are retained at canonical and historical names, and source/review/provenance remain. Independent reviewer must prefer shared encoding and decide old physical isolation is unnecessary; producer records acceptance of inode/time/shared-write losses before any action.','metadataEffects':'Recipient identities and atime/mtime would become canonical, original recipient inode encoding ultimately retired only after independent postcheck/producer judgment. Canonical nlink would become5 and ctime change; existing aliases observe that shared metadata. Candidate parent entries/times change. No timestamp/chmod/xattr equalization allowed; original metadata ledger stays retained.','rollback':'A separately authored Root transaction needs unique temporary link names, durable before/after journal, exact drift checks, retained old inode backups and atomic three-path replacement. Body/path rollback remains possible; exact kernel inode/ctime history cannot be recreated after original-inode retirement. No transaction implementation provided here.','proposalLimits':'Only the exact three PNG recipients selected in EVIDENCE. No remaining49 groups, audio, archives, JS/JSON duplicate bodies, extra art or source retirement. Discovery console with full excluded list truncated; focused exact summary re-read afterward, underlying guarded evidence intact.'}
with (r/'CONTEXT.json').open('x') as f:json.dump(context,f,indent=2);f.write('\n')
report='Propose only the three existing PNG leaves in '+e['selectedGroup']+' for independently reviewed exact-byte physical sharing with canonical public. Gross candidate allocation is '+str(e['allocatedCandidateBytes'])+' bytes on device27; logical bytes '+str(e['logicalCandidateBytes'])+'. Every full SHA, size, mode0600, owner1000:1000 and empty xattrs matches, with independent nlink1 historical inodes. O_NOATIME reads retained full metadata exactly. No recovery has occurred.\n\nThe complete bounded scratch metadata walk visited5,288 directories /37,640 entries without errors or symlink-directory traversal. Protected/retained-original archives, .git and node_modules were excluded. One eligible group was hashed; no second PNG group or other encoding was investigated. Existing canonical four hardlink entries per PNG are identified from the prior sharing record and current stat checks. This physical-entry count is not a global logical alias/process/mmap/future-writer absence proof.\n\nThe historical audio host was rejected for production promotion but preserves useful diagnostics and an exact build reproduction. Retain that source, its PNG paths/bytes, rights/provenance, manifests, reviews and rollback. Reproduction must use fresh stages. Root proposes an explicit immutable/fresh-stage-only hold for precisely these three old dist leaves; the hold is not yet certified by this packet. Existing canonical/frozen aliases remain held. Sharing trades old independent inode/time/writable isolation for retained-byte storage; independent preference and producer judgment must accept those exact losses before a current-push-verified journalled Root transaction. No action authority, hardlink, unlink, retirement, OS read-only guarantee or exact full-metadata rollback is implied.\n\nGross allocation is not a promised8MiB net recovery. This proposal packet and subsequent independent review/journal/backup/push footprints reduce available capacity; backups retain old allocation until separately reviewed retirement. Fresh actual disk/memory admission must pass after any approved recovery. All original candidates and previous negative case remain unchanged.\n'
with (r/'PROPOSAL.md').open('x') as f:f.write(report)
pins=[]
for p in sorted(r.rglob('*')):
 if not p.is_file() or 'seal-guard-r1' in p.parts:continue
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(65536),b''):h.update(b)
 pins.append({'path':str(p),'bytes':p.stat().st_size,'sha256':h.hexdigest()});guard()
g=json.loads((r/'reader-guard-r1/RESULT.json').read_text());assert g['exit_code']==0 and g['failure'] is None and g['memory_events_before']==g['memory_events_after']
seal={'decision':'Conditional exact-three-PNG storage proposal only; independent and producer judgment required; no action/recovery.','files':pins,'sourceControls':context['sourceControls'],'grossAllocation':e['allocatedCandidateBytes'],'resource':{'rows':rows,'final':guard(),'eventsBefore':events,'eventsAfter':(cg/'memory.events').read_text(),'qualifiedAggregateWorkMiB':64,'ownRSSLimitMiB':24,'allInputFDsClosed':True},'outerGuard':str(r/'seal-guard-r1/RESULT.json'),'outerGuardNote':'Generated after this seal; completed exact hash reported separately.','packetCap':128*1024,'packetBytesBeforeSeal':sum(p['bytes'] for p in pins)}
with (r/'FINAL-SEAL.json').open('x') as f:json.dump(seal,f,indent=2);f.write('\n')
total=sum(p.stat().st_size for p in r.rglob('*') if p.is_file());assert total<128*1024
print(json.dumps({'packetBytes':total,'grossAllocation':e['allocatedCandidateBytes'],'netMinusThisPacketOnly':e['allocatedCandidateBytes']-total,'futureCostsExcluded':True,'final':guard()}))
