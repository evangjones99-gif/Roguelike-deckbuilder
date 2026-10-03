"""Source packet/grammar/delta sealing only; no candidate execution or network."""
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
PARENT=ROOT.parent/"empty-intent-fresh-ci-source-r4"
ACTUAL=ROOT.parent/"opening-fresh-ci-actual-failures-cycle5-root-r1"
def sha(data):
    return hashlib.sha256(data).hexdigest()
def packed(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()+b"\n"
def save(name,obj):
    (ROOT/name).write_bytes(packed(obj))
def identity(path):
    data=path.read_bytes()
    return {"sha256":sha(data),"bytes":len(data)}

old_runner=(PARENT/"runner.py").read_bytes()
runner=(ROOT/"runner.py").read_bytes()
old_workflow=(PARENT/"rebuild-opening-baseline.yml").read_bytes()
workflow=(ROOT/"rebuild-opening-baseline.yml").read_bytes()
assert sha(old_runner)=="1241c9f9d3dce4248e566df2facd7b0218a08684d0b292647eb90c631d1a5ab7"
assert sha(old_workflow)=="26da96127464740600fe3d76bdde2b2b3525a888a2c9e4a0e5d304cf0e61f2ff"
assert (ROOT/"METADATA.json").read_bytes()==(PARENT/"METADATA.json").read_bytes()

def embedded_block(data):
    return "          source = r'''"+data.decode().replace("\n","\n          ")+"'''\n"
assert old_workflow.decode().count(embedded_block(old_runner))==1
template=old_workflow.decode().replace(embedded_block(old_runner),"@@EXACT_R4_EMBEDDED_SOURCE_BLOCK@@\n")
reconstructed=template.replace("@@EXACT_R4_EMBEDDED_SOURCE_BLOCK@@\n",embedded_block(old_runner)).encode()
assert reconstructed==old_workflow
expected=old_workflow.decode().replace(embedded_block(old_runner),embedded_block(runner)).replace(sha(old_runner),sha(runner)).encode()
assert expected==workflow,"No outer workflow/config/action/argv change is admitted"
originals={"runnerBase64":base64.b64encode(old_runner).decode(),"workflowTemplate":template,
           "templateMarker":"@@EXACT_R4_EMBEDDED_SOURCE_BLOCK@@\n","runner":identity(PARENT/"runner.py"),
           "workflow":identity(PARENT/"rebuild-opening-baseline.yml"),"originalsExternallyRetained":str(PARENT)}
(ROOT/"INVERSE-ORIGINALS.json.gz").write_bytes(gzip.compress(packed(originals),mtime=0))

def apply_diff(original,delta):
    lines=original.splitlines(keepends=True)
    patch=delta.splitlines(keepends=True)
    out=[]
    cursor=0
    i=2
    while i<len(patch):
        match=re.fullmatch(r"@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@.*\n",patch[i])
        assert match,patch[i]
        index=int(match[1])-1
        count=int(match[2] or "1")
        if count==0:
            index+=1
        assert index>=cursor
        out.extend(lines[cursor:index])
        cursor=index
        i+=1
        while i<len(patch) and not patch[i].startswith("@@ "):
            tag=patch[i][0]
            text=patch[i][1:]
            assert tag in " +-",tag
            if tag in " -":
                assert cursor<len(lines) and lines[cursor]==text,"Exact delta context"
                cursor+=1
            if tag in " +":
                out.append(text)
            i+=1
    out.extend(lines[cursor:])
    return "".join(out)

forward={}
inverse={}
for name in ("runner.py","rebuild-opening-baseline.yml"):
    old=(PARENT/name).read_text()
    new=(ROOT/name).read_text()
    f="".join(difflib.unified_diff(old.splitlines(keepends=True),new.splitlines(keepends=True),fromfile="R4/"+name,tofile="R5/"+name))
    inv="".join(difflib.unified_diff(new.splitlines(keepends=True),old.splitlines(keepends=True),fromfile="R5/"+name,tofile="R4/"+name))
    assert apply_diff(old,f)==new and apply_diff(new,inv)==old
    forward[name]={"before":identity(PARENT/name),"after":identity(ROOT/name),"unifiedDiff":f,"exactRoundtrip":True}
    inverse[name]={"before":identity(ROOT/name),"after":identity(PARENT/name),"unifiedDiff":inv,"exactRoundtrip":True}
(ROOT/"FORWARD.json.gz").write_bytes(gzip.compress(packed(forward),mtime=0))
(ROOT/"INVERSE.json.gz").write_bytes(gzip.compress(packed(inverse),mtime=0))

actual_receipt=json.loads((ACTUAL/"ROOT-RECEIPT.json").read_bytes())
for name in ("baseline/install-closure.json","candidate/install-closure.json","baseline/install.log","candidate/install.log"):
    pin=actual_receipt["files"][name]
    assert identity(ACTUAL/name)==pin,(name,pin)
save("ACTUAL-FAILURE-EVIDENCE.json",{
    "rootReceipt":{"path":str(ACTUAL/"ROOT-RECEIPT.json"),**identity(ACTUAL/"ROOT-RECEIPT.json")},
    "baselineClosure":json.loads((ACTUAL/"baseline/install-closure.json").read_bytes()),
    "candidateClosure":json.loads((ACTUAL/"candidate/install-closure.json").read_bytes()),
    "baselineInstallLog":{"path":str(ACTUAL/"baseline/install.log"),**identity(ACTUAL/"baseline/install.log")},
    "candidateInstallLog":{"path":str(ACTUAL/"candidate/install.log"),**identity(ACTUAL/"candidate/install.log")},
    "actualExceptionSitePath":"UNOBSERVED","dependencyInstalledMetadata":"UNOBSERVED; install aborted",
    "sourceInferenceOnly":"R4 isolated lstat race reproduces ENOENT; no actual-site attribution.",
    "oldSourceAndActualEvidenceChanged":False})

grammar=[]
for path in sorted(ROOT.glob("*.py")):
    compile(ast.parse(path.read_text(),filename=str(path)),str(path),"exec")
    grammar.append({"file":path.name,**identity(path)})
w=yaml.safe_load(workflow)
blocks=[]
shells=[]
for step in w["jobs"]["fresh-baseline"]["steps"]:
    if "run" not in step:
        continue
    run=step["run"]
    proc=subprocess.run(["bash","-n"],input=run,text=True,capture_output=True,timeout=5)
    assert proc.returncode==0,proc.stderr
    shells.append(step["id"])
    if "<<'PY'\n" in run:
        block=run[run.index("<<'PY'\n")+len("<<'PY'\n"):run.rindex("\nPY")]
        compile(ast.parse(block),step["id"],"exec")
        blocks.append({"step":step["id"],"pythonSHA256":sha(block.encode())})
node=subprocess.run(["node","--check",str(ROOT/"ORIGINAL-BUILD-GRAMMAR.mjs")],capture_output=True,text=True,timeout=5)
assert node.returncode==0,node.stderr
save("SOURCE-GRAMMAR-FINAL.json",{"status":"PASS_GRAMMAR_SOURCE_ONLY","pythonFiles":grammar,
    "workflowPythonBlocks":blocks,"bashNRunStepIDs":shells,"originalBuildNodeCheck":True,
    "candidateMainNpmNetworkArchiveBuildBrowserExecuted":False})
save("SOURCE-ADMISSION.json",{"sourceCapBytes":262144,"ordinaryWorkMiB":64,"reserveMiB":512,"ownDiskMiB":24,
    "executionScope":"Grammar, pure guards and isolated tiny filesystem races only; no candidate main/npm/network/build/browser.",
    "sourceFamilyIncludes":"All regular files recursively, fixture residue, diagnostics, deltas, manifest and seal.",
    "runtimeBudgetChange":False,"remoteWriter":"Root"})
save("PROVENANCE.json",{"parentSource":{"path":str(PARENT),"seal":identity(PARENT/"SOURCE-SEAL.json"),"manifest":identity(PARENT/"MANIFEST.json")},
    "externalParentReview":{"path":str(ROOT.parent/"empty-intent-fresh-ci-technical-r4/GATE.json"),
    **identity(ROOT.parent/"empty-intent-fresh-ci-technical-r4/GATE.json")},
    "metadata":identity(ROOT/"METADATA.json"),"forwardAndInverse":"Full exact runner/workflow roundtrips, plus self-contained compressed original runner/workflow template.",
    "changedOriginalFunctions":["disk_inventory","proof_bytes","run_phase"],
    "newHelpers":["mutation_roots","bounded_path","supervisor_fault","sampled_inventory"],
    "allOtherOriginalFunctionsByteExact":True,"originalInputsPackageLockScriptsTestsActionsCommandsResourcesUnchanged":True,
    "actualR5CI":"PENDING; no self-approval or actual build/test/default/art/gameplay/fun acceptance."})
(ROOT/"README.md").write_text("""R5 SOURCE-only supervisor sampling repair

Both actual predecessor installs were killed after a supervisor FileNotFoundError. The original diagnostics omit the syscall/path; that site remains UNOBSERVED. The retained external failure packet contains full ZIPs/logs/closures; ACTUAL-FAILURE-EVIDENCE.json binds its exact receipt and both closures. No dependency installed metadata or build/test result was produced.

An isolated intentional unlink between directory enumeration and R4 lstat reproduces kernel ENOENT. R5 accepts only exact ENOENT strictly beneath active phase mutation roots: npm cache/debug for npm phases, node_modules for install, dist/.vite-temp for build. It does not follow directory symlinks. Missing mutation roots themselves, pinned source/support/control/download/proof authority, unknown and permission errors remain fatal. Every enumerated name counts toward100000, including disappeared entries. There are at most256 misses per scan and4096 per phase; first8 bounded paths and per-site totals are recorded. Explicit os.walk onerror removes its prior silent OSError suppression. Closed-phase and final success scans have no missing allowance; membership and all hash guards remain exact.

The bounded supervisor fault records phase/site/type/errno, owned-relative path prefix/hash or opaque outside path hash, and last6 frame function/file/line entries. It omits raw exception messages. Sampling can miss transient bytes/peaks and remains an observed disk budget rather than a kernel quota. Existing work/reserve/disk/log/deadline caps, input/source maps, original npm ignore-scripts/build/test commands, credential-free configs, tool/version/SRI/entry/shim audits, fixed acquisitions and official actions are unchanged.

RACE-CHECKS has36 isolated cases; inherited source guards34 and shim/bin cases17 pass. SOURCE-GRAMMAR-FINAL binds Python AST compilation, all9 bash-n run strings, embedded Python grammar and node --check of the exact original build script. /usr/bin/time was unavailable; FAILED-CHECK-LAUNCHER-1 retains that launcher failure and CHECK-LAUNCHER binds subsequent finite successful checks. No npm/install/build/network/browser/candidate main was executed.

FORWARD/INVERSE.json.gz contain exact patches for complete runner and workflow. INVERSE-ORIGINALS.json.gz independently preserves original R4 runner plus exact workflow template and hashes; replacing its fixed marker with the indentation-preserving original literal recreates full R4 workflow. Prior packets and actual failures remain untouched. Root is sole canonical/remote writer; independent SOURCE review and separately authorized actual CI are pending. Source cap256KiB includes this entire recursive family and seal.
""")

files={}
for path in sorted(ROOT.rglob("*")):
    assert not path.is_symlink(),str(path)
    if path.is_file() and path.name not in ("MANIFEST.json","SOURCE-SEAL.json"):
        files[path.relative_to(ROOT).as_posix()]=identity(path)
for count in range(8):
    inclusive=sum(p.stat().st_size for p in ROOT.rglob("*") if p.is_file())
    manifest={"status":"FROZEN_SOURCE_R5_UNREVIEWED","files":files,"sourceCapBytes":262144,
              "inclusiveFamilyBytes":inclusive,"runtimeCI":"PENDING","actualPredecessorFaultSite":"UNOBSERVED"}
    save("MANIFEST.json",manifest)
    save("SOURCE-SEAL.json",{"status":"FROZEN_SOURCE_R5_UNREVIEWED","manifest":identity(ROOT/"MANIFEST.json"),
         "files":files,"inclusiveFamilyBytes":inclusive,"sourceCapBytes":262144,
         "candidateMainNpmNetworkArchiveBuildBrowserExecuted":False})
    actual=sum(p.stat().st_size for p in ROOT.rglob("*") if p.is_file())
    if actual==inclusive:
        break
else:
    raise AssertionError("family fixed point")
assert actual<=262144,actual
print(json.dumps({"status":"FROZEN_SOURCE_R5_UNREVIEWED","bytes":actual,"seal":identity(ROOT/"SOURCE-SEAL.json"),
      "runner":identity(ROOT/"runner.py"),"workflow":identity(ROOT/"rebuild-opening-baseline.yml")}))
