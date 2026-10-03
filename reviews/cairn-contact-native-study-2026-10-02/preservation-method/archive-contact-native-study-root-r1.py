from pathlib import Path
import hashlib,json,tarfile,io,os
R=Path('/workspace/Roguelike-deckbuilder');S=Path('/workspace/scratch');D=R/'reviews/cairn-contact-native-study-2026-10-02';assert not D.exists();D.mkdir()
entries={};blobs={}
def add(name,p):
 fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME)
 with os.fdopen(fd,'rb') as f:b=f.read()
 h=hashlib.sha256(b).hexdigest();entries[name]={'originalPath':str(p),'bytes':len(b),'sha256':h};blobs[h]=b
for folder in ['cairn-contact-reference-author-r1','cairn-contact-reference-native-author-r1','cairn-contact-native-visual-independent-r1']:
 for p in sorted((S/folder).rglob('*')):
  if p.is_file():assert not p.is_symlink();add(folder+'/'+p.relative_to(S/folder).as_posix(),p)
add('generated-contact-master.png',Path('/workspace/generated_images/exec-dd1c8ada-d990-4cac-821d-3173e7b9f346.png'))
for rel in ['clean-native-128.png','clean-nn2x-256.png']:
 add('retained-ready-reference/'+rel,S/'standard-sol-generated-cairn-128-converter-author-r1/prototype-r2'/rel)
assert entries['generated-contact-master.png']['sha256']=='769da0c3d431fb5c9f0e9ff26b3f196946d69f5651caa254e8564236651555d6'
assert entries['cairn-contact-native-visual-independent-r1/GATE.json']['sha256']=='b56ea96aeadfc5e3af3e0385a7256fc142ceb0d78eb0b484e143db6d7b2df03a'
m={'logicalBodies':entries,'decision':'RETAIN_UNSELECTED_CONTACT_STUDY_REJECT_DROP_IN_INTEGRATION','scope':'One generated CONTACT master, native conversion/recipes/audits, exact old READY references and independent personally viewed native/NN rejection. No game/default/release/retirement claim.','neededExcludedAncestorMaster':{'path':'/workspace/generated_images/exec-eeb463ad-a453-46de-a357-e6de4418590c.png','sha256':'1fb0b8531352d917c754ca4fec27577eaab9ef2ce5d60c8783d4a0f3aeae4e30d','bytes':843709,'stillNeeded':True}}
mb=(json.dumps(m,sort_keys=True,indent=2)+'\n').encode();a=D/'evidence.tar.gz'
with tarfile.open(a,'w:gz',compresslevel=6) as tf:
 for name,b in [('MANIFEST.json',mb)]+[('blobs/'+h,b) for h,b in sorted(blobs.items())]:
  t=tarfile.TarInfo(name);t.size=len(b);t.mtime=0;t.mode=0o444;tf.addfile(t,io.BytesIO(b))
assert a.stat().st_size<1048576
with tarfile.open(a,'r:gz') as tf:
 assert tf.extractfile('MANIFEST.json').read()==mb
 for h,b in blobs.items():assert tf.extractfile('blobs/'+h).read()==b
summary={'archiveBytes':a.stat().st_size,'archiveSHA256':hashlib.sha256(a.read_bytes()).hexdigest(),'manifestSHA256':hashlib.sha256(mb).hexdigest(),'logicalBodies':len(entries),'uniqueBodies':len(blobs),'allIncludedBodiesRoundtripVerified':True,'decision':m['decision'],'ancestorMasterExcludedPinnedNeeded':True,'noSourceOrMediaPromotionOrCleanup':True}
(D/'PRESERVATION.json').write_text(json.dumps(summary,indent=2)+'\n')
(D/'README.md').write_text("""# Targeted Cairn CONTACT: retained, rejected pose continuity

The one original generated CONTACT reference became a native192×144 transparent command cell at the same1/10 anatomical scale, shared16-entry palette and exact NN2× display. The retained128 READY body is unchanged and padded at17,14 in comparisons. Neither generated detail nor palette mechanics establishes crafted animation.

Author and separate independent reviewer personally viewed the original native384×144 andNN768×288 comparisons. The lower connected forward lunge improves on the older upward bark and disconnected mask studies, but a smaller skull/ears, broader lower torso/collar volume and lateral facing break continuity with tall READY. Both reject drop-in/game integration. Pixel clusters and a tiny bite silhouette still need craft. No actual game/timing/motion or fully pixel-scene proof follows.

The content-addressed capsule preserves the new598450B generated master, exact prompt/tool receipt/provenance, recipes, all draft/final native outputs, source/audit/guard records, initial truncated author-view limitation and later successful views, and the independent rejection. The original READY native/NN references are included; its843709B ancestor generated master remains pinned and needed outside the capsule. No artifact was removed, overwritten or selected. Some converter local RESOURCE final fields were null despite populated outer guard finals; original records and qualifications remain unchanged.

PRESERVATION.json identifies the archive and full body roundtrip. This is a bounded research capsule, not a self-contained game release, universal decoder reproduction or cleanup authorization. Continue coherent identity/pose work separately from card feedback and opening play.
""")
print(json.dumps(summary))
