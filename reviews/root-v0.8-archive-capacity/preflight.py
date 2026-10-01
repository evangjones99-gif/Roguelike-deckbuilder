"""Measure immutable source compression without creating a milestone."""
import subprocess,json,os,time
from pathlib import Path
root=Path('/workspace/Roguelike-deckbuilder')
def git(*args):return subprocess.check_output(['git',*args],cwd=root).decode().strip()
commit=git('rev-parse','HEAD')
roots=[s for s in subprocess.check_output(['git','ls-tree','-z','--name-only',commit],cwd=root).decode().split('\0') if s and s!='releases']
def count(args,stdin=None):
 p=subprocess.Popen(args,cwd=root,stdin=subprocess.PIPE if stdin else subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 if stdin:p.stdin.write(stdin);p.stdin.close()
 total=0
 while block:=p.stdout.read(1048576):total+=len(block)
 err=p.stderr.read();assert p.wait()==0,err
 return total
zipbytes=count(['git','archive','--format=zip',commit,'--',*roots])
# Bundle uses the same reachable closure. Compression/thread timing can vary;
# this streamed pack is a measured estimate, with a conservative 128MiB margin.
packbytes=count(['git','pack-objects','--stdout','--revs'],(commit+'\n').encode())
free=lambda p:os.statvfs(p).f_bavail*os.statvfs(p).f_frsize
margin=128*1024*1024
tmp_needed=max(zipbytes,packbytes+16*1024*1024)+margin
durable_needed=packbytes+146100000+191814688+12265727+42000000+margin
record={'sourceCommit':commit,'temporarySourceZIPStreamBytes':zipbytes,'reachablePackStreamBytes':packbytes,'packEstimateQualification':'Same source reachable closure; measured streamed pack, not an official retained bundle hash. Includes 128MiB margin plus temporary pack-index estimate. Actual bundle restoration must still pass.','tmpNeededBytes':tmp_needed,'durableNeededBytes':durable_needed,'tmpFreeBytes':free('/tmp'),'durableFreeBytes':free('/workspace'),'reserveBytes':margin,'tmpPass':free('/tmp')>=tmp_needed,'durablePass':free('/workspace')>=durable_needed,'noReleaseDirectoryCreated':not(root/'releases/0.8.0').exists(),'createdAtUTC':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}
dest=root/'reviews/root-v0.8-archive-capacity'/f'PREFLIGHT-{commit}.json'
with dest.open('x') as f:json.dump(record,f,indent=2);f.write('\n')
print(json.dumps(record))
