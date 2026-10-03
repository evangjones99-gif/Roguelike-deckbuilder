"""Read-only synthetic filesystem check of exact audit function; no real dependency execution."""
import ast
import hashlib
import json
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).parent
tree = ast.parse((ROOT / "runner.py").read_text())
functions = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in ("provision_audit", "need", "load_json", "unique", "safe_path", "canonical_bin_map", "observed_bin")]
pins = {name: {"version": "1.0.0", "resolved": "https://registry.npmjs.org/fixed", "integrity": "sha512-fixed", "bin": {command: entry}} for name, command, entry in
        [("typescript", "tsc", "bin/tsc"), ("vite", "vite", "bin/vite.js"), ("tsx", "tsx", "dist/cli.mjs"), ("@playwright/test", "playwright", "cli.js")]}
lock = {"packages": {"node_modules/" + name: pin for name, pin in pins.items()}}
reads = []
wrong_tsx = False
actual_bin_overrides = {}

class FakePath:
    def __init__(self, value):
        self.value = PurePosixPath(str(value))
    def __truediv__(self, other):
        return FakePath(self.value / other)
    def __str__(self):
        return str(self.value)
    def __eq__(self, other):
        return isinstance(other, FakePath) and self.value == other.value
    @property
    def parent(self):
        return FakePath(self.value.parent)
    @property
    def parents(self):
        return [FakePath(p) for p in self.value.parents]
    def is_dir(self):
        return True
    def is_symlink(self):
        return "/.bin/" in str(self)
    def resolve(self, strict=True):
        path = str(self)
        reads.append(path)
        replacements = {"tsc": "typescript/bin/tsc", "vite": "vite/bin/vite.js", "tsx": "tsx/dist/cli.mjs", "playwright": "playwright/cli.js"}
        if "/.bin/" in path:
            command = self.value.name
            if wrong_tsx and command == "tsx":
                return FakePath("/outside/unowned/tsx")
            return FakePath("/owned/stage/node_modules/" + replacements[command])
        return self
    def is_relative_to(self, other):
        return self.value.is_relative_to(other.value)
    def read_bytes(self):
        path = str(self)
        if path.endswith("package-lock.json"):
            return json.dumps(lock).encode()
        assert path.endswith("/package.json"), path
        name = path.removeprefix("/owned/stage/node_modules/").removesuffix("/package.json")
        data=dict(pins[name])
        if name in actual_bin_overrides:
            data["bin"]=actual_bin_overrides[name]
        return json.dumps(data).encode()

class FakePlatform:
    @staticmethod
    def platform():
        return "synthetic-linux"
    @staticmethod
    def machine():
        return "x86_64"
    @staticmethod
    def libc_ver():
        return ("glibc", "synthetic")

receipts = []
env = {"json": json, "hashlib": hashlib, "PurePosixPath": PurePosixPath, "re": __import__("re"), "FILE_CAP": 9*1048576,
       "platform": FakePlatform, "hash_file": lambda path,cap=None: {"sha256": "a"*64, "bytes": 1},
       "receipt": lambda root, name, obj,cap=None: receipts.append(obj)}
exec(compile(ast.Module(body=functions, type_ignores=[]), "synthetic-audit-definitions", "exec"), env)
env["provision_audit"](FakePath("/owned"), {"tools": pins, "expectedNodeVersion": "v24.19.0"})
assert not any("/.bin/playwright" in path for path in reads)
rows = receipts[-1]["selectedPackages"]
playwright = next(x for x in rows if x["package"] == "@playwright/test")
assert playwright["entryAndNativeHashes"]["cli.js"]["bytes"] == 1
assert playwright["binResolution"].startswith("Type-only")
for name in ("typescript", "vite", "tsx"):
    assert next(x for x in rows if x["package"] == name)["binResolution"].startswith("Owned selected executable")
wrong_tsx = True
try:
    env["provision_audit"](FakePath("/owned"), {"tools": pins, "expectedNodeVersion": "v24.19.0"})
except ValueError:
    pass
else:
    raise AssertionError("unowned actual executable shim should fail")
wrong_tsx = False
bin_cases=[]
def audit_case(name, package, bin_value, rejection=False):
    actual_bin_overrides.clear()
    actual_bin_overrides[package]=bin_value
    before=len(receipts)
    try:
        env["provision_audit"](FakePath("/owned"), {"tools": pins, "expectedNodeVersion": "v24.19.0"})
    except ValueError:
        assert rejection, name
        # Actual observation is preserved before the refused mapping.
        assert len(receipts)>before and receipts[-1]["diagnosticOnlyNotAdmission"]
    else:
        assert not rejection, name
    bin_cases.append(name)

audit_case("leading_dot_path_equivalence", "vite", {"vite":"./bin/vite.js"})
audit_case("single_package_named_string_bin", "vite", "./bin/vite.js")
audit_case("safe_unexecuted_extra_command", "typescript", {"tsc":"bin/tsc","tsserver":"./bin/tsserver"})
assert next(row for row in receipts[-1]["selectedPackages"] if row["package"]=="typescript")["unusedBinCommandsNotExecuted"]==["tsserver"]
audit_case("changed_required_path_rejected", "vite", {"vite":"bin/wrong.js"}, True)
audit_case("missing_required_command_rejected", "vite", {}, True)
audit_case("traversal_required_path_rejected", "vite", {"vite":"./../outside"}, True)
audit_case("absolute_required_path_rejected", "vite", {"vite":"/outside"}, True)
audit_case("internal_parent_segment_rejected", "vite", {"vite":"bin/../outside"}, True)
audit_case("unsafe_extra_command_path_rejected", "vite", {"vite":"bin/vite.js","unused":"../outside"}, True)
audit_case("extra_node_shadow_rejected", "vite", {"vite":"bin/vite.js","node":"bin/shadow.js"}, True)
audit_case("unsupported_bin_shape_rejected", "vite", ["bin/vite.js"], True)
audit_case("oversized_command_set_rejected", "vite", {"vite":"bin/vite.js",**{"extra"+str(i):"bin/unused" for i in range(32)}}, True)
bounded=env["observed_bin"]("a"*20000)
assert bounded["complete"] is False and bounded["serializedBytes"]==20002
assert len(bounded["prefix"])<=1024
bin_cases.append("oversized_diagnostic_bounded_and_explicit")

result = {"status": "PASS_PURE_SOURCE_ONLY", "cases": ["shared_unused_playwright_shim_not_admitted", "type_only_metadata_and_entry_hash_retained", "three_relevant_executable_shims_checked", "unowned_tsx_resolution_rejected"]+bin_cases, "methodSHA256": hashlib.sha256((ROOT / "runner.py").read_bytes()).hexdigest(), "realFilesystemDependencyWrites": False, "archiveNetworkMainChildExecution": False}
with (ROOT / "SHARED-SHIM-CHECKS.json").open("x") as f:
    json.dump(result, f, separators=(",", ":"))
    f.write("\n")
print(result["status"])
