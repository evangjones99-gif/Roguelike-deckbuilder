import os,json,hashlib,ast,base64,resource
from pathlib import Path
P=Path(__file__).parent;A=Path('/workspace/scratch/wording-development-source-selection-author-r1');R=Path('/workspace/Roguelike-deckbuilder');S=Path('/workspace/scratch');T=S/'opening-turn-payoff-wording-stage-r1'
resource.setrlimit(resource.RLIMIT_DATA,(24*1048576,24*1048576))
def read(p):
 fd=os.open(p,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW)
 with os.fdopen(fd,'rb') as f:return f.read()
def pin(p):
 fd=os.open(p,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW);h=hashlib.sha256();n=0
 with os.fdopen(fd,'rb') as f:
  for b in iter(lambda:f.read(32768),b''):h.update(b);n+=len(b)
 return {'path':str(p),'bytes':n,'sha256':h.hexdigest()}
j=lambda p:json.loads(read(p));sha=lambda b:hashlib.sha256(b).hexdigest()
pins=[pin(p) for p in sorted(A.rglob('*')) if p.is_file()];by={Path(x['path']).relative_to(A).as_posix():x for x in pins}
for k,h in {'select-development-source.py':'9c3c231b71c03ce23b5515f2cca5dcc3b341af418216000bc1edab0dc2a3b788','PLAN.json':'82604ccb107cecf084c5823044659e7c66994a4b1797e8a741cedf493acb315f','MANIFEST.json':'94f29aee55e4e331ee8a542788de1178086743df9eb2a6d0d0515f8a1025c800','CLOSURE.json':'281b80198499e72ac797c7760b5cb7e85e5bddb23ef2416fff6fb1890f9303ee','FINAL-SEAL.json':'919d5e8241c55e266002d15c4701eacc35fb83ddb2c688a3f563862733901c7c'}.items():assert by[k]['sha256']==h
for row in j(A/'MANIFEST.json')['files']:assert pin(Path(row['path']))==row
plan=j(A/'PLAN.json');method=read(A/'select-development-source.py').decode();tree=ast.parse(method);compile(tree,'<source grammar only>','exec')
successor=j(A/'METHOD-SUCCESSOR.json');prior=method
for line in successor['addedLines']:assert prior.count(line)==1;prior=prior.replace(line,'')
assert prior.encode()==read(A/'method-before-hold-binding.py') and sha(prior.encode())==successor['beforeMethodSHA256']
oldf=S/'target-clear-default-build-author-r1/RUNTIME-FREEZE.json';newf=S/'opening-turn-payoff-wording-strict-build-root-r1/final-seal-r1/RUNTIME-FREEZE.json'
assert pin(oldf)['sha256']=='739f5e87f95f2ca2ad4e60f7b90ea00aa6384d74c1ae2fc8a4e60266e705ce62'
assert pin(newf)['sha256']=='d6c225d5408c8e60433aed54655e922a44af224621fc8c48cb6aca8cd3c5883a'
old=j(oldf);new=j(newf)
assert len(old['inputs'])==88 and len(new['inputs'])==89 and len(old['outputs'])==len(new['outputs'])==56
agg=lambda m:sha(json.dumps(m,sort_keys=True,separators=(',',':')).encode())
for f in (old,new):assert agg(f['inputs'])==f['sourceDigest'] and agg(f['outputs'])==f['outputsDigest']
assert old['sourceDigest']==plan['scope']['sourceBefore'] and new['sourceDigest']==plan['scope']['sourceAfter']
assert old['outputsDigest']==plan['scope']['canonicalDistRetained'] and new['outputsDigest']==plan['scope']['candidateBuildReferenceOnly']
delta={k:[old['inputs'].get(k),new['inputs'].get(k)] for k in set(old['inputs'])|set(new['inputs']) if old['inputs'].get(k)!=new['inputs'].get(k)}
assert delta==plan['scope']['exactInputDelta']
before=read(R/'src/main.ts');after=read(T/'src/main.ts');css=read(T/'src/opening-turn-payoff.css');inverse=j(A/'MAIN-INVERSE.json')
assert sha(before)==inverse['beforeSHA256']==old['inputs']['src/main.ts']
assert sha(after)==inverse['afterSHA256']==new['inputs']['src/main.ts']
assert len(css)==163 and sha(css)==new['inputs']['src/opening-turn-payoff.css']
assert not (R/'src/opening-turn-payoff.css').exists() and not (R/'src/opening-turn-payoff.css').is_symlink()
forward=bytearray();cursor=0;offset=0;reverse=[]
for row in inverse['patches']:
 start,end=row['oldByteStart'],row['oldByteEnd'];a=base64.b64decode(row['oldBase64']);b=base64.b64decode(row['newBase64']);assert start>=cursor and before[start:end]==a
 forward+=before[cursor:start];offset+=start-cursor;reverse.append((offset,offset+len(b),a));forward+=b;offset+=len(b);cursor=end
forward+=before[cursor:];assert bytes(forward)==after
back=bytearray();cursor=0
for start,end,a in reverse:back+=after[cursor:start];back+=a;cursor=end
back+=after[cursor:];assert bytes(back)==before
current_src={p.relative_to(R).as_posix() for p in (R/'src').rglob('*') if p.is_file()}
mapped_src={p for p in old['inputs'] if p.startswith('src/')};assert current_src==mapped_src
held=read(R/'AGENTS.md');marker=b'## Frozen grounded-courtyard pixel and wording successors\n';assert marker in held
assert sha(held[held.index(marker):])=='19e35b29256309ef3fbded5d57ae4e3a582b07dfd0e18f7e8497341e0fe3378e'
gates=[]
for row in plan['actualReviewGates']:
 assert pin(Path(row['path']))['sha256']==row['sha256'];assert j(Path(row['path']))['decision']==row['decision'];gates.append(row)
complete=S/'wording-grounded-trials-checkpoint-complete-independent-r1/GATE.json';assert pin(complete)['sha256']=='df8ef40e5409409f004d2a2c08d7ca20dfb519f31590c379459c29d2f6983a85';assert j(complete)['decision'].startswith('ACCEPT')
checkpoint=Path(plan['checkpointSourcePlan']['path']);assert pin(checkpoint)['sha256']==plan['checkpointSourcePlan']['sha256'];cp=j(checkpoint)
assert any(Path(cp['roots'][r[0]])/r[1]==R/'src/main.ts' and r[2]==sha(before) for r in cp['rows'])
# Review AST/source without importing or executing the selection helper.
assert not any(isinstance(n,(ast.Import,ast.ImportFrom)) and any(a.name.split('.')[0] in ('subprocess','shutil') for a in n.names) for n in ast.walk(tree))
assert not any(isinstance(n,ast.Attribute) and n.attr in ('unlink','remove','rmtree','chmod','utime','setxattr','system') for n in ast.walk(tree))
assert method.count('os.replace(')==2
for text in ["if not __debug__:","grant['soleCanonicalWriterConfirmed'] is True","grant['noDevServerOrOtherCanonicalSourceWriterConfirmed'] is True","grant['canonicalPaths']==['src/main.ts','src/opening-turn-payoff.css']","grant['methodSHA256']==digest(__file__)[0]","independent['decision'].startswith('ACCEPT')","preservation['RootVerifiedCompleteScopeAndSourcePlan'] is True","digest(preservation['archive']['path'])[0]==preservation['archive']['sha256']","grant['confirmedPush']['RootVerifiedCurrentCleanAndPushed'] is True","os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW","write_new(out/'OLD-main.ts',old_bytes)","write_new(css,css_bytes,0o644)","fullmeta(main)==owned and digest(main)[0]==new['inputs']['src/main.ts']","if ours():os.replace(restore,main)","'fullOld88SourceSetRestored':False","'canonicalDistNowMatchesNewSource':False"]:assert text in method,text
assert method.index("for rel,h in new['outputs'].items()")<method.index('out.mkdir(')
assert method.index("write_new(out/'OLD-main.ts',old_bytes)")<method.index('write_new(temporary,candidate')<method.index('write_new(css,css_bytes')<method.index('os.replace(temporary,main)')
assert method.index('written=True')<method.index('owned=now')
guards={}
for p in sorted(A.glob('*GUARD/RESULT.json')):
 r=j(p);assert r['exit_code']==0 and r['failure'] is None and r['memory_events_before']==r['memory_events_after'];guards[str(p)]={'pin':pin(p),'rows':len(r['samples']),'exit_code':r['exit_code']}
rss={l.split(':')[0]:int(l.split()[1])*1024 for l in Path('/proc/self/status').read_text().splitlines() if l.startswith(('VmRSS:','VmHWM:'))};assert max(rss.values())<24*1048576
out={'decision':'ACCEPT_EXACT_TWO_FILE_WORDING_DEVELOPMENT_SOURCE_SELECTION_METHOD','developmentSourceSelectionMethodEligible':True,'method':pin(A/'select-development-source.py'),'methodPlan':pin(A/'PLAN.json'),'authorManifest':pin(A/'MANIFEST.json'),'fullAuthorBodyPins':pins,'exactFourLineMethodSuccessorInverse':True,'exactFourMainBytePatchForwardAndInverse':True,'currentCanonicalMain':pin(R/'src/main.ts'),'candidateMain':pin(T/'src/main.ts'),'newCSS':pin(T/'src/opening-turn-payoff.css'),'canonicalCSSCurrentlyAbsent':True,'currentSrcFileMembershipEqualsOldMappedSrcMembership':True,'mapReferences':{'old':pin(oldf),'new':pin(newf),'fullInputDelta':delta,'oldInputCount':88,'newInputCount':89,'oldOutputCount':56,'newOutputCount':56,'aggregateDigestsRecalculated':True},'actualReviewGates':gates,'completePreservationGateReference':pin(complete),'checkpointSourcePlan':pin(checkpoint),'currentHold':pin(R/'AGENTS.md'),'holdSuffixExact':True,'authorGuards':guards,'ownRSSBytes':rss,'sourceAssessment':['Only canonical main replacement and exclusive new163B CSS are permitted writes; source parents must be real directories, existing main a regular file. Existing dist/media/engine/tests/frozen stages receive read/hash operations only.','Full old literal is durably retained before source changes, with exact old-main archive logical reference. Fresh main temporary inode avoids writes through old aliases. New CSS O_EXCL never overwrites an existing path.','Two-file transaction is an observed durable prefix, not jointly atomic. On failure CSS/temporaries/receipts remain and restoring old main alone is explicitly not old88 restoration.','Recovery only restores current main if exact own inode/non-atime metadata/xattrs and candidate hash match twice. Original main inode/time metadata is surrendered; recovery may fail, and user changes are preserved by observed checks plus sole-writer contract.','All frozen old88/new89 and old56/new56 maps are hash-checked by the future method. Current source membership matches old mapped src inventory in this review. Method itself checks mapped bodies; Root fresh clean/current identity and sole-writer confirmation remain required.','Actual3 reviewed narrow gates, exact method/sourceplan/hold and independent COMPLETE archive/INDEX references must be pinned by the future Root grant before outputs. COMPLETE gate-to-archive/scope relationship and current Git cleanliness/head are expressly external Root confirmations, not helper Git verification.','Internal512KiB output/24MiB RSS/60s and initial64MiB+512KiB disk are sampled phase limits; outer64+512 guard required. Initial resource preflight happens before out.mkdir; durable prefix/terminal stdout measurement qualifications retained.'],'limitations':['This review executes no selection helper, Git, build, native browser, server or pixel/media decode. Existing full-body maps/admissibility rely on prior audits and method-source inspection; no redundant media/archive replay.','Known COMPLETE gate pinned; its archive/INDEX not freshly streamed by this source review. Future exact Root activation must bind that completed preservation scope.','Canonical development source after selection is64c2; preview/desktop dist stays old8b. No matching new canonical compiled runtime or release/version/tag claim.','Prior cue authorship disclosed: engineering selection-method review only, no independent own-cue fun/gameplay/visual judgment.','Not OS-enforced holds, CAS, universal writer exclusion, power-loss joint atomicity or unconditional rollback.','Bootstrap and final sealing outside sampled guard; shared cgroup accounting is not exclusive attribution.']}
(P/'PROOF.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'decision':out['decision'],'authorBodies':len(pins),'RSS':rss,'proofBytes':(P/'PROOF.json').stat().st_size}))
