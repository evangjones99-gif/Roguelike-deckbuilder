"""R9 source-only test memory admission change, with full exact R8 inversion."""
import ast
import base64
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import yaml

ROOT=Path(__file__).parent
PARENT=ROOT.parent/"empty-intent-fresh-ci-source-r8"
ACTUAL=ROOT.parent/"opening-ci-test-limit-failure-root-r1"
CAP=1048576
def packed(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()+b"\n"
def sha(b):
    return hashlib.sha256(b).hexdigest()
def identity(path):
    b=path.read_bytes()
    return {"sha256":sha(b),"bytes":len(b)}
def save(name,obj):
    (ROOT/name).write_bytes(packed(obj))
def block(source):
    return "          source = r'''"+source.replace("\n","\n          ")+"'''\n"
old=(PARENT/"runner.py").read_text()
new=(ROOT/"runner.py").read_text()
old_call='run_phase(root,name,["npm","test"],55,60,384*MIB)'
new_call='run_phase(root,name,["npm","test"],55,60,768*MIB)'
assert old.count(old_call)==1 and new==old.replace(old_call,new_call)
old_w=(PARENT/"rebuild-opening-baseline.yml").read_text()
new_w=(ROOT/"rebuild-opening-baseline.yml").read_text()
assert new_w==old_w.replace(block(old),block(new)).replace(sha(old.encode()),sha(new.encode()))
old_f={n.name:ast.get_source_segment(old,n) for n in ast.parse(old).body if isinstance(n,ast.FunctionDef)}
new_f={n.name:ast.get_source_segment(new,n) for n in ast.parse(new).body if isinstance(n,ast.FunctionDef)}
assert set(old_f)==set(new_f)
assert sorted(n for n in old_f if old_f[n]!=new_f[n])==["phase"]
parent_seal=json.loads((PARENT/"SOURCE-SEAL.json").read_bytes())
for name,pin in parent_seal["files"].items():
    assert identity(PARENT/name)==pin,name
save("R9-SOURCE-ADMISSION.json",{"sourceCapBytes":CAP,"workMiB":64,"reserveMiB":512,"ownDiskMiB":24,
    "authority":"Root authorized NEW R9 SOURCE1MiB and test-only aggregate RSS allowance384→768MiB based actual concurrent original-suite cap failures.",
    "testWorkCapBytes":805306368,"installBuildWorkCapBytes":402653184,
    "unchanged":"Original npmtest argv/scripts/8test bodies; time,disk,log,proof,reserve512MiB,native4096,closure,credentials,input/output counts.",
    "noActualR9Execution":True,"remoteWriter":"Root"})
actual_receipt=json.loads((ACTUAL/"ROOT-RECEIPT.json").read_bytes())
assert sha((ACTUAL/"ROOT-RECEIPT.json").read_bytes())=="664cdc6ff808fb16a809201164ff5d93c556606d347f76daeee486a68a447fa3"
facts={}
for side in ("A","C"):
    closure=ACTUAL/side/"members/test-closure.json"
    body=json.loads(closure.read_bytes())
    assert body["reason"]=="sampled aggregate RSS cap" and body["exit"]==-15
    assert body["closureObserved"] and not body["liveAtClosure"] and body["workCapBytes"]==402653184
    facts[side]={"testClosure":body,"testClosureIdentity":identity(closure),"testLog":identity(ACTUAL/side/"members/test.log"),
        "buildClosure":identity(ACTUAL/side/"members/build-closure.json"),"nativeInventory06":identity(ACTUAL/side/"members/native-inventory-06.json")}
save("ACTUAL-TEST-CAP-FAILURE.json",{"rootReceipt":{"path":str(ACTUAL/"ROOT-RECEIPT.json"),**identity(ACTUAL/"ROOT-RECEIPT.json")},
    "head":actual_receipt["head"],"facts":facts,"provisionBuildPASS":True,"wholeSuiteTestOutputSealPASS":False,
    "partialSummaries":"A24pass6cancelled;C31pass6cancelled; partial suites only, no whole-suite success.",
    "memoryInference":"Observed owned aggregate workers exceeded384MiB while host/finite-cgroup headroom was about15GiB and OOM counters0.",
    "rawZIPsAll78MembersRetainedExternally":True})
save("R9-READONLY-CHECKS.json",{"status":"PASS_SOURCE_ONLY","method":identity(ROOT/"runner.py"),"workflow":identity(ROOT/"rebuild-opening-baseline.yml"),
    "onlyMethodDifference":old_call+" → "+new_call,"onlyChangedFunction":"phase",
    "allGuardFunctionsByteExactR8":True,"inherited76CasesReused":"25native+34source+17shim guard cases; original proof hashes remain bound to R8, selected tested funcs untouched.",
    "workflowOutsideEmbeddedMethodAndHashesExactR8":True,"metadataExactR8":(ROOT/"METADATA.json").read_bytes()==(PARENT/"METADATA.json").read_bytes(),
    "mainNpmBuildBrowserNetworkExecuted":False})
save("R9-PROVENANCE.json",{"parentSeal":{"path":str(PARENT/"SOURCE-SEAL.json"),**identity(PARENT/"SOURCE-SEAL.json")},
    "parentManifest":identity(PARENT/"MANIFEST.json"),"independentParentGate":{"path":str(ROOT.parent/"empty-intent-fresh-ci-technical-r8/GATE.json"),
     **identity(ROOT.parent/"empty-intent-fresh-ci-technical-r8/GATE.json")},
    "retainedEarlierInverseAndFailureBodies":"All complete R8 paths copied; full R6/R7/R8 inversion ancestry and old failure receipts retained.",
    "testMemoryChangedOnly":True,"sourceGameAssetsAndPackageLockTestsUnchanged":True,"actualR9CI":"PENDING","independentR9Review":"PENDING"})
(ROOT/"README.md").write_text("""R9 SOURCE-only test-phase memory admission

R8 and candidateC3 both provisioned and built successfully, including observed native TypeScript114 files. Original npmtest was then terminated by the owned aggregate384MiB RSS cap: A549347328B and C579641344B sampled peaks, exit-15, clean observed closure and OOM counters0. Logs retain partial A24pass/6cancelled and C31pass/6cancelled; neither suite nor output seal passed. About15GiB observed available headroom supports Root's separately authorized test-only768MiB allowance, not a prediction of successful retry.

The only functional change is phase(test)'s run_phase workcap384→768MiB (805306368B). Original npmtest argv/scripts/8test bodies and install/build384MiB stay. Time/disk/log/proof/reserve512MiB/native4096/closure/credentials/input/output counts are unchanged. Existing sampled resource limitations remain; no dedicated hard cgroup or unseen peak guarantee. SOURCE1MiB is a distinct new family cap.

R9-READONLY-CHECKS proves the complete runner differs by exactly one literal call argument, only phase changes, all guard funcs remain byte-identical, and outer workflow is unchanged apart from embedded source/hash bindings. All76 inherited native/source/shim cases apply to exact untouched guard functions; original proof receipts are retained with their original R8 hashes, no fixture reruns. Grammar checks compile every Python AST and inline block and bash-n all9 run strings. Full R8 inversion restores every464060B regular-file body; earlier raw failure/source/inverse paths stay unchanged. Historical SOURCE-ADMISSION/PROVENANCE/READMEs in preserved inverse packets describe their own versions; R9-* carries current authority.

Root alone publishes. Independent R9 SOURCE review and actual retry are pending. No main/npm/build/browser/network/remote execution occurred here, no whole-suite/output/runtime/default/art/gameplay/fun acceptance follows. Retained old seal generators are historical; seal_r9.py produces this packet.
""")
grammar=[]
for path in sorted(ROOT.glob("*.py")):
    compile(ast.parse(path.read_text(),filename=str(path)),str(path),"exec")
    grammar.append({"file":path.name,**identity(path)})
shells=[]
blocks=[]
for step in yaml.safe_load(new_w)["jobs"]["fresh-baseline"]["steps"]:
    if "run" not in step:
        continue
    run=step["run"]
    p=subprocess.run(["bash","-n"],input=run,text=True,capture_output=True,timeout=5)
    assert p.returncode==0,p.stderr
    shells.append(step["id"])
    if "<<'PY'\n" in run:
        text=run[run.index("<<'PY'\n")+len("<<'PY'\n"):run.rindex("\nPY")]
        compile(ast.parse(text),step["id"],"exec")
        blocks.append({"step":step["id"],"pythonSHA256":sha(text.encode())})
save("R9-GRAMMAR.json",{"status":"PASS_SOURCE_GRAMMAR_ONLY","pythonFiles":grammar,"bashNRunStepIDs":shells,"workflowPythonBlocks":blocks,
    "candidateMainNpmBuildBrowserNetworkExecuted":False})
inverse={}
total=0
for path in sorted(PARENT.rglob("*")):
    assert not path.is_symlink()
    if not path.is_file():
        continue
    rel=path.relative_to(PARENT).as_posix()
    pin=identity(path)
    total+=pin["bytes"]
    if (ROOT/rel).is_file() and identity(ROOT/rel)==pin:
        inverse[rel]={**pin,"exactCurrentFile":rel}
    else:
        inverse[rel]={**pin,"originalBase64":base64.b64encode(path.read_bytes()).decode()}
assert total==464060
(ROOT/"R9-INVERSE.json.gz").write_bytes(gzip.compress(packed({"status":"PASS_FULL_R8_INVERSE","parentBytes":total,"files":inverse}),mtime=0))
for rel,row in inverse.items():
    b=(ROOT/row["exactCurrentFile"]).read_bytes() if "exactCurrentFile" in row else base64.b64decode(row["originalBase64"],validate=True)
    assert len(b)==row["bytes"] and sha(b)==row["sha256"] and b==(PARENT/rel).read_bytes()
save("R9-FORWARD.json",{"status":"PASS_EXACT_ONE_LITERAL_CHANGE","runnerBefore":identity(PARENT/"runner.py"),"runnerAfter":identity(ROOT/"runner.py"),
    "workflowBefore":identity(PARENT/"rebuild-opening-baseline.yml"),"workflowAfter":identity(ROOT/"rebuild-opening-baseline.yml"),
    "forwardRule":"Replace sole npmtest run_phase384*MIB with768*MIB and update exactembedded method/hash; all other method/workflow bytes unchanged.",
    "R8FullFamilyInverse":identity(ROOT/"R9-INVERSE.json.gz"),"completeParentCoverage":True})
files={p.relative_to(ROOT).as_posix():identity(p) for p in sorted(ROOT.rglob("*")) if p.is_file() and p.name not in ("MANIFEST.json","SOURCE-SEAL.json")}
base=sum(x["bytes"] for x in files.values())
inclusive=base
for count in range(8):
    manifest=packed({"status":"FROZEN_SOURCE_R9_UNREVIEWED","files":files,"inclusiveFamilyBytes":inclusive,"sourceCapBytes":CAP,"actualCI":"PENDING"})
    seal=packed({"status":"FROZEN_SOURCE_R9_UNREVIEWED","files":files,"inclusiveFamilyBytes":inclusive,"sourceCapBytes":CAP,
        "manifest":{"sha256":sha(manifest),"bytes":len(manifest)},"candidateMainNpmBuildBrowserNetworkExecuted":False})
    actual=base+len(manifest)+len(seal)
    if actual==inclusive:
        break
    inclusive=actual
else:
    raise AssertionError("family fixed point")
assert inclusive<=CAP,(inclusive,CAP)
(ROOT/"MANIFEST.json").write_bytes(manifest)
(ROOT/"SOURCE-SEAL.json").write_bytes(seal)
assert sum(p.stat().st_size for p in ROOT.rglob("*") if p.is_file())==inclusive
print(json.dumps({"inclusiveBytes":inclusive,"capBytes":CAP,"seal":identity(ROOT/"SOURCE-SEAL.json"),"manifest":identity(ROOT/"MANIFEST.json"),
     "runner":identity(ROOT/"runner.py"),"workflow":identity(ROOT/"rebuild-opening-baseline.yml"),"metadata":identity(ROOT/"METADATA.json")}))
