"""Read-only synthetic filesystem check of exact audit function; no real dependency execution."""
import ast
import hashlib
import json
from pathlib import Path, PurePosixPath

ROOT = Path("/workspace/scratch/empty-intent-fresh-ci-source-r2")
tree = ast.parse((ROOT / "runner.py").read_text())
functions = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in ("provision_audit", "need", "load_json", "unique", "safe_path")]
pins = {name: {"version": "1.0.0", "resolved": "https://registry.npmjs.org/fixed", "integrity": "sha512-fixed", "bin": {command: entry}} for name, command, entry in
        [("typescript", "tsc", "bin/tsc"), ("vite", "vite", "bin/vite.js"), ("tsx", "tsx", "dist/cli.mjs"), ("@playwright/test", "playwright", "cli.js")]}
lock = {"packages": {"node_modules/" + name: pin for name, pin in pins.items()}}
reads = []
wrong_tsx = False

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
        return json.dumps(pins[name]).encode()

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
env = {"json": json, "PurePosixPath": PurePosixPath, "re": __import__("re"), "FILE_CAP": 9*1048576,
       "platform": FakePlatform, "hash_file": lambda path: {"sha256": "a"*64, "bytes": 1},
       "receipt": lambda root, name, obj: receipts.append(obj)}
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
result = {"status": "PASS_PURE_SOURCE_ONLY", "cases": ["shared_unused_playwright_shim_not_admitted", "type_only_metadata_and_entry_hash_retained", "three_relevant_executable_shims_checked", "unowned_tsx_resolution_rejected"], "methodSHA256": hashlib.sha256((ROOT / "runner.py").read_bytes()).hexdigest(), "realFilesystemDependencyWrites": False, "archiveNetworkMainChildExecution": False}
with (Path("/workspace/scratch/empty-intent-fresh-ci-technical-r2") / "SHARED-SHIM-PROOF.json").open("x") as f:
    json.dump(result, f, separators=(",", ":"))
    f.write("\n")
print(result["status"])
