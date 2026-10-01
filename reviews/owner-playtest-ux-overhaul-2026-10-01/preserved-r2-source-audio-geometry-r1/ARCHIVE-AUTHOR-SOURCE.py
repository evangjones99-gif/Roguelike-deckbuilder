#!/usr/bin/env python3
"""Append exclusive evidence ZIPs; preserve copied files and all prior receipts."""
import contextlib
import hashlib
import json
import os
import pathlib
import resource
import stat
import time
import zipfile

M = 1024*1024
resource.setrlimit(resource.RLIMIT_DATA, (24*M, 24*M))
BASE = pathlib.Path('/workspace/Roguelike-deckbuilder/reviews/owner-playtest-ux-overhaul-2026-10-01')
NAMES = ('preserved-earned-2f1-independent-r1',
         'preserved-r2-build-root-smoke-r1',
         'preserved-r2-source-audio-geometry-r1')
PINS = ('6b556e8073045c21e9144099cdc49b23ee1e9ccb92b1bf9d89efe6ed86ef3f63',
        'cada1029354b60e91e11939e06aff245c4daf30f6b2a0a50c43440bf07f23244',
        '46ce27dc7e795b4d02385e4f624e882faafce4b4dd59b042dec7d2da7b641f91')
DF = os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW
RF = os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME

def stamp(s):
    return {k:getattr(s,'st_'+k) for k in
            ('dev','ino','mode','uid','gid','nlink','size','atime_ns','mtime_ns','ctime_ns')}

@contextlib.contextmanager
def parent(path):
    path=pathlib.Path(path);assert path.is_absolute() and '..' not in path.parts
    fd=os.open('/',DF)
    try:
        for part in path.parts[1:-1]:
            nxt=os.open(part,DF,dir_fd=fd);os.close(fd);fd=nxt
        yield fd,path.name
    finally:os.close(fd)

def guard(label,need=0,fresh=False):
    c=int(pathlib.Path('/sys/fs/cgroup/memory.current').read_text())
    mx=int(pathlib.Path('/sys/fs/cgroup/memory.max').read_text())
    mem={}
    for line in pathlib.Path('/proc/self/status').read_text().splitlines():
        if line.startswith(('VmRSS:','VmHWM:')):
            k,v,_=line.split();mem[k[:-1]]=int(v)*1024
    fs=os.statvfs(BASE)
    result={'label':label,'current':c,'maximum':mx,'headroom':mx-c,
            'free':fs.f_bavail*fs.f_frsize,**mem}
    assert mx-c >= 512*M+(24*M if fresh else 0),result
    assert mem['VmHWM']<=24*M and mem['VmRSS']<=24*M,result
    assert result['free']>=need+3*M,result
    return result

def stable_hash(path):
    with parent(path) as (p,n):
        fd=os.open(n,RF,dir_fd=p)
        try:
            before=stamp(os.fstat(fd));assert stat.S_ISREG(before['mode'])
            assert before['size']<=10*M
            h=hashlib.sha256()
            while chunk:=os.read(fd,65536):h.update(chunk);guard('hash')
            assert stamp(os.fstat(fd))==before
            assert stamp(os.stat(n,dir_fd=p,follow_symlinks=False))==before
            return h.hexdigest(),before
        finally:os.close(fd)

def exclusive_json(path,value):
    b=(json.dumps(value,indent=2,sort_keys=True)+'\n').encode();assert len(b)<M
    with parent(path) as (p,n):
        fd=os.open(n,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o644,dir_fd=p)
        try:
            view=memoryview(b)
            while view:view=view[os.write(fd,view):]
            os.fsync(fd)
        finally:os.close(fd)
        os.fsync(p)

def info(relative,metadata):
    assert relative and not relative.startswith('/') and '..' not in pathlib.PurePosixPath(relative).parts
    zi=zipfile.ZipInfo(relative,tuple(time.gmtime(metadata['mtime_ns']/1e9)[:6]))
    zi.create_system=3;zi.external_attr=metadata['mode']<<16
    zi.compress_type=zipfile.ZIP_DEFLATED
    return zi

identities=[]
for name,pin in zip(NAMES,PINS):
    capsule=BASE/name
    admitted=guard('fresh-zip-admission',64*M,fresh=True)
    digest,_=stable_hash(capsule/'PRESERVATION.json');assert digest==pin
    files=[]
    for current,dirs,names in os.walk(capsule,followlinks=False):
        dirs.sort();names.sort()
        for d in dirs:assert not (pathlib.Path(current)/d).is_symlink()
        for n in names:
            path=pathlib.Path(current)/n
            digest,metadata=stable_hash(path)
            files.append({'relative':path.relative_to(capsule).as_posix(),
                          'bytes':metadata['size'],'sha256':digest,'metadata':metadata})
    logical=sum(r['bytes'] for r in files);assert logical<=64*M
    member_manifest={'capsule':str(capsule),'preservationSHA256':pin,
        'members':files,'independentAcceptanceRequired':True,
        'limitations':['Chromium profiles excluded and retained in original locations.',
            'Unchanged R2 bodies are explicit ROOT801db references, not contained runtime bodies.',
            'ZIP timestamps have format precision; exact nanosecond file metadata is retained here and in PRESERVATION.json.',
            'No new gameplay, AAA or promotion claim.']}
    exclusive_json(capsule/'ARCHIVE-MEMBERS.json',member_manifest)
    digest,metadata=stable_hash(capsule/'ARCHIVE-MEMBERS.json')
    files.append({'relative':'ARCHIVE-MEMBERS.json','bytes':metadata['size'],
                  'sha256':digest,'metadata':metadata})
    archive=capsule/'FROZEN-EVIDENCE.zip'
    active=None
    try:
        with parent(archive) as (p,n):
            fd=os.open(n,os.O_RDWR|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_NOATIME,0o644,dir_fd=p)
            try:
                with os.fdopen(fd,'w+b',closefd=False) as output:
                    with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
                        for row in files:
                            active=row['relative'];guard('member-fresh',row['bytes'],fresh=True)
                            with parent(capsule/active) as (sp,sn):
                                sf=os.open(sn,RF,dir_fd=sp)
                                try:
                                    assert stamp(os.fstat(sf))==row['metadata']
                                    h=hashlib.sha256()
                                    with z.open(info(active,row['metadata']),'w',force_zip64=True) as member:
                                        while chunk:=os.read(sf,65536):member.write(chunk);h.update(chunk);guard('archive-stream')
                                    assert h.hexdigest()==row['sha256']
                                    assert stamp(os.fstat(sf))==row['metadata']
                                    assert stamp(os.stat(sn,dir_fd=sp,follow_symlinks=False))==row['metadata']
                                finally:os.close(sf)
                    output.flush();os.fsync(fd);os.fsync(p)
                    archive_before=stamp(os.fstat(fd));assert archive_before['size']<=64*M
                    output.seek(0)
                    with zipfile.ZipFile(output,'r') as z:
                        assert z.namelist()==[r['relative'] for r in files]
                        for row in files:
                            h=hashlib.sha256();count=0
                            with z.open(row['relative']) as member:
                                while chunk:=member.read(65536):count+=len(chunk);h.update(chunk);guard('member-roundtrip')
                            assert count==row['bytes'] and h.hexdigest()==row['sha256']
                    assert stamp(os.fstat(fd))==archive_before
                    output.seek(0);h=hashlib.sha256()
                    while chunk:=output.read(65536):h.update(chunk);guard('archive-identity')
                    assert stamp(os.fstat(fd))==archive_before
                    assert stamp(os.stat(n,dir_fd=p,follow_symlinks=False))==archive_before
                    result={'status':'PASS author ZIP member roundtrip; independent acceptance pending',
                        'archive':str(archive),'bytes':archive_before['size'],'sha256':h.hexdigest(),
                        'archiveMetadata':archive_before,'members':len(files),'logicalMemberBytes':sum(r['bytes'] for r in files),
                        'admission':admitted,'final':guard('archive-complete'),
                        'profilesIncluded':False,'completeStandaloneRuntimeCapsule':False}
            finally:os.close(fd)
        # Confirm every packaged canonical body/receipt still has its original snapshot identity.
        for row in files:
            with parent(capsule/row['relative']) as (p,n):
                assert stamp(os.stat(n,dir_fd=p,follow_symlinks=False))==row['metadata']
        exclusive_json(capsule/'ARCHIVE.json',result);identities.append(result)
    except BaseException as e:
        exclusive_json(capsule/'ARCHIVE-FAILURE.json',{'error':repr(e),'activeMember':active,
            'partialArchive':str(archive),'action':'Retain every partial file and original; no overwrite or deletion.'})
        raise
print(json.dumps({'archives':identities,'independentPreservationCheckRequired':True}))
