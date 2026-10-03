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
WORKFLOW = REPO + "/.github/workflows/rebuild-opening-cue-candidate.yml@" + REF
MIB = 1048576
META_SHA = "bbc8830505d51278a76f9913ff7d1564c6632fdc32e746b2b6e09417ecbddf17"
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
    need(len(m["source"]) == 104 and len(m["support"]) == 30 and len(m["blobPins"]) == 57, "fixed input counts")
    need(len({x["path"] for x in m["source"] + m["support"]}) == 134, "fixed paths unique")
    for x in m["source"] + m["support"]:
        safe_path(x["path"])
        need(re.fullmatch(r"[0-9a-f]{64}", x["sha256"]) and 0 <= x["bytes"] <= FILE_CAP, "input pin")
    hashes = dict(sorted((x["path"], x["sha256"]) for x in m["source"]))
    digest = hashlib.sha256(json.dumps(hashes, separators=(",", ":")).encode()).hexdigest()
    need(digest == m["sourceDigest"] == "993aa3681596c2488d4d394744e5beda2778ffcba3e1649736612304d20b50c5", "fixed C source104 digest")
    need(hashes["src/main.ts"] == "87a9bd7c2319522f77db7ea9e2edc306bb6124b019306dc220087f6b9b7762f4", "fixed C main")
    hashes["src/main.ts"] = "d1e71626b4c70679f4ba692b62ccb2aea0dbe5ce74e9a1426b6208fc26a45fe2"
    need(hashlib.sha256(json.dumps(hashes, separators=(",", ":")).encode()).hexdigest() == "65b31b3f21e34a624bdac962e4919c7dc1791e502eb6cfdb1612103b8036fe9c", "B to C only main changes")
    support = dict(sorted((x["path"], x["sha256"]) for x in m["support"]))
    need(hashlib.sha256(json.dumps(support, separators=(",", ":")).encode()).hexdigest() == "b21a0766a30f581221ad009e448f4f9c103efe017682e462ce1548263ada327e", "fixed original support30")
    need(sum(x["path"].startswith("public/") for x in m["source"]) == 65 and m["expectedOutputCount"] == 70, "fixed public65 output70")
    need(len({x["sha256"] for x in m["blobPins"]}) == 57 and [x.get("id") for x in m["blobPins"][-3:]] == ["8cdf", "4513", "ce0f"], "fixed unique blobs and archive suffix")
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
    root = temp / ("opening-cue-fresh-" + rid + "-" + attempt)
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
            "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "fixed-opening-cue-byte-recovery"})
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
        receipt(root, "acquisition-progress.json", {"verified": rows, "expected": 57, "complete": len(rows)==57, "elapsed":time.monotonic()-start})
    need(len(rows)==57, "all fixed blobs")

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
    receipt(root, "assembly.json", {"archives":reports,"restoredOriginalFilesystemMetadata":False,"sourceFiles":104,"supportFiles":30})

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
    # Exclude only fresh installation/output directories from the 134 pinned inputs.
    for base, dirs, files in os.walk(stage, followlinks=False):
        if Path(base)==stage:
            dirs[:] = [x for x in dirs if x not in ("node_modules", "dist")]
        for name in dirs:
            need(not (Path(base)/name).is_symlink(), "input directory symlink")
        for name in files:
            p = Path(base)/name
            observed[p.relative_to(stage).as_posix()] = hash_file(p)
    expected = {x["path"]:{"bytes":x["bytes"],"sha256":x["sha256"]} for x in m["source"]+m["support"]}
    need(observed==expected, "exact134 membership and bytes")
    hashes = dict(sorted((x["path"],x["sha256"]) for x in m["source"]))
    digest = hashlib.sha256(json.dumps(hashes,separators=(",", ":")).encode()).hexdigest()
    need(digest==m["sourceDigest"], "runtime104 digest")
    receipt(root, label+"-membership.json", {"sourceDigest":digest,"sourceCount":104,"supportCount":30,"supportDigest":hashlib.sha256(json.dumps(dict(sorted((x["path"],x["sha256"]) for x in m["support"])),separators=(",", ":")).encode()).hexdigest()})

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
            inventory=regular_inventory(package,100,128*MIB)
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
        run_phase(root,name,["npm","test"],55,60,384*MIB)
        membership(root,m,name+"-post")


def seal_output(root,m):
    alarm(30)
    membership(root,m,"seal-pre")
    dist=root/"stage/dist"
    rows=regular_inventory(dist,100)
    need(len(rows)==m["expectedOutputCount"],"actual output count differs expected70")
    public={x["path"][7:]:x for x in m["source"] if x["path"].startswith("public/")}
    need(len(public)==65,"source public65")
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
