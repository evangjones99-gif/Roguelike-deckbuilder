import hashlib,json,os,pathlib,resource,stat
repo=pathlib.Path('/workspace/Roguelike-deckbuilder')
base=pathlib.Path('/workspace/scratch')
action=base/'frozen128-canonical-media-sharing-action-root-r1'
guard=base/'frozen128-canonical-media-sharing-action-guard-root-r1'
pre=base/'frozen128-canonical-media-sharing-independent-r1'
out=base/'frozen128-canonical-media-sharing-post-independent-r1'
pins=[]
def sha(p):
    fd=os.open(p,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW);h=hashlib.sha256()
    try:
        before=os.fstat(fd);assert stat.S_ISREG(before.st_mode)
        while True:
            b=os.read(fd,65536)
            if not b:break
            h.update(b)
        after=os.fstat(fd);assert before==after
    finally:os.close(fd)
    return h.hexdigest()
def pin(p,expected=None):
    h=sha(p)
    if expected:assert h==expected,str(p)
    s=p.stat();r={'path':str(p),'sha256':h,'bytes':s.st_size,'allocatedBytes':s.st_blocks*512};pins.append(r)
    return r
def load(p,expected=None):
    pin(p,expected)
    fd=os.open(p,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW)
    with os.fdopen(fd,'r') as f:return json.load(f)
def identity(p):
    s=p.stat(follow_symlinks=False);assert stat.S_ISREG(s.st_mode)
    return {'dev':s.st_dev,'ino':s.st_ino,'nlink':s.st_nlink,'bytes':s.st_size,'blocks':s.st_blocks,
        'mode':s.st_mode,'uid':s.st_uid,'gid':s.st_gid,'mtimeNs':s.st_mtime_ns,
        'ctimeNs':s.st_ctime_ns,'atimeNs':s.st_atime_ns,'sha256':sha(p)}
proposal=load(base/'frozen128-canonical-media-sharing-proposal-root-r1/PROPOSAL.json','db8ebb732282149270e9bd87bb1aef191f083b67a06c47802bdc3ea03a004938')
gate=load(pre/'R2-GATE.json','39e55b9e7507ff3f5664d2ad00172a54a4025914398ac074a9c37b9f61ffc371')
prior=load(pre/'BODY-AND-METADATA-PROOF.json')
judgment=load(base/'frozen128-canonical-media-sharing-producer-judgment-root-r1.json','6f08a02730d44ad5cfca01f0c184595bc6a5860e01ea99feb8e74d75d47ba265')
push=load(base/'ready-opening-checkpoint-push-root-r1/PUSH-CONFIRMED.json',judgment['pushProofSHA256'])
before=load(action/'BEFORE.json');result=load(action/'RESULT.json')
pin(base/'frozen128-canonical-media-sharing-proposal-root-r1/share-r2.py',gate['actionSHA256'])
pin(base/'guard-retirement-bounded-journal-root-r1.py',gate['freeingOnlyGuardSHA256'])
assert gate['decision']=='ACCEPT_EXACT_PHYSICAL_SHARING_AND_ACTION_SOURCE'
assert before['groups']==proposal['groups'] and before['judgment']==judgment
assert before['proposalSHA256']==judgment['proposalSHA256']==gate['proposalSHA256']
assert before['gateSHA256']==judgment['gateSHA256']==pins[1]['sha256']
assert judgment['actionSHA256']==gate['actionSHA256'] and judgment['guardSHA256']==gate['freeingOnlyGuardSHA256']
commit='dc67551863e18b0a11afdf4c5276f9747ddc56bb'
assert judgment['commit']==result['commit']==result['remoteConfirmed']==commit
assert judgment['pushConfirmed'] and judgment['writersClosed'] and judgment['noUniqueMaterialRetired']
assert judgment['approvedGroups']==50 and judgment['approvedRecipients']==100
# Retain all push fields for explicit caller-record interpretation; no new Git/network commands.
assert commit in json.dumps(push)
assert result['normal'] and result['groups']==50 and result['recipients']==100 and result['allPathsAndBytesPreserved']
assert result['oldGrossAllocationBytes']==30638080
assert result['initialFreeBytes']==before['initialFreeBytes']==64327680
assert result['finalFreeBytes']==94674944 and result['observedNetRecoveredBytes']==30347264
assert result['finalFreeBytes']-result['initialFreeBytes']==result['observedNetRecoveredBytes']
pin(pathlib.Path(proposal['holdPath']),proposal['holdSHA256'])
frozen=load(pathlib.Path(proposal['freezePath']),proposal['freezeSHA256'])
selected=load(base/'ready-default-build-root-r1/RUNTIME-FREEZE.json',prior['selectedFreezeSHA256'])
assert selected['sourceDigest']==proposal['selectedSourceDigest'] and selected['outputsDigest']==proposal['selectedOutputsDigest']
pin(action/'JOURNAL.jsonl')
fd=os.open(action/'JOURNAL.jsonl',os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW)
with os.fdopen(fd,'r') as f:journal=[json.loads(x) for x in f]
assert len(journal)==300
anchorIDs={(g['anchorBefore']['dev'],g['anchorBefore']['ino']):[] for g in proposal['groups']}
scanned=0
for root,dirs,names in os.walk('/workspace',followlinks=False):
    dirs[:]=[d for d in dirs if d not in ['node_modules','.git','__pycache__']]
    for name in names:
        p=pathlib.Path(root)/name
        try:s=p.stat(follow_symlinks=False)
        except FileNotFoundError:continue
        scanned+=1;assert scanned<200000
        key=(s.st_dev,s.st_ino)
        if stat.S_ISREG(s.st_mode) and key in anchorIDs:anchorIDs[key].append(str(p))
groups=[];traceReceipts=[];modeChanges=0;mtimeChanges=0
for gi,g in enumerate(proposal['groups']):
    a=pathlib.Path(g['anchor']);now=identity(a);old=g['anchorBefore'];key=(now['dev'],now['ino'])
    for k in ['dev','ino','bytes','blocks','mode','uid','gid','mtimeNs','sha256']:assert now[k]==old[k],(str(a),k)
    assert now['nlink']==old['nlink']+2 and now['ctimeNs']>old['ctimeNs']
    assert not os.listxattr(a,follow_symlinks=False)
    oldaliases=prior['groups'][gi]['knownCanonicalAliases']
    expected=set(oldaliases+[r['path'] for r in g['recipients']])
    assert set(anchorIDs[key])==expected and len(expected)==now['nlink']
    grecord={'anchor':str(a),'anchorObserved':now,'allCurrentAliases':sorted(expected),'recipients':[]}
    for ri,r in enumerate(g['recipients']):
        p=pathlib.Path(r['path']);live=identity(p);assert live==now,(str(p),'shared identity mismatch')
        assert not os.listxattr(p,follow_symlinks=False)
        assert not p.with_name(p.name+'.reviewed-share-tmp-r1').exists()
        start,prepared,complete=journal[(gi*2+ri)*3:(gi*2+ri)*3+3]
        assert [x['phase'] for x in [start,prepared,complete]]==['BEFORE','PREPARED','COMPLETE']
        assert all(x['group']==gi and x['recipient']==ri for x in [start,prepared,complete])
        assert start['path']==complete['path']==str(p) and start['anchor']['sha256']==old['sha256']
        assert prepared['temp']==start['temp']==str(p.with_name(p.name+'.reviewed-share-tmp-r1'))
        assert start['old']['dev']==r['before']['dev'] and start['old']['ino']==r['before']['ino']
        assert start['old']['nlink']==2-ri
        for k in ['bytes','blocks','mode','uid','gid','mtimeNs','sha256']:assert start['old'][k]==r['before'][k]
        if ri==0:assert start['old']['ctimeNs']==r['before']['ctimeNs']
        assert prepared['identity']['nlink']==old['nlink']+ri+1
        for obj in [prepared['identity'],complete['after'],complete['anchor']]:
            for k in ['dev','ino','bytes','blocks','mode','uid','gid','mtimeNs','sha256']:assert obj[k]==now[k],(str(p),k)
        assert complete['after']==complete['anchor']
        assert complete['after']['nlink']==old['nlink']+ri+1
        if ri==1:assert complete['after']['ctimeNs']==now['ctimeNs']
        mtimeChanges+=live['mtimeNs']!=r['before']['mtimeNs'];modeChanges+=live['mode']!=r['before']['mode']
        grecord['recipients'].append({'path':str(p),'liveBodyAndIdentityMatchAnchor':True,
            'oldInodeReleased':r['before']['ino'],'mtimeChanged':live['mtimeNs']!=r['before']['mtimeNs'],
            'modeValueChanged':live['mode']!=r['before']['mode'],'journalRowsVerified':[(gi*2+ri)*3+i for i in range(3)],
            'tempAbsent':True})
    for alias in oldaliases:
        if alias!=str(a):
            live=identity(pathlib.Path(alias));assert live==now
            traceReceipts.append({'path':alias,'liveIdentity':live,'sameOriginalBody':True,'anchorNlinkDelta':2,'ctimeChanged':True})
    groups.append(grecord)
assert len(traceReceipts)==8 and modeChanges==0 and mtimeChanges==100
maps=[]
for label,freeze,sourceBase in [('frozen128',frozen,pathlib.Path(frozen['stage'])),('selectedCanonical',selected,repo),('selectedRetainedStage',selected,pathlib.Path(selected['stage']))]:
    for kind,root,entries in [('inputs',sourceBase,freeze['hashes']),('outputs',sourceBase/'dist',freeze['outputs'])]:
        for rel,expected in entries.items():assert sha(root/rel)==expected,(label,kind,rel)
        maps.append({'label':label,'kind':kind,'count':len(entries),'allBodiesMatch':True})
excluded=[]
for e in prior['excluded']:
    observed=[]
    for path,old in [(e['path'],e['publicObserved']),(e['distPath'],e['distObserved'])]:
        live=identity(pathlib.Path(path))
        for k in live:
            if k!='atimeNs':assert live[k]==old[k],(path,k)
        observed.append({'path':path,'live':live})
    excluded.append({'uniqueReady':True,'unchangedExceptUnclaimedAtime':True,'observed':observed})
controls=load(pre/'OLD-RECORD-RECEIPTS.json')
for r in [controls['preservationReceipt'],controls['archiveReceipt']]:pin(pathlib.Path(r['path']),r['sha256'])
admission=load(guard/'ADMISSION.json');gr=load(guard/'RESULT.json');pin(guard/'EXECUTION.log')
assert admission['admitted'] and admission['work']==128*1048576 and admission['reserve']==512*1048576
assert admission['initial']['free']>=16*1048576
assert admission['initial']['headroom']>=admission['work']+admission['reserve']
assert admission['command']==['python3',str(base/'frozen128-canonical-media-sharing-proposal-root-r1/share-r2.py'),str(base/'frozen128-canonical-media-sharing-proposal-root-r1/PROPOSAL.json'),str(pre/'R2-GATE.json'),str(base/'frozen128-canonical-media-sharing-producer-judgment-root-r1.json')]
assert gr['exit_code']==0 and gr['failure'] is None and gr['memory_events_before']==gr['memory_events_after']
rows=[gr['initial']]+gr['samples']+[gr['final']]
for row in rows:
    assert row['headroom']>=512*1048576 and max(0,row['current']-gr['initial']['current'])<=128*1048576
    assert row['free']>=1048576
bodyJournalAllocation=sum((action/n).stat().st_blocks*512 for n in ['BEFORE.json','JOURNAL.jsonl'])
proof={'decision':'ACCEPT_POST_SHARING_PRESERVATION_AND_CLOSURE','pins':pins,'pushRecorded':push,'groups':groups,
    'traceAliases':traceReceipts,'maps':maps,'uniqueReadyControls':excluded,
    'livePathsVerified':150,'recipientCount':100,'anchorCount':50,'traceAliasCount':8,
    'journalRecordCount':300,'allJournalRowsVerified':True,'all100TemporaryLinksAbsent':True,
    'mtimeChangedRecipients':mtimeChanges,'modeValueChangedRecipients':modeChanges,
    'all150CurrentXattrSetsEmpty':True,'allPhysicalAnchorLinkPathsAccounted':True,
    'guard':{'rowsIncludingInitialFinal':len(rows),'eventsUnchanged':True,'exitCode':gr['exit_code'],
        'peakObservedAggregateDelta':max(max(0,r['current']-gr['initial']['current']) for r in rows),
        'minimumHeadroom':min(r['headroom'] for r in rows),'minimumFreeBytes':min(r['free'] for r in rows),
        'closureScope':gr['scope']},
    'allocation':{'grossOld':30638080,'initialFree':64327680,'measuredFinalFreeBeforeResultWrite':94674944,
        'measuredNetRecovered':30347264,'differenceGrossVsNet':30638080-30347264,
        'allocatedBeforeAndJournal':bodyJournalAllocation,
        'resultAndGuardFilesAfterMeasuredWindowNotIncluded':True},
    'stalePhrase':{'originalRetained':True,'text':'No current transaction authorization.',
        'qualification':'Copied proposal-stage disclaimer in immutable actual RESULT limitations; actual r2 gate, pinned producer judgment, confirmed clean-current push and recorded action command establish transaction authorization. Do not rewrite original.'},
    'protectedScope':'Prior archive and preservation controls independently unchanged. Unique READY and all runtime/rights maps verified. Exact mutator only linked/replaced100 reviewed paths and new metadata files; protected archives/inputs/datasets/reviews/releases are outside mutation and alias sets. No new multigigabyte archive rehash or full Git logical coverage claim.',
    'readerMaxRssKiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    'limitations':'No actual action/Git/backend/Node/browser/images by reviewer. Sampled guard accounting is aggregate, closure is normal action/wait/complete journal/no temp residue, not universal unobserved-child proof. Shared inode/time/write and permission isolation losses remain. No whole-review atime equality claimed; O_NOATIME controlled reads preserve during-read metadata.'}
(out/'POST-PROOF.json').write_text(json.dumps(proof,indent=2)+'\n')
print(json.dumps({k:proof[k] for k in ['decision','livePathsVerified','journalRecordCount','maps','allocation','guard','readerMaxRssKiB']}))
