import pathlib,json,hashlib,os,sys,time,subprocess
proposal_path,gate_path,judgment_path=sys.argv[1:]
repo=pathlib.Path('/workspace/Roguelike-deckbuilder');out=pathlib.Path('/workspace/scratch/frozen128-canonical-media-sharing-action-root-r1')
def sha(p):
 h=hashlib.sha256()
 with pathlib.Path(p).open('rb') as f:
  while b:=f.read(65536):h.update(b)
 return h.hexdigest()
def write(name,j):
 with (out/name).open('x') as f:json.dump(j,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def current(p):
 a=pathlib.Path(p).stat();return {'dev':a.st_dev,'ino':a.st_ino,'nlink':a.st_nlink,'bytes':a.st_size,'blocks':a.st_blocks,'mode':a.st_mode,'uid':a.st_uid,'gid':a.st_gid,'mtimeNs':a.st_mtime_ns,'ctimeNs':a.st_ctime_ns,'sha256':sha(p)}
proof=json.loads(pathlib.Path(proposal_path).read_text());gate=json.loads(pathlib.Path(gate_path).read_text());judgment=json.loads(pathlib.Path(judgment_path).read_text())
assert gate['decision']=='ACCEPT_EXACT_PHYSICAL_SHARING_AND_ACTION_SOURCE'
assert len({(g['anchorBefore']['dev'],g['anchorBefore']['ino']) for g in proof['groups']})==50
assert judgment['proposalSHA256']==sha(proposal_path) and judgment['gateSHA256']==sha(gate_path) and judgment['actionSHA256']==sha(__file__)
assert judgment['approvedGroups']==50 and judgment['approvedRecipients']==100 and judgment['pushConfirmed'] and judgment['writersClosed']
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()
assert head==judgment['commit']
assert not subprocess.check_output(['git','status','--porcelain'],cwd=repo,text=True).strip()
remote=subprocess.check_output(['git','ls-remote','origin','refs/heads/codex/lanternbound-production'],cwd=repo,text=True,timeout=30).split()[0]
assert remote==head
assert proof['holdSHA256']==sha(proof['holdPath']) and proof['freezeSHA256']==sha(proof['freezePath'])
for g in proof['groups']:
 for p,old in [(g['anchor'],g['anchorBefore'])]+[(r['path'],r['before']) for r in g['recipients']]:
  now=current(p)
  for k in now:assert now[k]==old[k],(p,k,'changed since review')
 assert len(g['recipients'])==2
out.mkdir(exist_ok=False);v=os.statvfs(out);initial_free=v.f_bavail*v.f_frsize
write('BEFORE.json',{'proposalSHA256':sha(proposal_path),'gateSHA256':sha(gate_path),'judgment':judgment,'groups':proof['groups'],'initialFreeBytes':initial_free})
with (out/'JOURNAL.jsonl').open('x') as journal:
 def emit(row):journal.write(json.dumps(row)+'\n');journal.flush();os.fsync(journal.fileno())
 for gi,g in enumerate(proof['groups']):
  anchor=pathlib.Path(g['anchor'])
  for ri,r in enumerate(g['recipients']):
   p=pathlib.Path(r['path']);old=r['before'];now=current(p)
   assert now['ino']==old['ino'] and now['dev']==old['dev'] and now['nlink']==2-ri and now['sha256']==old['sha256']
   temp=p.with_name(p.name+'.reviewed-share-tmp-r1');assert not temp.exists()
   emit({'phase':'BEFORE','group':gi,'recipient':ri,'path':str(p),'old':now,'temp':str(temp),'anchor':current(anchor)})
   os.link(anchor,temp)
   emit({'phase':'PREPARED','group':gi,'recipient':ri,'temp':str(temp),'identity':current(temp)})
   os.replace(temp,p)
   fd=os.open(p.parent,os.O_RDONLY|os.O_DIRECTORY)
   try:os.fsync(fd)
   finally:os.close(fd)
   after=current(p);a=current(anchor)
   assert after['sha256']==old['sha256'] and (after['dev'],after['ino'])==(a['dev'],a['ino']) and not temp.exists()
   emit({'phase':'COMPLETE','group':gi,'recipient':ri,'path':str(p),'after':after,'anchor':a})
 for g in proof['groups']:
  a=current(g['anchor']);assert a['nlink']==g['anchorBefore']['nlink']+2
  for r in g['recipients']:
   after=current(r['path']);assert after['sha256']==r['before']['sha256'] and (after['dev'],after['ino'])==(a['dev'],a['ino'])
v=os.statvfs(out);final_free=v.f_bavail*v.f_frsize
write('RESULT.json',{'normal':True,'groups':50,'recipients':100,'allPathsAndBytesPreserved':True,'oldGrossAllocationBytes':proof['grossOldAllocationBytes'],'initialFreeBytes':initial_free,'finalFreeBytes':final_free,'observedNetRecoveredBytes':final_free-initial_free,'commit':head,'remoteConfirmed':remote,'limitations':proof['limitations'],'utcNs':time.time_ns()})
print(json.dumps({'normal':True,'groups':50,'recipients':100,'observedNetRecoveredBytes':final_free-initial_free}))
