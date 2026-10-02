from pathlib import Path
import hashlib,json,tarfile,io,os
R=Path('/workspace/Roguelike-deckbuilder');S=Path('/workspace/scratch')
D=R/'reviews/opening-target-wait-cue-2026-10-02'
assert not D.exists();D.mkdir()
freeze=json.loads((S/'target-wait-cue-build-author-r1/RUNTIME-FREEZE.json').read_text())
stage=Path(freeze['stage']);entries={};blobs={};excluded={}
def add(name,p,omit=False):
 body=p.read_bytes();h=hashlib.sha256(body).hexdigest()
 row={'originalPath':str(p),'bytes':len(body),'sha256':h}
 if omit:excluded[name]=row
 else:
  assert len(body)<2*1024*1024,(name,len(body))
  entries[name]=row
  if h not in blobs:blobs[h]=body
for kind,base in [('inputs',stage),('outputs',stage/'dist')]:
 for rel,h in freeze[kind].items():
  p=base/rel;assert hashlib.sha256(p.read_bytes()).hexdigest()==h
  add('runtime/'+kind+'/'+rel,p,p.suffix.lower() in ['.png','.wav'])
for folder in [
 'blocked-target-feedback-source-author-r1','blocked-target-feedback-source-independent-r1',
 'target-wait-cue-build-author-r1','target-wait-cue-build-independent-r1',
 'target-wait-cue-caller-author-r1','target-wait-cue-caller-independent-r1',
 'target-wait-cue-comparison-actual-r1','target-wait-cue-actual-technical-independent-r1',
 'target-wait-cue-actual-gameplay-independent-r1','target-wait-cue-actual-visual-independent-r1',
 'target-wait-cue-native-grant-guard-root-r1',
]:
 for p in sorted((S/folder).rglob('*')):
  if p.is_file():
   assert not p.is_symlink(),p
   add('evidence/'+folder+'/'+p.relative_to(S/folder).as_posix(),p)
for filename in ['grant-target-wait-cue-native-root-r1.py','target-wait-cue-comparison-grant-root-r1.json']:
 add('root/'+filename,S/filename)
for rel in ['src/main.ts','src/tactile-hand.ts']:
 add('selected-baseline/'+rel,R/rel)
assert entries['evidence/target-wait-cue-actual-visual-independent-r1/GATE.json']['sha256']=='e687bd8afb2c6321ecd069ee9ef68ee8c042c6d74757af4398de0e4ada264f25'
manifest={'sourceDigest':freeze['sourceDigest'],'outputsDigest':freeze['outputsDigest'],'logicalBodies':entries,'excludedRetainedRuntimeMedia':excluded,'scope':'Unselected opt-in named-target feedback trial. Four original game captures and complete source/actual/review records; media omissions remain pinned and needed, not a self-contained release or retirement authority.'}
manifestBody=(json.dumps(manifest,sort_keys=True,indent=2)+'\n').encode()
archive=D/'evidence.tar.gz'
with tarfile.open(archive,'w:gz',compresslevel=6) as tf:
 for name,body in [('MANIFEST.json',manifestBody)]+[('blobs/'+h,body) for h,body in sorted(blobs.items())]:
  info=tarfile.TarInfo(name);info.size=len(body);info.mtime=0;info.mode=0o444;tf.addfile(info,io.BytesIO(body))
assert archive.stat().st_size<2*1024*1024,archive.stat().st_size
with tarfile.open(archive,'r:gz') as tf:
 assert tf.extractfile('MANIFEST.json').read()==manifestBody
 for h,body in blobs.items():assert tf.extractfile('blobs/'+h).read()==body
summary={'archiveBytes':archive.stat().st_size,'archiveSHA256':hashlib.sha256(archive.read_bytes()).hexdigest(),'manifestSHA256':hashlib.sha256(manifestBody).hexdigest(),'logicalBodies':len(entries),'uniqueBodies':len(blobs),'excludedNeededMediaBodies':len(excluded),'fourOriginalGameCapturesIncluded':True,'roundtripVerified':True,'sourceDigest':freeze['sourceDigest'],'outputsDigest':freeze['outputsDigest'],'noDefaultPromotionOrRetirement':True}
(D/'PRESERVATION.json').write_text(json.dumps(summary,indent=2)+'\n')
(D/'README.md').write_text('''# Opening target-wait cue: opt-in playable comparison

The private `targetWaitCue=1` proposal names a legally targetable creature whose owned field control is temporarily disabled. This changes feedback only; it does not relax release legality, queue a play, select a card, mutate a save or change rules/RNG.

The one matched native UI comparison took27.486917196s (driver26801ms): two fresh seed937240/default Initiate contexts. Both exposed genuine active held ghosts at the owned disabled Reaver, retained the entire save until release, became naturally ready, showed a fresh UID-owned5-damage lethal preview, committed once and produced no queued spend. All six complete checkpoint saved strings match. These are source-informed short diagnostic facts, not a fresh300-second human playtest, attention loss or reliable rapid-drop repair.

Three separate independent reviews accept the narrow named-wait information/fit and technical continuity. The held ghost still hides target art/name/HP; the phrase “not ready” risks confusion with allied READY. Still captures have phaseCertified=false and do not prove continuous timing. The current scene remains painted. The cue remains unselected pending a separately built/tested default successor. Selected251c4fd4 /2c664aa3 and sealed0.8.0 remain unchanged; no new version/tag follows.

The actual supervisor observes150 resource points with unchanged memory events, sampled aggregate delta716,193,792B/minimum headroom790,740,992B, and14 PID/start identities with no matching live descendants; two PPID1 zombies are nonlive/unreaped. This is bounded owned-process evidence, not universal exclusive resource attribution or unobserved-escape proof.

`evidence.tar.gz` is content-addressed: its MANIFEST maps each logical body to an original path/hash and a blobs/SHA body. It includes all four original1440×900q80 game JPEGs (776,624B total), complete source/build/caller/actual/review records and retained method failures. Encoded runtime PNG/WAV bodies are excluded, pinned and still needed at their retained original paths. It is not a self-contained release and grants no cleanup. PRESERVATION.json records the exact archive identity and verified roundtrip.
''')
print(json.dumps(summary))
