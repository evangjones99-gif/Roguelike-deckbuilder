import os,json,gzip,hashlib,resource
from pathlib import Path
resource.setrlimit(resource.RLIMIT_DATA,(24*1048576,24*1048576))
p=Path(__file__).resolve().parent;old=p.with_name('starter-family-native128-wiring-source-author-r1');sha=lambda b:hashlib.sha256(b).hexdigest()
def r(q):
 fd=os.open(q,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME)
 with os.fdopen(fd,'rb') as f:return f.read()
def w(n,b):
 if not isinstance(b,bytes):b=(json.dumps(b,separators=(',',':'))+'\n').encode()
 with (p/n).open('xb') as f:f.write(b);f.flush();os.fsync(f.fileno())
 assert r(p/n)==b
rows=[]
for q in sorted(old.rglob('*')):
 if q.is_file():b=r(q);rows.append({'path':str(q),'bytes':len(b),'sha256':sha(b)})
assert sum(x['bytes'] for x in rows)==129374
proof=json.loads(r(old/'candidate/PROOF.json'));f=json.loads(r(proof['baselineFreeze']['path']));base=Path(f['stage']);a=r(base/'public/art/coherent-native128-manual-crop-view-manifest.json');original=json.loads(a);m=json.loads(r(old/'candidate/coherent-native128-manual-crop-view-manifest.json'));m['sprites']=m['sprites'][:7];m['status']=original['status'];m['master_sha256']=original['master_sha256'];assert (json.dumps(m,indent=2)+'\n').encode()==a
candidates={}
for stored,decoded in [('main.ts.gz','main.ts'),('coherent-native128.ts.gz','coherent-native128.ts'),('art.ts','art.ts'),('coherent-native128-manual-crop-view-manifest.json','coherent-native128-manual-crop-view-manifest.json')]:
 q=old/'candidate'/stored;b=r(q);d=gzip.decompress(b) if stored.endswith('.gz') else b;assert len(d)<=128*1024
 if decoded in proof:assert sha(d)==proof[decoded]['decodedSHA256']
 candidates[decoded]={'path':str(q),'storedSHA256':sha(b),'storedBytes':len(b),'format':'gzip-mtime0' if stored.endswith('.gz') else 'plain','decodedSHA256':sha(d),'decodedBytes':len(d)}
inputs=json.loads(gzip.decompress(r(old/'candidate/PREDICTED-INPUTS.json.gz')));assert len(inputs)==104 and sha(json.dumps(dict(sorted(inputs.items())),separators=(',',':')).encode())==proof['predictedSourceDigest']
plan={'status':'UNSELECTED_SOURCE_PROPOSAL','immutableR1BodyRows':rows,'r1LogicalBytes':129374,'r1Cap':131072,'r1FinalSealRefusedTailReserve':True,'candidateSources':candidates,'full104MapPath':str(old/'candidate/PREDICTED-INPUTS.json.gz'),'full104MapStoredSHA256':sha(r(old/'candidate/PREDICTED-INPUTS.json.gz')),'predictedSourceDigest':proof['predictedSourceDigest'],'expectedInputs':104,'expectedOutputsPredictionOnly':70,'proofSHA256':sha(r(old/'candidate/PROOF.json')),'baseFreeze':proof['baselineFreeze'],'exactGatePins':proof['gatePins'],'externalSixPNGs':proof['externalNativePNGs'],'mainAndHelperFullByteInverses':True,'artFullByteInverse':True,'manifestFullByteInverse':True,'arenaUntouched':proof['unchangedArenaSHA256'],'privateCueFlagUnchanged':True,'currentCanonicalCueCompositionPending':True,'artAnimationDefaultFunAccepted':False,'actualBuild':False}
w('PLAN.json',plan)
method=b'''"""ROOT-only future source materialization, not assembly/build; exact external R1 pins."""\nimport os,sys,json,gzip,hashlib\nfrom pathlib import Path\np=Path(__file__).resolve().parent\ndef r(q):\n fd=os.open(q,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME)\n with os.fdopen(fd,'rb') as f:return f.read()\nplan=json.loads(r(p/'PLAN.json'));out=Path(sys.argv[1]);assert not out.exists()\nbodies={}\nfor name,x in plan['candidateSources'].items():\n b=r(x['path']);assert len(b)==x['storedBytes'] and hashlib.sha256(b).hexdigest()==x['storedSHA256']\n d=gzip.decompress(b) if x['format']=='gzip-mtime0' else b\n assert len(d)==x['decodedBytes']<=128*1024 and hashlib.sha256(d).hexdigest()==x['decodedSHA256'];bodies[name]=d\nout.mkdir(mode=0o700)\nfor n,b in bodies.items():\n with (out/n).open('xb') as f:f.write(b);f.flush();os.fsync(f.fileno())\n assert r(out/n)==b\nprint(json.dumps({'materializedExactSources':len(bodies),'actualBuild':False}))\n'''
w('materialize.py',method)
w('README.txt',b'''R2 is a fresh compact closure of the exact immutable R1 source candidate, not a second candidate or a retest. All129374B of R1 are pinned in PLAN including the failed exact-span reconstruction, pre-output capacity refusal and final reserve refusal. No R1 body is removed or rewritten. R1 stayed below128KiB; its FINAL-SEAL was absent. R3 reconstruction and saved full byte readback passed; distinct stored gzip/decoded source SHA and lengths are pinned here. Full source inverses for helper/main/art were executed in R1, manifest full inverse reverified here. Only starter Cairn/Ash/Fen/Briar IDs and their upgrades gain bodies/portraits; unsupported variants keep whole painted fallback. Existing seven rows, arena/floor/corpse/input/UID/rules/save/reduced motion remain untouched. Engineering/private-fit gates are exact references, not default/art/animation approval. No source modules/Pillow/Node/build/browser run. Future Root argv: python -B materialize.py NEW_PRIVATE_SOURCE_DIR; this only reconstructs the four modified source/manifest bodies and copies no media. Full predicted104 input map is external lossless gzip, outputs70 are an unbuilt prediction. Private cue OFF/query behavior is unchanged; canonical guidance composition remains separate.\n''')
print(json.dumps({'planSHA256':sha(r(p/'PLAN.json')),'methodSHA256':sha(method),'sourceDigest':proof['predictedSourceDigest'],'rssKiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'manifestFullInverse':True,'r1BodyCount':len(rows)}))
