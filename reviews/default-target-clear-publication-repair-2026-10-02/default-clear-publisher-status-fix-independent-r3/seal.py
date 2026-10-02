import os,pathlib,json,hashlib,time
P=pathlib.Path(__file__).parent;C=pathlib.Path('/sys/fs/cgroup')
def read(q):
 fd=os.open(q,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW)
 try:
  with os.fdopen(fd,'rb',closefd=False) as f:return f.read()
 finally:os.close(fd)
def sha(q):return hashlib.sha256(read(q)).hexdigest()
def state():
 cur=int((C/'memory.current').read_text());mx=int((C/'memory.max').read_text());v=os.statvfs(P)
 return {'time_ns':time.time_ns(),'current':cur,'maximum':mx,'headroom':mx-cur,'free':v.f_bavail*v.f_frsize}
def save(n,b):
 with (P/n).open('xb') as f:f.write(b);f.flush();os.fsync(f.fileno())
def js(n,o):save(n,(json.dumps(o,separators=(',',':'))+'\n').encode())
initial=state();events=(C/'memory.events').read_text();assert initial['headroom']>=576*1048576 and initial['free']>=64*1048576
proof=json.loads(read(P/'PROOF.json'));supp=json.loads(read(P/'SUPPLEMENT-r4.json'));guard=json.loads(read(P/'GUARD-r3/RESULT.json'))
assert guard['exit_code']==0 and guard['failure'] is None and guard['memory_events_before']==guard['memory_events_after']
for q,row in proof['pins'].items():assert sha(pathlib.Path(q))==row['sha256']
assert sha(pathlib.Path('/workspace/scratch/default-clear-publisher-tracking-fix-root-r4/publish-selected-r4.py'))==supp['r4SHA256']
review='''The exact r3 publisher is rejected because its inherited unconditional git add -u oldJS command addresses an absent, untracked index path. The three requested changes reverse byte-exactly to reviewed publisher2fb277: add the original common directory to sys.path, use fresh receipt Qr2 and replace strip() with rstrip('\\r\\n'). Original common/PLAN bodies and the previously accepted complete preservation gate match. The trim repair preserves leading porcelain status spaces. First publication receipt contains only one successful read-only git status command; guard exit1/failureNull and the AssertionError for M src/main.ts are retained. It refused before evidence copies, Git staging, commit or push. Normal selection and old-source/five-output rollback flags are evidenced by its small RESULT; this review did not rehash144 runtime/media bodies or the archive.

Current read-only Git status contains exactly leading-space modified src/main.ts and the three untracked capsule files. HEAD matches the prepared plan; old JS has no indexed entry. Ignored dist changes do not appear as a tracked rename/untracked status pair. This is a source-method rejection, not an observed execution of r3.

The distinct r4 supplement is accepted for Root's exact scoped publication method only. It adds a read-only ls-files check and calls add -u oldJS only when that path is tracked. Currently the query is empty, so the inherited blocker is skipped; if an old tracked path exists its removal is still staged. The entire r4 body inverses exactly to r3 with that sole conditional. Force-add of the five new nonmedia outputs, all evidence-copy constraints, canonical audit, complete-capsule hash check, intended commit/push, remote equality and final clean receipt controls remain unchanged. Qr2 is still absent, and no r3/r4 publisher has been run. The tiny Root r4 source bootstrap was unguarded and is explicitly qualified; its Python compile is grammar only, not execution acceptance.

Reader failures are retained: an inverse first removed original pre-existing import/sys flags too broadly, then its corrected script's Git subprocess was refused under inherited24MiB RLIMIT_DATA mappings. A new compact wrapper removes only that inherited DATA ceiling, keeping outer64MiB aggregate guard and final own RSS<24MiB; no resident-memory failure is inferred. Corrected source guard passed. No Node/native/browser/import/publisher execution, Git write, runtime/media/huge ZIP hash or canonical mutation occurred. This gate does not claim publication completed, new version/tag/release, art/game quality or cleanup/retirement authorization.
'''
save('REVIEW.md',review.encode())
js('GATE-r3.json',{'decision':'REJECT_EXACT_R3_PUBLISHER_SOURCE_UNTRACKED_OLD_JS_UPDATE','sourceOnly':True,'publisherSHA256':supp['r3SHA256'],'exactThreeRequestedChanges':True,'oldJSUntracked':True,'blocker':'Unconditional add -u oldJS when absent from index','r3Executed':False,'originalFailedPublicationPreserved':True,'proofSHA256':sha(P/'PROOF.json'),'reviewSHA256':sha(P/'REVIEW.md')})
js('GATE-r4.json',{'decision':'ACCEPT_EXACT_R4_PUBLISHER_SOURCE_WITH_CONDITIONAL_TRACKED_OLD_JS_UPDATE_ONLY','sourceOnly':True,'publisherSHA256':supp['r4SHA256'],'publisherBytes':supp['r4Bytes'],'inverseExactR3':True,'inheritedOldJSBlockerResolvedInSource':True,'commonAndPLANUnchanged':True,'currentPorcelainAllowedAndHEADExact':True,'freshReceiptQAbsent':True,'completePreservationGateSHA256':proof['completePreservationGateSHA256'],'normalSelectionReceiptVerified':True,'actualPublisherExecution':False,'runtimeMediaArchiveBodiesNotRehashed':True,'rootTinyBootstrapUngardedQualified':True,'originalR3RejectionPreserved':True,'supplementSHA256':sha(P/'SUPPLEMENT-r4.json'),'r3GateSHA256':sha(P/'GATE-r3.json'),'reviewSHA256':sha(P/'REVIEW.md'),'releaseRetirementCleanupAccepted':False})
final=state();rss=int(next(x.split()[1] for x in pathlib.Path('/proc/self/status').read_text().splitlines() if x.startswith('VmHWM:')))*1024
assert final['headroom']>=512*1048576 and final['current']-initial['current']<=64*1048576 and final['maximum']==initial['maximum'] and final['free']>=64*1048576 and (C/'memory.events').read_text()==events and rss<24*1048576
js('CLOSURE.json',{'status':'CLOSED','guardNormal':True,'guardSHA256':sha(P/'GUARD-r3/RESULT.json'),'sealInitial':initial,'sealFinal':final,'eventsBefore':events,'eventsAfter':(C/'memory.events').read_text(),'ownVmHWMBytes':rss,'scope':'64MiB aggregate source+512reserve/disk64; co-live tiny source reviewer, not exclusive attribution. Bootstrap/displays/seal finite outside guard. All own tools/processes/FDs closed at successful exit; Git commands only read status/index/HEAD.'})
rows=[{'path':str(q.relative_to(P)),'sha256':sha(q),'bytes':q.stat().st_size} for q in sorted(P.rglob('*')) if q.is_file()]
data=(json.dumps({'selfExcluded':True,'bodies':rows,'r3GateSHA256':sha(P/'GATE-r3.json'),'r4GateSHA256':sha(P/'GATE-r4.json'),'closureSHA256':sha(P/'CLOSURE.json'),'familyCapBytes':48*1024},separators=(',',':'))+'\n').encode()
assert sum(r['bytes'] for r in rows)+len(data)<=48*1024
save('MANIFEST.json',data)
print(json.dumps({'status':'CLOSED','r3GateSHA256':sha(P/'GATE-r3.json'),'r4GateSHA256':sha(P/'GATE-r4.json'),'manifestSHA256':sha(P/'MANIFEST.json'),'closureSHA256':sha(P/'CLOSURE.json'),'familyBytes':sum(r['bytes'] for r in rows)+len(data),'ownVmHWMBytes':rss}))
