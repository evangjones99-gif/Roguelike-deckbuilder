# Narrow closed-object cache-hint tool, authored only

**NO EXECUTION OR EXECUTION ACCEPTANCE.** Exact18,396B `closed_cache_hint.py` SHA256 **479e98a13cdcf58f181f3747fea3a093faf00a61bce1fa9abd861c26c8a1f9b5** is independently reviewable. Only Python AST parsing ran. No hints, Git body reads, object SHA streams, process/runtime audit, source/ref mutations or claimed RAM gain occurred. Root requested this distinct implementation; another agent must review it before a root-only attempt.

Scope is the fresh immutable1,020-file allowlist SHA `3e6280ec7a1825f0b43e92f87f4bcd44ef37d9397064563bb037ebdf5f834bd6` at `/dev/shm/hollowpact-git-cache-allowlist-independent-hm3eony7/ALLOWLIST.json.gz`. Schema has scope,inputSHA256,rootFinishedSHA256,objects; rows contain oid,ten metadata fields,atimeNs,xattrs(hex bytes) and encodedSHA256FromPriorProof. Existing full encoded-SHA and raw-object preservation proofs are references, not new byte claims. The prior immutable feasibility protocol is `/workspace/scratch/git-closed-cache-feasibility-independent-v09-r1/REVIEW.md`. Allowlist is an external ephemeral metadata dependency, not archived source data; a real run must pin it unchanged and copies it durably before advice.

The tool hardcodes the exact repository/objects root and prior INPUTS/FINISHED/independent finish-review hashes. It requires the same full allowlist, explicit fresh root closure declaration and independent implementation acceptance. Output must be a previously nonexistent `/workspace/scratch/git-closed-cache-hint-run-<identifier>` directory. No arbitrary object path or generic cache target can be supplied. Controls are bounded, anchored no-follow/no-atime reads; O_PATH directory components perform no data read/atime update on root-owned ancestors. Readable membership directories and actual object leaves require O_NOATIME; unsupported/permission failures refuse, with no fallback. O_NONBLOCK avoids unexpected special-file blocking, and regular-file identity is mandatory.

Before **any** hint, all1,020 membership/descriptor/path full metadata,atime,xattrs match the pinned rows. Every descriptor closes. A durable complete metadata preflight then permits the per-file phase. Each reopened file is checked again, with anchored path/fanout identity, measured128MiB work+512MiB cgroup reserve and fresh declaration. There is no object-descriptor read call. Only after acceptance and a durable armed record does `posix_fadvise(fd,0,0,POSIX_FADV_DONTNEED)` run. Full metadata/atime/xattrs are checked afterward; a durable returned record and close follow. Final complete membership/full metadata check precedes closure andthree cgroup current/stat/events samples50ms apart. Samples do not infer object residency, causal gain or permission to launch another operation; that operation must independently admit its own guard.

The bounded live-FD observation scans currently visible processes, skips actual zombie/dead states, checks target dev/inode against accessible live descriptors and permits only the tool's own current metadata FD. It runs before all hints and again for each target. Permission/incomplete/unknown probes refuse, rather than asserting absence of all readers. Process count is bounded8,192; live descriptors16,384 per observation; memory guard repeats during observation. This does not inspect mappings or create an atomic exclusion lock. Root's explicit ownership/quiescence declaration remains essential. FD races and reused process identities are not an adversarial guarantee. Cost is **unmeasured**; repeated scans may be slow and the300-second root declaration expires, stopping the attempt without further hints. A refusal must be preserved; do not diagnose indefinitely or waive unknown ownership/reserve to obtain a success.

Receipts reserve768KiB maximum plus remaining1MiB durable space before control work; per-file stream is bounded512KiB. New files/directories are exclusive and fsynced. A16KiB padded valid-JSON failure slot is preallocated and fsynced before checks, so a later refusal can record partial outcome without allocating additional blocks. Successful runs leave its explicit reserved/no-failure status. Armed and returned JSONL records carry metadata-only digests referencing durable allowlist/preflight; they are **not object-content hashes**. If interrupted between records, an armed record is an unknown outcome, never a claimed success. Failure preserves all earlier records/hints and stops; no rollback/cache flush/global sync/cgroup mutation/lock deletion/process kill is implemented. The new owned failure slot can be updated; old inputs/reports are never overwritten.

Root declaration JSON requirements, all checked literally:

```
repository: "/workspace/Roguelike-deckbuilder"
sourceSHA256: "479e98a13cdcf58f181f3747fea3a093faf00a61bce1fa9abd861c26c8a1f9b5"
allowlistSHA256: "3e6280ec7a1825f0b43e92f87f4bcd44ef37d9397064563bb037ebdf5f834bd6"
finishReviewSHA256: "8dfecded2b70774c6562d30532419a07fd1afc04b6eb4c195c2bc08fc21d2e2b"
scope: "Only pinned1020 immutable loose encodings; no bodies read; no other files advised"
affectedReadersClosed: true
affectedWritersAndMaintenanceHeld: true
affectedInodeAliasesQuiescent: true
noUnknownAffectedLockOwner: true
runtimeProcessesClosed: true
issuedUnixSeconds: <fresh root timestamp; age between -5 and300 seconds>
```

These are root declarations about coordinated ownership, **not facts created by writing true** and not a global FD-absence claim. The declaration body must stay unchanged throughout the attempt. Independently supplied acceptance requires sourceSHA256,allowlistSHA256,allowHintAttemptOnly:true,reviewPath and reviewSHA256; exact review bytes are checked. This author report is not the independent acceptance, and no acceptance/declaration file is fabricated here.

Only after independent review and root's genuine closure, the contemplated invocation is:

```
python3 /workspace/scratch/git-closed-cache-hint-author-r1/closed_cache_hint.py \
  --allowlist /dev/shm/hollowpact-git-cache-allowlist-independent-hm3eony7/ALLOWLIST.json.gz \
  --declaration <absolute root declaration> --acceptance <absolute independent acceptance> \
  --output /workspace/scratch/git-closed-cache-hint-run-r1
```

No command above ran. Advice can return successfully and reclaim zero, may cause existing dirty-page writeback, and can be followed by cache refill. No global flush, old-pack/ref/archive hint, body-read shortcut, source backup, archive solution, consumer/hardware qualification or production milestone follows. Root can close this cache window and resume its separately authorized installer push if the probe refuses.
