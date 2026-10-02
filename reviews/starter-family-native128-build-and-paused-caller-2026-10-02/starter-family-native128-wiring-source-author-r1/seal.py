import os,json,gzip,hashlib,resource
from pathlib import Path
resource.setrlimit(resource.RLIMIT_DATA,(24*1048576,24*1048576))
p=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def r(q):
 fd=os.open(q,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME)
 with os.fdopen(fd,'rb') as f:return f.read()
def write(n,b):
 with (p/n).open('xb') as f:f.write(b);f.flush();os.fsync(f.fileno())
 assert r(p/n)==b
c=p/'candidate';proof=json.loads(r(c/'PROOF.json'));freeze=Path(proof['baselineFreeze']['path']);base=Path(json.loads(r(freeze))['stage']);original=r(base/'public/art/coherent-native128-manual-crop-view-manifest.json');old=json.loads(original);new=json.loads(r(c/'coherent-native128-manual-crop-view-manifest.json'));inverse=dict(new);inverse['sprites']=inverse['sprites'][:7];inverse['status']=old['status'];inverse['master_sha256']=old['master_sha256'];assert (json.dumps(inverse,indent=2)+'\n').encode()==original
for n in ['main.ts','coherent-native128.ts']:
 b=gzip.decompress(r(c/(n+'.gz')));assert len(b)<=128*1024 and sha(b)==proof[n]['decodedSHA256']
notes=b'''Private SOURCE proposal only: predicted104/70, no actual build/scene/default/animation approval. Existing seven sprites and arena body unchanged. Corrected Ash pair uses engineering480e/private-fit3b2b; Fen/Briar four use engineering4c242 and scoped private-fit within broader REJECT7fd5. Old rejected Ash excluded. Only Cairn/Ash/Fen/Briar starter card IDs and upgrades gain native bodies/portraits; other summons preserve painted fallback. Private coherentNative128 query and cue flag behavior unchanged; canonical guidance composition remains future work. main.ts.gz and coherent-native128.ts.gz are deterministic mtime0 storage; decoded SHA/bytes are in PROOF, never their compressed SHA. PREDICTED-INPUTS.json.gz is the full104 hash map. No PNG copy/decode or held stage write. reconstruct-r3.py applies an exact invertible successor to immutable reconstruct.py; invoke python -B reconstruct-r3.py NEW_PRIVATE_OUTPUT. Retained first exact-span failure and later pre-output budget refusal produced no candidate. Initial bootstrap read had a wrong function locator/truncated output; subsequent guarded source reads corrected it. All failed histories retained. Manifest inverse restores seven rows/status/master and exact original indent2 bytes. Source limits64+512/disk64/24RSS/logical128KiB; observed cgroup attribution nonexclusive.\n'''
write('README.txt',notes)
rows=[]
for q in sorted(p.rglob('*')):
 if q.is_file() and 'SEAL-GUARD' not in q.parts:rows.append([str(q.relative_to(p)),len(r(q)),sha(r(q))])
seal={'scope':'SOURCE_ONLY_TOOL_GUARD_CLOSED_AFTER_FINITE_EXIT','bodyTupleSHA256':sha(json.dumps(rows,separators=(',',':')).encode()),'bodyCount':len(rows),'manifestFullByteInverse':True,'candidateSourceDigest':proof['predictedSourceDigest'],'inputs':104,'outputsPredictionOnly':70,'sourceProofSHA256':sha(r(c/'PROOF.json')),'methodSHA256':sha(r(p/'reconstruct-r3.py')),'rssKiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'allOriginalFailuresRetained':True,'sourceCap':131072,'reservedOuterGuardTailBytes':2500}
b=(json.dumps(seal,separators=(',',':'))+'\n').encode();total=sum(q.stat().st_size for q in p.rglob('*') if q.is_file());assert total+len(b)+2500<=131072
write('FINAL-SEAL.json',b);print(json.dumps({'sealSHA256':sha(b),'currentBytes':total+len(b),'tailReserve':2500,'rssKiB':seal['rssKiB'],'manifestInverse':True}))
