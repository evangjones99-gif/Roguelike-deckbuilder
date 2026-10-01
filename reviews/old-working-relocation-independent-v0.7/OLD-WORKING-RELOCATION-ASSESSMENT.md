# Independent duplicate working-copy relocation assessment

Accept relocating the two retained old 0.6.1 unpacked QA comparison directories to temporary storage, retaining their original scratch paths as symlinks, subject to exact post-move hash/mode comparison and explicit temporary-scope metadata. No unique file bytes need be lost: every existing file is represented by the untouched official durable native archives. This reviewer performed only reads and created exterior evidence; no file or directory was moved or deleted.

Independently enumerated and hashed actual retained Linux/Windows directories from `reviews/root-v0.7-source-capacity/retained-old-working-packages.json`; each of all root-recorded byte counts and hashes matches. Streamed original official archives and compared complete file sets and bytes:

- Linux: **72 files / 317,369,654 bytes**, exact official `hollowpact-0.6.1-linux-x64.tar.gz`; every archived file permission mode also equals the working mode, zero differences.
- Windows: **72 files / 406,118,254 bytes**, exact official `hollowpact-0.6.1-windows-native-x64.zip`, CRC passes.
- Total duplicated regular-file payload **723,487,908 bytes**. All file sets match completely, with no working-only file or unrepresented bytes. Original actual working permission modes are independently recorded in the comparison JSON for post-move checks; Windows ZIP permissions are not used as native Windows file-security acceptance.

Independently hashed **all six** official 0.6.1 archive files; every complete size/SHA-256 matches the existing immutable milestone manifest. These archives, source, review tree and other old versions must remain in durable storage at unchanged paths/hashes. The proposed relocation concerns duplicated working QA files, not durable version archives, art inputs, datasets or unique reviews. Temporary /tmp comparisons do not become a durable archive or a second tested native installation by being relocated; exact old baseline recovery remains backed by the existing official native archives.

Root must retain mapping paths, verify all 144 after-move file bytes/modes, preserve accessible scratch-path symlinks, verify official archive hashes unchanged, and recompute actual free capacity before new milestone creation. This operational acceptance does not approve the still-unfrozen opt-in bundle utility, certify adequate future capacity, or add game-quality/runtime claims.

Evidence: `old-working-official-archive-byte-comparison.json`, `old-six-official-archive-hashes.json`.
