"""Authoring-only deterministic adaptation of the accepted frozen R8 shared method; raw inverse restores complete old C2 functional files."""
import base64
import gzip
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).parent
PARENT = ROOT.parent / 'empty-intent-fresh-ci-source-r8'
PINS = {'runner.py': '9047ffa92b385965ec4f726a964116c457afc866d0303a218a9b2ab6c98ee392',
        'rebuild-opening-baseline.yml': '813edcaa9898b186cfbe5f50d6a53dc79a4075381d707cc3c42d2b686e63e1ef',
        'METADATA.json': 'b2f13179f14ccebecbc4452fa4e6b3cc88623dc629ff0009c1118401123ca46d'}
SHA = lambda b: hashlib.sha256(b).hexdigest()

def embedded(text):
    assert text.endswith('\n')
    return text.replace('\n', '\n          ')[:-10]

def main():
    originals = {name: (PARENT / name).read_bytes() for name in PINS}
    assert all(SHA(originals[name]) == pin for name, pin in PINS.items())
    assert SHA((PARENT / 'SOURCE-SEAL.json').read_bytes()) == '06a21194db443ea1d03165ee5b69e1a378ce5120bfee466c52ff9a9ff8644c35'
    gate_path=ROOT.parent/'empty-intent-fresh-ci-technical-r8/GATE.json'
    gate=gate_path.read_bytes()
    assert SHA(gate)=='11b8facb99e9957da95a24835eb0a86ef73ff97e360be03ee6705b0d2c29739e'
    admission=json.loads(gate)
    assert admission['verdict']=='ACCEPT_SOURCE_ONLY' and admission['sourceSealSHA256']=='06a21194db443ea1d03165ee5b69e1a378ce5120bfee466c52ff9a9ff8644c35'
    assert SHA((PARENT/'MANIFEST.json').read_bytes())=='22ebb5b4d584964ea81e622d73c1ffeefa47ac295093b6a9d64466a066aca20a'
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
    old_c=ROOT.parent/'opening-cue-build-source-r2'
    old_pins={'runner.py':'6710b2abb4e6684b4a4a8a7efad0838caa2d3ff528bf55e7ca736d7c44cdf624','rebuild-opening-cue-candidate.yml':'4ad3b12d32dccb501c81d366fdb63e14d8452a96dd3c7a8557cf56a386877eef','METADATA.json':'bbc8830505d51278a76f9913ff7d1564c6632fdc32e746b2b6e09417ecbddf17'}
    assert SHA((old_c/'SOURCE-SEAL.json').read_bytes())=='1082268d8489252d23c69b12dcb04d6157c29dce1bf09561d530001ff9474c43'
    inverse_pins={}
    for name,pin in old_pins.items():
        body=(old_c/name).read_bytes()
        assert SHA(body)==pin
        filename='INVERSE-'+name
        # Raw inverse was retained before shared derivation and must remain exact.
        assert (ROOT/filename).read_bytes()==body
        inverse_pins[name]={'sha256':pin,'bytes':len(body),'inverseBody':filename,'inverseEncoding':'raw-full-body'}
    (ROOT / 'ADAPTATION.json').write_text(json.dumps({'status': 'SOURCE_ONLY_SHARED_R8_ACCEPTED_C_ADAPTATION_REVIEW_PENDING',
        'predecessorDirectory': str(old_c), 'predecessorFiles': inverse_pins,
        'sharedMethod':{'directory':str(PARENT),'files':{name:{'sha256':SHA(body),'bytes':len(body)} for name,body in originals.items()},'sourceSealSHA256':'06a21194db443ea1d03165ee5b69e1a378ce5120bfee466c52ff9a9ff8644c35','manifestSHA256':'22ebb5b4d584964ea81e622d73c1ffeefa47ac295093b6a9d64466a066aca20a','independentGate':{'path':str(gate_path),'sha256':SHA(gate),'bytes':len(gate),'verdict':'ACCEPT_SOURCE_ONLY'},'rootSourceAcceptance':'CONFIRMED_BEFORE_DERIVATION'},
        'predecessorSourceSealSHA256': '1082268d8489252d23c69b12dcb04d6157c29dce1bf09561d530001ff9474c43',
        'predecessorManifestSHA256': 'd6644eedd1ffce8d7e897750c25fd9e2c310e07a4a5f19038f4ca5589f3491fb',
        'replacementsExceptMetadataLiteral': replacements,
        'metadataLiteralReplacement': 'Deterministic gzip of exact candidate METADATA.json; exact old C2 complete raw runner/workflow/metadata retained as inverse bodies.',
        'publicationCondition': 'R8 shared source gate accepted and Root confirmed before derivation. Root must accept exact C3 independent adaptation review before publication/run. Coherent7cc published812. Native audit allowance100→4096 explicitly authorized; memory/disk/log/time/lifecycle/input/output limits unchanged. No C output authority.'}, separators=(',', ':')) + '\n')

if __name__ == '__main__':
    main()
