"""Independent byte verifier. Streams archive/originals/parts; never extracts or runs members."""
from pathlib import Path,PurePosixPath
import collections,datetime,gzip,hashlib,json,resource,stat,tarfile
ROOT=Path('/workspace/scratch/first300-preservation-root-r1')
OWN=Path('/workspace/scratch/first300-preservation-technical-r1')
CHUNK=65536
def identity(p):
    n=p.stat().st_size;s=hashlib.sha256();g=hashlib.sha1(b'blob '+str(n).encode()+b'\0')
    with p.open('rb') as f:
        for b in iter(lambda:f.read(CHUNK),b''):s.update(b);g.update(b)
    return {'bytes':n,'sha256':s.hexdigest(),'gitBlobSHA1':g.hexdigest()}
def main():
    ib=(ROOT/'INDEX.json').read_bytes();index=json.loads(ib);archive=ROOT/'first300-evidence.tar.gz'
    ai=identity(archive);assert ai['bytes']==1358008==index['archiveBytes'];assert ai['sha256']==index['archiveSHA256']=='bfe66ad23dff2179e894016ce77e110e76c7c4f60b74e2ca00b806d29b67d025'
    families=index['families'];assert len(families)==len(set(families))==29
    members=index['members'];assert len(members)==185
    table={x['member']:x for x in members};assert len(table)==185
    actual_namespace=[]
    for family in families:
        p=Path('/workspace/scratch')/family;assert p.is_dir() and not p.is_symlink()
        for f in p.rglob('*'):
            assert not f.is_symlink(),'Unreviewed symlink '+str(f)
            if f.is_file():actual_namespace.append(family+'/'+f.relative_to(p).as_posix())
    assert sorted(actual_namespace)==sorted(table),'Full29-family namespace differs'
    for name,row in table.items():
        q=PurePosixPath(name);assert not q.is_absolute() and all(x not in ['.','..',''] for x in q.parts)
        assert q.parts[0] in families;assert row['originalPath']=='/workspace/scratch/'+name
    # Read gzip fully to EOF independently: validates all member CRC/trailer data.
    uncompressed=hashlib.sha256();plain_bytes=0
    with gzip.open(archive,'rb') as gz:
        for b in iter(lambda:gz.read(CHUNK),b''):plain_bytes+=len(b);uncompressed.update(b)
    seen=set();unique_hashes=set();body_bytes=0;normalized=[];metadata_mismatches=[]
    with gzip.open(archive,'rb') as gz:
        with tarfile.open(fileobj=gz,mode='r|',ignore_zeros=True) as tf:
            for member in tf:
                assert member.isfile() and not member.islnk() and not member.issym(),'Nonregular TAR member'
                assert member.name in table and member.name not in seen,'Unexpected/duplicate TAR name'
                seen.add(member.name);row=table[member.name];assert member.size==row['bytes']
                assert member.uid==member.gid==member.mtime==0 and member.mode==0o644,'Unexpected normalized TAR metadata'
                original=Path(row['originalPath']);st=original.lstat();assert stat.S_ISREG(st.st_mode)
                observed={'device':st.st_dev,'inode':st.st_ino,'mode':st.st_mode,'nlink':st.st_nlink,'mtimeNs':str(st.st_mtime_ns),'ctimeNs':str(st.st_ctime_ns)}
                if observed!=row['metadataObserved']:metadata_mismatches.append(member.name)
                s=hashlib.sha256();g=hashlib.sha1(b'blob '+str(member.size).encode()+b'\0');n=0
                body=tf.extractfile(member) # Streaming member reader; no extraction to filesystem.
                assert body is not None
                with original.open('rb') as old:
                    for b in iter(lambda:body.read(CHUNK),b''):
                        assert old.read(len(b))==b,'Direct original/member byte mismatch';n+=len(b);s.update(b);g.update(b)
                    assert old.read(1)==b''
                assert n==row['bytes'] and s.hexdigest()==row['sha256'] and g.hexdigest()==row['gitBlobSHA1']
                unique_hashes.add(s.hexdigest());body_bytes+=n
            # ignore_zeros prevents a second logical TAR after padding being omitted.
        while gz.read(CHUNK):pass
    assert seen==set(table)
    parts=index['parts'];assert len(parts)==21
    assembled=hashlib.sha256();part_bytes=0
    with archive.open('rb') as old:
        for i,row in enumerate(parts):
            assert row['path']==f'parts/part-{i:04d}.bin'
            p=ROOT/row['path'];assert p.is_file() and not p.is_symlink();got=identity(p)
            assert all(got[k]==row[k] for k in ['bytes','sha256','gitBlobSHA1']);assert got['bytes']==(65536 if i<20 else 47288)
            with p.open('rb') as part:
                for b in iter(lambda:part.read(CHUNK),b''):assert old.read(len(b))==b;assembled.update(b);part_bytes+=len(b)
        assert old.read(1)==b''
    assert part_bytes==ai['bytes'] and assembled.hexdigest()==ai['sha256']
    assert {p.name for p in (ROOT/'parts').iterdir()}=={Path(x['path']).name for x in parts}
    jpgs=[x for x in members if x['member'].endswith('.jpg')];saves=[x for x in members if '/save-' in x['member']]
    assert len(jpgs)==10
    outcomes={}
    for version in ['r2','r3','r4','r5']:
        p=Path('/workspace/scratch/starter-first300-observer-actual-'+version+'/RESULT.json');o=json.loads(p.read_text());assert str(p).removeprefix('/workspace/scratch/') in table
        outcomes[version]={'completed300':o['completed300'],'mechanicalFailures':o['mechanicalFailures'],'browser':o['browser'],'server':o['server']}
    assert all(not outcomes[v]['completed300'] for v in ['r2','r3','r4']);assert outcomes['r5']['completed300'] is True
    root_bytes=sum(p.stat().st_size for p in ROOT.rglob('*') if p.is_file());assert root_bytes==2812299 and root_bytes<12*1048576
    receipt={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'indexSHA256':hashlib.sha256(ib).hexdigest(),'archive':ai,'gzipFullStreamValidated':True,'decompressedTARBytes':plain_bytes,'decompressedTARSHA256':uncompressed.hexdigest(),'regularUniqueLogicalMembers':185,'uniqueBodySHA256Count':len(unique_hashes),'logicalBodyBytes':body_bytes,'fullNamespaceFamilies':families,'allCurrentOriginalBytesDirectlyCompared':True,'allCurrentOriginalPathsRetained':True,'currentMetadataObservationMismatches':metadata_mismatches,'normalizedMetadataNotRestoration':True,'orderedParts':21,'partBytes':part_bytes,'partsByteForByteArchiveMatch':True,'originalJPEGCount':10,'rawSavedStringFiles':len(saves),'emptyLogMembers':[x['member'] for x in members if x['bytes']==0 and x['member'].endswith('.log')],'outcomes':outcomes,'rootPhysicalBytesBeforeFutureMetadata':root_bytes,'rootPhysicalCapBytes':12*1048576,'reviewerMaxRSSKiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'ordinaryCapBytes':64*1048576,'reserveBytes':512*1048576,'extractedOrExecutedArchivedBodies':False,'sourceMeaningApproval':False}
    (OWN/'CHECKS.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:v for k,v in receipt.items() if k not in ['fullNamespaceFamilies','outcomes','emptyLogMembers']},indent=2))
if __name__=='__main__':main()
