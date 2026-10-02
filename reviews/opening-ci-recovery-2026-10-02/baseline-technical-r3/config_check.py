import pathlib,ast,json,hashlib,types,stat,os
P=pathlib.Path('/workspace/scratch/empty-intent-fresh-ci-source-r3');O=pathlib.Path('/workspace/scratch/empty-intent-fresh-ci-technical-r3')
source=(P/'runner.py').read_bytes();tree=ast.parse(source);nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in {'need','hash_file','verify_pin','child_env'}]
env={'os':types.SimpleNamespace(environ={'PATH':'/selected/bin','HOME':'/owned-home','GITHUB_TOKEN':'secret','ACTIONS_RUNTIME_TOKEN':'secret','NODE_AUTH_TOKEN':'secret','npm_config_userconfig':'/outside/config','NPM_CONFIG_GLOBALCONFIG':'/outside/global','NODE_OPTIONS':'--require outside'}),'hashlib':hashlib,'stat':stat,'FILE_CAP':9*1048576}
exec(compile(ast.Module(body=nodes,type_ignores=[]),'offline_exact_config_environment_functions','exec'),env)
root=P/'npm-config-repro';e=env['child_env'](root);assert e['npm_config_userconfig']==str(root/'control/npm-user.npmrc') and e['npm_config_globalconfig']==str(root/'control/npm-global.npmrc') and e['npm_config_userconfig']!=e['npm_config_globalconfig']
assert not any(k in e for k in ['GITHUB_TOKEN','ACTIONS_RUNTIME_TOKEN','NODE_AUTH_TOKEN','NPM_CONFIG_GLOBALCONFIG']) and e['NODE_OPTIONS']=='--max-old-space-size=256'
bad=O/'config-fixtures/bad/control';bad.mkdir(parents=True)
with (bad/'npm-user.npmrc').open('xb') as f:f.write(b'x')
with (bad/'npm-global.npmrc').open('xb') as f:pass
try:env['child_env'](bad.parent);raise AssertionError('Nonempty config admitted')
except ValueError as x:assert str(x)=='body identity'
try:env['child_env'](O/'config-fixtures/missing');raise AssertionError('Absent configs admitted')
except FileNotFoundError:pass
receipt=json.loads((P/'NPM-CONFIG-REPRO.json').read_bytes());logs=[]
for r in receipt['cases']:
 p=P/'npm-config-repro/proof'/(r['case']+'.log');b=p.read_bytes();assert hashlib.sha256(b).hexdigest()==r['stdoutSHA256'] and len(b)==r['rawBytes'];assert r['sampledAggregatePeakRSS']<=64*1048576 and r['closedDirectChild'] is True and r['elapsedSeconds']<10
 logs.append({'case':r['case'],'exit':r['exit'],'bytes':len(b),'sha256':r['stdoutSHA256']})
assert logs[0]['exit']==1 and logs[0]['bytes']==117 and logs[0]['sha256']=='250e369d730a46c4d41df37449a5c58c169b4b1d2ab546951a8bed0285805a95' and logs[1]['exit']==0
assert (P/'npm-config-repro/proof/fixed-owned-distinct.log').read_bytes()==b'11.9.0\n'
proof={'sourceOnly':True,'runnerSHA256':hashlib.sha256(source).hexdigest(),'cases':['exact_owned_distinct_empty_config_paths','inherited_credentials_configs_options_excluded','nonempty_config_refused','missing_config_refused'],'productionMainNetworkProcessOrNpmExecutedByReviewer':False,'authorizedAuthorOfflineNpmVersionReceiptLogsVerified':logs,'localNpmVersion':'11.9.0','actualR3CIResultAccepted':False,'qualification':'Exact selected configuration/hash/environment functions only. Reads frozen author empty-config fixtures without writes; reviewer bad/missing fixtures remain new owned files. Author local npm version reproduction is separate evidence and does not establish future pinned-CI npm/install/build success.'}
(O/'CONFIG-PROOF.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof))
