"""Seal narrow SOURCE R7 and exact parent inversion; no candidate execution/network."""
import ast
import base64
import difflib
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess
import yaml

ROOT=Path(__file__).parent
PARENT=ROOT.parent/"empty-intent-fresh-ci-source-r6"
ACTUAL=ROOT.parent/"opening-fresh-ci-actual-failures-2026-10-03-root-r1"
CAP=384*1024
def packed(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()+b"\n"
def sha(data):
    return hashlib.sha256(data).hexdigest()
def identity(path):
    b=path.read_bytes()
    return {"sha256":sha(b),"bytes":len(b)}
def save(name,obj):
    (ROOT/name).write_bytes(packed(obj))
def block(source):
    return "          source = r'''"+source.replace("\n","\n          ")+"'''\n"

old=(PARENT/"runner.py").read_text()
new=(ROOT/"runner.py").read_text()
old_workflow=(PARENT/"rebuild-opening-baseline.yml").read_text()
new_workflow=(ROOT/"rebuild-opening-baseline.yml").read_text()
assert old_workflow.count(block(old))==1
assert old_workflow.replace(block(old),block(new)).replace(sha(old.encode()),sha(new.encode()))==new_workflow
assert (ROOT/"METADATA.json").read_bytes()==(PARENT/"METADATA.json").read_bytes()
parent_seal=json.loads((PARENT/"SOURCE-SEAL.json").read_bytes())
for name,pin in parent_seal["files"].items():
    assert identity(PARENT/name)==pin,name
parent_files={}
for path in sorted(PARENT.rglob("*")):
    assert not path.is_symlink()
    if path.is_file():
        parent_files[path.relative_to(PARENT).as_posix()]={**identity(path),"base64":base64.b64encode(path.read_bytes()).decode()}
inverse_bytes=gzip.compress(packed({"status":"PASS_EXACT_FULL_R6_PARENT","files":parent_files,
                     "inclusiveBytes":304597,"externalOriginal":str(PARENT)}),mtime=0)
assert sum(row["bytes"] for row in parent_files.values())==304597
for name,row in parent_files.items():
    restored=base64.b64decode(row["base64"],validate=True)
    assert len(restored)==row["bytes"] and sha(restored)==row["sha256"]
    assert restored==(PARENT/name).read_bytes()
(ROOT/"INVERSE-FULL-R6.json.gz").write_bytes(inverse_bytes)

def apply_diff(original,delta):
    lines=original.splitlines(keepends=True)
    patch=delta.splitlines(keepends=True)
    out=[]
    cursor=0
    i=2
    while i<len(patch):
        match=re.fullmatch(r"@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@.*\n",patch[i])
        assert match,patch[i]
        index=int(match[1])-1+(int(match[2] or "1")==0)
        assert index>=cursor
        out.extend(lines[cursor:index])
        cursor=index
        i+=1
        while i<len(patch) and not patch[i].startswith("@@ "):
            tag=patch[i][0]
            text=patch[i][1:]
            assert tag in " +-"
            if tag in " -":
                assert lines[cursor]==text
                cursor+=1
            if tag in " +":
                out.append(text)
            i+=1
    out.extend(lines[cursor:])
    return "".join(out)
forward={}
inverse={}
for name in ("runner.py","rebuild-opening-baseline.yml"):
    a=(PARENT/name).read_text()
    b=(ROOT/name).read_text()
    f="".join(difflib.unified_diff(a.splitlines(keepends=True),b.splitlines(keepends=True),fromfile="R6/"+name,tofile="R7/"+name))
    inv="".join(difflib.unified_diff(b.splitlines(keepends=True),a.splitlines(keepends=True),fromfile="R7/"+name,tofile="R6/"+name))
    assert apply_diff(a,f)==b and apply_diff(b,inv)==a
    forward[name]={"before":identity(PARENT/name),"after":identity(ROOT/name),"unifiedDiff":f,"exactRoundtrip":True}
    inverse[name]={"before":identity(ROOT/name),"after":identity(PARENT/name),"unifiedDiff":inv,"exactRoundtrip":True}
(ROOT/"FORWARD.json.gz").write_bytes(gzip.compress(packed(forward),mtime=0))
(ROOT/"INVERSE.json.gz").write_bytes(gzip.compress(packed(inverse),mtime=0))

actual=json.loads((ACTUAL/"ROOT-RECEIPT.json").read_bytes())
assert sha((ACTUAL/"ROOT-RECEIPT.json").read_bytes())=="eaf5351e9fff9d48fd01bb907d5b461080d34ca91adc1fdbca484160e906f2ef"
facts={}
for mode in ("baseline","candidate"):
    rows={}
    for name in ("install-closure.json","install-failure.json","dependency-observed-06.json"):
        path=ACTUAL/mode/name
        assert identity(path)==actual["files"][mode+"/"+name]
        rows[name]={"body":json.loads(path.read_bytes()),"identity":identity(path)}
    for i in range(1,7):
        path=ACTUAL/mode/("dependency-observed-"+str(i).zfill(2)+".json")
        assert identity(path)==actual["files"][mode+"/"+path.name]
    facts[mode]=rows
save("ACTUAL-FAILURE-EVIDENCE.json",{"rootReceipt":{"path":str(ACTUAL/"ROOT-RECEIPT.json"),**identity(ACTUAL/"ROOT-RECEIPT.json")},
    "facts":facts,"observed":"npm subprocess PASS/exit0/closed; complete provision failed inventory count cap after observed06.",
    "actualNativeTotalCountFullNamesExactSyscall":"UNOBSERVED; native100 guard attribution is source/order inference.",
    "R6RaceActualObservation":"Candidate closure records one tolerated npm-cache lstat ENOENT, baseline none.",
    "originalFailureBytesChanged":False,"buildTestsOutputs":"SKIPPED/UNKNOWN"})
save("SOURCE-ADMISSION.json",{"sourceCapBytes":CAP,"ordinaryWorkMiB":64,"reserveMiB":512,"ownDiskMiB":24,
    "authority":"Root explicitly admitted NEW R7 SOURCE384KiB; runtime caps/argv/resources unchanged.",
    "nativeFileCountScope":"4096 only three selected exact Linux x64 native packages; old100 count blocked actual provision.",
    "actualNativeFileCountUnobserved":True,"execution":"Pure synthetic cases and grammar only; no install/build/main/network/browser.","remoteWriter":"Root"})
ancestry=[]
for directory,name in [(PARENT,"SOURCE-SEAL.json"),(PARENT,"MANIFEST.json"),(ROOT.parent/"empty-intent-fresh-ci-source-r5","SOURCE-SEAL.json"),
                       (ROOT.parent/"empty-intent-fresh-ci-source-r5","RACE-CHECKS.json"),(PARENT,"FAILED-R5-SOURCE-CAP.json"),
                       (ROOT.parent/"empty-intent-fresh-ci-technical-r6","GATE.json")]:
    ancestry.append({"path":str(directory/name),**identity(directory/name)})
save("PROVENANCE.json",{"ancestry":ancestry,"R6FullFamilyInverse":identity(ROOT/"INVERSE-FULL-R6.json.gz"),
    "originalFunctionChange":"provision_audit one callsite only; new native_inventory helper.",
    "allOtherOriginalFunctionsByteExact":True,"workflowOuterOnlyMethodLiteralAndHashesChanged":True,
    "originalMetadataInputsBuildLockTestsCommandsActionsResourcesUnchanged":True,
    "R5ReproductionInherited":"Exact helpers and run_phase unchanged R6; isolated source reproduction remains inference, separate actual R6 missed cache entry now observed.",
    "independentR7Review":"PENDING","actualR7CI":"PENDING","candidateCue993aa":"UNSELECTED; no build/default/art/gameplay/fun approval."})
grammar=[]
for path in sorted(ROOT.glob("*.py")):
    compile(ast.parse(path.read_text(),filename=str(path)),str(path),"exec")
    grammar.append({"file":path.name,**identity(path)})
shells=[]
blocks=[]
for step in yaml.safe_load(new_workflow)["jobs"]["fresh-baseline"]["steps"]:
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
save("SOURCE-GRAMMAR-FINAL.json",{"status":"PASS_GRAMMAR_SOURCE_ONLY","pythonFiles":grammar,
    "bashNRunStepIDs":shells,"workflowPythonBlocks":blocks,"originalBuildNodeCheck":"Successful current SOURCE-CHECKS node --check; original bytes unchanged.",
    "candidateMainNpmNetworkArchiveBuildBrowserExecuted":False})
(ROOT/"README.md").write_text("""R7 SOURCE-only selected native inventory repair

Both retained actual runs completed npm ci with exit0 and observed process closure, then complete provisioning failed `inventory count cap` after dependency-observed06 for @typescript/typescript-linux-x647.0.2. Build/tests were skipped; outputs remain unknown. Actual total native file count/names/syscall site were not captured. The old100-file native callsite is source/order inference. Candidate's closure separately records one npm-cache lstat disappearance tolerated by R6; that actual sampling observation does not identify the older R4 failure site.

R7 changes only provision_audit's native inventory callsite and adds native_inventory. The finite4096-file allowance applies only to exact selected @typescript/typescript-linux-x64, @rolldown/binding-linux-x64-gnu and @esbuild/linux-x64 at their owned stage paths. General inventory is unchanged. Canonical paths, regular-file/single-link/per-file128MiB hashes, version/original+installed lock SRI, package/entry/.bin containment, ELF64 little-endian x86_64/nonempty-native checks remain. Walk permission/missing/other errors fail closed. Diagnostic native-inventory-NN.json saves count observed, successfully hashed bytes, first16 names (prefix160+full-name hash), completion and bounded fault before refusal; cap4097 fails before hashing that entry. It is diagnostic bytes evidence, never executable usability or full dependency Merkle.

Memory/disk/log/proof/deadline/runtime caps, original package/lock/build and8 test bodies/argv, fixed acquisition/source/support maps, source membership, empty npm configs and official action pins are unchanged. Existing proof budget may still refuse additional diagnostics; no cap is raised. Source384KiB is a separate Root allowance.

25 synthetic native cases cover old100/101 and new100/101/4096/4097, selected-path scope, bounded diagnostics and errors; inherited34 source guards and17 shim cases pass. One invalid synthetic repeated-slash expectation was preserved with exact failed harness gzip and receipt, then corrected to a meaningful literal-backslash filename case. Grammar binds all Python ASTs,9 bash-n run strings, embedded Python and exact original build node --check. No candidate main/phase/npm/network/archive/build/browser ran.

FORWARD/INVERSE.json.gz reconstruct full R6/R7 runner/workflow exactly. INVERSE-FULL-R6.json.gz preserves every regular file of the entire304597B R6 family including its inverse ancestry and failed R5 seals. PROVENANCE also binds original R5 failure/reproduction and independent R6 gate externally. All frozen predecessors and actual failures remain untouched. Root is sole remote writer. Independent R7 SOURCE review and actual CI remain pending; candidate cue993aa stays unselected, with no art/default/gameplay/fun claim.
""")

files={p.relative_to(ROOT).as_posix():identity(p) for p in sorted(ROOT.rglob("*")) if p.is_file() and p.name not in ("MANIFEST.json","SOURCE-SEAL.json")}
base_bytes=sum(pin["bytes"] for pin in files.values())
inclusive=base_bytes
for count in range(8):
    manifest=packed({"status":"FROZEN_SOURCE_R7_UNREVIEWED","files":files,"inclusiveFamilyBytes":inclusive,"sourceCapBytes":CAP,"actualCI":"PENDING"})
    seal=packed({"status":"FROZEN_SOURCE_R7_UNREVIEWED","files":files,"inclusiveFamilyBytes":inclusive,"sourceCapBytes":CAP,
                 "manifest":{"sha256":sha(manifest),"bytes":len(manifest)},"candidateMainNpmNetworkArchiveBuildBrowserExecuted":False})
    actual_size=base_bytes+len(manifest)+len(seal)
    if actual_size==inclusive:
        break
    inclusive=actual_size
else:
    raise AssertionError("family size fixed point")
assert inclusive<=CAP,(inclusive,CAP)
# Admit measured inclusive size before writing either frozen label.
(ROOT/"MANIFEST.json").write_bytes(manifest)
(ROOT/"SOURCE-SEAL.json").write_bytes(seal)
assert sum(p.stat().st_size for p in ROOT.rglob("*") if p.is_file())==inclusive
print(json.dumps({"status":"FROZEN_SOURCE_R7_UNREVIEWED","inclusiveBytes":inclusive,"capBytes":CAP,
    "seal":identity(ROOT/"SOURCE-SEAL.json"),"manifest":identity(ROOT/"MANIFEST.json"),"runner":identity(ROOT/"runner.py"),
    "workflow":identity(ROOT/"rebuild-opening-baseline.yml"),"metadata":identity(ROOT/"METADATA.json")}))
