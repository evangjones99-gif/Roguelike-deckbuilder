"""Built-in-only read-only preflight; no packet, subprocess or browser creation."""
import os,json,pathlib,hashlib
def sha(body):return hashlib.sha256(body).hexdigest()
def regular(file):
 p=pathlib.Path(file);assert p.is_absolute() and str(p)==file
 for index,part in enumerate(p.parts[1:]):
  q=pathlib.Path(*p.parts[:index+2]);assert not q.is_symlink();assert q.is_file() if q==p else q.is_dir()
 return p.read_bytes()
def record(file,pin):
 body=regular(file);assert sha(body)==pin,file;return json.loads(body)
def identity(file,pin):
 p=pathlib.Path(file)
 for index,part in enumerate(p.parts[1:]):
  q=pathlib.Path(*p.parts[:index+2]);assert not q.is_symlink();assert q.is_file() if q==p else q.is_dir()
 s=p.stat()
 for key,value in {'bytes':s.st_size,'dev':s.st_dev,'ino':s.st_ino,'mode':s.st_mode,'nlink':s.st_nlink,'mtimeNs':s.st_mtime_ns,'ctimeNs':s.st_ctime_ns}.items():assert str(value)==str(pin[key]),(file,key)
def qualify(expected,expected_bytes,caller_root):
 assert expected.get('sealed') is True and expected.get('runtimeEligible') is True and expected.get('runtimeRecovery',{}).get('complete') is True,'SOURCE_ONLY_UNSEALED: complete NEW stages and reviewed Root method grant required'
 grant=json.loads(regular(expected['rootMethodGrantPath']));assert grant['schema']=='opening-runtime-root-grant-v1' and grant['authorized'] is True and grant['callerRoot']==caller_root
 assert grant['expectedSHA256']==sha(expected_bytes) and grant['sourceManifestSHA256']==sha(regular(caller_root+'/MANIFEST.json')) and grant['sourceSealSHA256']==sha(regular(caller_root+'/SOURCE-SEAL.json'))
 seal=json.loads(regular(caller_root+'/SOURCE-SEAL.json'))
 for ref in seal['files']:
  body=regular(caller_root+'/'+ref['name']);assert len(body)==ref['bytes'] and sha(body)==ref['sha256']
 assert grant['actualPacket']==expected['actualPacket'] and grant['driverSeconds']==60 and grant['supervisorWholeSeconds']==90 and len(grant['reviews'])==3
 assert sorted(r['role'] for r in grant['reviews'])==['gameplay','technical','visual']
 for ref in grant['reviews']:
  review=record(ref['path'],ref['sha256']);assert ref['accepted'] is True and review['accepted'] is True and review['sourceSealSHA256']==grant['sourceSealSHA256']
 stage_inodes=set()
 for config in expected['runtimes']:
  freeze=record(config['freezePath'],config['freezeSHA256']);manifest=record(config['stageManifestPath'],config['stageManifestSHA256']);authority=record(config['stageAuthorityPath'],config['stageAuthoritySHA256'])
  for row in [freeze,manifest]:
   for key in ['stage','sourceDigest','outputsDigest','inputCount','outputCount']:assert row[key]==config[key]
  assert manifest['schema']=='regular-file-stage-v1' and manifest['historicalMetadataRestored'] is False
  assert authority['schema']=='recovered-stage-authority-v1' and authority['stage']==config['stage'] and authority['acceptedByteExactReconstruction'] is True and authority['actualFreshBuild']==config['authorityActualFreshBuild']
  assert authority['historicalMetadataRestored'] is False and authority['artDefaultOrFunAccepted'] is False
  record(str(pathlib.Path(config['stageAuthorityPath']).parent/'BODY-COPY-RECEIPT.json'),authority['bodyCopyReceiptSHA256'])
  assert authority['freezeSHA256']==config['freezeSHA256'] and authority['stageManifestSHA256']==config['stageManifestSHA256']
  review=record(config['stageReviewPath'],config['stageReviewSHA256']);assert review['accepted'] is True
  if config['role']=='retainedB':
   assert review['decision']=='ACCEPT_EXACT_NEW_REGULAR_FILE_STATIC_RECONSTRUCTION_ONLY' and review['newRuntimeFreezeSHA256']==config['freezeSHA256'] and review['newStageManifestSHA256']==config['stageManifestSHA256'] and review['newRootAuthoritySHA256']==config['stageAuthoritySHA256']
   assert review['sourceDigest']==config['sourceDigest'] and review['outputsDigest']==config['outputsDigest'] and review['exactSource104Verified'] is True and review['exactOutputs70Verified'] is True and review['artDefaultGameplayFunApproved'] is False
   audit=record(str(pathlib.Path(config['stageReviewPath']).parent/'AUDIT.json'),review['fullAuditSHA256']);assert audit['stage']==config['stage'] and audit['inputCount']==104 and audit['outputCount']==70
  else:assert review['stage']==config['stage'] and review['freezeSHA256']==config['freezeSHA256'] and review['stageManifestSHA256']==config['stageManifestSHA256']
  membership={**freeze['inputs'],**{'dist/'+k:v for k,v in freeze['outputs'].items()}}
  assert set(manifest['files'])==set(membership) and len(freeze['inputs'])==config['inputCount'] and len(freeze['outputs'])==config['outputCount']
  actual=[]
  for dirpath,dirs,files in os.walk(config['stage']):
   assert not any(pathlib.Path(dirpath,name).is_symlink() for name in dirs+files)
   actual.extend(str(pathlib.Path(dirpath,name).relative_to(config['stage'])) for name in files)
  assert set(actual)==set(membership)
  for rel,pin in manifest['files'].items():
   assert not rel.startswith('/') and not any(x in ['','..','.'] for x in rel.split('/')) and pin['sha256']==membership[rel];assert pin['nlink']==1 and isinstance(pin['mtimeNs'],str) and isinstance(pin['ctimeNs'],str);identity(config['stage']+'/'+rel,pin)
   key=(str(pin['dev']),str(pin['ino']));assert key not in stage_inodes;stage_inodes.add(key)
 assert grant['stages']==[{k:r[k] for k in ['stage','freezeSHA256','stageManifestSHA256','stageAuthoritySHA256']} for r in expected['runtimes']]
 dependencies=record(expected['dependencies']['path'],expected['dependencies']['sha256']);assert dependencies['schema']=='installed-dependency-identities-v1' and dependencies['packageVersion']=='1.62.0' and dependencies['nodeVersion']=='v24.19.0'
 for key in ['modulePath','nodePath','browserExecutablePath']:assert dependencies[key]==expected['dependencies'][key]
 for pin in dependencies['files']:identity(pin['path'],pin)
 return grant
