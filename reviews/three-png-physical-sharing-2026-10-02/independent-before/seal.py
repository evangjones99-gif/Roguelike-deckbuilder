import os,json,hashlib,pathlib,time,resource
resource.setrlimit(resource.RLIMIT_DATA,(24*1048576,24*1048576))
P=pathlib.Path('/workspace/scratch/three-retained-png-sharing-before-independent-r1');C=pathlib.Path('/sys/fs/cgroup')
def j(p):
 with p.open() as f:return json.load(f)
def h(p):
 z=hashlib.sha256();n=0
 with p.open('rb') as f:
  for b in iter(lambda:f.read(32768),b''):z.update(b);n+=len(b)
 return {'sha256':z.hexdigest(),'bytes':n}
def wr(n,o):
 with (P/n).open('x') as f:json.dump(o,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def snap():
 cur=int((C/'memory.current').read_text());mx=int((C/'memory.max').read_text());v=os.statvfs(P)
 return {'current':cur,'headroom':mx-cur,'free':v.f_bavail*v.f_frsize,'utcNs':time.time_ns()}
i=snap();ev=(C/'memory.events').read_text();assert i['headroom']>=576*1048576 and i['free']>=64*1048576
p=j(P/'PROOF.json');r=j(P/'GUARD/RESULT.json');assert j(P/'GUARD/ADMISSION.json')['admitted'] and r['exit_code']==0 and r['failure'] is None and r['memory_events_before']==r['memory_events_after']
pts=[r['initial']]+r['samples']+[r['final']]
for v in pts:assert v['headroom']>=512*1048576 and v['current']-r['initial']['current']<=64*1048576 and v['free']>=1048576
review='''Accepted this exact three-PNG before proposal and the unexecuted Root r2 method, conditional on a recorded producer judgment accepting the stated losses and a fresh verified push of the proposal, review and exact workflow holds. This review grants no action.

The historical abbey-courtyard, tool-vignettes and hunter-portrait leaves are regular independent nlink1 files. All bytes, full stats, mode0600, owner1000:1000 and empty xattrs match the sealed proposal and canonical bodies. Gross old allocation is8,499,200 bytes, logical8,492,116. Net recovery remains unknown until an actual bounded transaction/postcheck because proof and preservation footprint consumes space. Full selected87 inputs/56 outputs still match1d5bf40a/30ddc549. Historical66-source/51-build ledgers, source/reviews, negative audio-host findings and exact PNG provenance remain; commercial rights remain pending. No quality or game-behavior change follows byte sharing.

I prefer shared exact byte encoding for these three frozen historical leaves. Their private physical encoding is not needed to reproduce historical bytes, keep rights evidence, retain old findings or restore separate future byte copies. Their exact inode/ctime history and independent write isolation do have value, but this scoped storage benefit outweighs those losses under the specific immutable/fresh-stage holds. This judgment does not apply to any other group or artifact.

Canonical nlink4 has three observed distinct physical entries and one unresolved entry per leaf. Current canonical dist is separate. A new link would change shared nlink/ctime for all aliases, including the unresolved entry; exact bodies remain identical. Existing known workflow holds and the new specific historical-leaf hold are checked, but no universal alias metadata hold, process, mmap or future-writer absence is proven. Holds are coordinated workflow rules, not OS read-only protection. Future modifications must use fresh names/inodes and stages. No universal physical isolation remains after sharing.

Root r2 ties exact proposal/gate/judgment/push, method/AGENTS/map hashes and producer decision together. It requires recorded confirmed clean matching push/commit and checks local Git status when Root later runs it. It checks all three old/canonical full stats, xattrs, bytes and absent temporary paths before mutation; full87/56 maps before and after; protected original archive metadata only, never its body. It durably saves BEFORE and journals each pre-link, durable link and per-leaf atomic replacement with directory fsync. Each resulting body and inode match is checked. There are no existing body writes, chmod, xattr or timestamp-setting operations. A partial prefix or temp can survive interruption, but its before/journal records remain. No all-three or power-loss-complete atomicity, automatic rollback or retry is claimed.

The method deliberately differs from unchanged author CONTEXT: it makes no old-inode backups and replaces each leaf sequentially. This acceptance explicitly permits deciding those exact redundant private physical encodings unnecessary before the later producer decision/action. Byte/path rollback is available from held canonical/checkpoint bytes; exact original inode/ctime rollback cannot be restored. Partial failures must be preserved and diagnosed under a fresh scope before continuation. The author backup suggestion has not been rewritten or falsely fulfilled.

Author stale current-dist alias-assumption failure, original source and guard are retained; corrected proposal/resource/seal checks pass. My initial discovery looked for BUILD/SOURCE-MANIFEST under independent rather than candidate and failed without mutation; the correct controls were found with rg and verified. Earlier ordinary source-document reads may affect atime; the verifier streams all PNG/runtime media with O_NOATIME and checks full stats remain exact. Reviewer source64+512 guard passes, all author resource rows/guard events were checked, and own reader stays below24MiB. Shared-cgroup samples do not establish exclusive actor attribution. No Node, browser, image/native action, Git, protected archive body read or storage mutation occurred. All tools/readers/FDs close before return.
'''
with (P/'REVIEW.md').open('x') as f:f.write(review);f.flush();os.fsync(f.fileno())
vm=next(int(v.split()[1])*1024 for v in pathlib.Path('/proc/self/status').read_text().splitlines() if v.startswith('VmHWM:'));assert vm<24*1048576
f=snap();assert f['headroom']>=512*1048576 and f['current']-i['current']<=64*1048576 and f['free']>=64*1048576 and ev==(C/'memory.events').read_text()
g={'decision':p['decision'],'proof':h(P/'PROOF.json'),'proposalPins':p['proposalPins'],'methodSHA256':p['rootMethodR2']['sha256'],'originalMethod':p['rootMethodR1'],'holdSHA256':p['hold']['sha256'],'selectedMapSHA256':p['selectedMap']['sha256'],'exactThreeBeforeBodiesMetadataXattrs':True,'grossAllocationBytes':p['grossAllocationBytes'],'current87Inputs56OutputsExact':True,'selectedSourceDigest':p['selectedSourceDigest'],'selectedOutputsDigest':p['selectedOutputsDigest'],'independentPreference':p['judgment'],'methodLimits':p['methodLimits'],'unknownCanonicalAliasQualification':p['knownAliases'],'retainedAuthorFailure':p['retainedAuthorFailure'],'methodDiscoveryFailure':p['ownMethodDiscoveryFailure'],'producerJudgmentAndFreshPushRequiredBeforeAnyAction':True,'noTransactionOrExtraRetirementAuthority':True,'noActionOccurred':True,'protectedArchiveMetadataOnly':p['protectedMetadataOnly'],'authorResources':p['authorGuardGroups'],'reviewerGuard':{'result':h(P/'GUARD/RESULT.json'),'points':len(pts),'minimumHeadroom':min(v['headroom'] for v in pts),'maximumAggregateDelta':max(v['current']-r['initial']['current'] for v in pts),'eventsUnchanged':True,'ownVmHWM':p['ownVmHWM']},'seal64Work512Reserve':{'initial':i,'finalBeforeSmallSealWrites':f,'eventsUnchanged':True,'ownVmHWM':vm,'sharedSourceAccountingQualified':True},'CLOSED':'All finite readers/guard/FDs closed; sealer has no child. Source method accepted only, no executed storage transaction or global absence claim.'}
wr('GATE.json',g);wr('MANIFEST.json',{'decision':p['decision'],'selfExcluded':True,'CLOSED':True,'files':[{'name':str(x.relative_to(P)),**h(x)} for x in sorted(P.rglob('*')) if x.is_file()]})
size=sum(x.stat().st_size for x in P.rglob('*') if x.is_file());assert size<=192*1024
print(json.dumps({'GATE':h(P/'GATE.json'),'MANIFEST':h(P/'MANIFEST.json'),'PROOF':h(P/'PROOF.json'),'method':p['rootMethodR2'],'hold':p['hold'],'selectedMap':p['selectedMap'],'packetBytes':size,'CLOSED':True}))
