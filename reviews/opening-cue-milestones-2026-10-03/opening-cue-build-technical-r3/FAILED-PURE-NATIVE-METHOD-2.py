"""Exact C helper with mocked inventory/hash/receipt sinks; no installed package or phase."""
import ast,errno,hashlib,json,os,pathlib,resource,signal,time
from unittest.mock import patch
P=pathlib.Path('/workspace/scratch/opening-cue-build-source-r3')
O=pathlib.Path(__file__).parent
start=time.monotonic();signal.alarm(20)
source=(P/'runner.py').read_text();tree=ast.parse(source)
names={'need','safe_path','native_inventory','bounded_path','supervisor_fault'}
selected=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names]
assert {n.name for n in selected}==names
env={'Path':pathlib.Path,'PurePosixPath':pathlib.PurePosixPath,'os':os,'hashlib':hashlib,'MIB':1048576,'re':__import__('re')}
exec(compile(ast.Module(body=selected,type_ignores=[]),'exact-isolated-C3-native-helper','exec'),env)
root=pathlib.Path('/uncreated-review-owned-fake-root');name='@typescript/typescript-linux-x64';package=root/'stage/node_modules'/name
results=[]
def case(label,count,want,fail_at=None,long_name=False):
    hashes=[];receipts=[]
    files=[(('x'*190)+str(i)+'.bin' if long_name else 'file-'+str(i)+'.bin') for i in range(count)]
    def hash_file(path,cap):
        hashes.append(path)
        if len(hashes)==fail_at:raise PermissionError(errno.EACCES,'mocked permission failure',str(path))
        assert cap==128*1048576
        return {'bytes':13,'sha256':'f'*64}
    def receipt(r,leaf,value,cap):
        assert r==root and cap==16384 and len((json.dumps(value,separators=(',',':'))+'\n').encode())<=cap
        receipts.append(json.loads(json.dumps(value)))
    env['hash_file']=hash_file;env['receipt']=receipt
    with patch.object(pathlib.Path,'is_dir',return_value=True),patch.object(pathlib.Path,'is_symlink',return_value=False),patch.object(os,'walk',return_value=iter([(str(package),[],files)])):
        failure=None
        try:rows=env['native_inventory'](root,package,name,6)
        except BaseException as e:failure=type(e).__name__;rows=None
    assert (failure is None)==want and len(receipts)==1
    observed=receipts[0]
    assert observed['fileCountObserved']==min(count,fail_at if fail_at else 4097)
    assert len(observed['firstBoundedNames'])==min(16,count)
    assert observed['hashedBytes']==13*(count if want else (fail_at-1 if fail_at else 4096))
    if want:assert observed['status']=='PASS_INVENTORY_BYTES_ONLY' and observed['completeInventory'] and len(rows)==count
    else:assert observed['status']=='FAILED' and not observed['completeInventory'] and observed['diagnosticOnlyNotAdmission']
    if count==4097:assert len(hashes)==4096
    if long_name:
        assert all(len(r['namePrefix'])==160 and not r['complete'] for r in observed['firstBoundedNames'])
        assert observed['firstBoundedNames'][0]['nameSHA256']==hashlib.sha256(files[0].encode()).hexdigest()
    results.append({'case':label,'pass':True,'requestedFiles':count,'hashCalls':len(hashes),'observedCount':observed['fileCountObserved'],'hashedBytes':observed['hashedBytes'],'status':observed['status'],'failureType':failure})
for count in [0,100,101,4096]:case('threshold '+str(count),count,True)
case('4097 refusal before hash',4097,False)
case('partial hash permission failure',3,False,fail_at=2)
case('bounded long name prefixes/full hashes',18,True,long_name=True)
# Fixed scope rejects before any enumeration, not another package's raised allowance.
for label,pkg,n in [('wrong package',package,'typescript'),('wrong path',root/'elsewhere',name)]:
    with patch.object(os,'walk',side_effect=AssertionError('enumeration must not occur')):
        try:env['native_inventory'](root,pkg,n,6)
        except ValueError:results.append({'case':label,'pass':True,'enumeration':False})
        else:raise AssertionError(label)
rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024;assert rss<64*1048576
result={'cases':results,'exactHelperCases':len(results),'runnerSHA256':hashlib.sha256(source.encode()).hexdigest(),'scope':'Pure mocked-source helper only. No main/phase, installed package file count, native execution, package extraction, network, npm/build/test/browser or old-path writes. Empty helper inventory can pass byte inventory; unchanged provisioning still requires ELF native bodies.','peakRSSBytes':rss,'elapsedSeconds':time.monotonic()-start}
with (O/'PURE-NATIVE-CHECKS.json').open('x') as f:json.dump(result,f,indent=2,sort_keys=True);f.write('\n')
signal.alarm(0);print(json.dumps({'cases':len(results),'peakRSSBytes':rss}))
