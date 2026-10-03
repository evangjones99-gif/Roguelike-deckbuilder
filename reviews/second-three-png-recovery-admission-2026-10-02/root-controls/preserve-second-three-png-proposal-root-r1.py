from pathlib import Path
import json,hashlib,os
R=Path('/workspace/Roguelike-deckbuilder');S=Path('/workspace/scratch')
assert json.loads((S/'second-three-retained-png-sharing-before-independent-r2/GATE.json').read_text())['decision'].startswith('ACCEPT')
D=R/'reviews/second-three-png-physical-sharing-2026-10-02';assert not D.exists();D.mkdir()
records={}
def copy(a,b):
    assert not a.is_symlink() and not b.exists();b.parent.mkdir(parents=True,exist_ok=True)
    fd=os.open(a,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME)
    with os.fdopen(fd,'rb') as f:v=f.read()
    b.write_bytes(v);h=hashlib.sha256(v).hexdigest();assert hashlib.sha256(b.read_bytes()).hexdigest()==h
    records[str(b.relative_to(D))]={'originalPath':str(a),'bytes':len(v),'sha256':h}
for name in ['media-loose-png-recovery-proposal-author-r2','second-three-retained-png-sharing-before-independent-r1','second-three-retained-png-sharing-before-independent-r2','second-three-png-method-draft-guard-root-r1']:
    for p in sorted((S/name).rglob('*')):
        if p.is_file():copy(p,D/name/p.relative_to(S/name))
for name in ['share-second-three-retained-pngs-root-r1.py','share-second-three-retained-pngs-root-r2.py','draft-second-three-png-method-root-r1.py']:
    copy(S/name,D/'root-method'/name)
(D/'COPY-IDENTITIES.json').write_text(json.dumps(records,indent=2)+'\n')
(D/'README.md').write_text('''# Second exact three-PNG proposal: conditional before action

The separate historical independent audio-host rebuilt-dist/art group retains abbey-courtyard.png, tool-vignettes.png and hunter-portrait.png. Full O_NOATIME candidate/canonical streams match; candidate device27/nlink1 can share held canonical device27/nlink5. Gross candidate allocation8499200B is not net recovery. No action has occurred in this pre-action record.

The original independent audio-host source/output/method and rejection remain useful; retain every logical path/body/provenance/review. Only independent physical encoding is proposed as redundant. The producer must accept loss of original candidate inodes/time/write isolation and anchor link/ctime changes after independent preference and confirmed current push. Four named matching entries leave one pre-existing physical alias unresolved; neither absence of future writers nor universal metadata coverage is certified. New reproduction uses fresh stages/inodes under the named coordinated hold, not OS-enforced protection. Author's earlier AGENTS pin predates the supplemental hold; current method/hold are independently pinned.

Independent source review rejected the unexecuted Root r1 method for indexing canonical rather than the proposal's anchor keys. Original source remains unchanged. The fresh r2 method uses anchor keys and held nofollow parent descriptors, checks each regular file's full body/metadata/xattrs, and rechecks identities before link/replacement and afterward. It preflights all three before any link and journals sequential per-leaf replacements durably. It keeps no old-inode backup, cannot restore original inode/time identity and does not claim all-three power-loss atomicity. Any interrupted prefix requires diagnosis, not automatic retry. Protected original archive is stat-checked without body reads. Current87/56 source/build maps must match before and after. No other action or art/game quality authority follows.

This folder preserves source proposal, original permission failure before input body reads and nofollow-parent correction, independent BEFORE findings, Root method and guard bytes. Whole old66/51 aggregate maps are historical claims separately retained, not fresh full revalidation by the narrow proposal. Rights remain pending. Current R1 ghost placement is independently rejected and selected named wait1d5/30dd remains unchanged.
''')
print(json.dumps({'copiedBodies':len(records),'bytes':sum(v['bytes'] for v in records.values()),'actionOccurred':False}))
