import ast,pathlib,base64,zlib,json,re,tarfile,io,hashlib
from pathlib import PurePosixPath
P=pathlib.Path('/workspace/scratch/empty-intent-fresh-ci-source-r3');O=pathlib.Path('/workspace/scratch/empty-intent-fresh-ci-technical-r3')
body=(P/'runner.py').read_bytes();tree=ast.parse(body);compile(tree,str(P/'runner.py'),'exec')
names={'MIB','META_SHA','META_LITERAL','FILE_CAP'}
nodes=[n for n in tree.body if (isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in names for t in n.targets)) or (isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in {'need','unique','load_json','metadata','safe_path','BoundedStream','member_header'})]
env={'base64':base64,'zlib':zlib,'json':json,'re':re,'tarfile':tarfile,'hashlib':hashlib,'PurePosixPath':PurePosixPath}
exec(compile(ast.fix_missing_locations(ast.Module(body=nodes,type_ignores=[])),'offline_pure_header_and_path_guards','exec'),env)
assert env['metadata']()==json.loads((P/'METADATA.json').read_bytes())
tests=[]
def check(label,f,accept=False):
 try:f();actual=True
 except (ValueError,TypeError):actual=False
 assert actual==accept,label;tests.append({'case':label,'accepted':actual})
for p in ['a/b.ts','public/art/one.png']:
 check('path_valid_'+p,lambda p=p:env['safe_path'](p),True)
for p in ['', '.', '..', '../a','a/../b','/a','a//b','a/./b','a/','a\\b','a\x00b','x'*241]:
 check('path_reject_'+repr(p),lambda p=p:env['safe_path'](p))
def member(name='blobs/'+'a'*64,size=10,type=tarfile.REGTYPE,pax=None,link='',sparse=None):
 t=tarfile.TarInfo(name);t.size=size;t.type=type;t.pax_headers=pax or {};t.linkname=link;t.sparse=sparse;return t
check('regular_hash_member',lambda:env['member_header'](member(),'8cdf'),True)
check('ce0f_index_exact_size',lambda:env['member_header'](member('INDEX.json',928223),'ce0f'),True)
for t,label in [(member(type=tarfile.DIRTYPE),'directory'),(member(type=tarfile.SYMTYPE,link='target'),'symlink'),(member(type=tarfile.LNKTYPE,link='target'),'hardlink'),(member(type=tarfile.CHRTYPE),'device'),(member(type=tarfile.FIFOTYPE),'FIFO'),(member(pax={'path':'bad'}),'pax'),(member(sparse=[(0,1)]),'sparse'),(member('../blobs/'+'a'*64),'traversal'),(member(size=9*1048576+1),'oversized'),(member(name='blobs/'+'A'*64),'uppercase'),(member(name='INDEX.json',size=928223),'foreign_index'),(member(name='INDEX.json',size=928222),'wrong_index_size')]:
 check('member_reject_'+label,lambda t=t:env['member_header'](t,'8cdf' if label!='wrong_index_size' else 'ce0f'))
check('bounded_stream_exact',lambda:env['BoundedStream'](io.BytesIO(b'1234'),4).read(4),True)
check('bounded_stream_overflow',lambda:env['BoundedStream'](io.BytesIO(b'12345'),4).read(6))
check('bounded_stream_unbounded_read',lambda:env['BoundedStream'](io.BytesIO(b'1'),4).read())
check('duplicate_JSON',lambda:env['load_json']('{"x":1,"x":2}'))
proof={'sourceOnly':True,'draftRunnerSHA256':hashlib.sha256(body).hexdigest(),'PythonASTCompilePassed':True,'literalMetadataExact':True,'cases':tests,'count':len(tests),'productionMainNetworkArchiveAssemblyOrNpmBuildTestExecuted':False,'qualification':'Only exact selected pure path/header/bounded-read functions exercised using inert TarInfo metadata and tiny BytesIO fixtures. No TAR bytes read or extracted; no process supervision/commands invoked. Rebind final source seal before final verdict.'}
(O/'BOUNDARY-PROOF.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({'cases':len(tests),'draftRunnerSHA256':proof['draftRunnerSHA256']}))
