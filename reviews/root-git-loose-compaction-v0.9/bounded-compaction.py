"""Replace only redundantly represented loose Git encodings after independent review.

No reachability filtering, pruning, old-pack replacement or source/ref writes.
prepare creates a complete durable pack but retains every loose input. publish
also retains every input. finish is a separate, explicitly gated root action.
"""
from pathlib import Path
import gzip, hashlib, json, os, re, stat, struct, subprocess, sys, zlib

mode, repository, staging, proof = sys.argv[1:5]
repo, stage, out = map(lambda p: Path(p).resolve(), (repository, staging, proof))
RESERVE, RECEIPT = 1024**2, 512*1024
INPUT_BUDGET = 256*1024
MEMORY_RESERVE = 512*1024**2

def git(args, data=None, env=None):
    p = subprocess.run(['git', *args], cwd=repo, input=data, env=env,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert p.returncode == 0, (args, p.returncode, p.stderr.decode())
    return p.stdout

root = Path(git(['rev-parse', '--absolute-git-dir']).decode().strip())
assert (root/'objects').is_dir() and repo.is_dir()
assert git(['rev-parse', '--show-object-format']).strip() == b'sha1'
assert stage.parent == root/'objects' and not stage.is_symlink()

def memory():
    base = Path('/sys/fs/cgroup')
    maximum = (base/'memory.max').read_text().strip()
    assert maximum != 'max', 'A measured cgroup bound is required'
    headroom = int(maximum)-int((base/'memory.current').read_text())
    assert headroom >= MEMORY_RESERVE+128*1024**2, headroom
    return headroom

def capacity():
    v = os.statvfs(root)
    return v.f_bavail*v.f_frsize

def meta(p):
    s = p.lstat()
    assert stat.S_ISREG(s.st_mode) and not p.is_symlink(), str(p)
    return [s.st_dev,s.st_ino,s.st_mode,s.st_uid,s.st_gid,s.st_size,
            s.st_blocks*512,s.st_mtime_ns,s.st_ctime_ns,s.st_nlink]

def digest_file(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        while b := f.read(1024**2):
            memory(); h.update(b)
    return h.hexdigest()

def identity():
    result = {'HEAD': (root/'HEAD').read_bytes().hex(),
              'refs': git(['for-each-ref','--format=%(refname) %(objectname)']).decode(),
              'referenceFiles': {}, 'packs': {}}
    refs = list((root/'refs').rglob('*')) if (root/'refs').exists() else []
    for p in refs+[root/'packed-refs']:
        if p.is_file(): result['referenceFiles'][str(p.relative_to(root))] = [meta(p),digest_file(p)]
    for p in sorted((root/'objects/pack').iterdir()):
        if p.is_file(): result['packs'][p.name] = meta(p)
    return result

def inventory():
    rows = []
    for d in sorted((root/'objects').iterdir()):
        if not re.fullmatch('[0-9a-f]{2}',d.name): continue
        assert d.is_dir() and not d.is_symlink()
        for p in sorted(d.iterdir()):
            assert re.fullmatch('[0-9a-f]{38}',p.name), str(p)
            m = meta(p)
            with p.open('rb') as f:
                header = zlib.decompressobj().decompress(f.read(4096),256).split(b'\0',1)[0]
            ty, size = header.decode().split(' ')
            assert ty in ('blob','tree','commit','tag') and size.isdecimal()
            rows.append({'oid':d.name+p.name,'metadata':m,'type':ty,'size':int(size),
                         'encodedSHA256':digest_file(p)})
            assert meta(p) == m
    return rows

def original(row):
    p = root/'objects'/row['oid'][:2]/row['oid'][2:]
    assert meta(p) == row['metadata'] and digest_file(p) == row['encodedSHA256']
    encoded = p.read_bytes(); dec = zlib.decompressobj()
    limit = len(f"{row['type']} {row['size']}".encode())+1+row['size']
    b = dec.decompress(encoded,limit+1)
    assert dec.eof and not dec.unused_data and not dec.unconsumed_tail
    ty, body = b.split(b'\0',1)
    assert ty == f"{row['type']} {row['size']}".encode() and len(body) == row['size']
    assert hashlib.sha1(b).hexdigest() == row['oid']
    return body

def isolated_check(pack_dir, rows):
    env = os.environ.copy()
    env['GIT_OBJECT_DIRECTORY'] = str(pack_dir.parent)
    for key in ['GIT_ALTERNATE_OBJECT_DIRECTORIES','GIT_COMMON_DIR','GIT_DIR',
                'GIT_REPLACE_REF_BASE','GIT_SHALLOW_FILE']: env.pop(key,None)
    env['GIT_NO_REPLACE_OBJECTS'] = '1'
    assert not (pack_dir.parent/'info/alternates').exists()
    data = ('\n'.join(r['oid'] for r in rows)+'\n').encode()
    got = git(['cat-file','--batch'],data,env)
    offset = 0
    for r in rows:
        end = got.index(b'\n',offset)
        assert got[offset:end] == f"{r['oid']} {r['type']} {r['size']}".encode()
        offset = end+1; body = got[offset:offset+r['size']]; offset += r['size']
        assert got[offset:offset+1] == b'\n'; offset += 1
        raw = f"{r['type']} {r['size']}".encode()+b'\0'+body
        assert hashlib.sha1(raw).hexdigest() == r['oid']
        assert hashlib.sha256(body).hexdigest() == r['bodySHA256']
    assert offset == len(got)

def checks(pack, idx, rows):
    b = pack.read_bytes(); i = idx.read_bytes()
    assert b[:4] == b'PACK' and struct.unpack('>II',b[4:12]) == (2,len(rows))
    assert hashlib.sha1(b[:-20]).digest() == b[-20:]
    assert i[:8] == b'\xfftOc\0\0\0\2'
    assert hashlib.sha1(i[:-20]).digest() == i[-20:] and i[-40:-20] == b[-20:]
    lines = git(['verify-pack','-v',str(idx)]).decode().splitlines()
    oids = [l.split()[0] for l in lines if re.match('^[0-9a-f]{40} ',l)]
    assert len(oids) == len(rows) and set(oids) == {r['oid'] for r in rows}
    isolated_check(pack.parent,rows)
    return {'packSHA256':hashlib.sha256(b).hexdigest(),'indexSHA256':hashlib.sha256(i).hexdigest(),
            'gitChecksum':b[-20:].hex(),'objects':len(rows),'allocatedPair':meta(pack)[6]+meta(idx)[6]}

def sync_dir(p):
    fd = os.open(p,os.O_DIRECTORY)
    try: os.fsync(fd)
    finally: os.close(fd)

def write(name, value):
    body = (json.dumps(value,separators=(',',':'))+'\n').encode()
    assert len(body) <= RECEIPT//4, 'Receipt exceeds bounded allowance'
    block = os.statvfs(root).f_frsize
    allocated = ((len(body)+block-1)//block)*block+2*block
    assert capacity() >= RESERVE+allocated
    with (out/name).open('xb') as f:
        f.write(body); f.flush(); os.fsync(f.fileno())
    sync_dir(out)
    assert capacity() >= RESERVE

memory()
if mode == 'prepare':
    assert not stage.exists() and not out.exists()
    before = identity(); rows = inventory()
    selected = [r.copy() for r in rows if r['size'] <= 4096]
    assert selected and sum(r['size'] for r in selected) <= 4*1024**2
    allowance = sum(r['size']+160 for r in selected)+8192+16384
    while selected and capacity() < allowance+RECEIPT+RESERVE:
        removed = selected.pop()
        allowance -= removed['size']+160
    assert selected, 'No independently verifiable batch fits the remaining reserve'
    assert capacity() >= allowance+RECEIPT+RESERVE, (capacity(),allowance)
    start_free = capacity()
    for r in selected: r['bodySHA256'] = hashlib.sha256(original(r)).hexdigest()
    stage.mkdir(mode=0o700); directory = stage/'objects/pack'; directory.mkdir(parents=True)
    out.mkdir(mode=0o700)
    with gzip.open(out/'INPUTS.json.gz','xb') as f:
        f.write(json.dumps({'identity':before,'inventory':rows,
              'selected':[{'oid':r['oid'],'bodySHA256':r['bodySHA256']} for r in selected]},
              separators=(',',':')).encode())
    assert (out/'INPUTS.json.gz').stat().st_size <= INPUT_BUDGET
    with (out/'INPUTS.json.gz').open('rb') as f: os.fsync(f.fileno())
    sync_dir(out); sync_dir(out.parent)
    pack, idx = directory/'candidate.pack',directory/'candidate.idx'
    flags = ['pack-objects','--stdout','--no-reuse-object','--no-reuse-delta','--delta-base-offset',
             '--threads=1','--window=32','--window-memory=16m','--depth=16','--compression=6','--no-thin']
    with pack.open('xb') as f:
        p = subprocess.run(['git',*flags],cwd=repo,input=('\n'.join(r['oid'] for r in selected)+'\n').encode(),
                           stdout=f,stderr=subprocess.PIPE)
        assert p.returncode == 0,p.stderr.decode()
        f.flush(); os.fsync(f.fileno())
    git(['index-pack','--strict','--threads=1','-o',str(idx),str(pack)])
    with idx.open('rb') as f: os.fsync(f.fileno())
    for d in [directory,directory.parent,stage,root/'objects']: sync_dir(d)
    pair = checks(pack,idx,selected)
    assert pair['allocatedPair'] <= allowance and capacity() >= RESERVE+RECEIPT
    assert identity() == before and inventory() == rows
    for r in selected: assert hashlib.sha256(original(r)).hexdigest() == r['bodySHA256']
    write('PREPARED.json',{'pair':pair,'identity':before,'stage':str(stage),'reserve':RESERVE,
          'allowance':allowance,'selectedCount':len(selected),'selectedRawBytes':sum(r['size'] for r in selected),
          'selectedLooseAllocated':sum(r['metadata'][6] for r in selected),
          'freeBefore':start_free,'freeAfter':capacity(),'memoryHeadroom':memory(),
          'everyLooseEncodingRetained':True,'allSelectedRawObjectsVerified':True,
          'allUnselectedEncodingsSHA256AndMetadataUnchanged':True,'published':False})
    print(json.dumps({'prepared':True,**pair,'free':capacity()}))
elif mode in ('publish','finish'):
    data = json.loads(gzip.decompress((out/'INPUTS.json.gz').read_bytes()))
    rows,before = data['inventory'],data['identity']
    by_oid = {r['oid']:r for r in rows}
    selected = [{**by_oid[r['oid']],**r} for r in data['selected']]
    prepared = json.loads((out/'PREPARED.json').read_text())
    assert prepared['stage'] == str(stage)
    # This exact three-field receipt is created only after independent inspection.
    approval = json.loads((out/'INDEPENDENT-ACCEPTANCE.json').read_text())
    assert approval['preparedSHA256'] == digest_file(out/'PREPARED.json')
    assert re.fullmatch('[0-9a-f]{64}',approval['reviewSHA256'])
    assert approval['acceptedPackSHA256'] == prepared['pair']['packSHA256']
    checksum = prepared['pair']['gitChecksum']; dest = root/'objects/pack'
    target_pack,target_idx = dest/f'pack-{checksum}.pack',dest/f'pack-{checksum}.idx'
    if mode == 'publish':
        assert identity() == before and inventory() == rows
        assert checks(stage/'objects/pack/candidate.pack',stage/'objects/pack/candidate.idx',selected) == prepared['pair']
        assert capacity() >= RESERVE+RECEIPT
        keep = dest/f'pack-{checksum}.keep'
        with keep.open('xb') as f:
            f.write(b'Bounded verified preservation; retained historical objects; no GC authorization\n')
            f.flush(); os.fsync(f.fileno())
        os.link(stage/'objects/pack/candidate.pack',target_pack)
        os.link(stage/'objects/pack/candidate.idx',target_idx); sync_dir(dest)
        isolated = stage/'published/objects/pack'; isolated.mkdir(parents=True)
        # Same durable inodes, separate pack-only namespace; never writes through links.
        os.link(target_pack,isolated/target_pack.name); os.link(target_idx,isolated/target_idx.name)
        for d in [isolated,isolated.parent,isolated.parent.parent,stage]: sync_dir(d)
        assert checks(isolated/target_pack.name,isolated/target_idx.name,selected) == prepared['pair']
        after = identity()
        assert {k:v for k,v in after.items() if k!='packs'} == {k:v for k,v in before.items() if k!='packs'}
        for name,m in before['packs'].items(): assert after['packs'][name] == m
        assert set(after['packs']) == set(before['packs'])|{target_pack.name,target_idx.name,keep.name}
        assert inventory() == rows and capacity() >= RESERVE
        write('PUBLISHED.json',{'pair':prepared['pair'],'identity':after,'freeAfter':capacity(),
              'everyLooseEncodingRetained':True,'allPublishedRawObjectsVerified':True})
        print(json.dumps({'published':True,'objects':len(selected),'looseInputsRetained':True}))
    else:
        published = json.loads((out/'PUBLISHED.json').read_text())
        # A distinct review of the exact durable published pair precedes unlink.
        publication_approval = json.loads((out/'INDEPENDENT-PUBLICATION-ACCEPTANCE.json').read_text())
        assert publication_approval['publishedSHA256'] == digest_file(out/'PUBLISHED.json')
        assert publication_approval['acceptedPackSHA256'] == prepared['pair']['packSHA256']
        assert re.fullmatch('[0-9a-f]{64}',publication_approval['reviewSHA256'])
        assert identity() == published['identity'] and inventory() == rows
        isolated = stage/'published/objects/pack'
        assert checks(isolated/target_pack.name,isolated/target_idx.name,selected) == prepared['pair']
        assert capacity() >= RESERVE
        for r in selected:
            assert hashlib.sha256(original(r)).hexdigest() == r['bodySHA256']
        free = capacity(); dirs = set()
        for r in selected:
            p = root/'objects'/r['oid'][:2]/r['oid'][2:]
            assert meta(p) == r['metadata'] and digest_file(p) == r['encodedSHA256']
            p.unlink(); dirs.add(p.parent)
        for d in dirs: sync_dir(d)
        assert checks(isolated/target_pack.name,isolated/target_idx.name,selected) == prepared['pair']
        assert identity() == published['identity']
        assert inventory() == [r for r in rows if r['oid'] not in {s['oid'] for s in selected}]
        assert capacity() >= RESERVE and capacity() > free
        write('FINISHED.json',{'pair':prepared['pair'],'objectsRetained':len(selected),
              'redundantLooseEncodingsRemoved':len(selected),'freeBeforeUnlink':free,'freeAfter':capacity(),
              'measuredFreeRecovery':capacity()-free,'allSelectedPublishedRawObjectsVerified':True,
              'allUnselectedEncodedBytesAndMetadataUnchanged':True,'refsAndOldPackMetadataUnchanged':True,
              'freeMeasurementScope':'Counters precede this bounded receipt allocation; reserve is checked again after fsynced write. Metadata receipts exclude access times changed by reads.',
              'scope':'Git storage encoding replacement only; no source/history/ref/archive/art/review/dataset deletion; no full fsck or all-loose raw-body claim.'})
        print(json.dumps({'finished':True,'objectsRetained':len(selected),'free':capacity()}))
else: raise AssertionError('Unknown operation')
