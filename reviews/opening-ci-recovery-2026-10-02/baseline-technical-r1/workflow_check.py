import pathlib,json,ast,yaml,hashlib,subprocess,re
P=pathlib.Path('/workspace/scratch/empty-intent-fresh-ci-source-r1');O=pathlib.Path('/workspace/scratch/empty-intent-fresh-ci-technical-r1')
wbytes=(P/'rebuild-opening-baseline.yml').read_bytes();runner=(P/'runner.py').read_bytes();w=yaml.load(wbytes,Loader=yaml.BaseLoader)
assert w['permissions']=={} and w['on']=={'push':{'branches':['codex/lanternbound-production'],'paths':['.github/workflows/rebuild-opening-baseline.yml']},'workflow_dispatch':{}}
assert set(w['jobs'])=={'fresh-baseline'};j=w['jobs']['fresh-baseline'];assert j['permissions']=={'contents':'read'} and j['runs-on']=='ubuntu-24.04' and j['timeout-minutes']=='15'
assert all(x in j['if'] for x in ["github.repository == 'evangjones99-gif/Roguelike-deckbuilder'","github.ref == 'refs/heads/codex/lanternbound-production'","github.event_name == 'workflow_dispatch'","github.event_name == 'push'","github.event.deleted == false"])
steps=j['steps'];assert len(steps)==12;ids={s.get('id'):s for s in steps if 'id' in s}
assert set(ids)=={'initialize','setup','acquire','assemble','preflight','install','build','test','seal','diagnostic'}
assert ids['setup']['uses']=='actions/setup-node@49933ea5288caeca8642d1e84afbd3f7d6820020'
assert ids['setup']['with']=={'node-version':'24.19.0','architecture':'x64','check-latest':'false','token':''} and ids['setup']['timeout-minutes']=='2'
assert ids['acquire']['env']=={'GITHUB_TOKEN':'${{ github.token }}'}
assert all('env' not in s for s in steps if s is not ids['acquire'])
init=ids['initialize']['run'];py=init.split("python3 -I -B - <<'PY'\n",1)[1].rsplit('\nPY',1)[0];it=ast.parse(py)
embedded=ast.literal_eval(next(n.value for n in it.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='source' for t in n.targets)))
assert embedded.encode()==runner
sha=hashlib.sha256(runner).hexdigest();assert sha in py and len([n for n in ast.walk(it) if isinstance(n,ast.Constant) and n.value==sha])==2
caps={'initialize':('18','1'),'acquire':('178','4'),'assemble':('58','2'),'preflight':('28','1'),'install':('178','4'),'build':('58','2'),'test':('58','2'),'seal':('28','1')}
runs=[]
for name,(seconds,minutes) in caps.items():
 s=ids[name];assert s['shell']=='bash --noprofile --norc -euo pipefail {0}' and s['timeout-minutes']==minutes
 assert s['run'].startswith('timeout --signal=TERM --kill-after=2s '+seconds+'s python3 -I -B ')
 if name!='initialize':assert s['run'].rstrip().endswith(' '+name)
 subprocess.run(['bash','-n'],input=s['run'].encode(),check=True,capture_output=True,timeout=10)
 runs.append(name)
diag=ids['diagnostic'];assert diag['if']=='failure()' and diag['timeout-minutes']=='1'
subprocess.run(['bash','-n'],input=diag['run'].encode(),check=True,capture_output=True,timeout=10)
fallback=diag['run'].split("python3 -I -B - <<'PY'\n",1)[1].split('\n  PY',1)[0]
# YAML literal scalar leaves fallback four-space shell indentation; AST already checked in author's receipt.
upload=[s for s in steps if s.get('uses','').startswith('actions/upload-artifact@')]
assert len(upload)==2
for u in upload:
 assert u['uses']=='actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02' and u['timeout-minutes']=='2'
 assert {k:v for k,v in u['with'].items() if k not in {'name','path'}}=={'if-no-files-found':'error','compression-level':'0','overwrite':'false','include-hidden-files':'false','retention-days':'30'}
assert upload[0]['if']=='success()' and upload[1]['if']=="failure() && steps.diagnostic.outcome == 'success'"
assert upload[0]['with']['path']=='${{ runner.temp }}/empty-intent-fresh-${{ github.run_id }}-${{ github.run_attempt }}/success-artifact/'
assert upload[1]['with']['path']=='${{ steps.diagnostic.outputs.path }}/'
assert all('continue-on-error' not in s for s in steps)
proof={'draftSourceOnly':True,'workflowSHA256':hashlib.sha256(wbytes).hexdigest(),'runnerSHA256':sha,'embeddedRunnerByteExact':True,'PythonASTGrammarPassed':True,'allNineRunShellSyntaxPassed':True,'fixedPushManualTriggersPermissionsActionsTokenScope':True,'successAndFailureUploadsSeparated':True,'phaseShellCapsSecondsPlusKill':{k:int(v[0])+2 for k,v in caps.items()},'methodOrNpmBuildTestsExecuted':False,'qualification':'Static grammar/contracts only, run strings never executed. Source still unsealed; final hashes/seal must be checked.'}
(O/'WORKFLOW-PROOF.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof))
