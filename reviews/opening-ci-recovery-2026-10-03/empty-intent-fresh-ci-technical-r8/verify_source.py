import ast,base64,gzip,hashlib,json,re,resource,shutil,signal,yaml
from pathlib import Path
resource.setrlimit(resource.RLIMIT_AS,(64*1024**2,64*1024**2))
resource.setrlimit(resource.RLIMIT_CPU,(25,25));signal.alarm(40)
P=Path("/workspace/scratch/empty-intent-fresh-ci-source-r8")
OLD=Path("/workspace/scratch/empty-intent-fresh-ci-source-r7")
BASE=Path("/workspace/scratch/empty-intent-fresh-ci-source-r6")
PREV=Path("/workspace/scratch/empty-intent-fresh-ci-technical-r7")
O=Path(__file__).parent
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return {"bytes":len(b),"sha256":sha(b)}
def pins(root):
 result={}
 for f in root.rglob("*"):
  assert not f.is_symlink()
  if f.is_file():result[f.relative_to(root).as_posix()]=pin(f)
 return result
host=int(next(s.split()[1] for s in Path("/proc/meminfo").read_text().splitlines() if s.startswith("MemAvailable:")))*1024
maximum=Path("/sys/fs/cgroup/memory.max").read_text().strip();current=int(Path("/sys/fs/cgroup/memory.current").read_text())
headroom=host if maximum=="max" else min(host,int(maximum)-current)
assert headroom>=(64+512)*1024**2 and shutil.disk_usage(O).free>=24*1024**2
before=pins(P);oldpins=pins(OLD);basepins=pins(BASE);reviewpins=pins(PREV)
assert before["SOURCE-SEAL.json"]["sha256"]=="06a21194db443ea1d03165ee5b69e1a378ce5120bfee466c52ff9a9ff8644c35"
assert before["MANIFEST.json"]["sha256"]=="22ebb5b4d584964ea81e622d73c1ffeefa47ac295093b6a9d64466a066aca20a"
s=json.loads((P/"SOURCE-SEAL.json").read_bytes());m=json.loads((P/"MANIFEST.json").read_bytes())
assert s["manifest"]==before["MANIFEST.json"]
assert s["files"]==m["files"]=={k:v for k,v in before.items() if k not in ("MANIFEST.json","SOURCE-SEAL.json")}
assert set(before)==set(s["files"])|{"MANIFEST.json","SOURCE-SEAL.json"}
assert sum(v["bytes"] for v in before.values())==s["inclusiveFamilyBytes"]==m["inclusiveFamilyBytes"]==464060<=s["sourceCapBytes"]==655360
assert reviewpins["GATE.json"]["sha256"]=="3e2ad22d0d876c2b6c1a2e390ac22a9e4c72070f04f5490af573bb4cdeb67815"
assert json.loads((PREV/"GATE.json").read_bytes())["verdict"]=="REJECT_SOURCE_CAP_EXCESS_NO_SEAL"
assert "SOURCE-SEAL.json" not in oldpins and "MANIFEST.json" not in oldpins
assert sum(v["bytes"] for v in oldpins.values())==437345
changed=sorted(k for k in oldpins if before.get(k)!=oldpins[k])
assert changed==["PROVENANCE.json","README.md","SOURCE-ADMISSION.json","SOURCE-GRAMMAR-FINAL.json"]
for name in ("runner.py","rebuild-opening-baseline.yml","METADATA.json","NATIVE-CHECKS.json","SOURCE-CHECKS.json","SHARED-SHIM-CHECKS.json","native_checks.py","source_checks.py","shared_shim_checks.py","FORWARD.json.gz","INVERSE.json.gz","INVERSE-FULL-R6.json.gz","FAILED-SOURCE-CAP.json","FAILED-NATIVE-HARNESS-1.py.gz"):
 assert (P/name).read_bytes()==(OLD/name).read_bytes()
inventory=json.loads((P/"R7-PARENT-INVENTORY.json").read_bytes())
assert inventory["files"]==oldpins and inventory["rawInclusiveBytes"]==437345
r7inverse=json.loads(gzip.decompress((P/"R8-INVERSE.json.gz").read_bytes()))
assert set(r7inverse["files"])==set(oldpins) and r7inverse["rawParentBytes"]==437345
reconstructedR7={}
for name,row in r7inverse["files"].items():
 b=(P/row["exactCurrentFile"]).read_bytes() if "exactCurrentFile" in row else base64.b64decode(row["originalBase64"],validate=True)
 assert b==(OLD/name).read_bytes()
 assert {"bytes":len(b),"sha256":sha(b)}==oldpins[name]=={k:row[k] for k in ("bytes","sha256")}
 reconstructedR7[name]=oldpins[name]
assert before["INVERSE-FULL-R6.json.gz"]=={"bytes":197053,"sha256":"3f25a5191c0f849893f47a10675daa4b385297486592c199490d0dd70d109526"}
r6inverse=json.loads(gzip.decompress((P/"INVERSE-FULL-R6.json.gz").read_bytes()))
assert set(r6inverse["files"])==set(basepins) and r6inverse["inclusiveBytes"]==304597
reconstructedR6={}
for name,row in r6inverse["files"].items():
 b=base64.b64decode(row["base64"],validate=True)
 assert b==(BASE/name).read_bytes()
 assert {"bytes":len(b),"sha256":sha(b)}==basepins[name]=={k:row[k] for k in ("bytes","sha256")}
 reconstructedR6[name]=basepins[name]
assert basepins["SOURCE-SEAL.json"]["sha256"]=="ba7cab54f2083374efb1a9fbd8328bcd6bd6a223a1aa3c08dd201b5a3cd6fdcc"
failed=json.loads((P/"FAILED-NATIVE-HARNESS-1.json").read_bytes())
assert sha(gzip.decompress((P/"FAILED-NATIVE-HARNESS-1.py.gz").read_bytes()))==failed["harnessSHA256"]
text=(P/"runner.py").read_text();old=(BASE/"runner.py").read_text()
a=ast.parse(old);b=ast.parse(text);compile(b,"source-grammar-only","exec")
am={n.name:ast.get_source_segment(old,n) for n in a.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
bm={n.name:ast.get_source_segment(text,n) for n in b.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
assert set(bm)-set(am)=={"native_inventory"} and not(set(am)-set(bm))
assert [k for k in am if am[k]!=bm[k]]==["provision_audit"]
assert bm["provision_audit"].replace("inventory=native_inventory(root,package,name,index)","inventory=regular_inventory(package,100,128*MIB)")==am["provision_audit"]
other=lambda t:ast.dump(ast.Module([n for n in t.body if not isinstance(n,(ast.FunctionDef,ast.ClassDef))],[]),include_attributes=False)
assert other(a)==other(b)
for name in ("METADATA.json","source_checks.py","shared_shim_checks.py","ORIGINAL-BUILD-GRAMMAR.mjs","PRIMARY-ACTIONS.json"):
 assert (P/name).read_bytes()==(BASE/name).read_bytes()
def block(source):return "          source = r'''"+source.replace("\n","\n          ")+"'''\n"
ow=(BASE/"rebuild-opening-baseline.yml").read_text();wf=(P/"rebuild-opening-baseline.yml").read_text()
assert ow.count(block(old))==1 and ow.replace(block(old),block(text)).replace(sha(old.encode()),sha(text.encode()))==wf
decoder=ast.parse(Path("/workspace/scratch/empty-intent-fresh-ci-technical-r1/final_seal_check.py").read_bytes())
fun=next(n for n in decoder.body if isinstance(n,ast.FunctionDef) and n.name=="unified")
scope={"re":re};exec(compile(ast.Module([fun],[]),"exact-unified-decoder","exec"),scope)
roundtrips=[]
for name,startroot,endroot in (("FORWARD.json.gz",BASE,P),("INVERSE.json.gz",P,BASE)):
 delta=json.loads(gzip.decompress((P/name).read_bytes()))
 assert set(delta)=={"runner.py","rebuild-opening-baseline.yml"}
 for key,row in delta.items():
  start=(startroot/key).read_text();end=(endroot/key).read_text()
  assert row["before"]==pin(startroot/key) and row["after"]==pin(endroot/key)
  assert scope["unified"](start,row["unifiedDiff"])==end and scope["unified"](end,row["unifiedDiff"],True)==start
  roundtrips.append({"direction":name,"file":key,"forwardReverseExact":True})
pure=json.loads((PREV/"PURE-NATIVE-CHECKS.json").read_bytes())
assert pure["methodSHA256"]==before["runner.py"]["sha256"] and pure["caseCount"]==28
assert pure["exactAuthorHarnessSHA256"]==before["native_checks.py"]["sha256"]
grammar=[]
for f in P.glob("*.py"):
 compile(ast.parse(f.read_bytes()),str(f),"exec");grammar.append(f.name)
w=yaml.load(wf,Loader=yaml.BaseLoader);embedded=[]
for step in w["jobs"]["fresh-baseline"]["steps"]:
 run=step.get("run","")
 if "<<'PY'\n" in run:
  py=run[run.index("<<'PY'\n")+len("<<'PY'\n"):run.rindex("\nPY")]
  compile(ast.parse(py),"embedded-source-only","exec");embedded.append({"step":step["id"],"sha256":sha(py.encode())})
prov=json.loads((P/"PROVENANCE.json").read_bytes())
for row in prov["ancestry"]:
 assert pin(Path(row["path"]))=={k:row[k] for k in ("bytes","sha256")}
facts=json.loads((P/"ACTUAL-FAILURE-EVIDENCE.json").read_bytes())
actual=Path("/workspace/scratch/opening-fresh-ci-actual-failures-2026-10-03-root-r1")
assert facts["rootReceipt"]["sha256"]=="eaf5351e9fff9d48fd01bb907d5b461080d34ca91adc1fdbca484160e906f2ef"
assert pin(actual/"ROOT-RECEIPT.json")=={k:facts["rootReceipt"][k] for k in ("bytes","sha256")}
for role,files in facts["facts"].items():
 for name,row in files.items():
  assert pin(actual/role/name)==row["identity"] and json.loads((actual/role/name).read_bytes())==row["body"]
assert before==pins(P) and oldpins==pins(OLD) and basepins==pins(BASE) and reviewpins==pins(PREV)
receipt={"status":"PASS_EXACT_NEW_R8_SOURCE_ONLY","sourceSeal":before["SOURCE-SEAL.json"],"manifest":before["MANIFEST.json"],"sourceFiles":before,"inclusiveSourceBytes":464060,"sourceCapBytes":655360,"method":before["runner.py"],"workflow":before["rebuild-opening-baseline.yml"],"R7ChangedBookkeepingOnly":changed,"R7Full23RawFilesReconstructed":reconstructedR7,"R6Full32FilesReconstructed":reconstructedR6,"unmodifiedOriginal197053ByteInverseRetained":True,"R6FunctionalChangeOnlyProvisionAuditOneCallAndNativeHelper":True,"allOtherFunctionsTopLevelASTMetadataAndOuterWorkflowExact":True,"fourFullMethodWorkflowDeltaForwardReverseRoundtrips":roundtrips,"failedAuthorNativeHarnessExactOriginalRetained":True,"independentPure28CasesReusedExactMethodHarness":True,"pythonASTGrammar":sorted(grammar),"embeddedPythonGrammar":embedded,"externalIndependentProofPins":{k:reviewpins[k] for k in ("GATE.json","REVIEW.md","PURE-NATIVE-CHECKS.json","REEXEC-NATIVE-CHECKS.json","SOURCE-FAILURE-CHECKS.json","actual-negative/GATE.json","actual-negative/REVIEW.md","actual-negative/CHECKS.json","actual-negative/PACKAGE-IDENTITY-CORRECTION.json")},"ordinary":{"workCapBytes":64*1024**2,"reserveBytes":512*1024**2,"initialHeadroom":headroom,"selfPeakRSS":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,"cpuSeconds":25,"wallAlarmSeconds":40},"qualification":"Source admission changes only NEW inclusive allowance. Selected native file-count100→4096 is explicitly authorized; other runtime budgets and input/output counts unchanged. OldR7 remains failed/no seal; oldA/C fullprovision failed/buildtests skipped. No sourcefullprephase compliance certification or actual native count/site claim. No full method/main/network/npm/archive extraction/children/build/test/browser execution; exact earlier grammar/pure checks reused, source readback and AST only.","allPredecessorsEvidenceReviewsUnchanged":True}
with (O/"CHECKS.json").open("x") as f:f.write(json.dumps(receipt,sort_keys=True,separators=(",",":"))+"\n")
print(json.dumps({"status":receipt["status"],"sourceBytes":464060,"R7InverseFiles":len(reconstructedR7),"R6InverseFiles":len(reconstructedR6),"selfPeakRSS":receipt["ordinary"]["selfPeakRSS"]}))
