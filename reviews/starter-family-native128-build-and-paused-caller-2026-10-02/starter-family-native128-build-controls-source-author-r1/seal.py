import os,json,gzip,hashlib,ast,re,resource
from pathlib import Path
resource.setrlimit(resource.RLIMIT_DATA,(24*1048576,24*1048576));P=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def r(q):
 f=os.open(q,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME)
 with os.fdopen(f,'rb') as s:return s.read()
def save(n,x):
 b=x if isinstance(x,bytes) else (json.dumps(x,separators=(',',':'))+'\n').encode()
 with (P/n).open('xb') as f:f.write(b);f.flush();os.fsync(f.fileno())
 assert r(P/n)==b;return sha(b)
def inverse_patch(new,delta):
 original=new.splitlines(True);lines=delta.splitlines(True);cursor=0;result=[];i=2
 while i<len(lines):
  m=re.match(r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@',lines[i]);assert m
  start=int(m[3])-1;assert start>=cursor;result.extend(original[cursor:start]);cursor=start;i+=1
  while i<len(lines) and not lines[i].startswith('@@ '):
   row=lines[i];assert row[0] in ' +-'
   if row[0] in ' +':assert original[cursor]==row[1:];cursor+=1
   if row[0] in ' -':result.append(row[1:])
   i+=1
 result.extend(original[cursor:]);return ''.join(result)
plan=json.loads(r(P/'PLAN.json'));proof=json.loads(r(P/'PROOF.json'))
for n in ['assemble.py','bounded-build.py','finalize.py','strict-build-runner.mjs']:
 b=r(P/n);x=proof[n];assert sha(b)==x['candidateSHA256'];delta=gzip.decompress(r(P/(n+'.diff.gz'))).decode();assert sha(r(P/(n+'.diff.gz')))==x['deltaGzipSHA256'];original=r(x['original']['path']);assert sha(original)==x['original']['sha256'];assert inverse_patch(b.decode(),delta).encode()==original
 if n.endswith('.py'):ast.parse(b)
assert len(plan['expectedInputs'])==104 and len(plan['expectedHeldOutputs'])==65 and len(set(plan['expectedAliasKeys']))==121
assert not Path(plan['stage']).exists() and not Path(plan['strictBuildEvidence']).exists()
notes=b'''SOURCE-only future build controls. Exact independent starter source gate d9e11 and Root materialization grant5f57/four regular outputs bound. Frozen donor76e5/2547 has98/64 and115 alias leaves. Proposed stage has four replacements/six private new PNG input copies, full104 input map and source65b31;65 art/audio output bodies plusfive fresh Vite/provenance/CREDITS/index outputs yield70 predicted. The old view JSON is replaced; other58 old retained output bodies remain exact. Actual source/body/support30 and donor chains will be streamed in Root assembly, then measured121 alias-domain freeze. New PNG inputs are private; their output aliases point to fresh public copies. All13 build resource checks unchanged; one384+512 strict installed tsc/Vite run, heap256,55stop/60whole/disk64. Assembly/finalize64+512. Current cue OFF/query flags preserved; no canonical composition or scene/art/default/animation/fun acceptance. No Node/PIL/build/browser/stage/assets copy occurred during authoring. All four saved gzip diff inverses independently parsed from their hunks here and return exact donor controls; Python source AST parses only. Future commands and activation schema in ARGV. RootGO and exact independent controlsPlanSHA256 gate required before assembly. Original source/materialization/failure histories remain external and pinned.\n'''
save('README.txt',notes)
manifest=[]
for q in sorted(P.iterdir()):
 if q.is_file():b=r(q);manifest.append({'name':q.name,'bytes':len(b),'sha256':sha(b)})
manifestSHA=save('MANIFEST.json',manifest)
resources=[]
for n in ['INSPECT-GUARD','PREPARE-GUARD']:
 q=P/n/'RESULT.json';x=json.loads(r(q));assert x['exit_code']==0 and x['failure'] is None and x['memory_events_before']==x['memory_events_after'];resources.append({'path':str(q),'sha256':sha(r(q)),'samples':len(x['samples']),'minHeadroom':min(t['headroom'] for t in x['samples'])})
x={'scope':'SOURCE_CONTROLS_PREPARED_PENDING_INDEPENDENT_REVIEW_ROOT_GO','controlsPlanSHA256':sha(r(P/'PLAN.json')),'manifestSHA256':manifestSHA,'candidateSourceDigest':plan['expectedSourceDigest'],'predictedInputCount':104,'predictedOutputCount':70,'derivedAliasCount':121,'fourExactSavedDiffInverses':True,'all13BuildResourceChecksUnchanged':True,'actualStageBuild':False,'capLogicalBytes':131072,'resources':resources,'rssKiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'closureRequiresSealGuardNormalReturn':True}
assert sum(q.stat().st_size for q in P.rglob('*') if q.is_file())+len(json.dumps(x))+3500<=131072
finalSHA=save('FINAL-SEAL.json',x);print(json.dumps({'finalSHA256':finalSHA,'planSHA256':x['controlsPlanSHA256'],'manifestSHA256':manifestSHA,'rssKiB':x['rssKiB'],'allFourSavedDiffInverses':True}))
