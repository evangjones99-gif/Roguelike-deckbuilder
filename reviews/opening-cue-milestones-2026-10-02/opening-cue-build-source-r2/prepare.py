"""Authoring-only deterministic adaptation of the exact frozen R6 shared method; full inverse restores old C R1."""
import base64
import gzip
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).parent
PARENT = ROOT.parent / 'empty-intent-fresh-ci-source-r6'
PINS = {'runner.py': '6dfdf0ca7be2053e3995f361746151e0f0c7447a4303b7c131529f158cc8c4b8',
        'rebuild-opening-baseline.yml': 'e4db8c93cc7a679a7639fdc1d64f9288189f796acf0c1feceb5a4d0c90afcaaa',
        'METADATA.json': 'b2f13179f14ccebecbc4452fa4e6b3cc88623dc629ff0009c1118401123ca46d'}
SHA = lambda b: hashlib.sha256(b).hexdigest()

def embedded(text):
    assert text.endswith('\n')
    return text.replace('\n', '\n          ')[:-10]

def main():
    originals = {name: (PARENT / name).read_bytes() for name in PINS}
    assert all(SHA(originals[name]) == pin for name, pin in PINS.items())
    assert SHA((PARENT / 'SOURCE-SEAL.json').read_bytes()) == 'ba7cab54f2083374efb1a9fbd8328bcd6bd6a223a1aa3c08dd201b5a3cd6fdcc'
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
    old_c = ROOT.parent / 'opening-cue-build-source-r1'
    old_pins = {'runner.py':'fe6fcff5fa5dd129061678a076d88ddfa938d5b2625f1db76e1c148cd69b29b0','rebuild-opening-cue-candidate.yml':'c53ec089963dc5f5553eecad91e7feba384ff6bb9f4ba5f0bc508bb054739101','METADATA.json':'bbc8830505d51278a76f9913ff7d1564c6632fdc32e746b2b6e09417ecbddf17'}
    old_bodies = {name:(old_c/name).read_bytes() for name in old_pins}
    assert all(SHA(old_bodies[name])==pin for name,pin in old_pins.items())
    old_embedded = embedded(old_bodies['runner.py'].decode())
    old_workflow = old_bodies['rebuild-opening-cue-candidate.yml'].decode()
    assert old_workflow.count(old_embedded)==1
    inverse_template = old_workflow.replace(old_embedded,'{{EXACT_PARENT_RUNNER}}')
    inverse_pins = {}
    for name, body in old_bodies.items():
        stored = inverse_template.encode() if name == 'rebuild-opening-cue-candidate.yml' else body
        filename = 'INVERSE-' + name + '.gz'
        (ROOT / filename).write_bytes(gzip.compress(stored, mtime=0))
        inverse_pins[name] = {'sha256': SHA(body), 'bytes': len(body), 'inverseBody': filename,
                             'inverseEncoding': 'gzip-workflow-template-plus-exact-parent-runner' if name == 'rebuild-opening-cue-candidate.yml' else 'gzip-full-body'}
    # The inverse template and complete original runner reconstruct the exact full workflow.
    assert inverse_template.replace('{{EXACT_PARENT_RUNNER}}', old_embedded).encode() == old_bodies['rebuild-opening-cue-candidate.yml']
    (ROOT / 'ADAPTATION.json').write_text(json.dumps({'status': 'SOURCE_ONLY_FROZEN_PREDECESSOR_INDEPENDENT_REVIEW_PENDING',
        'predecessorDirectory': str(old_c), 'predecessorFiles': inverse_pins,
        'sharedMethod': {'directory':str(PARENT),'files':{name:{'sha256':SHA(body),'bytes':len(body)} for name,body in originals.items()},'sourceSealSHA256':'ba7cab54f2083374efb1a9fbd8328bcd6bd6a223a1aa3c08dd201b5a3cd6fdcc','manifestSHA256':'28ef12400f0b937cd6227065efe87508f759a32674fb1802e20a846f341402bb','independentAcceptance':'PENDING_AT_SEAL'},
        'predecessorSourceSealSHA256': 'b2f095b052d6ebad7d28db5c7556c072956fb354d2b8890d72df4d0c00c5c0b8',
        'predecessorManifestSHA256': 'b38acd6f9cf8930459981e69b28c215395ae53b42f7cda4f3cc9d4b216c395a8',
        'replacementsExceptMetadataLiteral': replacements,
        'metadataLiteralReplacement': 'Deterministic gzip of exact candidate METADATA.json; original complete metadata and runner retained in inverse bodies.',
        'publicationCondition': 'Exact coherent7cc body is published812; Root must independently accept frozen R6 method and C adaptation before publication/run. Runtime budgets unchanged. Prior actual failures have no observed traceback site.'}, separators=(',', ':')) + '\n')

if __name__ == '__main__':
    main()
