"""Selected final source helpers only; fake bounded filesystem events, no CI method/children."""
import ast,errno,hashlib,json,os,resource,signal,stat,types
from pathlib import Path
resource.setrlimit(resource.RLIMIT_AS,(64*1024**2,64*1024**2))
resource.setrlimit(resource.RLIMIT_CPU,(15,15))
signal.alarm(25)
out=Path(__file__).parent
candidate=Path("/workspace/scratch/empty-intent-fresh-ci-source-r5")
b=(candidate/"runner.py").read_bytes()
tree=ast.parse(b)
names={"need","mutation_roots","bounded_path","supervisor_fault","sampled_inventory","disk_inventory","proof_bytes"}
functions=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names]
assert {n.name for n in functions}==names
root=out/"sampling-fixtures"
root.mkdir()
(root/"proof").mkdir()
env={"Path":Path,"os":os,"stat":stat,"errno":errno,"hashlib":hashlib,"DISK_CAP":2*1024**3,"PROOF_CAP":1024**2}
exec(compile(ast.Module(functions,type_ignores=[]),"exact-selected-source","exec"),env)
cases=[]
def test(name,relative,phase="install",expected=None,races=None,count=1,walk_error=None):
 target=root/relative
 if races is None:races={}
 def walk(scan_root,**kw):
  assert kw["followlinks"] is False and callable(kw["onerror"])
  if walk_error is not None:
   kw["onerror"](walk_error)
  else:
   yield str(target.parent),[],[target.name+str(i) if count>1 else target.name for i in range(count)]
 env["os"]=types.SimpleNamespace(fspath=os.fspath,path=os.path,walk=walk)
 caught=None
 try: result=env["disk_inventory"](root,phase=phase,races=races)
 except BaseException as error:caught=error
 if expected is None:assert caught is None and result==0,(name,caught)
 else:assert isinstance(caught,expected),(name,caught)
 cases.append({"name":name,"pass":True,"races":races,"rejectedType":type(caught).__name__ if caught else None})
for path in ("stage/node_modules/pkg/tmp","npm-cache/tmp","proof/npm-debug/rotation"):
 test("install_owned_missing_"+path,path)
for path in ("stage/src/main.ts","control/npm-user.npmrc","downloads/blob","proof/install.log","stage/node_modules-lookalike/tmp","npm-cache-lookalike/tmp","outside/tmp","stage/node_modules","proof/npm-debug"):
 test("stable_or_outside_missing_"+path,path,expected=FileNotFoundError)
test("build_dist_allowed","stage/dist/tmp",phase="build")
test("install_dist_rejected","stage/dist/tmp",expected=FileNotFoundError)
test("build_vite_temp_allowed","stage/node_modules/.vite-temp/tmp",phase="build")
test("build_other_modules_rejected","stage/node_modules/pkg/tmp",phase="build",expected=FileNotFoundError)
test("test_modules_rejected","stage/node_modules/pkg/tmp",phase="test",expected=FileNotFoundError)
test("npm_version_cache_allowed","npm-cache/tmp",phase="npm-version")
test("node_version_cache_rejected","npm-cache/tmp",phase="node-version",expected=FileNotFoundError)
test("unknown_phase_cache_rejected","npm-cache/tmp",phase="unknown",expected=FileNotFoundError)
test("quiescent_no_allowance","npm-cache/tmp",phase=None,expected=FileNotFoundError)
test("strict_scandir_no_allowance","npm-cache/tmp",phase=None,expected=FileNotFoundError,walk_error=FileNotFoundError(errno.ENOENT,"synthetic",str(root/"npm-cache/tmp")))
test("owned_scandir_enoent","npm-cache/tmp",walk_error=FileNotFoundError(errno.ENOENT,"synthetic",str(root/"npm-cache/tmp")))
test("permission_error_rejected","npm-cache/tmp",expected=PermissionError,walk_error=PermissionError(errno.EACCES,"synthetic",str(root/"npm-cache/tmp")))
test("io_error_rejected","npm-cache/tmp",expected=OSError,walk_error=OSError(errno.EIO,"synthetic",str(root/"npm-cache/tmp")))
test("missing_error_path_rejected","npm-cache/tmp",expected=FileNotFoundError,walk_error=FileNotFoundError(errno.ENOENT,"synthetic"))
test("wrong_errno_rejected","npm-cache/tmp",expected=FileNotFoundError,walk_error=FileNotFoundError(errno.EACCES,"synthetic",str(root/"npm-cache/tmp")))
test("per_scan_256_allowed","npm-cache/tmp",count=256)
test("per_scan_257_rejected","npm-cache/tmp",count=257,expected=ValueError)
test("phase_4096_allowed","npm-cache/tmp",races={"missedEntries":4095})
test("phase_4097_rejected","npm-cache/tmp",races={"missedEntries":4096},expected=ValueError)
# Bounded diagnostics retain no raw exception text or source locals.
try:raise FileNotFoundError(errno.ENOENT,"FAKE_SECRET_DO_NOT_RETAIN",str(root/"control/private"))
except FileNotFoundError as error:
 fault=env["supervisor_fault"](root,"install","fixture",error)
 assert "FAKE_SECRET" not in json.dumps(fault)
 assert len(fault["frames"])<=6 and fault["path"]["ownedRelativePrefix"]=="control/private"
cases.append({"name":"bounded_fault_path_frames_no_raw_message","pass":True})
assert env["bounded_path"](root,root/("x"*241))["complete"] is False
assert env["bounded_path"](root,"/outside")["outsideOwnedRoot"] is True
cases.append({"name":"long_owned_and_outside_path_qualification","pass":True})
# Stable scan root replacement cannot become PASS.
def replaced_walk(scan_root,**kw):
 root.rename(out/"sampling-fixtures-retained-original")
 root.mkdir();(root/"proof").mkdir()
 yield str(root),[],[]
env["os"]=types.SimpleNamespace(fspath=os.fspath,path=os.path,walk=replaced_walk)
try:env["disk_inventory"](root,phase="install",races={})
except ValueError:pass
else:raise AssertionError("changed inventory root accepted")
cases.append({"name":"root_identity_replacement_rejected","pass":True})
# Finite byte and entry caps still fail with no transient exception.
(root/"regular").write_bytes(b"abc")
def regular_walk(scan_root,**kw):yield str(root),[],["regular"]
env["os"]=types.SimpleNamespace(fspath=os.fspath,path=os.path,walk=regular_walk)
assert env["sampled_inventory"](root,root,None,None,1,3,True)==3
for limit,cap in ((0,3),(1,2)):
 try:env["sampled_inventory"](root,root,None,None,limit,cap,True)
 except ValueError:pass
 else:raise AssertionError("finite inventory cap bypass")
cases.append({"name":"exact_byte_cap_plus_overbyte_and_entry_cap","pass":True})
receipt={"status":"PASS_ISOLATED_SOURCE_HELPERS_ONLY","methodSHA256":hashlib.sha256(b).hexdigest(),"cases":cases,"caseCount":len(cases),"resource":{"addressSpaceCapBytes":64*1024**2,"cpuSeconds":15,"wallAlarmSeconds":25,"selfRssPeakBytes":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,"reserveBytes":512*1024**2},"qualification":"Exact selected helper bodies with injected os.walk events and tiny owned files. No full method/import, network, npm, archive, child, build/test, browser or proof of actual race cause. Fixture originals retained."}
with (out/"PURE-SAMPLING-CHECKS.json").open("x") as f:f.write(json.dumps(receipt,sort_keys=True,separators=(",",":"))+"\n")
print(json.dumps({"status":receipt["status"],"caseCount":len(cases),"methodSHA256":receipt["methodSHA256"]}))
