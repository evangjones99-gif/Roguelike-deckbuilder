# Independent native Windows package byte audit — Hollowpact 0.7.0

**Decision: accept this exact original Windows development package for milestone archival, alongside the separate accepted native CI receipt review.** All wrapper/part/full ZIP/extracted payload checks passed. This byte audit does not add a second Windows launch, installer acceptance, native six-pose animation coverage, human playtest consensus, Steam/Steam Deck verification or AAA-quality claim. Durable preservation and archive-capacity checks remain the root agent's separate responsibility.

Reviewer `/root/hunter_technical_independent` owns only this new exterior directory. No package, production source, dist, old review, retained version, dependency or release directory was written. Used the project's existing ZIP, ASAR and PE inspection tools. Source checkpoint `bdf27374358eb176e62f832cb50261cb3334d8df`; actual CI PR merge `debf73893c4e1d9acc163784a425bb0c12492ec4`; native run `36797759232`. These identities are distinct and match the original small CI evidence.

## Original transfer and all 72 files

Independently read all eight unchanged downloaded GitHub wrapper ZIPs from the root download records. Each wrapper's actual size/SHA-256 matches the reviewer's original GitHub artifact API snapshot; ZIP CRC passes and it contains exactly the corresponding expected `part-NN.bin`. Each inner part's actual size/SHA-256 matches the original small CI transfer manifest. Every streamed byte of ordered parts matches the reconstructed ZIP directly, without rebuilding, recompressing, writing or relabelling it.

Original native ZIP: `/tmp/hollowpact-native-v07/windows-native/hollowpact-0.7.0-windows-native-x64.zip`, **185,715,968 bytes**, SHA-256 **`256babeb74761b0608ae8be249f30f475522c70f86c0fd377f1bef737fb35fbe`**. Full CRC passes. All **72** members are unique, including case-insensitive uniqueness, and have safe relative paths without traversal, backslashes, drive markers or symbolic links. No additional extracted files are present. Every member was streamed against its extracted original bytes and hashed against all 72 native CI `packageFiles` entries; every byte and hash matches. Complete per-file byte counts/SHA-256, wrapper and inner-part hashes appear in `transfer-and-files.json`.

## ASAR, frozen source and original artwork

Actual Windows ASAR and the root's temporary Linux ASAR both hash **`e270b1fc9626f6df915449200d00f86cd593e3ca70876832436dd90ef7e6d3da`**, identical to the actual native CI ASAR hash. Each contains exactly **18 leaf files**: 15 dist files, two desktop files and package.json. All **17 dist/desktop** files are byte-identical to the current frozen files, including embedded build ID, relative `./art/hunter-marek-v07-r3.png` URL, current desktop shell security and complete credits. Both package.json records identify version `0.7.0` and main `desktop/main.cjs`.

Independently hashed all **29** runtime inputs and recomputed the ordered source digest: **`0be4f01d416e6fc4cca3f19b6916b5b65993b9fd426a926a1ede6d8487834a35`**. Both actual ASAR provenance objects equal the frozen local build provenance. All packaged public assets and desktop files match the corresponding source hashes. The hunter sheet is the original **2,128,117-byte**, **1536×1024** PNG, SHA-256 **`4492577d3bacc868e9b66da0abf25915bdeaf68bc8f5c31ae8a1d8db485f3c53`**, unchanged in both packages. Electron/Chromium license bytes were checked and are included. Detailed source/payload/license/ASAR records appear in `runtime-and-pe.json`.

## Actual executable resources and unsigned status

Actual original extracted `Hollowpact.exe` hashes **`4826913dc241a791373e690a0a822f8137fc1822c4c03f069b1148238e323640`**, matching actual native CI and archive receipts. Existing ResEdit read-only parsing identifies x86-64 PE (`0x8664`, PE32+ `0x20b`), seven icon resources and the complete size group (16, 24, 32, 48, 64, 128 and 256 pixels). Every resource hash and version structure equals the native CI evidence. Actual ProductName is **Hollowpact**, FileVersion **0.7.0**, ProductVersion **0.7.0.0**. The actual PE certificate table has offset **0**, size **0**, agreeing with CI's `NotSigned`. Builder settings retain executable resource editing (`signAndEditExecutable: true`), with signing disabled and no force signing. This is an unsigned directory package, not a signed installer.

## Preservation and acceptance limits

The previous native CI review's manifest SHA-256 `45fe59963cb9aefc046c6a65c024fabdadc02275d4af88ba748a671857557e1c` and all **141** recorded files—including original BOM/CRLF job logs, original small-artifact extracted members and the failed earlier packaging evidence—were verified unchanged. Original previous report SHA-256 remains `f56ac7e0aef0f76e61dde2df93aa86535dacc37cd7df79627154a7be71cc56cc`. This supplement resolves that report's then-pending full ZIP byte audit; it does not overwrite or rewrite that historical scope.

Actual Windows execution is the separate CI run already reviewed, with 13 automated phases, sandbox enabled, exact canonical save hashes, eight actual packaged idle-cell hunter draws and explicit local synthetic feedback. This new review verifies that the bytes being archived are exactly those tested. It does not broaden the single hosted-runner, unsigned package, automated-input, synthetic-feedback, no-installer/no-Steam/no-Steam-Deck/no-physical-controller/no-audio-listening/no-human-fun limitations. No blocker was found in this exact package. Root must preserve the original ZIP durably and verify the retained milestone archives before calling the milestone archived.

Reproducible review scripts: `audit-transfer.py` and `audit-runtime.mjs`. No dependency was installed or changed.
