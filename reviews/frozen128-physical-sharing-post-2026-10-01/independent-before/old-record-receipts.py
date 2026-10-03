import hashlib,json,os,pathlib,resource,tarfile
root=pathlib.Path('/workspace/Roguelike-deckbuilder/reviews/reviewed-trace-media-alias-recovery-2026-10-01')
out=pathlib.Path('/workspace/scratch/frozen128-canonical-media-sharing-independent-r1')
def digest(p):
    fd=os.open(p,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW);h=hashlib.sha256()
    try:
        before=os.fstat(fd)
        while True:
            b=os.read(fd,65536)
            if not b:break
            h.update(b)
        after=os.fstat(fd);assert before==after
    finally:os.close(fd)
    return {'path':str(p),'bytes':after.st_size,'sha256':h.hexdigest(),'duringReadMetadataStable':True}
preservation=json.loads((root/'PRESERVATION.json').read_text())
archive=root/'EVIDENCE.tar.gz';receipt=digest(archive)
assert receipt['sha256']=='4af14b984f3bd1b6bc49288dfdd8a73c6466d7d89b6f3a6ca5eb8af8d5f6f7bc'
assert receipt['bytes']==25642
fd=os.open(archive,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW);plan=None
with os.fdopen(fd,'rb') as stream:
    with tarfile.open(fileobj=stream,mode='r|gz') as tar:
        for member in tar:
            if member.name.endswith('/PLAN.json'):
                assert member.size==8888
                with tar.extractfile(member) as f:data=f.read(9000)
                assert len(data)==8888 and hashlib.sha256(data).hexdigest()=='6699c2ce1aea8302f6de7ddcc7e160d835e2f09cc35073158a47fd92f5dac7be'
                plan={'member':member.name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
                break
assert plan
result={'preservationReceipt':digest(root/'PRESERVATION.json'),'archiveReceipt':receipt,'streamedOriginalPlanReceipt':plan,
    'originalsReportedRetained':preservation['originals_retained'],
    'scope':'Verify retained old metadata/archive body and exact archived original PLAN only; no whole27-body re-audit, archive extraction, old-path removal, Git coverage claim or alteration. Rights/provenance files are covered by frozen and selected byte maps in independent body proof.',
    'readerMaxRssKiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
(out/'OLD-RECORD-RECEIPTS.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
