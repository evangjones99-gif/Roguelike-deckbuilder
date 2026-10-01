import sys,json,zipfile,hashlib
request=json.load(sys.stdin)
with zipfile.ZipFile(sys.argv[1]) as archive:
 if archive.comment!=request['sourceCommit'].encode():raise ValueError('Source archive commit comment mismatch')
 entries=archive.infolist();names=[i.filename for i in entries]
 if len(set(names))!=len(names):raise ValueError('Duplicate source archive members')
 members={i.filename:i for i in entries};records=[]
 for expected in request['files']:
  name=expected['path']
  if name not in members or members[name].is_dir():raise ValueError('Committed canonical review absent from source archive: '+name)
  info=members[name];sha=hashlib.sha256();blob=hashlib.sha1(('blob '+str(info.file_size)+'\0').encode());size=0
  with archive.open(info) as source:
   while chunk:=source.read(1024*1024):size+=len(chunk);sha.update(chunk);blob.update(chunk)
  if size!=info.file_size or blob.hexdigest()!=expected['gitBlob']:raise ValueError('Source archive review differs from committed blob: '+name)
  records.append({'path':name,'bytes':size,'sha256':sha.hexdigest(),'gitBlob':expected['gitBlob']})
 print(json.dumps(records,separators=(',',':')))
