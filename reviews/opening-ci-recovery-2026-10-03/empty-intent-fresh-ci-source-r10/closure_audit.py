"""Read-only audit of original eight tests' literal imports and filesystem dependencies."""
import hashlib
import json
import os
from pathlib import Path
import re

ROOT=Path(__file__).parent
STAGE=ROOT.parent/"empty-intent-source-recovered-stage-r1"
META=json.loads((ROOT/"METADATA.json").read_bytes())
PINSET={x["path"]:x for x in META["source"]+META["support"]}
FIXTURES=json.loads((ROOT.parent/"opening-ci-original-test-fixtures-root-r1/FIXTURE-PINS.json").read_bytes())
fixture_bodies={x["path"]:Path(x["bodyPath"]) for x in FIXTURES["files"]}
tests=sorted(x["path"] for x in META["support"] if re.fullmatch(r"tests/[^/]+\.test\.ts",x["path"]))
assert len(tests)==8
pending=list(tests)
seen={}
edges=[]
external=set()
fs_sites=[]
literal_urls=[]
hash_sites=[]
def logical(base,name):
    path=os.path.normpath(str(Path(base).parent/name))
    assert not path.startswith("../") and not Path(path).is_absolute(),(base,name)
    return Path(path).as_posix()
def resolve(base,name):
    value=logical(base,name)
    choices=[value,value+".ts",value+".tsx",value+".js",value+"/index.ts"]
    matches=[x for x in choices if x in PINSET]
    assert len(matches)==1,(base,name,matches)
    return matches[0]

while pending:
    name=pending.pop()
    if name in seen:
        continue
    pin=PINSET[name]
    path=fixture_bodies.get(name,STAGE/name)
    b=path.read_bytes()
    assert len(b)==pin["bytes"] and hashlib.sha256(b).hexdigest()==pin["sha256"],name
    text=b.decode()
    seen[name]={"bytes":len(b),"sha256":pin["sha256"]}
    specs=set(re.findall(r"\bfrom\s*['\"]([^'\"]+)['\"]",text))
    specs.update(re.findall(r"\bimport\s*\(\s*['\"]([^'\"]+)['\"]",text))
    specs.update(re.findall(r"\bimport\s*['\"]([^'\"]+)['\"]",text))
    specs.update(re.findall(r"\brequire\s*\(\s*['\"]([^'\"]+)['\"]",text))
    for spec in sorted(specs):
        if spec.startswith("."):
            target=resolve(name,spec)
            edges.append({"file":name,"literalImport":spec,"resolved":target})
            pending.append(target)
        else:
            external.add(spec)
    for no,line in enumerate(text.splitlines(),1):
        if re.search(r"readFile(?:Sync)?\s*\(|\b(?:writeFile|readdir|access|stat|open)(?:Sync)?\s*\(|\bfs\.",line):
            fs_sites.append({"file":name,"line":no,"source":line.strip()[:320]})
    for match in re.finditer(r"new\s+URL\s*\(\s*['\"]([^'\"]+)['\"]\s*,\s*import\.meta\.url",text):
        target=logical(name,match[1])
        assert target in PINSET,(name,target)
        literal_urls.append({"file":name,"literalURL":match[1],"resolved":target})
        pending.append(target)
    for match in re.finditer(r"\bhash\(\s*['\"]([^'\"]+)['\"]\s*\)",text):
        target=logical(name,match[1])
        assert target in PINSET,(name,target)
        hash_sites.append({"file":name,"literalHashRead":match[1],"resolved":target})
        pending.append(target)

assert external=={"node:test","node:assert/strict","node:fs","node:crypto","node:url","esbuild"},external
fs_files={x["file"] for x in fs_sites}
assert fs_files=={"tests/world-rng-v0.5.test.ts","tests/save-validity-v0.4.test.ts"},fs_files
assert len(fs_sites)==4,fs_sites
assert {x["resolved"] for x in hash_sites}=={"tests/fixtures/v0.4/engine.ts","tests/fixtures/v0.4/content.ts"}
json_reads={x["resolved"] for x in literal_urls if x["resolved"].endswith(".json")}
assert json_reads==set(fixture_bodies),json_reads
assert len([x for x in literal_urls if x["resolved"].endswith(".json")])==3
assert {x["resolved"] for x in literal_urls if x["resolved"].endswith(".ts")}=={"src/audio-host.ts"}
result={"status":"PASS_READONLY_STATIC_TEST_CLOSURE","entryTests":tests,"verifiedBodies":seen,
    "literalImportEdges":edges,"externalBuiltinsAndInstalledPackage":sorted(external),
    "filesystemReadSites":fs_sites,"literalURLReads":literal_urls,"parameterHashCalls":hash_sites,
    "onlyPreviouslyMissingReadBodies":sorted(json_reads),
    "dynamicImportQualification":"Original audio test imports its write:false esbuild-produced data URL from pinned src/audio-host.ts; hunter literal dynamic import/type import traversed. This is static source audit, not runtime filesystem tracing or TypeScript parser completeness.",
    "originalTestBodiesAndScriptsChanged":False,"candidateMainNpmNetworkBuildBrowserExecuted":False}
(ROOT/"TEST-CLOSURE-AUDIT.json").write_text(json.dumps(result,sort_keys=True,separators=(",",":"))+"\n")
print(json.dumps({"status":result["status"],"tests":len(tests),"verifiedBodies":len(seen),"missingRestored":len(json_reads)}))
