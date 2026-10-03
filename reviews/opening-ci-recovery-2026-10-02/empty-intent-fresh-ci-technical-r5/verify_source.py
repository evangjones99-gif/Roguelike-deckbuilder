import ast,base64,gzip,hashlib,json,os,re,resource,shutil,signal,stat,yaml
from pathlib import Path
resource.setrlimit(resource.RLIMIT_AS,(64*1024**2,64*1024**2))
resource.setrlimit(resource.RLIMIT_CPU,(25,25))
signal.alarm(35)
P=Path("/workspace/scratch/empty-intent-fresh-ci-source-r5")
OLD=Path("/workspace/scratch/empty-intent-fresh-ci-source-r4")
O=Path(__file__).parent
def sha(b):return hashlib.sha256(b).hexdigest()
def pins(root):
 result={}
 for p in root.rglob("*"):
  assert not p.is_symlink()
  if p.is_file():
   b=p.read_bytes()
   result[p.relative_to(root).as_posix()]={"bytes":len(b),"sha256":sha(b)}
 return result
host=int(next(s.split()[1] for s in Path("/proc/meminfo").read_text().splitlines() if s.startswith("MemAvailable:")))*1024
maxmem=Path("/sys/fs/cgroup/memory.max").read_text().strip()
current=int(Path("/sys/fs/cgroup/memory.current").read_text())
headroom=host if maxmem=="max" else min(host,int(maxmem)-current)
assert headroom>=(64+512)*1024**2 and shutil.disk_usage(O).free>=24*1024**2
before=pins(P);oldpins=pins(OLD)
seal=(P/"SOURCE-SEAL.json").read_bytes()
assert sha(seal)=="3b1ee95586d4c80fd2fbce9111d3bb99245b595963bc873f6e9ee9f473f01cd0"
s=json.loads(seal)
mbytes=(P/"MANIFEST.json").read_bytes();m=json.loads(mbytes)
assert s["manifest"]=={"bytes":len(mbytes),"sha256":sha(mbytes)}
assert s["files"]==m["files"]=={k:v for k,v in before.items() if k not in ("MANIFEST.json","SOURCE-SEAL.json")}
assert set(before)==set(s["files"])|{"MANIFEST.json","SOURCE-SEAL.json"}
inclusive=sum(v["bytes"] for v in before.values())
assert inclusive==s["inclusiveFamilyBytes"]==m["inclusiveFamilyBytes"]==277566
assert s["sourceCapBytes"]==262144 and inclusive>s["sourceCapBytes"]
assert sha((OLD/"SOURCE-SEAL.json").read_bytes())=="51f4e42e9ca6d846ad6edd93cb0445936becdf07a7230204c9b9e4ebb71a1080"
assert sha((OLD/"MANIFEST.json").read_bytes())=="1c8b2dea0a033a26abf203598f321b32bb61a79959a7da94bdbef4f9378dad70"
parent_review=Path("/workspace/scratch/empty-intent-fresh-ci-technical-r4/GATE.json")
assert sha(parent_review.read_bytes())=="4bc8c4100ef3c07ad39f2d71b1032cd2145ccb6dc6796a9683c8841b07d1157b"
for name in ("METADATA.json","PRIMARY-ACTIONS.json","ORIGINAL-BUILD-GRAMMAR.mjs","source_checks.py","shared_shim_checks.py"):
 assert (P/name).read_bytes()==(OLD/name).read_bytes()
text=(P/"runner.py").read_text();old=(OLD/"runner.py").read_text()
a=ast.parse(old);b=ast.parse(text);compile(b,"source-grammar-only","exec")
am={n.name:ast.dump(n,include_attributes=False) for n in a.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
bm={n.name:ast.dump(n,include_attributes=False) for n in b.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
assert set(bm)-set(am)=={"mutation_roots","bounded_path","supervisor_fault","sampled_inventory"}
assert not (set(am)-set(bm))
changed=sorted(k for k in am if am[k]!=bm[k])
assert changed==["disk_inventory","proof_bytes","run_phase"]
other=lambda t:ast.dump(ast.Module([n for n in t.body if not isinstance(n,(ast.FunctionDef,ast.ClassDef)) and not (isinstance(n,ast.Import) and len(n.names)==1 and n.names[0].name=="errno")],[]),include_attributes=False)
assert other(a)==other(b)
for name in am:
 if name not in changed:
  assert ast.get_source_segment(old,next(n for n in a.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name==name))==ast.get_source_segment(text,next(n for n in b.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name==name))
wf=(P/"rebuild-opening-baseline.yml").read_text()
owf=(OLD/"rebuild-opening-baseline.yml").read_text()
def block(source):return "          source = r'''"+source.replace("\n","\n          ")+"'''\n"
assert owf.count(block(old))==1
assert owf.replace(block(old),block(text)).replace(sha(old.encode()),sha(text.encode()))==wf
w=yaml.load(wf,Loader=yaml.BaseLoader)
grammar=[]
for step in w["jobs"]["fresh-baseline"]["steps"]:
 if "run" in step:
  run=step["run"]
  if run.startswith("python3 - <<'PY'\n"):
   py=run[len("python3 - <<'PY'\n"):run.rindex("\nPY")]
   compile(ast.parse(py),"embedded-source-only","exec")
   grammar.append({"step":step["id"],"pythonSHA256":sha(py.encode())})
decoder=ast.parse(Path("/workspace/scratch/empty-intent-fresh-ci-technical-r1/final_seal_check.py").read_bytes())
fun=next(n for n in decoder.body if isinstance(n,ast.FunctionDef) and n.name=="unified")
env={"re":re};exec(compile(ast.Module([fun],[]),"exact-delta-decoder","exec"),env)
roundtrips=[]
for name,starting,ending in (("INVERSE.json.gz",P,OLD),("FORWARD.json.gz",OLD,P)):
 delta=json.loads(gzip.decompress((P/name).read_bytes()))
 assert set(delta)=={"runner.py","rebuild-opening-baseline.yml"}
 for key,row in delta.items():
  start=(starting/key).read_text();end=(ending/key).read_text()
  assert row["before"]=={"bytes":len(start.encode()),"sha256":sha(start.encode())}
  assert row["after"]=={"bytes":len(end.encode()),"sha256":sha(end.encode())}
  assert env["unified"](start,row["unifiedDiff"])==end
  assert env["unified"](end,row["unifiedDiff"],True)==start
  roundtrips.append({"direction":name,"file":key,"exactForwardAndReverse":True})
original=json.loads(gzip.decompress((P/"INVERSE-ORIGINALS.json.gz").read_bytes()))
orunner=base64.b64decode(original["runnerBase64"],validate=True)
assert original["runner"]=={"bytes":len(orunner),"sha256":sha(orunner)}
assert orunner==(OLD/"runner.py").read_bytes()
assert original["workflowTemplate"].count(original["templateMarker"])==1
rebuilt=original["workflowTemplate"].replace(original["templateMarker"],block(orunner.decode())).encode()
assert rebuilt==(OLD/"rebuild-opening-baseline.yml").read_bytes()
assert original["workflow"]=={"bytes":len(rebuilt),"sha256":sha(rebuilt)}
actual=json.loads((O/"ACTUAL-FAILURE-CHECKS.json").read_bytes())
assert actual["status"]=="VERIFIED_PRESERVED_FAILED_INSTALLS_ONLY"
pure=json.loads((O/"PURE-SAMPLING-CHECKS.json").read_bytes())
assert pure["methodSHA256"]==sha(text.encode()) and pure["caseCount"]==35
assert before==pins(P) and oldpins==pins(OLD)
receipt={"status":"IDENTITY_FUNCTIONAL_BOUNDARIES_VERIFIED_BUT_SOURCE_CAP_REJECTED","sourceSealSHA256":sha(seal),"manifestSHA256":sha(mbytes),"sourceFiles":before,"sourceInclusiveBytes":inclusive,"assignedSourceCapBytes":262144,"excessBytes":inclusive-262144,"methodSHA256":sha(text.encode()),"workflowSHA256":sha(wf.encode()),"changedOriginalFunctions":changed,"addedHelpers":sorted(set(bm)-set(am)),"allOtherFunctionsByteExactR4":True,"allOtherTopLevelASTExactExceptErrnoImport":True,"workflowExactExceptEmbeddedMethodAndHash":True,"fullTwoBodyForwardInverseBothDirections":roundtrips,"selfContainedOriginalRunnerWorkflowReconstructionExact":True,"embeddedPythonGrammar":grammar,"independentIsolatedCases":35,"authorBoundReceipts":{"source":json.loads((P/"SOURCE-CHECKS.json").read_bytes())["caseCount"],"race":json.loads((P/"RACE-CHECKS.json").read_bytes())["caseCount"],"shim":len(json.loads((P/"SHARED-SHIM-CHECKS.json").read_bytes())["cases"])},"ordinary":{"workCapBytes":64*1024**2,"reserveBytes":512*1024**2,"initialHeadroom":headroom,"selfPeakRSS":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,"cpuLimitSeconds":25,"alarmSeconds":35},"qualification":"No full method/main/network/archive/npm/children/build/test/browser execution. Prior all-shell/original-build grammar receipts remain bound; unchanged original source received earlier independent checks. Actual predecessor syscall/path absent. Source cap excess is a blocking eligibility failure; no retroactive acceptance.","originalPacketsUnchanged":True}
with (O/"SOURCE-CHECKS.json").open("x") as f:f.write(json.dumps(receipt,sort_keys=True,separators=(",",":"))+"\n")
print(json.dumps({"status":receipt["status"],"inclusiveBytes":inclusive,"changedFunctions":changed,"roundtripCount":len(roundtrips)}))
