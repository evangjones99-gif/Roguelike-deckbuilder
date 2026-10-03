"""Independent candidate adaptation SOURCE review; never execute author prepare/check/main/phases."""
import ast
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import resource
import stat
import subprocess
import time
import zlib
import yaml

OUT = Path(__file__).parent
AUTHOR = Path('/workspace/scratch/opening-cue-build-source-r1')
BASE = Path('/workspace/scratch/empty-intent-fresh-ci-source-r4')
SROOT = Path('/workspace/scratch/starter-static-recovered-stage-r1')
SUPPORT = Path('/workspace/scratch/empty-intent-source-recovered-stage-r1')
CMAIN = Path('/workspace/scratch/opening-cue-milestones-source-r1/src/main.ts')
MAP = Path('/workspace/scratch/starter-runtime-recovery-map-source-r2/MAP.json')
CAP = 128*1024
sha = lambda b: hashlib.sha256(b).hexdigest()
START = time.monotonic()

def pins(directory):
    return {p.relative_to(directory).as_posix(): [sha(p.read_bytes()), p.stat().st_size] for p in sorted(directory.rglob('*')) if p.is_file()}

def file_hash(path, git=False):
    s=path.lstat()
    assert stat.S_ISREG(s.st_mode) and s.st_nlink==1 and not path.is_symlink()
    h=hashlib.sha256()
    g=hashlib.sha1(('blob '+str(s.st_size)+'\0').encode())
    size=0
    with path.open('rb') as f:
        for b in iter(lambda:f.read(65536),b''):
            size+=len(b);h.update(b);g.update(b)
    assert size==s.st_size
    return dict(bytes=size,sha256=h.hexdigest(),**({'gitBlobSHA1':g.hexdigest()} if git else {}))

def inflate(path, limit=131072):
    b=path.read_bytes();d=zlib.decompressobj(16+zlib.MAX_WBITS)
    result=d.decompress(b,limit+1)
    assert len(result)<=limit and d.eof and not d.unused_data and not d.unconsumed_tail
    return result

def compact_digest(rows):
    return sha(json.dumps(dict(sorted((x['path'],x['sha256']) for x in rows)),separators=(',',':')).encode())

def function(text,name):
    node=next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef) and n.name==name)
    return ast.get_source_segment(text,node)

before=pins(AUTHOR);base_before=pins(BASE)
seal=json.loads((AUTHOR/'SOURCE-SEAL.json').read_bytes());manifest=json.loads((AUTHOR/'MANIFEST.json').read_bytes())
assert sha((AUTHOR/'SOURCE-SEAL.json').read_bytes())=='b2f095b052d6ebad7d28db5c7556c072956fb354d2b8890d72df4d0c00c5c0b8'
assert sha((AUTHOR/'MANIFEST.json').read_bytes())==seal['manifestSHA256']=='b38acd6f9cf8930459981e69b28c215395ae53b42f7cda4f3cc9d4b216c395a8'
assert set(seal['sealedFiles'])==set(before)-{'SOURCE-SEAL.json'}
for name,pin in seal['sealedFiles'].items():
    assert before[name]==[pin['sha256'],pin['bytes']]
assert sum(x[1] for x in before.values())<=manifest['authoringSourceLimitBytes']==262144
for name,pin in manifest['filesExcludingManifestAndSeal'].items():
    assert before[name]==[pin['sha256'],pin['bytes']]
adapt=json.loads((AUTHOR/'ADAPTATION.json').read_bytes())
assert sha((BASE/'SOURCE-SEAL.json').read_bytes())==adapt['predecessorSourceSealSHA256']=='51f4e42e9ca6d846ad6edd93cb0445936becdf07a7230204c9b9e4ebb71a1080'
assert sha((BASE/'MANIFEST.json').read_bytes())==adapt['predecessorManifestSHA256']
original={}
for name,pin in adapt['predecessorFiles'].items():
    b=inflate(AUTHOR/pin['inverseBody'])
    if pin['inverseEncoding']=='gzip-workflow-template-plus-exact-parent-runner':
        assert b.count(b'{{EXACT_PARENT_RUNNER}}')==1
        embedded=original['runner.py'].decode().replace('\n','\n          ')[:-10].encode()
        b=b.replace(b'{{EXACT_PARENT_RUNNER}}',embedded)
    assert len(b)==pin['bytes'] and sha(b)==pin['sha256'] and b==(BASE/name).read_bytes()
    original[name]=b
meta=json.loads((AUTHOR/'METADATA.json').read_bytes());oldmeta=json.loads(original['METADATA.json'])
parent=json.loads((AUTHOR/'PARENT-SOURCE.json').read_bytes());evidence=json.loads((AUTHOR/'INPUT-EVIDENCE.json').read_bytes())
assert compact_digest(meta['source'])==meta['sourceDigest']=='993aa3681596c2488d4d394744e5beda2778ffcba3e1649736612304d20b50c5'
assert compact_digest(parent['source'])=='65b31b3f21e34a624bdac962e4919c7dc1791e502eb6cfdb1612103b8036fe9c'
assert len(meta['source'])==104 and len(meta['support'])==30 and len(meta['blobPins'])==57
assert meta['support']==oldmeta['support'] and meta['scripts']==oldmeta['scripts'] and meta['tools']==oldmeta['tools']
assert meta['expectedNodeVersion']==oldmeta['expectedNodeVersion']=='v24.19.0'
assert meta['expectedOutputCount']==70 and len([x for x in meta['source'] if x['path'].startswith('public/')])==65
bmap={x['path']:x for x in parent['source']};cmap={x['path']:x for x in meta['source']}
assert set(bmap)==set(cmap) and [p for p in cmap if cmap[p]['sha256']!=bmap[p]['sha256']]==['src/main.ts']
stage_manifest=Path('/workspace/scratch/starter-static-recovered-authority-r1/STAGE-MANIFEST.json')
for path,pin in evidence['authorityPins'].items():
    assert sha(Path(path).read_bytes())==pin
authority=json.loads(stage_manifest.read_bytes())
sourcefiles={p:pin for p,pin in authority['files'].items() if not p.startswith('dist/')}
assert set(sourcefiles)==set(bmap)
assert all(sourcefiles[p]['sha256']==pin['sha256'] and sourcefiles[p]['bytes']==pin['bytes'] for p,pin in bmap.items())
assert authority['sourceDigest']==compact_digest(parent['source']) and authority['outputCount']==70
inputs=[]
for row in meta['source']+meta['support']:
    path=SUPPORT/row['path'] if row in meta['support'] else CMAIN if row['path']=='src/main.ts' else SROOT/row['path']
    got=file_hash(path,git='blob' in row)
    assert got['bytes']==row['bytes'] and got['sha256']==row['sha256']
    inputs.append(dict(path=row['path'],local=str(path),**got))
original_body=file_hash(SROOT/'src/main.ts')
assert original_body['sha256']==bmap['src/main.ts']['sha256'] and original_body['bytes']==bmap['src/main.ts']['bytes']
pbins={x['sha256']:x for x in oldmeta['blobPins']};cbins={x['sha256']:x for x in meta['blobPins']}
assert len(cbins)==57 and set(pbins).issubset(cbins)
assert all(cbins[s]==p for s,p in pbins.items()) and meta['blobPins'][-3:]==oldmeta['blobPins'][-3:]
paths_by_body={x['sha256']:x['local'] for x in inputs if 'gitBlobSHA1' in x}
archive_paths={
    '8cdf':Path('/workspace/scratch/archive8cdf-acquired-r1/evidence-8cdf546a8429e949fe88611d781aca341566f473135fbcbe44b5373beabd7aa8.tar.gz'),
    '4513':Path('/workspace/scratch/opening-runtime-bytes-acquired-r2/containers/bodies/evidence-451347c174a3fe78e5f7b6ef22736b7cfbbd33b39fd04ea20556730bb3b15a8b.tar.gz'),
    'ce0f':Path('/workspace/scratch/opening-runtime-bytes-acquired-r2/containers/bodies/evidence-ce0f8f40bcf0f0b22e5e4d93eef3d4660662826e617900aba09ac208c148dc13.tar.gz')}
blob_rows=[]
for pin in meta['blobPins']:
    if 'id' in pin:
        path=archive_paths[pin['id']]
    elif pin['sha256'] in paths_by_body:
        path=Path(paths_by_body[pin['sha256']])
    else:
        assert pin['gitPath'].startswith('public/')
        path=Path('/workspace/scratch/opening-runtime-bytes-acquired-r2/canonical/bodies')/pin['gitPath'][7:]
    got=file_hash(path,True)
    assert got=={k:pin[k] for k in ('bytes','sha256','gitBlobSHA1')}
    blob_rows.append(dict(gitPath=pin['gitPath'],local=str(path),**got))
recovery=json.loads(MAP.read_bytes());oldsource={x['path']:x for x in oldmeta['source']}
new_archive=[]
for row in meta['source']:
    if 'archive' not in row:continue
    if row['path'] in oldsource and row==oldsource[row['path']]:continue
    witness=next(x for x in recovery['nativeArchiveTransferPins'] if 'public/'+x['path']==row['path'])
    assert row['archive']==witness['archive']=='8cdf' and row['sha256']==witness['sha256'] and row['bytes']==witness['bytes']
    new_archive.append(row)
assert len(new_archive)==6
headers=json.loads(Path('/workspace/scratch/archive8cdf-acquired-r1/TAR-HEADERS.json').read_bytes())
header_map={x['name']:x['bytes'] for x in headers['rows']}
assert all(header_map['blobs/'+x['sha256']]==x['bytes'] for x in new_archive)
package=json.loads((SROOT/'package.json').read_bytes())
assert package['scripts']['build']=='node scripts/build.mjs' and package['scripts']['test']=='tsx --test tests/*.test.ts'
assert not any(x in package['scripts'] for x in ('prebuild','postbuild','pretest','posttest'))
tests=sorted(x['path'] for x in meta['support'] if re.fullmatch(r'tests/[^/]+\.test\.ts',x['path']))
assert len(tests)==8
source=(AUTHOR/'runner.py').read_text();base_source=original['runner.py'].decode();tree=ast.parse(source);compile(tree,'candidate-runner','exec')
base_tree=ast.parse(base_source)
changed=[n.name for n in base_tree.body if isinstance(n,ast.FunctionDef) and function(source,n.name)!=ast.get_source_segment(base_source,n)]
assert changed==['metadata','context','fetch_blob','acquire','assemble','membership','seal_output']
unchanged=['canonical_bin_map','observed_bin','provision_audit','child_env','run_phase','phase','preflight','diagnostic','proc_snapshot','effective_available','cgroup_observation','member_header']
assert all(function(source,n)==function(base_source,n) for n in unchanged)
assert {n.name for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}=={n.name for n in base_tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
replayed=base_source
literal=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='META_LITERAL' for t in n.targets))
replayed=re.sub(r'^META_LITERAL = ".*"$', 'META_LITERAL = '+json.dumps(literal),replayed,count=1,flags=re.M)
for change in adapt['replacementsExceptMetadataLiteral']:
    assert replayed.count(change['before'])==change['count']
    replayed=replayed.replace(change['before'],change['after'])
assert replayed==source
selected=[n for n in tree.body if isinstance(n,(ast.Import,ast.ImportFrom,ast.Assign)) or isinstance(n,ast.FunctionDef) and n.name in ('need','unique','load_json','metadata','safe_path')]
env={'__name__':'independent_candidate_metadata_only'}
exec(compile(ast.Module(body=selected,type_ignores=[]),'metadata-only','exec'),env)
assert env['metadata']()==meta
workflow_text=(AUTHOR/'rebuild-opening-cue-candidate.yml').read_text();workflow=yaml.safe_load(workflow_text);prior=yaml.safe_load(original['rebuild-opening-baseline.yml'])
assert workflow.get('on',workflow.get(True))=={'push':{'branches':['codex/lanternbound-production'],'paths':['.github/workflows/rebuild-opening-cue-candidate.yml']},'workflow_dispatch':{}}
assert workflow['permissions']=={}
job=workflow['jobs']['fresh-cue-candidate'];pjob=prior['jobs']['fresh-baseline']
assert job['if']==pjob['if'] and job['permissions']=={'contents':'read'} and job['runs-on']=='ubuntu-24.04' and job['timeout-minutes']==15
assert len(job['steps'])==len(pjob['steps'])
grammar=[]
for step,old_step in zip(job['steps'],pjob['steps']):
    assert step.get('uses')==old_step.get('uses') and step['timeout-minutes']==old_step['timeout-minutes'] and step.get('env')==old_step.get('env')
    if 'uses' in step:
        for key in set(old_step['with'])-{'name','path'}:
            assert step['with'][key]==old_step['with'][key]
    if 'run' not in step:continue
    proc=subprocess.run(['bash','-n'],input=step['run'],text=True,capture_output=True,timeout=5)
    assert proc.returncode==0,proc.stderr
    grammar.append(step['id'])
    lines=step['run'].splitlines()
    for i,line in enumerate(lines):
        if "<<'PY'" not in line:continue
        end=next(k for k in range(i+1,len(lines)) if lines[k]=='PY');code='\n'.join(lines[i+1:end])+'\n';itree=ast.parse(code);compile(itree,'candidate-'+step['id'],'exec')
        assignments=[n for n in itree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='source' for t in n.targets)]
        if assignments:assert len(assignments)==1 and ast.literal_eval(assignments[0].value)==source
        if step['id']=='initialize':
            assert sha(source.encode()) in code and sha((AUTHOR/'METADATA.json').read_bytes()) in code
assert sum('GITHUB_TOKEN' in x.get('env',{}) for x in job['steps'])==1
assert next(x for x in job['steps'] if 'GITHUB_TOKEN' in x.get('env',{}))['id']=='acquire'
assert '.github/workflows/rebuild-opening-baseline.yml' not in workflow_text and 'empty-intent-fresh-' not in workflow_text
# Independently replay every allowed whole-workflow edit; outer shell timeouts/argv stay exact.
expected_workflow=original['rebuild-opening-baseline.yml'].decode()
old_embedded=base_source.replace('\n','\n          ')[:-10]
new_embedded=source.replace('\n','\n          ')[:-10]
assert expected_workflow.count(old_embedded)==1
expected_workflow=expected_workflow.replace(old_embedded,new_embedded)
expected_workflow=expected_workflow.replace(sha(original['runner.py']),sha(source.encode())).replace(sha(original['METADATA.json']),sha((AUTHOR/'METADATA.json').read_bytes()))
for old,new in [
    ('Rebuild exact empty-intent opening baseline','Build exact opening cue candidate C'),
    ('rebuild-opening-baseline.yml','rebuild-opening-cue-candidate.yml'),
    ('fresh-baseline:','fresh-cue-candidate:'),
    ('empty-intent-fresh-baseline-','opening-cue-fresh-candidate-'),
    ('empty-intent-fresh-','opening-cue-fresh-'),
    ('empty-intent-diagnostic-','opening-cue-diagnostic-'),
    ('Acquire exactly fifty canonical bodies and three original containers','Acquire fifty-four fixed direct bodies and three original containers'),
    ('runtime98 and support30','candidate source104 and original support30')]:
    assert old in expected_workflow
    expected_workflow=expected_workflow.replace(old,new)
assert expected_workflow==workflow_text
globals_before={n.targets[0].id:ast.get_source_segment(base_source,n) for n in base_tree.body if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name)}
globals_after={n.targets[0].id:ast.get_source_segment(source,n) for n in tree.body if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name)}
assert {k for k in globals_before if globals_before[k]!=globals_after[k]}=={'META_SHA','META_LITERAL','WORKFLOW'}
assert before==pins(AUTHOR) and base_before==pins(BASE)
assert time.monotonic()-START<45
conservative=(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss+resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss)*1024
assert conservative<=64*1048576
proof={'verdict':'PASS_ADAPTATION_SOURCE_ONLY','authorSealSHA256':sha((AUTHOR/'SOURCE-SEAL.json').read_bytes()),'authorManifestSHA256':seal['manifestSHA256'],'authorFamilyBytes':sum(x[1] for x in before.values()),'authorCapBytes':262144,
       'sourceDigest':meta['sourceDigest'],'sourceCount':104,'supportCount':30,'publicCount':65,'expectedNewOutputCount':70,'mainOnlyDeltaAgainstB':True,'all134LocalInputBodies':inputs,'all57FixedBlobBodies':blob_rows,
       'newNativeArchiveWitnesses':new_archive,'originalBuildAnd8TestsUnchanged':tests,'unchangedR4Functions':unchanged,'changedAdaptationFunctions':changed,'allCompleteCompressedParentBodiesRestored':True,'deterministicForwardAdaptationExact':True,'wholeWorkflowForwardAllowlistExact':True,'grammarSteps':grammar,
       'ordinaryConservativePeakBytes':conservative,'ordinaryWorkBytes':64*1048576,'reserveBytes':512*1048576,'finiteReviewSeconds':45,'noSourceWritesOrMainNetworkInstallBuildTestBrowserExecution':True,
       'baseR4Approval':'Separate independent evidence_audit gate required; comparison here is not base approval','coherentTreePublication':'Root must commit exact7cc111 review path before CI; blob API pin alone is not tree-path publication','actualCBuildDefaultArtGameplayFunAccepted':False}
with (OUT/'CHECKS.json').open('x') as f:json.dump(proof,f,separators=(',',':'));f.write('\n')
print(json.dumps({'status':proof['verdict'],'inputs':134,'fixedBodies':57,'changedFunctions':changed,'peakBytes':conservative,'authorFamilyBytes':proof['authorFamilyBytes']}))
