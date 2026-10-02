import pathlib,json,hashlib,ast,re,resource,signal,subprocess,shutil
P=pathlib.Path('/workspace/scratch/empty-intent-fresh-ci-source-r4');O=pathlib.Path('/workspace/scratch/empty-intent-fresh-ci-technical-r4')
signal.alarm(25)
# Run only retained pure synthetic helpers; delete top-level receipt writers before compilation.
pure=[]
for name,resultvar in [('source_checks.py','receipt'),('shared_shim_checks.py','result')]:
    t=ast.parse((P/name).read_bytes())
    kept=[]
    for n in t.body:
        if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='ROOT' for x in n.targets):
            n.value=ast.Call(func=ast.Name(id='Path',ctx=ast.Load()),args=[ast.Constant(str(P))],keywords=[]);ast.fix_missing_locations(n)
        if isinstance(n,ast.With) and any(isinstance(item.context_expr,ast.Call) and isinstance(item.context_expr.func,ast.Attribute) and item.context_expr.func.attr=='open' for item in n.items):continue
        if isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Name) and n.value.func.id=='print':continue
        kept.append(n)
    ns={'__name__':'review_pure_synthetic','__file__':str(O/name)}
    run=subprocess.run
    def finite_run(*args,**kwargs):
        kwargs['timeout']=min(kwargs.get('timeout',10),10)
        return run(*args,**kwargs)
    subprocess.run=finite_run
    try:exec(compile(ast.Module(body=kept,type_ignores=[]),name+'_pure_only','exec'),ns)
    finally:subprocess.run=run
    val=ns[resultvar]
    pure.append(dict(name=name,methodSHA256=val['methodSHA256'],caseCount=val.get('caseCount',len(val['cases'])),cases=val['cases'],sourceReceiptWriterRemoved=True))
    if name=='shared_shim_checks.py':audit_ns=ns
# Independent extra probes: exact helpers from candidate, synthetic filesystem only.
extra=[]
for key in ['node','npm','tsc','vite','tsx']:
    audit_ns['actual_bin_overrides'].clear()
    audit_ns['actual_bin_overrides']['vite' if key!='vite' else 'tsx']={'vite':'bin/vite.js',key:'bin/shadow'} if key!='vite' else {'tsx':'dist/cli.mjs','vite':'bin/shadow'}
    prev=len(audit_ns['receipts'])
    try:audit_ns['env']['provision_audit'](audit_ns['FakePath']('/owned'),{'tools':audit_ns['pins'],'expectedNodeVersion':'v24.19.0'})
    except ValueError as e:assert str(e)=='unused bin command conflicts with fixed execution scope'
    else:raise AssertionError('shadow admission '+key)
    assert len(audit_ns['receipts'])>prev and audit_ns['receipts'][-1]['diagnosticOnlyNotAdmission']
    extra.append('reject_extra_'+key+'_shadow_before_admission')
cn=audit_ns['env']['canonical_bin_map']
for value in [{'':'bin/vite.js'},{'bad/name':'bin/vite.js'},{'vite':'bin//vite.js'},{'vite':'./'},{'vite':'C:\\outside'},{'vite':'bin/./vite.js'},{'vite':'bin/vite.js','unused':'/outside'}]:
    try:cn(value,'vite')
    except ValueError:pass
    else:raise AssertionError('unsafe mapping passed')
    extra.append('reject_'+repr(value))
assert cn({'vite':'././bin/vite.js'},'vite')=={'vite':'bin/vite.js'}
extra.append('leading_dot_components_only_normalize')
ov=audit_ns['env']['observed_bin']({'unused':'x'*20000})
assert ov['complete'] is False and ov['serializedBytes']>8192 and len(ov['prefix'].encode())<=1024 and re.fullmatch('[0-9a-f]{64}',ov['serializedSHA256'])
extra.append('oversized_diagnostic_retains_qualified_hash_prefix')

rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024;child=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss*1024
assert rss+child<=64*1048576
out={'pure':pure,'extra':extra,'resource':{'selfPeakRSS':rss,'grammarChildPeakRSS':child,'conservativePeakSum':rss+child,'workBytes':64*1048576,'reserveBytes':512*1048576,'finiteSeconds':25},'noMainNetworkInstallBuildExecuted':True}
(O/'PURE-CHECKS.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'status':'PASS','cases':sum(x['caseCount'] for x in pure)+len(extra),'resource':out['resource']}))
