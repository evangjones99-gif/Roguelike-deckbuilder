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
META_SHA = "5c8cd7ba6b1ab63fa61bbe62c534e786fcdf76cf0ff8f2fb54dc58be14ab2694"
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
    need(len(m["source"]) == 104 and len(m["support"]) == 32 and len(m["blobPins"]) == 59, "fixed input counts")
    need(len({x["path"] for x in m["source"] + m["support"]}) == 136, "fixed paths unique")
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
    need(hashlib.sha256(json.dumps(support, separators=(",", ":")).encode()).hexdigest() == "ec163939480207d096376975f58bad0d4c9b6e56ac23a260a95f9916ea57e414", "fixed original support30 plus two exact archived fixture bodies")
    need(sum(x["path"].startswith("public/") for x in m["source"]) == 65 and m["expectedOutputCount"] == 70, "fixed public65 output70")
    need(len({x["sha256"] for x in m["blobPins"]}) == 59 and [x.get("id") for x in m["blobPins"][-3:]] == ["8cdf", "4513", "ce0f"], "fixed unique blobs and archive suffix")
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
        receipt(root, "acquisition-progress.json", {"verified": rows, "expected": 59, "complete": len(rows)==59, "elapsed":time.monotonic()-start})
    need(len(rows)==59, "all fixed blobs")

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
    receipt(root, "assembly.json", {"archives":reports,"restoredOriginalFilesystemMetadata":False,"sourceFiles":104,"supportFiles":32})

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
    # Exclude only fresh installation/output directories from the 136 pinned inputs.
    for base, dirs, files in os.walk(stage, followlinks=False):
        if Path(base)==stage:
            dirs[:] = [x for x in dirs if x not in ("node_modules", "dist")]
        for name in dirs:
            need(not (Path(base)/name).is_symlink(), "input directory symlink")
        for name in files:
            p = Path(base)/name
            observed[p.relative_to(stage).as_posix()] = hash_file(p)
    expected = {x["path"]:{"bytes":x["bytes"],"sha256":x["sha256"]} for x in m["source"]+m["support"]}
    need(observed==expected, "exact136 membership and bytes")
    hashes = dict(sorted((x["path"],x["sha256"]) for x in m["source"]))
    digest = hashlib.sha256(json.dumps(hashes,separators=(",", ":")).encode()).hexdigest()
    need(digest==m["sourceDigest"], "runtime104 digest")
    receipt(root, label+"-membership.json", {"sourceDigest":digest,"sourceCount":104,"supportCount":32,"supportDigest":hashlib.sha256(json.dumps(dict(sorted((x["path"],x["sha256"]) for x in m["support"])),separators=(",", ":")).encode()).hexdigest()})

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
