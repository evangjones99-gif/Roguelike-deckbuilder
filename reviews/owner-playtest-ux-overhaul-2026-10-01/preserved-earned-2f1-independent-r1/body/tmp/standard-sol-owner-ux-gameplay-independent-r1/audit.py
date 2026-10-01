"""Read-only streamed identity audit; never imports or runs game."""
import hashlib,json,os,pathlib,resource,stat,sys
resource.setrlimit(resource.RLIMIT_DATA,(24*1048576,24*1048576))
HERE=pathlib.Path(__file__).resolve().parent
VARIANTS={
 'candidate':('/dev/shm/hollowpact-owner-ux-overhaul-root-r1','2f1fd23d0af5d43d7ee1ed9242063404bd242702df44d2db7b15f007e8306629',82),
 'baseline':('/workspace/Roguelike-deckbuilder','801db1ce4000c15268569cb047e7388148a65105c7b86208611ceb3aff40f029',78)}
def memory():
    rows={s.split(':')[0]:int(s.split()[1])*1024 for s in pathlib.Path('/proc/self/status').read_text().splitlines() if s.startswith(('VmRSS:','VmHWM:'))}
    assert rows['VmHWM']<=24*1048576
    rows['ruMaxRSSBytes']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024
    return rows
def stamp(s):return [s.st_dev,s.st_ino,s.st_mode,s.st_size,s.st_mtime_ns,s.st_ctime_ns]
def read(path,small=False):
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME|os.O_CLOEXEC)
    try:
        before=os.fstat(fd);assert stat.S_ISREG(before.st_mode)
        assert not small or before.st_size<=262144
        h=hashlib.sha256();chunks=[];size=0
        while b:=os.read(fd,32768):
            h.update(b);size+=len(b)
            if small:chunks.append(b)
        assert size==before.st_size and stamp(before)==stamp(os.fstat(fd))==stamp(os.stat(path,follow_symlinks=False))
        row=dict(bytes=size,sha256=h.hexdigest(),metadata=stamp(before))
        return (row,b''.join(chunks)) if small else row
    finally:os.close(fd)
def members(root,dirs):
    paths=[]
    for directory in dirs:
        for p in sorted((root/directory).rglob('*')):
            m=p.lstat().st_mode;assert not stat.S_ISLNK(m)
            if stat.S_ISREG(m):paths.append(str(p.relative_to(root)))
            else:assert stat.S_ISDIR(m)
    return paths
assert len(sys.argv)==2 and sys.argv[1] in ['before','after']
phase=sys.argv[1];memory()
maximum=int(pathlib.Path('/sys/fs/cgroup/memory.max').read_text());current=int(pathlib.Path('/sys/fs/cgroup/memory.current').read_text())
assert maximum-current>=24*1048576+512*1048576
v=os.statvfs(HERE);assert v.f_bavail*v.f_frsize>=1048576+65536
results={}
for variant,(directory,expected,count) in VARIANTS.items():
    root=pathlib.Path(directory)
    paths=sorted(members(root,['src','desktop','public'])+['index.html','THIRD-PARTY.md','package.json','package-lock.json','tsconfig.json','vite.config.ts','scripts/build.mjs'])
    ledger={name:read(root/name) for name in paths};hashes={name:row['sha256'] for name,row in ledger.items()}
    digest=hashlib.sha256(json.dumps(hashes,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
    provenance=json.loads(read(root/'dist/build-provenance.json',True)[1])
    assert digest==expected==provenance['sourceDigest'] and hashes==provenance['hashes'] and len(ledger)==count
    output={name:read(root/name) for name in sorted(members(root,['dist']))};assert len(output)==56
    results[variant]=dict(root=str(root),sourceDigest=digest,inputs=ledger,outputs=output);memory()
report=dict(phase=phase,status='EXACT READONLY SOURCE/OUTPUT AUDIT',variants=results,memory=memory(),cgroup=dict(current=current,maximum=maximum))
if phase=='after':assert results==json.loads((HERE/'AUDIT-before.json').read_text())['variants']
b=(json.dumps(report,separators=(',',':'))+'\n').encode();assert len(b)<=65536
with (HERE/('AUDIT-'+phase+'.json')).open('xb') as f:f.write(b);f.flush();os.fsync(f.fileno())
print(json.dumps(dict(phase=phase,reportBytes=len(b),reportSHA256=hashlib.sha256(b).hexdigest(),memory=report['memory'])))
