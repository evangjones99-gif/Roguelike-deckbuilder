import os,stat,json,hashlib,resource,time
from pathlib import Path
P=Path(__file__).parent;S=Path('/workspace/scratch');A=S/'starter-family-native128-build-controls-source-author-r1';ST=S/'starter-family-native128-stage-r1';E=S/'starter-family-native128-strict-build-root-r1';beg=time.monotonic();pins={};logicalReads=0
def sha(p):
 global logicalReads
 p=Path(p);resolved=p.resolve(strict=True);h=hashlib.sha256();fd=os.open(resolved,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME)
 with os.fdopen(fd,'rb') as f:
  before=os.fstat(f.fileno());assert stat.S_ISREG(before.st_mode)
  while b:=f.read(65536):h.update(b);logicalReads+=len(b)
  after=os.fstat(f.fileno());assert (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns)
 return h.hexdigest()
def raw(p):
 fd=os.open(Path(p).resolve(strict=True),os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME)
 with os.fdopen(fd,'rb') as f:return f.read()
def doc(p,h=None):
 p=Path(p);z=sha(p);assert h is None or z==h,str(p);pins[str(p)]=z;return json.loads(raw(p))
def ref(x):
 z=doc(x['path'],x['sha256']);assert 'bytes' not in x or Path(x['path']).stat().st_size==x['bytes'];return z
def digest(v):return hashlib.sha256(json.dumps(dict(sorted(v.items())),separators=(',',':')).encode()).hexdigest()
plan=doc(A/'PLAN.json','753be1feac8d1e112f10a1f29c795c4648386670d171d8983795e31156e59f8c');controls=doc(S/'starter-family-native128-build-controls-source-independent-r1/GATE.json','d13ac39e58c37413ee9ac5ee8889bb03c9379bf5579e0d4491072c6de5c308a5');addendum=doc(S/'starter-family-native128-build-controls-source-independent-r1/SCOPE-ADDENDUM.json','479cfbf4c28e51db7e5d96a7872913dd5ea80abfa1814e5cf943d602dd267d13')
assert controls['controlsSourceEngineeringEligible'] and controls['controlsPlanSHA256']==pins[str(A/'PLAN.json')]
activation=doc(S/'starter-family-native128-activation-root-r1.json','19f0d4b161f3b1fcb237762fe6ddd763599681316d5c8c1431c7678bee98fea4');assert activation['rootAssemblyAuthorized'] and activation['allSourceActorsClosed'] and activation['privateBuildOnly'] and activation['methodGate']['sha256']==pins[str(S/'starter-family-native128-build-controls-source-independent-r1/GATE.json')]
freeze=doc(E/'final-seal-r1/RUNTIME-FREEZE.json','6e61e6e42b1c160e899da7888b20daf33264f8dc2f65d5301ac72e70537590fc');catalogue=ref(freeze['actualAliasCatalogue']);assert freeze['actualAliasCatalogue']['sha256']=='dc763ace41dfbb1666a989014fea57f71d8458c9cafdd0b0b280c6fa076686b6' and freeze['actualAliasCatalogue']['count']==121
assert freeze['stage']==str(ST) and freeze['inputCount']==len(freeze['inputs'])==104 and freeze['outputCount']==len(freeze['outputs'])==70
assert digest(freeze['inputs'])==freeze['sourceDigest']==plan['expectedSourceDigest']=='65b31b3f21e34a624bdac962e4919c7dc1791e502eb6cfdb1612103b8036fe9c'
assert digest(freeze['outputs'])==freeze['outputsDigest']=='960e723da3b98d31e99e2b4ce6ee2195dd9fea1bfce9c8254b3cb65c04b7b49d' and freeze['inputs']==plan['expectedInputs']
assert freeze['actualBrowserRun'] is False and freeze['acceptedDefault'] is False and freeze['animationProved'] is False
assembly=doc(ST/'.control/ASSEMBLY.json',freeze['assemblySHA256']);assert assembly['stage']==str(ST) and assembly['inputs']==freeze['inputs'] and assembly['sourceDigest']==freeze['sourceDigest'] and assembly['expectedHeldOutputs']==plan['expectedHeldOutputs'] and assembly['supportBodies']==freeze['supportBodies'] and assembly['expectedAliasKeys']==plan['expectedAliasKeys']
assert assembly['activationSHA256']==pins[str(S/'starter-family-native128-activation-root-r1.json')] and assembly['sourceGate']==activation['methodGate']
identity=doc(E/'final-seal-r1/ASSEMBLY-IDENTITY.json');assert identity['sha256']==freeze['assemblySHA256'] and identity['path']==str(ST/'.control/ASSEMBLY.json')
for k,v in controls['methods'].items():assert sha(A/k)==v
def membership(root):
 return {p.relative_to(root).as_posix() for d in ['src','desktop','public'] for p in (root/d).rglob('*') if p.is_file()}|{'index.html','THIRD-PARTY.md','package.json','package-lock.json','tsconfig.json','vite.config.ts','scripts/build.mjs'}
assert membership(ST)==set(freeze['inputs']) and {p.relative_to(ST/'dist').as_posix() for p in (ST/'dist').rglob('*') if p.is_file()}==set(freeze['outputs'])
for folder in ['src','desktop','public','dist','public/art','public/audio','dist/art','dist/audio']:assert (ST/folder).is_dir() and not (ST/folder).is_symlink()
for rel,h in freeze['inputs'].items():assert sha(ST/rel)==h,rel
for rel,h in freeze['outputs'].items():assert sha(ST/'dist'/rel)==h,rel
donor=Path(plan['donorStage']);base=ref(plan['donorFreeze']);oldcat=ref(plan['donorAliasCatalogue']);assert base['sourceDigest']==plan['donorSourceDigest'] and base['outputsDigest']==plan['donorOutputsDigest'] and len(base['inputs'])==98 and len(base['outputs'])==64
assert membership(donor)==set(base['inputs']) and {p.relative_to(donor/'dist').as_posix() for p in (donor/'dist').rglob('*') if p.is_file()}==set(base['outputs'])
for rel,h in base['inputs'].items():assert sha(donor/rel)==h
for rel,h in base['outputs'].items():assert sha(donor/'dist'/rel)==h
assert len(freeze['supportBodies'])==30 and freeze['supportBodies']==base['supportBodies']
for rel,h in freeze['supportBodies'].items():assert sha(ST/rel)==sha(donor/rel)==h and not (ST/rel).is_symlink()
inv=dict(freeze['inputs'])
for k in plan['newNativePNGs']:del inv[k]
for k in plan['replacements']:inv[k]=base['inputs'][k]
assert inv==base['inputs'] and digest(inv)==base['sourceDigest']
held={k:h for k,h in freeze['outputs'].items() if k.startswith(('art/','audio/'))};oldheld={k:h for k,h in base['outputs'].items() if k.startswith(('art/','audio/'))}
assert held==plan['expectedHeldOutputs'] and len(held)==65 and len(oldheld)==59 and sum(held[k]==h for k,h in oldheld.items())==58
invheld=dict(held)
for k in plan['newNativePNGs']:del invheld[k[7:]]
invheld['art/coherent-native128-manual-crop-view-manifest.json']=oldheld['art/coherent-native128-manual-crop-view-manifest.json'];assert invheld==oldheld
code={k:h for k,h in freeze['outputs'].items() if k not in held};assert len(code)==5 and {'index.html','CREDITS.md','build-provenance.json'}<=set(code) and sum(k.startswith('assets/') and k.endswith('.css') for k in code)==1 and sum(k.startswith('assets/') and k.endswith('.js') for k in code)==1
def trace(p):
 pending=list(Path(p).absolute().parts[1:]);cur=Path('/');links=[]
 while pending:
  cur/=pending.pop(0)
  if cur.is_symlink():
   target=os.readlink(cur);links.append([str(cur),os.path.normpath(os.path.join(str(cur.parent),target)),not pending]);assert len(links)<=16
   pending=list(Path(links[-1][1]).parts[1:])+pending;cur=Path('/')
  elif pending:assert cur.is_dir()
  else:assert cur.is_file()
 return str(cur),links
def verifycat(cat,root,inputs,outputs,expected):
 assert set(cat['leaves'])==set(expected) and len(cat['leaves'])==len(cat['chains'])==len(expected)
 mapped={**inputs,**{'dist/'+k:h for k,h in outputs.items()}}
 for rel,(h,leaf,ci) in cat['leaves'].items():
  decode=lambda v:cat['roots'][v[0]]+v[1]
  target,actual=trace(root/rel);wanted=[[decode(frm),decode(to),isleaf] for frm,to,isleaf in cat['chains'][ci]]
  assert actual==wanted and target==decode(leaf) and h==mapped[rel]
 return len(expected)
assert verifycat(catalogue,ST,freeze['inputs'],freeze['outputs'],plan['expectedAliasKeys'])==121
assert verifycat(oldcat,donor,base['inputs'],base['outputs'],oldcat['leaves'])==115
for rel in list(freeze['inputs'])+['dist/'+x for x in freeze['outputs']]:
 target,links=trace(ST/rel);assert bool(links)==(rel in catalogue['leaves'])
for rel,x in plan['newNativePNGs'].items():
 assert not (ST/rel).is_symlink() and sha(x['path'])==sha(ST/rel)==x['sha256']
 assert ((ST/rel).stat().st_dev,(ST/rel).stat().st_ino)!=(Path(x['path']).stat().st_dev,Path(x['path']).stat().st_ino)
 assert os.readlink(ST/'dist'/rel[7:])==str(ST/rel)
for rel,x in plan['replacements'].items():
 assert not (ST/rel).is_symlink() and sha(x['path'])==sha(ST/rel)==x['sha256']
 assert ((ST/rel).stat().st_dev,(ST/rel).stat().st_ino)!=(Path(x['path']).stat().st_dev,Path(x['path']).stat().st_ino)
assert not (ST/'dist/art/coherent-native128-manual-crop-view-manifest.json').is_symlink()
provenance=doc(ST/'dist/build-provenance.json');assert provenance['sourceDigest']==freeze['sourceDigest'] and provenance['hashes']==freeze['inputs']
view=doc(ST/'public/art/coherent-native128-manual-crop-view-manifest.json');art=raw(ST/'src/art.ts').decode();descriptor=json.loads(art.split('export const COHERENT_NATIVE128 = ',1)[1].split(' as const;',1)[0]);assert len(view['sprites'])==13 and descriptor['sprites']==view['sprites'] and descriptor['manifestSha256']==sha(ST/'public/art/coherent-native128-manual-crop-view-manifest.json') and view['animation'] is None
assert view['sprites'][:7]==json.loads(raw(donor/'public/art/coherent-native128-manual-crop-view-manifest.json'))['sprites']
for row in view['sprites']:assert row['native_dimensions']==[128,128] and row['ground_anchor']==[64,120] and row['mirror'] is False and sha(ST/'public/art'/row['filename'])==row['sha256']
helper=raw(ST/'src/coherent-native128.ts').decode();assert 'sprites.length !== 13' in helper and 'images.length === 13' in helper and 'if (config.allies > 2 || config.enemies > 2' in helper
assert freeze['inputs']['src/arena.ts']==base['inputs']['src/arena.ts']=='ce8ba9e8cd80ca5acd3e9eb6956a4879fc14abd465b66d7a4f358ca9052d2835'
main=raw(ST/'src/main.ts');assert main==raw(plan['replacements']['src/main.ts']['path'])
tsconfig=doc(ST/'tsconfig.json');assert tsconfig['compilerOptions']['noEmit'] is True and {'src','tests','scripts/*.ts','vite.config.ts','playwright.config.ts'}<=set(tsconfig['include'])
moduleChain=[];q=ST/'node_modules'
while q.is_symlink():target=os.readlink(q);moduleChain.append([str(q),target]);q=Path(os.path.normpath(os.path.join(str(q.parent),target)));assert len(moduleChain)<16
assert q.is_dir();tools=[]
for tool in ['typescript','vite']:
 p=q/tool/'package.json';package=doc(p);tools.append({'path':str(p),'sha256':pins[str(p)],'version':package['version']})
outer=doc(E/'build-outer-r1/RESULT.json');inner=doc(E/'build-inner-r1/RESULT.json');outerad=doc(E/'build-outer-r1/ADMISSION.json');innerad=doc(E/'build-inner-r1/ADMISSION.json');launch=doc(E/'build-outer-r1/OWNED-LAUNCH.json')
assert outer['normal'] is True and len(outer['checks'])==13 and all(outer['checks'].values()) and outer['exitCode']==0 and outer['failure'] is None and outer['errors']==[] and len(outer['rows'])==5
assert outer['eventsBefore']==outer['eventsAfter'] and not any(x['state']!='Z' for x in outer['remaining'].values()) and outer['originalRootStarttime']==launch['originalStarttime']
for pair in outer['allObservedPIDStartPairs'].values():assert pair['starttime'] and str(pair['pid']) in outer['ownedObserved']
assert outer['final']['elapsed']==1.3813678789883852 and outer['final']['elapsed']<60 and outer['maxDelta']==225497088<=384*1048576 and outer['minHeadroom']==1175814144>=512*1048576
assert outerad['admitted'] and outerad['work']==384*1048576 and outerad['reserve']==512*1048576 and outerad['stopAt']==55 and outerad['wholeLimit']==60 and outerad['initial']['free']>=64*1048576
assert sha(outerad['genericGuardPath'])==outerad['genericGuardSHA256']
assert inner['exit_code']==0 and inner['failure'] is None and inner['memory_events_before']==inner['memory_events_after'] and len(inner['samples'])==11
assert innerad['admitted'] and innerad['work']==384*1048576 and innerad['reserve']==512*1048576
assert innerad['command']==['node',str(A/'strict-build-runner.mjs')] and innerad['stage']==str(ST)
for sample in inner['samples']:assert sample['headroom']>=512*1048576 and sample['delta']<=384*1048576
log=raw(E/'build-inner-r1/EXECUTION.log').decode();terminal=json.loads(log.splitlines()[-1]);assert 'vite v8.3.1' in log and terminal['strictTypecheck'] and terminal['sourceDigest']==freeze['sourceDigest'] and terminal['inputs']==104 and terminal['publicDir'] is False and terminal['cache']=='.vite-cache' and terminal['mediaMountedAfterBuild'] is False
for guardname in ['starter-family-native128-assembly-guard-root-r1','starter-family-native128-freeze-guard-root-r1']:
 gd=S/guardname;r=doc(gd/'RESULT.json');ad=doc(gd/'ADMISSION.json');pins[str(gd/'EXECUTION.log')]=sha(gd/'EXECUTION.log')
 assert r['exit_code']==0 and r['failure'] is None and r['memory_events_before']==r['memory_events_after'] and ad['admitted'] and ad['work']==64*1048576 and ad['reserve']==512*1048576
 assert all(x['headroom']>=512*1048576 and x['delta']<=64*1048576 for x in r['samples'])
 if 'assembly' in guardname:assert ad['command'][-1]==str(S/'starter-family-native128-activation-root-r1.json')
 else:assert ad['command'][-1]==str(E/'final-seal-r1')
# The canonical hold is a separate existing authority, never a target of these methods.
canonical=Path('/workspace/Roguelike-deckbuilder');word=doc(S/'opening-turn-payoff-wording-strict-build-root-r1/final-seal-r1/RUNTIME-FREEZE.json','d6c225d5408c8e60433aed54655e922a44af224621fc8c48cb6aca8cd3c5883a');default=doc(S/'target-clear-default-build-author-r1/RUNTIME-FREEZE.json')
assert word['sourceDigest']=='64c2a14ada2b24796535f9bb71d8a6acc534685365bcf4f5665b21bf18595353' and default['outputsDigest'].startswith('8bba')
for rel,h in word['inputs'].items():assert sha(canonical/rel)==h,'Canonical source hold changed '+rel
for rel,h in default['outputs'].items():assert sha(canonical/'dist'/rel)==h,'Canonical dist hold changed '+rel
assert resource.getrusage(resource.RUSAGE_SELF).ru_maxrss<=24576
out={'decision':'ACCEPT_EXACT_ACTUAL_STARTER_PRIVATE_STRICT_BUILD_ENGINEERING_ONLY','actualComparisonEngineeringEligible':True,'stage':str(ST),'sourceDigest':freeze['sourceDigest'],'outputsDigest':freeze['outputsDigest'],'inputCount':104,'outputCount':70,'freezeSHA256':pins[str(E/'final-seal-r1/RUNTIME-FREEZE.json')],'aliasCatalogueSHA256':freeze['actualAliasCatalogue']['sha256'],'actual121FullAliasChainsVerified':True,'all174ActualMappedBodiesSHA256Verified':True,'all162DonorMappedBodiesUnchangedSHA256Verified':True,'full104To98And65To59MapInverses':True,'heldOutputs65':'58 unchanged+replacementview+6nativePNGs;5 actual code outputs measured','support30StageAndDonorHashed':True,'strictActualFullInstalledTSCNoEmitEvidence':'Actual runner resolved installed TSC, noEmit includes src/tests/scripts/Vite/Playwright configs with all30 support bodies copied and hashed; generic/outer normal0 and Viteactual log. No tests/browser executed.','strict13ChecksNormal':True,'wholeSeconds':outer['final']['elapsed'],'outerSamples':5,'innerSamples':11,'maxDeltaBytes':outer['maxDelta'],'outerMinHeadroomBytes':outer['minHeadroom'],'resourceQualification':'Observed cgroup point samples/aggregate delta, not exclusive process RSS or continuous peak. Final sampled resource/time after owned cleanup before RESULT write; Source/outer terminal receipts normal, no universal unobserved process-escape claim.','installedToolMetadata':tools,'nodeModulesLiteralChain':moduleChain,'fullDependencyTreeMerkleClaimed':False,'native13Admission':'All13 static saved byte identities and manifest/descriptor/source loader contract checked; browser decode/readiness/admission not exercised. Source stillmax2 allies/enemies despite enginecap6; latch/fallback/cueOFF remain, firstCairn+Ash≤2 and hand portraits privatefit only. Thirdbinding continuity separate.','canonicalHoldVerified':{'sourceDigest':word['sourceDigest'],'sourceBodies':len(word['inputs']),'outputsDigest':default['outputsDigest'],'distBodies':len(default['outputs']),'canonicalMutated':False},'sourceGateSHA256':'d13ac39e58c37413ee9ac5ee8889bb03c9379bf5579e0d4491072c6de5c308a5','activationSHA256':'19f0d4b161f3b1fcb237762fe6ddd763599681316d5c8c1431c7678bee98fea4','priorRoles':'Reviewer authored older utility/witness/helper work and reviewed distinct starter source/build controls; Cairn authors current wiring/control adaptation. Actual saved build identities/receipts independently verified, no own art/design/game approval.','artDefaultAnimationFirst300FunApproved':False,'browserRuntimeOrBuildRerun':False,'PNGDecode':False,'canonicalOrHeldMutation':False,'logicalBodyReadBytes':logicalReads,'ownMaxRSSKiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'elapsedSeconds':time.monotonic()-beg,'pins':pins}
(P/'AUDIT.json').open('x').write(json.dumps(out,separators=(',',':'))+'\n');print(json.dumps({k:out[k] for k in ['decision','inputCount','outputCount','actual121FullAliasChainsVerified','logicalBodyReadBytes','ownMaxRSSKiB','elapsedSeconds']}))
