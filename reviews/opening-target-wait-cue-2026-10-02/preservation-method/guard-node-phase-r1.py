import os,sys,time,json,pathlib,subprocess,signal

stage,packet,work_mb,*command=sys.argv[1:]
packet=pathlib.Path(packet);packet.mkdir(exist_ok=False)
work=int(work_mb)*1048576;reserve=512*1048576
cgroup=pathlib.Path('/sys/fs/cgroup')
def sample():
    current=int((cgroup/'memory.current').read_text())
    maximum=int((cgroup/'memory.max').read_text())
    return {'time_ns':time.time_ns(),'current':current,'maximum':maximum,'headroom':maximum-current,'free':os.statvfs(stage).f_bavail*os.statvfs(stage).f_frsize}
initial=sample();events_before=(cgroup/'memory.events').read_text();rows=[]
admission=initial['headroom']>=work+reserve and initial['free']>=64*1048576
(packet/'ADMISSION.json').write_text(json.dumps({'initial':initial,'work':work,'reserve':reserve,'command':command,'stage':stage,'admitted':admission,'memory_events_before':events_before},indent=2)+'\n')
if not admission:
    print('REFUSED',json.dumps(initial));sys.exit(75)
process=None;failure=None
try:
    with (packet/'EXECUTION.log').open('xb') as log:
        process=subprocess.Popen(command,cwd=stage,env={**os.environ,'NODE_OPTIONS':'--max-old-space-size=256'},stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        while process.poll() is None:
            row=sample();row['delta']=row['current']-initial['current'];rows.append(row)
            if row['headroom']<reserve or row['delta']>work or row['free']<1048576:
                failure={'kind':'resource stop','sample':row}
                os.killpg(process.pid,signal.SIGTERM)
                try:process.wait(timeout=5)
                except subprocess.TimeoutExpired:os.killpg(process.pid,signal.SIGKILL);process.wait()
                break
            time.sleep(.1)
        rc=process.wait();log.flush();os.fsync(log.fileno())
except BaseException as error:
    failure={'kind':'wrapper exception','error':repr(error)}
    if process and process.poll() is None:
        os.killpg(process.pid,signal.SIGTERM);process.wait()
    rc=76
result={'exit_code':rc,'failure':failure,'initial':initial,'final':sample(),'samples':rows,'memory_events_before':events_before,'memory_events_after':(cgroup/'memory.events').read_text(),'scope':'observed cgroup delta, not exclusive process attribution; all child group processes closed'}
(packet/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'packet':str(packet),'exit_code':rc,'failure':failure,'samples':len(rows),'minimum_headroom':min((r['headroom'] for r in rows),default=initial['headroom'])}))
sys.exit(rc if rc>=0 else 77)
