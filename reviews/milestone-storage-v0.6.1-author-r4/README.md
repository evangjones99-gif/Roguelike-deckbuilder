# Fixed v0.6.1 native draft preservation — R4 AUTHOR repair

**Frozen exterior proposal, not an executed preservation workflow. No production edits, promotion, push, trigger or live GitHub release writes.** Intended reviewed bootstrap path remains only `.github/workflows/preserve-v061.yml`. Root promotion and fresh independent review must precede activation.

Selected workflow SHA256: `a9641339213d6a42808df1d1504ed49f1eda3d9e18f8e2bbfb8ec735d759aa9d`.

## Concrete independent rejection and minimal correction

Independent reviewer `/root/audio_host_independent` withheld R3 because an upload response with a wrong `asset.name`, correct size and correct downloadable bytes passed. The workflow then reported official filenames despite the returned assets being named `UNEXPECTED-*`. Exact independent witness/helper/17-case summary and frozen REVIEW-R3 are copied unchanged under `independent-r3-failure/`; the source witness remains `/workspace/scratch/milestone-storage-v061-independent/upload-name-witness/mock-results/wrong-upload-name-accepted-witness.json`. This is a mocked API-contract failure, not evidence that a live upload actually returned that name.

R4 adds exactly one runtime guard before size/readback/reporting, for both uploaded and matching existing assets:

```js
check(asset && typeof asset === 'object' && asset.name === filename && Number.isSafeInteger(asset.id) && asset.id > 0, `Stored ${filename} asset identity mismatch; no overwrite attempted`);
```

`r3-to-r4.patch` contains the complete one-line workflow delta. Names must match exactly; ID must be a positive safe numeric integer, rejecting missing/null/string/fraction/zero/negative/unsafe values and malformed response shapes. The existing fixed download-endpoint regex remains unchanged. Invalid responses fail before their body is downloaded or they are added to verified report assets. An already completed upload can remain in a partial draft on refusal; it is not renamed, overwritten or deleted.

Normal listed assets with unrelated names remain untouched and are not selected as the official asset; a missing official file is uploaded once under its correct name. This is intentional existing-draft behavior, not a malformed matching-name acceptance. A malformed matching-name asset ID is refused before any upload or readback. Existing JSON name matching is already exact in the filter; the new guard also validates the response used after upload.

No tag, commit, repository, branch, artifact, checksum, byte bound, timer, token/redirect behavior, privilege, action pin, release capability, coverage statement, final-draft or readback condition changed. `README-r3.md` and historical `README-r2.md` retain the complete specification and qualifiers; their candidate hashes are historical. Original R2/R3 directories remain frozen and unchanged.

## Executed author evidence

**117 final exact-inline-JavaScript workflow mocks pass**, preserved in `mock-summary.json` / `mock-results/`: all 75 prior cases plus 42 affected cases. Fresh coverage includes wrong returned upload names independently at each of the five upload positions; eleven invalid ID forms for both new and existing matching assets; missing/null/numeric names; null/absent/scalar/empty-object/array responses; preserving an unrelated existing name while adding the correct file; null existing entries; stale readback bytes; and malformed pre-upload/final draft states and a changed final body marker. Assertions retain prior verified counts, forbid invalid-ID/name readback, and confirm unrelated assets are untouched. The prior all-five readback corruption, idempotence, token isolation, metadata pins, byte bounds and final-draft tests remain passing.

**Eight exact-R3 baseline probes** in `r3-asset-identity-baseline-results/` reproduce acceptance of first/last wrong upload names, string new/existing IDs, unsafe new numeric IDs, and missing/null/numeric upload names with otherwise correct mocked bytes/size. They are preserved failures of the prior guard contract, not R4 successes. A first baseline helper attempt incorrectly stored string IDs as string Map keys while decoding HTTP resource IDs numerically, causing an accidental mock refusal. Its original helper, first two results and error/cause are retained in `baseline-r1-failure.json` and `r3-asset-identity-baseline-r1*`; the corrected HTTP mock indexes resources numerically. No runtime change was made for that helper defect.

The exact R4 extraction/helper validation also passes the existing YAML policy/script-correspondence/action pin checks and **12 real tiny-ZIP subprocess probes**. Real local original native/evidence SHA256 checks still match the pinned manifest with bounded 1 MiB reads. No large artifact copy/download occurred. Large mock payloads use virtual size/hash objects; metadata/coverage uses real crypto. These author checks prove guard/control-flow behavior, not actual server transfer, runner execution or remote asset identity. No actionlint/live runner claim is made.

## Scope and later live proof

This fixed operation preserves exactly two of six release archives: the original native Windows ZIP and original evidence ZIP, plus unchanged manifest/SHA256SUMS and explicit coverage, making five verified assets. The full native wrapper is artifact **11132128179**, **192975515 bytes**, SHA256 `ee181194451f10e601742fa4a570303e7ed6e66c79a2a7c58555bb2feb91b8d4`; evidence is artifact **11131988966**, **9545515 bytes**, SHA256 `1741107cb452d08eb9c2f33a02f8ff1c64076776892b512cd075747adff6f047`. Saved authenticated GitHub GET metadata pins run **36791619534**, attempt **1**, head `9e6e7d7e76a2ce606acae24d2f6a27c903b54a5f`, and existing annotated tag `cb1c3964d4865ae729807fcb3208b6d856bd25fc` targeting `83d75e30a90db65db743a4522288607cf45682b1`. The recorded source archive commit `ac877b3e2bacdf5f15bf847b5ddd1d41ec94c476` is distinct. Artifacts were unexpired at read; their October 30 expiration is rechecked by the job, not reserved by this proposal.

The old v0.4 workflow remains SHA256 `90d317a7207b8a6e66e52b016d4e8024a4244730719b0157863ce0b71d31f81f`. No old release/input/review was modified. No arbitrary refs/URLs/payloads, checkout/build/dependency/artifact code execution, replacement/delete/publish/Steam operations are added. Draft storage is deletable and partial; it is not immutable storage, a complete remote mirror, an independent backup, public commercial release or Steam/AAA/human-fun acceptance. Five successful live readbacks, actual release/asset IDs, a matching release that remains draft, and retained live diagnostics are still required after authorized activation. Existing failures can leave partial assets, which retries verify without clobbering.

The only authorized scope completed here is this new exterior proposal and its preserved author evidence. `FROZEN-FILES.json` hashes retained files except itself. Helpers regenerate outputs; reproduce only in a new exterior copy. Read copied old manifests as historical records for their original directories, not manifests for current renamed R4 files.
