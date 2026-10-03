import ast,base64,gzip,hashlib,json,resource,shutil,signal,subprocess,sys,yaml
from pathlib import Path
resource.setrlimit(resource.RLIMIT_AS,(64*1024**2,64*1024**2));resource.setrlimit(resource.RLIMIT_CPU,(25,25));signal.alarm(40)
P=Path('/workspace/scratch/empty-intent-fresh-ci-source-r10');B=P.parent/'empty-intent-fresh-ci-source-r9';O=Path(__file__).parent
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return {'bytes':len(b),'sha256':sha(b)}
def pins(p):
 r={}
 for f in p.rglob('*'):
  assert not f.is_symlink()
  if f.is_file():r[f.relative_to(p).as_posix()]=pin(f)
 return r
host=int(next(l.split()[1] for l in Path('/proc/meminfo').read_text().splitlines() if l.startswith('MemAvailable:')))*1024
maximum=Path('/sys/fs/cgroup/memory.max').read_text().strip();current=int(Path('/sys/fs/cgroup/memory.current').read_text());headroom=host if maximum=='max' else min(host,int(maximum)-current)
assert headroom>=(64+512)*1024**2 and shutil.disk_usage(O).free>=24*1024**2
before=pins(P);parent=pins(B);negative=pins(O/'actual-negative');closurepin=pin(O/'FIXTURE-CLOSURE-CHECKS.json')
assert len(sys.argv)==2 and len(sys.argv[1])==64 and before['SOURCE-SEAL.json']['sha256']==sys.argv[1]
s=json.loads((P/'SOURCE-SEAL.json').read_bytes());m=json.loads((P/'MANIFEST.json').read_bytes())
assert s['manifest']==before['MANIFEST.json'] and s['files']==m['files']=={k:v for k,v in before.items() if k not in ('MANIFEST.json','SOURCE-SEAL.json')}
size=sum(v['bytes'] for v in before.values());assert size==s['inclusiveFamilyBytes']==m['inclusiveFamilyBytes']<=s['sourceCapBytes']==2097152
assert parent['SOURCE-SEAL.json']['sha256']=='59cd0e4c7fb4caf8996650e78798c7ef57317cef3238747a2ed7aef5c18c18ed'
inverse=json.loads(gzip.decompress((P/'R10-INVERSE.json.gz').read_bytes()));assert set(inverse['files'])==set(parent)
recovered={}
for name,row in inverse['files'].items():
 b=(P/row['exactCurrentFile']).read_bytes() if 'exactCurrentFile' in row else base64.b64decode(row['originalBase64'],validate=True)
 assert b==(B/name).read_bytes() and {'bytes':len(b),'sha256':sha(b)}==parent[name]=={k:row[k] for k in ('bytes','sha256')};recovered[name]=parent[name]
assert sum(v['bytes'] for v in recovered.values())==578687
old=(B/'runner.py').read_text();new=(P/'runner.py').read_text();om=json.loads((B/'METADATA.json').read_bytes());nm=json.loads((P/'METADATA.json').read_bytes())
fixtureProof=json.loads((O/'FIXTURE-CLOSURE-CHECKS.json').read_bytes());fixtures=fixtureProof['fixtures'];newpaths=set(fixtures)
assert len(nm['source'])==98 and len(nm['support'])==32 and len(nm['blobPins'])==55
assert set(nm)==set(om) and sorted(k for k in nm if nm[k]!=om[k])==['blobPins','support']
assert [r for r in nm['support'] if r['path'] not in newpaths]==om['support']
assert [r for r in nm['blobPins'] if r['gitPath'] not in newpaths]==om['blobPins'] and nm['blobPins'][-3:]==om['blobPins'][-3:]
assert len({r['path'] for r in nm['source']+nm['support']})==130
for row in nm['support']:
 if row['path'] in newpaths:
  original=fixtures[row['path']];assert row=={'path':row['path'],'bytes':original['bytes'],'sha256':original['sha256'],'blob':original['sha256']}
for row in nm['blobPins']:
 if row['gitPath'] in newpaths:
  original=fixtures[row['gitPath']];assert row=={'gitPath':row['gitPath'],'bytes':original['bytes'],'sha256':original['sha256'],'gitBlobSHA1':original['gitBlobSHA1']}
assert len(nm['blobPins'][:-3])==52 and sum(r['bytes'] for r in nm['blobPins'])==sum(r['bytes'] for r in om['blobPins'])+20772
def constants(text):
 return {n.targets[0].id:ast.literal_eval(n.value) for n in ast.parse(text).body if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name) and n.targets[0].id in ('META_SHA','META_LITERAL')}
oc=constants(old);nc=constants(new)
assert nc['META_SHA']==before['METADATA.json']['sha256'] and gzip.decompress(base64.b64decode(nc['META_LITERAL'],validate=True))==(P/'METADATA.json').read_bytes()
changes=[('len(m["support"]) == 30','len(m["support"]) == 32'),('len(m["blobPins"]) == 53','len(m["blobPins"]) == 55'),('}) == 128','}) == 130'),('"expected": 53','"expected": 55'),('len(rows)==53','len(rows)==55'),('"supportFiles":30','"supportFiles":32'),('the 128 pinned','the 130 pinned'),('exact128 membership','exact130 membership'),('"supportCount":30','"supportCount":32')]
expected=old.replace(oc['META_LITERAL'],nc['META_LITERAL']).replace(oc['META_SHA'],nc['META_SHA'])
for a,b in changes:
 assert a in expected,(a,'absent');expected=expected.replace(a,b)
assert expected==new
def block(t):return "          source = r'''"+t.replace('\n','\n          ')+"'''\n"
ow=(B/'rebuild-opening-baseline.yml').read_text();nw=(P/'rebuild-opening-baseline.yml').read_text()
assert ow.count(block(old))==1 and ow.replace(block(old),block(new)).replace(sha(old.encode()),sha(new.encode())).replace(oc['META_SHA'],nc['META_SHA'])==nw
assert nw.replace(block(new),block(old)).replace(sha(new.encode()),sha(old.encode())).replace(nc['META_SHA'],oc['META_SHA'])==ow
def funcs(t):return {n.name:ast.get_source_segment(t,n) for n in ast.parse(t).body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
a=funcs(old);b=funcs(new);assert set(a)==set(b) and sorted(k for k in a if a[k]!=b[k])==['acquire','assemble','membership','metadata']
for name in ('phase','run_phase','child_env','disk_inventory','native_inventory','fetch_blob','member_header','exclusive','verify_pin','safe_path'):
 assert a[name]==b[name]
grammar=[];shells=[];embedded=[]
for f in P.glob('*.py'):compile(ast.parse(f.read_bytes()),str(f),'exec');grammar.append(f.name)
for step in yaml.load(nw,Loader=yaml.BaseLoader)['jobs']['fresh-baseline']['steps']:
 if 'run' not in step:continue
 run=step['run'];r=subprocess.run(['bash','-n'],input=run,text=True,capture_output=True,timeout=5);assert r.returncode==0,(step['id'],r.stderr);shells.append(step['id'])
 if "<<'PY'\n" in run:
  text=run[run.index("<<'PY'\n")+7:run.rindex('\nPY')];compile(ast.parse(text),step['id'],'exec');embedded.append({'step':step['id'],'sha256':sha(text.encode())})
assert len(shells)==9 and len(embedded)==2
assert before==pins(P) and parent==pins(B) and negative==pins(O/'actual-negative') and closurepin==pin(O/'FIXTURE-CLOSURE-CHECKS.json')
receipt={'status':'PASS_EXACT_R10_SOURCE_ONLY','sourceSeal':before['SOURCE-SEAL.json'],'manifest':before['MANIFEST.json'],'files':before,'inclusiveSourceBytes':size,'sourceCapBytes':2097152,'completeR9Inverse':recovered,'completeR9InverseBytes':578687,'onlyChangedFunctions':['metadata','acquire','assemble','membership'],'completeRunnerExactAllowlistedCountsAndMetaReplacement':True,'completeWorkflowForwardReverseExact':True,'intentionalCounts':{'source':98,'support':32,'stage':130,'directBlobs':52,'allBlobs':55},'originalMetadataOtherFieldsAndExistingRowsUnchanged':True,'twoFixturePrimaryProof':closurepin,'fixtureBodiesSHA256AndGitSHA1Verified':True,'phaseResourcesCommandsAllOtherGuardsExactR9':True,'pythonAST':sorted(grammar),'bashN':shells,'embeddedPythonAST':embedded,'negativeGate':negative['GATE.json'],'ordinary':{'workCapBytes':64*1024**2,'reserveBytes':512*1024**2,'initialHeadroom':headroom,'selfPeakRSS':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,'cpuSeconds':25,'wallAlarmSeconds':40},'mainNetworkNpmBuildTestsBrowserExecution':False,'allFrozenPacketsUnchanged':True}
with (O/'SOURCE-CHECKS.json').open('x') as f:f.write(json.dumps(receipt,sort_keys=True,separators=(',',':'))+'\n')
print(json.dumps({'status':receipt['status'],'sourceBytes':size,'parentFiles':len(recovered),'selfPeakRSS':receipt['ordinary']['selfPeakRSS']}))
