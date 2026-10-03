from pathlib import Path
import hashlib,json,tarfile,io,os
R=Path('/workspace/Roguelike-deckbuilder');S=Path('/workspace/scratch')
D=R/'reviews/opening-default-wait-cue-2026-10-02'
assert not D.exists();D.mkdir()
freeze=json.loads((S/'target-wait-default-author-r1/RUNTIME-FREEZE.json').read_text())
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
 'target-wait-default-author-r1','target-wait-default-independent-r1',
 'target-wait-default-caller-author-r1','target-wait-default-caller-independent-r1',
 'target-wait-default-comparison-actual-r1','target-wait-default-actual-technical-independent-r1',
 'target-wait-default-actual-gameplay-independent-r1','target-wait-default-actual-visual-independent-r1',
 'target-wait-default-native-grant-guard-root-r1','target-wait-default-promotion-root-r1','target-wait-default-promotion-guard-root-r1',
]:
 for p in sorted((S/folder).rglob('*')):
  if p.is_file():
   assert not p.is_symlink(),p
   add('evidence/'+folder+'/'+p.relative_to(S/folder).as_posix(),p)
for filename in ['grant-target-wait-default-native-root-r1.py','target-wait-default-comparison-grant-root-r1.json','promote-target-wait-default-root-r1.py']:
 add('root/'+filename,S/filename)
for rel in ['src/main.ts','src/tactile-hand.ts']:
 add('selected-baseline/'+rel,R/rel)
assert entries['evidence/target-wait-default-actual-visual-independent-r1/GATE.json']['sha256']=='6767ff32bc264f04a495774766f2e539486bf0924c1d61ea1f4d07504b13a44b'
manifest={'sourceDigest':freeze['sourceDigest'],'outputsDigest':freeze['outputsDigest'],'logicalBodies':entries,'excludedRetainedRuntimeMedia':excluded,'scope':'Selected default named-target feedback checkpoint. Four original game captures and complete source/actual/review records; media omissions remain pinned and needed, not a self-contained release or retirement authority.'}
manifestBody=(json.dumps(manifest,sort_keys=True,indent=2)+'\n').encode()
archive=D/'evidence.tar.gz'
with tarfile.open(archive,'w:gz',compresslevel=6) as tf:
 for name,body in [('MANIFEST.json',manifestBody)]+[('blobs/'+h,body) for h,body in sorted(blobs.items())]:
  info=tarfile.TarInfo(name);info.size=len(body);info.mtime=0;info.mode=0o444;tf.addfile(info,io.BytesIO(body))
assert archive.stat().st_size<2*1024*1024,archive.stat().st_size
with tarfile.open(archive,'r:gz') as tf:
 assert tf.extractfile('MANIFEST.json').read()==manifestBody
 for h,body in blobs.items():assert tf.extractfile('blobs/'+h).read()==body
summary={'archiveBytes':archive.stat().st_size,'archiveSHA256':hashlib.sha256(archive.read_bytes()).hexdigest(),'manifestSHA256':hashlib.sha256(manifestBody).hexdigest(),'logicalBodies':len(entries),'uniqueBodies':len(blobs),'excludedNeededMediaBodies':len(excluded),'fourOriginalGameCapturesIncluded':True,'roundtripVerified':True,'sourceDigest':freeze['sourceDigest'],'outputsDigest':freeze['outputsDigest'],'defaultCueSelected':True,'noRetirement':True}
(D/'PRESERVATION.json').write_text(json.dumps(summary,indent=2)+'\n')
(D/'README.md').write_text("""# Default named target-wait feedback selected

One native A/B comparison on the exact strict-built1d5bf40a /30ddc54987/56 development candidate used explicit A?targetWaitCue=0 false /Bemptyquery true, ordinary UI-typed937240/default Initiate. In27.421373981s (driver26736ms), both genuinely held Scour over the disabled Reaver without changing the complete save, became naturally ready, showed fresh UID-owned5healthdamage(lethal), released once and produced no queued repeat. All six full checkpoint saved strings match. No state/clock/DOM injection or runtime retry occurred.

Separate technical, gameplay and visual reviews accept narrow named waiting information/fit/purity. The full-card ghost still covers target art/name/HP; “not ready” can be confused with allied READY. The missed rapid-release problem remains unresolved. Four original1440×900q80 captures have uncertified request/completion phases, not continuous animation proof. This source-informed short diagnostic is supplementary to the retained first300 negative, not human fun, novice pacing or attention-loss evidence.

Root selected the exact tested default source/output bodies and verified full87/56 maps, retaining READY251c4fd4 /2c664aa3 main/hand, all five nonmedia outputs and complete maps in rollback. The old current generated JS was moved into that snapshot, not deleted; old frozen stages and all media/releases/reviews/art inputs/datasets remain. This is a narrow development checkpoint without a version/tag or native Windows/Deck/Steam claim. The current scene remains painted. Next improve held-card target occlusion separately.

The actual supervisor observed149 resourcepoints (147live plus initial/final), unchanged memory events, sampled aggregate peak726933504B/minhead767188992B,14 PID/startidentities and no matching live descendants. Two PPID1 zombies remain nonlive/unreaped; universal attribution or unobserved escape is unproved. Four original game JPEGs total776612B, with complete raw saves,176trusted native events, methods and independent findings in the content-addressed capsule.

PRESERVATION.json identifies a full roundtrip of every included logical body. Runtime PNG/WAV bodies are excluded, pinned and still needed at their original paths. This is not a self-contained release or retirement approval. Original method failures, including metadata D-rebinding and visual empty-container assumption, remain preserved unchanged.
""")
print(json.dumps(summary))
