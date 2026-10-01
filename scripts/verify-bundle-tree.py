import sys,subprocess,json,hashlib
source,restored,commit=sys.argv[1:]
def git(repo,*args):return subprocess.check_output(['git',*args],cwd=repo)
if git(source,'cat-file','commit',commit)!=git(restored,'cat-file','commit',commit):raise ValueError('Restored commit bytes differ')
a=git(source,'ls-tree','-r','-z',commit);b=git(restored,'ls-tree','-r','-z',commit)
if a!=b:raise ValueError('Restored complete tree identity differs')
entries=[]
for item in a.split(b'\0'):
 if not item:continue
 info,name=item.split(b'\t',1);mode,kind,oid=info.split(b' ')
 if kind!=b'blob':raise ValueError('Bundle current tree contains unsupported non-blob entry')
 entries.append((name.decode('utf8'),mode.decode(),oid.decode()))
procs=[subprocess.Popen(['git','cat-file','--batch'],cwd=repo,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)for repo in [source,restored]]
records=[]
try:
 for name,mode,oid in entries:
  hashes=[];sizes=[]
  for proc in procs:
   proc.stdin.write((oid+'\n').encode());proc.stdin.flush();parts=proc.stdout.readline().split()
   if len(parts)!=3 or parts[0].decode()!=oid or parts[1]!=b'blob':raise ValueError('Invalid restored/source blob response: '+name)
   size=int(parts[2]);remain=size;digest=hashlib.sha256();blob=hashlib.sha1(('blob '+str(size)+'\0').encode())
   while remain:
    chunk=proc.stdout.read(min(remain,1024*1024))
    if not chunk:raise ValueError('Truncated blob stream: '+name)
    remain-=len(chunk);digest.update(chunk);blob.update(chunk)
   if proc.stdout.read(1)!=b'\n' or blob.hexdigest()!=oid:raise ValueError('Invalid canonical blob identity: '+name)
   hashes.append(digest.hexdigest());sizes.append(size)
  if hashes[0]!=hashes[1] or sizes[0]!=sizes[1]:raise ValueError('Restored full-tree bytes differ: '+name)
  records.append({'path':name,'mode':mode,'gitBlob':oid,'bytes':sizes[0],'sha256':hashes[0]})
finally:
 for proc in procs:
  proc.stdin.close();proc.wait(timeout=20)
  if proc.returncode:raise ValueError('Git blob reader failed')
print(json.dumps({'commit':commit,'tree':git(source,'rev-parse',commit+'^{tree}').decode().strip(),'files':records},separators=(',',':')))
