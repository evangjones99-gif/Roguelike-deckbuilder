from pathlib import Path
import os,json,hashlib,resource,stat,ast
resource.setrlimit(resource.RLIMIT_DATA,(24*1048576,24*1048576))
S=Path('/workspace/scratch');R=Path('/workspace/Roguelike-deckbuilder');M=S/'default-clear-publication-source-author-r1';P=S/'default-clear-preservation-independent-r1'
def pin(path,body=False):
 p=Path(path);fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME);h=hashlib.sha256();parts=[]
 with os.fdopen(fd,'rb') as f:
  before=os.fstat(f.fileno());assert stat.S_ISREG(before.st_mode)
  for b in iter(lambda:f.read(65536),b''):
   h.update(b)
   if body:parts.append(b);assert sum(map(len,parts))<262144
  assert before==os.fstat(f.fileno())==os.lstat(p)
 q={'path':str(p),'sha256':h.hexdigest(),'bytes':before.st_size}
 return (q,b''.join(parts)) if body else q
def load(p):
 q,b=pin(p,True);return q,json.loads(b)
planp,plan=load(M/'PLAN-r2.json');seal,final=load(M/'FINAL-SEAL-r2.json');cp,controls=load(M/'REVIEW-CONTROLS.json')
assert planp['sha256']=='70d17add054eaabfd28f6fef64858815d642d4a966a0d4db8e958e882df22fd9' and seal['sha256']=='e82302c7c71a80a8ca42a3042f3e5b29765af381a4e181eb6ec05b5ef55fec40' and cp['sha256']=='85a5315b6af4ed30afa7d72436ab8fc09c426ce5e330af0a9f7c7f33a3f06ef9'
methods=[]
for n,h in [('common.py','088c08e787ecfaaf7f2cb448b9736a0cdc1a605e647ea4b598ef2c45c7bd03a8'),('build-capsule-r2.py','bd9391206d25ad86b132bf11bb0774e3a66fe34067b312cc567a82283dbcfd8e'),('promote-default-r2.py','3080b1b9ee08dd3f3751bc2f18afb532715aaade1874434864c2156be10521c9'),('publish-selected-r2.py','2fb2771bc7d9fd85334cb35498347cbea0e32d0409d031fbdc9e3076f7806d9a')]:
 q,b=pin(M/n,True);assert q['sha256']==h;ast.parse(b);methods.append(q)
sealedCount=0
for rel,z in final['files'].items():
 q=pin(M/rel);assert q['sha256']==z['sha256'] and q['bytes']==z['bytes'];sealedCount+=1
reviewpins=[]
for role,z in controls.items():
 q,g=load(z['path']);assert q['sha256']==z['sha256'] and g['decision'].startswith('ACCEPT');reviewpins.append({'role':role,**q})
beforep,before=load(plan['beforeMap']['path']);afterp,after=load(plan['candidateFreeze']['path']);assert beforep==plan['beforeMap'] and afterp==plan['candidateFreeze'];stage=Path(after['stage'])
assert len(before['inputs'])==len(after['inputs'])==88 and len(before['outputs'])==len(after['outputs'])==56
assert set(before['inputs'])==set(after['inputs']) and {r for r in before['inputs'] if before['inputs'][r]!=after['inputs'][r]}=={'src/main.ts'}
assert after['sourceDigest']==plan['candidateSourceDigest'] and after['outputsDigest']==plan['candidateOutputsDigest']
media={r:h for r,h in before['outputs'].items() if r.startswith(('art/','audio/'))};assert len(media)==51 and media==plan['unchanged51Media']=={r:h for r,h in after['outputs'].items() if r.startswith(('art/','audio/'))}
assert plan['old5']=={r:h for r,h in before['outputs'].items() if r not in media} and plan['new5']=={r:h for r,h in after['outputs'].items() if r not in media}
assert plan['oldJS']!=plan['newJS'] and not (R/'dist'/plan['newJS']).exists()
records=[];deps=[]
for label,base,freeze in [('old-current',R,before),('candidate',stage,after)]:
 for scope,root,mapping in [('inputs',base,freeze['inputs']),('outputs',base/'dist',freeze['outputs'])]:
  for rel,h in mapping.items():
   path=root/rel;q=pin(path);assert q['sha256']==h
   row={'logicalPath':label+'/'+scope+'/'+rel,'originalPath':str(path),'bytes':q['bytes'],'sha256':h}
   if rel.endswith(('.png','.wav')) or scope=='outputs' and rel.startswith(('art/','audio/')):deps.append(row)
   else:records.append(row)
def tree(root):
 for p in sorted(root.rglob('*')):
  assert not p.is_symlink()
  if p.is_file():yield p,str(p.relative_to(root))
actual=Path(plan['actual']['root']);actualfiles=list(tree(actual));assert len(actualfiles)==28 and {rel:p.stat().st_size for p,rel in actualfiles}=={q['name']:q['bytes'] for q in plan['actual']['metadata']}
roots=plan['roots']+[{'label':'publication-source','path':str(M)}]+[{'label':'actual-review-'+role,'path':str(Path(q['path']).parent)} for role,q in controls.items()]
rootcounts={}
for root in roots:
 count=0
 for path,rel in tree(Path(root['path'])):
  assert not path.name.endswith(('.zip','.tar.gz','.tgz','.png','.wav'));q=pin(path);records.append({'logicalPath':root['label']+'/'+rel,'originalPath':str(path),'bytes':q['bytes'],'sha256':q['sha256']});count+=1
 rootcounts[root['label']]=count
for q in plan['singleControls']+[cp]:
 fresh=pin(q['path']);assert fresh==q;records.append({'logicalPath':'single-controls/'+Path(q['path']).name,'originalPath':q['path'],'bytes':q['bytes'],'sha256':q['sha256']})
assert len(records)<1500 and len({q['logicalPath'] for q in records})==len(records)
oldmp,oldcaller=load(S/'target-clear-default-caller-author-r1/MANIFEST.json');assert len(oldcaller['bodies'])==34
_,compactcaller=load(S/'target-clear-default-compact-caller-author-r2/MANIFEST.json');assert len(compactcaller['bodies'])==3
assert compactcaller['retainedRoot']==str(S/'target-clear-default-caller-author-r1') and compactcaller['retainedManifestSHA256']==oldmp['sha256']
for auditname in ['BYTE-AUDIT-before.json','BYTE-AUDIT-after.json']:
 _,aud=load(actual/auditname);assert len(aud['controls'])==37
 expected={(str(S/'target-clear-default-caller-author-r1'),z['name'],z['sha256'],z['bytes']) for z in oldcaller['bodies']}|{(str(S/'target-clear-default-compact-caller-author-r2'),z['name'],z['sha256'],z['bytes']) for z in compactcaller['bodies']}
 assert {(z['root'],z['name'],z['sha256'],z['bytes']) for z in aud['controls']}==expected
for folder,manifest in [('old-caller-controls',oldcaller),('compact-caller',compactcaller)]:
 root=next(Path(z['path']) for z in roots if z['label']==folder)
 for z in manifest['bodies']:
  q=pin(root/z['name']);assert q['sha256']==z['sha256'] and any(x['originalPath']==q['path'] for x in records)
saveidentities=[]
for side in ['A','B']:
 for label in ['C0','C1','C2','C-firstDrop','C-secondOutcome','C-normalized']:
  path=actual/(side+'-hold-release-'+label+'-OPAQUE-SAVE.json');q,wrapper=load(path);b=wrapper['raw'].encode();saveidentities.append({'label':side+'/'+label,'wrapperSHA':q['sha256'],'rawSHA':hashlib.sha256(b).hexdigest(),'rawBytes':len(b)})
assert all(saveidentities[i]['rawSHA']==saveidentities[i+6]['rawSHA'] for i in range(6))
protected=S/'retained-original-archives/preflight-bdf273-original-r4.zip';z=os.lstat(protected);zipstat={k:getattr(z,k) for k in ['st_dev','st_ino','st_mode','st_nlink','st_uid','st_gid','st_size','st_blocks','st_atime_ns','st_mtime_ns','st_ctime_ns']}
headp,b=pin(R/'.git/refs/heads/codex/lanternbound-production',True);assert b.decode().strip()==plan['currentHEADAtSourcePreparation']=='c2050598c334fa390a61d1b385c309dc6fa17c87'
unique={q['sha256']:q['bytes'] for q in records};rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024;assert rss<24*1048576
d={'conditionalSourceOnly':True,'plan':planp,'sourceSeal':seal,'methods':methods,'reviewControls':cp,'actualReviewGates':reviewpins,'beforeMap':beforep,'candidateFreeze':afterp,'inputCounts':[88,88],'outputCounts':[56,56],'onlyChangedSource':'src/main.ts','unchangedHeldMedia':51,'oldFive':plan['old5'],'newFive':plan['new5'],'oldJS':plan['oldJS'],'newJS':plan['newJS'],'plannedActualCount':28,'rootCounts':rootcounts,'plannedLogicalBodyCount':len(records),'plannedUniqueBlobs':len(unique),'plannedUniqueBodyBytes':sum(unique.values()),'logicalRecordDigest':hashlib.sha256(json.dumps(records,sort_keys=True,separators=(',',':')).encode()).hexdigest(),'neededDependencyCount':len(deps),'neededDependencyRecordDigest':hashlib.sha256(json.dumps(deps,sort_keys=True,separators=(',',':')).encode()).hexdigest(),'oldCallerFullAuditedBodies':34,'compactCallerNewBodies':3,'aggregateAuditedCallerControls':37,'sixFullRawStringPairs':saveidentities,'currentHEADSourcePin':headp,'protectedZIPFullStat':zipstat,'protectedZIPBodyNeverOpened':True,'ownMaxRSSBytes':rss,'limits':'Source eligibility only: no capsule exists/roundtrip claimed here. Complete immutable capsule+later independent GATE required before Root selection. Oldmain/fiveoutputs manual rollback, oldJS physical rename finaldist56/transient57 until completion; no alltransaction atomicity/auto rollback or media writes. Retained dependencies not self-contained executable release.','noCapsuleGitPromotionEngineNodeCleanup':True}
with (P/'SOURCE-PROOF.json').open('x') as f:json.dump(d,f,separators=(',',':'));f.write('\n');f.flush();os.fsync(f.fileno())
print(json.dumps({'sourceNormal':True,'logicalBodies':len(records),'uniqueBlobs':len(unique),'dependencies':len(deps),'actualFiles':28,'oldCallerBodies':34,'compactCallerNewBodies':3,'aggregateAuditedCallerControls':37,'ownRSSBytes':rss,'allOwnFDsClosed':True}))
