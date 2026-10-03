"""One guarded retention of exact generated media copies; never overwrite inputs.

Only the independently listed PNG/WAV pairs may change. Public media must remain
immutable and future writers must use the independently checked empty-out-dir
strict build, or detach generated links before any direct/incremental writes.
"""
from pathlib import Path
import hashlib,json,os,stat

ROOT = Path('/workspace/Roguelike-deckbuilder')
PLAN = Path('/workspace/scratch/root-dist-media-hardlink-plan-independent-v09-r1')
OUT = ROOT/'reviews/root-dist-media-retention-v0.9/transaction-r1'
TOKEN = 'hollowpact-media-retention-r1'
RESERVE = 1024**2

def free():
    v=os.statvfs(ROOT);return v.f_bavail*v.f_frsize

def memory():
    b=Path('/sys/fs/cgroup')
    remaining=int((b/'memory.max').read_text())-int((b/'memory.current').read_text())
    assert remaining >= (512+128)*1024**2,remaining
    return remaining

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        while body:=f.read(1024**2):memory();h.update(body)
    return h.hexdigest()

def meta(p):
    s=p.lstat();assert not p.is_symlink()
    return {'dev':s.st_dev,'ino':s.st_ino,'mode':s.st_mode,'uid':s.st_uid,'gid':s.st_gid,
            'nlink':s.st_nlink,'bytes':s.st_size,'blocks':s.st_blocks,'atimeNS':s.st_atime_ns,
            'mtimeNS':s.st_mtime_ns,'ctimeNS':s.st_ctime_ns,
            'xattrs':{k:os.getxattr(p,k,follow_symlinks=False).hex() for k in os.listxattr(p,follow_symlinks=False)}}

def stable(m):return {k:v for k,v in m.items() if k!='atimeNS'}

def sync_dir(p):
    fd=os.open(p,os.O_DIRECTORY)
    try:os.fsync(fd)
    finally:os.close(fd)

def write(name,value):
    body=(json.dumps(value,separators=(',',':'))+'\n').encode()
    assert len(body)<=64*1024
    block=os.statvfs(ROOT).f_frsize
    assert free()>=RESERVE+((len(body)+block-1)//block)*block+2*block
    with (OUT/name).open('xb') as f:f.write(body);f.flush();os.fsync(f.fileno())
    sync_dir(OUT);assert free()>=RESERVE

def paths(row):
    src,dst=ROOT/row['source'],ROOT/row['destination']
    assert row['source'].startswith('public/') and row['destination']=='dist/'+row['source'][7:]
    assert src.suffix.lower() in ('.png','.wav')
    for p in (src,dst):
        assert p.resolve()==p and '..' not in p.parts
        assert all(not ancestor.is_symlink() for ancestor in p.parents)
    return src,dst

def contents():
    p=ROOT/'dist/build-provenance.json';runtime=json.loads(p.read_text())
    assert runtime['sourceDigest']=='801db1ce4000c15268569cb047e7388148a65105c7b86208611ceb3aff40f029'
    assert len(runtime['hashes'])==78
    assert hashlib.sha256(json.dumps(runtime['hashes'],separators=(',',':')).encode()).hexdigest()==runtime['sourceDigest']
    for name,digest in runtime['hashes'].items():assert sha(ROOT/name)==digest,name
    files=sorted(p for p in (ROOT/'dist').rglob('*') if p.is_file())
    assert len(files)==56
    return {'runtime':runtime['sourceDigest'],'sources':runtime['hashes'],
            'outputs':{str(p.relative_to(ROOT)):sha(p) for p in files}}

memory();assert not OUT.exists() and free()>=RESERVE+256*1024
assert sha(PLAN/'PLAN.md')=='583c96a517070ac09075cbc488528daf69d333353b1e6c92635de0850744fcf2'
assert sha(PLAN/'INVENTORY-R2.json')=='069fbddb61bc5fc9af80b94e4770f7bf9a808fb5356bc4b1f5264034c9982113'
data=json.loads((PLAN/'INVENTORY-R2.json').read_text());pairs=data['pairs']
assert len(pairs)==50 and data['eligibleCount']==50
assert len({r['source'] for r in pairs})==50 and len({r['destination'] for r in pairs})==50
before=contents();directories={str(p):meta(p) for p in [ROOT/'public',ROOT/'public/art',ROOT/'public/audio',ROOT/'dist',ROOT/'dist/art',ROOT/'dist/audio']}
checked=[]
for row in pairs:
    src,dst=paths(row);sm,dm=meta(src),meta(dst)
    assert stable(sm)==stable(row['sourceMetadata']) and stable(dm)==stable(row['destinationMetadata'])
    assert stat.S_ISREG(sm['mode']) and stat.S_ISREG(dm['mode'])
    assert sm['uid']==dm['uid']==os.getuid() and sm['gid']==dm['gid']==os.getgid()
    assert sm['dev']==dm['dev'] and sm['ino']!=dm['ino'] and sm['nlink']==dm['nlink']==1
    assert sm['mode']==dm['mode'] and sm['xattrs']==dm['xattrs']
    assert sha(src)==sha(dst)==row['sha256']
    temp=dst.with_name('.'+dst.name+'.'+TOKEN);assert not temp.exists() and not temp.is_symlink()
    checked.append({**row,'sourceMetadata':sm,'destinationMetadata':dm,'temporary':str(temp)})
OUT.mkdir(mode=0o700);sync_dir(OUT.parent)
initial_free=free()
write('PREFLIGHT.json',{'token':TOKEN,'planSHA256':sha(PLAN/'PLAN.md'),'inventorySHA256':sha(PLAN/'INVENTORY-R2.json'),
      'freeBefore':initial_free,'reserve':RESERVE,'memoryHeadroom':memory(),'pairs':checked,'directories':directories,
      'scope':'Exclusive root media writer freeze; exact immutable source and generated copies; no historical release/input/art/dataset/Git bytes changed'})
write('BEFORE-BYTES.json',before)
temps=[]
for row in checked:
    src,dst=paths(row);temp=Path(row['temporary'])
    assert stable(meta(src))==stable(row['sourceMetadata']) and stable(meta(dst))==stable(row['destinationMetadata'])
    assert sha(src)==sha(dst)==row['sha256']
    os.link(src,temp,follow_symlinks=False)
    sm,tm=meta(src),meta(temp)
    assert sm==tm and sm['nlink']==2 and sha(temp)==row['sha256']
    assert {k:v for k,v in sm.items() if k not in ('ctimeNS','atimeNS','nlink')}=={k:v for k,v in row['sourceMetadata'].items() if k not in ('ctimeNS','atimeNS','nlink')}
    temps.append({'source':str(src),'temporary':str(temp),'sourceAfterLink':meta(src)})
for d in (ROOT/'dist/art',ROOT/'dist/audio'):sync_dir(d)
write('ALL-TEMPORARIES-VERIFIED.json',temps)
# All fifty replacement byte paths exist before the first atomic output rename.
with (OUT/'STEPS.jsonl').open('xb') as journal:
    journal.flush();os.fsync(journal.fileno());sync_dir(OUT)
    for row in checked:
        src,dst=paths(row);temp=Path(row['temporary'])
        assert stable(meta(dst))==stable(row['destinationMetadata']) and sha(dst)==row['sha256']
        assert meta(src)==meta(temp) and sha(temp)==row['sha256']
        assert free()>=RESERVE+64*1024
        os.replace(temp,dst);sync_dir(dst.parent)
        sm,dm=meta(src),meta(dst)
        assert sm==dm and sm['nlink']==2 and sha(src)==sha(dst)==row['sha256']
        entry={'source':row['source'],'destination':row['destination'],'beforeSource':row['sourceMetadata'],
               'beforeDestination':row['destinationMetadata'],'afterSource':meta(src),'afterDestination':meta(dst),'sha256':row['sha256']}
        journal.write((json.dumps(entry,separators=(',',':'))+'\n').encode());journal.flush();os.fsync(journal.fileno())
sync_dir(OUT)
after=contents();assert after==before
for row in checked:
    src,dst=paths(row);assert meta(src)==meta(dst) and not Path(row['temporary']).exists()
    assert {k:v for k,v in meta(src).items() if k not in ('ctimeNS','atimeNS','nlink')}=={k:v for k,v in row['sourceMetadata'].items() if k not in ('ctimeNS','atimeNS','nlink')}
assert free()>=RESERVE and free()>initial_free
write('AFTER-BYTES.json',after)
write('POST.json',{'pairs':50,'sourceInputs':78,'outputs':56,'runtime':before['runtime'],'allRawSourceAndOutputBytesUnchanged':True,
       'allLinksIdentityAndPreservedSourceFieldsVerified':True,'noTemporaryPathsRemain':True,
       'freeBefore':initial_free,'freeAfterBeforeThisReceipt':free(),'measuredRecoveryBeforeThisReceipt':free()-initial_free,
       'directoriesAfter':{name:meta(Path(name)) for name in directories},
       'scope':'Only redundant generated output copies replaced; source nlink/ctime and adopted output metadata are disclosed. Old releases/reviews/art/datasets untouched. Full rebuild rematerializes copies and needs a separate allocation budget; no build/hardware/crash qualification.'})
print(json.dumps({'retainedPairs':50,'runtime':before['runtime'],'free':free()}))
