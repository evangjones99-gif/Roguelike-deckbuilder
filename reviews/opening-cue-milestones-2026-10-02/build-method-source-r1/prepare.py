"""Authoring-only deterministic adaptation of the exact frozen R4 predecessor."""
import base64
import gzip
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).parent
PARENT = ROOT.parent / 'empty-intent-fresh-ci-source-r4'
PINS = {'runner.py': '1241c9f9d3dce4248e566df2facd7b0218a08684d0b292647eb90c631d1a5ab7',
        'rebuild-opening-baseline.yml': '26da96127464740600fe3d76bdde2b2b3525a888a2c9e4a0e5d304cf0e61f2ff',
        'METADATA.json': 'b2f13179f14ccebecbc4452fa4e6b3cc88623dc629ff0009c1118401123ca46d'}
SHA = lambda b: hashlib.sha256(b).hexdigest()

def embedded(text):
    assert text.endswith('\n')
    return text.replace('\n', '\n          ')[:-10]

def main():
    originals = {name: (PARENT / name).read_bytes() for name in PINS}
    assert all(SHA(originals[name]) == pin for name, pin in PINS.items())
    assert SHA((PARENT / 'SOURCE-SEAL.json').read_bytes()) == '51f4e42e9ca6d846ad6edd93cb0445936becdf07a7230204c9b9e4ebb71a1080'
    source = originals['runner.py'].decode()
    meta_bytes = (ROOT / 'METADATA.json').read_bytes()
    meta = json.loads(meta_bytes)
    support_digest = SHA(json.dumps(dict(sorted((x['path'], x['sha256']) for x in meta['support'])), separators=(',', ':')).encode())
    replacements = []
    def replace(old, new, count=1):
        nonlocal source
        assert source.count(old) == count, old
        source = source.replace(old, new)
        replacements.append({'before': old, 'after': new, 'count': count})
    source = re.sub(r'^META_LITERAL = ".*"$', 'META_LITERAL = ' + json.dumps(base64.b64encode(gzip.compress(meta_bytes, mtime=0)).decode()), source, count=1, flags=re.M)
    replace(PINS['METADATA.json'], SHA(meta_bytes))
    replace('/.github/workflows/rebuild-opening-baseline.yml@', '/.github/workflows/rebuild-opening-cue-candidate.yml@')
    replace('empty-intent-fresh-', 'opening-cue-fresh-')
    replace('fixed-empty-intent-byte-recovery', 'fixed-opening-cue-byte-recovery')
    replace('len(m["source"]) == 98 and len(m["support"]) == 30 and len(m["blobPins"]) == 53', 'len(m["source"]) == 104 and len(m["support"]) == 30 and len(m["blobPins"]) == 57')
    replace('}) == 128, "fixed paths unique")', '}) == 134, "fixed paths unique")')
    replace('    return m\n', '''    hashes = dict(sorted((x["path"], x["sha256"]) for x in m["source"]))
    digest = hashlib.sha256(json.dumps(hashes, separators=(",", ":")).encode()).hexdigest()
    need(digest == m["sourceDigest"] == "993aa3681596c2488d4d394744e5beda2778ffcba3e1649736612304d20b50c5", "fixed C source104 digest")
    need(hashes["src/main.ts"] == "87a9bd7c2319522f77db7ea9e2edc306bb6124b019306dc220087f6b9b7762f4", "fixed C main")
    hashes["src/main.ts"] = "d1e71626b4c70679f4ba692b62ccb2aea0dbe5ce74e9a1426b6208fc26a45fe2"
    need(hashlib.sha256(json.dumps(hashes, separators=(",", ":")).encode()).hexdigest() == "65b31b3f21e34a624bdac962e4919c7dc1791e502eb6cfdb1612103b8036fe9c", "B to C only main changes")
    support = dict(sorted((x["path"], x["sha256"]) for x in m["support"]))
    need(hashlib.sha256(json.dumps(support, separators=(",", ":")).encode()).hexdigest() == "SUPPORT_DIGEST", "fixed original support30")
    need(sum(x["path"].startswith("public/") for x in m["source"]) == 65 and m["expectedOutputCount"] == 70, "fixed public65 output70")
    need(len({x["sha256"] for x in m["blobPins"]}) == 57 and [x.get("id") for x in m["blobPins"][-3:]] == ["8cdf", "4513", "ce0f"], "fixed unique blobs and archive suffix")
    return m
'''.replace('SUPPORT_DIGEST', support_digest))
    replace('"expected": 53, "complete": len(rows)==53', '"expected": 57, "complete": len(rows)==57')
    replace('need(len(rows)==53, "all fixed blobs")', 'need(len(rows)==57, "all fixed blobs")')
    replace('"sourceFiles":98', '"sourceFiles":104')
    replace('the 128 pinned inputs', 'the 134 pinned inputs')
    replace('"exact128 membership and bytes"', '"exact134 membership and bytes"')
    replace('"runtime98 digest"', '"runtime104 digest"')
    replace('"sourceCount":98', '"sourceCount":104')
    replace('"actual output count differs expected64"', '"actual output count differs expected70"')
    replace('need(len(public)==59,"source public59")', 'need(len(public)==65,"source public65")')
    (ROOT / 'runner.py').write_text(source)
    workflow = originals['rebuild-opening-baseline.yml'].decode()
    old_embedded = embedded(originals['runner.py'].decode())
    assert workflow.count(old_embedded) == 1
    inverse_template = workflow.replace(old_embedded, '{{EXACT_PARENT_RUNNER}}')
    workflow = workflow.replace(old_embedded, embedded(source))
    workflow = workflow.replace(PINS['runner.py'], SHA(source.encode())).replace(PINS['METADATA.json'], SHA(meta_bytes))
    workflow = workflow.replace('Rebuild exact empty-intent opening baseline', 'Build exact opening cue candidate C')
    workflow = workflow.replace('rebuild-opening-baseline.yml', 'rebuild-opening-cue-candidate.yml')
    workflow = workflow.replace('fresh-baseline:', 'fresh-cue-candidate:')
    workflow = workflow.replace('empty-intent-fresh-baseline-', 'opening-cue-fresh-candidate-')
    workflow = workflow.replace('empty-intent-fresh-', 'opening-cue-fresh-').replace('empty-intent-diagnostic-', 'opening-cue-diagnostic-')
    workflow = workflow.replace('Acquire exactly fifty canonical bodies and three original containers', 'Acquire fifty-four fixed direct bodies and three original containers')
    workflow = workflow.replace('runtime98 and support30', 'candidate source104 and original support30')
    (ROOT / 'rebuild-opening-cue-candidate.yml').write_text(workflow)
    inverse_pins = {}
    for name, body in originals.items():
        stored = inverse_template.encode() if name == 'rebuild-opening-baseline.yml' else body
        filename = 'INVERSE-' + name + '.gz'
        (ROOT / filename).write_bytes(gzip.compress(stored, mtime=0))
        inverse_pins[name] = {'sha256': SHA(body), 'bytes': len(body), 'inverseBody': filename,
                             'inverseEncoding': 'gzip-workflow-template-plus-exact-parent-runner' if name == 'rebuild-opening-baseline.yml' else 'gzip-full-body'}
    # The inverse template and complete original runner reconstruct the exact full workflow.
    assert inverse_template.replace('{{EXACT_PARENT_RUNNER}}', old_embedded).encode() == originals['rebuild-opening-baseline.yml']
    (ROOT / 'ADAPTATION.json').write_text(json.dumps({'status': 'SOURCE_ONLY_FROZEN_PREDECESSOR_INDEPENDENT_REVIEW_PENDING',
        'predecessorDirectory': str(PARENT), 'predecessorFiles': inverse_pins,
        'predecessorSourceSealSHA256': '51f4e42e9ca6d846ad6edd93cb0445936becdf07a7230204c9b9e4ebb71a1080',
        'predecessorManifestSHA256': '1c8b2dea0a033a26abf203598f321b32bb61a79959a7da94bdbef4f9378dad70',
        'replacementsExceptMetadataLiteral': replacements,
        'metadataLiteralReplacement': 'Deterministic gzip of exact candidate METADATA.json; original complete metadata and runner retained in inverse bodies.',
        'publicationCondition': 'Root commits coherent body review path and independently accepts both frozen R4 method and candidate adaptation before any workflow run.'}, separators=(',', ':')) + '\n')

if __name__ == '__main__':
    main()
