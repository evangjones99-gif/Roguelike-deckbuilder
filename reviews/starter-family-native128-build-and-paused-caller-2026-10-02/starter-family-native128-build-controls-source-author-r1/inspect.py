import os,json,ast,resource
from pathlib import Path
resource.setrlimit(resource.RLIMIT_DATA,(24*1048576,24*1048576))
p=Path('/workspace/scratch/native128-empty-intent-build-controls-source-author-r1')
def r(q):
 fd=os.open(q,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME)
 with os.fdopen(fd) as f:return f.read()
for n in ['PLAN.json','ARGV.json','SOURCE-GATE.json']:
 x=json.loads(r(p/n));print(json.dumps({'file':n,'body':x}))
s=r(p/'assemble.py');t=ast.parse(s)
for node in t.body:
 if isinstance(node,(ast.FunctionDef,ast.If)) and (not isinstance(node,ast.FunctionDef) or node.name not in ['sha','read','write','digest_map','require']):
  print(json.dumps({'assembly':getattr(node,'name','main'),'source':ast.get_source_segment(s,node)}))
print(json.dumps({'runner':r(p/'strict-build-runner.mjs')}))
print(json.dumps({'finalizerFunctions':[(n.name,n.lineno,n.end_lineno) for n in ast.parse(r(p/'finalize.py')).body if isinstance(n,ast.FunctionDef)]}))
