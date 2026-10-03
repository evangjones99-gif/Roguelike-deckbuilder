# Independent actual v0.6.1 partial draft-storage audit

Verdict: **accepted actual partial draft preservation**. Read-only GitHub snapshots taken on 2026-10-01 and a new independently authored verifier agree with the original successful diagnostic. This verifies the stated storage scope, not gameplay quality or a public release.

## Exact executed source and diagnostic

- Actual run **36797748556**, attempt **1**, head **bdf27374358eb176e62f832cb50261cb3334d8df**, `push` on `codex/lanternbound-production`, `.github/workflows/preserve-v061.yml`: completed/success. Its single job **110164968568** and recorded steps succeeded.
- Independently fetched workflow at that head is byte-identical to the independently approved R4 workflow and current repository file: SHA256 **a9641339213d6a42808df1d1504ed49f1eda3d9e18f8e2bbfb8ec735d759aa9d**. It includes the asset-object/exact-name/positive-safe-integer-ID guard missing from rejected R3.
- Diagnostic artifact **11134083866**: original ZIP **850 bytes**, SHA256 **7fcf1a6b197549bac44b5885793c9383b5b6218b841145c4e21c4346137ead66**. Independently retrieved metadata matches the locally preserved original wrapper, unexpired until 2026-10-31T00:45:58Z. The ZIP has exactly `report.json`; its decoded bytes equal the retained raw report. Report SHA256 **d06250794536eefa11b7ef48bc293d743482593262643dd6b74c16e836476fc5**.
- The raw report says `passed-draft-partial-preservation`, `partial-native-windows-and-original-evidence`, with five `readBackVerified: true` entries. Those full remote byte downloads/hash checks were performed by the actual approved workflow, **not repeated by this independent audit**.

## Independent verification

`verify.py` ran successfully against newly fetched API responses and copied original local diagnostic inputs. No credentials, external writes, uploads, workflow triggers, native binary download, executable installation or downloaded-code execution occurred. Independent network operations were GET-only metadata and the small pinned manifest/checksums/workflow source files. Responses are retained exactly inside their tool-result wrappers.

Annotated `v0.6.1` still resolves to tag object **cb1c3964d4865ae729807fcb3208b6d856bd25fc**, commit **83d75e30a90db65db743a4522288607cf45682b1**. The fetched pinned manifest SHA256 is **6999e88dfc4b19626e50734571e997c9fd19b1a5c2e4ce9439159343160fd500**; checksums SHA256 is **66ea71f543eb0c2bd29bcb80538b41db22eb21c655c28dafaf18aa54fc5542c1**. Their six archive entries agree exactly. Source archive commit `ac877b3e2bacdf5f15bf847b5ddd1d41ec94c476` and runtime digest `8720a38701aa78ccae894ba4ca7cb8656cc3072d5b023cdd9cc3d9d2b3d4c22d` remain separate identities; storage does not rebuild them.

Independent current metadata also confirms original native run **36791619534**, attempt 1, success, head **9e6e7d7e76a2ce606acae24d2f6a27c903b54a5f**, Windows-validation workflow. Original native Actions wrapper **11132128179** remains unexpired, 192975515 bytes, SHA256 `ee181194451f10e601742fa4a570303e7ed6e66c79a2a7c58555bb2feb91b8d4`; evidence **11131988966** remains unexpired, 9545515 bytes, SHA256 `1741107cb452d08eb9c2f33a02f8ff1c64076776892b512cd075747adff6f047`. This audit checks their metadata; extraction and byte verification are workflow evidence.

Release **400547880** is presently `draft: true`, `prerelease: true`, `tag_name: v0.6.1`, `published_at: null`. Its body explicitly states development-only, partial coverage and no Steam publication. Exactly five unique uploaded assets match report identities, sizes and live API digests:

| Asset | ID | Bytes | SHA256 |
| --- | ---: | ---: | --- |
| hollowpact-0.6.1-windows-native-x64.zip | 602099580 | 183597187 | 06e48cce30ccd2a8fcfcc7a829ec79d3fa6b628541a19effa368852df0bce90b |
| hollowpact-0.6.1-native-evidence-36791619534-1.zip | 602099837 | 9545515 | 1741107cb452d08eb9c2f33a02f8ff1c64076776892b512cd075747adff6f047 |
| manifest.json | 602099865 | 2754 | 6999e88dfc4b19626e50734571e997c9fd19b1a5c2e4ce9439159343160fd500 |
| SHA256SUMS | 602099879 | 607 | 66ea71f543eb0c2bd29bcb80538b41db22eb21c655c28dafaf18aa54fc5542c1 |
| preservation-coverage.json | 602099901 | 884 | 53c5043cf2c3443a3eebb684130f6da55695f7dafe1f0253cf293c88b37fbf4e |

The coverage bytes were independently reconstructed from the exact reviewed workflow and fetched pinned manifest. Their 884-byte length/hash matches both actual asset metadata and diagnostic. This audit did not fetch the remote coverage body separately. Coverage preserves native Windows and original native evidence only; Linux, source, web and repacked Windows archive names are absent from the actual release. `draft/developmentOnly` are true; `commercialQualityAccepted/steamPublished` are false.

## Retained negatives and limits

Rejected R3 workflow SHA256 **70a5bb168df51a5c3b2caa532af89bdce0911e6f21aa26259c2759e5457776ba**, its original independent review and wrong-upload-name witness are copied without altering the old frozen directories. The witness remains an adversarial mock using qualified virtual large payloads; it is not a claim GitHub returned malformed assets. R4's accepted negative testing remains source-review evidence, separate from this actual run. Root's failed initial Python release-snapshot attempt is retained verbatim as `root-snapshot-r1-error.txt`; its corrected snapshot is copied separately. No new verifier failure occurred.

This is longer-lived **partial** draft storage, not a six-archive remote mirror, immutable backup, published game or Steam publication. The job's narrow permissions, no checkout/build/dependency install, token-only-to-API downloads and bounds remain those of the approved immutable source review. A privileged administrator may subsequently change/delete a draft; these snapshots establish observed state, not an atomic future guarantee. No consumer installation, physical controller, audible timbre, human enjoyment, Windows/Steam Deck compatibility or AAA craft certification was performed in this storage audit. Original game-quality limitations remain valid.

`verification.json` records actual verification time and scope. `SHA256.json` freezes every new audit file except itself. No production repository file or prior review/release was modified by this reviewer.
