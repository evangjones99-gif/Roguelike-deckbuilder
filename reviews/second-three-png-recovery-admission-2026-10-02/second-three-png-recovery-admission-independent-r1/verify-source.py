import pathlib,os,json,hashlib,resource,difflib,ast,time
p=pathlib.Path(__file__).parent;s=pathlib.Path('/workspace/scratch')
def read(path):
 fd=os.open(path,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW)
 with os.fdopen(fd,'rb') as f:return f.read()
def rec(path):
 b=read(path);return {'path':str(path),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
guard=s/'guard-source-recovery-56m-root-r2.py';proposal=s/'bounded-source-recovery-admission-proposal-root-r2.json';r3=s/'share-second-three-retained-pngs-root-r3.py';r2=s/'share-second-three-retained-pngs-root-r2.py';ordinary=s/'guard-node-phase-r1.py'
assert rec(guard)['sha256']=='c2b24f58d6abbbe0449fc49515e6bb9eeaf0997bd287642d87a3a1754388fff3'
assert rec(r3)['sha256']=='af73daa64cb87e5595d2e1f6d6742baa611bc472a114b381832eaf0de55adf74'
assert rec(r2)['sha256']=='3ac77cbd683f43b00910066dc8248d6a77e2576df9111f30c856558555e62d99'
g=read(guard).decode();o=read(ordinary).decode();a=read(r3).decode();b=read(r2).decode()
assert a.replace('initial_free>=56*1048576','initial_free>=64*1048576').replace('second-r3.tmp','second-r2.tmp').replace('actual-root-r3','actual-root-r2')==b
extra="assert stage=='/workspace/Roguelike-deckbuilder'\nassert int(work_mb) in (64,256)\nassert len(command)>=2 and command[0]=='python' and command[1].startswith('/workspace/scratch/')\nassert not any(term in command[1] for term in ['build','native','browser','release','image'])\n"
assert g.replace(extra,'').replace("initial['free']>=56*1048576","initial['free']>=64*1048576")==o
ast.parse(g);ast.parse(a)
body=json.loads(read(proposal));assert body['guardSHA256']==rec(guard)['sha256'] and body['methodSHA256']==rec(r3)['sha256']
oldgate=s/'second-three-retained-png-sharing-before-independent-r2/GATE.json';assert rec(oldgate)['sha256']=='d12f5667c1eb28a0d0153c63a98318e1e9ab104e433139e2f8083fac8cf24b2a'
hold=pathlib.Path('/workspace/Roguelike-deckbuilder/AGENTS.md');assert rec(hold)['sha256']=='69a82ce96a594a2b2a5244154de8758b200290ba9de46b40a221a52ba4a0cfb7'
refusal=s/'second-three-png-judgment-guard-root-r1/ADMISSION.json';ref=json.loads(read(refusal));assert ref['admitted'] is False and ref['initial']['free']<64*1048576
bootstrap=[]
for name in ['guard-source-recovery-56m-root-r1.py','bounded-source-recovery-admission-proposal-root-r1.json']:
 path=s/name
 if path.exists():bootstrap.append(rec(path))
guarddiff='\n'.join(difflib.unified_diff(o.splitlines(),g.splitlines(),fromfile=str(ordinary),tofile=str(guard)))+'\n'
methoddiff='\n'.join(difflib.unified_diff(b.splitlines(),a.splitlines(),fromfile=str(r2),tofile=str(r3)))+'\n'
(p/'GUARD-DELTA.patch').write_text(guarddiff);(p/'METHOD-R2-R3-DELTA.patch').write_text(methoddiff)
budget={'preactionPublicationUpperBytes':512*1024,'independentProofUpperBytes':192*1024,'transactionControlUpperBytes':64*1024,'combinedUpperBytes':(512+192+64)*1024,'admissionBytes':56*1048576,'quotedFreeBytes':66203648,'quotedFreeAfterCombinedUpperBytes':66203648-(512+192+64)*1024,'minimumAdmissionAfterCombinedUpperBytes':56*1048576-(512+192+64)*1024,'prospectiveGrossReleasedBytes':8499200,'oldInodeBackupOrMediaCopyBytes':0}
assert budget['combinedUpperBytes']<1048576 and budget['quotedFreeAfterCombinedUpperBytes']>56*1048576
rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss;assert rss<24*1024
proof={'guard':rec(guard),'proposal':rec(proposal),'methodR3':rec(r3),'priorMethodR2':rec(r2),'priorAcceptedGate':rec(oldgate),'currentHold':rec(hold),'ordinaryGuard':rec(ordinary),'guardExactDelta':'Four scope asserts plus disk64to56; all work/reserve/live1MiB/heap256 stops/lifecycle bytes exact','methodExactDelta':'Only diskpreflight64to56 and fresh root-r3/temp-r3 identifiers; all identity/body/currentpush/producer/journal/FD checks byteexact','old64Refusal':rec(refusal),'old64RefusalBeforeBodyExecuted':True,'bootstrapDraftsPreserved':bootstrap,'bootstrapQualification':'TwoRoot finite unguarded bootstrapdrafts andthisreview initialtiny read have no cgroupguard compliance certification. No draft executed as transaction or build.','wrapperScopeLimit':'Only filename/prefix filter; NOT exactscript allowlist or enforcement of body/child workload. Positive approval must externally bind exactreviewed invocation/pins; arbitrary scratchPython/unreviewedpublication scripts notcovered.','budget':budget,'budgetQualification':'Bounds are explicit scope obligations, not automatically enforced by genericfilename guard. Reviewproof has192KiB ownassertion; exactsharing writes only bounded3pair BEFORE/journal/RESULT anddirentries, no media copies/backups. Git/publication canexceed estimate unless producer uses boundedreviewed scope/freshadmission; method itself rechecks56 initialdisk beforeaction.','strictBuildAdmissionMiB':64,'nativeAdmissionMiB':70,'workAllowancesMiB':[64,256],'reserveMiB':512,'liveDiskStopMiB':1,'producerAndNewCurrentPush':'Stillrequired beforeANYaction; earlier9ce3push predatesr3/reviewpublication, not sufficient fornewaction. No Git inspected byreviewer.','noMediaOrActionPerformed':True,'ownRSSKiB':rss,'ownSourceResourceScope':'Exactbounded verify-source.py invocation only, new56 sourceguard work64+512 unchangedreserve; initialbootstrap read unmetered separate. Sharedsampled delta notexclusive attribution.','utcNs':time.time_ns()}
(p/'PROOF.json').write_text(json.dumps(proof,indent=2)+'\n')
total=sum(x.stat().st_size for x in p.rglob('*') if x.is_file());assert total<=192*1024
print(json.dumps({'guard':proof['guard'],'methodR3':proof['methodR3'],'budget':budget,'ownRSSKiB':rss,'packetBytes':total,'scope':'boundedsource only; no action/Git/media'}))
