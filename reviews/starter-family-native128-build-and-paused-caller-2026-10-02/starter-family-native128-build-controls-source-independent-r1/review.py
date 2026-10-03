import os,stat,json,hashlib,gzip,io,re,ast,resource,time
from pathlib import Path
P=Path(__file__).parent;A=Path('/workspace/scratch/starter-family-native128-build-controls-source-author-r1');beg=time.monotonic();pins={}
def raw(p):
 fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME)
 with os.fdopen(fd,'rb') as f:assert stat.S_ISREG(os.fstat(fd).st_mode);return f.read()
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p,h=None):
 b=raw(p);z=sha(b);assert h is None or z==h,str(p);pins[str(p)]=z;return b
def obj(p,h=None):return json.loads(pin(p,h))
def doc(x):
 b=pin(x['path'],x['sha256']);assert 'bytes' not in x or len(b)==x['bytes'];return json.loads(b)
def digest(m):return sha(json.dumps(dict(sorted(m.items())),separators=(',',':')).encode())
plan=obj(A/'PLAN.json','753be1feac8d1e112f10a1f29c795c4648386670d171d8983795e31156e59f8c');manifest=obj(A/'MANIFEST.json','78ca820ede04c0d6e7558aae6a2a4cabe0d6a4cc63dfb6e00fc761362b004cdd');final=obj(A/'FINAL-SEAL.json');proof=obj(A/'PROOF.json','3631899defeac8717128d48a42cd7879728dcde21aeb5fe01276085715ddcace');argv=obj(A/'ARGV.json','c223ec56b7d58b4d0856f19569aba79d4ca2b7bdd9f0ad0389f5df0c103e1b75')
for row in manifest:assert len(pin(A/row['name'],row['sha256']))==row['bytes']
assert final['controlsPlanSHA256']==pins[str(A/'PLAN.json')] and final['manifestSHA256']==pins[str(A/'MANIFEST.json')] and final['candidateSourceDigest']==plan['expectedSourceDigest']
for name in ['INSPECT-GUARD','PREPARE-GUARD','SEAL-GUARD']:
 r=obj(A/name/'RESULT.json');assert r['exit_code']==0 and r['failure'] is None and r['memory_events_before']==r['memory_events_after']
 assert all(x['headroom']>=512*1048576 and x['delta']<=64*1048576 for x in r['samples'])
def apply(diff,body,reverse=False):
 lines=diff.splitlines(True);src=body.splitlines(True);out=[];cursor=0;i=2;hunks=0
 while i<len(lines):
  match=re.match(r'^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@',lines[i]);assert match
  start=int(match.group(3 if reverse else 1))-1;i+=1;old=[];new=[]
  while i<len(lines) and not lines[i].startswith('@@ '):
   line=lines[i];assert line[0] in ' +-';kind=line[0];value=line[1:]
   if kind in ' -':old.append(value)
   if kind in ' +':new.append(value)
   i+=1
  before,after=(new,old) if reverse else (old,new);assert start>=cursor and src[start:start+len(before)]==before
  out+=src[cursor:start]+after;cursor=start+len(before);hunks+=1
 out+=src[cursor:];return ''.join(out),hunks
inverses=[];texts={}
for n in ['assemble.py','bounded-build.py','finalize.py','strict-build-runner.mjs']:
 x=proof[n];old=pin(x['original']['path'],x['original']['sha256']);new=pin(A/n,x['candidateSHA256']);assert len(old)==x['original']['bytes'] and len(new)==x['bytes']
 zipped=pin(A/(n+'.diff.gz'),x['deltaGzipSHA256']);assert zipped[4:8]==b'\0'*4
 with gzip.GzipFile(fileobj=io.BytesIO(zipped)) as f:delta=f.read(131073);assert len(delta)<=131072 and f.read(1)==b''
 generated,hunks=apply(delta.decode(),old.decode());restored,hunks2=apply(delta.decode(),new.decode(),True)
 assert generated.encode()==new and restored.encode()==old and hunks==hunks2
 texts[n]=new.decode();inverses.append({'name':n,'baselineSHA256':sha(old),'candidateSHA256':sha(new),'diffSHA256':sha(zipped),'fullForwardAndReverseBytesEqual':True,'hunks':hunks})
 if n.endswith('.py'):ast.parse(new)
 # Both executable build controls change only their exact private-stage literal.
 if n in ['bounded-build.py','strict-build-runner.mjs']:
  assert new==old.replace(b'/workspace/scratch/native128-empty-intent-stage-r1',b'/workspace/scratch/starter-family-native128-stage-r1')
stage=Path(plan['stage']);donor=Path(plan['donorStage']);assert str(stage)=='/workspace/scratch/starter-family-native128-stage-r1' and not os.path.lexists(stage)
baseline=doc(plan['donorFreeze']);assert baseline['stage']==str(donor) and baseline['sourceDigest']==plan['donorSourceDigest']=='76e5ba02635900ad242b047f9aa5e11adbc67b9e99f9cb67b35884405d21bc40' and baseline['outputsDigest']==plan['donorOutputsDigest']=='2547c159b14f634a2ec17473bded94af60c38e6f4aba8ea208f32dba9875f3a8'
assert len(baseline['inputs'])==98 and len(baseline['outputs'])==64 and digest(baseline['inputs'])==baseline['sourceDigest'] and digest(baseline['outputs'])==baseline['outputsDigest']
gate=doc(plan['starterSourceGate']);author=doc(plan['sourcePlan']);sourcefinal=doc(plan['sourceFinal']);assert plan['starterSourceGate']['sha256']=='d9e11d101944af80ada2f36cf7137633742aeff1d601d6bdf823ef924ade9beb'
assert gate['accepted'] and gate['sourceEngineeringEligible'] and gate['controlsPlanSHA256']==plan['sourcePlan']['sha256'] and gate['authorFinalSHA256']==plan['sourceFinal']['sha256'] and gate['candidateSourceDigest']==plan['expectedSourceDigest']
required={'src/main.ts':'mainDecodedSHA256','src/coherent-native128.ts':'helperDecodedSHA256','src/art.ts':'artSHA256','public/art/coherent-native128-manual-crop-view-manifest.json':'manifestSHA256'};assert set(plan['replacements'])==set(required)
for rel,field in required.items():
 x=plan['replacements'][rel];b=pin(x['path'],x['sha256']);assert len(b)==x['bytes'] and not Path(x['path']).is_symlink() and sha(b)==gate[field]==author['candidateSources'][Path(rel).name]['decodedSHA256']
assert author['externalSixPNGs']==list(plan['newNativePNGs'].values()) and len(plan['newNativePNGs'])==6
for x in plan['newNativePNGs'].values():assert len(pin(x['path'],x['sha256']))==x['bytes'] and not Path(x['path']).is_symlink()
for x in author['exactGatePins'].values():doc(x)
grant=doc(plan['materializationGrant']);receipt=doc(plan['materializationGuard']);assert plan['materializationGrant']['sha256']=='5f57fdd5cba66dae233643cf64a6fca3ad5a97d48a2f218a58114ddeaa1eb341'
assert grant['authorized'] and grant['sourceMaterializationOnly'] and grant['gateSHA256']==plan['starterSourceGate']['sha256'] and grant['planSHA256']==plan['sourcePlan']['sha256'] and receipt['exit_code']==0 and receipt['failure'] is None and receipt['memory_events_before']==receipt['memory_events_after']
assert all(str(Path(x['path']).parent)==grant['exactOutputDirectory'] for x in plan['replacements'].values())
expected=dict(baseline['inputs']);expected.update({k:x['sha256'] for k,x in plan['replacements'].items()});expected.update({k:x['sha256'] for k,x in plan['newNativePNGs'].items()})
assert expected==plan['expectedInputs'] and len(expected)==104 and digest(expected)==plan['expectedSourceDigest']=='65b31b3f21e34a624bdac962e4919c7dc1791e502eb6cfdb1612103b8036fe9c'
inverse=dict(expected)
for rel in plan['newNativePNGs']:del inverse[rel]
for rel in plan['replacements']:inverse[rel]=baseline['inputs'][rel]
assert inverse==baseline['inputs'] and expected['src/arena.ts']=='ce8ba9e8cd80ca5acd3e9eb6956a4879fc14abd465b66d7a4f358ca9052d2835'
originalHeld={k:v for k,v in baseline['outputs'].items() if k.startswith(('art/','audio/'))};held=dict(originalHeld);assert len(originalHeld)==59
held.update({k[7:]:x['sha256'] for k,x in plan['replacements'].items() if k.startswith('public/')});held.update({k[7:]:x['sha256'] for k,x in plan['newNativePNGs'].items()});assert held==plan['expectedHeldOutputs'] and len(held)==65 and digest(held)==plan['expectedHeldOutputsDigest']
inverseHeld=dict(held)
for rel in plan['newNativePNGs']:del inverseHeld[rel[7:]]
inverseHeld['art/coherent-native128-manual-crop-view-manifest.json']=originalHeld['art/coherent-native128-manual-crop-view-manifest.json'];assert inverseHeld==originalHeld
assert sum(held[k]==v for k,v in originalHeld.items())==58
def media(k):return Path(k).suffix.lower() in ['.png','.wav'] and k.startswith(('public/','desktop/','art/','audio/'))
aliasKeys=sorted([r for r in expected if media(r) and r not in plan['newNativePNGs']]+['dist/'+r for r in held if media(r)])
assert aliasKeys==plan['expectedAliasKeys'] and len(aliasKeys)==plan['expectedAliasCount']==121
cat=doc(plan['donorAliasCatalogue']);assert baseline['actualAliasCatalogue']=={'path':plan['donorAliasCatalogue']['path'],'sha256':plan['donorAliasCatalogue']['sha256'],'count':115} and len(cat['leaves'])==len(cat['chains'])==115
for name,(h,leaf,ci) in cat['leaves'].items():
 mapped=baseline['outputs'][name[5:]] if name.startswith('dist/') else baseline['inputs'][name];assert mapped==h
 for frm,to,isleaf in cat['chains'][ci]:
  q=Path(cat['roots'][frm[0]]+frm[1]);z=Path(cat['roots'][to[0]]+to[1]);assert q.is_symlink() and os.path.normpath(os.path.join(str(q.parent),os.readlink(q)))==str(z)
 body=Path(cat['roots'][leaf[0]]+leaf[1]);assert (donor/name).resolve()==body.resolve() and body.is_file()
for root in ['src','desktop','public','dist']:assert (donor/root).is_dir() and not (donor/root).is_symlink()
membership={p.relative_to(donor).as_posix() for d in ['src','desktop','public'] for p in (donor/d).rglob('*') if p.is_file()}|{'index.html','THIRD-PARTY.md','package.json','package-lock.json','tsconfig.json','vite.config.ts','scripts/build.mjs'}
assert membership==set(baseline['inputs']) and {q.relative_to(donor/'dist').as_posix() for q in (donor/'dist').rglob('*') if q.is_file()}==set(baseline['outputs'])
assert len(baseline['supportBodies'])==plan['supportCount']==30
for rel,h in baseline['supportBodies'].items():assert sha(raw((donor/rel).resolve()))==h
modules=(donor/'node_modules').resolve();assert modules.is_dir()
tools=[]
for n in ['typescript','vite']:
 q=modules/n/'package.json';data=pin(q);tools.append({'path':str(q),'sha256':sha(data),'version':json.loads(data)['version']})
view=json.loads(raw(plan['replacements']['public/art/coherent-native128-manual-crop-view-manifest.json']['path']));art=raw(plan['replacements']['src/art.ts']['path']).decode();descriptor=json.loads(art.split('export const COHERENT_NATIVE128 = ',1)[1].split(' as const;',1)[0]);oldview=json.loads(raw(donor/'public/art/coherent-native128-manual-crop-view-manifest.json'))
assert len(view['sprites'])==13 and view['sprites'][:7]==oldview['sprites'] and descriptor['sprites']==view['sprites'] and descriptor['manifestSha256']==plan['replacements']['public/art/coherent-native128-manual-crop-view-manifest.json']['sha256'] and view['animation'] is None
assert plan['resourcePlan']=={'assemblyMiB':64,'buildWorkMiB':384,'reserveMiB':512,'diskMiB':64,'heapMiB':256,'stopSeconds':55,'wholeSeconds':60,'attempts':1}
runner=texts['strict-build-runner.mjs'];assert "[tscEntry,'--noEmit']" in runner and "publicDir:false,cacheDir:path.resolve('.vite-cache')" in runner and "NODE_OPTIONS':'--max-old-space-size=256'" in texts['bounded-build.py']
tree=ast.parse(texts['bounded-build.py']);checks=next(x.value for x in tree.body if isinstance(x,ast.Assign) and any(isinstance(z,ast.Name) and z.id=='checks' for z in x.targets));assert len(checks.keys)==13
assert 'pgrp==proc.pid' not in texts['bounded-build.py'] and "v['starttime']==launched_starttime" in texts['bounded-build.py'] and "if check[19]!=v['starttime']:continue" in texts['bounded-build.py']
assert argv['buildCwd']==str(stage) and argv['futureAssembly'][6:8]==['python3','-B'] and argv['futureAssembly'][5]=='64' and argv['futureFreeze'][5]=='64'
assert argv['futureAssembly'][-1]=='/workspace/scratch/starter-family-native128-activation-root-r1.json' and argv['futureStrictBuild'][-1]==plan['strictBuildEvidence'] and argv['futureFreeze'][-1]==plan['strictBuildEvidence']+'/final-seal-r1'
assert "method.get('controlsPlanSHA256')==sha(P/'PLAN.json')" in texts['assemble.py'] and "activation.get('rootAssemblyAuthorized') is True" in texts['assemble.py']
assert 'require(set(aliases)==set(assembly[\'expectedAliasKeys\'])' in texts['finalize.py'] and "freeze['actualAliasCatalogue']={'path':str(aliasPath),'sha256':sha(aliasPath),'count':len(aliases)}" in texts['finalize.py']
assert resource.getrusage(resource.RUSAGE_SELF).ru_maxrss<=24576
result={'decision':'ACCEPT_EXACT_STARTER_BUILD_CONTROLS_SOURCE_FOR_FRESH_PRIVATE_STRICT_BUILD_ELIGIBILITY_ONLY','controlsSourceEngineeringEligible':True,'controlsPlanSHA256':pins[str(A/'PLAN.json')],'authorFinalSHA256':pins[str(A/'FINAL-SEAL.json')],'manifestSHA256':pins[str(A/'MANIFEST.json')],'candidateSourceDigest':plan['expectedSourceDigest'],'inputCountPrediction':104,'outputCountUnbuiltPrediction':70,'heldOutputCount':65,'originalHeldRowsUnchanged':58,'source104To98AndHeld65To59FullInverses':True,'fourMethodDiffForwardInverseVerified':inverses,'derivedFutureAliasKeys':121,'actualNewAliasCatalogueExists':False,'donor115CurrentLiteralAliasChainsChecked':True,'support30BodiesHashed':True,'actualMaterializationGrantAndNormalClosureVerified':True,'installedToolMetadata':tools,'strict13ResourceChecksAndOwnershipUnchanged':True,'activationRequirements':'Root exactmethodGate path/SHA, ACCEPT decision/controlsPlanSHA binding, explicit rootAssemblyAuthorized, new stage/activation/evidence paths, accepted starterSource d9e full tuple and materialization5f57/16b3 pins; later assembly/build/finalize guards and independently measured freeze needed.','resourcePlan':plan['resourcePlan'],'mediaHashQualification':'New6 PNG byte hashes and4 materialized sources independently renewed; all donor115 literal chains/freeze maps/current memberships/support30 checked. Donor bulk media bodies not rehashed here; inherited exact frozen body authority and future assembly/finalize full hashing required. No PNG decode.','dependencyQualification':'Current shared node_modules real target and installed TSC/Vite package metadata checked; full dependency tree not Merkle hashed. Future runner resolves actual installed TSC --noEmit including copied support30, Vite publicDirfalse/fresh stage cache; no Node run here.','authorityQualification':'Only reviewed presentation4body+6PNG changes from accepted Source d9e; content/engine/save/input/UID/Cairn7/floor/corpse maps unchanged. Canonical cue composition remains pending. Private fit eligibility not scene/art/default/animation/first300/fun acceptance.','freshness':'Stage absent now; assembly/finalizer reject existing targets and never overwrite old stages/media/support/shared node_modules. New6 PNG inputs regular private copies, existing media leaf symlinks, private manifest copy; final outputs6newPNG links to own private inputs, replacementviewregularcopy.','roleDisclosure':'Reviewer earlier utility/witness/helper-related authorship plus accepted distinct new starter wiring SOURCE; Cairn authors build controls. This is independent engineering adaptation of controls, no own creative or runtime approval.','noActualAssemblyBuildImportOrCopy':True,'ownMaxRSSKiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'elapsedSeconds':time.monotonic()-beg,'pins':pins}
(P/'AUDIT.json').open('x').write(json.dumps(result,separators=(',',':'))+'\n');print(json.dumps({k:result[k] for k in ['decision','candidateSourceDigest','inputCountPrediction','outputCountUnbuiltPrediction','derivedFutureAliasKeys','ownMaxRSSKiB','elapsedSeconds']}))
