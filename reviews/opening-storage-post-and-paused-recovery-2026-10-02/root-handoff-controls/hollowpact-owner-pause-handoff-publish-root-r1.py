from pathlib import Path
import os,json,hashlib,time,resource,stat
R=Path('/workspace/Roguelike-deckbuilder');S=Path('/workspace/scratch');start=time.monotonic();rows=[]
def check():
 if time.monotonic()-start>45:raise RuntimeError('Finite45s handoff publication limit')
 if resource.getrusage(resource.RUSAGE_SELF).ru_maxrss>24576:raise RuntimeError('Own24MiB handoff limit')
def read(p):
 check();fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME)
 with os.fdopen(fd,'rb') as f:
  before=os.fstat(f.fileno());assert stat.S_ISREG(before.st_mode) and before.st_size<=600000
  b=f.read();assert len(b)==before.st_size and before==os.fstat(f.fileno())
 return b
def copy(p,q):
 b=read(p);q.parent.mkdir(parents=True,exist_ok=True)
 with q.open('xb') as f:f.write(b)
 assert read(q)==b
 rows.append({'original':str(p),'canonical':str(q),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
def write(p,v):
 b=(json.dumps(v,indent=2)+'\n').encode()
 with p.open('xb') as f:f.write(b)
def tree(source,dest):
 assert source.is_dir() and not source.is_symlink()
 for p in sorted(source.rglob('*')):
  if p.is_file():assert not p.is_symlink();copy(p,dest/p.relative_to(source))
a=R/'reviews/starter-family-native128-build-and-paused-caller-2026-10-02';b=R/'reviews/opening-storage-post-and-paused-recovery-2026-10-02'
a.mkdir(exist_ok=False);b.mkdir(exist_ok=False)
for n in ['starter-family-native128-wiring-source-author-r1','starter-family-native128-wiring-source-author-r2','starter-family-native128-wiring-source-independent-r2','starter-family-native128-materialized-source-root-r1','starter-family-native128-materialization-guard-root-r1','starter-family-native128-build-controls-source-author-r1','starter-family-native128-build-controls-source-independent-r1','starter-family-native128-assembly-guard-root-r1','starter-family-native128-strict-build-root-r1','starter-family-native128-freeze-guard-root-r1','starter-family-native128-strict-build-independent-r1','starter-family-native128-first-session-protocol-source-r1','starter-family-native128-opening-caller-source-author-r1']:
 tree(S/n,a/n)
for n in ['starter-family-native128-materialization-grant-root-r1.json','starter-family-native128-activation-root-r1.json']:copy(S/n,a/'root-controls'/n)
f=json.loads(read(S/'starter-family-native128-strict-build-root-r1/final-seal-r1/RUNTIME-FREEZE.json'));stage=Path(f['stage']);code=[x for x in f['outputs'] if not x.startswith(('art/','audio/'))];assert len(code)==5
for n in code:
 p=stage/'dist'/n;assert hashlib.sha256(read(p)).hexdigest()==f['outputs'][n];copy(p,a/'actual-code-outputs'/n)
for n in ['opening-capsule-duplicate-retirement-action-root-r2','opening-capsule-duplicate-retirement-post-independent-r1','native-checkpoint-push-retirement-guard-root-r2','native-checkpoint-push-retirement-guard-root-r3','native-checkpoint-ignored-logs-push-guard-root-r1','opening-loop-additional-duplicate-storage-triage-independent-r1','git-immutable-pack-cache-hint-opening-root-r1','opening-readonly-pack-cache-hint-source-independent-r1']:
 tree(S/n,b/n)
for n in ['native-checkpoint-current-push-receipt-root-r1.json','opening-capsule-duplicate-retirement-action-grant-root-r2.json','native-checkpoint-ignored-logs-current-push-receipt-root-r1.json','native-checkpoint-push-and-reviewed-retirement-root-r1.py','native-checkpoint-push-and-reviewed-retirement-root-r2.py','native-checkpoint-push-and-reviewed-retirement-root-r3.py','native-checkpoint-push-retirement-root-r2-derivation.json','native-checkpoint-push-retirement-root-r3-derivation.json','native-checkpoint-ignored-logs-push-root-r1.py','hollowpact-hourly-pause-and-owner-steering-2026-10-02.json']:
 copy(S/n,b/'root-controls'/n)
for d,scope in [(a,'Actual starter strict build engineering only; static thirteen images and first<=2ally/enemy eligibility, no browser/art/default/300fun acceptance. Unsealed caller original144KiB failed; pause closure is not a seal. Source families and original failures copied literally.'),(b,'Actual two duplicate encodings absent/canonical exact; independent POST rejects complete pre-action publication because25 logs pushed later. Extra4513 preference and pack cache Source proposal CONDITIONAL only, no new cleanup/advice authorized by handoff.')]:
 selected=[x for x in rows if x['canonical'].startswith(str(d)+'/')]
 write(d/'PUBLICATION.json',{'literalCopies':selected,'ownerPause':True,'scope':scope,'sourceReadMode':'O_RDONLY|NOFOLLOW|NOATIME; original regular bodies/stat unchanged','logicalBytes':sum(x['bytes'] for x in selected),'notARelease':True,'generatedCodeOutputs':5 if d==a else 0,'externalAssetsAndDependencies':True})
 (d/'README.md').write_text('# Owner-requested pause evidence\n\n'+scope+'\n\nSee ../../docs/FRESH-SESSION-HANDOFF-2026-10-02.md for exact pending work, guards, timer/model rules and all limitations. Literal original files and rejected findings are preserved; no silent rewrite. Actual code outputs are retained only for the labelled private build; controlled media/dependencies and original old stage identities remain external. No version/tag/default promotion.\n')
prefix='''## Owner pause and fresh-session handoff — 2 October 2026\n\nThe owner explicitly requested pausing production, disabling the hourly timer and preparing a fresh-session restart. All agents/tools are closed; the timer is confirmed disabled. Read [fresh-session handoff]({link}) and its full restart/timer prompts before resuming. Agents use gpt-6.1-sol, with reasoning chosen by the lead as necessary; fixed high everywhere is superseded. Standard speed/Fast off remains the preference, but these tools expose no app speed toggle.\n\nPrivate starter-family source65b31b3f/outputs960e723d is ACTUALLY strict-built104/70 with121 measured aliases and independent engineering gate2f4f3ef6, but no playable/art/default approval. Its new caller remains unfinished after failing144KiB; third-ally native continuity is blocked by the unchanged two-ally layout. Selected source64c2a14a and held dist8bbaea72 stay. New literal evidence is in reviews/starter-family-native128-build-and-paused-caller-2026-10-02 and reviews/opening-storage-post-and-paused-recovery-2026-10-02.\n\nTwo scratch-only duplicate encodings were removed after a confirmed push; their canonical bytes and metadata remain exact. Independent POST a25a0180 accepts that post-state but REJECTS full pre-publication compliance:25 execution logs were ignored before action and force-pushed afterward in9726c5. Preserve this negative finding. Future cleanup must verify all files, including ignored logs, are tracked with exact HEAD bytes before action. Further4513 retirement and readonly pack advice are conditional proposals only; neither has run. No new release/tag or default pixel selection. Earlier paragraphs remain historical.\n\n'''
for rel,link in [('AGENTS.md','docs/FRESH-SESSION-HANDOFF-2026-10-02.md'),('docs/CONTINUATION.md','FRESH-SESSION-HANDOFF-2026-10-02.md'),('docs/PRODUCTION.md','FRESH-SESSION-HANDOFF-2026-10-02.md')]:
 p=R/rel;before=read(p);addition=prefix.format(link=link).encode();p.write_bytes(addition+before);assert p.read_bytes()[len(addition):]==before
logical=sum(x['bytes'] for x in rows);assert logical<=4*1048576
print(json.dumps({'literalCopies':len(rows),'copiedBytes':logical,'sourceEngineeringOnly':True,'unfinishedCallerPreserved':True,'negativeStorageProcessFindingPreserved':True,'timerPaused':True,'gameSourceAndCanonicalDistNotWritten':True,'phaseElapsed':time.monotonic()-start}))
