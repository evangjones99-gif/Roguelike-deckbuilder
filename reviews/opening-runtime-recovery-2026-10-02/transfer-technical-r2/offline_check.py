import ast,base64,hashlib,json,pathlib,re,types
P=pathlib.Path('/workspace/scratch/opening-runtime-transfer-source-r2');O=pathlib.Path('/workspace/scratch/opening-runtime-transfer-technical-r2')
source=(P/'acquire_pinned_runtime_bytes.py').read_text();tree=ast.parse(source);compile(tree,str(P/'acquire_pinned_runtime_bytes.py'),'exec')
names={'REPOSITORY','REF','WORKFLOW','RESPONSE_CAP','RECEIPT_CAP','PER_FILE_CAP','OUTPUT_CAP','ARTIFACT_CAP','ZIP_MARGIN','GROUP_BYTES','GROUP_COUNTS','PINSET_SHA256','RAW_PINSET','PINSET'}
safe=[n for n in tree.body if (isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in names for t in n.targets)) or (isinstance(n,ast.FunctionDef) and n.name in ['require','unique_object','validate_pinset','fetch_verified'])]
env={'base64':base64,'hashlib':hashlib,'json':json,'re':re};exec(compile(ast.fix_missing_locations(ast.Module(body=safe,type_ignores=[])),'offline_exact_source_functions','exec'),env)
env['validate_pinset']();pins=env['PINSET'];assert json.loads((P/'PINSET.json').read_bytes())==pins
git={r['path']:r for r in json.loads(pathlib.Path('/workspace/scratch/evidence-audit-resume-r1/tree.json').read_bytes())['tree']}
historical=json.loads((O/'HISTORICAL-CANONICAL-SHA256.json').read_bytes());checked=[]
for group,rows in pins.items():
 for r in rows:
  q=git[r['gitPath']];assert q['type']=='blob' and q['sha']==r['gitBlobSHA1'] and q['size']==r['bytes']
  if group=='canonical':assert historical[r['gitPath']]==r['sha256']
  checked.append({'gitPath':r['gitPath'],'metadataAndHistoricalHashPinVerified':True})
assert sum(r['bytes'] for r in pins['canonical'])==30524821 and sum(r['bytes'] for r in pins['containers'])==16177681
fixture=b'synthetic exact fixed-list blob\x00\xff';sha1=hashlib.sha1(b'blob '+str(len(fixture)).encode()+b'\0'+fixture).hexdigest();sha256=hashlib.sha256(fixture).hexdigest();pin={'bytes':len(fixture),'gitBlobSHA1':sha1,'sha256':sha256};url='https://api.github.com/repos/'+env['REPOSITORY']+'/git/blobs/'+sha1
good={'sha':sha1,'size':len(fixture),'encoding':'base64','url':url,'content':base64.b64encode(fixture).decode()};default_headers={'Content-Type':'application/json; charset=utf-8','Content-Encoding':'identity'};tests=[];env['RESPONSE_CAP']=1024
class FakeResponse:
 def __init__(self,body,status,headers):self.body=body;self.status=status;self.headers=headers;self.position=0;self.requests=[]
 def getheader(self,name,default=None):return self.headers.get(name,default)
 def read(self,n):self.requests.append(n);r=self.body[self.position:self.position+n];self.position+=len(r);return r
class FakeConnection:
 def __init__(self,*args,**kwargs):assert args==('api.github.com',443) and kwargs['timeout']==10;self.closed=False;self.calls=[];connections.append(self)
 def request(self,method,path,headers):assert method=='GET' and path=='/repos/'+env['REPOSITORY']+'/git/blobs/'+test_pin['gitBlobSHA1'];assert headers['Authorization']=='Bearer synthetic-token';self.calls.append((method,path))
 def getresponse(self):return response
 def close(self):self.closed=True
env['http']=types.SimpleNamespace(client=types.SimpleNamespace(HTTPSConnection=FakeConnection));env['ssl']=types.SimpleNamespace(create_default_context=lambda:object())
def check(name,payload=good,status=200,headers=None,accepted=False,pin_override=None,raw=None):
 global response,connections,test_pin
 test_pin={**pin,**(pin_override or {})};connections=[];body=raw if raw is not None else json.dumps(payload).encode();response=FakeResponse(body,status,{**default_headers,**(headers or {})})
 try:actual,count=env['fetch_verified'](test_pin,'synthetic-token');ok=True
 except (ValueError,TypeError,KeyError):ok=False
 assert ok==accepted,name;assert len(connections)==1 and connections[0].closed and len(connections[0].calls)==1;assert all(0<n<=65536 for n in response.requests)
 if ok:assert actual==fixture and count==len(body)
 tests.append({'name':name,'expectedAccepted':accepted,'observedAccepted':ok,'connectionClosed':True,'noRedirectOrRetry':True})
check('correct_exact_fixture',accepted=True)
check('LF_wrapping',payload={**good,'content':good['content'][:8]+'\n'+good['content'][8:]},accepted=True)
for status in [302,404,500]:check('HTTP_'+str(status),status=status)
for name,headers in [('wrongType',{'Content-Type':'text/html'}),('compressed',{'Content-Encoding':'gzip'}),('oversizeDeclared',{'Content-Length':'1025'}),('invalidDeclared',{'Content-Length':'oops'}),('truncated',{'Content-Length':'1000'}),('underDeclared',{'Content-Length':'1'})]:check(name,headers=headers)
for key,value in [('sha','0'*40),('size',float(len(fixture))),('size',len(fixture)+1),('encoding','utf-8'),('url','https://elsewhere.invalid/'),('content',good['content']+'\r'),('content',good['content']+'='),('content','!'+good['content'][1:])]:check('wrong_'+key+'_'+str(value)[:8],payload={**good,key:value})
check('wrong_SHA256',pin_override={'sha256':'0'*64})
changed=bytes([fixture[0]^1])+fixture[1:];check('changed_same_size_body',payload={**good,'content':base64.b64encode(changed).decode()})
check('response_cap_plus_one',raw=b'x'*1025)
check('duplicateJSON',raw=b'{"sha":"x","sha":"y"}')
original=env['RAW_PINSET'];env['RAW_PINSET']=original+' '
try:env['validate_pinset']();raise AssertionError('Changed pinset accepted')
except ValueError:tests.append({'name':'changed_literal_pinset','rejected':True})
env['RAW_PINSET']=original
workflow=(P/'recover-opening-evidence.yml').read_text();embedded=workflow.split("python3 -I -B - <<'PY'\n",1)[1].split('          PY\n',1)[0];embedded=''.join(l[10:] for l in embedded.splitlines(keepends=True));assert embedded==source
receipt={'sourceOnly':True,'grammarPassed':True,'literalPinsetValidationPassed':True,'fixedPinsAgainstGitMetadataAndCanonicalHistoricalHashes':checked,'pinsetSHA256':env['PINSET_SHA256'],'counts':{k:len(v) for k,v in pins.items()},'groupBytes':env['GROUP_BYTES'],'reservedZipMarginBytes':env['ZIP_MARGIN'],'offlineTests':tests,'embeddedSourceByteExact':True,'methodSHA256':hashlib.sha256(source.encode()).hexdigest(),'workflowSHA256':hashlib.sha256(workflow.encode()).hexdigest(),'actualNetworkMethodOrMediaOrArchiveExecuted':False,'qualification':'Extracted exact pure pinset/fetch functions tested through fakeHTTPS and tiny fixtures. No production main, network, real credentials, body output/extraction or execution. CanonicalSHA pins checked against exact2f4f historical freeze; all52Git blob metadata checked at immutable23e7cdd tree.'}
(O/'PROOF.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'tests':len(tests),'pins':len(checked),'sourceHashes':[receipt['methodSHA256'],receipt['workflowSHA256']]}))
