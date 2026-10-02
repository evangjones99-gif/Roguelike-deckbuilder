from pathlib import Path
import os,hashlib,json
R=Path('/workspace/Roguelike-deckbuilder');S=Path('/workspace/scratch')
D=R/'reviews/three-png-physical-sharing-post-2026-10-02'; assert not D.exists();D.mkdir()
records={}
def copy(src,dst):
    assert not dst.exists() and not src.is_symlink()
    dst.parent.mkdir(parents=True,exist_ok=True)
    fd=os.open(src,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME)
    with os.fdopen(fd,'rb') as a,dst.open('xb') as b:
        h=hashlib.sha256()
        for chunk in iter(lambda:a.read(65536),b''):b.write(chunk);h.update(chunk)
    assert hashlib.sha256(dst.read_bytes()).hexdigest()==h.hexdigest()
    records[str(dst.relative_to(R/'reviews'))]={'originalPath':str(src),'bytes':dst.stat().st_size,'sha256':h.hexdigest()}
for name in ['three-retained-png-sharing-actual-root-r1','three-retained-png-sharing-post-independent-r1','three-png-sharing-actual-guard-root-r1','three-png-preaction-push-root-r1']:
    for p in sorted((S/name).rglob('*')):
        if p.is_file():copy(p,D/name/p.relative_to(S/name))
copy(S/'three-png-producer-judgment-root-r1.json',D/'three-png-producer-judgment-root-r1.json')
G=R/'reviews/opening-target-clear-rejected-2026-10-02'
copy(S/'preserve-target-clear-rejection-root-r1.py',G/'preservation-method/preserve-target-clear-rejection-root-r1.py')
for p in sorted((S/'target-clear-rejection-preservation-guard-root-r1').rglob('*')):
    if p.is_file():copy(p,G/'preservation-method/guard'/p.relative_to(S/'target-clear-rejection-preservation-guard-root-r1'))
(D/'COPY-IDENTITIES.json').write_text(json.dumps(records,indent=2)+'\n')
(D/'README.md').write_text('''# Exact three-PNG sharing: completed preservation review

After confirmed clean push34f0a2a4 and recorded producer judgment, one transaction kept every historical candidate path/body and shared only abbey-courtyard.png, tool-vignettes.png and hunter-portrait.png under `/workspace/scratch/audio-host-independent-v08/candidate/dist/art` with exact canonical public art. No unique art, version, review or dataset was retired. The prior proposal folder remains historical pre-action evidence.

Gross allocation removed was8499200B. The measured statvfs window was67526656→76009472B: net8482816B after16384B journal/BEFORE overhead, before RESULT and later review writes. This is not an enduring free-space guarantee. The independent POST gate014c9d26 verifies exact three bodies, ordered nine-event durable journal, absent temporary paths, selected87/56 and historical66/51 maps, consumer provenance and protected original full stat identity. It grants no further action.

Original private inode/time/write-isolation identities were intentionally lost and preserved in BEFORE. Anchors gained one link each (4→5) and ctime changed. One pre-existing physical alias per anchor is unresolved, so universal consumer/metadata coverage is not claimed. Sequential per-leaf replacement has durable prefix records, no old-inode backup or all-three power-loss atomicity. All retained paths remain immutable/fresh-stage-only under coordinated workflow holds, not OS-enforced protection. Rights and game quality remain separate.

All originals remain retained. This supplement copies the exact judgment, confirmed push, transaction, guard and independent POST bytes. No additional cleanup is performed.
''')
intro='''## Held-card placement rejected; next protect the whole choice — 2 October2026

The opt-in targetClearGhost R1 actual completed once in27.838516157s on source2b3fcb03/output8235e599 (88/56). It clears the chosen hostile but obscures the bound Cairn's name, health/attack and Command-spent status, with label overlap over the hand. Separate gameplay and visual reviews reject default promotion; technical acceptance covers identity/state purity and sampled geometry only. Six full raw save pairs match and each held release commits once. Preserve the [exact rejection evidence](../reviews/opening-target-clear-rejected-2026-10-02/README.md). Source-informed short diagnostics are not300-second novice pacing or human fun.

Selected named wait1d5bf40a/30ddc549 (87/56) stays unchanged; current scene remains painted. R2 private source work protects each neighboring actor readout and occupied hand/HUD controls, with no release/rules/save change and no claimed improvement until actual comparison.

The separately reviewed exact3-PNG transaction completed after confirmed clean push34f0a2a4 and producer judgment. Independent POST014c9d26 verifies retained paths/bodies/current maps/protected stat; net8482816B was recovered in the measured pre-RESULT window, with inode/time/isolation losses and one unresolved alias per anchor qualified. See [completed storage supplement](../reviews/three-png-physical-sharing-post-2026-10-02/README.md). No further cleanup authority follows. Read-only cache hints preserved bytes/metadata and allowed fresh native memory admission after two refusals; they are not deletion or an enduring capacity guarantee.

'''
for name in ['CONTINUATION.md','PRODUCTION.md']:
    p=R/'docs'/name;body=p.read_text();pos=body.index('\n')+1;p.write_text(body[:pos]+'\n'+intro+body[pos:])
print(json.dumps({'copiedBodies':len(records),'storagePostGate':'014c9d26442bdc581783766d219905a377a99536ef03443bcbab29a9174775ef','noCleanupOrSourceChange':True}))
