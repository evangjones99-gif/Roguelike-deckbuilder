import hashlib,json,os,pathlib,resource,stat
repo=pathlib.Path('/workspace/Roguelike-deckbuilder')
proposal=pathlib.Path('/workspace/scratch/frozen128-canonical-media-sharing-proposal-root-r1')
out=pathlib.Path('/workspace/scratch/frozen128-canonical-media-sharing-independent-r1')
def sha(p):
    fd=os.open(p,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW)
    h=hashlib.sha256()
    try:
        before=os.fstat(fd);assert stat.S_ISREG(before.st_mode)
        while True:
            b=os.read(fd,65536)
            if not b:break
            h.update(b)
        after=os.fstat(fd);assert before==after
    finally:os.close(fd)
    return h.hexdigest()
def identity(p):
    s=p.stat(follow_symlinks=False);assert stat.S_ISREG(s.st_mode)
    return {'dev':s.st_dev,'ino':s.st_ino,'nlink':s.st_nlink,'bytes':s.st_size,
      'blocks':s.st_blocks,'mode':s.st_mode,'uid':s.st_uid,'gid':s.st_gid,
      'mtimeNs':s.st_mtime_ns,'ctimeNs':s.st_ctime_ns,'atimeNs':s.st_atime_ns,'sha256':sha(p)}
p=proposal/'PROPOSAL.json';action=proposal/'share.py'
assert sha(p)=='db8ebb732282149270e9bd87bb1aef191f083b67a06c47802bdc3ea03a004938'
assert sha(action)=='552668d636d65011f1faa51e7858c3e16e2eafedecd28df01085ee21526b3c60'
j=json.loads(p.read_text())
assert len(j['groups'])==50 and j['recipientCount']==100
assert sha(pathlib.Path(j['holdPath']))==j['holdSHA256']
assert sha(pathlib.Path(j['freezePath']))==j['freezeSHA256']
anchor_ids={(g['anchorBefore']['dev'],g['anchorBefore']['ino']):[] for g in j['groups']}
scanned=0
for base,dirs,names in os.walk('/workspace',followlinks=False):
    dirs[:]=[d for d in dirs if d not in ['node_modules','.git','__pycache__']]
    for name in names:
        q=pathlib.Path(base)/name
        try:s=q.stat(follow_symlinks=False)
        except FileNotFoundError:continue
        scanned+=1;assert scanned<200000
        key=(s.st_dev,s.st_ino)
        if stat.S_ISREG(s.st_mode) and key in anchor_ids:anchor_ids[key].append(str(q))
checks=[];anchors=set();oldinodes=set();paths=set();modeChanges=[];mtimeChanges=0;gross=0
knownAliases=[]
for g in j['groups']:
    a=pathlib.Path(g['anchor']);ai=identity(a);aid=(ai['dev'],ai['ino'])
    assert aid not in anchors;anchors.add(aid)
    assert len(g['recipients'])==2
    group={'anchor':str(a),'anchorObserved':ai,'recipients':[]}
    for r in g['recipients']:
        rp=pathlib.Path(r['path']);ri=identity(rp)
        assert str(rp) not in paths;paths.add(str(rp))
        for k,v in r['before'].items():
            if k!='atimeNs':assert ri[k]==v,(str(rp),k)
        assert ri['sha256']==ai['sha256'] and ri['bytes']==ai['bytes']
        assert ri['nlink']==2 and ri['dev']==ai['dev'] and ri['ino']!=ai['ino']
        group['recipients'].append({'path':str(rp),'observed':ri,
            'metadataExceptAtimeMatchesProposal':True,
            'atimeDifferenceFromProposalNs':ri['atimeNs']-r['before']['atimeNs']})
        if ri['mode']!=ai['mode']:modeChanges.append({'path':str(rp),'old':ri['mode'],'successor':ai['mode']})
        mtimeChanges+=ri['mtimeNs']!=ai['mtimeNs']
    one,two=group['recipients']
    oi=(one['observed']['dev'],one['observed']['ino'])
    assert oi==(two['observed']['dev'],two['observed']['ino']) and oi not in oldinodes
    oldinodes.add(oi)
    assert one['observed']['blocks']*512==g['oldAllocatedBytes'];gross+=g['oldAllocatedBytes']
    for k,v in g['anchorBefore'].items():
        if k!='atimeNs':assert ai[k]==v,(str(a),k)
    aliases=anchor_ids[aid]
    group['knownCanonicalAliases']=aliases
    group['allAnchorHardlinksAccountedByCanonicalAliases']=len(aliases)==ai['nlink']
    assert len(aliases)==ai['nlink'],(str(a),ai['nlink'],aliases)
    knownAliases.extend(aliases);checks.append(group)
assert gross==j['grossOldAllocationBytes']==30638080
assert len(anchors)==len(oldinodes)==50 and len(paths)==100
frozen=json.loads(pathlib.Path(j['freezePath']).read_text())
selectedPath=pathlib.Path('/workspace/scratch/ready-default-build-root-r1/RUNTIME-FREEZE.json')
selected=json.loads(selectedPath.read_text())
assert selected['sourceDigest']==j['selectedSourceDigest'] and selected['outputsDigest']==j['selectedOutputsDigest']
maps=[]
for label,freeze,sourceBase in [('frozen128',frozen,pathlib.Path(frozen['stage'])),
                               ('selectedCanonical',selected,repo),
                               ('selectedRetainedStage',selected,pathlib.Path(selected['stage']))]:
    for kind,base,entries in [('inputs',sourceBase,freeze['hashes']),('outputs',sourceBase/'dist',freeze['outputs'])]:
        for rel,expected in entries.items():assert sha(base/rel)==expected,(label,kind,rel)
        maps.append({'label':label,'kind':kind,'count':len(entries),'allBodiesMatch':True})
excluded=[]
for e in j['excluded']:
    q=pathlib.Path(e['path']);d=pathlib.Path(e['distPath'])
    qi=identity(q);di=identity(d)
    assert qi['sha256']==di['sha256']=='ce0897f80894e2fd3196605af1dfa5b9a4a5209fd2d5178aaa71a70f721fc441'
    assert str(q) not in paths and str(d) not in paths
    assert not (repo/'public'/'art'/q.name).exists()
    excluded.append({'path':str(q),'distPath':str(d),'publicObserved':qi,'distObserved':di,'excluded':True})
result={'proposalSHA256':sha(p),'actionSHA256':sha(action),'holdSHA256':j['holdSHA256'],
    'frozenFreezeSHA256':j['freezeSHA256'],'selectedFreezePath':str(selectedPath),
    'selectedFreezeSHA256':sha(selectedPath),'selectedSourceDigest':selected['sourceDigest'],
    'selectedOutputsDigest':selected['outputsDigest'],'groups':checks,'maps':maps,'excluded':excluded,
    'groupCount':50,'recipientCount':100,'proposedPathsAndAnchors':150,'grossOldAllocationBytes':gross,
    'modeChanges':modeChanges,'recipientMtimeChangesExpected':mtimeChanges,
    'allKnownAnchorHardlinksAccounted':True,'readerMaxRssKiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    'aliasInventory':{'method':'Read-only walk of /workspace, no symlink following, skip node_modules/.git/__pycache__, no content reads in walk. Exact discovered regular hardlink counts equal kernel nlink for every anchor. Controlled symlink mounts are exposures, not additional hardlinks.','filesLstatCount':scanned},
    'limitations':'No actual sharing/action, images or media mutation. All link aliases share metadata after linking. Workflow hold is not OS isolation. Atime equality with proposal is excluded; controlled O_NOATIME identity reads preserve during-read metadata. Existing textual source reads can update atime. Source/body equality does not preserve old physical inode/ctime/write isolation or full Git logical archive coverage.'}
(out/'BODY-AND-METADATA-PROOF.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'pathsAndAnchors':150,'groups':50,'gross':gross,'maps':maps,
    'modeChanges':len(modeChanges),'mtimeChanges':mtimeChanges,'maxrssKiB':result['readerMaxRssKiB']}))
