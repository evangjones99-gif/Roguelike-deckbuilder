"""Read-only exact cap successor audit; reuse byte-identical isolated R5 checks."""
import ast,base64,gzip,hashlib,json,resource,shutil,signal
from pathlib import Path
resource.setrlimit(resource.RLIMIT_AS,(64*1024**2,64*1024**2))
resource.setrlimit(resource.RLIMIT_CPU,(20,20))
signal.alarm(30)
P=Path("/workspace/scratch/empty-intent-fresh-ci-source-r6")
OLD=Path("/workspace/scratch/empty-intent-fresh-ci-source-r5")
PREV=Path("/workspace/scratch/empty-intent-fresh-ci-technical-r5")
O=Path(__file__).parent
def sha(b):return hashlib.sha256(b).hexdigest()
def identity(p):
 b=p.read_bytes();return {"bytes":len(b),"sha256":sha(b)}
def pins(p):
 result={}
 for f in p.rglob("*"):
  assert not f.is_symlink()
  if f.is_file():result[f.relative_to(p).as_posix()]=identity(f)
 return result
host=int(next(s.split()[1] for s in Path("/proc/meminfo").read_text().splitlines() if s.startswith("MemAvailable:")))*1024
maximum=Path("/sys/fs/cgroup/memory.max").read_text().strip();current=int(Path("/sys/fs/cgroup/memory.current").read_text())
headroom=host if maximum=="max" else min(host,int(maximum)-current)
assert headroom>=(64+512)*1024**2 and shutil.disk_usage(O).free>=24*1024**2
before=pins(P);prior=pins(OLD);review=pins(PREV)
assert prior["SOURCE-SEAL.json"]["sha256"]=="3b1ee95586d4c80fd2fbce9111d3bb99245b595963bc873f6e9ee9f473f01cd0"
assert review["GATE.json"]["sha256"]=="3d23cc6366e82b02ce361dca0e68443a82dc077554318333d3b73e694c7a09a6"
oldgate=json.loads((PREV/"GATE.json").read_bytes())
assert oldgate["verdict"]=="REJECT_SOURCE_CAP_EXCESS"
s=json.loads((P/"SOURCE-SEAL.json").read_bytes());m=json.loads((P/"MANIFEST.json").read_bytes())
assert before["SOURCE-SEAL.json"]["sha256"]=="ba7cab54f2083374efb1a9fbd8328bcd6bd6a223a1aa3c08dd201b5a3cd6fdcc"
assert s["manifest"]==before["MANIFEST.json"]
assert before["MANIFEST.json"]["sha256"]=="28ef12400f0b937cd6227065efe87508f759a32674fb1802e20a846f341402bb"
assert s["files"]==m["files"]=={k:v for k,v in before.items() if k not in ("MANIFEST.json","SOURCE-SEAL.json")}
assert set(before)==set(m["files"])|{"MANIFEST.json","SOURCE-SEAL.json"}
assert sum(v["bytes"] for v in before.values())==s["inclusiveFamilyBytes"]==m["inclusiveFamilyBytes"]==304597<=s["sourceCapBytes"]==327680
changed=sorted(k for k in prior if before.get(k)!=prior[k])
assert changed==["MANIFEST.json","PROVENANCE.json","README.md","SOURCE-ADMISSION.json","SOURCE-GRAMMAR-FINAL.json","SOURCE-SEAL.json"]
for name in ("runner.py","rebuild-opening-baseline.yml","METADATA.json","RACE-CHECKS.json","SOURCE-CHECKS.json","SHARED-SHIM-CHECKS.json","race_checks.py","source_checks.py","shared_shim_checks.py","FORWARD.json.gz","INVERSE.json.gz","INVERSE-ORIGINALS.json.gz"):
 assert (P/name).read_bytes()==(OLD/name).read_bytes()
assert (P/"PREDECESSOR-SOURCE-SEAL.json").read_bytes()==(OLD/"SOURCE-SEAL.json").read_bytes()
assert (P/"PREDECESSOR-MANIFEST.json").read_bytes()==(OLD/"MANIFEST.json").read_bytes()
failure=json.loads((P/"FAILED-R5-SOURCE-CAP.json").read_bytes())
assert failure["measuredInclusiveBytes"]==277566 and failure["excessBytes"]==15422
assert failure["failedSeal"]==prior["SOURCE-SEAL.json"] and failure["failedManifest"]==prior["MANIFEST.json"]
delta=json.loads(gzip.decompress((P/"R6-INVERSE.json.gz").read_bytes()))
assert set(delta["files"])==set(prior) and delta["parentInclusiveBytes"]==277566
reconstructed={}
for key,row in delta["files"].items():
 assert (set(row)=={"bytes","sha256","exactCurrentFile"}) or (set(row)=={"bytes","sha256","originalBase64"})
 b=(P/row["exactCurrentFile"]).read_bytes() if "exactCurrentFile" in row else base64.b64decode(row["originalBase64"],validate=True)
 assert b==(OLD/key).read_bytes()
 assert {"bytes":len(b),"sha256":sha(b)}==prior[key]=={k:row[k] for k in ("bytes","sha256")}
 reconstructed[key]=prior[key]
forward=json.loads((P/"R6-FORWARD.json").read_bytes())
assert forward["parentSeal"]==prior["SOURCE-SEAL.json"] and forward["R5FullInverse"]==before["R6-INVERSE.json.gz"]
assert forward["changedBookkeepingFiles"]==changed
prov=json.loads((P/"PROVENANCE.json").read_bytes())
assert prov["parentSource"]["seal"]==prior["SOURCE-SEAL.json"] and prov["parentSource"]["sourceCapStatus"]=="FAILED"
assert prov["externalParentReview"]["sha256"]=="4bc8c4100ef3c07ad39f2d71b1032cd2145ccb6dc6796a9683c8841b07d1157b"
python=[]
for f in P.glob("*.py"):
 compile(ast.parse(f.read_bytes()),str(f),"exec");python.append(f.name)
checks=json.loads((PREV/"SOURCE-CHECKS.json").read_bytes())
pure=json.loads((PREV/"PURE-SAMPLING-CHECKS.json").read_bytes())
assert pure["methodSHA256"]==before["runner.py"]["sha256"] and pure["caseCount"]==35
assert checks["methodSHA256"]==before["runner.py"]["sha256"] and checks["workflowSHA256"]==before["rebuild-opening-baseline.yml"]["sha256"]
assert before==pins(P) and prior==pins(OLD) and review==pins(PREV)
receipt={"status":"PASS_CAP_ONLY_NEW_SOURCE_SUCCESSOR","sourceSeal":before["SOURCE-SEAL.json"],"manifest":before["MANIFEST.json"],"sourceInclusiveBytes":304597,"sourceCapBytes":327680,"sourceFiles":before,"method":before["runner.py"],"workflow":before["rebuild-opening-baseline.yml"],"changedPredecessorFiles":changed,"allRuntimeInputGuardActionResourceAndGrammarBodiesByteExactR5":True,"fullAll25FileR5InverseReconstruction":reconstructed,"predecessorRejectedSourceBudgetPreserved":True,"priorIndependentProofFiles":{k:review[k] for k in ("GATE.json","REVIEW.md","SOURCE-CHECKS.json","PURE-SAMPLING-CHECKS.json","ACTUAL-FAILURE-CHECKS.json","CONNECTED-ACTUAL-METADATA.json","FAILED-ACTUAL-REVIEW-HARNESS.json")},"pythonGrammarCompiled":sorted(python),"independentIsolatedCasesReusedExactBody":35,"fullOriginalR4AndFourDeltaRoundtripsReusedExactCompressedBytes":True,"ordinary":{"workCapBytes":64*1024**2,"reserveBytes":512*1024**2,"initialHeadroom":headroom,"selfPeakRSS":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,"cpuLimitSeconds":20,"wallAlarmSeconds":30},"qualification":"Read-only complete source/inverse identity audit, AST grammar only. Exact previous technical functional checks retained and reused, no redundant fixture mutations or full method/network/archive/npm/children/build/test/browser execution. Root explicit NEW320KiB SOURCE grant changes no runtime budget. Actual old2jobs stillFAILED; their syscall/site remainsUNOBSERVED. Sampled disk/RSS/closure remain qualified.","oldSourcesReviewsAndFailuresUnchanged":True}
with (O/"CHECKS.json").open("x") as f:f.write(json.dumps(receipt,sort_keys=True,separators=(",",":"))+"\n")
print(json.dumps({"status":receipt["status"],"bytes":304597,"cap":327680,"R5InverseMembers":len(reconstructed),"selfPeakRSS":receipt["ordinary"]["selfPeakRSS"]}))
