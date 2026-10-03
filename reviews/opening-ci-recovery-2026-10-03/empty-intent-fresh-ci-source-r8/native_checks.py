"""Pure selected-native inventory and diagnostics cases; no npm/network/candidate main."""
import ast
import errno
import hashlib
import json
import os
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).parent
PARENT=ROOT.parent/"empty-intent-fresh-ci-source-r6"
source=(ROOT/"runner.py").read_text()
prior=(PARENT/"runner.py").read_text()
tree=ast.parse(source)
chosen={"need","safe_path","bounded_path","supervisor_fault","native_inventory","regular_inventory"}
body=[n for n in tree.body if isinstance(n,(ast.Import,ast.ImportFrom,ast.Assign)) or
      isinstance(n,ast.FunctionDef) and n.name in chosen]
receipts=[]
hashed=[]
def record(root,name,obj,cap=65536):
    assert len(json.dumps(obj,separators=(",",":")))+1<=cap
    receipts.append((name,obj))
def hash_stub(path,cap):
    assert cap==128*1048576
    hashed.append(str(path))
    return {"bytes":3,"sha256":hashlib.sha256(b"abc").hexdigest()}
env={"__name__":"pure_native_inventory_definitions","receipt":record,"hash_file":hash_stub}
exec(compile(ast.Module(body=body,type_ignores=[]),"pure-native-definitions","exec"),env)
root=Path("/owned")
name="@typescript/typescript-linux-x64"
package=root/"stage/node_modules"/name
results=[]

def run(names,error=None,dirs=(),hash_error=None,symlink=None,old=False,package_name=name,package_path=None):
    receipts.clear()
    hashed.clear()
    target=package if package_path is None else package_path
    def walker(*args,**kwargs):
        if error is not None:
            kwargs["onerror"](error)
        return iter([(str(target),list(dirs),list(names))])
    def hasher(path,cap):
        if hash_error is not None:
            raise hash_error
        return hash_stub(path,cap)
    with patch.object(Path,"is_dir",lambda path:True),patch.object(Path,"is_symlink",lambda path:path==symlink),patch.object(os,"walk",walker):
        original=env["hash_file"]
        env["hash_file"]=hasher
        try:
            if old:
                return env["regular_inventory"](target,100,128*1048576)
            return env["native_inventory"](root,target,package_name,6)
        finally:
            env["hash_file"]=original

def case(label,operation,rejected=None,diagnostic=True):
    try:
        value=operation()
    except BaseException as error:
        assert rejected is not None and isinstance(error,rejected),(label,type(error).__name__)
        if diagnostic:
            assert len(receipts)==1 and receipts[0][1]["status"]=="FAILED",label
            assert not receipts[0][1]["completeInventory"]
            assert "fault" in receipts[0][1] and len(receipts[0][1]["firstBoundedNames"])<=16
    else:
        assert rejected is None,label
        assert len(receipts)==1 and receipts[0][1]["completeInventory"]
        assert receipts[0][1]["status"]=="PASS_INVENTORY_BYTES_ONLY"
    results.append(label)

def counted(count,old=False):
    names=["lib/file-"+str(i)+".d.ts" for i in range(count)]
    got=run(names,old=old)
    assert len(got)==count and len(hashed)==count
    if not old:
        assert receipts[0][1]["fileCountObserved"]==count
        assert receipts[0][1]["hashedBytes"]==count*3
        assert len(receipts[0][1]["firstBoundedNames"])==min(count,16)
    return got
assert len(counted(100,old=True))==100
results.append("legacy100_pass")
case("legacy101_count_failure_reproduced",lambda:counted(101,old=True),ValueError,False)
case("selected_native100_pass",lambda:counted(100))
case("selected_native101_pass",lambda:counted(101))
case("selected_native4096_exact_bound_pass",lambda:counted(4096))
case("selected_native4097_rejected_before_hash",lambda:counted(4097),ValueError)
assert len(hashed)==4096 and receipts[0][1]["fileCountObserved"]==4097
assert receipts[0][1]["hashedBytes"]==4096*3
results.append("cap_failure_retains_exact_count_partial_bytes_first16")
case("unknown_package_refused",lambda:run(["a"],package_name="@other/native"),ValueError,False)
case("wrong_package_root_refused",lambda:run(["a"],package_path=root/"outside"),ValueError,False)
case("native_root_symlink_refused",lambda:run(["a"],symlink=package),ValueError)
case("native_directory_symlink_refused",lambda:run(["a"],dirs=["link"],symlink=package/"link"),ValueError)
for label,path in [("traversal","../outside"),("absolute","/outside"),("backslash","a\\b"),
                   ("long_path","x"*241)]:
    case("native_path_"+label+"_refused",lambda path=path:run([path]),ValueError)
case("duplicate_path_refused",lambda:run(["same","same"]),ValueError)
for error in [PermissionError(errno.EACCES,"synthetic",str(package/"lib")),
              FileNotFoundError(errno.ENOENT,"synthetic",str(package/"lib")),
              OSError(errno.EIO,"synthetic",str(package/"lib"))]:
    case("native_walk_"+type(error).__name__+"_refused",lambda error=error:run([],error=error),type(error))
for error in [PermissionError(errno.EACCES,"synthetic",str(package/"file")),
              FileNotFoundError(errno.ENOENT,"synthetic",str(package/"file")),
              ValueError("regular owned file")]:
    case("native_hash_"+type(error).__name__+"_refused",lambda error=error:run(["file"],hash_error=error),type(error))
    assert receipts[0][1]["hashedBytes"]==0 and receipts[0][1]["fileCountObserved"]==1
case("bounded_long_name_diagnostic_before_rejection",lambda:run(["x"*241]),ValueError)
assert len(receipts[0][1]["firstBoundedNames"][0]["namePrefix"])==160
assert not receipts[0][1]["firstBoundedNames"][0]["complete"]

old_functions={n.name:ast.get_source_segment(prior,n) for n in ast.parse(prior).body if isinstance(n,ast.FunctionDef)}
new_functions={n.name:ast.get_source_segment(source,n) for n in tree.body if isinstance(n,ast.FunctionDef)}
assert sorted(n for n in old_functions if old_functions[n]!=new_functions[n])==["provision_audit"]
assert set(new_functions)-set(old_functions)=={"native_inventory"}
old_audit=old_functions["provision_audit"]
new_audit=new_functions["provision_audit"]
assert new_audit.replace("inventory=native_inventory(root,package,name,index)","inventory=regular_inventory(package,100,128*MIB)")==old_audit
results.append("only_native_callsite_changed_all_other_functions_exactR6")
assert 'header[:4]==b"\\x7fELF"' in new_audit and 'actual ELF64 x86_64 platform' in new_audit
results.append("unchanged_ELF64_x86_64_nonempty_native_requirement")
result={"status":"PASS_PURE_SOURCE_ONLY","caseCount":len(results),"cases":results,
        "methodSHA256":hashlib.sha256(source.encode()).hexdigest(),"actualNativePackageTotalCountNames":"UNOBSERVED",
        "candidateMainNpmNetworkArchiveBuildBrowserExecuted":False}
(ROOT/"NATIVE-CHECKS.json").write_text(json.dumps(result,separators=(",",":"))+"\n")
print(json.dumps({"status":result["status"],"caseCount":len(results)}))
