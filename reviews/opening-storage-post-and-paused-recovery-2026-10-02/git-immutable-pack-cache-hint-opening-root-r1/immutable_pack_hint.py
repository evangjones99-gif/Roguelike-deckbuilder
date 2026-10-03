"""SOURCE ONLY: requires new independent exact-source review and serial root grant.
One advisory DONTNEED call on a single pinned immutable repository pack.
Never reads its body, writes its bytes, scans global PIDs, or claims fresh SHA.
"""
import argparse, hashlib, json, os, re, resource, stat, sys, time
from pathlib import Path
BASE='/workspace/scratch/git-immutable-pack-cache-hint-opening-root-r1'
TARGET='/workspace/Roguelike-deckbuilder/.git/objects/pack/pack-b3e7e0bb9ce2d0a4d41cdb2daf9b6c3412cebe58.pack'
OUTPUT='/workspace/scratch/git-immutable-pack-cache-hint-opening-run-root-r1'
SCOPE='One immutable old Git pack FD cache hint; metadata-only preservation; no whole-pack SHA proof'
WORK=24*1024**2
# Distinct lightweight-only proposal; this is NOT a reduced build/browser guard.
RESERVE=64*1024**2
LIMIT=128*1024

def require(ok, text):
    if not ok:raise RuntimeError(text)

def sha(b):return hashlib.sha256(b).hexdigest()

def encoded(v):return (json.dumps(v,sort_keys=True,separators=(',',':'))+'\n').encode()

def meta(s):return {k:getattr(s,k)for k in ['st_dev','st_ino','st_mode','st_uid','st_gid','st_size','st_blocks','st_nlink','st_atime_ns','st_mtime_ns','st_ctime_ns']}

def identity(s):return {'device':s.st_dev,'inode':s.st_ino,'mode':s.st_mode,'uid':s.st_uid,'gid':s.st_gid}

def anchor(p):
    require(p.startswith('/') and '..'not in p.split('/'),'Literal absolute path required')
    flags=os.O_PATH|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC
    fds=[];rows=[]
    try:
        fds.append(os.open('/',flags))
        for n in p.split('/')[1:]:
            if not n:continue
            parent=fds[-1];fd=os.open(n,flags,dir_fd=parent);fds.append(fd)
            s=os.fstat(fd);t=os.stat(n,dir_fd=parent,follow_symlinks=False)
            require(stat.S_ISDIR(s.st_mode)and identity(s)==identity(t),'Redirected parent')
            rows.append((parent,n,fd,identity(s)))
        return fds,rows
    except BaseException:
        for f in reversed(fds):os.close(f)
        raise

def stable(rows):
    for parent,n,fd,r in rows:
        require(identity(os.fstat(fd))==r==identity(os.stat(n,dir_fd=parent,follow_symlinks=False)),'Parent drift')

def control(p,limit=32768):
    p=Path(p);fds,rows=anchor(str(p.parent));fd=None
    try:
        fd=os.open(p.name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME|os.O_NONBLOCK|os.O_CLOEXEC,dir_fd=fds[-1]);before=os.fstat(fd)
        require(stat.S_ISREG(before.st_mode)and before.st_size<=limit,'Control bounds/type')
        b=bytearray()
        while True:
            chunk=os.read(fd,min(4096,limit+1-len(b)))
            if not chunk:break
            b.extend(chunk);require(len(b)<=limit,'Control read bound')
        stable(rows);require(before==os.fstat(fd)==os.stat(p.name,dir_fd=fds[-1],follow_symlinks=False),'Control drift')
        return bytes(b)
    finally:
        if fd is not None:os.close(fd)
        for f in reversed(fds):os.close(f)

def process_memory():
    # /proc reports this executable's high-water/current RSS; getrusage may
    # retain a pre-exec high-water mark. Record both, never silently discard it.
    with open('/proc/self/status','rb')as f:raw=f.read(8193)
    require(len(raw)<=8192,'Own process status exceeds8KiB')
    values={}
    for line in raw.decode('ascii').splitlines():
        if line.startswith(('VmSize:','VmHWM:','VmRSS:','VmPeak:')):
            key,value,unit=line.split();require(unit=='kB','Unexpected process-memory unit')
            values[key.rstrip(':')]=int(value)*1024
    return {'currentExecBytes':values,'ruMaxRSSKiBHistorical':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}

def guard():
    c=Path('/sys/fs/cgroup');v={n:(c/n).read_text()for n in ['memory.current','memory.max','memory.stat','memory.events']}
    own=process_memory();finite=v['memory.max'].strip()!='max'
    head=int(v['memory.max'])-int(v['memory.current'])if finite else None
    # Root wrapper must capture stderr even if the first guard/AS ceiling
    # refuses before any receipt directory or target FD can be created.
    print(json.dumps({'phase':'lightweight-admission-before-assertions','headroomBytes':head,'requiredBytes':WORK+RESERVE,'workBytes':WORK,'reserveBytes':RESERVE,'ownMemory':own,'memoryEvents':v['memory.events']}),file=sys.stderr,flush=True)
    require(finite,'Finite cgroup required')
    require(head>=WORK+RESERVE,'Lightweight24MiB work +64MiB reserve unavailable')
    m=own['currentExecBytes'];require(all(k in m for k in ['VmRSS','VmHWM','VmSize']),'Own current-exec memory fields unavailable')
    require(m['VmHWM']<=WORK and m['VmRSS']<=WORK,'Own current-exec RSS high-water/current exceeds24MiB')
    return {'headroom':head,'cgroup':v,'ownMemory':own}

def locks(dev,ino):
    # Observation only: no lock acquisition/removal and no process-FD scan.
    with open('/proc/locks','rb')as f:b=f.read(LIMIT+1)
    require(len(b)<=LIMIT,'Lock observation exceeds128KiB')
    target=(os.major(dev),os.minor(dev),ino);count=0
    for line in b.decode('ascii').splitlines():
        if not line.strip():continue
        addresses=[re.fullmatch(r'([0-9a-fA-F]+):([0-9a-fA-F]+):(\d+)',t)for t in line.split()]
        matches=[m for m in addresses if m]
        require(len(matches)==1,'Unknown lock row syntax')
        m=matches[0];observed=(int(m[1],16),int(m[2],16),int(m[3]));count+=1
        require(observed!=target,'Affected inode has a visible lock, including blocked lock')
    return {'rowsObserved':count,'rawMetadataSHA256':sha(b),'scope':'Visible /proc/locks only, namespace/kernel-dependent; not global PID/reader absence or atomic exclusion'}

def observe(fd,parent,leaf,pin):
    a=os.fstat(fd);b=os.stat(leaf,dir_fd=parent,follow_symlinks=False)
    require(stat.S_ISREG(a.st_mode)and a.st_uid==os.geteuid()and a.st_nlink==1,'Owned regular single-link target required')
    require(not(a.st_mode&0o222),'Pinned target has writable permission bits')
    attrs={n:os.getxattr(fd,n).hex()for n in sorted(os.listxattr(fd))}
    require(meta(a)==meta(b)==meta(os.fstat(fd))==pin['metadata']and attrs==pin['xattrs'],'Target metadata/atime/xattr drift')
    return {'metadata':meta(a),'xattrs':attrs,'freshBodySHA':False}

class Receipts:
    def __init__(self):
        self.fds,self.rows=anchor('/workspace/scratch');self.fd=None;self.failure=None
        try:
            v=os.statvfs('/workspace/scratch');require(v.f_bavail*v.f_frsize>=1024**2+49152,'Receipt space reserve')
            os.mkdir(Path(OUTPUT).name,0o700,dir_fd=self.fds[-1])
            self.fd=os.open(Path(OUTPUT).name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_NOATIME|os.O_CLOEXEC,dir_fd=self.fds[-1])
            self.used=0;self.write('FAILURE-SLOT.json',encoded({'status':'reserved; no failure recorded'}).ljust(8192,b' '))
            self.failure=os.open('FAILURE-SLOT.json',os.O_WRONLY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=self.fd)
        except BaseException:
            self.close();raise
    def write(self,n,b):
        require(self.used+len(b)<=49152,'Receipt budget exhausted');fd=None
        try:
            fd=os.open(n,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600,dir_fd=self.fd)
            view=memoryview(b)
            while view:
                count=os.write(fd,view);require(count>0,'Short write');view=view[count:]
            os.fsync(fd);os.fsync(self.fd);self.used+=len(b)
        finally:
            if fd is not None:os.close(fd)
    def fail(self,v):
        b=encoded(v);require(len(b)<=8192,'Failure slot bound');b=b.ljust(8192,b' ');pos=0
        while pos<len(b):
            n=os.pwrite(self.failure,b[pos:],pos);require(n>0,'Short failure write');pos+=n
        os.fsync(self.failure);os.fsync(self.fd)
    def close(self):
        if self.failure is not None:os.close(self.failure);self.failure=None
        if self.fd is not None:os.close(self.fd);self.fd=None
        for f in reversed(self.fds):os.close(f)
        self.fds=[]

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--declaration',required=True);parser.add_argument('--acceptance',required=True)
    args=parser.parse_args();guard()
    # At most8MiB additional virtual address room; no allocation experiment.
    vm=process_memory()['currentExecBytes']['VmSize']
    print(json.dumps({'phase':'address-ceiling-before-assertion','virtualBaselineBytes':vm,'maximumVirtualBaselineBytes':64*1024**2,'additionalAddressAllowanceBytes':8*1024**2}),file=sys.stderr,flush=True)
    require(vm<=64*1024**2,'Interpreter virtual baseline exceeds64MiB')
    resource.setrlimit(resource.RLIMIT_AS,(vm+8*1024**2,vm+8*1024**2))
    r=Receipts();fds=[];fd=None;armed=False;returned=False
    try:
        require(all(hasattr(os,k)for k in ['O_PATH','O_NOATIME','POSIX_FADV_DONTNEED','posix_fadvise']),'Required Linux APIs absent')
        source=control(str(Path(__file__).absolute()));pinbytes=control(BASE+'/METADATA-INTAKE.json');pin=json.loads(pinbytes)
        require(pin['path']==TARGET and pin['metadata']['st_ino']==659415 and pin['metadata']['st_size']==1612289309,'Wrong single target pin')
        declaration=control(args.declaration);d=json.loads(declaration);acceptance=control(args.acceptance);a=json.loads(acceptance)
        sourceSHA=sha(source);pinSHA=sha(pinbytes)
        for v in [d,a]:require(v['sourceSHA256']==sourceSHA and v['pinSHA256']==pinSHA and v['scope']==SCOPE,'Declaration/review identity')
        require(a.get('allowSingleHintAttemptOnly')is True and a.get('historicalWholePackHashUnavailableAcknowledged')is True,'Distinct explicit review missing')
        require(sha(control(a['reviewPath']))==a['reviewSHA256'],'Independent review bytes changed')
        for k in ['priorPushConfirmed','exclusiveKnownRepoWritersHeld','repositoryMaintenanceHeld','noUnknownAffectedWriter','noUnknownAffectedLockOwner','noHeavyRuntimeConcurrent']:
            require(d.get(k)is True,'Root coordination missing: '+k)
        def fresh():
            require(control(args.declaration)==declaration,'Declaration drift')
            require(-5<=time.time()-d['issuedUnixSeconds']<=120,'Serial declaration expired')
        fresh();r.write('CONTROL-RECEIPTS.json',encoded({'declaration':d,'acceptance':a,'sourceSHA256':sourceSHA,'pinSHA256':pinSHA,'priorWholePackSHA256':None,'qualification':'Absent exact historical whole-pack SHA; no bundle/newpack SHA substituted'}))
        target=Path(TARGET);fds,chain=anchor(str(target.parent))
        require([{'name':n,**i}for _,n,_,i in chain]==pin['parentChain'],'Pinned parent identity mismatch')
        fd=os.open(target.name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME|os.O_NONBLOCK|os.O_CLOEXEC,dir_fd=fds[-1])
        before=observe(fd,fds[-1],target.name,pin);stable(chain);lockbefore=locks(pin['metadata']['st_dev'],pin['metadata']['st_ino']);fresh();memorybefore=guard()
        r.write('BEFORE.json',encoded({'target':before,'locks':lockbefore,'memory':memorybefore,'bodyRead':False,'globalPIDsExamined':False}))
        stable(chain);observe(fd,fds[-1],target.name,pin);locks(pin['metadata']['st_dev'],pin['metadata']['st_ino']);fresh();guard()
        r.write('ARMED.json',encoded({'target':TARGET,'fdO_RDONLY':True,'length':0,'offset':0,'advice':'POSIX_FADV_DONTNEED','oneCallOnly':True}));armed=True
        os.posix_fadvise(fd,0,0,os.POSIX_FADV_DONTNEED);returned=True
        r.write('RETURNED.json',encoded({'returnedWithoutException':True,'errno':0,'reclaimGuaranteed':False}))
        after=observe(fd,fds[-1],target.name,pin);stable(chain);lockafter=locks(pin['metadata']['st_dev'],pin['metadata']['st_ino'])
        os.close(fd);fd=None
        for f in reversed(fds):os.close(f)
        fds=[]
        samples=[]
        for i in range(3):
            if i:time.sleep(0.05)
            samples.append(guard())
        r.write('AFTER.json',encoded({'target':after,'locks':lockafter,'samples':samples,'ownTargetFDClosed':True,'metadataUnchanged':True,'ownToolPackByteWrites':False,'packBodiesRead':False,'freshWholePackSHA':False,'scope':'Observed counters only; no causal attribution, all-byte fresh proof, residency guarantee or later runtime admission'}))
        print('Single advice returned; metadata exact. Inspect receipts; no reclaim guarantee.')
    except BaseException as e:
        if fd is not None:os.close(fd);fd=None
        for f in reversed(fds):os.close(f)
        fds=[]
        v={'errorType':type(e).__name__,'error':str(e)[:1500],'errno':getattr(e,'errno',None),'armed':armed,'adviceReturned':returned,'scope':'Stop, no retry/rollback/global action. Armed without return remains unknown outcome.'}
        try:v['memory']=guard()
        except BaseException as secondary:v['memorySnapshotRefused']=str(secondary)[:300]
        r.fail(v);raise
    finally:
        if fd is not None:os.close(fd)
        for f in reversed(fds):os.close(f)
        r.close()
if __name__=='__main__':main()
