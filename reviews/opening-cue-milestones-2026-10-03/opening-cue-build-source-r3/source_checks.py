"""Offline source, metadata and inverse checks. Never execute CI method phases."""
import ast
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess
import yaml

ROOT = Path(__file__).parent
SHA = lambda b: hashlib.sha256(b).hexdigest()

def digest(rows):
    return SHA(json.dumps(dict(sorted((x['path'], x['sha256']) for x in rows)), separators=(',', ':')).encode())

def node_source(tree, text, name):
    node = next(x for x in tree.body if isinstance(x, ast.FunctionDef) and x.name == name)
    return ast.get_source_segment(text, node)

def main():
    adaptation = json.loads((ROOT / 'ADAPTATION.json').read_bytes())
    old = {}
    for name, pin in adaptation['predecessorFiles'].items():
        stored = (ROOT / pin['inverseBody']).read_bytes()
        old[name] = stored if pin['inverseEncoding'] == 'raw-full-body' else gzip.decompress(stored)
        if pin['inverseEncoding'] == 'gzip-workflow-template-plus-exact-parent-runner':
            parent_runner = old['runner.py'].decode()
            old[name] = old[name].replace(b'{{EXACT_PARENT_RUNNER}}', parent_runner.replace('\n', '\n          ')[:-10].encode())
        assert len(old[name]) == pin['bytes'] and SHA(old[name]) == pin['sha256']
    shared = adaptation['sharedMethod']
    shared_bodies = {name: (Path(shared['directory']) / name).read_bytes() for name in shared['files']}
    assert all(SHA(shared_bodies[name]) == pin['sha256'] and len(shared_bodies[name]) == pin['bytes'] for name, pin in shared['files'].items())
    predecessor = shared_bodies['runner.py'].decode()
    source = (ROOT / 'runner.py').read_text()
    tree = ast.parse(source)
    compile(tree, 'runner.py', 'exec')
    prior_tree = ast.parse(predecessor)
    changed_functions = []
    for node in prior_tree.body:
        if isinstance(node, ast.FunctionDef):
            if node_source(tree, source, node.name) != ast.get_source_segment(predecessor, node):
                changed_functions.append(node.name)
    assert changed_functions == ['metadata', 'context', 'fetch_blob', 'acquire', 'assemble', 'membership', 'seal_output']
    # Every shared top-level function/class is exact, except fixed C identity/count adaptation.
    shared_exact = []
    for node in prior_tree.body:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name not in changed_functions:
            current = next(x for x in tree.body if type(x) is type(node) and x.name == node.name)
            assert ast.get_source_segment(source, current) == ast.get_source_segment(predecessor, node), node.name
            shared_exact.append(node.name)
    assert [x.name for x in tree.body if isinstance(x, (ast.FunctionDef, ast.ClassDef))] == [x.name for x in prior_tree.body if isinstance(x, (ast.FunctionDef, ast.ClassDef))]
    static = lambda t, text: [ast.get_source_segment(text, x) for x in t.body if isinstance(x, (ast.Import, ast.ImportFrom, ast.Assign)) and not (isinstance(x, ast.Assign) and any(isinstance(a, ast.Name) and a.id == 'META_LITERAL' for a in x.targets))]
    expected_static = [x.replace('/.github/workflows/rebuild-opening-baseline.yml@','/.github/workflows/rebuild-opening-cue-candidate.yml@').replace('b2f13179f14ccebecbc4452fa4e6b3cc88623dc629ff0009c1118401123ca46d','bbc8830505d51278a76f9913ff7d1564c6632fdc32e746b2b6e09417ecbddf17') for x in static(prior_tree, predecessor)]
    assert static(tree, source) == expected_static
    assert SHA((Path(shared['directory'])/'SOURCE-SEAL.json').read_bytes()) == shared['sourceSealSHA256']
    assert SHA((Path(shared['directory'])/'MANIFEST.json').read_bytes()) == shared['manifestSHA256']
    selected = [x for x in tree.body if isinstance(x, (ast.Import, ast.ImportFrom, ast.Assign)) or isinstance(x, ast.FunctionDef) and x.name in ('need', 'unique', 'load_json', 'metadata', 'safe_path')]
    env = {'__name__': 'offline_metadata_checks'}
    exec(compile(ast.Module(body=selected, type_ignores=[]), 'metadata-only', 'exec'), env)
    meta = env['metadata']()
    assert meta == json.loads((ROOT / 'METADATA.json').read_bytes())
    baseline = json.loads(gzip.decompress((ROOT / 'PARENT-SOURCE.json.gz').read_bytes()))
    a_meta = json.loads(old['METADATA.json'])
    c = {x['path']: x['sha256'] for x in meta['source']}
    b = {x['path']: x['sha256'] for x in baseline['source']}
    assert set(c) == set(b) and [x for x in c if c[x] != b[x]] == ['src/main.ts']
    assert digest(meta['source']) == '993aa3681596c2488d4d394744e5beda2778ffcba3e1649736612304d20b50c5'
    assert digest(baseline['source']) == '65b31b3f21e34a624bdac962e4919c7dc1791e502eb6cfdb1612103b8036fe9c'
    assert meta['support'] == a_meta['support'] and meta['scripts'] == a_meta['scripts'] and meta['tools'] == a_meta['tools']
    assert len(meta['source']) == 104 and len(meta['support']) == 30 and len(meta['blobPins']) == 57
    assert sum(x['path'].startswith('public/') for x in meta['source']) == 65
    assert meta['expectedOutputCount'] == 70
    assert [(x['path'], x['sha256']) for x in meta['source'] if x['path'] in meta['scripts']] == [(x['path'], x['sha256']) for x in a_meta['source'] if x['path'] in a_meta['scripts']]
    tests = [x['path'] for x in meta['support'] if re.fullmatch(r'tests/[^/]+\.test\.ts', x['path'])]
    assert len(tests) == 8
    blob_map = {x['sha256']: x for x in meta['blobPins']}
    assert len(blob_map) == 57
    assert meta['blobPins'][-3:] == a_meta['blobPins'][-3:]
    for pin in meta['source'] + meta['support']:
        if 'archive' in pin:
            assert pin['archive'] in ('8cdf', '4513', 'ce0f') and 'blob' not in pin
        else:
            assert pin['blob'] == pin['sha256'] and blob_map[pin['blob']]['bytes'] == pin['bytes']
    for pin in meta['source'] + meta['support']:
        path = ROOT.parent / 'starter-static-recovered-stage-r1' / pin['path']
        if pin in meta['support']:
            path = ROOT.parent / 'empty-intent-source-recovered-stage-r1' / pin['path']
        elif pin['path'] == 'src/main.ts':
            path = ROOT.parent / 'opening-cue-milestones-source-r1/src/main.ts'
        h = hashlib.sha256()
        size = 0
        with path.open('rb') as f:
            for chunk in iter(lambda: f.read(65536), b''):
                h.update(chunk)
                size += len(chunk)
        assert size == pin['bytes'] and h.hexdigest() == pin['sha256']
        if 'blob' in pin:
            body = path.read_bytes()
            assert hashlib.sha1(('blob ' + str(len(body)) + '\0').encode() + body).hexdigest() == blob_map[pin['blob']]['gitBlobSHA1']
    workflow_text = (ROOT / 'rebuild-opening-cue-candidate.yml').read_text()
    # Complete workflow comparison prevents unrelated guard/env/lifecycle changes.
    indent = lambda text: text.replace('\n','\n          ')[:-10]
    expected_workflow = shared_bodies['rebuild-opening-baseline.yml'].decode().replace(indent(predecessor), indent(source))
    changes = [(SHA(shared_bodies['runner.py']),SHA(source.encode())),(SHA(shared_bodies['METADATA.json']),SHA((ROOT/'METADATA.json').read_bytes())),
        ('Rebuild exact empty-intent opening baseline','Build exact opening cue candidate C'),('rebuild-opening-baseline.yml','rebuild-opening-cue-candidate.yml'),
        ('fresh-baseline:','fresh-cue-candidate:'),('empty-intent-fresh-baseline-','opening-cue-fresh-candidate-'),
        ('empty-intent-fresh-','opening-cue-fresh-'),('empty-intent-diagnostic-','opening-cue-diagnostic-'),
        ('Acquire exactly fifty canonical bodies and three original containers','Acquire fifty-four fixed direct bodies and three original containers'),
        ('runtime98 and support30','candidate source104 and original support30')]
    for before, after in changes:
        expected_workflow = expected_workflow.replace(before,after)
    assert expected_workflow == workflow_text
    workflow = yaml.safe_load(workflow_text)
    trigger = workflow.get('on', workflow.get(True))
    assert trigger == {'push': {'branches': ['codex/lanternbound-production'], 'paths': ['.github/workflows/rebuild-opening-cue-candidate.yml']}, 'workflow_dispatch': {}}
    assert workflow['permissions'] == {}
    job = workflow['jobs']['fresh-cue-candidate']
    assert job['runs-on'] == 'ubuntu-24.04' and job['timeout-minutes'] == 15 and job['permissions'] == {'contents': 'read'}
    prior_workflow = yaml.safe_load(shared_bodies['rebuild-opening-baseline.yml'])
    prior_steps = prior_workflow['jobs']['fresh-baseline']['steps']
    steps = job['steps']
    assert len(steps) == len(prior_steps)
    for step, prior_step in zip(steps, prior_steps):
        assert step.get('uses') == prior_step.get('uses') and step['timeout-minutes'] == prior_step['timeout-minutes']
        if 'run' in step:
            subprocess.run(['bash', '-n'], input=step['run'], text=True, check=True, capture_output=True)
            match = re.search(r"<<'PY'\n(.*?)\nPY(?:\n|$)", step['run'], re.S)
            if match:
                init_tree = ast.parse(match.group(1))
                compile(init_tree, 'workflow-heredoc', 'exec')
                assignments = [x for x in init_tree.body if isinstance(x, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'source' for t in x.targets)]
                if assignments:
                    assert len(assignments) == 1 and ast.literal_eval(assignments[0].value) == source
    assert SHA(source.encode()) in workflow_text and SHA((ROOT / 'METADATA.json').read_bytes()) in workflow_text
    assert 'runtime98' not in source and 'exact128' not in source and 'public59' not in source and 'expected64' not in source
    assert 'empty-intent-fresh-' not in source and 'empty-intent-fresh-' not in workflow_text
    assert '.github/workflows/rebuild-opening-baseline.yml' not in workflow_text
    # Frozen inverse restores each complete original file, including embedded method and metadata.
    result = {'status': 'PASS_SOURCE_ONLY', 'changedFunctions': changed_functions, 'sharedExactFunctionsAndClasses': shared_exact,
              'unchangedProvisioningAndSupervision': True, 'metadataLiteralExact': True,
              'candidateSource104Support30': True, 'candidateParentOnlyMainDelta': True,
              'localBytesChecked': 134, 'directBlobFramedSHA1Checked': True,
              'workflowPythonBashGrammar': True, 'workflowEmbeddedMethodExact': True,
              'fullInverseOriginalFilesVerified': True, 'originalTestsCount': len(tests),
              'networkInstallBuildTestBrowserExecuted': False}
    failure = json.loads((ROOT / 'ACTUAL-FAILURES.json').read_bytes())
    references = [failure['rootReceipt']] + [dict(path=k, **v) for k, v in failure['pins'].items()]
    for pin in references:
        h = hashlib.sha256(); size = 0
        with Path(pin['path']).open('rb') as stream:
            for chunk in iter(lambda: stream.read(65536), b''):
                h.update(chunk); size += len(chunk)
        assert size == pin['bytes'] and h.hexdigest() == pin['sha256'], pin['path']
    actual = json.loads(Path(next(k for k in failure['pins'] if k.endswith('/candidate/acquisition-progress.json'))).read_bytes())
    actual_rows = actual['verified']
    assert [(x['sha256'], x['gitBlobSHA1'], x['bytes']) for x in actual_rows] == [(x['sha256'], x['gitBlobSHA1'], x['bytes']) for x in meta['blobPins']]
    previous_dir = Path(adaptation['predecessorDirectory'])
    previous_seal_body = (previous_dir/'SOURCE-SEAL.json').read_bytes()
    assert SHA(previous_seal_body) == adaptation['predecessorSourceSealSHA256']
    previous_seal = json.loads(previous_seal_body)
    assert set(previous_seal['sealedFiles']) == {x.name for x in previous_dir.iterdir()} - {'SOURCE-SEAL.json'}
    for name, pin in previous_seal['sealedFiles'].items():
        body = (previous_dir/name).read_bytes()
        assert len(body) == pin['bytes'] and SHA(body) == pin['sha256'], name
    gate = adaptation['sharedMethod']['independentGate']
    assert SHA(Path(gate['path']).read_bytes()) == gate['sha256']
    assert meta == json.loads(old['METADATA.json'])
    result['exactFrozenOldCSourceFilesChecked'] = len(previous_seal['sealedFiles']) + 1
    result['unchangedFullCMetadata'] = True
    result['R8IndependentGateIdentityChecked'] = True
    result['allActualFailureReferencePinsChecked'] = len(references)
    result['actualCandidateAcquisition57MatchesUnchangedMetadata'] = True
    (ROOT / 'SOURCE-CHECKS.json').write_text(json.dumps(result, sort_keys=True, separators=(',', ':')) + '\n')
    print(json.dumps(result, sort_keys=True))

if __name__ == '__main__':
    main()
