import ast,base64,hashlib,json,pathlib
P=pathlib.Path('/workspace/scratch/archive8cdf-transfer-source-r1')
O=pathlib.Path('/workspace/scratch/archive8cdf-transfer-technical-r1')
source=(P/'acquire_exact_blob.py').read_text();tree=ast.parse(source);compile(tree,str(P/'acquire_exact_blob.py'),'exec')
main=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
start=next(i for i,n in enumerate(main.body) if ast.unparse(n)=="require(isinstance(payload, dict))")
end=next(i for i,n in enumerate(main.body) if ast.unparse(n).startswith('directory.mkdir('))
validation=ast.fix_missing_locations(ast.Module(body=main.body[start:end],type_ignores=[]))
helpers=ast.fix_missing_locations(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['require','unique_object']],type_ignores=[]))
namespace={'base64':base64,'hashlib':hashlib};exec(compile(helpers,'offline_helpers','exec'),namespace)
fixture=b'bounded synthetic byte identity\x00\xff';sha1=hashlib.sha1(b'blob '+str(len(fixture)).encode()+b'\0'+fixture).hexdigest();sha256=hashlib.sha256(fixture).hexdigest();url='https://api.github.com/repos/test/fixture/git/blobs/'+sha1
good={'sha':sha1,'size':len(fixture),'encoding':'base64','url':url,'content':base64.b64encode(fixture).decode()}
code=compile(validation,'offline_exact_source_validation','exec');tests=[]
def check(name,payload,accept,overrides=None):
 env={**namespace,'payload':payload,'BLOB_SHA1':sha1,'ARCHIVE_SHA256':sha256,'ARCHIVE_BYTES':len(fixture),'API_URL':url,'RESPONSE_CAP':1024};env.update(overrides or {})
 try:exec(code,env);passed=True
 except (ValueError,TypeError,KeyError):passed=False
 assert passed==accept,name
 if passed:assert env['body']==fixture
 tests.append({'name':name,'expectedAccepted':accept,'observedAccepted':passed})
check('correct_exact_synthetic_body',dict(good),True)
check('LF_wrapping_only',dict(good,content=good['content'][:8]+'\n'+good['content'][8:]),True)
for k,v in [('sha','0'*40),('size',len(fixture)+1),('encoding','utf-8'),('url','https://elsewhere.invalid/'),('content',good['content']+'='),('content',good['content'][:3]+'!'+good['content'][4:]),('content',good['content']+'\r')]:check('reject_'+k+'_'+str(v)[:12],dict(good,**{k:v}),False)
check('reject_correct_metadata_wrong_SHA256',dict(good),False,{'ARCHIVE_SHA256':'0'*64})
changed=bytes([fixture[0]^1])+fixture[1:];check('reject_same_size_changed_body',dict(good,content=base64.b64encode(changed).decode()),False)
try:json.loads('{"sha":"x","sha":"y"}',object_pairs_hook=namespace['unique_object']);raise AssertionError('Duplicate JSON accepted')
except ValueError:tests.append({'name':'duplicate_JSON_keys','rejected':True})
# Exercise the exact streaming loop with an offline FakeResponse at a tiny cap.
t=next(n for n in main.body if isinstance(n,ast.Try));rawstart=next(i for i,n in enumerate(t.body) if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='raw' for x in n.targets));rawend=next(i for i,n in enumerate(t.body) if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='response_bytes' for x in n.targets));chunkcode=compile(ast.fix_missing_locations(ast.Module(body=t.body[rawstart:rawend+1],type_ignores=[])),'offline_bounded_read','exec')
class FakeResponse:
 def __init__(self,body):self.body=body;self.position=0;self.requests=[]
 def read(self,n):self.requests.append(n);r=self.body[self.position:self.position+n];self.position+=len(r);return r
for name,data,declared,accepted in [('exact_cap',b'x'*32,'32',True),('cap_plus_one',b'x'*33,None,False),('short_content_length',b'x'*31,'32',False),('over_declared_length',b'x'*32,'31',False),('chunked_under_cap',b'x'*31,None,True)]:
 response=FakeResponse(data);env={**namespace,'response':response,'RESPONSE_CAP':32,'declared':declared}
 try:exec(chunkcode,env);result=True
 except ValueError:result=False
 assert result==accepted,name;assert all(0<n<=65536 for n in response.requests);tests.append({'name':name,'expectedAccepted':accepted,'observedAccepted':result,'maximumReadRequest':max(response.requests)})
workflow=(P/'recover-opening-evidence.yml').read_text();assert workflow.count("timeout --signal=TERM --kill-after=2s 70s python3 -I -B - <<'PY'")==1
embedded=workflow.split("python3 -I -B - <<'PY'\n",1)[1].split('          PY\n',1)[0];embedded=''.join(line[10:] for line in embedded.splitlines(keepends=True));assert embedded==source
assert 'actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02' in workflow
receipt={'sourceOnly':True,'methodGrammarPassed':True,'embeddedSourceExact':True,'offlineSyntheticTests':tests,'networkOrArchiveMethodExecuted':False,'realArchiveBytesAcquired':False,'syntheticFixtureBytes':len(fixture),'methodSHA256':hashlib.sha256(source.encode()).hexdigest(),'workflowSHA256':hashlib.sha256(workflow.encode()).hexdigest(),'qualification':'Extracted unchanged pure validation and streaming-loop AST tested with tiny fixtures and overridden test identities/caps. No main(), token, HTTP, filesystem archive output, archive extraction or production blob execution.'}
(O/'OFFLINE-PROOF.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
