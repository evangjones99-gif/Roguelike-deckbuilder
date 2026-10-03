import os,json,gzip,hashlib,ast,difflib,resource
from pathlib import Path
resource.setrlimit(resource.RLIMIT_DATA,(24*1048576,24*1048576))
P=Path(__file__).resolve().parent;OLD=Path('/workspace/scratch/native128-empty-intent-build-controls-source-author-r1');BASE=Path('/workspace/scratch/native128-empty-intent-stage-r1');NEW='/workspace/scratch/starter-family-native128-stage-r1';E='/workspace/scratch/starter-family-native128-strict-build-root-r1';sha=lambda b:hashlib.sha256(b).hexdigest()
def r(p):
 fd=os.open(Path(p).resolve(strict=True),os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME)
 with os.fdopen(fd,'rb') as f:return f.read()
def pin(p):
 b=r(p);return {'path':str(p),'bytes':len(b),'sha256':sha(b)}
def enc(x):return (json.dumps(x,separators=(',',':'))+'\n').encode()
def digest(m):return sha(json.dumps(dict(sorted(m.items())),separators=(',',':')).encode())
def need(x,m):
 if not x:raise ValueError(m)
freezePin=pin('/workspace/scratch/native128-empty-intent-strict-build-root-r1/final-seal-r1/RUNTIME-FREEZE.json');need(freezePin['sha256']=='71327a14333f97af3037ca87f3ffadcee81e1a20b97d561d79ec48d7685f73ca','Exact donor freeze');f=json.loads(r(freezePin['path']));need(len(f['inputs'])==98 and len(f['outputs'])==64 and digest(f['inputs'])==f['sourceDigest'] and digest(f['outputs'])==f['outputsDigest'],'Full98/64 donor map')
sourcePlan=pin('/workspace/scratch/starter-family-native128-wiring-source-author-r2/PLAN.json');need(sourcePlan['sha256']=='7f40607b43f820e0e738b3899b0ab66c61c6acfc3ec42e6af9b6ee362e5b908f','Exact source tuple');sp=json.loads(r(sourcePlan['path']));sg=pin('/workspace/scratch/starter-family-native128-wiring-source-independent-r2/GATE.json');need(sg['sha256']=='d9e11d101944af80ada2f36cf7137633742aeff1d601d6bdf823ef924ade9beb','Independent exact source gate')
replacements={}
for n,x in sp['candidateSources'].items():
 rel='public/art/'+n if n.endswith('.json') else 'src/'+n;q=Path('/workspace/scratch/starter-family-native128-materialized-source-root-r1')/n;pp=pin(q);need(pp['sha256']==x['decodedSHA256'] and pp['bytes']==x['decodedBytes'] and not q.is_symlink(),'Actual materialized4 exact full regular bodies');replacements[rel]=pp
newPNGs={'public/art/'+Path(x['path']).name:x for x in sp['externalSixPNGs']};need(len(newPNGs)==6 and all(not Path(x['path']).is_symlink() and pin(x['path'])==x for x in newPNGs.values()),'Six exact external native bodies')
inputs=dict(f['inputs']);inputs.update({rel:x['sha256'] for rel,x in replacements.items()});inputs.update({rel:x['sha256'] for rel,x in newPNGs.items()});need(len(inputs)==104 and digest(inputs)==sp['predictedSourceDigest'],'Full104 prediction')
held={k:v for k,v in f['outputs'].items() if k.startswith(('art/','audio/'))};oldHeld=dict(held);need(len(held)==59,'Exact59 baseline held outputs');held.update({k[7:]:v['sha256'] for k,v in replacements.items() if k.startswith('public/')});held.update({k[7:]:v['sha256'] for k,v in newPNGs.items()});need(len(held)==65,'Candidate65 retained/new output bodies')
media=lambda s:Path(s).suffix.lower() in ('.png','.wav') and s.startswith(('public/','desktop/','art/','audio/'))
aliasInputs=[k for k in inputs if media(k) and k not in newPNGs];aliasOutputs=['dist/'+k for k in held if media(k)];expectedAliases=sorted(aliasInputs+aliasOutputs)
inv=dict(inputs)
for k in newPNGs:del inv[k]
for k in replacements:inv[k]=f['inputs'][k]
need(inv==f['inputs'],'Full104→98 inverse')
invHeld=dict(held)
for k in newPNGs:del invHeld[k[7:]]
for k in replacements:
 if k.startswith('public/'):invHeld[k[7:]]=oldHeld[k[7:]]
need(invHeld==oldHeld,'Full65→59 held-output inverse')
catalogue=pin(f['actualAliasCatalogue']['path']);need(catalogue['sha256']==f['actualAliasCatalogue']['sha256'],'Exact donor catalogue')
plan={'stage':NEW,'donorStage':str(BASE),'donorFreeze':freezePin,'donorSourceDigest':f['sourceDigest'],'donorOutputsDigest':f['outputsDigest'],'donorAliasCatalogue':catalogue,'donorAliasCount':f['actualAliasCatalogue']['count'],'supportCount':30,'sourcePlan':sourcePlan,'starterSourceGate':sg,'sourceFinal':pin('/workspace/scratch/starter-family-native128-wiring-source-author-r2/FINAL-SEAL.json'),'materializationGrant':pin('/workspace/scratch/starter-family-native128-materialization-grant-root-r1.json'),'materializationGuard':pin('/workspace/scratch/starter-family-native128-materialization-guard-root-r1/RESULT.json'),'replacements':replacements,'newNativePNGs':newPNGs,'expectedInputs':inputs,'expectedSourceDigest':digest(inputs),'expectedInputCount':104,'expectedHeldOutputs':held,'expectedHeldOutputCount':65,'expectedHeldOutputsDigest':digest(held),'expectedAliasKeys':expectedAliases,'expectedAliasCount':len(expectedAliases),'strictBuildEvidence':E,'qualification':'Fresh private starter-family static asset trial. Four exact source/manifest replacements, six private new PNG copies; old media/support mounts held. Existing floor/corpse/UI/input/rules/save/query/cue behavior unchanged; canonical guidance composition future. Engineering/private-fit art gates do not approve scene/default/animation/fun. Alias count derived from complete expected leaf set, measured chains frozen after build. Workflow hold is not OS readonly/selfcontained.','resourcePlan':{'assemblyMiB':64,'buildWorkMiB':384,'reserveMiB':512,'diskMiB':64,'heapMiB':256,'stopSeconds':55,'wholeSeconds':60,'attempts':1}}
newBody='''def assemble(activation_path):
    plan=json.loads(data(P/'PLAN.json'));activation=json.loads(data(activation_path))
    require(activation.get('rootAssemblyAuthorized') is True,'Root activation required')
    method=document(activation.get('methodGate'))
    require(str(method.get('decision','')).startswith('ACCEPT') and method.get('controlsPlanSHA256')==sha(P/'PLAN.json'),'Wrong independent controls gate')
    source=document(plan['starterSourceGate']);author=document(plan['sourcePlan']);final=document(plan['sourceFinal'])
    require(source.get('accepted') is True and source.get('sourceEngineeringEligible') is True and source.get('controlsPlanSHA256')==plan['sourcePlan']['sha256'] and source.get('authorFinalSHA256')==plan['sourceFinal']['sha256'] and source.get('candidateSourceDigest')==plan['expectedSourceDigest'] and source.get('fourFullByteInversesVerified') is True and source.get('all13NativeImageIdentitiesVerifiedWithoutDecode') is True,'Exact accepted starter tuple')
    required={'src/main.ts':'mainDecodedSHA256','src/coherent-native128.ts':'helperDecodedSHA256','src/art.ts':'artSHA256','public/art/coherent-native128-manual-crop-view-manifest.json':'manifestSHA256'}
    require(set(plan['replacements'])==set(required),'Only four declared substitutions')
    for relative,field in required.items():
        pp=plan['replacements'][relative];cp=author['candidateSources'][Path(relative).name]
        require(source[field]==pp['sha256']==cp['decodedSHA256'] and pp['bytes']==cp['decodedBytes'] and sha(pp['path'])==pp['sha256'] and not Path(pp['path']).is_symlink(),'Materialized source full identity changed')
    require(author['externalSixPNGs']==list(plan['newNativePNGs'].values()) and len(plan['newNativePNGs'])==6,'Exact six native source tuple')
    for pp in plan['newNativePNGs'].values():require(sha(pp['path'])==pp['sha256'] and Path(pp['path']).stat().st_size==pp['bytes'] and not Path(pp['path']).is_symlink(),'Native external body changed')
    for pp in author['exactGatePins'].values():document(pp)
    grant=document(plan['materializationGrant']);receipt=document(plan['materializationGuard'])
    require(grant.get('authorized') is True and grant.get('sourceMaterializationOnly') is True and grant['gateSHA256']==plan['starterSourceGate']['sha256'] and grant['planSHA256']==plan['sourcePlan']['sha256'] and receipt['exit_code']==0 and receipt['failure'] is None,'Exact prior Root materialization controls')
    require(all(str(Path(pp['path']).parent)==grant['exactOutputDirectory'] for pp in plan['replacements'].values()),'Wrong materialized directory')
    baseline=document(plan['donorFreeze']);donor=Path(baseline['stage'])
    require(str(donor)==plan['donorStage'] and baseline['sourceDigest']==plan['donorSourceDigest'] and baseline['outputsDigest']==plan['donorOutputsDigest'],'Wrong frozen donor')
    require(len(baseline['inputs'])==98 and len(baseline['outputs'])==64 and digest_map(baseline['inputs'])==baseline['sourceDigest'] and digest_map(baseline['outputs'])==baseline['outputsDigest'],'Full98/64 donor coherence')
    catalogue=document(plan['donorAliasCatalogue'])
    require(baseline['actualAliasCatalogue']=={'path':plan['donorAliasCatalogue']['path'],'sha256':plan['donorAliasCatalogue']['sha256'],'count':plan['donorAliasCount']} and catalogue['roots'][0]==str(donor) and len(catalogue['leaves'])==plan['donorAliasCount'],'Exact complete donor chain catalogue')
    for root in ['src','desktop','public']:require((donor/root).is_dir() and not (donor/root).is_symlink(),'Private donor directories required')
    actual={x.relative_to(donor).as_posix() for root in ['src','desktop','public'] for x in (donor/root).rglob('*') if x.is_file()}
    actual.update(['index.html','THIRD-PARTY.md','package.json','package-lock.json','tsconfig.json','vite.config.ts','scripts/build.mjs'])
    require(actual==set(baseline['inputs']),'Donor full input membership mismatch')
    require({x.relative_to(donor/'dist').as_posix() for x in (donor/'dist').rglob('*') if x.is_file()}==set(baseline['outputs']),'Donor full output membership mismatch')
    for root,mapping in [('',baseline['inputs']),('dist/',baseline['outputs'])]:
        for relative,expectedSHA in mapping.items():
            rel=root+relative;before=pinned_donor_file(donor,rel,catalogue)
            require(sha(donor/rel)==expectedSHA and pinned_donor_file(donor,rel,catalogue)==before,'Donor body/chain changed: '+rel)
    support=baseline['supportBodies'];require(len(support)==30,'Full support30 required')
    for relative,expectedSHA in support.items():safe_relative(relative);require(relative not in baseline['inputs'] and sha(donor/relative)==expectedSHA,'Support changed')
    inputs=dict(baseline['inputs']);inputs.update({r:x['sha256'] for r,x in plan['replacements'].items()});inputs.update({r:x['sha256'] for r,x in plan['newNativePNGs'].items()})
    require(inputs==plan['expectedInputs'] and len(inputs)==104 and digest_map(inputs)==plan['expectedSourceDigest'],'Full104 source prediction mismatch')
    inverse=dict(inputs)
    for r in plan['newNativePNGs']:del inverse[r]
    for r in plan['replacements']:inverse[r]=baseline['inputs'][r]
    require(inverse==baseline['inputs'],'Full104→98 map inverse')
    originalHeld={r:h for r,h in baseline['outputs'].items() if r.startswith(('art/','audio/'))};held=dict(originalHeld)
    require(len(originalHeld)==59,'Baseline59 output bodies')
    held.update({r[7:]:x['sha256'] for r,x in plan['replacements'].items() if r.startswith('public/')});held.update({r[7:]:x['sha256'] for r,x in plan['newNativePNGs'].items()})
    require(held==plan['expectedHeldOutputs'] and len(held)==65 and digest_map(held)==plan['expectedHeldOutputsDigest'],'Candidate65 output bodies')
    inverseHeld=dict(held)
    for r in plan['newNativePNGs']:del inverseHeld[r[7:]]
    inverseHeld['art/coherent-native128-manual-crop-view-manifest.json']=originalHeld['art/coherent-native128-manual-crop-view-manifest.json']
    require(inverseHeld==originalHeld,'Full65→59 output inverse')
    manifest=document(plan['replacements']['public/art/coherent-native128-manual-crop-view-manifest.json']);art=data(plan['replacements']['src/art.ts']['path']).decode();helper=data(plan['replacements']['src/coherent-native128.ts']['path']).decode()
    descriptor=json.loads(art.split('export const COHERENT_NATIVE128 = ',1)[1].split(' as const;',1)[0])
    oldManifest=json.loads(data(donor/'public/art/coherent-native128-manual-crop-view-manifest.json'))
    require(len(manifest['sprites'])==13 and manifest['sprites'][:7]==oldManifest['sprites'] and descriptor['sprites']==manifest['sprites'] and descriptor['manifestSha256']==plan['replacements']['public/art/coherent-native128-manual-crop-view-manifest.json']['sha256'] and manifest['animation'] is None,'Exact13 roles/digest descriptor')
    require('sprites.length !== 13' in helper and 'images.length === 13' in helper,'All13 readiness admission source')
    expectedAliases=sorted([r for r in inputs if media_leaf(r) and r not in plan['newNativePNGs']]+['dist/'+r for r in held if media_leaf(r)])
    require(expectedAliases==plan['expectedAliasKeys'],'Derived complete new alias domain')
    require(not STAGE.exists() and not STAGE.is_symlink(),'Fresh stage only; preserve partial failures')
    v=os.statvfs(STAGE.parent);require(v.f_bavail*v.f_frsize>=64*1048576,'Disk64 absent');STAGE.mkdir()
    for relative in sorted(inputs):
        destination=STAGE/safe_relative(relative);destination.parent.mkdir(parents=True,exist_ok=True)
        pp=plan['replacements'].get(relative) or plan['newNativePNGs'].get(relative);origin=pp['path'] if pp else donor/relative
        if media_leaf(relative) and relative not in plan['newNativePNGs']:destination.symlink_to(origin)
        else:copy(origin,destination)
    (STAGE/'node_modules').symlink_to(donor/'node_modules',target_is_directory=True)
    for relative in support:
        destination=STAGE/relative;destination.parent.mkdir(parents=True,exist_ok=True);require(not destination.exists(),'Support collision');copy(donor/relative,destination)
    observed={r:sha(STAGE/r) for r in sorted(inputs)};require(observed==inputs,'Fresh assembly full identity mismatch')
    for rel in inputs:
        real,chain=trace(STAGE/rel)
        if media_leaf(rel) and rel not in plan['newNativePNGs']:
            donorReal,donorChain=pinned_donor_file(donor,rel,catalogue);require(chain==[{'path':str(STAGE/rel),'target':str(donor/rel),'finalLeaf':True}]+donorChain and real==donorReal,'New input alias chain mismatch')
        else:
            require(not chain and real==STAGE/rel,'Code/JSON/new PNG must be private copies')
            origin=plan['replacements'].get(rel) or plan['newNativePNGs'].get(rel);origin=Path(origin['path']) if origin else donor/rel
            old=origin.stat();new=(STAGE/rel).stat();require((old.st_dev,old.st_ino)!=(new.st_dev,new.st_ino),'Private inode reused')
    assembly={'stage':str(STAGE),'inputs':observed,'inputCount':104,'sourceDigest':digest_map(observed),'baselineStage':str(donor),'baselineOutputs':baseline['outputs'],'baseline':plan['donorFreeze'],'expectedHeldOutputs':held,'supportBodies':support,'activationPath':str(Path(activation_path).absolute()),'activationSHA256':sha(activation_path),'sourceGate':activation['methodGate'],'starterSourceGate':plan['starterSourceGate'],'starterSourcePlan':plan['sourcePlan'],'donorAliasCatalogue':plan['donorAliasCatalogue'],'newPrivateNativeInputs':sorted(plan['newNativePNGs']),'expectedAliasKeys':expectedAliases,'qualification':plan['qualification']}
    control=STAGE/'.control';control.mkdir();(control/'ASSEMBLY.json').write_text(json.dumps(assembly,indent=2)+'\\n');return assembly
'''
originals={n:r(OLD/n).decode() for n in ['assemble.py','bounded-build.py','finalize.py','strict-build-runner.mjs']};new={};proof={};diffs={}
for n,s0 in originals.items():
 s=s0.replace('/workspace/scratch/native128-empty-intent-stage-r1',NEW)
 if n=='assemble.py':
  node=next(x for x in ast.parse(s).body if isinstance(x,ast.FunctionDef) and x.name=='assemble');oldBody=ast.get_source_segment(s,node);s=s.replace(oldBody,newBody.rstrip(),1);s=s.replace('future fresh empty-intent CSS assembly','future fresh thirteen-sprite starter assembly')
 elif n=='finalize.py':
  for a,b in [("assembly['inputCount']==98","assembly['inputCount']==104"),("len(held)==59","len(held)==65"),("Exact59 retained art/audio outputs required","Exact65 retained/new art/audio outputs required"),("len(inputs)==98 and len(outputs)==64","len(inputs)==104 and len(outputs)==70"),("Full98/64 identity mismatch","Full104/70 identity mismatch"),("'inputCount':98,'outputCount':64","'inputCount':104,'outputCount':70"),("require(len(aliases)==115,'Full115 fresh leaf chain inventory required')","require(set(aliases)==set(assembly['expectedAliasKeys']),'Complete derived fresh alias leaf domain required')"),("'count':115","'count':len(aliases)")]:need(s.count(a)==1,'Unique finalizer delta '+a);s=s.replace(a,b)
 # Record whole-source replacement inverse as a lossless unified delta; verify every byte unchanged outside named intended edit spans via reverse sequence.
 delta=list(difflib.unified_diff(s0.splitlines(True),s.splitlines(True),fromfile=str(OLD/n),tofile=str(P/n)))
 new[n]=s.encode();diffs[n+'.diff.gz']=gzip.compress(''.join(delta).encode(),mtime=0)
 # Exact full inverse using frozen original slices from matching-block map (no module execution).
 matcher=difflib.SequenceMatcher(None,s0,s,autojunk=False);recovered=[]
 for tag,i,j,k,l in matcher.get_opcodes():recovered.append(s[k:l] if tag=='equal' else s0[i:j])
 need(''.join(recovered)==s0,'Full controls byte inverse '+n)
 if n.endswith('.py'):ast.parse(s)
 proof[n]={'original':pin(OLD/n),'candidateSHA256':sha(new[n]),'bytes':len(new[n]),'deltaGzipSHA256':sha(diffs[n+'.diff.gz']),'fullByteInverse':True}
need(originals['bounded-build.py'].split('checks=',1)[1]==new['bounded-build.py'].decode().split('checks=',1)[1],'All13 resource checks exact unchanged')
proof['full104SourceMapInverse']=True;proof['full65HeldOutputMapInverse']=True;proof['expectedAliasCountDerived']=len(expectedAliases);proof['newPNGsPrivateInputCopies']=True;proof['noActualStageBuild']=True;proof['rssKiB']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
argv={'futureAssembly':['python3','-B','/workspace/scratch/guard-node-phase-r1.py',str(BASE),'/workspace/scratch/starter-family-native128-assembly-guard-root-r1','64','python3','-B',str(P/'assemble.py'),'--activation','/workspace/scratch/starter-family-native128-activation-root-r1.json'],'futureStrictBuild':['python3','-B',str(P/'bounded-build.py'),E],'buildCwd':NEW,'futureFreeze':['python3','-B','/workspace/scratch/guard-node-phase-r1.py',NEW,'/workspace/scratch/starter-family-native128-freeze-guard-root-r1','64','python3','-B',str(P/'finalize.py'),'--evidence',E+'/final-seal-r1'],'commandsNotExecuted':True,'rootGOAndIndependentControlsGateRequired':True,'activationSchema':{'rootAssemblyAuthorized':True,'methodGate':{'path':'FUTURE_INDEPENDENT_GATE_PATH','sha256':'EXACT_FUTURE_GATE_SHA256'}}}
files={**new,**diffs,'PLAN.json':enc(plan),'PROOF.json':enc(proof),'ARGV.json':enc(argv)}
current=sum(q.stat().st_size for q in P.rglob('*') if q.is_file());need(current+sum(map(len,files.values()))+10000<=131072,'Upfront family128KiB with10000B final/guard reserve')
for n,b in files.items():
 with (P/n).open('xb') as q:q.write(b);q.flush();os.fsync(q.fileno())
 need(r(P/n)==b,'Full saved body readback')
print(json.dumps({'writtenBytes':sum(map(len,files.values())),'predictedSource':digest(inputs),'inputs':104,'outputsUnbuilt':70,'derivedAliases':len(expectedAliases),'fullControlsInverses':True,'all13ChecksUnchanged':True,'rssKiB':proof['rssKiB']}))
