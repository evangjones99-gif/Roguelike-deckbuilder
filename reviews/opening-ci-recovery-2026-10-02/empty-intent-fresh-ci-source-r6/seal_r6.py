"""Seal R6 cap-only successor; do not execute the retained failed R5 generator."""
import ast
import base64
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import yaml

ROOT=Path(__file__).parent
PARENT=ROOT.parent/"empty-intent-fresh-ci-source-r5"
CAP=320*1024
def packed(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()+b"\n"
def sha(data):
    return hashlib.sha256(data).hexdigest()
def identity(path):
    data=path.read_bytes()
    return {"sha256":sha(data),"bytes":len(data)}
def save(name,obj):
    (ROOT/name).write_bytes(packed(obj))

parent_seal=json.loads((PARENT/"SOURCE-SEAL.json").read_bytes())
for name,pin in parent_seal["files"].items():
    assert identity(PARENT/name)==pin,name
assert sum(p.stat().st_size for p in PARENT.rglob("*") if p.is_file())==277566
for name in ("runner.py","rebuild-opening-baseline.yml","METADATA.json","RACE-CHECKS.json","SOURCE-CHECKS.json",
             "SHARED-SHIM-CHECKS.json","race_checks.py","source_checks.py","shared_shim_checks.py",
             "FORWARD.json.gz","INVERSE.json.gz","INVERSE-ORIGINALS.json.gz"):
    assert (ROOT/name).read_bytes()==(PARENT/name).read_bytes(),name
save("FAILED-R5-SOURCE-CAP.json",{"status":"FAILED_SOURCE_CAP","sourceFamilyPath":str(PARENT),
    "measuredInclusiveBytes":277566,"admittedCapBytes":262144,"excessBytes":15422,
    "failedSeal":identity(PARENT/"SOURCE-SEAL.json"),"failedManifest":identity(PARENT/"MANIFEST.json"),
    "failure":"R5 generator wrote manifest/seal then final actual<=262144 assertion failed; all bytes preserved unchanged.",
    "actualRuntimeExecution":False,"newAuthority":"Root admits NEW R6 320KiB only, not retroactive R5 compliance or runtime increase."})
save("FAILED-R6-PATCH-LAUNCH-1.json",{"status":"FAILED_TOOL_PATCH_ONLY","reason":"apply_patch refused delete/add same target before any mutation; retained copied R5 generator unchanged and added distinct seal_r6.py instead.","candidateExecution":False})
save("SOURCE-ADMISSION.json",{"sourceCapBytes":CAP,"ordinaryWorkMiB":64,"reserveMiB":512,"ownDiskMiB":24,
    "measuredSizingReason":"R5 inclusive277566B exceeded256KiB by15422B with full inverse/grammar/source receipts; R6 adds exact failed-parent/full inverse retention. Root explicitly granted320KiB SOURCE only.",
    "executionScope":"Read-only grammar/identity checks; exact R5 isolated cases reused without repeated fixture mutations.",
    "runtimeBudgetChange":False,"remoteWriter":"Root"})
provenance=json.loads((PARENT/"PROVENANCE.json").read_bytes())
provenance["functionalR4Parent"]=provenance.pop("parentSource")
provenance["parentSource"]={"path":str(PARENT),"seal":identity(PARENT/"SOURCE-SEAL.json"),"manifest":identity(PARENT/"MANIFEST.json"),"sourceCapStatus":"FAILED"}
provenance["R6RuntimeMethodWorkflowMetadataByteExactR5"]=True
provenance["actualR6CI"]="PENDING; separately reviewed/authorized CI required"
provenance.pop("actualR5CI",None)
save("PROVENANCE.json",provenance)
readme=(PARENT/"README.md").read_text().replace("R5 SOURCE-only supervisor sampling repair","R6 SOURCE-only successor retaining exact R5 supervisor repair")
readme=readme.replace("Source cap256KiB includes this entire recursive family and seal.",
    "R5 sealed277566B exceeded262144B and remains FAILED and unchanged. Root explicitly admitted this NEW R6 SOURCE family at320KiB for full provenance/failed-cap retention; runtime caps/argv/actions/source inputs are unchanged. PREDECESSOR-* and R6 inverse preserve exact failed R5. Runtime method/workflow/metadata are byte-identical to R5; the36+34+17 functional SOURCE cases are reused by exact source hashes without repeated fixture mutation. Retained seal_source.py is the failed R5 generator; seal_r6.py is this successor generator.")
(ROOT/"README.md").write_text(readme)
python_rows=[]
for path in sorted(ROOT.glob("*.py")):
    compile(ast.parse(path.read_text(),filename=str(path)),str(path),"exec")
    python_rows.append({"file":path.name,**identity(path)})
shells=[]
blocks=[]
for step in yaml.safe_load((ROOT/"rebuild-opening-baseline.yml").read_bytes())["jobs"]["fresh-baseline"]["steps"]:
    if "run" not in step:
        continue
    run=step["run"]
    p=subprocess.run(["bash","-n"],input=run,text=True,capture_output=True,timeout=5)
    assert p.returncode==0,p.stderr
    shells.append(step["id"])
    if "<<'PY'\n" in run:
        block=run[run.index("<<'PY'\n")+len("<<'PY'\n"):run.rindex("\nPY")]
        compile(ast.parse(block),step["id"],"exec")
        blocks.append({"step":step["id"],"pythonSHA256":sha(block.encode())})
save("SOURCE-GRAMMAR-FINAL.json",{"status":"PASS_GRAMMAR_SOURCE_ONLY","pythonFiles":python_rows,
    "workflowPythonBlocks":blocks,"bashNRunStepIDs":shells,"originalBuildNodeCheck":"Exact unchanged body and successful R5 receipt reused.",
    "candidateMainNpmNetworkArchiveBuildBrowserExecuted":False})
entries={}
for path in sorted(PARENT.rglob("*")):
    assert not path.is_symlink()
    if not path.is_file():
        continue
    rel=path.relative_to(PARENT).as_posix()
    pin=identity(path)
    current=ROOT/rel
    if current.is_file() and identity(current)==pin:
        entries[rel]={**pin,"exactCurrentFile":rel}
    else:
        entries[rel]={**pin,"originalBase64":base64.b64encode(path.read_bytes()).decode()}
(ROOT/"R6-INVERSE.json.gz").write_bytes(gzip.compress(packed({"status":"PASS_EXACT_FULL_R5_INVERSE","parent":str(PARENT),"files":entries,"parentInclusiveBytes":277566}),mtime=0))
for rel,entry in entries.items():
    restored=(ROOT/entry["exactCurrentFile"]).read_bytes() if "exactCurrentFile" in entry else base64.b64decode(entry["originalBase64"],validate=True)
    assert len(restored)==entry["bytes"] and sha(restored)==entry["sha256"]
    assert restored==(PARENT/rel).read_bytes(),rel
save("R6-FORWARD.json",{"status":"PASS_EXACT_CAP_ONLY_SUCCESSOR","parentSeal":identity(PARENT/"SOURCE-SEAL.json"),
    "runner":identity(ROOT/"runner.py"),"workflow":identity(ROOT/"rebuild-opening-baseline.yml"),"metadata":identity(ROOT/"METADATA.json"),
    "runtimeBodiesByteExactR5":True,"changedBookkeepingFiles":[name for name,e in entries.items() if "originalBase64" in e],
    "R5FullInverse":identity(ROOT/"R6-INVERSE.json.gz"),"R4FunctionalForwardInverseRetained":True,"functionalChecksReusedExactSource":True,
    "independentReview":"PENDING"})
files={p.relative_to(ROOT).as_posix():identity(p) for p in sorted(ROOT.rglob("*")) if p.is_file() and p.name not in ("MANIFEST.json","SOURCE-SEAL.json")}
for count in range(8):
    inclusive=sum(p.stat().st_size for p in ROOT.rglob("*") if p.is_file())
    save("MANIFEST.json",{"status":"FROZEN_SOURCE_R6_UNREVIEWED","files":files,"sourceCapBytes":CAP,
         "inclusiveFamilyBytes":inclusive,"runtimeCI":"PENDING","actualPredecessorFaultSite":"UNOBSERVED"})
    save("SOURCE-SEAL.json",{"status":"FROZEN_SOURCE_R6_UNREVIEWED","manifest":identity(ROOT/"MANIFEST.json"),
         "files":files,"inclusiveFamilyBytes":inclusive,"sourceCapBytes":CAP,"candidateMainNpmNetworkArchiveBuildBrowserExecuted":False})
    actual=sum(p.stat().st_size for p in ROOT.rglob("*") if p.is_file())
    if actual==inclusive:
        break
else:
    raise AssertionError("family fixed point")
assert actual<=CAP,actual
print(json.dumps({"status":"FROZEN_SOURCE_R6_UNREVIEWED","bytes":actual,"seal":identity(ROOT/"SOURCE-SEAL.json"),
      "manifest":identity(ROOT/"MANIFEST.json"),"runner":identity(ROOT/"runner.py"),"workflow":identity(ROOT/"rebuild-opening-baseline.yml")}))
