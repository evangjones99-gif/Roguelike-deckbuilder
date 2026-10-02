import hashlib,json,resource,signal,stat,time,zipfile
from pathlib import Path
resource.setrlimit(resource.RLIMIT_AS,(64*1024**2,64*1024**2))
resource.setrlimit(resource.RLIMIT_CPU,(20,20))
signal.alarm(30)
base=Path("/workspace/scratch/opening-fresh-ci-actual-failures-cycle5-root-r1")
out=Path(__file__).parent
def sha(b):return hashlib.sha256(b).hexdigest()
root=json.loads((base/"ROOT-RECEIPT.json").read_bytes())
pins={}
for key,row in root["files"].items():
 b=(base/key).read_bytes()
 assert len(b)==row["bytes"] and sha(b)==row["sha256"],key
 pins[key]=row
live=json.loads((out/"CONNECTED-ACTUAL-METADATA.json").read_bytes())
result={}
for role in ("baseline","candidate"):
 meta=root["metadata"][role]
 jobs=next(r["value"]["jobs"] for r in live["responses"] if r["run"]==meta["run"] and r["kind"]=="jobs")
 arts=next(r["value"]["artifacts"] for r in live["responses"] if r["run"]==meta["run"] and r["kind"]=="artifacts")
 job=next(j for j in jobs if j["id"]==meta["job"])
 art=next(a for a in arts if a["id"]==meta["artifact"]["id"])
 assert art==meta["artifact"] and job["conclusion"]=="failure"
 assert art["workflow_run"]["head_sha"]==root["metadata"]["head"]
 members={}
 with zipfile.ZipFile(base/(role+"-original.zip")) as z:
  assert not z.testzip()
  names=z.namelist()
  assert len(names)==len(set(names))
  for info in z.infolist():
   assert not info.is_dir()
   assert not info.filename.startswith("/") and ".." not in info.filename.split("/")
   b=z.read(info)
   assert len(b)==info.file_size and len(b)<=200000
   assert b==(base/role/info.filename).read_bytes(),info.filename
   members[info.filename]={"bytes":len(b),"sha256":sha(b),"crc32":info.CRC}
 index=json.loads((base/role/"diagnostic-index.json").read_bytes())
 assert index["allProofBytesUploaded"] is True
 assert set(index["proofInventory"])==set(members)-{"diagnostic-index.json"}
 for key,row in index["proofInventory"].items():
  assert row=={k:members[key][k] for k in ("bytes","sha256")}
 pre=(base/role/"install-pre-membership.json").read_bytes()
 assert pre==(base/role/"install-failed-post-membership.json").read_bytes()
 closure=json.loads((base/role/"install-closure.json").read_bytes())
 assert closure["status"]=="FAILED" and closure["exit"]==-9
 assert closure["reason"]=="supervisor failure: FileNotFoundError"
 assert closure["closureObserved"] is True
 assert closure["sampledAggregatePeakRSS"]<384*1024**2
 result[role]={"run":meta["run"],"job":meta["job"],"artifact":art,"jobSteps":job["steps"],"members":members,"closure":closure,"preservedPrePostMembershipIdentical":True}
receipt={"status":"VERIFIED_PRESERVED_FAILED_INSTALLS_ONLY","rootReceiptSHA256":sha((base/"ROOT-RECEIPT.json").read_bytes()),"pinnedFiles":pins,"cases":result,"qualification":"All original ZIP regular members CRC/readback/hash match preserved selected originals. Only supervisor exception type survives, not syscall/path. No successful install/build/test or actual race site claim; no TAR extraction/npm/browser/game execution.","resource":{"addressSpaceCapBytes":64*1024**2,"cpuSeconds":20,"wallAlarmSeconds":30,"selfRssPeakBytes":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,"reserveBytes":512*1024**2}}
(out/"ACTUAL-FAILURE-CHECKS.json").write_text(json.dumps(receipt,sort_keys=True,separators=(",",":"))+"\n")
print(json.dumps({"status":receipt["status"],"roles":list(result),"members":{k:len(v["members"]) for k,v in result.items()}}))
