import os,stat,json,hashlib,resource,time
from pathlib import Path
OWN=Path(__file__).parent; S=Path('/workspace/scratch'); A=S/'native-aftermath-starter-checkpoint-source-author-r1'
beg=time.monotonic(); pins={}; hashed=0
def raw(p):
 p=Path(p);fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME)
 with os.fdopen(fd,'rb') as f:
  assert stat.S_ISREG(os.fstat(f.fileno()).st_mode);return f.read()
def sha(p):
 global hashed
 h=hashlib.sha256();p=Path(p);fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME)
 with os.fdopen(fd,'rb') as f:
  b=os.fstat(f.fileno());assert stat.S_ISREG(b.st_mode)
  while chunk:=f.read(65536):h.update(chunk);hashed+=len(chunk)
  z=os.fstat(f.fileno());assert (b.st_dev,b.st_ino,b.st_size,b.st_mtime_ns)==(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns)
 return h.hexdigest()
def pin(p,h):
 assert sha(p)==h,str(p);pins[str(p)]=h;return json.loads(raw(p))
planpath=S/'native-checkpoint-final-input-manifest-root-r3.json';ph='91c82de1139c861da723ad8ec5208eac3791da16a6e67d32659865584b01ddc3'
p=pin(planpath,ph);assert planpath.stat().st_size==238090
s=pin(A/'SOURCE-SPEC.json','c433f479bf32a66beeb2696fb5a009be7746d9353641ea3caee7fbbd77bdcdaf')
patch=pin(A/'SOURCE-SPEC-final.json','13d1c918f57c103929e098a03ce90ba7574161e1e0ae75e598960812e7ec6e0f');assert patch['inherits']['sha256']==pins[str(A/'SOURCE-SPEC.json')];s.update(patch['updates'])
for key,addition in [('requiredRoots','appendRequiredRoots'),('fixedSingleFiles','appendFixedSingleFiles'),('requiredControlPins','appendControlPins')]:s[key]+=patch[addition]
g=pin(S/'native-aftermath-starter-checkpoint-source-independent-r1/GATE.json','698daceaa2775a0934f825fdf20020050937cf7d2450cf962fe7114a8485fd97')
assert g['sourceEngineeringEligible'] and g['finalRootManifestAndGrantRequired'] and not g['archiveExecuted']
assert sha(A/'preserve-direct-final.py')==g['methodSHA256']==s['activeMethodSHA256']=='5ad10c515b362ac6434ad6041565a13d74551f53e658c1f65c5ab4a08c10dd0f'
assert sha(A/'preserve-direct-r2.py')==g['implementationSHA256']=='9818bfbbb52ff3f4ad173c6c29071c77531011c95bda404f61636f9b3fad0568'
assert p['sourceSpecSHA256']==g['specSHA256']==pins[str(A/'SOURCE-SPEC-final.json')]
assert p['runtimeAuthorities']==s['runtimeAuthorities'] and p['existingCapsules']==s['existingCapsules']
roots=p['roots']; runtime={x['stage']:x for x in s['runtimeAuthorities']};singles=set(s['fixedSingleFiles'])
assert len(roots)==141 and len(set(roots))==len(roots)
assert set(roots)==set(s['requiredRoots'])|set(s['futureOptionalFixedRoots'])|set(runtime)
assert set(roots)<= {x['path'] for x in s['fixedRoots']}|singles|set(runtime)
assert p['closedRoots']==roots and p['notRunRoots']==[]
assert p['futurePhaseStates']=={x:'CLOSED_INCLUDED' for x in s['futureOptionalFixedRoots']} and len(p['futurePhaseStates'])==6
assert p['status']=='FINAL_SOURCE_PLAN_REQUIRES_ROOT_ARCHIVE_GRANT'
assert p['rowColumns']==['rootIndex','relativePath','sha256','bytes','role','storage']
assert p['proposedArchive']=={'physicalOutputCapBytes':12582912,'newStoredArchiveCopies':1}
rows=p['rows'];assert len(rows)==1278;members={r:set() for r in roots};identities={};fullbytes=0
for i,rel,h,n,role,storage in rows:
 assert type(i)==int and 0<=i<len(roots) and type(n)==int and n>=0
 q=Path(roots[i])/rel;assert not Path(rel).is_absolute() and '..' not in Path(rel).parts
 assert str(q) not in identities;identities[str(q)]=(h,n,storage);members[roots[i]].add(rel)
 assert q.lstat().st_size==n and sha(q)==h;fullbytes+=n
 assert role==('frozen-runtime-code' if roots[i] in runtime else 'original-complete-evidence')
 assert storage in ['newBlob','existing:4513']
 assert not any(x in str(q) for x in ['/node_modules/','/.git/','/releases/','/retained-original-archives/'])
for root in roots:
 q=Path(root);assert not q.is_symlink()
 if root in singles:assert members[root]=={'.'}
 elif root not in runtime:
  actual={str(z.relative_to(q)) for z in q.rglob('*') if z.is_file() and not z.is_symlink()};assert actual==members[root],root
for c in s['requiredControlPins']:
 assert identities[c['path']][:2]==(c['sha256'],c['bytes'])
old=s['existingCapsules'][0];oldst=Path(old['archive']['path']).lstat();assert stat.S_ISREG(oldst.st_mode) and oldst.st_size==old['archive']['bytes']
idx=pin(old['index']['path'],old['index']['sha256']);complete=pin(old['complete']['path'],old['complete']['sha256']);assert idx['newArchive']['sha256']==old['archive']['sha256']
prior={(str(Path(idx['roots'][r[0]])/r[1]),r[2],r[3]) for r in idx['rows']};del idx
for q,(h,n,storage) in identities.items():assert (storage=='existing:4513')==((q,h,n) in prior)
assert len({r[2] for r in rows if r[5]=='newBlob'})==1116
assert Path(old['archive']['path']).lstat()==oldst
assert len(p['externalDependencies'])==2;ext={x['stage']:x for x in p['externalDependencies']};runtimefacts=[]
for root,a in runtime.items():
 f=pin(a['freeze']['path'],a['freeze']['sha256']);assert [f['inputCount'],f['outputCount']]==a['mappedCounts']==[98,64]
 assert f['sourceDigest']==a['sourceDigest'] and f['outputsDigest']==a['outputsDigest']
 mapped={**f['inputs'],**{'dist/'+k:v for k,v in f['outputs'].items()}}
 code={k:h for k,h in mapped.items() if not any(x in k for x in ['public/art/','public/audio/','dist/art/','dist/audio/']) and k!='desktop/icon.png'}
 assert len(code)==43 and members[root]==set(code) and p['runtimeCodeAllowedRelativePaths'][root]==sorted(code)
 for rel,h in code.items():assert identities[str(Path(root)/rel)][0]==h
 e=ext[root];assert e['freeze']==a['freeze'] and e['mediaAliasCatalogue']==f['actualAliasCatalogue']
 assert e['mediaAndDesktopIconOutsideNewCapsule']=={k:h for k,h in mapped.items() if k not in code}
 assert e['support30BodiesExternalSHA256']==f['supportBodies'] and len(f['supportBodies'])==30
 for name,h in f['supportBodies'].items():assert sha(Path(root)/name)==h
 ref=f['actualAliasCatalogue'];cat=pin(ref['path'],ref['sha256']);assert ref['count']==len(cat['leaves'])==len(cat['chains'])==115
 for name,(h,leaf,ci) in cat['leaves'].items():
  assert mapped[name]==h
  for frm,to,isleaf in cat['chains'][ci]:
   q=Path(cat['roots'][frm[0]]+frm[1]);z=Path(cat['roots'][to[0]]+to[1]);assert q.is_symlink()
   assert os.path.normpath(os.path.join(str(q.parent),os.readlink(q)))==str(z)
  body=Path(cat['roots'][leaf[0]]+leaf[1]);assert body.is_file() and (Path(root)/name).resolve()==body.resolve()
 chain=[];q=Path(root)/'node_modules'
 while q.is_symlink():
  target=os.readlink(q);chain.append({'path':str(q),'literalTarget':target});q=Path(os.path.normpath(os.path.join(str(q.parent),target)));assert len(chain)<20
 assert q.is_dir() and chain==e['nodeModulesLiteralChain']
 assert len(e['installedToolPackagePins'])==4
 for tool in e['installedToolPackagePins']:
  assert sha(tool['path'])==tool['sha256'] and json.loads(raw(tool['path']))['version']==tool['version']
 assert e['all115LiteralChainsAndLeafSHA256Verified'] is True and 'NOT Merkle' in e['qualification']
 runtimefacts.append({'stage':root,'codeRows':len(code),'freezeSHA256':a['freeze']['sha256'],'aliasCatalogueSHA256':ref['sha256'],'literalAliasChainsVerified':115,'supportBodiesHashed':30,'installedPackageMetadataHashed':4,'mediaBytesNotRehashedHere':True})
assert sum(x['codeRows'] for x in runtimefacts)==86
guard=S/'native-checkpoint-manifest-guard-root-r3';r=json.loads(raw(guard/'RESULT.json'));ad=json.loads(raw(guard/'ADMISSION.json'));execution=json.loads(raw(guard/'EXECUTION.log'))
assert r['exit_code']==0 and r['failure'] is None and r['memory_events_before']==r['memory_events_after'] and len(r['samples'])==4
assert ad['admitted'] and ad['work']==64*1048576 and ad['reserve']==512*1048576
assert ad['command']==['python3','-B','/workspace/scratch/native-checkpoint-root-manifest-r3.py']
assert execution['sha256']==ph and execution['bytes']==238090 and execution['rows']==1278 and execution['roots']==141 and execution['runtimeCodeRows']==86 and execution['everyLogicalBodyHashed']==1278
assert execution['ownMaxRSSKiB']==13412 and execution['elapsedSeconds']<60
assert all(x['delta']<=64*1048576 and x['headroom']>=512*1048576 for x in r['samples'])
assert resource.getrusage(resource.RUSAGE_SELF).ru_maxrss<=24576
for q in [guard/'RESULT.json',guard/'ADMISSION.json',guard/'EXECUTION.log',S/'native-checkpoint-root-manifest-r3.py']:pins[str(q)]=sha(q)
result={'decision':'ACCEPT_EXACT_ROOT_R3_MANIFEST_CONTRACT_FOR_FUTURE_SEPARATE_ARCHIVE_GRANT','inputManifestSHA256':ph,'roots':141,'logicalRows':1278,'allLogicalRowsIndependentlyHashed':True,'fullLogicalBytesHashed':fullbytes,'runtimeCodeRows':86,'runtimeAuthoritiesLiterallyEqualToEffectiveSPEC':True,'membershipsComplete':True,'allSixFutureAshRootsClosedIncluded':True,'newUniqueBodies':1116,'runtime':runtimefacts,'priorArchiveRead':'STAT_ONLY; exact pinned prior index and COMPLETE read; no protected ZIP/TAR body opened','priorCompleteDecision':complete.get('decision'),'rootGuardNormal':True,'rootMinimumHeadroom':min(x['headroom'] for x in r['samples']),'rootFailures':'R1 omitted stages invalid; R2 missing guessed vitest metadata failed before manifest; both untouched and outside fixed archive scope','mediaQualification':'All 230 literal frozen alias chains and manifest/freeze/catalogue SHA bindings independently verified; media bodies not rehashed here. Root R3 source guard and prior independent build checks supplied full media byte hashing. Installed package metadata and support30 per stage checked; no full dependency Merkle claim.','closureQualification':'Root declared named phases closed; normal source guard establishes observed child-group closure, not universal workspace PID attribution.','methodAuthorDistinct':True,'priorRoleDisclosure':'Reviewer authored older converter utility/witness and helper-related work; this verdict reviews different-author preservation contract and actual Root manifest, not old algorithm/art design approval.','archiveExecuted':False,'artGameDefaultReleaseSelected':False,'ownMaxRSSKiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'elapsedSeconds':time.monotonic()-beg,'pins':pins}
out=OWN/'AUDIT.json';out.open('x').write(json.dumps(result,separators=(',',':'))+'\n');print(json.dumps({k:result[k] for k in ['decision','roots','logicalRows','runtimeCodeRows','fullLogicalBytesHashed','ownMaxRSSKiB','elapsedSeconds']}))
