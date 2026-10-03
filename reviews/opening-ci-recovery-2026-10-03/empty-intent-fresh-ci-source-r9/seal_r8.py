"""R8 preservation/cap successor; shared native method is exact failed-budget R7."""
import ast
import base64
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import yaml

ROOT=Path(__file__).parent
PARENT=ROOT.parent/"empty-intent-fresh-ci-source-r7"
CAP=640*1024
def packed(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()+b"\n"
def sha(data):
    return hashlib.sha256(data).hexdigest()
def identity(path):
    b=path.read_bytes()
    return {"sha256":sha(b),"bytes":len(b)}
def save(name,obj):
    (ROOT/name).write_bytes(packed(obj))

parent_files={p.relative_to(PARENT).as_posix():identity(p) for p in sorted(PARENT.rglob("*")) if p.is_file()}
parent_total=sum(x["bytes"] for x in parent_files.values())
assert parent_total==437345
for name in parent_files:
    assert identity(ROOT/name)==parent_files[name],name
assert not (PARENT/"MANIFEST.json").exists() and not (PARENT/"SOURCE-SEAL.json").exists()
save("R7-PARENT-INVENTORY.json",{"status":"RETAINED_FAILED_SOURCE_BUDGET_DRAFT","path":str(PARENT),
     "files":parent_files,"rawInclusiveBytes":parent_total,"failedBudgetReceipt":identity(PARENT/"FAILED-SOURCE-CAP.json"),
     "runtimeMethodWorkflowExactCurrent":True})
save("SOURCE-ADMISSION.json",{"sourceCapBytes":CAP,"ordinaryWorkMiB":64,"reserveMiB":512,"ownDiskMiB":24,
     "authority":"Root expressly authorized NEW R8 SOURCE640KiB to retain R7 original197053B inverse, complete failures and bookkeeping. No R7 retroactive compliance.",
     "nativeFileCountAllowance":"Root separately authorized selected native inventory100→4096 based actual old-count failure; actual native total unknown.",
     "unchangedLimits":"Memory/disk/log/time/lifecycle and original input/output counts.",
     "execution":"Read-only grammar and exact inverse/hash checks;25+34+17 validated R7 cases reused by exactruntime source identity.",
     "remoteWriter":"Root"})
provenance=json.loads((PARENT/"PROVENANCE.json").read_bytes())
provenance["R8Parent"]={"path":str(PARENT),"rawInclusiveBytes":parent_total,"failedBudgetReceipt":identity(PARENT/"FAILED-SOURCE-CAP.json")}
provenance["R8SharedRuntimeExactR7"]=True
provenance["independentR8Review"]="PENDING"
provenance["actualR8CI"]="PENDING"
save("PROVENANCE.json",provenance)
readme=(PARENT/"README.md").read_text()
(ROOT/"README.md").write_text("""R8 SOURCE-only preservation successor

R7's pre-seal projected439487B exceeded its393216B SOURCE allowance; no frozen manifest/seal was written. Its complete raw437345B family including additive failed-budget receipt remains unchanged. Root authorized this distinct R8 SOURCE640KiB to preserve the original197053B full R6 inverse and all diagnostics. No encoding was moved, optimized, removed or replaced to fit a cap. package_source.py remains the failed R7 generator; seal_r8.py produces this successor.

Runtime runner/workflow/metadata and25+34+17 existing source case proofs are byte-identical to R7, reused without fixture or functional-test churn. The narrowly authorized native file-count changes100→4096; memory/disk/log/time/lifecycle and source/output count limits are unchanged. No R7 retroactive pass or actual R8 CI/build/test acceptance follows.

R7-PARENT-INVENTORY binds every original file. R8-INVERSE reconstructs each R7 body using exact unchanged current bodies or lossless old changed-bookkeeping bytes, including failed receipt. The original raw INVERSE-FULL-R6.json.gz and R6/R7 forward/inverse patches remain present unchanged, preserving all R6 and R5 failure ancestry. Read-only checks confirm complete source restoration and grammar. Root is sole remote writer; independent R8 review and separately authorized actual execution remain pending.

The retained R7 method and scope description follows:

"""+readme)

for name in ("runner.py","rebuild-opening-baseline.yml","METADATA.json","NATIVE-CHECKS.json","SOURCE-CHECKS.json","SHARED-SHIM-CHECKS.json"):
    assert identity(ROOT/name)==parent_files[name],name
proof=json.loads((ROOT/"INVERSE-FULL-R6.json.gz").read_bytes()) if False else json.loads(gzip.decompress((ROOT/"INVERSE-FULL-R6.json.gz").read_bytes()))
restored_count=restored_bytes=0
for name,row in proof["files"].items():
    b=base64.b64decode(row["base64"],validate=True)
    assert len(b)==row["bytes"] and sha(b)==row["sha256"]
    assert b==(ROOT.parent/"empty-intent-fresh-ci-source-r6"/name).read_bytes()
    restored_count+=1
    restored_bytes+=len(b)
assert restored_bytes==304597
grammar=[]
for path in sorted(ROOT.glob("*.py")):
    compile(ast.parse(path.read_text(),filename=str(path)),str(path),"exec")
    grammar.append({"file":path.name,**identity(path)})
shells=[]
blocks=[]
job=yaml.safe_load((ROOT/"rebuild-opening-baseline.yml").read_text())["jobs"]["fresh-baseline"]
for step in job["steps"]:
    if "run" not in step:
        continue
    run=step["run"]
    process=subprocess.run(["bash","-n"],input=run,text=True,capture_output=True,timeout=5)
    assert process.returncode==0,process.stderr
    shells.append(step["id"])
    if "<<'PY'\n" in run:
        text=run[run.index("<<'PY'\n")+len("<<'PY'\n"):run.rindex("\nPY")]
        compile(ast.parse(text),step["id"],"exec")
        blocks.append({"step":step["id"],"pythonSHA256":sha(text.encode())})
save("SOURCE-GRAMMAR-FINAL.json",{"status":"PASS_SOURCE_GRAMMAR_ONLY","pythonFiles":grammar,"bashNRunStepIDs":shells,
     "workflowPythonBlocks":blocks,"functionalCases":"ExactR7 proof bodies reused25+34+17, no rerun.",
     "fullR6InverseFiles":restored_count,"fullR6InverseBytes":restored_bytes,
     "candidateMainNpmNetworkArchiveBuildBrowserExecuted":False})

inverse={}
for name,pin in parent_files.items():
    if (ROOT/name).is_file() and identity(ROOT/name)==pin:
        inverse[name]={**pin,"exactCurrentFile":name}
    else:
        inverse[name]={**pin,"originalBase64":base64.b64encode((PARENT/name).read_bytes()).decode()}
(ROOT/"R8-INVERSE.json.gz").write_bytes(gzip.compress(packed({"status":"PASS_FULL_EXACT_R7_INVERSE","files":inverse,"rawParentBytes":parent_total}),mtime=0))
for name,row in inverse.items():
    b=(ROOT/row["exactCurrentFile"]).read_bytes() if "exactCurrentFile" in row else base64.b64decode(row["originalBase64"],validate=True)
    assert len(b)==row["bytes"] and sha(b)==row["sha256"] and b==(PARENT/name).read_bytes()
save("R8-FORWARD.json",{"status":"PASS_EXACT_RUNTIME_IDENTITY_CAP_SUCCESSOR","parentInventory":identity(ROOT/"R7-PARENT-INVENTORY.json"),
     "runtimeMethod":identity(ROOT/"runner.py"),"workflow":identity(ROOT/"rebuild-opening-baseline.yml"),"metadata":identity(ROOT/"METADATA.json"),
     "changedBookkeepingFiles":[n for n,x in inverse.items() if "originalBase64" in x],"inverse":identity(ROOT/"R8-INVERSE.json.gz"),
     "originalR7FilesAnd197053InversePreserved":True,"independentReview":"PENDING"})
files={p.relative_to(ROOT).as_posix():identity(p) for p in sorted(ROOT.rglob("*")) if p.is_file() and p.name not in ("MANIFEST.json","SOURCE-SEAL.json")}
base_bytes=sum(x["bytes"] for x in files.values())
inclusive=base_bytes
for count in range(8):
    manifest=packed({"status":"FROZEN_SOURCE_R8_UNREVIEWED","files":files,"inclusiveFamilyBytes":inclusive,"sourceCapBytes":CAP,"actualCI":"PENDING"})
    seal=packed({"status":"FROZEN_SOURCE_R8_UNREVIEWED","files":files,"inclusiveFamilyBytes":inclusive,"sourceCapBytes":CAP,
       "manifest":{"sha256":sha(manifest),"bytes":len(manifest)},"candidateMainNpmNetworkArchiveBuildBrowserExecuted":False})
    actual=base_bytes+len(manifest)+len(seal)
    if actual==inclusive:
        break
    inclusive=actual
else:
    raise AssertionError("family fixed point")
assert inclusive<=CAP,(inclusive,CAP)
(ROOT/"MANIFEST.json").write_bytes(manifest)
(ROOT/"SOURCE-SEAL.json").write_bytes(seal)
assert sum(p.stat().st_size for p in ROOT.rglob("*") if p.is_file())==inclusive
print(json.dumps({"status":"FROZEN_SOURCE_R8_UNREVIEWED","inclusiveBytes":inclusive,"capBytes":CAP,
     "seal":identity(ROOT/"SOURCE-SEAL.json"),"manifest":identity(ROOT/"MANIFEST.json"),"runner":identity(ROOT/"runner.py"),
     "workflow":identity(ROOT/"rebuild-opening-baseline.yml"),"metadata":identity(ROOT/"METADATA.json")}))
