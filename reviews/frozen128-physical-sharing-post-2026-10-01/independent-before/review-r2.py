import ast,hashlib,json,os,pathlib,resource
out=pathlib.Path('/workspace/scratch/frozen128-canonical-media-sharing-independent-r1')
root=pathlib.Path('/workspace/scratch/frozen128-canonical-media-sharing-proposal-root-r1')
def read(p):
    fd=os.open(p,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW)
    try:
        before=os.fstat(fd);blocks=[]
        while True:
            b=os.read(fd,65536)
            if not b:break
            blocks.append(b)
        after=os.fstat(fd);assert before==after
    finally:os.close(fd)
    data=b''.join(blocks)
    return data,{'path':str(p),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'duringReadMetadataStable':True}
r1,r1receipt=read(root/'share.py');r2,r2receipt=read(root/'share-r2.py')
assert r1receipt['sha256']=='552668d636d65011f1faa51e7858c3e16e2eafedecd28df01085ee21526b3c60'
assert r2receipt['sha256']=='a2739ae5688d61238d3a125c4861aa8ebebaba9cbbb1d3b30fa8a2b82a43c748'
ast.parse(r2.decode()) # Do not execute/import the action.
guard,greceipt=read(pathlib.Path('/workspace/scratch/guard-retirement-bounded-journal-root-r1.py'))
ordinary,_=read(pathlib.Path('/workspace/scratch/guard-node-phase-r1.py'))
assert guard==ordinary.replace(b'initial[\'free\']>=64*1048576',b'initial[\'free\']>=16*1048576')
assert b"row['free']<1048576" in guard and b'reserve=512*1048576' in guard
proof=json.loads((out/'BODY-AND-METADATA-PROOF.json').read_text())
xattrs=[]
for group in proof['groups']:
    for p in [group['anchor']]+[r['path'] for r in group['recipients']]:
        names=os.listxattr(p,follow_symlinks=False)
        assert not names,(p,names)
        xattrs.append({'path':p,'names':names})
result={'r1ActionReceipt':r1receipt,'r2ActionReceipt':r2receipt,'syntaxParsedWithoutExecution':True,
    'guardReceipt':greceipt,'guardOnlyChangeFromOrdinary':'Initial available-disk admission64MiB→16MiB;512MiB reserve and1MiB runtime disk stop unchanged.',
    'reviewedActionScope':'Only exact freeing50groups/100recipients transaction after fresh current push and producer judgment;128MiB aggregate work; not a general lowdisk waiver.',
    'r2Repair':'Fsync evidence parent after mkdir, evidence directory after BEFORE/RESULT names, empty JOURNAL content/name before mutation, and recipient temp-link directory before PREPARED; existing post-replace recipient directory fsync retained.',
    'xattrPathsChecked':len(xattrs),'all150CurrentXattrSetsEmpty':True,
    'xattrScope':'Read current xattr name sets for proposed150 paths; no values exist to lose. No historical untouched-path xattr inventory claimed.',
    'readerMaxRssKiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
(out/'R2-SOURCE-RECEIPTS.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
