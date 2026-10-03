import hashlib,json,posixpath,re,resource,signal
from pathlib import Path
resource.setrlimit(resource.RLIMIT_AS,(64*1024**2,64*1024**2));resource.setrlimit(resource.RLIMIT_CPU,(20,20));signal.alarm(30)
P=Path('/workspace/scratch/opening-ci-original-test-fixtures-root-r1');S=Path('/workspace/scratch/empty-intent-source-recovered-stage-r1');O=Path(__file__).parent
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return {'bytes':len(b),'sha256':sha(b)}
before={f.relative_to(P).as_posix():pin(f) for f in P.rglob('*') if f.is_file()}
data=json.loads((P/'FIXTURE-PINS.json').read_bytes());carrier=json.loads((P/'CARRIER.json').read_bytes())
assert data['sourceRef']==carrier['sourceRef']=='fbb617eff4b6ed04ea866ed57751ba23d8b6097d'
fixtures={}
for row in data['files']:
 b=Path(row['bodyPath']).read_bytes();assert pin(Path(row['bodyPath']))=={k:row[k] for k in ('bytes','sha256')}
 assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==row['gitBlobSHA1']
 assert next(r['content'] for r in carrier['files'] if r['path']==row['path']).encode()==b
 json.loads(b);fixtures[row['path']]=row
assert len(fixtures)==2 and sum(r['bytes'] for r in fixtures.values())==20772
m=json.loads(Path('/workspace/scratch/empty-intent-fresh-ci-source-r9/METADATA.json').read_bytes())
expected={r['path']:r for r in m['source']+m['support']};tests=sorted(k for k in expected if re.fullmatch('tests/[^/]+\.test\.ts',k));assert len(tests)==8
def resolve(name,parent):
 path=posixpath.normpath(posixpath.join(posixpath.dirname(parent),name))
 for k in (path,path+'.ts',path+'.mjs',path+'.js',path+'/index.ts'):
  if k in expected:return k
 raise AssertionError((parent,name,path))
seen={};todo=list(tests);external=set();edges=[];reads=[]
while todo:
 name=todo.pop()
 if name in seen:continue
 body=(S/name).read_bytes();assert {'bytes':len(body),'sha256':sha(body)}=={k:expected[name][k] for k in ('bytes','sha256')}
 text=body.decode();seen[name]=pin(S/name)
 for match in re.finditer(r'''(?:\bfrom\s*|\bimport\s*\(\s*|\bimport\s*)["']([^"']+)["']''',text):
  spec=match[1]
  if not spec.startswith('.'):external.add(spec);continue
  child=resolve(spec,name);edges.append({'from':name,'specifier':spec,'to':child});todo.append(child)
 for match in re.finditer(r'''new URL\(\s*["']([^"']+)["']\s*,\s*import\.meta\.url''',text):
  spec=match[1];path=posixpath.normpath(posixpath.join(posixpath.dirname(name),spec))
  reads.append({'from':name,'literalURL':spec,'path':path,'inOldStage':path in expected,'isMissingFixture':path in fixtures})
  assert path in expected or path in fixtures,(name,path)
  if path in expected and path.endswith(('.ts','.js','.mjs')):todo.append(path)
assert sorted({r['path'] for r in reads if r['isMissingFixture']})==sorted(fixtures)
world=(S/'tests/world-rng-v0.5.test.ts').read_text()
hashargs=re.findall(r'''\bhash\(["']([^"']+)["']\)''',world)
assert hashargs==['fixtures/v0.4/engine.ts','fixtures/v0.4/content.ts']
for arg in hashargs:assert resolve(arg,'tests/world-rng-v0.5.test.ts') in seen
assert external<={'node:test','node:assert/strict','node:fs','node:crypto','node:url','esbuild'}
assert before=={f.relative_to(P).as_posix():pin(f) for f in P.rglob('*') if f.is_file()}
r={'status':'PASS_EXACT_TWO_PRIMARY_FIXTURES_STATIC_TEST_IMPORT_CLOSURE','fixturePins':pin(P/'FIXTURE-PINS.json'),'carrier':pin(P/'CARRIER.json'),'fixtures':fixtures,'originalTests':tests,'closureBodies':seen,'importEdges':edges,'literalURLReads':reads,'worldHashHelperLiteralArguments':hashargs,'externalImports':sorted(external),'qualification':'Static literal imports (including relative dynamic/type imports), bundle entry and literal URLs traced; world hash helper two literal args checked. This is source inspection, not execution or a proof of arbitrary dynamically computed future reads. audio data URL derives inspected esbuild entry; package esbuild remains original locked dependency. Two fixture bodies are primary retained UTF8 bodies from pinned fbb carrier, not manufactured.','ordinaryWorkCapBytes':64*1024**2,'reserveBytes':512*1024**2,'selfPeakRSS':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,'oldBodiesUnchanged':True,'gameNetworkMainBuildTestsExecuted':False}
with (O/'FIXTURE-CLOSURE-CHECKS.json').open('x') as f:f.write(json.dumps(r,sort_keys=True,separators=(',',':'))+'\n')
print(json.dumps({'status':r['status'],'tests':len(tests),'closureBodies':len(seen),'fixtureBytes':20772,'fixturePins':r['fixturePins']}))
