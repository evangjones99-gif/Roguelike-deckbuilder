import resource
resource.setrlimit(resource.RLIMIT_DATA,(24*1048576,24*1048576))
import os,pathlib,json,hashlib
P=pathlib.Path(__file__).parent;E=pathlib.Path('/workspace/scratch/coherent-native128-pixel-comparison-actual-r4');S=pathlib.Path('/workspace/scratch/coherent-native128-pixel-stage-r4');pins={}
def read(q):
 fd=os.open(pathlib.Path(q).resolve(strict=True),os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW)
 try:
  with os.fdopen(fd,'rb',closefd=False) as f:return f.read()
 finally:os.close(fd)
def sha(q):return hashlib.sha256(read(q)).hexdigest()
def pin(q,h=None):
 value=sha(q)
 if h:assert value==h
 pins[str(q)]={'sha256':value,'bytes':q.stat().st_size};return value
def doc(q):return json.loads(read(q))
for q in sorted(E.iterdir()):assert q.is_file();pin(q)
result=doc(E/'RESULT.json');v=doc(E/'VISUAL-RESULT.json');progress=doc(E/'VISUAL-PROGRESS.json');ad=doc(E/'ADMISSION.json')
assert result['exit_code']==2 and result['failure'] is None and not result['cleanup_errors'] and not result['normal_wait']
assert result['checks']['driver_rc0'] is False and all(value for key,value in result['checks'].items() if key!='driver_rc0')
assert v['browser']==v['server']=='NOT_LAUNCHED' and not v['mechanicalPass']
for key in ['actions','captures','contexts','pixelEvents','pageErrors']:assert v[key]==[]
assert v['failure']==progress['failure']=="Error: ELOOP: too many symbolic links encountered, open '/workspace/scratch/coherent-native128-pixel-stage-r4/desktop/audio-lifecycle.cjs'"
assert v['wholeElapsedMs']==24 and not (E/'BYTE-AUDIT-before.json').exists() and not (E/'SERVED-BYTE-AUDIT.json').exists() and not any(q.suffix=='.jpg' for q in E.iterdir())
events=[json.loads(x) for x in read(E/'LIFECYCLE.jsonl').decode().splitlines()];failure=[json.loads(x) for x in read(E/'FAILURE.jsonl').decode().splitlines()]
assert len(events)==2 and events[0]['event']=='close initiated' and events[1]['event']=='normal browser and server close' and events[1]['errors']==[] and len(failure)==1
assert result['memory_events_before']==result['memory_events_after']
assert ad['admitted'] and ad['work']==896*1048576 and ad['reserve']==512*1048576 and result['initial']['headroom']>=1408*1048576 and result['initial']['free']>=70*1048576
for row in result['samples']:
 assert row['maximum']==result['initial']['maximum'] and row['current']-result['initial']['current']==row['delta']<=ad['work'] and row['headroom']>=ad['reserve'] and row['free']>=1048576
final=result['final'];assert final['maximum']==result['initial']['maximum'] and final['headroom']>=ad['reserve'] and final['current']-result['initial']['current']<=ad['work'] and result['whole_seconds']<90
assert result['live_remaining']==result['tracked_zombies']==result['post_wait_descendants']=={}
launch=doc(E/'OWNED-LAUNCH.json');observed=[]
for pid,row in result['owned_observed'].items():
 assert launch['identities'][pid]['starttime']==row['starttime'];q=pathlib.Path('/proc')/pid/'stat';current=None
 if q.exists():
  raw=q.read_text();x=raw[raw.rindex(')')+2:].split();current={'starttime':x[19],'state':x[0]}
 assert current is None or current['starttime']!=row['starttime'] or current['state']=='Z'
 observed.append({'pid':pid,'starttime':row['starttime'],'current':current})
caps=doc(E/'FINAL-PACKET-CAPS.json');assert caps['jpegBytes']==0 and caps['pass']
freezePath=pathlib.Path('/workspace/scratch/coherent-native128-strict-build-root-r4/final-seal-r1/RUNTIME-FREEZE.json');pin(freezePath,'e8d6e3942f8b1b32e00bd3846f2587b065b6c230600c9e5c25f0da6ff4fecd21');f=doc(freezePath)
assemblyPath=S/'.control/ASSEMBLY.json';pin(assemblyPath,f['assemblySHA256']);assembly=doc(assemblyPath);assert assembly['inputs']==f['inputs']
aliases=[];smallBodies=[]
for domain,root,rows in [('input',S,f['inputs']),('output',S/'dist',f['outputs'])]:
 for name,h in rows.items():
  q=root/name
  if q.is_symlink():
   target=q.resolve(strict=True);assert q.stat().st_size==target.stat().st_size
   assert (domain=='input' and name.startswith(('public/','desktop/'))) or (domain=='output' and name.startswith(('art/','audio/')))
   donor=pathlib.Path(assembly['baselineStage'])/('dist' if domain=='output' else '')/name
   assert target==donor.resolve(strict=True)
   aliases.append({'domain':domain,'path':name,'target':str(target),'expectedSHA256':h,'bytes':target.stat().st_size})
  media=name.endswith(('.png','.wav')) or name.startswith(('public/art/','public/audio/','art/','audio/'))
  if not media:assert sha(q)==h;smallBodies.append({'domain':domain,'path':name,'sha256':h})
q=S/'desktop/audio-lifecycle.cjs';assert q.is_symlink() and sha(q)==f['inputs']['desktop/audio-lifecycle.cjs']
driverPath=pathlib.Path('/workspace/scratch/coherent-native128-actual-caller-author-r4/driver-paired-r1.mjs');pin(driverPath);driver=read(driverPath).decode()
assert "fs.constants.O_RDONLY|fs.constants.O_NOATIME|fs.constants.O_NOFOLLOW" in driver and "hashFile(path.join(stage,rel))" in driver
assert driver.index("await audit('before')")<driver.index('server=http.createServer')<driver.index('browser=await chromium.launch')
rss=int(next(x.split()[1] for x in pathlib.Path('/proc/self/status').read_text().splitlines() if x.startswith('VmHWM:')))*1024;assert rss<24*1048576
proof={'decisionBasis':'Prebrowser byte-audit method rejects deliberate final-leaf symlink using O_NOFOLLOW; not a game or visual trial outcome','actualFiles':len(pins)-3,'actualAllSmallFilePins':pins,'driverBrowserServerNotLaunched':True,'zeroContextsActionsCaptures':True,'driverWholeMs':24,'outerWholeSeconds':result['whole_seconds'],'outerExitCode':2,'outerNormalWait':False,'checks':result['checks'],'resourceSampleRows':len(result['samples']),'initial':result['initial'],'final':result['final'],'observedMaxDelta':max(x['delta'] for x in result['samples']),'minHeadroom':min(x['headroom'] for x in result['samples']),'eventsStable':True,'observedPIDStartPairs':observed,'allObservedNonlive':True,'ownedClosureLimits':'Only sampled observed PID/start pairs, no exhaustive unobserved-process/global-FD proof','caps':caps,'stageFullFrozenMapsUnchanged':{'inputs':len(f['inputs']),'outputs':len(f['outputs']),'sourceDigest':f['sourceDigest'],'outputsDigest':f['outputsDigest']},'smallCurrentNonmediaBodies':smallBodies,'fullKnownHeldLeafAliasInventory':aliases,'failedLeafResolvedBodyExact':True,'mediaBodiesNotRehashed':True,'noOSReadOnlyProtectionClaim':True,'noGameAppExecutedSupportedBySourceOrderAndActualEmptyLifecycle':True,'newCallerRepairScope':'Permit only assembly-map-bound held leaf aliases resolving to exact expected frozen donor destinations; hash resolved regular files with NOATIME/NOFOLLOW. Retain strict non-alias caller controls/captures paths. Audit complete known input/output aliases, not only the first desktop leaf.','ownVmHWMBytes':rss,'sourceReadOnlyScope':True}
with (P/'PROOF.json').open('xb') as fp:fp.write((json.dumps(proof,separators=(',',':'))+'\n').encode());fp.flush();os.fsync(fp.fileno())
print(json.dumps({'prebrowserFailureVerified':True,'knownHeldAliases':len(aliases),'smallNonmediaBodies':len(smallBodies),'ownVmHWMBytes':rss}))
