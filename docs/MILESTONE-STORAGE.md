# Preserving milestone binaries beyond Actions retention

All six v0.4.0 release archives currently exist locally in `releases/0.4.0/`, totaling about 1.2 GiB. The exact native-tested Windows ZIP has SHA256 `ec5203567cf15bcae28c6b1b4e908469fd075197bba6b67cfab2185f2b9d8927`; its original evidence ZIP has SHA256 `55f967466653acda8fe52545892590de663629f8ed28c8e697d7b0c9f07dcd3a`. Current CI artifacts expire after 30 days. A preserved local archive and an expiring remote artifact do not establish durable remote binary storage.

The reviewable `.github/workflows/preserve-milestones.yml` provides a concrete destination: assets on a **draft development GitHub Release for existing tag v0.4.0**. At initial document creation it had not run. The verified execution below supersedes that initial state. Draft releases have no Actions retention timer, but repository administrators can still delete them; this is longer-lived storage, not immutable storage or a substitute for independent backups. Drafts require authorized repository access and do not publicly publish the game.

## Pinned identity and privilege boundaries

The workflow grants its single bounded job only `contents: write` and `actions: read`, with a 15-minute timeout. There are no PR triggers, checkout, builds, dependency installation, Steam credentials, arbitrary URLs, custom version/artifact payloads or execution of downloaded code. It pins:

| Identity | Exact value |
| --- | --- |
| Existing annotated tag object | `33b8325452622f7be745fa88d69818896cc8b34a` |
| Existing tag target commit | `dae9758ea40f849b36d9891c859b7bf6df09d242` |
| Manifest SHA256 | `59b252300f50244d06ea0d40e6d4e2318a02806bcfa5d719a2ca7186217fbb67` |
| SHA256SUMS SHA256 | `0b227baad42e6529cff939598903533171a24b078e792536cfcebbaadb38c0b4` |
| Native successful run | `36772521612`, attempt 1 |
| Full native Actions artifact | `11123973383`, 180,306,034 bytes |
| Original small evidence artifact | `11123858254`, 1,993,027 bytes |
| Runtime source digest | `da553781de9d57a2ca3a0c6260082335e7db65ad423c8cfd647e84d4055f5425` |

It reads manifests at the pinned commit, verifies tag/object/hash/run/artifact identity and expiration, downloads both original artifacts, and extracts only the exact 178,481,506-byte inner native ZIP. Streamed downloads stop if they exceed their exact expected byte bound; each request has a three-minute timeout, and the runner must have at least 500 MiB free for the fixed files. The ZIP parser rejects absolute/parent-traversal member paths and only writes the selected bounded member. It checks the entire outer artifact hash, inner native hash and original evidence hash before creating the draft. Tokens go only to the GitHub API; signed download redirects receive no token. Every uploaded or existing matching asset is downloaded again and hash-checked. Existing assets are never overwritten, deleted or clobbered. A published release or an unrelated draft causes refusal, preserving that state.

The draft stores the two native archives under the exact official manifest filenames, unchanged `manifest.json` and `SHA256SUMS`, and an explicit `preservation-coverage.json`. That coverage file names the four absent Linux/source/web/repacked-Windows archives. Their bytes are local; the workflow does not recreate them, infer them from a source checkout or claim a full remote mirror. It creates a draft prerelease and never changes it to public. The release body preserves the known defects and independent rejection of polished/public/commercial/AAA promotion.

## Activation and access limits

Manual dispatch requires selecting version `0.4.0`, native run `36772521612` and confirming draft preservation on the production branch. GitHub dispatch normally requires the workflow file to exist on the repository's default branch. Available connector tools include artifact reads/downloads and limited workflow reruns, but no new dispatch or release-creation/upload method was found. Workspace `gh api` and direct documentation reads return HTTP 403 through the session proxy. No credential workaround was used. The reviewed bootstrap workflow subsequently performed the fixed draft operation with its own narrow job permissions, as recorded below.

To make activation concrete without broadening PR privileges, the proposed workflow also has a narrow bootstrap trigger: a push on `codex/lanternbound-production` that changes `.github/workflows/preserve-milestones.yml`. A commit may also contain other files, but its changed paths must include this selected workflow path. The production lead must review this privileged workflow before committing it. Committing that file to the named branch intentionally starts preservation with the fixed v0.4.0 gates. Ordinary runtime/docs pushes without a workflow edit do not match the trigger. This is a repository workflow capability, not a claim that the current connector dispatched it. Future milestones require new reviewed immutable identities rather than arbitrary untrusted inputs.

If workflow activation is unavailable, an authorized maintainer can use GitHub's release UI to create a draft prerelease for the existing tag and upload the two local exact archives, manifest/checksums and a clear partial-coverage statement. Verify uploaded bytes against the official hashes before recording preservation as passed. Upload the remaining four local archives later only after hash verification; keep the draft body/coverage truthful until those bytes exist remotely. Never replace the tested Windows ZIP with a newly built one under its filename.

## Evidence required after running

Inspect the workflow result and its `report.json`: require `passed-draft-partial-preservation`, all five asset read-back hashes, the existing tag target and a release that remains draft. Save its release/asset IDs and verification report into the next production record. A failed or partial upload can leave unverified or incomplete assets in the draft, including a successful upload whose read-back failed. Inspect the diagnostic and retained assets; a retry verifies existing bytes and refuses mismatches without overwriting or deleting them. Do not label partial or unverified preservation complete. Actions diagnostic retention is still 30 days, so preserve the diagnostic locally too. Commercial, Steam, broad platform and human-fun gates remain separate.

Reference schemas: [create a release](https://docs.github.com/en/rest/releases/releases#create-a-release), [release assets](https://docs.github.com/en/rest/releases/assets), [Actions artifact downloads](https://docs.github.com/en/rest/actions/artifacts#download-an-artifact), [workflow dispatch](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#workflow_dispatch). Live retrieval of these references returned proxy HTTP 403 in this workspace; validate the configured API calls on the actual runner before claiming remote preservation.

Privileged executable actions are pinned to independently fetched full commit SHAs: github-script v7 `f28e40c7f34bde8b3046d885e986cb6290c5673b` and upload-artifact v4 `ea165f8d65b6e75b540449e92b4886f43607fa02`. Connected GitHub Git-ref reads verified these identities; shell documentation/API reads remained HTTP 403. Their source provenance is recorded separately from the still-unexecuted preservation job.

## Actual verified v0.4 partial preservation

Bootstrap run36778210203 failed with HTTP415 before release creation; its exact diagnostic and log remain in reviews/milestone-storage-v0.4/run-36778210203-1. The reviewed compatibility repair distinguishes GitHub JSON negotiation for Actions archives from octet-stream release-asset downloads. It retains all fixed identities, bounds, token rules and hash/draft gates.

Retry run36779379544 (job110105312046, head3ece2f4e5b7591167190aac3aacaae01f33fdc7f) succeeded. The exact downloaded diagnostic has status `passed-draft-partial-preservation` and five hash-verified read-backs: native ZIP asset601826618, evidenceZIP601826777, manifest601826795, checksums601826799 and coverage601826812. ReleaseID400449104 remains a draft development prerelease; its owner-access URL is https://github.com/evangjones99-gif/Roguelike-deckbuilder/releases/tag/untagged-fc0f44877e9fdadfb1d9. The846-byte diagnostic artifact11126708197 has SHA256b877883e7e288d7d76553ef7a2e79968d08633a24823f1790541c89e5ca5c0be; exact report/log/transfer evidence is retained in reviews/milestone-storage-v0.4/run-36779379544-1.

This is actual partial preservation of two of six archives, not a full mirror, immutable backup, public game release or Steam publication. Four Linux/source/web/repacked-Windows archives remain local. The separate independent actual-storage review determines any further qualification; do not infer complete game-quality acceptance from storage success.

## Selected v0.6.1 fixed draft-storage workflow

The new preserve-v061.yml is the exact independently accepted R4 source, SHA256a9641339213d6a42808df1d1504ed49f1eda3d9e18f8e2bbfb8ec735d759aa9d. It pins the existing annotated v0.6.1 tag, metadata/source identities and original native run36791619534. The job verifies full original Actions wrappers, extracts only the exact named native ZIP, and verifies five named assets by readback. Its coverage remains two of six archives. R2/R3 refusals and the wrong-upload-name witness are retained with R4 negative fixtures under milestone-storage-v0.6.1-* canonical reviews.

Pushing this new fixed path deliberately starts its narrowly privileged job under existing owner preservation authorization. No live transfer, successful draft storage, durable full mirror or public publication is claimed by source approval. Inspect the actual run diagnostic, exact five IDs/hashes and final draft/prerelease state before recording success. Existing v0.4 workflow/tag/release bytes remain unchanged.
