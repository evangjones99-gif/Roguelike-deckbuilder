"""Authorized bounded npm --version only; synthetic empty cwd/configs, offline, no install/build."""
import ast
import hashlib
import json
import os
from pathlib import Path
import resource
import selectors
import signal
import subprocess
import time

BASE = Path(__file__).parent
tree = ast.parse((BASE / "runner.py").read_text())
selected = {"need", "child_env", "verify_pin", "hash_file"}
definitions = [n for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom, ast.Assign)) or isinstance(n, ast.FunctionDef) and n.name in selected]
env = {"__name__": "authorized_config_repro_definitions"}
exec(compile(ast.Module(body=definitions, type_ignores=[]), "config-repro-definitions", "exec"), env)
root = BASE / "npm-config-repro"
root.mkdir(mode=0o700)
for directory in ("control", "proof", "stage"):
    (root / directory).mkdir(mode=0o700)
for name in ("npm-user.npmrc", "npm-global.npmrc"):
    fd = os.open(root / "control" / name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    os.close(fd)
assert (root / "control/npm-user.npmrc").stat().st_ino != (root / "control/npm-global.npmrc").stat().st_ino
child = env["child_env"](root)
child.update({"NODE_OPTIONS": "--max-old-space-size=24", "npm_config_offline": "true"})

def available():
    return next(int(x.split()[1])*1024 for x in Path("/proc/meminfo").read_text().splitlines() if x.startswith("MemAvailable:"))

assert available() >= (64+512)*1048576
rows = []
for name in ("old-shared-devnull", "fixed-owned-distinct"):
    e = dict(child)
    if name.startswith("old"):
        e["npm_config_userconfig"] = e["npm_config_globalconfig"] = "/dev/null"
    start = time.monotonic()
    p = subprocess.Popen(["npm", "--version"], cwd=root/"stage", env=e, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, start_new_session=True, close_fds=True)
    # The un-reaped direct child cannot reuse its PID while its pidfd is opened.
    handle = os.pidfd_open(p.pid)
    selector = selectors.DefaultSelector()
    os.set_blocking(p.stdout.fileno(), False)
    selector.register(p.stdout, selectors.EVENT_READ)
    output = bytearray()
    peak = 0
    stop = None
    while True:
        rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024
        for entry in Path("/proc").iterdir():
            if not entry.name.isdecimal():
                continue
            try:
                s = (entry/"stat").read_text()
                values = s[s.rfind(")")+2:].split()
                if int(values[3]) == p.pid and values[0] != "Z":
                    rss += max(0, int(values[21]))*os.sysconf("SC_PAGE_SIZE")
            except (FileNotFoundError, ProcessLookupError, PermissionError):
                pass
        peak = max(peak, rss)
        if rss > 64*1048576:
            stop = "sampled64MiB source work cap"
        if available() < 512*1048576:
            stop = "sampled512MiB reserve cap"
        if time.monotonic()-start > 5:
            stop = "five-second version-only deadline"
        if stop is not None:
            try:
                signal.pidfd_send_signal(handle, signal.SIGKILL)
            except ProcessLookupError:
                pass
        for key,_ in selector.select(0.01):
            b = os.read(key.fd,4096)
            if b:
                output.extend(b)
                assert len(output) <= 65536
            else:
                selector.unregister(key.fileobj)
        code = p.poll()
        if code is not None and not selector.get_map():
            break
    os.close(handle)
    selector.close()
    p.stdout.close()
    with (root/"proof"/(name+".log")).open("xb") as f:
        f.write(output)
    rows.append({"case":name,"argv":["npm","--version"],"exit":code,"elapsedSeconds":time.monotonic()-start,"sampledAggregatePeakRSS":peak,"stop":stop,"stdoutSHA256":hashlib.sha256(output).hexdigest(),"rawBytes":len(output),"closedDirectChild":True})
assert all(x["stop"] is None for x in rows), rows
assert rows[0]["exit"] != 0 and b"double-loading config" in (root/"proof/old-shared-devnull.log").read_bytes()
assert rows[1]["exit"] == 0
assert (root/"proof/fixed-owned-distinct.log").read_text().strip().replace(".", "").isdigit()
result = {"status":"PASS_NPM_VERSION_CONFIG_REPRO_ONLY", "cases":rows,"networkInstallBuildBrowserExecuted":False,"offlineEnvironment":True,"localHeapMiB":24,"CIHeapUnchangedMiB":256,"workMiB":64,"reserveMiB":512,"qualification":"Local npm version only; actual CI provisioning/build/test remain unaccepted."}
with (BASE/"NPM-CONFIG-REPRO.json").open("x") as f:
    json.dump(result,f,separators=(",", ":"))
    f.write("\n")
print(json.dumps({"status":result["status"],"cases":rows}))
