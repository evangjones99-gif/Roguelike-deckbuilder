# Retained artifact locations

This is a location record, not a release manifest or a claim of remote backup.

## Original preflight ZIP encoding

The temporary preflight for source checkpoint `bdf27374358eb176e62f832cb50261cb3334d8df` is **not** the formal 0.7 release archive. Its exact ZIP encoding has been copied from RAM-backed storage to local disk:

| Role | Absolute path |
| --- | --- |
| Old physical TMP duplicate, reviewed retirement completed | `/tmp/hollowpact-native-v07/source-preflight-bdf27374358eb176e62f832cb50261cb3334d8df.zip` |
| Disk-backed retained original encoding | `/workspace/scratch/retained-original-archives/preflight-bdf273-original-r4.zip` |

Both full streams matched 1,856,041,104 bytes and SHA256 `e7c40a711ec970e265818d3153b02237efde959231ebc024f13a2b57c21bfef0` in the producer's actual copy and reopened-file verification. This hash was freshly measured, not recovered from a historical golden manifest. A distinct actual-transaction review accepted those observations. The independent full-new-file native check subsequently completed the entire stream with the same hash, exact protected metadata and closed readers. Earlier partial failures and admission refusals remain retained. Final storage/path-need review and producer judgment preferred the disk placement. After all current changes were pushed and confirmed at `e225cdeaab72358bf783b81bb14d055c0e20d1cd`, the single old TMP physical duplicate was retired. Separate independent post inspection confirms the old name absent and the retained full metadata unchanged; no formal release or unique encoded content was removed.

The disk copy retains the entire container encoding rather than substituting a Git bundle for unexamined ZIP contents. No logical ZIP/Git coverage claim follows from byte equality. Historical reports keep their original path references; the completed reviewed retirement removed only the obsolete physical TMP duplicate, with its decision and actual outcome recorded separately. The disk copy remains local; Git preserves the small proof records, not this 1.86 GB archive.

All formal releases, unique source/art inputs, reviews and datasets remain governed by the reviewed retention rule in AGENTS.md. Preserve what is required for rights, provenance, reproducibility, useful rollback and historical evidence. Confirm all current changes pushed before an approved cleanup transaction.
