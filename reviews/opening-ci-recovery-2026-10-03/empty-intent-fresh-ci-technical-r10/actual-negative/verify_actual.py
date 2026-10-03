import hashlib,json,re,resource,signal,shutil,zipfile
from pathlib import Path
resource.setrlimit(resource.RLIMIT_AS,(64*1024**2,64*1024**2))
resource.setrlimit(resource.RLIMIT_CPU,(25,25));signal.alarm(35)
B=Path("/workspace/scratch/opening-ci-fixture-failure-root-r1");O=Path(__file__).parent
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 h=hashlib.sha256();size=0
 with p.open("rb") as f:
  for b in iter(lambda:f.read(65536),b""):h.update(b);size+=len(b)
 return {"bytes":size,"sha256":h.hexdigest()}
def pins(p):return {f.relative_to(p).as_posix():pin(f) for f in p.rglob("*") if f.is_file()}
host=int(next(s.split()[1] for s in Path("/proc/meminfo").read_text().splitlines() if s.startswith("MemAvailable:")))*1024
maximum=Path("/sys/fs/cgroup/memory.max").read_text().strip();current=int(Path("/sys/fs/cgroup/memory.current").read_text())
headroom=host if maximum=="max" else min(host,int(maximum)-current)
assert headroom>=(64+512)*1024**2 and shutil.disk_usage(O).free>=24*1024**2
before=pins(B);root=json.loads((B/"ROOT-RECEIPT.json").read_bytes());carrier=json.loads((B/"CARRIER.json").read_bytes())
assert before["ROOT-RECEIPT.json"]["sha256"]=="1ea76cca177d79eec22e0490d962947167bb8792d78dca899499ae5d377c8f3d"
assert root["head"]==carrier["head"]=="fbb617eff4b6ed04ea866ed57751ba23d8b6097d"
assert len(before)==90 and sum(v["bytes"] for v in before.values())==1246885<=2097152
assert {k:v for k,v in before.items() if k!="ROOT-RECEIPT.json"}==root["files"]
results={}
for role,source in (("A","empty-intent-fresh-ci-source-r9"),("C","opening-cue-build-source-r4")):
 case=next(c for c in carrier["cases"] if c["case"]==role)
 jobfile=json.loads((B/role/"JOBS.json").read_bytes());arts=json.loads((B/role/"ARTIFACTS.json").read_bytes())
 assert jobfile==case["jobs"] and arts==case["artifacts"]
 job=next(j for j in jobfile["jobs"] if j["id"]==case["job"]);art=next(a for a in arts["artifacts"] if a["id"]==case["artifact"])
 assert job["conclusion"]=="failure" and job["run_id"]==case["run"]
 assert art["workflow_run"]["head_sha"]==root["head"]
 assert before[role+"/ORIGINAL.zip"]=={"bytes":art["size_in_bytes"],"sha256":art["digest"].removeprefix("sha256:")}
 members={}
 with zipfile.ZipFile(B/role/"ORIGINAL.zip") as z:
  assert len(z.namelist())==39 and len(set(z.namelist()))==39
  for info in z.infolist():
   assert not info.is_dir() and not info.filename.startswith("/") and ".." not in info.filename.split("/")
   h=hashlib.sha256();size=0
   with z.open(info) as stream,(B/role/"members"/info.filename).open("rb") as direct:
    for b in iter(lambda:stream.read(65536),b""):
     assert b==direct.read(len(b));h.update(b);size+=len(b)
    assert direct.read(1)==b""
   assert size==info.file_size
   members[info.filename]={"bytes":size,"sha256":h.hexdigest(),"crc32":info.CRC}
   assert {k:members[info.filename][k] for k in ("bytes","sha256")}==before[role+"/members/"+info.filename]
 assert members==json.loads((B/role/"MEMBERS.json").read_bytes())
 diagnostic=json.loads((B/role/"members/diagnostic-index.json").read_bytes())
 assert diagnostic["allProofBytesUploaded"] is True and set(diagnostic["proofInventory"])==set(members)-{"diagnostic-index.json"}
 for key,row in diagnostic["proofInventory"].items():assert row=={k:members[key][k] for k in ("bytes","sha256")}
 source_root=Path("/workspace/scratch")/source;m=json.loads((source_root/"METADATA.json").read_bytes())
 init=json.loads((B/role/"members/initialization.json").read_bytes())
 assert init["methodSHA256"]==pin(source_root/"runner.py")["sha256"]
 assert init["metadataSHA256"]==pin(source_root/"METADATA.json")["sha256"]
 sourcehash=sha(json.dumps(dict(sorted((r["path"],r["sha256"]) for r in m["source"])),separators=(",",":")).encode())
 supporthash=sha(json.dumps(dict(sorted((r["path"],r["sha256"]) for r in m["support"])),separators=(",",":")).encode())
 assert sourcehash==m["sourceDigest"]
 expected={"sourceCount":len(m["source"]),"sourceDigest":sourcehash,"supportCount":30,"supportDigest":supporthash}
 membership={}
 for label in ("assembled","install-pre","install-post","build-pre","build-post","test-pre","test-failed-post"):
  row=json.loads((B/role/"members"/(label+"-membership.json")).read_bytes())
  assert row==expected;membership[label]=row
 native={}
 for i in (6,7,8):
  row=json.loads((B/role/"members"/("native-inventory-"+str(i).zfill(2)+".json")).read_bytes())
  assert row["completeInventory"] and row["status"]=="PASS_INVENTORY_BYTES_ONLY" and row["fileCountCap"]==4096
  native[row["package"]]=row
 assert native["@typescript/typescript-linux-x64"]["fileCountObserved"]==114
 deps=json.loads((B/role/"members/dependencies.json").read_bytes())
 assert len(deps["selectedPackages"])==len(m["tools"])==8 and not deps["completeDependencyMerkle"]
 for row in deps["selectedPackages"]:
  tool=m["tools"][row["package"]]
  for key in ("version","resolved","integrity"):assert row[key]==tool[key]
  for entry,pinned in tool.get("entries",{}).items():assert row["entryAndNativeHashes"][entry]["sha256"]==pinned
 closures={}
 for phase in ("install","build","test"):
  closure=json.loads((B/role/"members"/(phase+"-closure.json")).read_bytes())
  assert closure["closureObserved"] and closure["liveAtClosure"]==[] and closure["rawLogComplete"]
  assert closure["workCapBytes"]==(768 if phase=="test" else 384)*1024**2 and closure["reserveBytes"]==512*1024**2
  assert closure["cgroupAfter"]["events"]==closure["cgroupBefore"]["events"]
  if phase!="test":
   assert closure["status"]=="PASS" and closure["exit"]==0 and closure["reason"] is None
   assert closure["sampledAggregatePeakRSS"]<=384*1024**2
  else:
   assert closure["status"]=="FAILED" and closure["exit"]==1 and closure["reason"] is None
   assert closure["sampledAggregatePeakRSS"]<768*1024**2
   assert closure["stopSeconds"]==55 and closure["wholeSeconds"]==60
  assert closure["rawLogBytes"]==members[phase+".log"]["bytes"]
  closures[phase]=closure
 log=(B/role/"members/test.log").read_text()
 assert "tsx --test tests/*.test.ts" in log and "Interrupted while running:" not in log
 assert "ENOENT" in log and "reviews/solo-v0.3/silence-overflow-campaign.json" in log and "reviews/world-rng-v0.5/golden-vectors-r1.json" in log
 failed=log[log.index("✖ failing tests:"):]
 assert failed.count("Error: ENOENT:")==2 and "tests/save-validity-v0.4.test.ts" in failed
 counts={k:int(re.search("ℹ "+k+" ([0-9]+)",log)[1]) for k in ("tests","pass","fail","cancelled","skipped")}
 assert counts=={"tests":107,"pass":104,"fail":3,"cancelled":0,"skipped":0}
 scope=json.loads((B/role/"members/test-scope.json").read_bytes())
 tests=sorted(r["path"] for r in m["support"] if re.fullmatch("tests/[^/]+\\.test\\.ts",r["path"]))
 assert scope["files"]==tests and len(tests)==8 and scope["argv"]==["npm","test"]
 assert ("Runtime source digest: "+sourcehash) in (B/role/"members/build.log").read_text()
 steps={s["number"]:s for s in job["steps"]}
 assert steps[7]["conclusion"]==steps[8]["conclusion"]=="success" and steps[9]["conclusion"]=="failure"
 assert steps[10]["conclusion"]==steps[11]["conclusion"]=="skipped"
 assert (B/role/"JOB-DECODED-UTF8.log").read_bytes()==case["jobLog"].encode()
 assert "fresh-output-map.json" not in members
 results[role]={"run":case["run"],"job":case["job"],"artifact":art,"members":members,"membership":membership,"metadataPin":pin(source_root/"METADATA.json"),"executedMethodPin":pin(source_root/"runner.py"),"nativeDiagnostics":native,"dependencies":deps,"phaseClosures":closures,"testScope":scope,"observedRawTestCounts":counts,"jobSteps":job["steps"]}
assert results["A"]["phaseClosures"]["test"]["sampledAggregatePeakRSS"]==624603136
assert results["C"]["phaseClosures"]["test"]["sampledAggregatePeakRSS"]==649003008
assert before==pins(B)
receipt={"status":"VERIFIED_PROVISION_BUILD_PASS_TEST_FIXTURE_FAILURE_NO_SEAL","head":root["head"],"rootReceipt":before["ROOT-RECEIPT.json"],"all90EvidenceFiles":before,"physicalBytes":1246885,"roles":results,"qualification":"All78 ZIP members streamed to EOF CRC validation and direct chunk compare. Retained API jobs/artifacts/carrier consumed; no new network read. Provision+build succeeded but tests completed107 with104pass/3fail/0cancelled, missing two fixture paths and no output seal/map/raw built output bodies available. Membership digests recomputed from exact initialization-bound input metadata; raw stage bodies are not independently reopened here. Source114 native diagnostic and selected hashes verified as recorded, not every native body independently available. Sampled aggregate RSS is a supervisor budget, not exclusive game memory or OOM.","ordinary":{"workCapBytes":64*1024**2,"reserveBytes":512*1024**2,"initialHeadroom":headroom,"selfPeakRSS":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,"cpuSeconds":25,"wallAlarmSeconds":35},"oldOriginalsUnchanged":True}
with (O/"CHECKS.json").open("x") as f:f.write(json.dumps(receipt,sort_keys=True,separators=(",",":"))+"\n")
print(json.dumps({"status":receipt["status"],"members":78,"selfPeakRSS":receipt["ordinary"]["selfPeakRSS"]}))
