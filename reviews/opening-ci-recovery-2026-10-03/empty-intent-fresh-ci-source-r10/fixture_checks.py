"""Pure fixture pinning/membership checks; no archive/acquire/npm/main execution."""
import ast
import hashlib
import json
import os
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).parent
PARENT=ROOT.parent/"empty-intent-fresh-ci-source-r9"
source=(ROOT/"runner.py").read_text()
tree=ast.parse(source)
selected={"need","unique","load_json","metadata","safe_path","verify_pin","membership"}
body=[n for n in tree.body if isinstance(n,(ast.Import,ast.ImportFrom,ast.Assign)) or
      isinstance(n,ast.FunctionDef) and n.name in selected]
env={"__name__":"pure_fixture_guard_definitions"}
exec(compile(ast.Module(body=body,type_ignores=[]),"pure-fixture-definitions","exec"),env)
m=env["metadata"]()
assert m==json.loads((ROOT/"METADATA.json").read_bytes())
old=json.loads((PARENT/"METADATA.json").read_bytes())
pins=json.loads((ROOT.parent/"opening-ci-original-test-fixtures-root-r1/FIXTURE-PINS.json").read_bytes())
paths={x["path"] for x in pins["files"]}
assert m["source"]==old["source"] and m["sourceDigest"]==old["sourceDigest"]
assert [x for x in m["support"] if x["path"] not in paths]==old["support"]
assert m["blobPins"][:50]==old["blobPins"][:50] and m["blobPins"][-3:]==old["blobPins"][-3:]
assert len(m["source"])==98 and len(m["support"])==32 and len(m["blobPins"])==55
assert {k:v for k,v in m.items() if k not in ("support","blobPins")}=={k:v for k,v in old.items() if k not in ("support","blobPins")}
cases=["fixed55_metadata_literal_exact","only2_support32_direct52_added_original98_source76e5_unchanged"]
for pin in pins["files"]:
    data=Path(pin["bodyPath"]).read_bytes()
    assert len(data)==pin["bytes"] and hashlib.sha256(data).hexdigest()==pin["sha256"]
    assert hashlib.sha1(b"blob "+str(len(data)).encode()+b"\x00"+data).hexdigest()==pin["gitBlobSHA1"]
    support=next(x for x in m["support"] if x["path"]==pin["path"])
    assert support=={k:pin[k] for k in ("path","sha256","bytes")}|{"blob":pin["sha256"]}
    acquisition=next(x for x in m["blobPins"] if x["gitPath"]==pin["path"])
    assert acquisition=={"gitPath":pin["path"],**{k:pin[k] for k in ("gitBlobSHA1","bytes","sha256")}}
cases.append("both_original_fixture_size_SHA256_gitframedSHA1_verified")
root=Path("/owned")
expected={x["path"]:{"sha256":x["sha256"],"bytes":x["bytes"]} for x in m["source"]+m["support"]}
rows=dict(expected)
receipts=[]
env["hash_file"]=lambda path:rows[path.relative_to(root/"stage").as_posix()]
env["receipt"]=lambda root,name,obj:receipts.append(obj)
def member_run(label,rejected=False):
    with patch.object(Path,"is_dir",lambda path:True),patch.object(Path,"is_symlink",lambda path:False),patch.object(os,"walk",lambda *args,**kw:iter([(str(root/"stage"),[],list(rows))])):
        try:
            env["membership"](root,m,label)
        except ValueError:
            assert rejected,label
        else:
            assert not rejected,label
    cases.append(label)
member_run("complete130_membership_admitted_source98_support32")
assert receipts[-1]["sourceDigest"]==old["sourceDigest"] and receipts[-1]["supportCount"]==32
for missing in sorted(paths):
    rows=dict(expected);del rows[missing]
    member_run("missing_fixture_rejected_"+missing,True)
rows=dict(expected)
target=sorted(paths)[0]
rows[target]={**rows[target],"sha256":"0"*64}
member_run("changed_fixture_bytes_membership_rejected",True)
rows=dict(expected)
rows[target]={**rows[target],"bytes":rows[target]["bytes"]+1}
member_run("changed_fixture_size_membership_rejected",True)
old_functions={n.name:ast.get_source_segment((PARENT/"runner.py").read_text(),n) for n in ast.parse((PARENT/"runner.py").read_text()).body if isinstance(n,ast.FunctionDef)}
new_functions={n.name:ast.get_source_segment(source,n) for n in tree.body if isinstance(n,ast.FunctionDef)}
assert set(old_functions)==set(new_functions)
assert sorted(n for n in old_functions if old_functions[n]!=new_functions[n])==["acquire","assemble","membership","metadata"]
assert new_functions["acquire"].replace('"expected": 55','"expected": 53').replace('len(rows)==55','len(rows)==53')==old_functions["acquire"]
assert new_functions["assemble"].replace('"supportFiles":32','"supportFiles":30')==old_functions["assemble"]
cases.append("only4_metadata_count_receipt_functions_change_all_phase_resource_guards_exactR9")
(ROOT/"FIXTURE-CHECKS.json").write_text(json.dumps({"status":"PASS_PURE_SOURCE_ONLY","caseCount":len(cases),"cases":cases,
    "methodSHA256":hashlib.sha256(source.encode()).hexdigest(),"candidateMainArchiveNetworkNpmBuildBrowserExecuted":False},separators=(",",":"))+"\n")
print(json.dumps({"status":"PASS_PURE_SOURCE_ONLY","caseCount":len(cases)}))
