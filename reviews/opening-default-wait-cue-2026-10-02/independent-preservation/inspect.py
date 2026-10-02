import os,json,tarfile,resource,collections
resource.setrlimit(resource.RLIMIT_DATA,(24*1048576,24*1048576))
p='/workspace/Roguelike-deckbuilder/reviews/opening-default-wait-cue-2026-10-02/evidence.tar.gz'
with os.fdopen(os.open(p,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW),'rb') as f:
 with tarfile.open(fileobj=f,mode='r|gz') as tf:
  m=next(iter(tf))
  with tf.extractfile(m) as b:data=json.load(b)
  print(json.dumps({'keys':list(data),'logical':len(data['logicalBodies']),'excluded':len(data['excludedRetainedRuntimeMedia']),'prefixes':dict(collections.Counter('/'.join(n.split('/')[:2]) for n in data['logicalBodies'])),'nonEvidenceNames':[n for n in data['logicalBodies'] if not n.startswith('evidence/') and not n.startswith('runtime/')],'reviewNames':[n for n in data['logicalBodies'] if n.endswith('GATE.json') or n.endswith('FINAL-SEAL.json')]}))
