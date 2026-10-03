"""R10 fixture support SOURCE sealing, grammar and exact complete R9 inverse only."""
import ast
import base64
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import yaml

ROOT=Path(__file__).parent
PARENT=ROOT.parent/"empty-intent-fresh-ci-source-r9"
ACTUAL=ROOT.parent/"opening-ci-fixture-failure-root-r1"
FIXTURE=ROOT.parent/"opening-ci-original-test-fixtures-root-r1"
CAP=2097152
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
old_w=(PARENT/"rebuild-opening-baseline.yml").read_text()
new_w=(ROOT/"rebuild-opening-baseline.yml").read_text()
old_m=(PARENT/"METADATA.json").read_bytes()
new_m=(ROOT/"METADATA.json").read_bytes()
expected_w=old_w.replace(block(old),block(new)).replace(sha(old.encode()),sha(new.encode())).replace(sha(old_m),sha(new_m))
assert new_w==expected_w
parent_seal=json.loads((PARENT/"SOURCE-SEAL.json").read_bytes())
for name,pin in parent_seal["files"].items():
    assert identity(PARENT/name)==pin,name
save("R10-SOURCE-ADMISSION.json",{"sourceCapBytes":CAP,"ordinaryWorkMiB":64,"reserveMiB":512,"ownDiskMiB":24,
    "authority":"Root authorized NEW R10 SOURCE2MiB and adding exactly two original readFile data fixtures only.",
    "intentionalCountChanges":{"support":[30,32],"stagePinnedFiles":[128,130],"directBlobs":[50,52],"allBlobs":[53,55]},
    "runtimeSource":"Original98/source76e5 unchanged; original test/script/package/lock bodies unchanged.",
    "unchangedBounds":"test768MiB/installbuild384MiB/time/disk/log/proof/reserve/native4096/closure/credentials/outputcounts",
    "noActualR10Execution":True,"remoteWriter":"Root"})
assert sha((FIXTURE/"FIXTURE-PINS.json").read_bytes())=="2e4e82387617f1a013d159869a8a1facd20c4b4f6728501c6f43da4616c714da"
assert (ROOT/"ORIGINAL-FIXTURE-PINS.json").read_bytes()==(FIXTURE/"FIXTURE-PINS.json").read_bytes()
for pin in json.loads((ROOT/"ORIGINAL-FIXTURE-PINS.json").read_bytes())["files"]:
    data=(ROOT/"original-fixture-bodies"/pin["path"]).read_bytes()
    assert len(data)==pin["bytes"] and sha(data)==pin["sha256"]
    assert hashlib.sha1(b"blob "+str(len(data)).encode()+b"\x00"+data).hexdigest()==pin["gitBlobSHA1"]
actual=json.loads((ACTUAL/"ROOT-RECEIPT.json").read_bytes())
assert sha((ACTUAL/"ROOT-RECEIPT.json").read_bytes())=="1ea76cca177d79eec22e0490d962947167bb8792d78dca899499ae5d377c8f3d"
facts={}
for side in ("A","C"):
    test=ACTUAL/side/"members/test-closure.json"
    body=json.loads(test.read_bytes())
    assert body["exit"]==1 and body["reason"] is None and body["closureObserved"] and not body["liveAtClosure"]
    assert body["workCapBytes"]==805306368
    facts[side]={"testClosure":body,"identity":identity(test),"testLog":identity(ACTUAL/side/"members/test.log")}
save("ACTUAL-FIXTURE-FAILURE.json",{"rootReceipt":{"path":str(ACTUAL/"ROOT-RECEIPT.json"),**identity(ACTUAL/"ROOT-RECEIPT.json")},
    "head":actual["head"],"facts":facts,"outcome":"Both107tests104pass3fail0cancelled; exit1 ENOENT two archived datafixtures. Provision/build PASS, outputseal absent.",
    "oldFailuresOriginal90FilesAndZIPsRetained":True,"noMemoryOverflowObserved":True})
save("R10-PROVENANCE.json",{"parentSource":{"path":str(PARENT),"seal":identity(PARENT/"SOURCE-SEAL.json"),"manifest":identity(PARENT/"MANIFEST.json")},
    "parentIndependentGate":{"path":str(ROOT.parent/"empty-intent-fresh-ci-technical-r9/GATE.json"),
          **identity(ROOT.parent/"empty-intent-fresh-ci-technical-r9/GATE.json")},
    "originalFixturePins":{"path":str(FIXTURE/"FIXTURE-PINS.json"),**identity(FIXTURE/"FIXTURE-PINS.json")},
    "staticTestClosure":identity(ROOT/"TEST-CLOSURE-AUDIT.json"),"focusedFixtureChecks":identity(ROOT/"FIXTURE-CHECKS.json"),
    "originalRuntimeTestsScriptsToolsNoChanges":True,"independentR10Review":"PENDING","actualR10CI":"PENDING"})
(ROOT/"README.md").write_text("""R10 SOURCE-only original test data support

R9/C4 tests completed within768MiB: both107 tests,104 pass,3 fail,0 cancelled; exit1 with ENOENT for two omitted original archived fixtures. Provision/build passed; outputseal did not. Root's original90-file failure/ZIP packet stays intact. This repair adds the exact original silence-overflow-campaign.json17880B/Git0356b84f and golden-vectors-r1.json2892B/Gitead26214, fetched at immutablefbb617ef, measured SHA256 and Git-framed SHA1 verified. Local source review copies and exact primary pin receipt are retained; runtime acquisition uses their fixed Git blob IDs, never fabricated data.

Support30→32, pinned stage128→130, direct acquisition50→52 and total blobs53→55 are intentional. Runtime source98/source76e5, original8 test bodies/scripts/package/lock/tools and expected64 output count stay. Exact JSON bytes pass normal direct-blob download/readback/assembly/hash and full membership gates; both are support only and excluded from runtime source digest. New pins are inserted before the unchanged last3 archive pins, preserving streaming assembly's existing archive loop.

The read-only static closure audit covers all8 exact tests and27 pinned module/data bodies. It records static/literal dynamic/type imports, three literal JSON readURL sites for exactly these two missing files, two existing engine/content hash reads, and the existing write:false esbuild src/audio-host input/data-URL import. No other static read dependency was missing. This is source inspection and bounded literal matching, not runtime filesystem tracing or general TypeScript-parser completeness. Nine pure metadata/direct-pin/membership cases admit130 complete bytes and refuse either missing fixture, wrong hash or size. Unchanged guards retain inherited source/provision proof ancestry; no fixture testing/game execution occurred.

Memory test768MiB/installbuild384MiB, time/disk/log/proof/reserve512MiB/native4096/closure/credential/output limits and original commands remain unchanged. Root separately authorized SOURCE2MiB. Every original R9 body, all failure/source/inverse ancestry and raw paths stay preserved; R10-INVERSE recreates the complete578687B parent family. R10-FORWARD binds the exact count/literal/metadata changes, and grammar verifies all Python/inline blocks and9 bash-n run strings. Historical generators/receipts describe their own versions; seal_r10.py and R10-* record this packet.

Root alone publishes. Independent SOURCE review and actual retry are pending. No main/npm/build/browser/network/remote execution happened here; no output/runtime/default/art/gameplay/fun acceptance or candidate selection follows.
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
    proc=subprocess.run(["bash","-n"],input=run,text=True,capture_output=True,timeout=5)
    assert proc.returncode==0,proc.stderr
    shells.append(step["id"])
    if "<<'PY'\n" in run:
        text=run[run.index("<<'PY'\n")+len("<<'PY'\n"):run.rindex("\nPY")]
        compile(ast.parse(text),step["id"],"exec")
        blocks.append({"step":step["id"],"pythonSHA256":sha(text.encode())})
save("R10-GRAMMAR.json",{"status":"PASS_SOURCE_GRAMMAR_ONLY","pythonFiles":grammar,"bashNRunStepIDs":shells,"workflowPythonBlocks":blocks,
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
assert total==578687
(ROOT/"R10-INVERSE.json.gz").write_bytes(gzip.compress(packed({"status":"PASS_FULL_R9_INVERSE","parentBytes":total,"files":inverse}),mtime=0))
for rel,row in inverse.items():
    b=(ROOT/row["exactCurrentFile"]).read_bytes() if "exactCurrentFile" in row else base64.b64decode(row["originalBase64"],validate=True)
    assert len(b)==row["bytes"] and sha(b)==row["sha256"] and b==(PARENT/rel).read_bytes()
save("R10-FORWARD.json",{"status":"PASS_FIXED2_SUPPORT_INPUTS","runnerBefore":identity(PARENT/"runner.py"),"runnerAfter":identity(ROOT/"runner.py"),
    "workflowBefore":identity(PARENT/"rebuild-opening-baseline.yml"),"workflowAfter":identity(ROOT/"rebuild-opening-baseline.yml"),
    "metadataBefore":identity(PARENT/"METADATA.json"),"metadataAfter":identity(ROOT/"METADATA.json"),
    "methodChanges":"META_SHA/literal plus4 functions metadata/acquire/assemble/membership fixed55/32/130 guards+receipts only.",
    "completeParentInverse":identity(ROOT/"R10-INVERSE.json.gz"),"original98SourceAndRuntimeResourceFunctionsExact":True,
    "workflowOuterOnlyEmbeddedMethodMetadataAndHashesChanged":True})
files={p.relative_to(ROOT).as_posix():identity(p) for p in sorted(ROOT.rglob("*")) if p.is_file() and p.name not in ("MANIFEST.json","SOURCE-SEAL.json")}
base=sum(x["bytes"] for x in files.values())
inclusive=base
for count in range(8):
    manifest=packed({"status":"FROZEN_SOURCE_R10_UNREVIEWED","files":files,"inclusiveFamilyBytes":inclusive,"sourceCapBytes":CAP,"actualCI":"PENDING"})
    seal=packed({"status":"FROZEN_SOURCE_R10_UNREVIEWED","files":files,"inclusiveFamilyBytes":inclusive,"sourceCapBytes":CAP,
        "manifest":{"sha256":sha(manifest),"bytes":len(manifest)},"candidateMainNpmBuildBrowserNetworkExecuted":False})
    actual_size=base+len(manifest)+len(seal)
    if actual_size==inclusive:
        break
    inclusive=actual_size
else:
    raise AssertionError("family fixed point")
assert inclusive<=CAP,(inclusive,CAP)
(ROOT/"MANIFEST.json").write_bytes(manifest)
(ROOT/"SOURCE-SEAL.json").write_bytes(seal)
assert sum(p.stat().st_size for p in ROOT.rglob("*") if p.is_file())==inclusive
print(json.dumps({"inclusiveBytes":inclusive,"capBytes":CAP,"seal":identity(ROOT/"SOURCE-SEAL.json"),"manifest":identity(ROOT/"MANIFEST.json"),
     "runner":identity(ROOT/"runner.py"),"workflow":identity(ROOT/"rebuild-opening-baseline.yml"),"metadata":identity(ROOT/"METADATA.json")}))
