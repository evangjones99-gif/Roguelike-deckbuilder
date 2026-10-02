"""Isolated inventory race and pure diagnostics; never run candidate main or npm."""
import ast
import errno
import hashlib
import json
import os
from pathlib import Path
import stat
from unittest.mock import patch

ROOT=Path(__file__).parent
PARENT=ROOT.parent/"empty-intent-fresh-ci-source-r4"
source=(ROOT/"runner.py").read_text()
tree=ast.parse(source)
selected={"need","mutation_roots","bounded_path","supervisor_fault","sampled_inventory","disk_inventory","proof_bytes"}
body=[n for n in tree.body if isinstance(n,(ast.Import,ast.ImportFrom)) or
      isinstance(n,ast.Assign) or isinstance(n,ast.FunctionDef) and n.name in selected]
env={"__name__":"isolated_inventory_definitions"}
exec(compile(ast.Module(body=body,type_ignores=[]),"isolated-definitions","exec"),env)
prior_tree=ast.parse((PARENT/"runner.py").read_text())
old_env=dict(env)
old_body=[n for n in prior_tree.body if isinstance(n,ast.FunctionDef) and n.name in ("disk_inventory","proof_bytes")]
exec(compile(ast.Module(body=old_body,type_ignores=[]),"original-R4-inventory","exec"),old_env)
fixture=ROOT/"race-fixtures"
fixture.mkdir()
for rel in ("stage/node_modules/pkg","stage/dist/assets","stage/node_modules/.vite-temp",
            "npm-cache/cache","proof/npm-debug","stage/src","control","downloads"):
    (fixture/rel).mkdir(parents=True,exist_ok=True)
(fixture/"control/stable.txt").write_bytes(b"stable")
real_walk=os.walk
real_lstat=Path.lstat
cases=[]
def check(name,operation,rejected=None):
    try:
        value=operation()
    except BaseException as error:
        assert rejected is not None and isinstance(error,rejected),(name,type(error).__name__)
    else:
        assert rejected is None,name
    cases.append(name)

def disappearing(rel,phase="install",old=False,proof=False):
    target=fixture/rel
    target.write_bytes(b"tiny-race-body")
    deleted=False
    def raced_lstat(path,*args,**kwargs):
        nonlocal deleted
        if path==target and not deleted:
            path.unlink()
            deleted=True
        return real_lstat(path,*args,**kwargs)
    races={}
    selected_env=old_env if old else env
    with patch.object(Path,"lstat",raced_lstat):
        if proof:
            selected_env["proof_bytes"](fixture,**({} if old else {"phase":phase,"races":races}))
        else:
            selected_env["disk_inventory"](fixture,**({} if old else {"phase":phase,"races":races}))
    assert deleted and races["missedEntries"]==1
    assert races["sites"]=={"lstat":1} and len(races["firstExamples"])==1

check("R4_actual_unlink_between_enumeration_and_lstat_reproduces_ENOENT",
      lambda:disappearing("stage/node_modules/pkg/old-race",old=True),FileNotFoundError)
check("R5_install_modules_ENOENT_tolerated_and_recorded",lambda:disappearing("stage/node_modules/pkg/race"))
check("R5_install_cache_ENOENT_tolerated",lambda:disappearing("npm-cache/cache/race"))
check("R5_build_dist_ENOENT_tolerated",lambda:disappearing("stage/dist/assets/race",phase="build"))
check("R5_build_vite_temp_ENOENT_tolerated",lambda:disappearing("stage/node_modules/.vite-temp/race",phase="build"))
check("R5_proof_debug_ENOENT_tolerated",lambda:disappearing("proof/npm-debug/race",proof=True))
for rel,phase in [("stage/src/race","install"),("control/race","install"),("downloads/race","install"),
                  ("proof/race","install"),("stage/node_modules/pkg/race","test"),
                  ("stage/dist/assets/race","install"),("stage/node_modules/.vite-temp/race","test"),
                  ("npm-cache/cache/race","node-version"),("npm-cache/cache/race",None)]:
    check("refused_missing_"+rel+"_"+str(phase),lambda rel=rel,phase=phase:disappearing(rel,phase),FileNotFoundError)
check("proof_authority_ENOENT_fatal",lambda:disappearing("proof/authority-race",proof=True),FileNotFoundError)

def scan_error(error,phase="install",races=None):
    def walk(*args,**kwargs):
        kwargs["onerror"](error)
        return iter(())
    with patch.object(os,"walk",walk):
        return env["disk_inventory"](fixture,phase=phase,races={} if races is None else races)

check("scandir_missing_mutating_descendant_tolerated",
      lambda:scan_error(FileNotFoundError(errno.ENOENT,"synthetic",str(fixture/"npm-cache/cache/gone"))))
check("scandir_missing_exact_mutation_root_fatal",
      lambda:scan_error(FileNotFoundError(errno.ENOENT,"synthetic",str(fixture/"npm-cache"))),FileNotFoundError)
for error in [PermissionError(errno.EACCES,"synthetic",str(fixture/"npm-cache/cache")),
              OSError(errno.EIO,"synthetic",str(fixture/"npm-cache/cache")),
              NotADirectoryError(errno.ENOTDIR,"synthetic",str(fixture/"npm-cache/cache")),
              FileNotFoundError(errno.EIO,"synthetic",str(fixture/"npm-cache/cache")),
              FileNotFoundError(errno.ENOENT,"synthetic",str(fixture/"control")),
              FileNotFoundError(errno.ENOENT,"synthetic")]:
    check("scandir_refuses_"+type(error).__name__+"_"+str(error.errno)+"_"+str(error.filename),
          lambda error=error:scan_error(error),type(error))

def many_misses(count,prior=0,entry_limit=100000):
    target=fixture/"npm-cache/cache"
    names=["absent-"+str(i) for i in range(count)]
    with patch.object(os,"walk",lambda *args,**kw:iter([(str(target),[],names)])):
        return env["disk_inventory"](fixture,phase="install",races={"missedEntries":prior},limit=entry_limit)
check("256_missing_entries_exact_scan_bound",lambda:many_misses(256))
check("257_missing_entries_refused",lambda:many_misses(257),ValueError)
check("phase_accumulated_4096_exact_bound",lambda:many_misses(1,4095))
check("phase_accumulated_4097_refused",lambda:many_misses(1,4096),ValueError)
check("disappeared_names_still_count_toward_entry_cap",lambda:many_misses(2,entry_limit=1),ValueError)
check("strict_scan_has_no_mutation_allowance",
      lambda:scan_error(FileNotFoundError(errno.ENOENT,"synthetic",str(fixture/"npm-cache/cache/gone")),None),FileNotFoundError)

def replacement_root():
    calls=0
    root_stat=real_lstat(fixture)
    class Changed:
        st_mode=root_stat.st_mode
        st_dev=root_stat.st_dev
        st_ino=root_stat.st_ino+1
    def changed(path,*args,**kwargs):
        nonlocal calls
        if path==fixture:
            calls+=1
            if calls==2:
                return Changed()
        return real_lstat(path,*args,**kwargs)
    with patch.object(Path,"lstat",changed):
        env["disk_inventory"](fixture)
check("inventory_root_replacement_fatal",replacement_root,ValueError)
check("missing_inventory_root_fatal",lambda:env["disk_inventory"](fixture/"absent"),FileNotFoundError)
(fixture/"root-link").symlink_to(fixture,target_is_directory=True)
check("inventory_root_symlink_fatal",lambda:env["disk_inventory"](fixture/"root-link"),ValueError)
(fixture/"root-link").unlink()  # Test-created link only; no frozen/predecessor bytes.

fault_error=FileNotFoundError(errno.ENOENT,"synthetic secret must not log",str(fixture/"control/missing"))
try:
    raise fault_error
except FileNotFoundError as error:
    fault=env["supervisor_fault"](fixture,"install","synthetic owned scan",error)
assert fault["path"]["ownedRelativePrefix"]=="control/missing" and fault["errno"]==errno.ENOENT
assert fault["frames"] and "synthetic secret" not in json.dumps(fault)
cases.append("supervisor_fault_stage_errno_owned_path_frames_bounded")
outside=env["bounded_path"](fixture,"/other/secret-marker")
assert outside["outsideOwnedRoot"] and "secret-marker" not in json.dumps(outside)
long=env["bounded_path"](fixture,fixture/("a"*1000))
assert len(long["ownedRelativePrefix"])==240 and not long["complete"]
cases.append("diagnostic_outside_path_opaque_and_long_path_bounded")

prior_functions={n.name:ast.get_source_segment((PARENT/"runner.py").read_text(),n) for n in prior_tree.body if isinstance(n,ast.FunctionDef)}
new_functions={n.name:ast.get_source_segment(source,n) for n in tree.body if isinstance(n,ast.FunctionDef)}
changed=sorted(name for name,value in prior_functions.items() if new_functions[name]!=value)
assert changed==["disk_inventory","proof_bytes","run_phase"],changed
assert set(new_functions)-set(prior_functions)=={"mutation_roots","bounded_path","supervisor_fault","sampled_inventory"}
run=new_functions["run_phase"]
assert 'disk_inventory(root,phase=name,races=races)' in run and 'proof_bytes(root,phase=name,races=races)' in run
assert 'site="closed-phase strict owned disk scan"\n            disk_inventory(root)' in run
assert 'need(time.monotonic()-start<whole_s' in run
assert 'supervisorFault":fault' in run and 'samplingDisappearance":races' in run
cases.append("only_three_original_functions_changed_all_other_guards_byte_exact")
result={"status":"PASS_ISOLATED_SOURCE_ONLY","caseCount":len(cases),"cases":cases,"changedOriginalFunctions":changed,
        "actualFailureSite":"UNOBSERVED","originalReproduction":"Kernel ENOENT after intentional unlink in an isolated owned fixture; inference only.",
        "methodSHA256":hashlib.sha256(source.encode()).hexdigest(),"candidateMainNpmNetworkArchiveBuildBrowserExecuted":False}
(ROOT/"RACE-CHECKS.json").write_text(json.dumps(result,separators=(",",":"))+"\n")
print(json.dumps({"status":result["status"],"caseCount":len(cases)}))
