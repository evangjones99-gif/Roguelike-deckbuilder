# Independent release-pipeline repair gate

Decision: **accept the frozen utility repair for a fresh v0.6.1 DEVELOPMENT archive attempt**. The large-file checksum failure is repaired and source scope is explicit/tested. This is not approval of an already completed archive, fresh native v0.6.1 binaries or Steam/AAA quality. v0.6.0 remains an incomplete, preserved transaction and must never be reused or labeled a successful release.

## Actual failure and exact repair

Original transaction at source26286ec6 failed while checksumming its **2863760699-byte source ZIP**, after retaining four archives and its local review/web copies. INCOMPLETE.txt records ERR_FS_FILE_TOO_LARGE from the whole-file Node read. No SHA256SUMS/manifest claiming successful0.6.0 completion exists. The failed artifacts remain in place; fresh version0.6.1 honors the existing no-overwrite policy.

| Reviewed frozen utility | SHA256 |
|---|---|
| scripts/sha256-file.mjs | `db14f59204898c15a0fc6d22893a59b85b81f171978db93d778026b3afb6b7d1` |
| scripts/release.mjs | `4c9a4a3d9519cdaac8069014b57c699fb5ca1f02c195ebd517aea7e900892b16` |

The helper iterates a real filesystem read stream into SHA256. Producer awaits every archive digest before writing sums/manifest; read failures propagate into the existing incomplete-transaction handling. Whole-file archive buffers are removed. Exclusive version-directory creation, whole-transaction lock, clean committed-source precondition, mandatory rules/build and desktop version/source guards remain unchanged.

Source archive selects NUL-delimited tracked top-level entries from the recorded source commit, excludes only releases/, passes paths as separate arguments after --, and rejects an empty include list. Canonical reviews/art inputs/datasets/source stay included once. Old milestones remain at their original paths/commits; the new ZIP explicitly does not recursively copy them. Manifest sourceArchiveScope and review-location wording reflect that distinction. Existing review copy/gzip losslessness checks remain in place; the duplicate local0.6.1 review copy is ignored for Git, not omitted by the producer.

## Independently executed evidence

- Imported the **actual production helper** and hashed a sparse2147483905-byte file containing beginning/middle/end markers. GNU coreutils sha256sum independently gives `f0519b3f1fcd4ff9ca74b9d433c30dda01e9022f4ddc177d5abeee069cf545ca`; the helper matches exactly. Fixture allocates12288 disk bytes but streams its complete logical size. Runtime about2.0seconds, sampled peak RSS94756864bytes: no whole-file allocation. The original readFileSync reproduces the2GiB failure on that same file. Empty-vector/binary-vector checks pass; absent file rejects ENOENT.
- Original newline-based source enumeration fails a real scratch Git repository containing a newline-named top-level directory. The fixed **exact production enumeration/archive fragment** passes newline/Unicode, spaces and leading-dash roots; all6 included file contents match the Git fixture exactly, ZIP CRC passes, releases/ is absent, and its original milestone marker remains unchanged. A separate releases-only repository triggers the new empty-root refusal before running archive.
- Existing project-tree oracle at26286ec6 identifies22 included roots/3088 tracked files and excludes2476 release-history copies; canonical reviews, original art and core sources are present. These counts retain that historical commit identity, rather than claiming counts for later commits.
- Actual release CLI refuses existing failed0.6.0, older0.5.0, a scratch existing lock and an invalid version before builds/output mutation. Original failed directory and scratch lock owner remain exact; no real new release transaction was launched by this reviewer. Both utility files pass Node syntax checks.

Owned probes and raw outcomes are in release-pipeline-v0.6.1-evidence/. First exact-fragment harness omitted the producer's outer version variable and raised ReferenceError; original harness/failure are retained. Corrected separateR2 passes. That was a reviewer fixture error, not a producer defect. The oracle record's beforeReleaseProducerSHA was observed after oracle hashing while root prepared its initial repair; the frozen hashes in this report/exact-scope record identify the final reviewed producer.

## Fresh runtime and remaining gates

Personally verified all27 source hashes/digest for actual v0.6.1 runtime `8720a38701aa78ccae894ba4ca7cb8656cc3072d5b023cdd9cc3d9d2b3d4c22d`. Only package.json/package-lock.json differ from accepted0ec; removing their version fields proves the parsed package/locked dependency content otherwise exact. Every engine/input/presentation/art/desktop input remains unchanged. This carries narrow source behavior assessments through matching code; it does **not** borrow version0.6.0 executable resources, exported identity or native results to certify0.6.1.

Commit the new helper/probes/review before the final clean source archive. Verify the actual resulting source ZIP against its final committed tracked scope, all runtime inputs/package bytes, every checksum and the complete six-artifact manifest before tagging. Preserve the original failed0.6.0 artifacts and actual failure receipt. Require fresh matching Windows version/runtime/resources/native interaction evidence and rebuilt Linux correspondence.

Review gzip comparisons still use whole buffers; current largest raw JSON is76133528bytes, so this does not recreate the observed archive2GiB failure. This gate establishes large-archive streaming, not unlimited single-review decompression, every filesystem fault or future arbitrary repository layout. Durable remote preservation and commercial/hardware/player acceptance remain separate requirements.
