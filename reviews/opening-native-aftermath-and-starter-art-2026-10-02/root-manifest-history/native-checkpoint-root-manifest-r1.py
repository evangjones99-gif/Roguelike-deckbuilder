import os,stat,json,hashlib,time,subprocess,resource
from pathlib import Path
S=Path('/workspace/scratch'); R=Path('/workspace/Roguelike-deckbuilder'); A=S/'native-aftermath-starter-checkpoint-source-author-r1'
started=time.monotonic()
def sha(p):
 h=hashlib.sha256();fd=os.open(p,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW)
 with os.fdopen(fd,'rb') as f:
  assert stat.S_ISREG(os.fstat(f.fileno()).st_mode)
  while b:=f.read(65536):h.update(b)
 return h.hexdigest()
def pin(p,h):assert sha(p)==h,(str(p),h);return json.loads(Path(p).read_bytes())
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()=='06007e0d81298fa49cedeb46719d03cae9fba04c'
assert not subprocess.check_output(['git','status','--porcelain'],cwd=R)
s=pin(A/'SOURCE-SPEC.json','c433f479bf32a66beeb2696fb5a009be7746d9353641ea3caee7fbbd77bdcdaf');patch=pin(A/'SOURCE-SPEC-final.json','13d1c918f57c103929e098a03ce90ba7574161e1e0ae75e598960812e7ec6e0f');s.update(patch['updates'])
for key,add in [('requiredRoots','appendRequiredRoots'),('fixedSingleFiles','appendFixedSingleFiles'),('requiredControlPins','appendControlPins')]:s[key]+=patch[add]
g=pin(S/'native-aftermath-starter-checkpoint-source-independent-r1/GATE.json','698daceaa2775a0934f825fdf20020050937cf7d2450cf962fe7114a8485fd97');assert g['sourceEngineeringEligible'] and g['methodSHA256']==s['activeMethodSHA256'] and g['specSHA256']==sha(A/'SOURCE-SPEC-final.json')
assert sha(A/'preserve-direct-final.py')==s['activeMethodSHA256'];assert sha(A/'preserve-direct-r2.py')==g['implementationSHA256']
for q in s['requiredControlPins']:assert sha(q['path'])==q['sha256'] and Path(q['path']).stat().st_size==q['bytes']
roots=sorted(set(s['requiredRoots'])|set(s['futureOptionalFixedRoots']));assert all(Path(x).exists() for x in roots)
old=s['existingCapsules'][0];idx=pin(old['index']['path'],old['index']['sha256']);pin(old['complete']['path'],old['complete']['sha256']);assert idx['newArchive']['sha256']==old['archive']['sha256'];oldst=Path(old['archive']['path']).lstat();assert stat.S_ISREG(oldst.st_mode) and oldst.st_size==old['archive']['bytes']
prior={(str(Path(idx['roots'][r[0]])/r[1]),r[2],r[3]) for r in idx['rows']};del idx
runtime={x['stage']:x for x in s['runtimeAuthorities']};singles=set(s['fixedSingleFiles']);allowed={x['path'] for x in s['fixedRoots']}|set(runtime)|singles;assert set(roots)<=allowed
rows=[];codes={};external=[];verified=0
for i,root in enumerate(roots):
 p=Path(root);assert not p.is_symlink()
 if root in runtime:
  a=runtime[root];f=pin(a['freeze']['path'],a['freeze']['sha256']);assert [f['inputCount'],f['outputCount']]==a['mappedCounts'] and f['sourceDigest']==a['sourceDigest'] and f['outputsDigest']==a['outputsDigest']
  m={**f['inputs'],**{'dist/'+k:v for k,v in f['outputs'].items()}}; code={k:h for k,h in m.items() if not any(z in k for z in ['public/art/','public/audio/','dist/art/','dist/audio/']) and k!='desktop/icon.png'};assert len(code)==43
  codes[root]=sorted(code); members=[p/k for k in codes[root]]
  catref=f['actualAliasCatalogue'];cat=pin(catref['path'],catref['sha256']);assert catref['count']==len(cat['leaves'])==len(cat['chains'])==115
  for name,(h,leaf,chainidx) in cat['leaves'].items():
   assert m[name]==h
   for frm,to,isleaf in cat['chains'][chainidx]:
    q=Path(cat['roots'][frm[0]]+frm[1]);target=Path(cat['roots'][to[0]]+to[1]);assert q.is_symlink();literal=os.readlink(q);assert os.path.normpath(os.path.join(str(q.parent),literal))==str(target)
   body=Path(cat['roots'][leaf[0]]+leaf[1]);assert sha(body)==h and (p/name).resolve()==body.resolve()
  for name,h in f['supportBodies'].items():assert sha(p/name)==h
  chain=[];q=p/'node_modules'
  while q.is_symlink():
   target=os.readlink(q);chain.append({'path':str(q),'literalTarget':target});q=Path(os.path.normpath(os.path.join(str(q.parent),target)));assert len(chain)<20
  assert q.is_dir();tools=[]
  for name in ['vite','typescript','vitest','tsx','@playwright/test']:
   tool=q/name/'package.json';tools.append({'path':str(tool),'sha256':sha(tool),'version':json.loads(tool.read_bytes())['version']})
  external.append({'stage':root,'freeze':a['freeze'],'mediaAliasCatalogue':catref,'all115LiteralChainsAndLeafSHA256Verified':True,'mediaAndDesktopIconOutsideNewCapsule':{k:v for k,v in m.items() if k not in code},'support30BodiesExternalSHA256':f['supportBodies'],'nodeModulesLiteralChain':chain,'installedToolPackagePins':tools,'qualification':'All media aliases and leaf bytes checked here; support30 checked. Installed shared tool package metadata pinned; full installed dependency tree NOT Merkle hashed or included. Runtime media, tool binaries, node_modules and prior capsules remain external; this is not a self-contained release.'})
 elif root in singles:members=[p]
 else:
  assert p.is_dir();members=sorted((q for q in p.rglob('*') if q.is_file() and not q.is_symlink()),key=str)
 for q in members:
  rel='.' if root in singles else str(q.relative_to(p));assert not q.is_symlink();st=q.lstat();assert stat.S_ISREG(st.st_mode)
  assert not any(z in str(q) for z in ['/node_modules/','/.git/','/releases/','/retained-original-archives/']);h=sha(q);size=st.st_size
  if root in runtime:assert h==code[rel]
  rows.append([i,rel,h,size,'frozen-runtime-code' if root in runtime else 'original-complete-evidence','existing:4513' if (str(q),h,size) in prior else 'newBlob']);verified+=1
assert resource.getrusage(resource.RUSAGE_SELF).ru_maxrss<=24576
plan={'status':'FINAL_SOURCE_PLAN_REQUIRES_ROOT_ARCHIVE_GRANT','sourceSpecSHA256':sha(A/'SOURCE-SPEC-final.json'),'roots':roots,'rows':rows,'rowColumns':['rootIndex','relativePath','sha256','bytes','role','storage'],'roles':['frozen-runtime-code','original-complete-evidence'],'closedRoots':roots,'notRunRoots':[],'futurePhaseStates':{x:'CLOSED_INCLUDED' for x in s['futureOptionalFixedRoots']},'runtimeCodeAllowedRelativePaths':codes,'runtimeAuthorities':s['runtimeAuthorities'],'existingCapsules':s['existingCapsules'],'externalDependencies':external,'RootVerifiedCompleteFixedScopeAndOriginalFailures':True,'RootVerifiedFrozenMediaAliasAndInstalledDependenciesExplicit':True,'RootVerifiedEveryLogicalRowHashAndFrozenRuntimeCodeBinding':True,'proposedArchive':{'physicalOutputCapBytes':12*1048576,'newStoredArchiveCopies':1},'qualification':'Source-only CSS proposal included; CSS actual build/failed comparison and later caller repair outside fixed scope. Every named tree CLOSED, all old paths retained, prior4513 inheritance qualified. This finite offline Root manifest pass does not select art/default/game/release or delete anything. Metadata and literal bodies checked; no full xattr/time preservation claim.'}
raw=(json.dumps(plan,separators=(',',':'))+'\n').encode();assert len(raw)<=1048576 and len(rows)<=8192
out=S/'native-checkpoint-final-input-manifest-root-r1.json';out.open('xb').write(raw)
print(json.dumps({'path':str(out),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'roots':len(roots),'rows':len(rows),'newUniqueBodies':len({r[2] for r in rows if r[5]=='newBlob'}),'everyLogicalBodyHashed':verified,'runtimeCodeRows':sum(len(x) for x in codes.values()),'elapsedSeconds':time.monotonic()-started,'ownMaxRSSKiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}))
