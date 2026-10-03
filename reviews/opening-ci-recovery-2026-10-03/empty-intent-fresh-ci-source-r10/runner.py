"""Reviewed fixed-input fresh CI method; local main/network/build execution is not admitted."""
import base64
import errno
import gzip
import hashlib
import http.client
import io
import json
import os
from pathlib import Path, PurePosixPath
import platform
import re
import resource
import selectors
import shutil
import signal
import ssl
import stat
import subprocess
import sys
import tarfile
import time
import zlib

REPO = "evangjones99-gif/Roguelike-deckbuilder"
REF = "refs/heads/codex/lanternbound-production"
WORKFLOW = REPO + "/.github/workflows/rebuild-opening-baseline.yml@" + REF
MIB = 1048576
META_SHA = "2b7de11520d1bfc4d61f52a5c454a01261d0127cddd2ce8164992651919d1d89"
META_LITERAL = "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"
DISK_CAP = 2 * 1024 * MIB
PROOF_CAP = MIB
FILE_CAP = 9 * MIB
RESPONSE_CAP = 12 * MIB
ARTIFACT_CAP = 32 * MIB
LOG_CAP = 192 * 1024
ARCHIVE_STREAM_CAP = 64 * MIB
ARCHIVE_MEMBER_CAP = 6000

def need(ok, reason):
    if not ok:
        raise ValueError(reason)

def unique(pairs):
    d = {}
    for k, v in pairs:
        need(k not in d, "duplicate JSON key")
        d[k] = v
    return d

def load_json(data):
    return json.loads(data, object_pairs_hook=unique)

def metadata():
    d = zlib.decompressobj(16 + zlib.MAX_WBITS)
    b = d.decompress(base64.b64decode(META_LITERAL, validate=True), 65537)
    need(len(b) <= 65536 and d.eof and not d.unused_data and not d.unconsumed_tail, "metadata bound")
    need(hashlib.sha256(b).hexdigest() == META_SHA, "metadata identity")
    m = load_json(b)
    need(len(m["source"]) == 98 and len(m["support"]) == 32 and len(m["blobPins"]) == 55, "fixed input counts")
    need(len({x["path"] for x in m["source"] + m["support"]}) == 130, "fixed paths unique")
    for x in m["source"] + m["support"]:
        safe_path(x["path"])
        need(re.fullmatch(r"[0-9a-f]{64}", x["sha256"]) and 0 <= x["bytes"] <= FILE_CAP, "input pin")
    return m

def safe_path(name):
    p = PurePosixPath(name)
    need(isinstance(name, str) and 0 < len(name) <= 240 and not p.is_absolute()
         and bool(p.parts) and name == str(p) and all(x not in ("", ".", "..") for x in p.parts)
         and "\\" not in name and "\x00" not in name, "noncanonical path")
    return p

def context():
    need(os.environ.get("GITHUB_REPOSITORY") == REPO and os.environ.get("GITHUB_REF") == REF
         and os.environ.get("GITHUB_WORKFLOW_REF") == WORKFLOW
         and os.environ.get("GITHUB_EVENT_NAME") in ("push", "workflow_dispatch"), "fixed CI context")
    rid, attempt = os.environ.get("GITHUB_RUN_ID", ""), os.environ.get("GITHUB_RUN_ATTEMPT", "")
    need(re.fullmatch(r"[0-9]{1,20}", rid) and re.fullmatch(r"[0-9]{1,10}", attempt), "run identity")
    temp = Path(os.environ["RUNNER_TEMP"])
    need(temp.is_absolute() and temp.is_dir() and not temp.is_symlink(), "runner temp")
    root = temp / ("empty-intent-fresh-" + rid + "-" + attempt)
    need(root.is_dir() and not root.is_symlink(), "fresh owned root")
    return root

def exclusive(path, data, mode=0o600):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, mode)
    with os.fdopen(fd, "wb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    need(path.read_bytes() == data, "full write readback")

def receipt(root, name, obj, cap=64*1024):
    b = (json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n").encode()
    need(len(b) <= cap, "receipt cap")
    exclusive(root / "proof" / name, b)

def alarm(seconds):
    def stop(_sig, _frame):
        raise TimeoutError("whole phase deadline")
    signal.signal(signal.SIGALRM, stop)
    signal.alarm(seconds)

def mutation_roots(root, phase):
    # Lexical scope only: never resolve/follow symlinks for a disappearance allowance.
    paths=[]
    if phase in ("npm-version","install","build","test"):
        paths=[root/"npm-cache",root/"proof/npm-debug"]
    if phase=="install":
        paths.append(root/"stage/node_modules")
    if phase=="build":
        paths += [root/"stage/dist",root/"stage/node_modules/.vite-temp"]
    return paths

def bounded_path(root, path):
    value=os.fspath(path) if path is not None else None
    if value is None:
        return None
    lexical=Path(os.path.abspath(value))
    if lexical.is_relative_to(root):
        text=lexical.relative_to(root).as_posix()
        return {"ownedRelativePrefix":text[:240],"complete":len(text)<=240,
                "pathSHA256":hashlib.sha256(text.encode()).hexdigest()}
    return {"outsideOwnedRoot":True,"pathSHA256":hashlib.sha256(value.encode(errors="replace")).hexdigest()}

def supervisor_fault(root, phase, site, error):
    frames=[]
    tb=error.__traceback__
    while tb is not None:
        frames.append({"file":Path(tb.tb_frame.f_code.co_filename).name[:80],
                       "function":tb.tb_frame.f_code.co_name[:80],"line":tb.tb_lineno})
        frames=frames[-6:]
        tb=tb.tb_next
    return {"phase":phase,"site":site,"exceptionType":type(error).__name__,
            "errno":getattr(error,"errno",None),"path":bounded_path(root,getattr(error,"filename",None)),
            "frames":frames,"rawExceptionMessageRetained":False}

def sampled_inventory(root, scan_root, phase, races, limit, cap, directories):
    root=Path(os.path.abspath(root))
    scan_root=Path(os.path.abspath(scan_root))
    need(scan_root.is_relative_to(root),"owned inventory root")
    initial=scan_root.lstat()
    need(stat.S_ISDIR(initial.st_mode),"regular inventory root")
    allowed=mutation_roots(root,phase)
    misses=total=count=0
    def missing(error, path, site):
        nonlocal misses
        lexical=Path(os.path.abspath(path))
        if (not isinstance(error,FileNotFoundError) or error.errno!=errno.ENOENT or
                races is None or not any(lexical!=p and lexical.is_relative_to(p) for p in allowed)):
            raise error
        misses+=1
        races["missedEntries"]=races.get("missedEntries",0)+1
        sites=races.setdefault("sites",{})
        sites[site]=sites.get(site,0)+1
        examples=races.setdefault("firstExamples",[])
        if len(examples)<8:
            examples.append({"site":site,"path":bounded_path(root,lexical)})
        need(misses<=256 and races["missedEntries"]<=4096,"finite sampling disappearance cap")
    def walk_error(error):
        # os.walk otherwise silently skips permission and other scandir errors.
        if error.filename is None:
            raise error
        missing(error,error.filename,"scandir")
    for directory, dirs, files in os.walk(scan_root,followlinks=False,onerror=walk_error):
        for name in dirs+files:
            count+=1
            need(count<=limit,"disk entry cap")
            path=Path(directory)/name
            try:
                st=path.lstat()
            except OSError as error:
                missing(error,path,"lstat")
                continue
            # Symlink sizes are measured without following targets, as in the prior disk scan.
            if not stat.S_ISDIR(st.st_mode):
                total+=st.st_size
            need(total<=cap,"owned disk budget" if directories else "proof byte cap")
    final=scan_root.lstat()
    need(stat.S_ISDIR(final.st_mode) and (initial.st_dev,initial.st_ino)==(final.st_dev,final.st_ino),
         "stable inventory root identity")
    return total

def disk_inventory(root, limit=100000, phase=None, races=None):
    return sampled_inventory(root,root,phase,races,limit,DISK_CAP,True)

def proof_bytes(root, phase=None, races=None):
    return sampled_inventory(root,root/"proof",phase,races,100000,PROOF_CAP,False)

def hash_file(path, cap=FILE_CAP):
    st = path.lstat()
    need(stat.S_ISREG(st.st_mode) and st.st_nlink == 1 and st.st_size <= cap, "regular owned file")
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(65536), b""):
            h.update(b)
    return {"bytes": st.st_size, "sha256": h.hexdigest()}

def verify_pin(path, pin):
    got = hash_file(path)
    need(got == {"bytes": pin["bytes"], "sha256": pin["sha256"]}, "body identity")
    return got

def fetch_blob(pin, token, deadline):
    need(0 < pin["bytes"] <= FILE_CAP and re.fullmatch(r"[0-9a-f]{40}", pin["gitBlobSHA1"]), "Git pin")
    need(time.monotonic() < deadline, "fetch deadline")
    c = http.client.HTTPSConnection("api.github.com", 443, timeout=min(15, max(0.1, deadline-time.monotonic())), context=ssl.create_default_context())
    try:
        c.request("GET", "/repos/" + REPO + "/git/blobs/" + pin["gitBlobSHA1"], headers={
            "Authorization": "Bearer " + token, "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "fixed-empty-intent-byte-recovery"})
        r = c.getresponse()
        need(r.status == 200 and r.getheader("Location") is None, "blob status/no redirects")
        need(r.getheader("Content-Encoding") in (None, "identity"), "response encoding")
        length = r.getheader("Content-Length")
        if length is not None:
            need(length.isdecimal() and int(length) <= RESPONSE_CAP, "response declared cap")
        raw = bytearray()
        while True:
            need(time.monotonic() < deadline, "response whole deadline")
            if c.sock is not None:
                c.sock.settimeout(min(15, max(0.1, deadline-time.monotonic())))
            part = r.read(min(65536, RESPONSE_CAP + 1 - len(raw)))
            if not part:
                break
            raw.extend(part)
            need(len(raw) <= RESPONSE_CAP, "response byte cap")
        if length is not None:
            need(len(raw) == int(length), "response length")
        j = load_json(raw)
        need(j.get("sha") == pin["gitBlobSHA1"] and type(j.get("size")) is int
             and j["size"] == pin["bytes"] and j.get("encoding") == "base64"
             and isinstance(j.get("content"), str), "Git API identity")
        content = j["content"]
        need(len(content) <= RESPONSE_CAP and re.fullmatch(r"[A-Za-z0-9+/=\n\r]*", content), "base64 grammar")
        body = base64.b64decode(content.replace("\n", "").replace("\r", ""), validate=True)
        need(len(body) == pin["bytes"] and hashlib.sha256(body).hexdigest() == pin["sha256"], "body SHA256/size")
        need(hashlib.sha1(("blob " + str(len(body)) + "\x00").encode() + body).hexdigest() == pin["gitBlobSHA1"], "Git framed SHA1")
        return body
    finally:
        c.close()

def acquire(root, m):
    resource.setrlimit(resource.RLIMIT_AS, (128*MIB, 128*MIB))
    resource.setrlimit(resource.RLIMIT_CPU, (40, 40))
    alarm(180)
    need(shutil.disk_usage(root).free >= 4*1024*MIB, "initial 4GiB free")
    token = os.environ.pop("GITHUB_TOKEN", "")
    need(bool(token) and "\n" not in token and "\r" not in token, "scoped acquisition token")
    out = root / "downloads"
    out.mkdir()
    start = time.monotonic()
    rows = []
    try:
        for pin in m["blobPins"]:
            body = fetch_blob(pin, token, start+180)
            path = out / (pin["sha256"] + ".blob")
            exclusive(path, body)
            verify_pin(path, pin)
            rows.append({"sha256": pin["sha256"], "gitBlobSHA1": pin["gitBlobSHA1"], "bytes": pin["bytes"]})
            del body
            need(disk_inventory(root) <= DISK_CAP, "acquisition owned disk")
    finally:
        token = ""
        receipt(root, "acquisition-progress.json", {"verified": rows, "expected": 55, "complete": len(rows)==55, "elapsed":time.monotonic()-start})
    need(len(rows)==55, "all fixed blobs")

class BoundedStream:
    def __init__(self, stream, cap):
        self.stream, self.cap, self.count = stream, cap, 0
    def read(self, size=-1):
        need(size >= 0, "unbounded archive read")
        b = self.stream.read(min(size, self.cap-self.count+1))
        self.count += len(b)
        need(self.count <= self.cap, "whole decompressed stream cap")
        return b

def member_header(member, archive):
    safe_path(member.name)
    need(member.isfile() and not member.issparse() and not member.linkname and not member.pax_headers
         and member.type in (tarfile.REGTYPE, tarfile.AREGTYPE)
         and 0 <= member.size <= FILE_CAP, "nonregular/extended archive member")
    need(re.fullmatch(r"blobs/[0-9a-f]{64}", member.name)
         or (archive == "ce0f" and member.name == "INDEX.json" and member.size == 928223), "unknown archive member")

def assemble(root, m):
    resource.setrlimit(resource.RLIMIT_AS, (128*MIB, 128*MIB))
    resource.setrlimit(resource.RLIMIT_CPU, (40, 40))
    alarm(60)
    stage = root / "stage"
    stage.mkdir()
    needed = {key:{} for key in ("8cdf", "4513", "ce0f")}
    for x in m["source"] + m["support"]:
        if "archive" in x:
            needed[x["archive"]].setdefault(x["sha256"], []).append(x)
        else:
            path = root / "downloads" / (x["blob"] + ".blob")
            verify_pin(path, x)
            exclusive(stage / x["path"], path.read_bytes())
    reports = []
    total_stream = 0
    for pin in m["blobPins"][-3:]:
        key = pin["id"]
        path = root / "downloads" / (pin["sha256"] + ".blob")
        verify_pin(path, pin)
        seen, chosen, index = set(), set(), False
        with path.open("rb") as compressed, gzip.GzipFile(fileobj=compressed) as gz:
            stream = BoundedStream(gz, ARCHIVE_STREAM_CAP-total_stream)
            with tarfile.open(fileobj=stream, mode="r|") as tf:
                for member in tf:
                    member_header(member, key)
                    need(member.name not in seen and len(seen) < ARCHIVE_MEMBER_CAP, "duplicate/member count")
                    seen.add(member.name)
                    if member.name == "INDEX.json":
                        data = tf.extractfile(member).read(member.size + 1)
                        need(len(data)==928223 and hashlib.sha1(b"blob 928223\x00"+data).hexdigest()=="46980a8ab7289c6f013390ac5f283cde389cffdd", "ce0f INDEX witness")
                        index = True
                    elif member.name[6:] in needed[key]:
                        sha = member.name[6:]
                        data = tf.extractfile(member).read(member.size + 1)
                        need(len(data)==member.size and hashlib.sha256(data).hexdigest()==sha, "selected archive body")
                        for x in needed[key][sha]:
                            need(x["bytes"]==len(data), "selected archive size")
                            exclusive(stage / x["path"], data)
                        chosen.add(sha)
            # Drain padding/remainder through the same bound and validate gzip trailer.
            while stream.read(65536):
                pass
        total_stream += stream.count
        need(total_stream <= ARCHIVE_STREAM_CAP, "combined decompressed stream cap")
        need(chosen == set(needed[key]) and (key != "ce0f" or index), "selected member completeness")
        reports.append({"archive":key,"members":len(seen),"selectedUnique":len(chosen),"decompressedBytes":stream.count,"indexWitness":index})
    membership(root, m, "assembled")
    receipt(root, "assembly.json", {"archives":reports,"restoredOriginalFilesystemMetadata":False,"sourceFiles":98,"supportFiles":32})

def regular_inventory(directory, cap=10000, file_cap=ARTIFACT_CAP):
    need(directory.is_dir() and not directory.is_symlink(), "inventory root regular directory")
    rows = {}
    for base, dirs, files in os.walk(directory, followlinks=False):
        for name in dirs:
            need(not (Path(base)/name).is_symlink(), "directory symlink")
        for name in files:
            path = Path(base)/name
            key = path.relative_to(directory).as_posix()
            safe_path(key)
            need(len(rows)<cap, "inventory count cap")
            rows[key] = hash_file(path, file_cap)
    return dict(sorted(rows.items()))

def membership(root, m, label):
    stage = root / "stage"
    need(stage.is_dir() and not stage.is_symlink(), "membership root regular directory")
    observed = {}
    # Exclude only fresh installation/output directories from the 130 pinned inputs.
    for base, dirs, files in os.walk(stage, followlinks=False):
        if Path(base)==stage:
            dirs[:] = [x for x in dirs if x not in ("node_modules", "dist")]
        for name in dirs:
            need(not (Path(base)/name).is_symlink(), "input directory symlink")
        for name in files:
            p = Path(base)/name
            observed[p.relative_to(stage).as_posix()] = hash_file(p)
    expected = {x["path"]:{"bytes":x["bytes"],"sha256":x["sha256"]} for x in m["source"]+m["support"]}
    need(observed==expected, "exact130 membership and bytes")
    hashes = dict(sorted((x["path"],x["sha256"]) for x in m["source"]))
    digest = hashlib.sha256(json.dumps(hashes,separators=(",", ":")).encode()).hexdigest()
    need(digest==m["sourceDigest"], "runtime98 digest")
    receipt(root, label+"-membership.json", {"sourceDigest":digest,"sourceCount":98,"supportCount":32,"supportDigest":hashlib.sha256(json.dumps(dict(sorted((x["path"],x["sha256"]) for x in m["support"])),separators=(",", ":")).encode()).hexdigest()})

def child_env(root):
    user_config=root/"control/npm-user.npmrc"
    global_config=root/"control/npm-global.npmrc"
    need(user_config != global_config, "distinct owned npm config paths")
    for config in (user_config,global_config):
        verify_pin(config,{"bytes":0,"sha256":"e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"})
    # Never pass GitHub, Actions runtime, registry tokens, arbitrary NODE_OPTIONS or npmrc.
    e = {k:os.environ[k] for k in ("PATH","HOME","LANG","LC_ALL","TMPDIR") if k in os.environ}
    e.update({"CI":"true", "NODE_OPTIONS":"--max-old-space-size=256",
        "npm_config_cache":str(root/"npm-cache"), "npm_config_logs_dir":str(root/"proof"/"npm-debug"),
        "npm_config_userconfig":str(user_config), "npm_config_globalconfig":str(global_config),
        "npm_config_registry":"https://registry.npmjs.org", "npm_config_fetch_retries":"0",
        "npm_config_fetch_timeout":"30000", "npm_config_audit":"false", "npm_config_fund":"false",
        "npm_config_update_notifier":"false", "npm_config_progress":"false",
        "ELECTRON_SKIP_BINARY_DOWNLOAD":"1", "PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD":"1",
        "PUPPETEER_SKIP_DOWNLOAD":"1"})
    return e

def proc_snapshot():
    result = {}
    entries = list(Path("/proc").iterdir())
    need(len(entries)<=10000, "proc census cap")
    for p in entries:
        if not p.name.isdecimal():
            continue
        try:
            text = (p/"stat").read_text()
            s = text[text.rfind(")")+2:].split()
            result[int(p.name)] = {"state":s[0],"ppid":int(s[1]),"pgrp":int(s[2]),"sid":int(s[3]),
                "cpuTicks":int(s[11])+int(s[12]),"start":int(s[19]),"rss":max(0,int(s[21]))*os.sysconf("SC_PAGE_SIZE")}
        except (FileNotFoundError, ProcessLookupError, PermissionError):
            continue
    return result

def mem_available():
    for line in Path("/proc/meminfo").read_text().splitlines():
        if line.startswith("MemAvailable:"):
            return int(line.split()[1])*1024
    raise ValueError("MemAvailable absent")

def cgroup_observation():
    # Shared hosted runner cgroup is evidence, never a dedicated per-job enforcement claim.
    rows = Path("/proc/self/cgroup").read_text().splitlines()
    row = next((x[3:] for x in rows if x.startswith("0::")), None)
    if row is None:
        return {"available":False}
    p = Path("/sys/fs/cgroup") / row.lstrip("/")
    try:
        return {"available":True,"path":str(p),"max":(p/"memory.max").read_text().strip(),
            "current":int((p/"memory.current").read_text()),"events":(p/"memory.events").read_text().strip()}
    except (FileNotFoundError, PermissionError):
        return {"available":False}

def effective_available():
    host=mem_available()
    cg=cgroup_observation()
    if cg.get("available") and cg["max"].isdecimal():
        return min(host,max(0,int(cg["max"])-cg["current"]))
    return host

def run_phase(root, name, argv, stop_s, whole_s, memory_cap):
    stage = root/"stage"
    need(effective_available()>=memory_cap+512*MIB, "phase work+reserve availability")
    need(shutil.disk_usage(root).free>=4*1024*MIB, "phase4GiB free")
    before = cgroup_observation()
    start = time.monotonic()
    control = {"reason":None}
    site="phase initialization"
    fault=None
    races={"missedEntries":0,"sites":{},"firstExamples":[],"perScanMissCap":256,"perPhaseMissCap":4096,
           "qualification":"Exact ENOENT beneath phase-owned mutation roots only; transient missing entries are not measured. Final closed-phase scan has no missing allowance."}
    def interrupt(sig, _frame):
        control["reason"] = "supervisor signal " + str(sig)
    oldterm = signal.signal(signal.SIGTERM, interrupt)
    oldint = signal.signal(signal.SIGINT, interrupt)
    p = None
    handles, identities, cpu, sel = {}, {}, {}, selectors.DefaultSelector()
    samples = peak = 0
    min_available = effective_available()
    seen_log = 0
    received_log = 0
    overflow_first_bytes = 0
    log_complete = True
    term_at = None
    alive = {}
    exited = None
    status = "FAILED"
    closure = False
    last_disk = start
    fd = os.open(root/"proof"/(name+".log"), os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    def bind_handle(pid, start_identity):
        identity=(pid,start_identity)
        if identity in handles:
            return
        try:
            h=os.pidfd_open(pid)
        except ProcessLookupError:
            return
        try:
            current=proc_snapshot().get(pid)
            if current is None:
                os.close(h)
                return
            need(current["start"]==start_identity, "pidfd initial identity race")
        except BaseException:
            os.close(h)
            raise
        handles[identity]=h
    def observe():
        nonlocal peak, samples, min_available, alive
        snap = proc_snapshot()
        owned = {pid for pid,v in snap.items() if p is not None and (v["sid"]==p.pid or (pid in identities and identities[pid]==v["start"]))}
        change = True
        while change:
            new = {pid for pid,v in snap.items() if v["ppid"] in owned}
            change = not new.issubset(owned)
            owned |= new
        alive = {pid:snap[pid] for pid in owned if snap[pid]["state"] != "Z"}
        for pid in owned:
            v = snap[pid]
            identities[pid]=v["start"]
            cpu[(pid,v["start"])]=max(cpu.get((pid,v["start"]),0),v["cpuTicks"])
            if v["state"]!="Z":
                bind_handle(pid,v["start"])
        own = snap.get(os.getpid(),{}).get("rss",0)
        rss = own + sum(v["rss"] for v in alive.values())
        peak=max(peak,rss)
        samples+=1
        avail=effective_available()
        min_available=min(min_available,avail)
        if rss>memory_cap:
            control["reason"]="sampled aggregate RSS cap"
        if avail<512*MIB:
            control["reason"]="sampled host/cgroup available reserve cap"
        if sum(cpu.values())/os.sysconf("SC_CLK_TCK") > (150 if name=="install" else 55):
            control["reason"]="sampled aggregate CPU cap"
    def terminate(sig):
        # pidfd pins the observed process identity; never signal a recycled numeric PGID.
        for identity,h in list(handles.items()):
            try:
                signal.pidfd_send_signal(h,sig)
            except ProcessLookupError:
                pass
    try:
        site="child launch/environment"
        p = subprocess.Popen(argv,cwd=stage,env=child_env(root),stdout=subprocess.PIPE,stderr=subprocess.STDOUT,start_new_session=True,close_fds=True)
        site="initial process census/pidfd binding"
        identities[p.pid]=proc_snapshot()[p.pid]["start"]
        bind_handle(p.pid,identities[p.pid])
        os.set_blocking(p.stdout.fileno(),False)
        sel.register(p.stdout,selectors.EVENT_READ)
        while True:
            now=time.monotonic()
            site="process census/pidfd/resource observation"
            observe()
            if now-start>=stop_s and alive:
                control["reason"] = control["reason"] or "phase stop deadline"
            if now-last_disk>=0.1:
                try:
                    site="owned disk sampling"
                    disk_inventory(root,phase=name,races=races)
                    site="proof byte sampling"
                    need(proof_bytes(root,phase=name,races=races)<=850*1024,"proof log/receipt soft cap")
                except ValueError as e:
                    control["reason"]="sampled disk/log cap: "+str(e)
                last_disk=now
            if control["reason"] and term_at is None:
                site="owned process termination"
                terminate(signal.SIGTERM)
                term_at=now
            if term_at is not None and now-term_at>=1:
                site="owned process forced termination"
                terminate(signal.SIGKILL)
            site="raw log select/read/write"
            for key,_ in sel.select(0.05):
                b=os.read(key.fd,4096)
                if not b:
                    sel.unregister(key.fileobj)
                elif seen_log+len(b)<=LOG_CAP:
                    received_log+=len(b)
                    need(os.write(fd,b)==len(b),"complete raw log write")
                    seen_log+=len(b)
                else:
                    received_log+=len(b)
                    overflow_first_bytes=len(b)
                    need(len(b)<=64*1024,"finite first overflow residue")
                    exclusive(root/"proof"/(name+"-overflow-first.log"),b)
                    sel.unregister(key.fileobj)
                    log_complete=False
                    control["reason"]="raw log cap; first delivered overflow chunk retained; unread tail exists"
            # Census occurs before poll/reap so orphaned descendants stay tracked.
            site="launcher poll/closure observation"
            exited=p.poll()
            if exited is not None and not alive and not sel.get_map():
                closure=True
                break
            if now-start>=whole_s-0.5:
                control["reason"]=control["reason"] or "whole phase closure deadline"
                terminate(signal.SIGKILL)
                observe()
                closure=not alive and p.poll() is not None
                break
        if closure:
            site="closed-phase strict owned disk scan"
            disk_inventory(root)
            site="closed-phase strict proof scan"
            need(proof_bytes(root)<=850*1024,"closed-phase proof log/receipt soft cap")
            need(time.monotonic()-start<whole_s,"strict scan whole phase deadline")
        status="PASS" if exited==0 and closure and control["reason"] is None and log_complete else "FAILED"
    except BaseException as e:
        fault=supervisor_fault(root,name,site,e)
        control["reason"]="supervisor failure: "+type(e).__name__
        if p is not None:
            # Known pidfds are safe even if census failed. Unobserved closure is never PASS.
            terminate(signal.SIGKILL)
            try:
                observe()
                terminate(signal.SIGKILL)
            except BaseException:
                alive={p.pid:{"closure":"census unavailable"}}
            until=min(start+whole_s,time.monotonic()+1)
            while alive and time.monotonic()<until:
                time.sleep(0.02)
                try:
                    observe()
                    terminate(signal.SIGKILL)
                except BaseException:
                    break
            try:
                exited=p.wait(timeout=max(0.01,until-time.monotonic()))
            except subprocess.TimeoutExpired:
                pass
            closure=not alive and p.poll() is not None
    finally:
        os.fsync(fd)
        os.close(fd)
        sel.close()
        if p is not None and p.stdout is not None:
            p.stdout.close()
        for h in handles.values():
            os.close(h)
        signal.signal(signal.SIGTERM,oldterm)
        signal.signal(signal.SIGINT,oldint)
        result={"phase":name,"argv":argv,"status":status,"exit":exited,"elapsedSeconds":time.monotonic()-start,
            "stopSeconds":stop_s,"wholeSeconds":whole_s,"sampledAggregatePeakRSS":peak,"workCapBytes":memory_cap,
            "reserveBytes":512*MIB,"minHostOrFiniteCgroupHeadroom":min_available,"samples":samples,"ownedObservedProcesses":len(identities),
            "sampledCPUseconds":sum(cpu.values())/os.sysconf("SC_CLK_TCK"),"closureObserved":closure,
            "liveAtClosure":sorted(alive),"rawLogBytes":seen_log,"receivedRawLogBytes":received_log,"rawLogBudget":LOG_CAP,"firstOverflowBytesRetained":overflow_first_bytes,"rawLogComplete":log_complete,"reason":control["reason"],
            "supervisorFault":fault,"samplingDisappearance":races,
            "memoryQualification":"Owned process session/descendant census plus supervisor RSS sampled; shared cgroup is observed only, no dedicated hard cgroup guarantee, transient peaks/escaped descendants not certified.",
            "diskQualification":"Owned paths sampled, not kernel quota; overflow fails and is retained.",
            "cgroupBefore":before,"cgroupAfter":cgroup_observation()}
        receipt(root,name+"-closure.json",result,16*1024)
    need(status=="PASS", name+" failed; retained closure/log")

def canonical_bin_map(value, package_name):
    # npm accepts a string for one package-named command, or a command-to-path object.
    if isinstance(value,str):
        value={package_name.rsplit("/",1)[-1]:value}
    need(isinstance(value,dict) and len(value)<=32,"bounded bin representation")
    result={}
    for command,path in value.items():
        need(isinstance(command,str) and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,63}",command),"canonical bin command")
        need(isinstance(path,str) and len(path)<=240,"bounded bin path")
        while path.startswith("./"):
            path=path[2:]
        safe_path(path)
        result[command]=path
    return result


def observed_bin(value,cap=8192):
    # Keep ordinary actual mappings exact; oversized/malformed data stays explicitly bounded.
    b=json.dumps(value,sort_keys=True,separators=(",", ":")).encode()
    if len(b)<=cap:
        return {"complete":True,"value":value}
    return {"complete":False,"serializedBytes":len(b),"serializedSHA256":hashlib.sha256(b).hexdigest(),"prefix":b[:min(1024,cap)].decode("utf-8",errors="replace")}


def native_inventory(root,package,name,index):
    # This larger finite count applies only to the three pinned selected Linux x64 packages.
    need(name in ("@typescript/typescript-linux-x64","@rolldown/binding-linux-x64-gnu","@esbuild/linux-x64"),
         "fixed selected native package")
    need(package==root/"stage/node_modules"/name,"fixed selected native package path")
    rows={}
    observed={"package":name,"status":"FAILED","fileCountObserved":0,"hashedBytes":0,
              "fileCountCap":4096,"perFileBytesCap":128*MIB,"firstBoundedNames":[],
              "diagnosticOnlyNotAdmission":True,"completeInventory":False}
    site="native inventory root"
    def walk_error(error):
        raise error
    try:
        need(package.is_dir() and not package.is_symlink(),"inventory root regular directory")
        for base,dirs,files in os.walk(package,followlinks=False,onerror=walk_error):
            site="native directory symlink guard"
            for entry in dirs:
                need(not (Path(base)/entry).is_symlink(),"directory symlink")
            for entry in files:
                path=Path(base)/entry
                rel=path.relative_to(package).as_posix()
                observed["fileCountObserved"]+=1
                if len(observed["firstBoundedNames"])<16:
                    observed["firstBoundedNames"].append({"namePrefix":rel[:160],"complete":len(rel)<=160,
                         "nameSHA256":hashlib.sha256(rel.encode()).hexdigest()})
                site="native canonical path/count guard"
                safe_path(rel)
                need(observed["fileCountObserved"]<=4096,"inventory count cap")
                need(rel not in rows,"duplicate native inventory path")
                site="native regular per-file hash"
                rows[rel]=hash_file(path,128*MIB)
                observed["hashedBytes"]+=rows[rel]["bytes"]
        observed["completeInventory"]=True
        observed["status"]="PASS_INVENTORY_BYTES_ONLY"
    except BaseException as error:
        observed["fault"]=supervisor_fault(root,"provision-native",site,error)
        receipt(root,"native-inventory-"+str(index).zfill(2)+".json",observed,16*1024)
        raise
    receipt(root,"native-inventory-"+str(index).zfill(2)+".json",observed,16*1024)
    return dict(sorted(rows.items()))

def provision_audit(root,m):
    stage=root/"stage"
    need((stage/"node_modules").is_dir() and not (stage/"node_modules").is_symlink(),"owned modules root")
    need((stage/"node_modules/.bin").is_dir() and not (stage/"node_modules/.bin").is_symlink(),"owned bin directory")
    lock=load_json((stage/"package-lock.json").read_bytes())["packages"]
    installed=load_json((stage/"node_modules/.package-lock.json").read_bytes())["packages"]
    rows=[]
    for index,(name,pin) in enumerate(m["tools"].items(),1):
        key="node_modules/"+name
        package=stage/key
        need(package.is_dir() and not package.is_symlink(),"owned selected tool package")
        need(all(not ancestor.is_symlink() for ancestor in package.parents if ancestor!=stage.parent),"owned tool ancestors")
        package_json=hash_file(package/"package.json",64*1024)
        actual=load_json((package/"package.json").read_bytes())
        receipt(root,"dependency-observed-"+str(index).zfill(2)+".json",{"package":name,"packageJSON":package_json,"actualName":observed_bin(actual.get("name"),256),"actualVersion":observed_bin(actual.get("version"),256),"actualBin":observed_bin(actual.get("bin")),"requiredPinnedBins":pin.get("bin"),"expectedVersion":pin["version"],"lockPinsExpected":{k:pin[k] for k in ("version","resolved","integrity")},"diagnosticOnlyNotAdmission":True},16*1024)
        need(actual["version"]==pin["version"],"tool version")
        for k in ("version","resolved","integrity"):
            need(lock[key][k]==pin[k] and installed[key][k]==pin[k],"installed lock identity")
        files={}
        executable=name in ("typescript","vite","tsx")
        resolution="Type-only metadata and entry hashes; no shared npm shim admission."
        unused_commands=[]
        if "bin" in pin:
            if executable:
                actual_bins=canonical_bin_map(actual.get("bin"),name)
                required_bins=canonical_bin_map(pin["bin"],name)
                need(all(actual_bins.get(command)==path for command,path in required_bins.items()),"required executable bin mapping")
                # Unused additional commands are metadata only: never execute or substitute them.
                unused_commands=sorted(set(actual_bins)-set(required_bins))
                need(not set(unused_commands)&{"node","npm","tsc","vite","tsx"},"unused bin command conflicts with fixed execution scope")
            for command,rel in pin["bin"].items():
                safe_path(rel)
                entry=package/rel
                need(entry.resolve(strict=True).is_relative_to(package.resolve(strict=True)),"owned selected entry containment")
                for parent in entry.parents:
                    need(parent.is_dir() and not parent.is_symlink(),"selected entry parent regular directory")
                    if parent==package:
                        break
                files[rel]=hash_file(entry)
                if executable:
                    shim=stage/"node_modules/.bin"/command
                    need(shim.is_symlink() and shim.resolve(strict=True)==(package/rel).resolve(strict=True),"owned actual executable npm bin resolution")
                    resolution="Owned selected executable .bin matches package entry; build resolves tsc/vite package.json directly; npm test uses tsx."
        if name.startswith(("@typescript/typescript-linux-","@rolldown/binding-linux-","@esbuild/linux-")):
            inventory=native_inventory(root,package,name,index)
            natives={}
            for rel,r in inventory.items():
                with (package/rel).open("rb") as binary:
                    header=binary.read(20)
                    if header[:4]==b"\x7fELF":
                        need(len(header)==20 and header[4:6]==b"\x02\x01" and int.from_bytes(header[18:20],"little")==62,"actual ELF64 x86_64 platform")
                        natives[rel]=r
            need(bool(natives),"Linux x64 native package body")
            files.update(natives)
        rows.append({"package":name,"version":actual["version"],"integrity":pin["integrity"],"resolved":pin["resolved"],"entryAndNativeHashes":files,"packageJSON":hash_file(package/"package.json"),"binResolution":resolution,"unusedBinCommandsNotExecuted":unused_commands})
    receipt(root,"dependencies.json",{"platform":platform.platform(),"machine":platform.machine(),"libc":platform.libc_ver(),"nodeExpected":m["expectedNodeVersion"],"selectedPackages":rows,"completeDependencyMerkle":False,"nativeExecutionUsability":"Determined by subsequent original build/tests, never presumed from bytes."})

def preflight(root,m):
    need(platform.system()=="Linux" and platform.machine()=="x86_64", "exact Linux x64 runner")
    run_phase(root,"node-version",["node","--version"],8,10,384*MIB)
    need((root/"proof/node-version.log").read_text().strip()==m["expectedNodeVersion"], "exact actual Node version")
    run_phase(root,"npm-version",["npm","--version"],8,10,384*MIB)
    receipt(root,"toolchain.json",{"nodeVersion":(root/"proof/node-version.log").read_text().strip(),"npmVersion":(root/"proof/npm-version.log").read_text().strip(),"nodeExecutable":shutil.which("node"),"npmExecutable":shutil.which("npm"),"platform":platform.platform(),"machine":platform.machine(),"setupNodeCommit":"49933ea5288caeca8642d1e84afbd3f7d6820020","nodePin":m["expectedNodeVersion"]})

def phase(root,m,name):
    membership(root,m,name+"-pre")
    if name=="install":
        need(not (root/"stage/node_modules").exists() and not (root/"stage/dist").exists(),"fresh dependency/output dirs")
        run_phase(root,name,["npm","ci","--ignore-scripts","--no-audit","--no-fund"],170,180,384*MIB)
        membership(root,m,name+"-post")
        provision_audit(root,m)
    elif name=="build":
        need(not (root/"stage/dist").exists(),"new dist")
        run_phase(root,name,["npm","run","build"],55,60,384*MIB)
        membership(root,m,name+"-post")
    elif name=="test":
        tests=sorted(x["path"] for x in m["support"] if re.fullmatch(r"tests/[^/]+\.test\.ts",x["path"]))
        need(len(tests)==8,"eight original top level tests")
        receipt(root,"test-scope.json",{"files":tests,"argv":["npm","test"],"browserExecuted":False,"countsAndSkipsSource":"raw test.log only, no synthesized counts"})
        run_phase(root,name,["npm","test"],55,60,768*MIB)
        membership(root,m,name+"-post")


def seal_output(root,m):
    alarm(30)
    membership(root,m,"seal-pre")
    dist=root/"stage/dist"
    rows=regular_inventory(dist,100)
    need(len(rows)==m["expectedOutputCount"],"actual output count differs expected64")
    public={x["path"][7:]:x for x in m["source"] if x["path"].startswith("public/")}
    need(len(public)==59,"source public59")
    for path,pin in public.items():
        need(rows.get(path)=={"bytes":pin["bytes"],"sha256":pin["sha256"]},"copied public byte coherence")
    hashes=dict(sorted((x["path"],x["sha256"]) for x in m["source"]))
    provenance=load_json((dist/"build-provenance.json").read_bytes())
    need(provenance["sourceDigest"]==m["sourceDigest"] and provenance["hashes"]==hashes
         and provenance["node"]==m["expectedNodeVersion"],"NEW build provenance")
    need(rows["CREDITS.md"]["sha256"]==hashes["THIRD-PARTY.md"],"credits copy")
    generated=set(rows)-set(public)-{"CREDITS.md","build-provenance.json","index.html"}
    js=[x for x in generated if re.fullmatch(r"assets/[^/]+\.js",x)]
    css=[x for x in generated if re.fullmatch(r"assets/[^/]+\.css",x)]
    need(len(js)==len(css)==1 and len(generated)==2,"actual generated JS/CSS scope")
    html=(dist/"index.html").read_text()
    refs=re.findall(r'(?:src|href)=["\']([^"\']+)["\']',html)
    local=set()
    for ref in refs:
        if ref.startswith("data:"):
            continue
        need(not re.match(r"[a-zA-Z]+:|//",ref),"unexpected external output ref")
        local.add(ref.removeprefix("./").removeprefix("/"))
    need(set(js+css)<=local and all(x in rows for x in local),"index asset coherence")
    need(m["sourceDigest"].encode() in (dist/js[0]).read_bytes(),"compiled source ID")
    digest=hashlib.sha256(json.dumps(dict(sorted((k,v["sha256"]) for k,v in rows.items())),separators=(",", ":")).encode()).hexdigest()
    receipt(root,"fresh-output-map.json",{"outputs":rows,"outputsDigest":digest,"sourceDigest":m["sourceDigest"],"node":provenance["node"],"outputCount":len(rows),"oldFreezeRestored":False,"oldAliasMetadataRestored":False,"historicalOutputsDigest":m["historicalOldOutputsDigest"],"equalsHistoricalDigestObserved":digest==m["historicalOldOutputsDigest"],"browserGameplayVisualApproval":False})
    need(proof_bytes(root)<=PROOF_CAP,"success proof cap")
    out=root/"success-artifact"
    out.mkdir()
    for key in rows:
        exclusive(out/"dist"/key,(dist/key).read_bytes())
    for key in regular_inventory(root/"proof"):
        exclusive(out/"proof"/key,(root/"proof"/key).read_bytes())
    inventory=regular_inventory(out)
    need(sum(x["bytes"] for x in inventory.values())+256*1024<=ARTIFACT_CAP,"success artifact32MiB withZIPmargin")
    need(disk_inventory(root)<=DISK_CAP,"final disk budget")

def diagnostic(root):
    alarm(20)
    out=root/"failure-artifact"
    out.mkdir()
    rows={}
    # Preserve all bounded regular proof logs; oversized failures retain only an explicit inventory.
    for base,dirs,files in os.walk(root/"proof",followlinks=False):
        for name in dirs:
            need(not (Path(base)/name).is_symlink(),"proof symlink")
        for name in files:
            path=Path(base)/name
            st=path.lstat()
            need(stat.S_ISREG(st.st_mode),"proof regular file")
            h=hashlib.sha256()
            with path.open("rb") as f:
                for b in iter(lambda:f.read(65536),b""):
                    h.update(b)
            rows[path.relative_to(root/"proof").as_posix()]={"bytes":st.st_size,"sha256":h.hexdigest()}
            need(len(rows)<=200,"proof file count")
    complete=sum(x["bytes"] for x in rows.values())<=PROOF_CAP-32*1024
    if complete:
        for key in rows:
            exclusive(out/key,(root/"proof"/key).read_bytes())
    manifest={"status":"FAILED_OR_INCOMPLETE","allProofBytesUploaded":complete,"proofInventory":rows,
        "overCapPolicy":"No deletion/truncation; owned runner originals retained. If over cap, full proof upload is blocked; no complete-log claim. Hosted retention is external.",
        "runtimeBuildGameplayApproval":False}
    b=(json.dumps(manifest,sort_keys=True,separators=(",", ":"))+"\n").encode()
    need(len(b)<=32*1024,"diagnostic inventory cap")
    exclusive(out/"diagnostic-index.json",b)
    need(sum(x["bytes"] for x in regular_inventory(out).values())<=PROOF_CAP,"diagnostic artifact1MiB")

def main():
    need(len(sys.argv)==2 and sys.argv[1] in ("acquire","assemble","preflight","install","build","test","seal","diagnose"),"fixed phase")
    root=context()
    m=metadata()
    mode=sys.argv[1]
    if mode!="acquire":
        need(not os.environ.get("GITHUB_TOKEN"),"token absent outside acquisition")
    if mode=="diagnose":
        diagnostic(root)
        return
    try:
        if mode=="acquire":
            acquire(root,m)
        elif mode=="assemble":
            assemble(root,m)
        elif mode=="preflight":
            preflight(root,m)
        elif mode in ("install","build","test"):
            phase(root,m,mode)
        else:
            seal_output(root,m)
    except BaseException as e:
        if mode in ("install","build","test"):
            try:
                membership(root,m,mode+"-failed-post")
            except BaseException as changed:
                receipt(root,mode+"-failed-post-discrepancy.json",{"status":"INPUT_RECHECK_FAILED","exceptionType":type(changed).__name__},4096)
        # Exception details may contain paths/HTTP content; never print credentials/body.
        receipt(root,mode+"-failure.json",{"phase":mode,"status":"FAILED","exceptionType":type(e).__name__,"message":str(e) if isinstance(e,ValueError) else "details omitted; raw owned phase evidence retained"},4096)
        print("Fixed fresh phase failed: "+mode+" ("+type(e).__name__+")",file=sys.stderr)
        raise SystemExit(1)

if __name__ == "__main__":
    main()
