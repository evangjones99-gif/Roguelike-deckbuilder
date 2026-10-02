from pathlib import Path
import os,json,hashlib,time,sys,subprocess,stat
S=Path('/workspace/scratch');R=Path('/workspace/Roguelike-deckbuilder')
proposal,proposal_sha,gate,gate_sha,judgment,judgment_sha,push,push_sha=sys.argv[1:]
KEYS=['st_dev','st_ino','st_mode','st_nlink','st_uid','st_gid','st_size','st_blocks','st_atime_ns','st_mtime_ns','st_ctime_ns']
def md(t):return {k:getattr(t,k) for k in KEYS}
def meta(p):return md(os.stat(p,follow_symlinks=False))
def sha(p):
    h=hashlib.sha256();fd=os.open(p,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW)
    with os.fdopen(fd,'rb') as f:
        for b in iter(lambda:f.read(65536),b''):h.update(b)
    return h.hexdigest()
def read(p):return json.loads(Path(p).read_text())
def syncdir(p):
    fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    try:os.fsync(fd)
    finally:os.close(fd)
def syncfd(fd):
    q=os.open('.',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd)
    try:os.fsync(q)
    finally:os.close(q)
def save(p,j):
    with p.open('x') as f:json.dump(j,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    syncdir(p.parent)
def parentfd(p):
    assert p.is_absolute()
    fd=os.open('/',os.O_PATH|os.O_DIRECTORY|os.O_NOFOLLOW)
    try:
        for component in p.parent.parts[1:]:
            assert component not in ('','.', '..')
            q=os.open(component,os.O_PATH|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd)
            os.close(fd);fd=q
        return fd
    except BaseException:os.close(fd);raise
def leafcheck(fd,name,expected,digest):
    before=md(os.stat(name,dir_fd=fd,follow_symlinks=False));assert before==expected and stat.S_ISREG(before['st_mode'])
    f=os.open(name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME,dir_fd=fd)
    try:
        assert md(os.fstat(f))==expected
        assert not os.listxattr('/proc/self/fd/'+str(f))
        h=hashlib.sha256()
        for b in iter(lambda:os.read(f,65536),b''):h.update(b)
        assert h.hexdigest()==digest and md(os.fstat(f))==expected
    finally:os.close(f)
    assert md(os.stat(name,dir_fd=fd,follow_symlinks=False))==expected
def absent(fd,name):
    try:os.stat(name,dir_fd=fd,follow_symlinks=False)
    except FileNotFoundError:return True
    return False
for p,h in [(proposal,proposal_sha),(gate,gate_sha),(judgment,judgment_sha),(push,push_sha)]:assert sha(p)==h,p
j=read(judgment);assert j['decision']=='AUTHORIZE_EXACT_THREE_PATH_PHYSICAL_SHARING_ONCE' and j['proposalSHA256']==proposal_sha and j['independentGateSHA256']==gate_sha
assert read(gate)['decision'].startswith('ACCEPT')
assert sha(Path(__file__))==j['methodSHA256'] and sha(R/'AGENTS.md')==j['holdSHA256']
map_path=S/'target-wait-default-promotion-root-r1/RESULT.json';assert sha(map_path)==j['selectedMapSHA256'];selected=read(map_path)
def verify_selected():
    for rel,h in selected['canonicalInputs'].items():assert sha(R/rel)==h,rel
    for rel,h in selected['canonicalOutputs'].items():assert sha(R/'dist'/rel)==h,rel
verify_selected()
protected=S/'retained-original-archives/preflight-bdf273-original-r4.zip';protected_before=meta(protected)
assert (protected_before['st_dev'],protected_before['st_ino'],protected_before['st_size'],protected_before['st_nlink'])==(27,678628,1856041104,1)
pushed=read(push);assert pushed['confirmed'] and pushed['clean'] and pushed['commit']==j['commit']
assert (R/'.git/refs/heads/codex/lanternbound-production').read_text().strip()==j['commit']
status=subprocess.run(['git','status','--porcelain'],cwd=R,text=True,capture_output=True,timeout=10);assert status.returncode==0 and not status.stdout,status.stdout
initial_free=os.statvfs(R).f_bavail*os.statvfs(R).f_frsize;assert initial_free>=56*1048576
cg=Path('/sys/fs/cgroup');assert int((cg/'memory.max').read_text())-int((cg/'memory.current').read_text())>=576*1048576
E=read(proposal);pairs=E['pairs'];assert len(pairs)==3
oldroot=S/'audio-host-independent-v08/independent/rebuilt-dist/art';anchors=R/'public/art'
assert E['candidateGroup']==str(oldroot)
assert {Path(x['candidate']['path']).name for x in pairs}=={'abbey-courtyard.png','tool-vignettes.png','hunter-portrait.png'}
handles=[]
try:
    for x in pairs:
        a=x['anchor'];b=x['candidate'];ap=Path(a['path']);bp=Path(b['path'])
        assert ap.parent==anchors and bp.parent==oldroot and ap.name==bp.name
        assert a['lstat']==a['fstat'] and b['lstat']==b['fstat'] and a['xattrs']==b['xattrs']=={}
        assert a['fstat']['st_nlink']==5 and b['fstat']['st_nlink']==1 and a['fstat']['st_dev']==b['fstat']['st_dev']==27
        assert a['sha256']==b['sha256']
        af=parentfd(ap)
        try:bf=parentfd(bp)
        except BaseException:os.close(af);raise
        handles.append((x,af,bf,ap,bp))
        leafcheck(af,ap.name,a['fstat'],a['sha256']);leafcheck(bf,bp.name,b['fstat'],b['sha256'])
        assert absent(bf,bp.name+'.root-share-second-r3.tmp')
    P=S/'second-three-retained-png-sharing-actual-root-r3';P.mkdir();syncdir(P.parent)
    save(P/'BEFORE.json',{'utcNs':time.time_ns(),'pairs':pairs,'initialFree':initial_free,'proposalSHA256':proposal_sha,'gateSHA256':gate_sha,'judgmentSHA256':judgment_sha,'pushSHA256':push_sha,'commit':j['commit']})
    log=P/'JOURNAL.jsonl'
    def journal(entry):
        with log.open('a') as f:f.write(json.dumps({'utcNs':time.time_ns(),**entry})+'\n');f.flush();os.fsync(f.fileno())
        syncdir(P)
    for x,af,bf,ap,bp in handles:
        tmp=bp.name+'.root-share-second-r3.tmp'
        leafcheck(af,ap.name,x['anchor']['fstat'],x['anchor']['sha256']);leafcheck(bf,bp.name,x['candidate']['fstat'],x['candidate']['sha256']);assert absent(bf,tmp)
        journal({'operation':'PRE_LINK','source':str(ap),'target':str(bp),'temp':str(bp.with_name(tmp))})
        os.link(ap.name,tmp,src_dir_fd=af,dst_dir_fd=bf,follow_symlinks=False);syncfd(bf)
        linked=md(os.stat(tmp,dir_fd=bf,follow_symlinks=False));now=md(os.stat(ap.name,dir_fd=af,follow_symlinks=False))
        assert linked==now and now['st_ino']==x['anchor']['fstat']['st_ino'] and now['st_nlink']==6
        leafcheck(af,ap.name,now,x['anchor']['sha256']);leafcheck(bf,tmp,now,x['anchor']['sha256'])
        assert md(os.stat(bp.name,dir_fd=bf,follow_symlinks=False))==x['candidate']['fstat']
        journal({'operation':'LINK_DURABLE','target':str(bp),'temp':str(bp.with_name(tmp))})
        os.replace(tmp,bp.name,src_dir_fd=bf,dst_dir_fd=bf);syncfd(bf)
        journal({'operation':'REPLACED_DURABLE','target':str(bp),'tempAbsent':absent(bf,tmp)})
        current=md(os.stat(ap.name,dir_fd=af,follow_symlinks=False))
        leafcheck(af,ap.name,current,x['anchor']['sha256']);leafcheck(bf,bp.name,current,x['anchor']['sha256'])
    verify_selected();assert meta(protected)==protected_before
    final_free=os.statvfs(R).f_bavail*os.statvfs(R).f_frsize
    result={'normal':True,'pairs':[{'candidate':str(bp),'canonical':str(ap),'sha256':x['anchor']['sha256'],'candidateMetadata':meta(bp),'canonicalMetadata':meta(ap)} for x,af,bf,ap,bp in handles],'grossAllocationBytes':sum(x['candidate']['fstat']['st_blocks']*512 for x in pairs),'windowFreeBefore':initial_free,'windowFreeAfterBeforeResultWrite':final_free,'netWindowGainBytes':final_free-initial_free,'allPathsBodiesKept':True,'allTempAbsent':all(absent(bf,bp.name+'.root-share-second-r3.tmp') for x,af,bf,ap,bp in handles),'losses':'Three private inodes/time/write isolation lost; anchors nlink5 to6 and ctime changes, one previous alias unresolved per anchor. No original-inode backup, no all-three atomicity, durable prefix only. All bytes/paths/provenance remain needed.','noOtherActionAuthorized':True}
    save(P/'RESULT.json',result);print(json.dumps({'normal':True,'gross':result['grossAllocationBytes'],'netWindowGain':result['netWindowGainBytes'],'freeBeforeResultWrite':final_free}))
finally:
    for x,af,bf,ap,bp in handles:os.close(af);os.close(bf)
