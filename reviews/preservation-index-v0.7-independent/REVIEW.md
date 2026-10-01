# Independent future review-index preservation audit

**Decision: reject r2. Accept the exact r3 candidate for the scoped future local release workflow tested below, subject to the stated host/file-policy limits.** This is independent review: root authored the proposed helpers; this reviewer copied frozen candidates into a separately owned exterior directory, inspected code/diffs and ran fresh adversarial fixtures plus an actual existing archive audit. No project utility, old archive, manifest, source, artwork, input, kit experiment or production build was edited. No new project release/version was created.

The reduction replaces only a new milestone's repeated local `reviews/` copy with an index referencing canonical review bytes already in that same milestone's Git source ZIP. Existing milestones/full copies/raw inputs remain where they were. The current old0.6.1 copy occupies approximately1.5G according to `du -sh`; that is the observed redundant-copy scale, not a promise of universal exact savings or a durable remote mirror.

## Frozen inputs and the r2 rejection

`frozen/` retains reviewed r2 plus the untouched0.6.1 baseline and streaming SHA helper. `frozen-r3/` retains the separately authored r3 module, Python ZIP scanner, release producer and SHA helper. Full SHA256 values are in `input-hashes.json` and recursive `EVIDENCE-MANIFEST.json`. The source diff preserves required test/build/version/clean-tree/lock/native-version/native-digest/refusal/partial-retention gates; r3 passes an absolute actual source-ZIP path to the scanner rather than an unverified basename.

R2 had two demonstrated blockers:

1. Actual metadata commit83d75e30a90db65db743a4522288607cf45682b1 has2,905 canonical review blobs, but r2 stopped at an old Windows job log whose preserved working bytes contain CRLF while Git stores LF. A Git-clean worktree does not guarantee identical raw working bytes. Four old native records differ only by CRLF normalization. They were not normalized or rewritten during this audit.
2. Fresh Git archive fixtures with `export-ignore` and `export-subst` silently omitted/rewrote canonical files, yet r2 asserted exact archive preservation because it never read the archive. Both failures are preserved in `index-results.json` and their actual ZIP fixtures.

R2's available-raw gzip checks and13 synthetic CLI release safeguards passed, but that does not override the containment/normalization blockers. One directory-raw test rejected safely with a different error string than my narrow oracle expected; that original oracle mismatch remains recorded, not relabeled a utility success. Absent-raw invalid gzip was accepted by r2; this was content-validity scope, not evidence of a valid dataset.

## Independent actual old source-archive truth

This audit used the **actual existing** `releases/0.6.1/hollowpact-0.6.1-source.zip` and exact manifest source commit **ac877b3e2bacdf5f15bf847b5ddd1d41ec94c476**. It did not pair the old archive with metadata-tag83d75 or write an index into that old version.

- Source ZIP size1,549,339,735bytes; independently streamed SHA256 **a52f59439d1e5961fe799bc223580e32c57a7db9f813c52ba96437381254128c**, matching its existing manifest.
- Independently enumerated all2,901 committed canonical review members at ac877; read all1,540,569,714 canonical bytes from the ZIP, recomputed each SHA256 and Git SHA1 blob header/content identity. Zero missing members and zero blob differences.
- Current metadata83d75 hasfour additional canonical files, explaining2,905 versus2,901. The metadata-tag author's dry run is research, not an old-archive identity. `actual-source-archive-audit.json` records both identities explicitly.
- R3 independently rescanned that same existing ac877 archive: all2,901 paths/SHA256/blob values matched my separately implemented Python audit, and allfive available raw/JSON.gz pairs were lossless. Its qualified research output is `r3-actual-existingZIP-index.json`; no old release metadata changed.

The four original working/Git normalization differences are0.4 failed-run job-log,0.4 successful job-log/native-package and0.5 native-package. R3 hashes actual canonical ZIP/Git bytes and explicitly qualifies original working CI differences. It preserves those originals. This confirms canonical source bytes; exact old native evidence/source-byte caveats in prior reports remain in force.

## Fresh r3 affected tests

`r3-index-results.json` preserves22 cases:

- Actual same-commit Git ZIP with Unicode/emoji, newline/tab, leading punctuation/glob-like quote names and binary NUL bytes: canonical paths and SHA256/blob identities match. Git path enumeration is NUL-delimited; actual filenames cannot contain NUL.
- Empty canonical tree, missing ZIP, wrong commit comment, omitted canonical member, changed blob, changed comment and duplicate ZIP members reject. `export-ignore`/`export-subst` now reject instead of claiming preservation.
- Historical CRLF working bytes remain unchanged while the source ZIP's normalized canonical bytes index correctly. The index is not a raw worktree identity certificate; producer clean-tree gating remains separate.
- Available-raw invalid/truncated gzip, equal-size mismatch, decompressed oversize/undersize and changed compressed working bytes versus source ZIP reject. Valid raw/gzip pairs verify exactly. Available raw is streamed and constrained to the expected raw byte count before comparing SHA256.
- Without a raw counterpart, valid **and invalid** compressed files remain canonical byte-preservation cases. R3 explicitly says it cannot prove the unavailable original raw value; it does not decompress/validate the absent-raw dataset. This is qualified acceptance of scope, not a dataset-validity claim.
- An additional unlisted ZIP review member is accepted but omitted from the canonical index. This is retained as a limit: the helper verifies every declared canonical review member and duplicate-name absence, **not authenticity/completeness of every arbitrary ZIP member**. The actual release producer creates its ZIP directly from the stated Git commit and later hashes the full artifact. Do not reuse the helper alone as a general hostile-ZIP authenticity check.

All22 cases completed without unexpected harness errors. The extra-member case is an intentional observed limitation, not a refusal pass.

## Release transaction safeguards

`r3-gate-results.json` preserves13 fresh **actual candidate CLI executions in synthetic scratch Git repositories**. Their package version9.9.9-independent is a fixture label only; the project package/version/release tree was never targeted. Actual npm commands ran test/build fixture stubs, and minimal real ASARs were produced with the already installed project ASAR library. These are transaction/provenance checks, not production rules quality or native game launch evidence.

All13 cases passed their declared assertions:

1. Clean synthetic success: mandatory test→build order, same source commit/ZIP/index binding, manifest/artifact creation and lock cleanup.
2. Existing version refusal before any checks; retained sentinel bytes unchanged.
3. Existing release lock refusal; original owner record unchanged.
4. Package-version mismatch refusal before tests, no version directory.
5. Test failure stops before build/archive; lock released.
6. Build failure stops before archive; lock released.
7. Dirty committed source refused after checks and before version-directory creation.
8. Gzip/index error retains web/source artifacts and `INCOMPLETE.txt`, creates no success manifest, releases lock.
9. That failed version is refused on retry and all retained partial-file hashes stay unchanged.
10. Stale ASAR version refuses and retains incomplete evidence.
11. Stale ASAR source digest refuses and retains incomplete evidence.
12. Matching minimal ASAR provenance permits its synthetic desktop archive.
13. ZIP-command error retains `INCOMPLETE.txt` and unlocks.

The corresponding13 r2 transaction cases also passed and remain preserved separately. No required gate was removed to obtain r3 acceptance. There was no SIGKILL recovery test; the existing known stale-lock/liveness handling is unchanged.

## Streaming evidence and limits

A fresh64MiB+257byte raw file plus its tracked gzip/sourceZIP passed under Node `--max-old-space-size=64`; lossless SHA256 exactly matched GNU sha256sum **1f968d73c3aa62728b987953094d9fd262f7a32316700ee7b0d0ee97108cf53b**. Python `RUSAGE_CHILDREN` measured69,544KiB child peak RSS, and the Node final RSS was70,950,912bytes. This is local utility/process accounting, not a simultaneous summed process-tree RSS ceiling or game target-hardware budget. The actual1.55GB source ZIP scan also completed, but its timing is not a commercial performance guarantee.

The first memory launcher referenced unavailable `/usr/bin/time`, yielding statusnull and starting no utility; `r3-stream-memory.json` retains that failed attempt. `stream-memory-r2.py` used the actual installed Node path/Python resource accounting; `r3-stream-memory-r2.json` records the completed successful measurement. Nothing was silently replaced.

R3 requires a **Python3 archive host**, Git and zip/tar tools already available in the Linux development workflow. It adds no npm dependency and establishes no Windows consumer install/runtime prerequisite or Windows release-host test. The scanner expects a full Git commit hash, SHA1 Git blobs and valid UTF8 paths; SHA256-format Git repositories/opaque non-UTF8 filenames are outside this implementation's supported contract. Node Python-output capture is capped16MiB, and Git enumeration has execFileSync's default buffer limit; this is not unlimited metadata-scale support.

The helper streams review payloads; ZIP central directory, the declared path list and returned index still scale with member count. It checks ZIP CRC through Python reads and actual Git blob content for declared reviews. It does not provide an overall arbitrary-hostile-archive expansion/time budget. This workflow uses the producer's own Git-generated archive.

Only **committed canonical review files** are indexed. An ignored raw file is represented only when a tracked JSON.gz counterpart exists and validates lossless while raw is available. Arbitrary ignored/untracked files elsewhere are not newly preserved by this policy. Other tracked source roots are included by the existing producer's Git archive command; this review's per-member verification is specifically canonical reviews, not every game/art member or an external storage/upload audit. Past copies, source commits, raw files and native artifacts remain untouched. No durable remote mirror, all-filesystem backup, signed authenticity or Steam/AAA/human enjoyment claim follows.

## Preservation and replication

The reviewer owns only `/workspace/scratch/preservation-v07-independent`. Preparation's earlier384-run dataset stayed frozen. Frozen helper copies and adversarial/synthetic artifacts remain intact; `EVIDENCE-MANIFEST.json` records ordinary-file SHA256/bytes plus symlink targets without following the installed dependency link. Original author files match frozen input hashes at completion.

Harnesses use this distinct scratch path. Replications must copy frozen helpers/harnesses into a **new** exterior root and adjust only harness directory literals; never rerun over completed fixture/results directories or existing project releases. A replica is new evidence with its own wrapper hashes. The exact candidate helpers accepted here may be promoted only through root's separately coordinated next-cycle source ownership and review process; this report itself does not perform promotion.
