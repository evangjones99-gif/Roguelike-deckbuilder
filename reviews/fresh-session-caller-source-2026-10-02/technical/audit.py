import ast,gzip,hashlib,json,pathlib,subprocess,time,os
P=pathlib.Path('/workspace/scratch/starter-caller-resume-source-r2')
O=pathlib.Path('/workspace/scratch/caller-technical-review-resume-r1')
def h(b):return hashlib.sha256(b).hexdigest()
def read(p):
 p=pathlib.Path(p);assert p.is_file() and not p.is_symlink();return p.read_bytes()
sealbody=read(P/'SOURCE-SEAL.json');assert h(sealbody)=='4cdd96a6a5c173e0a4558d93d7b4f37adbfc2448abfd8ad08e2dcb63bddfabc1'
seal=json.loads(sealbody);m=json.loads(read(P/'MANIFEST.json'));assert h(read(P/'MANIFEST.json'))=='b8c74ac46a40b66d6cd7a296c91686700e1927dfc9ea055f3b5aa74936c304bc'
actual={p.name for p in P.iterdir()};assert actual=={r['name'] for r in seal['files']}|{'SOURCE-SEAL.json'}
for r in seal['files']:
 b=read(P/r['name']);assert len(b)==r['bytes'] and h(b)==r['sha256'],r['name']
family=sum(p.stat().st_size for p in P.iterdir());assert family==seal['familyBytesIncludingSeal']==162468 and family<=163840
external=[]
for group in [m['R1External'],m['historicalRuntimeEvidence']]:
 for r in group['files']:
  b=read(pathlib.Path(group['recoveredRoot'])/r['name']);assert len(b)==r['bytes'] and h(b)==r['sha256'];external.append(r)
v=json.loads(gzip.decompress(read(P/'R2-INVERSE.json.gz')));roundtrips=[]
def transform(body,hunks,side):
 lines=body.splitlines(keepends=True);out=[];cursor=0
 for q in hunks:
  start=q[side+'LineStart'];a=q[side].splitlines(keepends=True);z=q['after' if side=='before' else 'before'];assert start>=cursor;assert ''.join(lines[start:start+len(a)])==q[side];out.append(''.join(lines[cursor:start]));out.append(z);cursor=start+len(a)
 out.append(''.join(lines[cursor:]));return ''.join(out)
for r in v['files']:
 before=read(pathlib.Path(v['originRoot'])/r['originName']);after=read(P/r['newName']);assert len(before)==r['beforeBytes'] and len(after)==r['afterBytes'];assert h(before)==r['beforeSHA256'] and h(after)==r['afterSHA256'];assert transform(before.decode(),r['hunks'],'before').encode()==after;assert transform(after.decode(),r['hunks'],'after').encode()==before;roundtrips.append({'name':r['newName'],'forward':True,'inverse':True,'hunks':len(r['hunks'])})
prior=json.loads(gzip.decompress(read(P/'INVERSE.json.gz')));d=read(pathlib.Path(v['originRoot'])/'driver-opening-r1.mjs').decode()
for q in reversed(prior['driverLiteralDeltas']):assert d.count(q['after'])==q['count'];d=d.replace(q['after'],q['before'])
assert h(d.encode())==prior['donorDriverSHA256']
s=read(pathlib.Path(v['originRoot'])/'supervise-opening-r1.py').decode().replace(m['R1External']['historicalRoot']+'/driver-opening-r1.mjs','/workspace/scratch/native128-empty-intent-caller-source-author-r2/driver-paired-r2.mjs');assert h(s.encode())==prior['donorSupervisorSHA256']
e=json.loads(read(P/'EXPECTED-CANDIDATE.json'));old=json.loads(read(pathlib.Path(v['originRoot'])/'EXPECTED-CANDIDATE.json'));a,b=e['runtimes'];g=json.loads(read(P/'starter-build-GATE.json'))
assert e['sealed'] is False and e['runtimeEligible'] is False and e['runtimeRecovery']['complete'] is False
assert a['nativeAssets']==old['runtimes'][0]['nativeAssets'] and len(a['nativeAssets'])==7 and len(b['nativeAssets'])==13
assert b['buildGateSHA256']==h(read(P/'starter-build-GATE.json'))=='2f4f3ef63b325bcbe08a151cf7f0432831afac0d820abaa785c2457fe59f4c12'
for k in ['stage','sourceDigest','outputsDigest','inputCount','outputCount']:assert b[k]==g[k]
assert b['freezeSHA256']==g['freezeSHA256'] and b['aliasPolicySHA256']==g['aliasCatalogueSHA256'] and b['aliasCount']==g['actualAliasCount'];assert b['buildGateDecision']==g['decision']
caps=['captureCap','perContextCaptureCap','captureFormat','captureQuality','estimatedCaptureBytes','estimatedProofBytes','minimumPostCaptureReviewFreeBytes','pointerEventCap','pointerEventByteCap','rawSaveByteCap','driverSeconds','supervisorWholeSeconds','pixelEventCap','pixelEventByteCap','geometryNeighborCap','geometryGhostCap','geometryActorCap','geometryControlCap'];assert all(e[k]==old[k] for k in caps)
driver=read(P/'driver-opening-r2.mjs').decode();supervisor=read(P/'supervise-opening-r2.py').decode()
assert driver.index('assert(expected.sealed===true')<driver.index("await import(")<driver.index('fs.writeFileSync(')
assert supervisor.index("if expected.get('sealed')")<supervisor.index('stage,freeze,packet,port=sys.argv')<supervisor.index('p.mkdir(')<supervisor.index('subprocess.Popen(')
start=time.monotonic();n=subprocess.run(['node','--check',str(P/'driver-opening-r2.mjs')],capture_output=True,text=True,timeout=15);assert n.returncode==0
tree=ast.parse(supervisor,filename=str(P/'supervise-opening-r2.py'));compile(tree,str(P/'supervise-opening-r2.py'),'exec')
receipt={'sourceOnly':True,'callerExecuted':False,'allSealFileHashesVerified':True,'inclusiveFamilyBytes':family,'capBytes':163840,'externalBodyPinsVerified':len(external),'threeBodyR2ForwardInverse':roundtrips,'priorDriverSupervisorInverseVerified':True,'priorExpectedDonorBytesAvailable':False,'exactBActualGateBound':True,'baselineSevenAssetsCorrect':True,'runtimeCapsUnchanged':True,'failClosedStaticOrderingVerified':True,'nodeCheck':{'exitCode':n.returncode,'stdout':n.stdout,'stderr':n.stderr},'pythonASTCompile':True,'grammarWholeSeconds':time.monotonic()-start,'noBrowserBuildMediaAcquired':True}
(O/'PROOF.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
