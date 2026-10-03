import ast,base64,gzip,hashlib,json,resource,shutil,signal,subprocess,yaml
from pathlib import Path
resource.setrlimit(resource.RLIMIT_AS,(64*1024**2,64*1024**2))
resource.setrlimit(resource.RLIMIT_CPU,(25,25));signal.alarm(40)
P=Path('/workspace/scratch/empty-intent-fresh-ci-source-r9')
B=Path('/workspace/scratch/empty-intent-fresh-ci-source-r8')
O=Path(__file__).parent
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return {'bytes':len(b),'sha256':sha(b)}
def pins(p):
 result={}
 for f in p.rglob('*'):
  assert not f.is_symlink()
  if f.is_file():result[f.relative_to(p).as_posix()]=pin(f)
 return result
host=int(next(l.split()[1] for l in Path('/proc/meminfo').read_text().splitlines() if l.startswith('MemAvailable:')))*1024
maximum=Path('/sys/fs/cgroup/memory.max').read_text().strip();current=int(Path('/sys/fs/cgroup/memory.current').read_text())
headroom=host if maximum=='max' else min(host,int(maximum)-current)
assert headroom>=(64+512)*1024**2 and shutil.disk_usage(O).free>=24*1024**2
before=pins(P);parent=pins(B);negative=pins(O/'actual-negative');prior=pins(B.parent/'empty-intent-fresh-ci-technical-r8')
assert before['SOURCE-SEAL.json']['sha256']=='59cd0e4c7fb4caf8996650e78798c7ef57317cef3238747a2ed7aef5c18c18ed'
assert before['MANIFEST.json']['sha256']=='58b9091139133b82f5398dbe01fa07c38ed7a439c85bfe760fffa4a2a80ed3a9'
s=json.loads((P/'SOURCE-SEAL.json').read_bytes());m=json.loads((P/'MANIFEST.json').read_bytes())
assert s['manifest']==before['MANIFEST.json']
assert s['files']==m['files']=={k:v for k,v in before.items() if k not in ('MANIFEST.json','SOURCE-SEAL.json')}
assert sum(v['bytes'] for v in before.values())==s['inclusiveFamilyBytes']==m['inclusiveFamilyBytes']==578687<=s['sourceCapBytes']==1048576
assert parent['SOURCE-SEAL.json']['sha256']=='06a21194db443ea1d03165ee5b69e1a378ce5120bfee466c52ff9a9ff8644c35'
assert prior['GATE.json']['sha256']=='11b8facb99e9957da95a24835eb0a86ef73ff97e360be03ee6705b0d2c29739e'
assert json.loads((B.parent/'empty-intent-fresh-ci-technical-r8/GATE.json').read_bytes())['verdict']=='ACCEPT_SOURCE_ONLY'
inverse=json.loads(gzip.decompress((P/'R9-INVERSE.json.gz').read_bytes()))
assert set(inverse['files'])==set(parent) and inverse['parentBytes']==sum(v['bytes'] for v in parent.values())==464060
recovered={}
for name,row in inverse['files'].items():
 b=(P/row['exactCurrentFile']).read_bytes() if 'exactCurrentFile' in row else base64.b64decode(row['originalBase64'],validate=True)
 assert b==(B/name).read_bytes() and {'bytes':len(b),'sha256':sha(b)}==parent[name]=={k:row[k] for k in ('bytes','sha256')}
 recovered[name]=parent[name]
changed=sorted(k for k in parent if parent[k]!=before.get(k))
assert changed==['MANIFEST.json','README.md','SOURCE-SEAL.json','rebuild-opening-baseline.yml','runner.py']
old=(B/'runner.py').read_text();new=(P/'runner.py').read_text()
oldcall='run_phase(root,name,["npm","test"],55,60,384*MIB)';newcall=oldcall.replace('384*MIB','768*MIB')
assert old.count(oldcall)==1 and old.replace(oldcall,newcall)==new and new.replace(newcall,oldcall)==old
def functions(t):return {n.name:ast.get_source_segment(t,n) for n in ast.parse(t).body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
a=functions(old);b=functions(new)
assert set(a)==set(b) and [k for k in a if a[k]!=b[k]]==['phase']
def block(t):return "          source = r'''"+t.replace('\n','\n          ')+"'''\n"
ow=(B/'rebuild-opening-baseline.yml').read_text();nw=(P/'rebuild-opening-baseline.yml').read_text()
assert ow.count(block(old))==1 and ow.replace(block(old),block(new)).replace(sha(old.encode()),sha(new.encode()))==nw
assert nw.replace(block(new),block(old)).replace(sha(new.encode()),sha(old.encode()))==ow
calls=[]
phase=next(n for n in ast.parse(new).body if isinstance(n,ast.FunctionDef) and n.name=='phase')
for n in ast.walk(phase):
 if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='run_phase':
  calls.append(ast.unparse(n))
assert 'run_phase(root, name, [\'npm\', \'test\'], 55, 60, 768 * MIB)' in calls
assert 'run_phase(root, name, [\'npm\', \'run\', \'build\'], 55, 60, 384 * MIB)' in calls
assert 'run_phase(root, name, [\'npm\', \'ci\', \'--ignore-scripts\', \'--no-audit\', \'--no-fund\'], 170, 180, 384 * MIB)' in calls
grammar=[];shells=[];embedded=[]
for f in P.glob('*.py'):
 compile(ast.parse(f.read_bytes()),str(f),'exec');grammar.append(f.name)
workflow=yaml.load(nw,Loader=yaml.BaseLoader)
for step in workflow['jobs']['fresh-baseline']['steps']:
 if 'run' not in step:continue
 run=step['run'];r=subprocess.run(['bash','-n'],input=run,text=True,capture_output=True,timeout=5)
 assert r.returncode==0,(step['id'],r.stderr)
 shells.append(step['id'])
 if "<<'PY'\n" in run:
  py=run[run.index("<<'PY'\n")+7:run.rindex('\nPY')]
  compile(ast.parse(py),step['id'],'exec');embedded.append({'step':step['id'],'sha256':sha(py.encode())})
assert len(shells)==9 and len(embedded)==2
actual=Path('/workspace/scratch/opening-ci-test-limit-failure-root-r1')
facts=json.loads((P/'ACTUAL-TEST-CAP-FAILURE.json').read_bytes())
assert facts['rootReceipt']['sha256']=='664cdc6ff808fb16a809201164ff5d93c556606d347f76daeee486a68a447fa3'
assert pin(actual/'ROOT-RECEIPT.json')=={k:facts['rootReceipt'][k] for k in ('bytes','sha256')}
for role,f in facts['facts'].items():
 p=actual/role/'members'
 assert pin(p/'test-closure.json')==f['testClosureIdentity'] and json.loads((p/'test-closure.json').read_bytes())==f['testClosure']
 for key,name in [('buildClosure','build-closure.json'),('nativeInventory06','native-inventory-06.json'),('testLog','test.log')]:assert pin(p/name)==f[key]
assert before==pins(P) and parent==pins(B) and prior==pins(B.parent/'empty-intent-fresh-ci-technical-r8') and negative==pins(O/'actual-negative')
receipt={'status':'PASS_EXACT_R9_SOURCE_ONLY','sourceSeal':before['SOURCE-SEAL.json'],'manifest':before['MANIFEST.json'],'files':before,'inclusiveSourceBytes':578687,'sourceCapBytes':1048576,'fullR8Reconstruction':recovered,'parentBytes':464060,'changedParentPaths':changed,'onlyFunctionalChange':oldcall+' -> '+newcall,'allOtherFunctionsConstantsAndMetadataExact':True,'workflowForwardAndReverseExact':True,'phaseCalls':calls,'pythonAST':sorted(grammar),'bashN':shells,'embeddedPythonAST':embedded,'inheritedGuardCases':'76 author cases retained; unchanged tested guard functions; no reruns claimed','negativeGate':negative['GATE.json'],'priorGate':prior['GATE.json'],'ordinary':{'workCapBytes':64*1024**2,'reserveBytes':512*1024**2,'initialHeadroom':headroom,'selfPeakRSS':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,'cpuSeconds':25,'wallAlarmSeconds':40},'sourceMethodMainNetworkNpmBuildTestsBrowserExecuted':False,'allFrozenPacketsUnchanged':True}
with (O/'SOURCE-CHECKS.json').open('x') as f:f.write(json.dumps(receipt,sort_keys=True,separators=(',',':'))+'\n')
print(json.dumps({'status':receipt['status'],'sourceBytes':578687,'parentFilesRecovered':len(recovered),'selfPeakRSS':receipt['ordinary']['selfPeakRSS']}))
