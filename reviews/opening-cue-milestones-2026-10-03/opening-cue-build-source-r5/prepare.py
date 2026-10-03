"""Authoring-only deterministic adaptation of the accepted frozen R10 shared method; raw inverse restores complete old C4 functional files."""
import base64
import gzip
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).parent
PARENT = ROOT.parent / 'empty-intent-fresh-ci-source-r10'
PINS = {'runner.py': '6ec835cf42c2735547ca10a748ea23cfd8a249c9e8cb3d810724d371bd53f57d',
        'rebuild-opening-baseline.yml': '912d510a087b2a7a5b175e3c4613c68b3ce8d011d0d4351be89be4b0932dee0c',
        'METADATA.json': '2b7de11520d1bfc4d61f52a5c454a01261d0127cddd2ce8164992651919d1d89'}
SHA = lambda b: hashlib.sha256(b).hexdigest()

def embedded(text):
    assert text.endswith('\n')
    return text.replace('\n', '\n          ')[:-10]

def main():
    originals = {name: (PARENT / name).read_bytes() for name in PINS}
    assert all(SHA(originals[name]) == pin for name, pin in PINS.items())
    assert SHA((PARENT / 'SOURCE-SEAL.json').read_bytes()) == '83188dc11eb1259cc961cf38e69cc7232040d08d6a7f209e5f817e599872f4bc'
    gate_path=ROOT.parent/'empty-intent-fresh-ci-technical-r10/GATE.json'
    gate=gate_path.read_bytes()
    assert SHA(gate)=='664f78f61f5669c4c2870ca629e228fa944087727384268b95aa66f68d671aee'
    admission=json.loads(gate)
    assert admission['verdict']=='ACCEPT_SOURCE_ONLY' and admission['sourceSeal']['sha256']=='83188dc11eb1259cc961cf38e69cc7232040d08d6a7f209e5f817e599872f4bc'
    assert SHA((PARENT/'MANIFEST.json').read_bytes())=='0878c30adad478a17db69d9599f9c9ecfe119b808c18533657b3d857253658f7'
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
    replace('len(m["source"]) == 98 and len(m["support"]) == 32 and len(m["blobPins"]) == 55', 'len(m["source"]) == 104 and len(m["support"]) == 32 and len(m["blobPins"]) == 59')
    replace('}) == 130, "fixed paths unique")', '}) == 136, "fixed paths unique")')
    replace('    return m\n', '''    hashes = dict(sorted((x["path"], x["sha256"]) for x in m["source"]))
    digest = hashlib.sha256(json.dumps(hashes, separators=(",", ":")).encode()).hexdigest()
    need(digest == m["sourceDigest"] == "993aa3681596c2488d4d394744e5beda2778ffcba3e1649736612304d20b50c5", "fixed C source104 digest")
    need(hashes["src/main.ts"] == "87a9bd7c2319522f77db7ea9e2edc306bb6124b019306dc220087f6b9b7762f4", "fixed C main")
    hashes["src/main.ts"] = "d1e71626b4c70679f4ba692b62ccb2aea0dbe5ce74e9a1426b6208fc26a45fe2"
    need(hashlib.sha256(json.dumps(hashes, separators=(",", ":")).encode()).hexdigest() == "65b31b3f21e34a624bdac962e4919c7dc1791e502eb6cfdb1612103b8036fe9c", "B to C only main changes")
    support = dict(sorted((x["path"], x["sha256"]) for x in m["support"]))
    need(hashlib.sha256(json.dumps(support, separators=(",", ":")).encode()).hexdigest() == "SUPPORT_DIGEST", "fixed original support30 plus two exact archived fixture bodies")
    need(sum(x["path"].startswith("public/") for x in m["source"]) == 65 and m["expectedOutputCount"] == 70, "fixed public65 output70")
    need(len({x["sha256"] for x in m["blobPins"]}) == 59 and [x.get("id") for x in m["blobPins"][-3:]] == ["8cdf", "4513", "ce0f"], "fixed unique blobs and archive suffix")
    return m
'''.replace('SUPPORT_DIGEST', support_digest))
    replace('"expected": 55, "complete": len(rows)==55', '"expected": 59, "complete": len(rows)==59')
    replace('need(len(rows)==55, "all fixed blobs")', 'need(len(rows)==59, "all fixed blobs")')
    replace('"sourceFiles":98', '"sourceFiles":104')
    replace('the 130 pinned inputs', 'the 136 pinned inputs')
    replace('"exact130 membership and bytes"', '"exact136 membership and bytes"')
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
    workflow = workflow.replace('Acquire exactly fifty canonical bodies and three original containers', 'Acquire fifty-six fixed direct bodies and three original containers')
    workflow = workflow.replace('runtime98 and support30', 'candidate source104 and original support32')
    (ROOT / 'rebuild-opening-cue-candidate.yml').write_text(workflow)
    old_c=ROOT.parent/'opening-cue-build-source-r4'
    old_pins={'runner.py':'c0345015a5f59a12e3f1397d3599090db773cdaa02fa57eadb6ea62eb358dfcd','rebuild-opening-cue-candidate.yml':'0f70389ddf37798c6869502f4d800d5caf214dd79e22eeff96334c6df5bdf495','METADATA.json':'bbc8830505d51278a76f9913ff7d1564c6632fdc32e746b2b6e09417ecbddf17'}
    assert SHA((old_c/'SOURCE-SEAL.json').read_bytes())=='8581a39c88c3ce906678fad6392e14ea080dfeb4a338064e7983ea65f26d560c'
    inverse_pins={}
    for name,pin in old_pins.items():
        body=(old_c/name).read_bytes()
        assert SHA(body)==pin
        filename='INVERSE-'+name
        # Raw inverse was retained before shared derivation and must remain exact.
        assert (ROOT/filename).read_bytes()==body
        inverse_pins[name]={'sha256':pin,'bytes':len(body),'inverseBody':filename,'inverseEncoding':'raw-full-body'}
    (ROOT / 'ADAPTATION.json').write_text(json.dumps({'status': 'SOURCE_ONLY_SHARED_R10_ACCEPTED_C_ADAPTATION_REVIEW_PENDING',
        'predecessorDirectory': str(old_c), 'predecessorFiles': inverse_pins,'candidateMetadataSHA256':SHA(meta_bytes),
        'sharedMethod':{'directory':str(PARENT),'files':{name:{'sha256':SHA(body),'bytes':len(body)} for name,body in originals.items()},'sourceSealSHA256':'83188dc11eb1259cc961cf38e69cc7232040d08d6a7f209e5f817e599872f4bc','manifestSHA256':'0878c30adad478a17db69d9599f9c9ecfe119b808c18533657b3d857253658f7','independentGate':{'path':str(gate_path),'sha256':SHA(gate),'bytes':len(gate),'verdict':'ACCEPT_SOURCE_ONLY'},'rootSourceAcceptance':'CONFIRMED_BEFORE_DERIVATION'},
        'predecessorSourceSealSHA256': '8581a39c88c3ce906678fad6392e14ea080dfeb4a338064e7983ea65f26d560c',
        'predecessorManifestSHA256': '77c648fad01572624a62378b3976c3c9f88287549c7b92b7d665b0bbd90e8aed',
        'replacementsExceptMetadataLiteral': replacements,
        'metadataLiteralReplacement': 'Deterministic gzip of exact candidate METADATA.json; exact old C4 complete raw runner/workflow/metadata retained as inverse bodies.',
        'publicationCondition': 'R10 shared source gate accepted and Root confirmed before derivation. Root must accept exact C5 independent adaptation review before publication/run. Coherent7cc published812. ONLY two original test fixtures added to original support30 and Gitpins, support32/stage136/blobs59. Runtime source104/main/art/rules/save/RNG/scripts8tests unchanged. Test768/installbuild384/native4096/disk/log/time/lifecycle/output limits unchanged. Full raw frozen C4 packet and3rawfunctional inverse retained/countedinclusive. No C output authority.'}, separators=(',', ':')) + '\n')

if __name__ == '__main__':
    main()
