import pathlib,json,hashlib,difflib,subprocess,resource,os,signal,shutil,time,zipfile
ROOT=pathlib.Path('/workspace/scratch/windows-opening-smoke-technical-r1')
SRC=pathlib.Path('/workspace/scratch/windows-opening-smoke-source-r1')
OLD=pathlib.Path('/workspace/scratch/windows-checkout-actual-evidence-r1')
ACT=pathlib.Path('/workspace/scratch/windows-opening-smoke-actual-evidence-r1')
signal.alarm(30)
def sha(b): return hashlib.sha256(b).hexdigest()
def pin(p):
    b=p.read_bytes()
    return dict(bytes=len(b),sha256=sha(b))
def stream_pin(p):
    h=hashlib.sha256();n=0
    with p.open('rb') as f:
        for b in iter(lambda:f.read(65536),b''):h.update(b);n+=len(b)
    return dict(bytes=n,sha256=h.hexdigest())
host=int(next(l.split()[1] for l in pathlib.Path('/proc/meminfo').read_text().splitlines() if l.startswith('MemAvailable:')))*1024
cg=pathlib.Path('/sys/fs/cgroup')
mx=(cg/'memory.max').read_text().strip();cur=int((cg/'memory.current').read_text())
finite=host if mx=='max' else min(host,int(mx)-cur)
admission=dict(hostAvailable=host,cgroupMax=mx,cgroupCurrent=cur,minimumHeadroom=finite,required=64*1024**2+512*1024**2,freeDisk=shutil.disk_usage(ROOT).free)
assert finite>=admission['required'] and admission['freeDisk']>=24*1024**2
before={p.name:pin(p) for p in SRC.iterdir() if p.is_file()}
manifest=json.loads((SRC/'MANIFEST.json').read_text())
assert sum(v['bytes'] for v in before.values())==98919<=131072
assert before['SOURCE-GATE.json']['sha256']=='f86651361d2a4f0e036a3be09953ac30b27371e8add4c378764f86de9c9fd0ad'
assert before['MANIFEST.json']['sha256']=='5a9f80abfafec56f366b59afa285949e76c325783dbb65c040b4f2537c23fa7b'
assert manifest['files']=={k:v for k,v in before.items() if k not in ('SOURCE-GATE.json','MANIFEST.json')}
original=(SRC/'windows-smoke.before.mjs').read_text(); proposed=(SRC/'windows-smoke.proposed.mjs').read_text()
ledger=json.loads((SRC/'CHANGE-LEDGER.json').read_text())
forward=original
for c in ledger['changes']:
    assert forward.count(c['before'])==1
    forward=forward.replace(c['before'],c['after'])
assert forward==proposed
reverse=proposed
for c in reversed(ledger['changes']):
    assert reverse.count(c['after'])==1
    reverse=reverse.replace(c['after'],c['before'])
assert reverse==original
patch=''.join(difflib.unified_diff(original.splitlines(True),proposed.splitlines(True),fromfile='a/scripts/windows-smoke.mjs',tofile='b/scripts/windows-smoke.mjs'))
assert patch==(SRC/'windows-smoke.patch').read_text()
gitpins={}
for name in ['windows-smoke.before.mjs','hunt-entry.265eb047.ts','hunt-entry.265eb047.css']:
    b=(SRC/name).read_bytes();h=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
    gitpins[name]=h
assert gitpins==dict(zip(['windows-smoke.before.mjs','hunt-entry.265eb047.ts','hunt-entry.265eb047.css'],['f4b53e0b942305aba8b8e8e4e3b7445d33f7377c','f3cdeefb038b71491bff984f464305dbdb425fbe','3e45d3f4f218a10f3eee9aa117a4e6223b5dbe07']))
grammar=[]
for name in ['windows-smoke.before.mjs','windows-smoke.proposed.mjs']:
    t=time.monotonic();r=subprocess.run(['node','--check',str(SRC/name)],capture_output=True,timeout=10)
    grammar.append(dict(file=name,argv=['node','--check',str(SRC/name)],exit=r.returncode,stdoutBytes=len(r.stdout),stderrBytes=len(r.stderr),stdoutSHA256=sha(r.stdout),stderrSHA256=sha(r.stderr),seconds=time.monotonic()-t))
    assert r.returncode==0 and len(r.stdout)+len(r.stderr)<=4096
oldpins={p.name:pin(p) for p in OLD.iterdir() if p.is_file()}
log=(OLD/'run-37053546108-job-110992548885.decoded.log').read_text()
assert "waiting for locator('.title-hunter')" in log and 'Timeout 15000ms exceeded.' in log and 'HEAD is now at ebbcd78 Merge 265eb047' in log
jobs=json.loads((OLD/'jobs.json').read_text())['jobs'];assert len(jobs)==1 and jobs[0]['id']==110992548885 and jobs[0]['conclusion']=='failure'
artifact=json.loads((OLD/'artifacts.json').read_text())['artifacts']
art=next(x for x in artifact if x['id']==11247905305)
zp=stream_pin(ACT/'original.zip');assert zp==dict(bytes=10406248,sha256='a4287b8dc1e8257e310f21176dd0c328576a9310dae85c086655c6b10909045c')
assert art['digest']=='sha256:'+zp['sha256'] and art['workflow_run']['head_sha']==manifest['ref']
transfer=json.loads((ACT/'TRANSFER.json').read_text())
expected={x['name']:x for x in transfer['members']}; checked=[]
with zipfile.ZipFile(ACT/'original.zip') as z:
    info=z.infolist();assert len(info)==57 and len(set(x.filename for x in info))==57 and set(expected)==set(z.namelist())
    for x in info:
        assert not x.is_dir() and x.file_size<=2*1024**2 and not(x.flag_bits&1)
        n=0;h=hashlib.sha256()
        with z.open(x) as f:
            for b in iter(lambda:f.read(65536),b''):n+=len(b);h.update(b)
        entry=dict(name=x.filename,bytes=n,sha256=h.hexdigest());assert entry==expected[x.filename];checked.append(entry)
selected={}
for name,archive_name in [('failure.png','reviews/windows-native/0.9.0/run-37053546108-1/failure.png'),('smoke.json','reviews/windows-native/0.9.0/run-37053546108-1/smoke.json'),('build-provenance.json','dist/build-provenance.json')]:
    selected[name]=pin(ACT/name);assert selected[name]=={k:v for k,v in expected[archive_name].items() if k!='name'}
smoke=json.loads((ACT/'smoke.json').read_text());prov=json.loads((ACT/'build-provenance.json').read_text())
assert smoke['status']=='failed' and smoke['commit']=='ebbcd78a14ddf42dc2a8a8f7c695fe302035a0c3'
assert smoke['runtimeSourceDigest']==prov['sourceDigest']=='64c2a14ada2b24796535f9bb71d8a6acc534685365bcf4f5665b21bf18595353'
assert '.title-hunter' in smoke['failure'] and smoke['failedPhase']=='decode packaged hunter portrait'
assert before=={p.name:pin(p) for p in SRC.iterdir() if p.is_file()}
assert oldpins=={p.name:pin(p) for p in OLD.iterdir() if p.is_file()}
rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024;child=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss*1024
assert rss+child<=64*1024**2
receipt=dict(verdict='PASS bounded source grammar/inverse/byte checks only',admission=admission,sourceFiles=before,sourceInclusiveBytes=98919,sourceGateSHA256=before['SOURCE-GATE.json']['sha256'],manifestSHA256=before['MANIFEST.json']['sha256'],roundtrip=dict(blocks=len(ledger['changes']),forward=True,inverse=True,wholeFile=True,unifiedPatchExact=True),gitBlobPins=gitpins,grammar=grammar,preservedOldEvidence=oldpins,originalArtifact=dict(id=11247905305,zip=zp,memberCount=57,allMembers=checked,selectedCopies=selected,crcCheckedByFullZipRead=True),actualFailure=dict(head=manifest['ref'],checkedOutMerge=smoke['commit'],run=37053546108,job=110992548885,phase=smoke['failedPhase'],sourceDigest=prov['sourceDigest'],archiveSteps='SKIPPED',status='FAIL'),resource=dict(selfPeakRSS=rss,directGrammarChildPeakRSS=child,conservativePeakSum=rss+child,ordinaryCap=64*1024**2,reserve=512*1024**2,finiteSeconds=30),noSmokeExecution=True,noNativeWindowsExecution=True,sourceAndOriginalEvidenceUnchanged=True,atimeMayChange=True)
out=json.dumps(receipt,indent=2)+'\n';assert len(out.encode())<48*1024
(ROOT/'CHECKS.json').write_text(out)
print(json.dumps(dict(status='PASS',sourceBytes=98919,roundtripBlocks=3,zipMembers=57,resource=receipt['resource'],checks=pin(ROOT/'CHECKS.json'))))
