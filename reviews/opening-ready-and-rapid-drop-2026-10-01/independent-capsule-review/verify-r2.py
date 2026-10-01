import os,json,hashlib,pathlib,resource,tarfile,difflib,subprocess,collections,time
P=pathlib.Path('/workspace/scratch/ready-and-drag-capsule-independent-r1');R=pathlib.Path('/workspace/Roguelike-deckbuilder');A=R/'reviews/opening-ready-and-rapid-drop-2026-10-01';ROOT=pathlib.Path('/workspace/scratch/ready-and-drag-evidence-capsule-root-r1');S=pathlib.Path('/workspace/scratch')
resource.setrlimit(resource.RLIMIT_DATA,(24*1048576,24*1048576))
def openread(p,mode='rb'):return os.fdopen(os.open(str(p),os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW),mode)
def h(p):
 z=hashlib.sha256();n=0
 with openread(p) as f:
  while True:
   b=f.read(32768)
   if not b:break
   z.update(b);n+=len(b)
 return {'sha256':z.hexdigest(),'bytes':n}
def read(p):
 with openread(p) as f:return f.read()
def j(p):return json.loads(read(p))
def sha(b):return hashlib.sha256(b).hexdigest()
def write(n,v):
 with (P/n).open('x') as f:json.dump(v,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
summary=j(A/'SUMMARY.json');archive=A/'evidence.tar.gz';ap=h(archive);assert ap=={'sha256':'27c7d4e2a117c5fa2625146a5ca78e7965705f8f809e44b6c2d7b9efb52817af','bytes':3303630}
assert summary['archiveSHA256']==ap['sha256'] and summary['archiveBytes']==ap['bytes']
seen=set();verified={};manifest=None;manifestpin=None
with openread(archive) as f,tarfile.open(fileobj=f,mode='r|gz',bufsize=32768) as tar:
 for member in tar:
  assert member.isfile() and member.name not in seen and not member.linkname;seen.add(member.name)
  assert not pathlib.PurePosixPath(member.name).is_absolute() and '..' not in pathlib.PurePosixPath(member.name).parts
  with tar.extractfile(member) as body:
   if member.name=='MANIFEST.json':
    raw=body.read();manifest=json.loads(raw);manifestpin=sha(raw);assert manifestpin==summary['manifestSHA256']=='005225286c6784598181a46bd0ad25cc99d4ee54b3c2394d58d5ea915b41155b'
   else:
    assert member.name.startswith('blobs/') and len(member.name)==70;z=hashlib.sha256();n=0
    while True:
     b=body.read(32768)
     if not b:break
     z.update(b);n+=len(b)
    pin=member.name[6:];assert z.hexdigest()==pin and n==member.size;verified[pin]=n
assert manifest and len(seen)==662 and len(verified)==summary['uniqueBlobs']==661
entries=manifest['entries'];excluded=manifest['excludedRetainedBodies'];assert len(entries)==summary['logicalBodies']==737 and len(excluded)==summary['retainedExcludedBodies']==166
assert len({e['path'] for e in entries+excluded})==903 and set(verified)=={e['sha256'] for e in entries}
originalcache={}
for e in entries+excluded:
 logical=pathlib.PurePosixPath(e['path']);assert not logical.is_absolute() and all(x not in ['..','.',''] for x in logical.parts)
 path=pathlib.Path(e['originalPath']);assert path.is_absolute() and str(path).startswith('/workspace/') and path.is_file()
 if str(path) not in originalcache:originalcache[str(path)]=h(path)
 assert originalcache[str(path)]=={'sha256':e['sha256'],'bytes':e['bytes']}
 if e in entries:assert verified[e['sha256']]==e['bytes']
 else:assert 'retained at original path' in e['reason'] and 'not retired' in e['reason']
lookup={e['path']:e for e in entries+excluded};included={e['path'] for e in entries}
freeze=j(S/'ready-default-build-root-r1/RUNTIME-FREEZE.json');assert h(S/'ready-default-build-root-r1/RUNTIME-FREEZE.json')['sha256']=='950685b1857bf94d68fa965613576337eac44954d7e6f4ede4e11c55c1d93c91'
assert manifest['sourceDigest']==summary['sourceDigest']==freeze['sourceDigest']=='251c4fd4fdcce5bbbc39bf438155277ea440c724bd803adf10cd07b5ffa89a65' and manifest['outputsDigest']==summary['outputsDigest']==freeze['outputsDigest']=='2c664aa389221f8570e1f6cebd1ae63f0784d2cba95a7fcc267c3743096a823c'
runtime=[]
for kind,base,values in [('inputs',R,freeze['inputs']),('outputs',R/'dist',freeze['outputs'])]:
 assert len(values)==(87 if kind=='inputs' else 56)
 for rel,pin in values.items():
  logical='selected/'+kind+'/'+rel;assert logical in lookup and lookup[logical]['sha256']==pin
  body=h(base/rel);assert body['sha256']==pin and body['bytes']==lookup[logical]['bytes'];runtime.append({'kind':kind,'path':rel,**body})
assert h(R/'src/main.ts')['sha256']=='276999ac8c8feeb148d326b5adcfca7d175db99c743e5722501a34256fd54b9a'
oldroot=S/'ready-default-promotion-root-r1';old=j(oldroot/'R8-IDENTITIES.json');oldmain=read(oldroot/'original-main.ts');main=read(R/'src/main.ts');assert sha(oldmain)=='2027b1f73c804ab22bac0a949e26c34ea6bc9d9cd61f416f8e6072bec41d126d'
assert len(old['inputs'])==87 and len(old['outputs'])==56
for rel,pin in old['inputs'].items():assert h(oldroot/'original-main.ts' if rel=='src/main.ts' else R/rel)['sha256']==pin
oldout=[]
for rel,pin in old['outputs'].items():
 path=oldroot/'R8-OUTPUTS'/rel
 if not path.exists():path=R/'dist'/rel
 assert h(path)['sha256']==pin
 if str(path).startswith(str(oldroot/'R8-OUTPUTS')):oldout.append(rel)
assert len(oldout)==5
diff=list(difflib.unified_diff(oldmain.decode().splitlines(True),main.decode().splitlines(True),fromfile='R8',tofile='selectedREADY'))
added=[v for v in diff if v.startswith('+') and not v.startswith('+++')];removed=[v for v in diff if v.startswith('-') and not v.startswith('---')]
assert len(added)==11 and len(removed)==2 and sum(v.startswith('@@') for v in diff)==1
assert oldmain[:oldmain.index(b'  const playable = actions().filter')]==main[:main.index(b'  const available = actions();')]
assert oldmain[oldmain.index(b'  const hand = document.querySelector<HTMLElement>'):] == main[main.index(b'  const hand = document.querySelector<HTMLElement>'):]
cue_delta=''.join(diff);write('READY-DELTA.json',{'addedLines':len(added),'removedLines':len(removed),'onePresentationHunk':True,'diff':cue_delta,'rulesInputStateSaveTimersOutsideHunkByteExact':True})
required=['ready-coach-actual-technical-independent-r1','ready-coach-actual-gameplay-independent-r1','ready-coach-visual-independent-r1','ready-default-build-technical-independent-r1','ready-default-first300-technical-independent-r1','ready-default-first300-gameplay-independent-r1','ready-default-first300-visual-independent-r1','ready-default-promotion-and-settle-build-independent-r1','settle-drag-source-technical-independent-r1','settle-drag-caller-technical-independent-r1','settle-drag-caller-technical-independent-r2','settle-drag-actual-technical-independent-r1','settle-drag-actual-gameplay-independent-r1','settle-drag-actual-visual-independent-r1']
reviewpins=[]
for name in required:
 candidates=[e for e in entries if e['path'].startswith('packets/'+name+'/') and pathlib.PurePosixPath(e['path']).name in ['GATE.json','MANIFEST.json','REVIEW.md','PROOF.json']];assert candidates;reviewpins.extend(candidates)
assert lookup['packets/settle-drag-actual-technical-independent-r1/GATE.json']['sha256']=='93feab5a60593a6adcf771f1727cfed38d3f70816052ae7bd32a02a3df076b9e'
actual=S/'settle-drag-comparison-actual-r1';comparisons=[]
for scenario in ['rapid-release','hold-release','hold-cancel']:
 for label in ['C0','C1','C2','C-firstDrop','C-secondOutcome','C-normalized']:
  a=j(actual/('A-'+scenario+'-'+label+'-OPAQUE-SAVE.json'));b=j(actual/('B-'+scenario+'-'+label+'-OPAQUE-SAVE.json'));assert a['raw']==b['raw']
  for prefix in ['A','B']:assert 'packets/settle-drag-comparison-actual-r1/'+prefix+'-'+scenario+'-'+label+'-OPAQUE-SAVE.json' in included
  comparisons.append({'scenario':scenario,'label':label,'completeRawEqual':True,'rawSHA256':sha(a['raw'].encode())})
images=[e for e in entries if pathlib.PurePosixPath(e['path']).suffix.lower() in ['.jpg','.jpeg','.png','.webp']]
defaultimages=[e for e in images if '/ready-default-first300-actual-r1/' in e['path']];heldimages=[e for e in images if '/settle-drag-comparison-actual-r1/' in e['path']]
assert len(images)==8 and len(defaultimages)==6 and len(heldimages)==2 and all('-hold-release-' in e['path'] for e in heldimages)
guards=[]
for name,work,rc in [('guard-r1',128,1),('guard-r2',64,0)]:
 r=j(ROOT/name/'RESULT.json');ad=j(ROOT/name/'ADMISSION.json');assert ad['admitted'] and ad['work']==work*1048576 and ad['reserve']==512*1048576 and r['exit_code']==rc and r['failure'] is None and r['memory_events_before']==r['memory_events_after']
 pts=[r['initial']]+r['samples']+[r['final']];assert r['initial']['headroom']>=(work+512)*1048576 and r['initial']['free']>=64*1048576
 assert all(x['maximum']==r['initial']['maximum'] and x['headroom']>=512*1048576 and x['current']-r['initial']['current']<=work*1048576 and x['free']>=1048576 for x in pts)
 guards.append({'name':name,'points':len(pts),'workMiB':work,'reserveMiB':512,'exitCode':rc,'minimumHeadroom':min(x['headroom'] for x in pts),'maximumAggregateDelta':max(x['current']-r['initial']['current'] for x in pts),'result':h(ROOT/name/'RESULT.json'),'eventsUnchanged':True})
assert read(A/'ARCHIVE-CAP-FAILURE.json')==read(ROOT/'guard-r1/RESULT.json')
assert b"AssertionError: ('capsule size limit', 3303630)" in read(ROOT/'guard-r1/EXECUTION.log') and summary['declaredBudgetDeviation']['plannedCompressedCapBytes']==2621440 and summary['declaredBudgetDeviation']['originalGuardExit']==1
releasepins={'manifest.json':'0ac18130702c1b2d50831516d1119485c30ae275d42cb26bedb897fa368a5668','SHA256SUMS':'4c0c7c0c7dd68afab94d474e69eebcdfd66b792f27d2f9b93a6ce762dc2db01c','VERIFICATION.json':'206cf5ebfb8e5df00da8f91524c59709d02d1f5d49c0920f7f03cfe991591a37'}
for name,pin in releasepins.items():
 path=R/'releases/0.8.0'/name;assert h(path)['sha256']==pin
 gitbody=subprocess.check_output(['git','show','HEAD:releases/0.8.0/'+name],cwd=R,timeout=5);assert sha(gitbody)==pin
assert j(R/'releases/0.8.0/manifest.json')['version']=='0.8.0' and j(R/'package.json')['version']=='0.9.0'
readme=read(A/'README.md').decode();assert 'All18 full saved checkpoint pairs' in readme and '15-pair normalized subset' in readme and 'no benefit' in readme and 'not a new version or release' in readme
assert h(archive)==ap
hwm=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024;assert hwm<=24*1048576
proof={'decision':'ACCEPT_EXACT_BOUNDED_EVIDENCE_CAPSULE_WITH_DECLARED_FOOTPRINT_DEVIATION','archive':ap,'manifestSHA256':manifestpin,'logicalEntries':737,'uniqueBlobs':661,'excludedRetainedBodies':166,'fullArchiveRoundtrip':True,'originalAndExcludedBodies':{'totalLogicalBodies':903,'uniqueOriginalPaths':len(originalcache),'allBytesEqual':True,'fullLogicalMapUniqueAndSafe':True,'logicalMapDigest':sha(json.dumps(entries+excluded,sort_keys=True,separators=(',',':')).encode()),'verifiedBlobMapDigest':sha(json.dumps(verified,sort_keys=True,separators=(',',':')).encode()),'excludedBySuffix':dict(collections.Counter(pathlib.PurePosixPath(x['path']).suffix for x in excluded))},'selectedRuntime':{'sourceDigest':freeze['sourceDigest'],'outputsDigest':freeze['outputsDigest'],'sourceCount':87,'outputCount':56,'fullCurrentCanonicalBodiesVerified':True,'runtimeMapsDigest':sha(json.dumps(runtime,sort_keys=True,separators=(',',':')).encode()),'mainSHA256':sha(main),'presentationDeltaAdded11Removed2':True,'rollbackOriginalMainSHA256':sha(oldmain),'fullOld87Inputs56OutputsReconstructed':True,'fiveOldNonmediaBodies':oldout,'engineRulesInputStateSaveTimersByteExactOutsidePresentationHunk':True},'gatesPresent':reviewpins,'completeRaw18PairComparisons':comparisons,'callerAsserts15SubsetNot18':True,'includedOriginalPhotographs':images,'excludedBodyRetention':'Every166 excluded body remains byte exact at its declared original path and remains needed for unique art/rawphoto/reproduction/evidence. Exclusion is not retirement authorization. No decoded visual judgement here.','producerGuards':guards,'failureAndFootprint':'Original archive command rc1 after full3303630B complete write exceeds planned2621440 softcap by682190B. Failure artifact/receipt retained byte exact. Separate64+512 finite fullroundtrip0 accepted actual declared footprint; unchangedarchive, no re-encoding/runtime retry. This does not convert sizecapfailure into a test pass or authorize cleanup.','summaryReadmeClaims':'Matches soleREADY selection; privatequery showed no differential benefit, rapid no-ops preserved and causeunknown; first300 turn1 without response/clear;18 complete raw pairs versuscaller15 normalized subset verified; withheld art/trial, no humanfun/release/platform/selfcontained/OSreadonly/retirement claim.','releaseControlPins':releasepins,'releaseControlsEqualHEAD':True,'releaseScope':'Only three0.8 metadata/control bodies compared to exact HEAD blobs and retainedpins; no new tag/version/release inferred. Existing0.9 developmentpackage distinct. Historical multiGB release archive bodies were not rehashed here.','snapshotLimits':'Capsule is selected bounded evidence, not fullglobal scratch archival coverage or selfcontained playable release. Protectedmedia mounted under workflow holds, not OSenforcement. Independent gate copies preserve original findings/failures; not an approval of excluded art or allpast experiments.','toolsClosureScope':'Producer generic guards normal finitechild waits (archive rc1, verifyrc0), all sample/events inspected. No numericchild-startidentity ledger/globalbackend census; no exhaustive reviewer/backend actor attribution or unknownconsumer absence claim. Reviewer streamed archive/source bodies only, no extraction/runtime/build/Node/imageview/write; three finite Gitshow read-only subprocesses waited.','readMethod':'NOATIME|NOFOLLOW terminal retainedbody reads,32768B hashing/tarstream. JPEG/media bytes compared solely for preservation, no decode/view. FDs closed, NEWproof writes only. Producer ordinaryread atimequalifications remain.','reviewerCountAssumptionFailurePreserved':'Initial verifier GUARD rc1 before proof after fullarchive/current/rollback bodies passed: assumed13/4 line counts. Exact default main276999 versusR8main2027 has11 added/2 removed lines, one hunk. Original verifier/log retained; r2 adjusts only reviewer count/wording, no archive/source or runtime retry.', 'reviewerOwnHWM':hwm,'utcNs':time.time_ns()}
write('PROOF.json',proof)
with (P/'REVIEW.md').open('x') as out:out.write('Accept the exact evidence capsule with its explicitly declared3,303,630-byte retention footprint. Every661 archive blob roundtrips, all737 logical entries and166 excluded retained bodies match originals, and logical paths are unique. The failed2.5MiB softcap assertion remains a failure; the subsequent finite verification accepts the unchanged artifact, not the failed cap.\n\nAll current87/56 canonical bodies match selected READY source251c4f/output2c664a/main276999. Full R8 rollback87/56 bodies remain recoverable. Only the reviewed presentation hunk (11 added/2 removed lines) differs in main; rules/input/save/timers are unchanged. Independent positive and negative gates/failures are preserved. All18 complete drag checkpoint pairs match, while the caller asserts15 normalized pairs. Eight selected originals are included; other media remain needed at pinned retained paths. No images were decoded or judged.\n\nProducer128+512 failure and64+512 correction receipts pass sampled resources/events with finite closure. Generic receipts do not establish exhaustive child identities or global reviewer/backend attribution. The three0.8 release control bodies match retained hashes and HEAD; multiGB historical release archives were not reread. Development package0.9 is distinct from latest sealed0.8.\n\nThis accepts bounded evidence preservation, not a self-contained game release, drag improvement/repair, art quality, human enjoyment, promotion or retirement. No archive rewriting, source/media mutation, runtime, Node, build or image operation occurred.\n')
print(json.dumps({'decision':proof['decision'],'entries':737,'blobs':661,'excluded':166,'ownHWM':hwm,'proofSHA256':h(P/'PROOF.json')['sha256']}))
