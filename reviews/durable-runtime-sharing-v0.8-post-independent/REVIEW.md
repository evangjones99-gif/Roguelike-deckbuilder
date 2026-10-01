# Independent actual durable-runtime consolidation postgate

ACCEPTED for the measured storage transaction. This is a read-only check of actual poststate, not approval of gameplay, visuals, native installers or release readiness.

Fresh full-file streaming SHA-256 and lstat/xattr checks pass for all 432 original regular files across six unchanged directory paths. Sizes, modes, uid/gid and xattrs match the frozen independent inventory and root pretransaction snapshot. All 18 directory memberships, modes, ownership, inode identity and restored mtime pass. All 141 shared groups have one inode each, equal bytes and metadata, and link counts account for every alias inside the inventory: no unaccounted outside aliases. All 281 unique atomic-operation journal entries match original and actual inode identities and full hashes. The helper has the required SHA-256 `4de719bd0bfd04f7dac75cf425fc29735005da48a4d4a7268f611e62a726beff`.

The 422 shared paths contain only previously inventoried stock-runtime leaves/locales. All ten excluded regular files, including unique resources/app.asar, retain their original complete bytes and stable metadata (inode, ctime, nlink, mtime, uid/gid, modes, blocks and xattrs). Directory membership proves no new temporary leaves remain. Every source inventory, helper and transaction receipt is hashed again after inspection.

All **35** current sealed official release archives independently match full SHA-256 in their original SHA256SUMS: the requested 30 retained archives through v0.6.1, plus five v0.7 archives. Incomplete v0.6.0 is excluded. No archive was modified. This establishes archive-byte equality against retained sealed ledgers; no nonexistent fresh pretransaction archive inode/timestamp snapshot is claimed.

The original forecast was 1,117,147,136 allocated bytes. Root observed 1,116,823,552 bytes of free-space increase; this measurement includes unrelated concurrent workspace writers and is not an isolated exact saving claim. Current free-space snapshots are retained in RESULTS.json.

Sharing intentionally changes inode, nlink, ctime and differing per-file timestamps to canonical metadata. Root retained original per-path snapshots and restored directory atime/mtime; subsequent readers can change atime. Directory ctime is not restored. Shared stock files are immutable by usage contract, not chmod enforcement: any later build must write fresh independent files instead of modifying these aliases. Old game data, art, profiles, datasets, official archives and every original path remain preserved. No reviewed input was mutated by this agent; only this new review packet was written.

Evidence: verify.py, RESULTS.json (450 metadata rows, 141 groups), ARCHIVES.json (35 full archive identities and seven sealed ledgers), stdout and empty stderr. No live remote writes or source/build changes were performed.
