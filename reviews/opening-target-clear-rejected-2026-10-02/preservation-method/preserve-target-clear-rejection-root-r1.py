from pathlib import Path
import os,json,hashlib,tarfile,io
R=Path('/workspace/Roguelike-deckbuilder'); S=Path('/workspace/scratch')
D=R/'reviews/opening-target-clear-rejected-2026-10-02'
assert not D.exists(); D.mkdir()
entries={}; blobs={}
def add(name,p):
    assert not p.is_symlink()
    fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME)
    with os.fdopen(fd,'rb') as f:b=f.read()
    h=hashlib.sha256(b).hexdigest()
    entries[name]={'originalPath':str(p),'bytes':len(b),'sha256':h}; blobs[h]=b
folders=['target-clear-ghost-source-root-r1','target-clear-ghost-source-independent-r1','target-clear-ghost-build-author-r1','target-clear-ghost-build-independent-r1','target-clear-ghost-caller-author-r1','target-clear-ghost-caller-author-r2','target-clear-ghost-caller-visual-independent-r1','target-clear-ghost-comparison-actual-r1','target-clear-ghost-actual-technical-independent-r1','target-clear-ghost-actual-gameplay-independent-r1','target-clear-ghost-actual-visual-independent-r1','target-clear-ghost-actual-visual-independent-r2','target-clear-ghost-native-grant-guard-root-r1','target-clear-ghost-native-grant-guard-root-r2','target-clear-ghost-native-grant-guard-root-r3','inactive-build-media-cache-hint-root-r1','inactive-build-media-cache-hint-guard-root-r1','retained-source-bundle-cache-hint-root-r1','retained-source-bundle-cache-hint-guard-root-r1','inactive-git-pack-cache-hint-root-r1','inactive-git-pack-cache-hint-guard-root-r1']
for folder in folders:
    assert (S/folder).is_dir(),folder
    for p in sorted((S/folder).rglob('*')):
        if p.is_file():add(folder+'/'+p.relative_to(S/folder).as_posix(),p)
for name in ['grant-target-clear-ghost-native-root-r1.py','target-clear-ghost-comparison-grant-root-r1.json','hint-inactive-build-media-cache-root-r1.py','hint-retained-source-bundle-cache-root-r1.py','hint-inactive-git-pack-cache-root-r1.py']:
    add(name,S/name)
assert entries['target-clear-ghost-actual-visual-independent-r2/GATE.json']['sha256']=='851c1a5cbd3a0d3bf4216885aa89d162e42f9b6cbbc4abce569a56956edcb5e7'
assert entries['target-clear-ghost-actual-technical-independent-r1/GATE.json']['sha256']=='4cc1dc2d2ea2532c5d66a41e3c5778e4c757a321dcf633330f9a48b07b3f77e5'
assert sum(v['bytes'] for v in entries.values())<12*1048576
m={'decision':'REJECT_TARGET_CLEAR_GHOST_R1_FOR_DEFAULT_SELECTION','sourceDigest':'2b3fcb03236f600581c396c5130643ad8f3b6a94d6144f24980d903559759254','outputsDigest':'8235e599a7685e281dd707f54d57ee869fb57bc26e469bbf28df2c37b15665a6','logicalBodies':entries,'neededExcludedFrozenStage':'/workspace/scratch/target-clear-ghost-stage-r1','scope':'Exact private source, build controls/maps, caller controls, one actual with all saves and four original JPEGs, three independent findings, failed visual packet and restoration qualification, resource-refused grants and reversible cache hints. Frozen stage/media remain needed; no deletion or promotion.'}
mb=(json.dumps(m,indent=2,sort_keys=True)+'\n').encode(); a=D/'evidence.tar.gz'
with tarfile.open(a,'w:gz',compresslevel=6) as tf:
    for name,b in [('MANIFEST.json',mb)]+[('blobs/'+h,b) for h,b in sorted(blobs.items())]:
        t=tarfile.TarInfo(name);t.size=len(b);t.mtime=0;t.mode=0o444;tf.addfile(t,io.BytesIO(b))
assert a.stat().st_size<3*1048576
with tarfile.open(a,'r:gz') as tf:
    assert tf.extractfile('MANIFEST.json').read()==mb
    for h,b in blobs.items():assert tf.extractfile('blobs/'+h).read()==b
summary={'archiveBytes':a.stat().st_size,'archiveSHA256':hashlib.sha256(a.read_bytes()).hexdigest(),'manifestSHA256':hashlib.sha256(mb).hexdigest(),'logicalBodies':len(entries),'uniqueBodies':len(blobs),'allIncludedBodiesRoundtripVerified':True,'neededFrozenStageExcluded':True,'sourceDigest':m['sourceDigest'],'outputsDigest':m['outputsDigest'],'decision':m['decision'],'noCleanupOrPromotion':True}
(D/'PRESERVATION.json').write_text(json.dumps(summary,indent=2)+'\n')
(D/'README.md').write_text('''# Target-clear ghost R1: rejected after actual comparison

The private opt-in candidate strict-built as source2b3fcb03/output8235e599 (88/56), then completed one native comparison in27.838516157s. Both ordinary UI-created Initiate contracts used typed seed937240. Six complete raw checkpoint save pairs match,176 trusted events resolve, and each held second Scour release commits once after naturally observed readiness. Neither rapid missed releases nor300-second human enjoyment is qualified.

The chosen Reaver's sampled ghost-plus-label rectangle union falls from24473.6278/27209.9446px² to zero. Cairn's union rises from7442.1472/4588.3179 to15557.7634/15645.5528. Its name, stats and Command-spent status become covered. The separate visual reviewer personally viewed all four1440×900 originals and also reports overlap with Survey's upper art/cost and weaker spatial target association. Gameplay and visual reviews reject promotion; technical acceptance covers identity, state purity and calculations only. The selected named-wait build1d5bf40a/30ddc549 remains unchanged. The default is still painted.

The capsule preserves the exact source/build/caller controls, actual resources/lifecycle/saves/events/captures and independent reports. A visual review helper exceeded its cap, briefly removed two unsealed JSON paths after verified gzip, then restored their exact bodies. Pre-removal inode/time identity is unknown. The original failed oversized packet, compression receipts and fresh qualified review supplement are retained; no history is silently replaced.

Two Root grant checks refused insufficient memory before browser launch. Read-only POSIX cache hints subsequently allowed fresh admission; they neither delete artifacts nor guarantee future memory. Metadata of the hinted files was preserved, and the protected original ZIP body was not read. The normal actual observed150 resource points, peak725913600B and minimum headroom1513713664B, unchanged memory events and14 tracked launch identities closed, with two nonlive PPID1 zombies recorded. Unknown escaped processes and backend image resources are not universally certified.

All original scratch evidence and the excluded frozen stage/media remain needed. This is a bounded rejection capsule, not a release, source retirement or cleanup grant. R2 will protect neighboring actor readouts and occupied hand/HUD controls while keeping actual-pointer authority.
''')
print(json.dumps(summary))
