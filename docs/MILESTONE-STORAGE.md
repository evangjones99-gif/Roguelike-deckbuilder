# Preserving milestone binaries beyond Actions retention

All six v0.4.0 release archives currently exist locally in `releases/0.4.0/`, totaling about 1.2 GiB. The exact native-tested Windows ZIP has SHA256 `ec5203567cf15bcae28c6b1b4e908469fd075197bba6b67cfab2185f2b9d8927`; its original evidence ZIP has SHA256 `55f967466653acda8fe52545892590de663629f8ed28c8e697d7b0c9f07dcd3a`. Current CI artifacts expire after 30 days. A preserved local archive and an expiring remote artifact do not establish durable remote binary storage.

The reviewable `.github/workflows/preserve-milestones.yml` provides a concrete destination: assets on a **draft development GitHub Release for existing tag v0.4.0**. It has not run or created a release at document creation. Draft releases have no Actions retention timer, but repository administrators can still delete them; this is longer-lived storage, not immutable storage or a substitute for independent backups. Drafts require authorized repository access and do not publicly publish the game.

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

The draft stores the two native archives under the exact official manifest filenames, unchanged `manifest.json` and `SHA256SUMS`, and an explicit `preservation-coverage.json`. That coverage file names the four absent Linux/source/web/crossbuilt-Windows archives. Their bytes are local; the workflow does not recreate them, infer them from a source checkout or claim a full remote mirror. It creates a draft prerelease and never changes it to public. The release body preserves the known defects and independent rejection of polished/public/commercial/AAA promotion.

## Activation and access limits

Manual dispatch requires selecting version `0.4.0`, native run `36772521612` and confirming draft preservation on the production branch. GitHub dispatch normally requires the workflow file to exist on the repository's default branch. Available connector tools include artifact reads/downloads and limited workflow reruns, but no new dispatch or release-creation/upload method was found. Workspace `gh api` and direct documentation reads return HTTP 403 through the session proxy. No credential workaround or external release operation was attempted.

To make activation concrete without broadening PR privileges, the proposed workflow also has a narrow bootstrap trigger: a push on `codex/lanternbound-production` that changes `.github/workflows/preserve-milestones.yml`. A commit may also contain other files, but its changed paths must include this selected workflow path. The production lead must review this privileged workflow before committing it. Committing that file to the named branch intentionally starts preservation with the fixed v0.4.0 gates. Ordinary runtime/docs pushes without a workflow edit do not match the trigger. This is a repository workflow capability, not a claim that the current connector dispatched it. Future milestones require new reviewed immutable identities rather than arbitrary untrusted inputs.

If workflow activation is unavailable, an authorized maintainer can use GitHub's release UI to create a draft prerelease for the existing tag and upload the two local exact archives, manifest/checksums and a clear partial-coverage statement. Verify uploaded bytes against the official hashes before recording preservation as passed. Upload the remaining four local archives later only after hash verification; keep the draft body/coverage truthful until those bytes exist remotely. Never replace the tested Windows ZIP with a newly built one under its filename.

## Evidence required after running

Inspect the workflow result and its `report.json`: require `passed-draft-partial-preservation`, all five asset read-back hashes, the existing tag target and a release that remains draft. Save its release/asset IDs and verification report into the next production record. A failed or partial upload can leave unverified or incomplete assets in the draft, including a successful upload whose read-back failed. Inspect the diagnostic and retained assets; a retry verifies existing bytes and refuses mismatches without overwriting or deleting them. Do not label partial or unverified preservation complete. Actions diagnostic retention is still 30 days, so preserve the diagnostic locally too. Commercial, Steam, broad platform and human-fun gates remain separate.

Reference schemas: [create a release](https://docs.github.com/en/rest/releases/releases#create-a-release), [release assets](https://docs.github.com/en/rest/releases/assets), [Actions artifact downloads](https://docs.github.com/en/rest/actions/artifacts#download-an-artifact), [workflow dispatch](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#workflow_dispatch). Live retrieval of these references returned proxy HTTP 403 in this workspace; validate the configured API calls on the actual runner before claiming remote preservation.

Privileged executable actions are pinned to independently fetched full commit SHAs: github-script v7 `f28e40c7f34bde8b3046d885e986cb6290c5673b` and upload-artifact v4 `ea165f8d65b6e75b540449e92b4886f43607fa02`. Connected GitHub Git-ref reads verified these identities; shell documentation/API reads remained HTTP 403. Their source provenance is recorded separately from the still-unexecuted preservation job.
