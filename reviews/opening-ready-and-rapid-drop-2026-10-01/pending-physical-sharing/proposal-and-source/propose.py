import pathlib,json,hashlib,os,time,resource
s=pathlib.Path('/workspace/scratch');repo=pathlib.Path('/workspace/Roguelike-deckbuilder');stage=s/'first-five-opening-cairn128-ready-stage-r1';out=s/'frozen128-canonical-media-sharing-proposal-root-r1'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(65536):h.update(b)
 return h.hexdigest()
def identity(p):
 a=p.stat();return {'dev':a.st_dev,'ino':a.st_ino,'nlink':a.st_nlink,'bytes':a.st_size,'blocks':a.st_blocks,'mode':a.st_mode,'uid':a.st_uid,'gid':a.st_gid,'atimeNs':a.st_atime_ns,'mtimeNs':a.st_mtime_ns,'ctimeNs':a.st_ctime_ns,'sha256':sha(p)}
groups=[];excluded=[]
for sub,suffix in [('art','.png'),('audio','.wav')]:
 for p in sorted((stage/'public'/sub).glob('*'+suffix)):
  dest=stage/'dist'/sub/p.name;anchor=repo/'public'/sub/p.name
  if not anchor.exists():excluded.append({'path':str(p),'distPath':str(dest),'reason':'No canonical same-name anchor; unique native128 sprite excluded.'});continue
  a,b,c=identity(p),identity(dest),identity(anchor)
  assert a['sha256']==b['sha256']==c['sha256']
  assert (a['dev'],a['ino'])==(b['dev'],b['ino']) and a['nlink']==b['nlink']==2
  assert (a['dev'],a['ino'])!=(c['dev'],c['ino']) and a['dev']==c['dev']
  groups.append({'anchor':str(anchor),'anchorBefore':c,'recipients':[{'path':str(p),'before':a},{'path':str(dest),'before':b}],'oldAllocatedBytes':a['blocks']*512})
assert len(groups)==50 and len(excluded)==1
proof={'kind':'proposal only; no mutation or retirement','groups':groups,'groupCount':50,'recipientCount':100,'grossOldAllocationBytes':sum(x['oldAllocatedBytes'] for x in groups),'excluded':excluded,'selectedSourceDigest':'251c4fd4fdcce5bbbc39bf438155277ea440c724bd803adf10cd07b5ffa89a65','selectedOutputsDigest':'2c664aa389221f8570e1f6cebd1ae63f0784d2cba95a7fcc267c3743096a823c','freezePath':str(s/'first-five-opening-cairn128-ready-runtime-freeze-root-r1.json'),'freezeSHA256':sha(s/'first-five-opening-cairn128-ready-runtime-freeze-root-r1.json'),'holdPath':str(repo/'AGENTS.md'),'holdSHA256':sha(repo/'AGENTS.md'),'limitations':'Only exact redundant physical media encodings. Preserve all100 paths/bytes/maps and unique native sprite, reviews, inputs/datasets/releases/protected archives. Original recipient inode/ctime/independent-write semantics intentionally surrendered after independent review, producer judgment and current push confirmation. New links increase canonical anchor nlink/ctime and all aliases observe those metadata changes. Current original atime snapshots precede ordinary body reads; no atime equality claimed. No current transaction authorization.','ownHWM':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,'utcNs':time.time_ns()}
(out/'PROPOSAL.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({k:proof[k] for k in ['groupCount','recipientCount','grossOldAllocationBytes','ownHWM']}))
