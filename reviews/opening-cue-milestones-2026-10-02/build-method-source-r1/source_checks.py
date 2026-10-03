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
        old[name] = gzip.decompress((ROOT / pin['inverseBody']).read_bytes())
        if pin['inverseEncoding'] == 'gzip-workflow-template-plus-exact-parent-runner':
            parent_runner = old['runner.py'].decode()
            old[name] = old[name].replace(b'{{EXACT_PARENT_RUNNER}}', parent_runner.replace('\n', '\n          ')[:-10].encode())
        assert len(old[name]) == pin['bytes'] and SHA(old[name]) == pin['sha256']
    predecessor = old['runner.py'].decode()
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
    # Entire provisioning repair, command launch and resource/closure guards are reused exactly.
    for name in ['canonical_bin_map', 'observed_bin', 'provision_audit', 'child_env', 'run_phase', 'phase', 'preflight', 'diagnostic']:
        assert node_source(tree, source, name) == node_source(prior_tree, predecessor, name), name
    selected = [x for x in tree.body if isinstance(x, (ast.Import, ast.ImportFrom, ast.Assign)) or isinstance(x, ast.FunctionDef) and x.name in ('need', 'unique', 'load_json', 'metadata', 'safe_path')]
    env = {'__name__': 'offline_metadata_checks'}
    exec(compile(ast.Module(body=selected, type_ignores=[]), 'metadata-only', 'exec'), env)
    meta = env['metadata']()
    assert meta == json.loads((ROOT / 'METADATA.json').read_bytes())
    baseline = json.loads((ROOT / 'PARENT-SOURCE.json').read_bytes())
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
    workflow = yaml.safe_load(workflow_text)
    trigger = workflow.get('on', workflow.get(True))
    assert trigger == {'push': {'branches': ['codex/lanternbound-production'], 'paths': ['.github/workflows/rebuild-opening-cue-candidate.yml']}, 'workflow_dispatch': {}}
    assert workflow['permissions'] == {}
    job = workflow['jobs']['fresh-cue-candidate']
    assert job['runs-on'] == 'ubuntu-24.04' and job['timeout-minutes'] == 15 and job['permissions'] == {'contents': 'read'}
    prior_workflow = yaml.safe_load(old['rebuild-opening-baseline.yml'])
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
    result = {'status': 'PASS_SOURCE_ONLY', 'changedFunctions': changed_functions,
              'unchangedProvisioningAndSupervision': True, 'metadataLiteralExact': True,
              'candidateSource104Support30': True, 'candidateParentOnlyMainDelta': True,
              'localBytesChecked': 134, 'directBlobFramedSHA1Checked': True,
              'workflowPythonBashGrammar': True, 'workflowEmbeddedMethodExact': True,
              'fullInverseOriginalFilesVerified': True, 'originalTestsCount': len(tests),
              'networkInstallBuildTestBrowserExecuted': False}
    (ROOT / 'SOURCE-CHECKS.json').write_text(json.dumps(result, sort_keys=True, separators=(',', ':')) + '\n')
    print(json.dumps(result, sort_keys=True))

if __name__ == '__main__':
    main()
