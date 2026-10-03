"""Grammar and pure guard checks only: no candidate main, network, extraction or child launch."""
import ast
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import tarfile
from unittest.mock import patch
import yaml

ROOT = Path(__file__).parent
source = (ROOT / "runner.py").read_text()
tree = ast.parse(source, filename="runner.py")
compile(tree, "runner.py", "exec")
selected = {"need", "unique", "load_json", "metadata", "safe_path", "child_env", "member_header", "cgroup_observation", "effective_available"}
body = [n for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom)) or
        isinstance(n, ast.Assign) or isinstance(n, ast.FunctionDef) and n.name in selected or
        isinstance(n, ast.ClassDef) and n.name == "BoundedStream"]
env = {"__name__": "pure_source_definitions"}
exec(compile(ast.Module(body=body, type_ignores=[]), "pure-definitions", "exec"), env)
results = []

def check(name, operation, rejected=False):
    try:
        operation()
    except ValueError:
        assert rejected, name
    else:
        assert not rejected, name
    results.append({"name": name, "pass": True})

meta = env["metadata"]()
assert meta == json.loads((ROOT / "METADATA.json").read_bytes())
results.append({"name": "fixed_metadata_literal_exact", "pass": True})
assert hashlib.sha256((ROOT / "ORIGINAL-BUILD-GRAMMAR.mjs").read_bytes()).hexdigest() == meta["scripts"]["scripts/build.mjs"]
for name in ["src/main.ts", "tests/fixtures/v0.4/content.ts"]:
    check("path_accept_" + name, lambda name=name: env["safe_path"](name))
for name in [".", "", "../x", "/x", "a/../b", "a//b", "a/./b", "a\\b", "x\x00y"]:
    check("path_reject_" + repr(name), lambda name=name: env["safe_path"](name), True)
check("duplicate_json_key", lambda: env["load_json"]('{"x":1,"x":2}'), True)

def member(name="blobs/" + "a" * 64, size=1, type_=tarfile.REGTYPE):
    m = tarfile.TarInfo(name)
    m.size, m.type = size, type_
    return m

check("regular_hash_member", lambda: env["member_header"](member(), "8cdf"))
check("ce0f_index_witness_header", lambda: env["member_header"](member("INDEX.json", 928223), "ce0f"))
for name, value in [("traversal", member("../blobs/" + "a" * 64)),
                    ("symlink", member(type_=tarfile.SYMTYPE)),
                    ("hardlink", member(type_=tarfile.LNKTYPE)),
                    ("device", member(type_=tarfile.CHRTYPE)),
                    ("unknown", member("helper.py")),
                    ("too_large", member(size=9 * 1048576 + 1))]:
    check("archive_reject_" + name, lambda value=value: env["member_header"](value, "ce0f"), True)
sparse = member()
sparse.sparse = [(0, 1)]
check("archive_reject_sparse", lambda: env["member_header"](sparse, "ce0f"), True)
pax = member()
pax.pax_headers = {"path": "x"}
check("archive_reject_pax", lambda: env["member_header"](pax, "ce0f"), True)
check("index_wrong_container", lambda: env["member_header"](member("INDEX.json", 928223), "8cdf"), True)
check("index_wrong_size", lambda: env["member_header"](member("INDEX.json", 928224), "ce0f"), True)
bounded = env["BoundedStream"](io.BytesIO(b"abc"), 3)
assert bounded.read(3) == b"abc" and bounded.read(1) == b""
results.append({"name": "stream_exact_bound", "pass": True})
check("stream_overflow", lambda: env["BoundedStream"](io.BytesIO(b"abcd"), 3).read(4), True)
check("stream_unbounded_read", lambda: env["BoundedStream"](io.BytesIO(b"a"), 3).read(), True)
with patch.dict(os.environ, {"PATH": "/trusted/bin", "HOME": "/home/runner", "GITHUB_TOKEN": "fake", "ACTIONS_RUNTIME_TOKEN": "fake", "NPM_TOKEN": "fake", "NODE_OPTIONS": "unsafe"}, clear=True):
    child = env["child_env"](Path("/owned/example"))
assert all(x not in child for x in ("GITHUB_TOKEN", "ACTIONS_RUNTIME_TOKEN", "NPM_TOKEN"))
assert child["NODE_OPTIONS"] == "--max-old-space-size=256"
assert child["npm_config_userconfig"] == child["npm_config_globalconfig"] == "/dev/null"
results.append({"name": "credential_free_child_environment", "pass": True})
env["mem_available"] = lambda: 1000
env["cgroup_observation"] = lambda: {"available": True, "max": "500", "current": 400}
assert env["effective_available"]() == 100
env["cgroup_observation"] = lambda: {"available": True, "max": "max", "current": 400}
assert env["effective_available"]() == 1000
results.append({"name": "host_finite_cgroup_min_headroom", "pass": True})

workflow = yaml.safe_load((ROOT / "rebuild-opening-baseline.yml").read_text())
trigger = workflow.get("on", workflow.get(True))
assert trigger == {"push": {"branches": ["codex/lanternbound-production"], "paths": [".github/workflows/rebuild-opening-baseline.yml"]}, "workflow_dispatch": {}}
assert workflow["permissions"] == {}
job = workflow["jobs"]["fresh-baseline"]
assert job["permissions"] == {"contents": "read"} and job["timeout-minutes"] == 15
init = job["steps"][0]["run"]
init_py = init[init.index("\n") + 1:init.rindex("\nPY")]
init_tree = ast.parse(init_py)
embedded = next(ast.literal_eval(n.value) for n in init_tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "source" for t in n.targets))
assert embedded == source
results.append({"name": "workflow_embedded_source_exact", "pass": True})
for step in job["steps"]:
    if "run" in step:
        proc = subprocess.run(["bash", "-n"], input=step["run"], text=True, capture_output=True)
        assert proc.returncode == 0, proc.stderr
    if step.get("uses", "").startswith("actions/upload-artifact"):
        w = step["with"]
        assert step["uses"].endswith("ea165f8d65b6e75b540449e92b4886f43607fa02")
        assert w["compression-level"] == 0 and w["overwrite"] is False and w["include-hidden-files"] is False
        assert w["retention-days"] == 30 and w["if-no-files-found"] == "error"
results.append({"name": "all_shell_grammar_and_upload_pins", "pass": True})
setup = next(x for x in job["steps"] if x.get("id") == "setup")
assert setup["uses"].endswith("49933ea5288caeca8642d1e84afbd3f7d6820020")
assert setup["with"] == {"node-version": "24.19.0", "architecture": "x64", "check-latest": False, "token": ""}
assert sum("GITHUB_TOKEN" in x.get("env", {}) for x in job["steps"]) == 1
assert next(x for x in job["steps"] if "GITHUB_TOKEN" in x.get("env", {}))["id"] == "acquire"
results.append({"name": "setup_token_blank_and_only_acquisition_credential", "pass": True})
check_js = subprocess.run(["node", "--check", str(ROOT / "ORIGINAL-BUILD-GRAMMAR.mjs")], capture_output=True, text=True)
assert check_js.returncode == 0, check_js.stderr
results.append({"name": "original_build_JS_grammar_only", "pass": True})
receipt = {"status": "PASS_SOURCE_ONLY", "cases": results, "caseCount": len(results), "pythonASTCompiled": True,
           "candidateMainExecuted": False, "networkExecuted": False, "archiveOpened": False,
           "npmBuildTestExecuted": False, "methodSHA256": hashlib.sha256(source.encode()).hexdigest(),
           "workflowSHA256": hashlib.sha256((ROOT / "rebuild-opening-baseline.yml").read_bytes()).hexdigest()}
with (ROOT / "SOURCE-CHECKS.json").open("x") as f:
    json.dump(receipt, f, indent=2)
    f.write("\n")
print(json.dumps({"status": receipt["status"], "caseCount": len(results)}))
