"""Rerun pure final native guards into owned proof only; never execute candidate main."""
import hashlib,json,resource,signal,shutil
from pathlib import Path
resource.setrlimit(resource.RLIMIT_AS,(64*1024**2,64*1024**2))
resource.setrlimit(resource.RLIMIT_CPU,(15,15));signal.alarm(25)
P=Path("/workspace/scratch/empty-intent-fresh-ci-source-r7");O=Path(__file__).parent
host=int(next(s.split()[1] for s in Path("/proc/meminfo").read_text().splitlines() if s.startswith("MemAvailable:")))*1024
maximum=Path("/sys/fs/cgroup/memory.max").read_text().strip();current=int(Path("/sys/fs/cgroup/memory.current").read_text())
headroom=host if maximum=="max" else min(host,int(maximum)-current)
assert headroom>=(64+512)*1024**2 and shutil.disk_usage(O).free>=24*1024**2
script=(P/"native_checks.py").read_text();method=(P/"runner.py").read_bytes()
needle='(ROOT/"NATIVE-CHECKS.json").write_text'
assert script.count(needle)==1
adapted=script.replace(needle,'(OWN/"REEXEC-NATIVE-CHECKS.json").write_text')
scope={"__file__":str(P/"native_checks.py"),"__name__":"pure_native_review","OWN":O}
exec(compile(adapted,"exact-author-native-cases-owned-output","exec"),scope)
env=scope["env"];recorded=scope["receipts"]
extra=[]
for name in ("@rolldown/binding-linux-x64-gnu","@esbuild/linux-x64"):
 target=scope["root"]/"stage/node_modules"/name
 got=scope["run"](["z","a"],package_name=name,package_path=target)
 assert list(got)==["a","z"] and len(recorded)==1 and recorded[0][1]["package"]==name
 extra.append({"name":"other_exact_native_package_sorted_rows_"+name,"pass":True})
got=scope["run"]([])
assert got=={} and recorded[0][1]["fileCountObserved"]==0 and recorded[0][1]["completeInventory"]
# Empty bytes-only helper result cannot bypass unchanged caller ELF/nonempty admission.
source=(P/"runner.py").read_text()
assert 'need(bool(natives),"Linux x64 native package body")' in source
extra.append({"name":"empty_helper_inventory_not_native_usability_admission","pass":True})
assert hashlib.sha256((P/"runner.py").read_bytes()).hexdigest()==hashlib.sha256(method).hexdigest()
receipt={"status":"PASS_PURE_SELECTED_NATIVE_SOURCE_ONLY","methodSHA256":hashlib.sha256(method).hexdigest(),"exactAuthorHarnessSHA256":hashlib.sha256(script.encode()).hexdigest(),"onlyAdaptation":"Redirect sole final receipt write to owned proof; __file__ still identifies exact frozen source root.","reexecutedAuthorCases":json.loads((O/"REEXEC-NATIVE-CHECKS.json").read_bytes()),"independentExtraCases":extra,"caseCount":json.loads((O/"REEXEC-NATIVE-CHECKS.json").read_bytes())["caseCount"]+len(extra),"ordinary":{"workCapBytes":64*1024**2,"reserveBytes":512*1024**2,"initialHeadroom":headroom,"selfPeakRSS":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,"cpuSeconds":15,"wallAlarmSeconds":25},"qualification":"Mocked filesystem enumeration/hash/diagnostic sink, no npm, actual installed subtree, method main, network, archive, child, build/test or browser; threshold cases do not prove actual native file count. Frozen source receives no writes."}
with (O/"PURE-NATIVE-CHECKS.json").open("x") as f:f.write(json.dumps(receipt,sort_keys=True,separators=(",",":"))+"\n")
print(json.dumps({"status":receipt["status"],"cases":receipt["caseCount"],"selfPeakRSS":receipt["ordinary"]["selfPeakRSS"]}))
