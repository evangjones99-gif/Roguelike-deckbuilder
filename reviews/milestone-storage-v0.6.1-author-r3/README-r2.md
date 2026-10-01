# Fixed v0.6.1 draft native preservation proposal — AUTHOR QA, not live preservation

This is a new exterior author proposal. It does not edit production files, the old v0.4 workflow, release manifests, binaries or Git refs, and it has not been pushed or triggered. Root promotion and genuinely independent review are required before activation. Intended new production path: `.github/workflows/preserve-v061.yml` only. Copying/pushing that file on `codex/lanternbound-production` intentionally activates the fixed privileged job; ordinary runtime/docs changes do not match its path filter. GitHub path filters do not require every other changed path in that commit to be absent; the intended reviewed bootstrap commit must contain only the new workflow path.

The final proposed workflow SHA256 is `5ae1a43671e156e0b7bd7c14565e23ae216dc5079c3426c52a2e1accc00bb9d9`. Existing v0.4 workflow remains byte-identical SHA256 `90d317a7207b8a6e66e52b016d4e8024a4244730719b0157863ce0b71d31f81f`. The initial successful author revision is retained as `proposal-r1.yml`, `workflow-script-r1.js`, `mock-summary-r1.json` and `mock-results-r1/`; the final revision additionally redacts the supplied token from caught API error messages. No failed or partial real storage run occurred here.

## Verified immutable identities

GitHub connector GET reads saved in `github-read-metadata.json` and `github-annotated-tag.json` discovered the full native wrapper rather than inferring IDs from the nine locally retained bounded transfer wrappers. The annotated tag and target agree with the local immutable tag.

| Item | Pin |
| --- | --- |
| Repository / branch | `evangjones99-gif/Roguelike-deckbuilder` / `codex/lanternbound-production` |
| Existing tag / annotated object | `v0.6.1` / `cb1c3964d4865ae729807fcb3208b6d856bd25fc` |
| Metadata tag target | `83d75e30a90db65db743a4522288607cf45682b1` |
| Source archive source commit | `ac877b3e2bacdf5f15bf847b5ddd1d41ec94c476` — distinct from the metadata commit |
| Manifest SHA256 | `6999e88dfc4b19626e50734571e997c9fd19b1a5c2e4ce9439159343160fd500` |
| Checksums SHA256 | `66ea71f543eb0c2bd29bcb80538b41db22eb21c655c28dafaf18aa54fc5542c1` |
| Runtime digest | `8720a38701aa78ccae894ba4ca7cb8656cc3072d5b023cdd9cc3d9d2b3d4c22d` |
| Successful native run / attempt | `36791619534` / `1` |
| Native run head | `9e6e7d7e76a2ce606acae24d2f6a27c903b54a5f` |
| Actual recorded PR merge checkout | `913577b23eede5acec79be1b6938dbb86dad0ab7` — not substituted for run head |
| Full native Actions artifact | ID `11132128179`; name `hollowpact-0.6.1-windows-x64-36791619534-1`; `192975515` bytes; SHA256 `ee181194451f10e601742fa4a570303e7ed6e66c79a2a7c58555bb2feb91b8d4` |
| Inner original native ZIP | `hollowpact-0.6.1-windows-native-x64.zip`; `183597187` bytes; SHA256 `06e48cce30ccd2a8fcfcc7a829ec79d3fa6b628541a19effa368852df0bce90b` |
| Original evidence Actions ZIP | ID `11131988966`; name `hollowpact-0.6.1-windows-evidence-36791619534-1`; `9545515` bytes; SHA256 `1741107cb452d08eb9c2f33a02f8ff1c64076776892b512cd075747adff6f047` |
| Official evidence filename | `hollowpact-0.6.1-native-evidence-36791619534-1.zip` |

Both full artifacts were unexpired at the recorded GET read. Native wrapper expiration: `2026-10-30T23:35:07Z`; evidence expiration: `2026-10-30T23:34:42Z`. Expiration and digest are checked again by the proposed live job; this report cannot reserve their future availability. Full wrapper SHA256 is GitHub's metadata digest, not a new local download verification. The original inner native/evidence bytes were independently streamed from the existing local release files in 1 MiB chunks and matched their official hashes; no large artifact was copied or downloaded.

## Fixed capability and failure behavior

The workflow has no version/run/ref/URL payload input; manual dispatch accepts only a boolean confirmation. Both YAML and inline code require the exact repository/production branch and push or confirmed dispatch. Push is restricted by the new workflow path. No PR trigger, checkout, build, dependency installation or downloaded executable/script occurs. The privileged job grants `contents: write` and `actions: read` only, with 15-minute timeout, a version-specific non-cancelling concurrency group, and the same previously verified full action SHAs as v0.4. An `always()` diagnostic step preserves only `report.json` for 30 days.

Tag object/target, pinned metadata hashes, six-archive manifest/checksum correspondence, native run ID/status/conclusion/attempt/path/repository/head/branch, and each artifact ID/name/size/head/branch/digest/expiry are checked before draft creation. Body downloads are bounded by exact expected bytes, a 200 MiB ceiling and 180-second requests; headers, actual byte length and SHA256 are checked. At least 500 MiB free disk is required. Downloads buffer the bounded body in Node and can temporarily hold both chunks and the concatenated buffer; this is not constant-memory streaming. It is bounded runner work, not a workspace download.

Authenticated custom fetch requests go only to fixed `api.github.com` artifact/asset endpoints. Octokit release uploads use its official authenticated GitHub upload endpoint, with fixed repository/release identity. Signed body redirects receive no headers/token, require HTTPS, a known GitHub/Azure suffix and no URL userinfo/non-default port, and cannot redirect a second time. Signed URLs are not included in errors/reports. Caught API error messages redact the supplied token. The exact Python ZIP parser rejects absolute/traversal/backslash members and duplicate/missing/wrong-sized targets, reads only the specified native member into a fixed output path, bounds actual extraction and verifies CRC through `zipfile`; no member code executes or member path is used as an output location.

Only five release assets are uploaded or verified: the two exact originals, unchanged manifest/checksums and explicit `preservation-coverage.json`. Existing exact assets are read back and retained; mismatches and duplicates fail without overwrite or deletion. The release must be the matching existing-tag draft prerelease, or a new draft prerelease for that existing tag. Published releases and unrelated drafts are refused. Draft state is rechecked before each upload and after all five readbacks. Upload/readback failures can leave an incomplete or unverified draft/asset; diagnostics are retained and retries verify existing bytes rather than replacing them. There is no update, delete, tag creation or public-publish operation.

The coverage is two of six archives for this operation. Linux, source, web and repacked Windows archives remain outside its verified remote coverage; the workflow neither rebuilds them nor claims a complete backup. Coverage does not audit any unrelated pre-existing assets. Draft storage is access-controlled and deletable by repository administrators; it is not immutable storage, an independent backup, commercial approval, a public game release, Steam publication, consumer installation evidence or human enjoyment evidence.

## Executed author checks and limits

`mock-workflow.mjs` executes the **exact final extracted inline JavaScript** in an isolated VM. `mock-summary.json` and `mock-results/` preserve all **70 passing cases**: creation, existing-draft reuse, five-asset idempotency, confirmed dispatch, repository/ref/trigger/confirmation, tag/file/run/artifact identities, both artifact expiry/size checks, required digest, body/header bounds, absent/short/corrupt bodies, API errors, redirect spoof/userinfo/port/chain rejection and token boundaries, extraction/hash failure, release duplication/publication/mismatch, upload errors/size, separate readback corruption for all five assets, final draft/tag checks, and token redaction. No mocked GitHub mutation invokes a real API. Large native/evidence payloads are virtual objects with declared size/hash; real crypto checks metadata/coverage bytes. Therefore mock success proves control flow, not actual server downloads or original full-wrapper bytes.

`validate.py` parses YAML with the available PyYAML BaseLoader and asserts exact triggers/privileges/timeout/action pins/no run steps/diagnostic settings/inline-script correspondence and unchanged v0.4/new-path absence. Node parses the inline JavaScript; Python compiles the exact embedded extraction. **12 real tiny-ZIP subprocess probes pass**, including nested selection, unrelated directory, wrong size, missing/duplicate target, empty wrapper, traversal/absolute/backslash, target directory, truncated ZIP and corrupted CRC. These execute unchanged Python extraction with synthetic name/size CLI arguments; production invocation remains hardcoded to the original native filename and byte count. Probe bytes/output/errors are retained in `zip-probes/` and `zip-probes.json`.

This author report is ready for independent privileged-workflow review. No actionlint invocation or live runner execution is claimed. GitHub dispatch visibility depends on workflow presence on the default branch; the reviewed path-restricted push bootstrap is the proposed activation. Actual success requires a later authorized job with `passed-draft-partial-preservation`, five exact asset readbacks and release/asset IDs plus retained live diagnostic. No production or previous release was changed by these checks.

Reproduce outside the repository:

```sh
python3 prepare.py
node mock-workflow.mjs
python3 validate.py
```

Do not rerun these commands in the frozen evidence directory: they intentionally regenerate author outputs. Copy the directory to a new exterior test location for independent reproduction. `FROZEN-FILES.json` hashes every retained evidence/input/helper file except itself.
