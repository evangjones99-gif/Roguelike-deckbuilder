# Independent retained working-copy capacity review

**Accepted for a separately executed, verified relocation; no relocation has occurred.** All seven candidate trees contain exactly 504 regular files, totalling **2,644,517,293 logical bytes**. Every byte matches a preserved complete official release archive whose SHA-256 was checked against that release's SHA256SUMS before and after streaming comparison. Every working inventory was measured before and after comparison and was unchanged. No extraction, deletion, move, source edit or archive write occurred.

| Case | Candidate directory | Files | Logical bytes | Recovery proof |
| --- | --- | ---: | ---: | --- |
| 1 | `/workspace/scratch/retained-working-linux-0.4.0-da553781de9d` | 72 | 312,213,615 | Direct official archive |
| 2 | `/workspace/scratch/retained-working-linux-0.5.0-d6221bf764ba` | 72 | 317,356,081 | Direct official archive |
| 3 | `/workspace/scratch/retained-working-windows-0.4.0-da553781de9d` | 72 | 400,962,215 | Direct official archive |
| 4 | `/workspace/scratch/retained-working-windows-0.5.0-d6221bf764ba` | 72 | 406,104,681 | Direct official archive |
| 5 | `/workspace/scratch/native-windows-v04/retained-working-v0.3-win-unpacked` | 72 | 400,813,805 | Direct official archive |
| 6 | `/workspace/scratch/native-windows-v04/run-36772521612-1/win-unpacked` | 72 | 400,962,215 | Native content + cross-platform ZIP modes |
| 7 | `/workspace/scratch/native-windows-v05/run-36782560136-1/native-extracted` | 72 | 406,104,681 | Native content + cross-platform ZIP modes |

There are **2,645,671,936 allocated regular-file bytes**, 504 distinct device/inode identities and no file link count above one. This excludes directory allocation and does not guarantee that a later filesystem reports exactly this many free bytes. Five direct archive/mode matches provide 1,837,450,397 bytes. Adding case 6 provides 2,238,412,612 bytes; all seven provide 2,644,517,293 bytes. Root may choose a smaller sufficient subset after a fresh target-capacity check.

The original native-tested Windows ZIPs use DOS metadata and carry no Unix modes. I **reject** any claim that those ZIPs alone preserve POSIX modes. Cases 6 and 7 nevertheless match all 72 file sizes, hashes **and** POSIX modes in their corresponding preserved 0.4/0.5 cross-platform Windows ZIPs. CROSS-ARCHIVE-MODES.json names those explicit alternative archives. Native ZIPs independently match every content byte. No evidence from incomplete 0.6.0 is used.

Linux TARs explicitly include the three directories and their modes. Windows ZIP directories are implicit. Every original directory's mode is recorded in the respective working inventory sidecar; reproducing Windows extraction directories must apply those recorded modes. I do not claim those directory modes are encoded in the ZIPs. No symlink or special leaf exists inside these trees.

This is a pre-move capacity finding, not a post-move acceptance or a new native/platform certification. Root must preserve this inventory durably, copy/move the exact working trees only to fresh uniquely owned TMP destinations, compare every regular file's SHA/size/mode and every directory mode after transfer, retain original paths as explicit symlinks, and recheck original official archives. Original inode identities will legitimately change across filesystems. Report that location change. Do not treat TMP as a durable backup: the complete official release archives plus this mode inventory are the durable reconstruction evidence. Keep all version archives, native transfer parts, wrappers, reviews, source inputs and distinct variants untouched.

Investigation scripts and full per-file inventories are included. run.stderr.txt and cross.stderr.txt are empty. The source tree/archive metadata were only read. Relocation may proceed only under root's separate ownership and verification; this reviewer has not modified any candidate.
