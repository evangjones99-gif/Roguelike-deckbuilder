import hashlib,json,resource,signal,shutil,zipfile
from pathlib import Path
resource.setrlimit(resource.RLIMIT_AS,(64*1024**2,64*1024**2))
resource.setrlimit(resource.RLIMIT_CPU,(20,20));signal.alarm(30)
B=Path("/workspace/scratch/opening-fresh-ci-actual-failures-2026-10-03-root-r1")
O=Path(__file__).parent
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 h=hashlib.sha256();size=0
 with p.open("rb") as f:
  for b in iter(lambda:f.read(65536),b""):h.update(b);size+=len(b)
 return {"bytes":size,"sha256":h.hexdigest()}
host=int(next(s.split()[1] for s in Path("/proc/meminfo").read_text().splitlines() if s.startswith("MemAvailable:")))*1024
maximum=Path("/sys/fs/cgroup/memory.max").read_text().strip();current=int(Path("/sys/fs/cgroup/memory.current").read_text())
headroom=host if maximum=="max" else min(host,int(maximum)-current)
assert headroom>=(64+512)*1024**2 and shutil.disk_usage(O).free>=24*1024**2
root=json.loads((B/"ROOT-RECEIPT.json").read_bytes());carrier=json.loads((B/"API-CARRIER.json").read_bytes())
assert pin(B/"ROOT-RECEIPT.json")["sha256"]=="eaf5351e9fff9d48fd01bb907d5b461080d34ca91adc1fdbca484160e906f2ef"
assert root["head"]==carrier["head"]=="daef3fd4fade3790c85a0960317c8f98e5cdfced"
before={p.relative_to(B).as_posix():pin(p) for p in B.rglob("*") if p.is_file()}
assert len(before)==52 and sum(v["bytes"] for v in before.values())==1074874<=2097152
for key,row in root["files"].items():assert before[key]==row,key
live=json.loads((O/"CONNECTED-METADATA.json").read_bytes());result={}
for role in ("baseline","candidate"):
 meta=carrier[role]
 jobs=next(r["value"]["jobs"] for r in live if r["run"]==meta["run"] and r["kind"]=="jobs")
 arts=next(r["value"]["artifacts"] for r in live if r["run"]==meta["run"] and r["kind"]=="artifacts")
 job=next(j for j in jobs if j["id"]==meta["job"]);art=next(a for a in arts if a["id"]==meta["artifact"]["id"])
 assert art==meta["artifact"] and job["conclusion"]=="failure"
 assert before[role+"-original.zip"]=={"bytes":art["size_in_bytes"],"sha256":art["digest"].removeprefix("sha256:")}
 members={}
 with zipfile.ZipFile(B/(role+"-original.zip")) as z:
  names=z.namelist();assert len(names)==23 and len(names)==len(set(names))
  for info in z.infolist():
   assert not info.is_dir() and not info.filename.startswith("/") and ".." not in info.filename.split("/")
   h=hashlib.sha256();size=0
   with z.open(info) as stream,(B/role/info.filename).open("rb") as retained:
    for b in iter(lambda:stream.read(65536),b""):
     assert b==retained.read(len(b));h.update(b);size+=len(b)
    assert retained.read(1)==b""
   assert size==info.file_size
   members[info.filename]={"bytes":size,"sha256":h.hexdigest()}
   assert members[info.filename]==before[role+"/"+info.filename]
 index=json.loads((B/role/"diagnostic-index.json").read_bytes())
 assert index["allProofBytesUploaded"] is True
 assert set(index["proofInventory"])==set(members)-{"diagnostic-index.json"}
 assert all(members[k]==v for k,v in index["proofInventory"].items())
 closure=json.loads((B/role/"install-closure.json").read_bytes())
 failure=json.loads((B/role/"install-failure.json").read_bytes())
 assert closure==root["actual"][role]["installClosure"] and closure["status"]=="PASS" and closure["exit"]==0
 assert closure["closureObserved"] and closure["liveAtClosure"]==[] and closure["reason"] is None
 assert closure["sampledAggregatePeakRSS"]<384*1024**2 and closure["rawLogComplete"]
 assert failure=={"exceptionType":"ValueError","message":"inventory count cap","phase":"install","status":"FAILED"}
 pre=(B/role/"install-pre-membership.json").read_bytes()
 assert all((B/role/name).read_bytes()==pre for name in ("install-post-membership.json","install-failed-post-membership.json"))
 observed=[json.loads((B/role/("dependency-observed-"+str(i).zfill(2)+".json")).read_bytes()) for i in range(1,7)]
 assert observed[-1]["package"]=="@typescript/typescript-linux-x64" and observed[-1]["actualVersion"]["value"]=="7.0.2"
 assert all(s["conclusion"]=="skipped" for s in job["steps"] if s["number"] in (8,9,10,11))
 assert ("added 316 packages" in (B/role/"install.log").read_text())
 result[role]={"run":meta["run"],"job":meta["job"],"artifact":art,"members":members,"subprocessClosure":closure,"completePhaseFailure":failure,"observedPackages":observed,"prePostFailedPostMembershipIdentical":True,"steps":job["steps"]}
assert result["baseline"]["subprocessClosure"]["samplingDisappearance"]["missedEntries"]==0
assert result["candidate"]["subprocessClosure"]["samplingDisappearance"]["missedEntries"]==1
after={p.relative_to(B).as_posix():pin(p) for p in B.rglob("*") if p.is_file()};assert before==after
receipt={"status":"VERIFIED_NEGATIVE_PROVISIONING_OUTCOME","rootReceipt":before["ROOT-RECEIPT.json"],"evidenceHead":root["head"],"evidenceFiles":before,"evidencePhysicalBytes":1074874,"roles":result,"qualification":"ZIP streams consumed to EOF (CRC verified), every46 member chunk matches direct retained original and all hashes. npm subprocess succeeded, complete provision phase failed; build/tests skipped. Native audit count>100/file names/site are not captured; source/order inference only, no recovered installed subtree, runtime output or acceptance.","resource":{"workCapBytes":64*1024**2,"reserveBytes":512*1024**2,"initialHeadroom":headroom,"selfPeakRSS":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,"cpuSeconds":20,"wallAlarmSeconds":30},"originalsUnchanged":True}
with (O/"CHECKS.json").open("x") as f:f.write(json.dumps(receipt,sort_keys=True,separators=(",",":"))+"\n")
print(json.dumps({"status":receipt["status"],"members":46,"roles":list(result),"selfPeakRSS":receipt["resource"]["selfPeakRSS"]}))
