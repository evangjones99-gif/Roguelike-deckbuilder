import os,pathlib,json,hashlib,time
P=pathlib.Path(__file__).parent;C=pathlib.Path('/sys/fs/cgroup')
def read(q):
 fd=os.open(pathlib.Path(q).resolve(strict=True),os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW)
 try:
  with os.fdopen(fd,'rb',closefd=False) as f:return f.read()
 finally:os.close(fd)
def sha(q):return hashlib.sha256(read(q)).hexdigest()
def sample():
 cur=int((C/'memory.current').read_text());mx=int((C/'memory.max').read_text());v=os.statvfs(P)
 return {'time_ns':time.time_ns(),'current':cur,'maximum':mx,'headroom':mx-cur,'free':v.f_bavail*v.f_frsize}
def save(n,b):
 with (P/n).open('xb') as f:f.write(b);f.flush();os.fsync(f.fileno())
def js(n,o):save(n,(json.dumps(o,separators=(',',':'))+'\n').encode())
initial=sample();events=(C/'memory.events').read_text();assert initial['headroom']>=576*1048576 and initial['free']>=64*1048576
v=json.loads(read(P/'PROOF.json'));g=json.loads(read(P/'GUARD-r2/RESULT.json'));assert g['exit_code']==0 and g['failure'] is None and g['memory_events_before']==g['memory_events_after']
for q,row in v['actualAllSmallFilePins'].items():assert sha(pathlib.Path(q))==row['sha256']
js('DRAFT-CAP-DEVIATION.json',{'originalRequestedFinalCapBytes':49152,'actualDraftBeforeSealBytes':51392,'draftOvershootBytes':2240,'originalCapNotSatisfied':True,'newFiniteFinalCapBytes':65536,'newCapAuthorizedByRootBeforeSeal':True,'all105AliasRecordsAndFailureRetained':True,'noExpandedAuditOrCopiesAfterAuthorization':True})
save('REVIEW.md',b'''Confirmed prebrowser caller-method failure with normally closed observed lifecycle/resources. Root launched the caller once; its audit refused the first deliberate final-leaf desktop/audio-lifecycle.cjs symlink because hashFile opens with O_NOFOLLOW. ELOOP here is the no-follow refusal, not evidence of a malformed cyclic mount. The leaf resolves to the expected frozen donor and its small body matches the freeze. All105 known held aliases were inventoried:54 inputs and51 outputs. Each resolves to its assembly-declared frozen donor destination. Existing controls/captures do not need arbitrary symlink permission.

The driver reports24ms with browser/server NOT_LAUNCHED, no contexts/actions/captures/pixel events/page errors, no served or complete before-audit receipt and no JPEGs. Source order is audit before server creation before Chromium launch. The close message with empty errors describes closing absent handles, not proof that a browser ran. Outer rc2/normal_wait false reflects the failed driver; all resource/lifecycle/cleanup checks pass in0.5916496349964291s. Two sampled rows plus initial/final pass896MiB work/512 reserve/events/deadline; one observed PID/starttime now absent, all remaining/zombie sets empty. Peak sampled delta72880128/min headroom1921404928 are aggregate samples, not continuous/exclusive/global attribution.

Freeze and assembly bodies/pins remain exact and all43 small nonmedia current source/output bodies match them. No game app/page was executed or source write exists in this prebrowser audit method; media body hashes were not replayed after the failed attempt, so no fresh universal media-body postcondition is invented. Mounts remain workflow aliases, not OS read-only or self-contained. No art/fit/motion/quality/gameplay/fun conclusion is available.

The next caller should resolve only complete assembly-map-bound input/output held aliases to their exact expected donor destinations, then retain O_NOATIME/O_NOFOLLOW on the resolved regular body and strict non-alias control/capture paths. This review does not approve that unreviewed future implementation. One verifier function-name assumption failed; its original guard/script remain unchanged and the exact source-order correction passed. The original48KiB draft cap was exceeded by2240 bytes before seal; Root explicitly authorized finite64KiB completion before this seal, retaining all aliases and failures. No Node/browser/native/Git writes/PIL/images/large media/ZIP body or runtime mutation by this reviewer.
''')
js('GATE.json',{'decision':'CONFIRM_EXACT_R4_PREBROWSER_CALLER_AUDIT_REFUSAL_AND_OBSERVED_TECHNICAL_CLOSURE','callerAuditMethodRejectedForHeldLeafRepresentation':True,'gameOrVisualTrialExecuted':False,'browserServerNotLaunched':True,'contextsActionsCaptures':0,'driverExitCode':2,'wholeSeconds':v['outerWholeSeconds'],'resourceLifecycleChecksPass':True,'eventsStable':True,'observedPIDStartPairs':1,'allObservedIdentitiesAbsent':True,'knownHeldInputAliases':54,'knownHeldOutputAliases':51,'smallNonmediaBodyChecks':43,'fullMediaPostBodyReplay':False,'frozenMapIdentitiesExact':True,'actualQualityFitGameplayAcceptance':False,'futureCallerRepairAccepted':False,'prior48KiBCapSatisfied':False,'new64KiBCapAuthorizedBeforeSeal':True,'proofSHA256':sha(P/'PROOF.json'),'reviewSHA256':sha(P/'REVIEW.md')})
final=sample();rss=int(next(x.split()[1] for x in pathlib.Path('/proc/self/status').read_text().splitlines() if x.startswith('VmHWM:')))*1024
assert final['headroom']>=512*1048576 and final['current']-initial['current']<=64*1048576 and final['maximum']==initial['maximum'] and final['free']>=64*1048576 and (C/'memory.events').read_text()==events and rss<24*1048576
js('CLOSURE.json',{'status':'CLOSED','normalSourceGuardSHA256':sha(P/'GUARD-r2/RESULT.json'),'initialSeal':initial,'finalSeal':final,'eventsBefore':events,'eventsAfter':(C/'memory.events').read_text(),'ownVmHWMBytes':rss,'scope':'64MiB aggregate source+512reserve/disk64 shared accounting; bootstrap/displays/seal finite outside sampled guard. All own processes/FDs/tools close at successful exit; no runtime tools launched.'})
rows=[{'path':str(q.relative_to(P)),'sha256':sha(q),'bytes':q.stat().st_size} for q in sorted(P.rglob('*')) if q.is_file()]
data=(json.dumps({'selfExcluded':True,'bodies':rows,'gateSHA256':sha(P/'GATE.json'),'closureSHA256':sha(P/'CLOSURE.json'),'finalAuthorizedCapBytes':65536},separators=(',',':'))+'\n').encode()
assert sum(r['bytes'] for r in rows)+len(data)<=65536
save('MANIFEST.json',data)
print(json.dumps({'status':'CLOSED','gateSHA256':sha(P/'GATE.json'),'manifestSHA256':sha(P/'MANIFEST.json'),'closureSHA256':sha(P/'CLOSURE.json'),'finalBytes':sum(r['bytes'] for r in rows)+len(data),'ownVmHWMBytes':rss}))
