"""SOURCE ONLY: one350s outer monotonic clock,337s work cutoff. No execution grant."""
import time
ENTRY=time.monotonic();DEADLINE=ENTRY+350;CUTOFF=ENTRY+337
import os,sys,json,hashlib,pathlib,subprocess,signal,select
ROOT=pathlib.Path(__file__).resolve().parent
M=1048576;WORK=896*M;RESERVE=512*M
def remaining(reserve=0):return max(0,DEADLINE-time.monotonic()-reserve)
def memory():
    p=pathlib.Path('/sys/fs/cgroup');cur=int((p/'memory.current').read_text());limit=(p/'memory.max').read_text().strip()
    if limit=='max':raise RuntimeError('Finite cgroup bound required')
    return cur,int(limit)
def alive(pid):
    try:os.killpg(pid,0);return True
    except ProcessLookupError:return False
def metrics(packet,initial,maximum):
    cur,limit=memory();v=os.statvfs(packet);rows={str(p.relative_to(packet)):p.stat().st_size for p in packet.rglob('*') if p.is_file()};total=sum(rows.values());free=v.f_bavail*v.f_frsize;fails=[]
    if max(0,cur-initial)>WORK or limit!=maximum or maximum-cur<RESERVE:fails.append('896MiB work/512MiB reserve')
    if total>71*M:fails.append('71MiB inclusive physical proof')
    if rows.get('JOURNAL.jsonl',0)>M:fails.append('1MiB journal')
    if rows.get('PROCESS.log',0)>M:fails.append('1MiB process log')
    if rows.get('PROCESS-FIRST-OVERFLOW.bin',0)>65536:fails.append('64KiB first overflow')
    if sum(n for k,n in rows.items() if k.endswith('.jpg'))>2*M or sum(k.endswith('.jpg') for k in rows)>4:fails.append('4JPEG/2MiB')
    if free<64*M:fails.append('64MiB review disk margin')
    if time.monotonic()>=DEADLINE:fails.append('350s outer deadline')
    return {'current':cur,'maximum':limit,'delta':max(0,cur-initial),'physicalProofBytes':total,'files':rows,'diskFreeBytes':free,'elapsedSeconds':time.monotonic()-ENTRY,'failures':fails}
def run():
    grant_path=pathlib.Path(sys.argv[1]);b=grant_path.read_bytes();g=json.loads(b)
    if not all(g.get(k) is True for k in ['enabled','rootMethodReviewed','independentTechnicalSourceReviewed','bFullBodyReviewed']):raise RuntimeError('Runtime boundary closed')
    if g.get('wholeBudgetSeconds')!=350 or g.get('observationSeconds')!=300:raise RuntimeError('Wrong method clocks')
    mb=(ROOT/'MANIFEST.json').read_bytes()
    if hashlib.sha256(mb).hexdigest()!=g['methodManifestSHA256']:raise RuntimeError('Wrong source manifest')
    for name,pin in json.loads(mb)['files'].items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=pin['sha256']:raise RuntimeError('Source changed')
    packet=pathlib.Path(g['actualPacket'])
    if not str(packet).startswith('/workspace/scratch/starter-first300-observer-actual-'):raise RuntimeError('Wrong packet')
    packet.mkdir(exist_ok=False);cur,maximum=memory();v=os.statvfs(packet);free=v.f_bavail*v.f_frsize
    admitted=maximum-cur>=WORK+RESERVE and free>=135*M and time.monotonic()<CUTOFF
    admission={'admitted':admitted,'work':WORK,'reserve':RESERVE,'initial':{'current':cur,'maximum':maximum,'diskFree':free},'wholeBudgetSeconds':350,'observationSeconds':300,'outerEntryMonotonicSeconds':ENTRY,'workerCutoffMonotonicSeconds':CUTOFF,'outerDeadlineMonotonicSeconds':DEADLINE,'setupElapsedSeconds':time.monotonic()-ENTRY,'grantSHA256':hashlib.sha256(b).hexdigest(),'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}
    (packet/'ADMISSION.json').write_text(json.dumps(admission)+'\n')
    if not admitted:raise RuntimeError('Fresh896+512 admission rejected')
    db=pathlib.Path('/workspace/scratch/starter-opening-runtime-dependency-evidence-r3/DEPENDENCIES.json').read_bytes()
    if hashlib.sha256(db).hexdigest()!=g['dependenciesSHA256']:raise RuntimeError('Dependency manifest changed')
    deps=json.loads(db)
    if deps['nodePath']!='/opt/codex/runtimes/codex-primary-runtime/dependencies/node/bin/node':raise RuntimeError('Unexpected Node path')
    child=None;reason=None;peak=cur;received=0;output_bytes=0;overflow_bytes=0;eof=False;stream_hash=hashlib.sha256();term=False;kill=False;errors=[]
    try:
        if time.monotonic()>=CUTOFF:raise RuntimeError('Setup exhausted work budget')
        child=subprocess.Popen([deps['nodePath'],str(ROOT/'observe.mjs'),str(grant_path),str(packet)],start_new_session=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        os.set_blocking(child.stdout.fileno(),False)
        with (packet/'PROCESS.log').open('wb') as out:
            while not eof:
                sample=metrics(packet,cur,maximum);peak=max(peak,sample['current'])
                if sample['failures']:reason='; '.join(sample['failures'])
                if time.monotonic()>=CUTOFF:reason=reason or '337s work cutoff;13s cleanup/receipt reserve'
                if reason:break
                ready,_,_=select.select([child.stdout],[],[],max(0,min(0.2,CUTOFF-time.monotonic())))
                if not ready:continue
                chunk=os.read(child.stdout.fileno(),65536)
                if not chunk:eof=True;break
                received+=len(chunk);stream_hash.update(chunk);room=max(0,M-output_bytes);prefix=chunk[:room];out.write(prefix);out.flush();output_bytes+=len(prefix)
                extra=chunk[len(prefix):]
                if extra:
                    (packet/'PROCESS-FIRST-OVERFLOW.bin').write_bytes(extra);overflow_bytes=len(extra)
                    reason='Process log cap exceeded; first received overflow preserved; unread tail possible';break
                # Continue through EOF after child exit; no log-completeness claim from exit alone.
    except BaseException as e:reason=str(e)
    finally:
        if child:
            if eof and child.poll() is None and remaining(5)>0:
                try:child.wait(timeout=min(1,remaining(5)))
                except subprocess.TimeoutExpired:pass
            if child.poll() is None and remaining(5)>0:
                try:os.killpg(child.pid,signal.SIGTERM);term=True
                except ProcessLookupError:pass
                except OSError as e:errors.append(str(e))
                try:child.wait(timeout=min(8,remaining(5)))
                except subprocess.TimeoutExpired:pass
            if alive(child.pid):
                try:os.killpg(child.pid,signal.SIGKILL);kill=True
                except ProcessLookupError:pass
                except OSError as e:errors.append(str(e))
            if child.poll() is None and remaining(2)>0:
                try:child.wait(timeout=min(3,remaining(2)))
                except subprocess.TimeoutExpired:errors.append('Child exit unconfirmed within remaining deadline')
            while alive(child.pid) and remaining(2)>0:select.select([],[],[],min(0.05,remaining(2)))
            group_closed=not alive(child.pid);child.stdout.close()
        else:group_closed=True
        result={}
        try:result=json.loads((packet/'RESULT.json').read_text())
        except (OSError,ValueError):errors.append('Worker RESULT unavailable/partial')
        normal_worker=result.get('browser')=='CLOSED' and result.get('server')=='CLOSED' and not result.get('closeErrors') and not result.get('mechanicalFailures')
        normal=reason is None and child is not None and child.returncode==0 and eof and group_closed and normal_worker and not term and not kill
        receipt={'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'outerEntryMonotonicSeconds':ENTRY,'elapsedSeconds':time.monotonic()-ENTRY,'workerCutoffSeconds':337,'reason':reason,'exitCode':None if child is None else child.returncode,'peakCgroupBytes':peak,'peakDeltaBytes':max(0,peak-cur),'ownedProcessGroup':None if child is None else child.pid,'termSent':term,'killSent':kill,'processGroupConfirmedAbsent':group_closed,'normalWorkerBrowserServerClosed':normal_worker,'closedNormally':normal,'cleanupErrors':errors,'receivedStreamBytes':received,'receivedStreamSHA256':stream_hash.hexdigest(),'processLogBytes':output_bytes,'firstOverflowBytes':overflow_bytes,'firstOverflowCapBytes':65536,'receivedEOF':eof,'unreadTailPossible':not eof,'completeLogClaim':eof and overflow_bytes==0,'humanFunAccepted':False,'terminalAccountingRequired':True}
        (packet/'SUPERVISOR-CLOSURE.json').write_text(json.dumps(receipt,indent=2)+'\n')
        final=metrics(packet,cur,maximum);final['closedNormally']=normal;final['completed300']=result.get('completed300') is True;final['finalMethodPass']=normal and final['completed300'] and not errors and not final['failures'];final['inclusiveBytesIncludingThisReceipt']=0
        for _ in range(6):
            (packet/'FINAL-ACCOUNTING.json').write_text(json.dumps(final,indent=2)+'\n');measured=metrics(packet,cur,maximum)
            if measured['physicalProofBytes']==final['inclusiveBytesIncludingThisReceipt']:break
            final['inclusiveBytesIncludingThisReceipt']=measured['physicalProofBytes']
        post=metrics(packet,cur,maximum);terminal_pass=final['finalMethodPass'] and not post['failures'] and time.monotonic()<DEADLINE
        if not terminal_pass:
            final['finalMethodPass']=False;final['postWriteFailureMeasurement']=post;(packet/'FINAL-ACCOUNTING.json').write_text(json.dumps(final,indent=2)+'\n')
        return 0 if terminal_pass else 2
if __name__=='__main__':sys.exit(run())
