# Independent milestone-storage review — v0.4.0

Reviewer: independent technical/release agent, 30 September 2026. Scope: the new preservation workflow and storage document before the production lead's bootstrap commit. Only this report was edited by the reviewer; no real release, asset upload, workflow dispatch or network mutation was performed.

**Approve the repaired workflow for the owner-authorized, fixed v0.4.0 draft-preservation operation. This is a source review, not evidence that remote storage has succeeded.** The operation preserves two of six archives plus metadata, remains draft/development-only, and does not grant game-quality, public-release, commercial/AAA or Steam approval.

## Inspected identities and repairs

Final inspected `.github/workflows/preserve-milestones.yml` SHA-256: `66e27da4ab741c207314e289bcf1f6577880f0050aee373a50f5ed24ac3f0252`. Final inspected `docs/MILESTONE-STORAGE.md` SHA-256: `a0a7ee2167f4e68be034ed83b72113d4a489dfc0aaca7ba2456c66d05eeb5370`.

Independently read the actual annotated tag object `33b8325452622f7be745fa88d69818896cc8b34a` and its peeled target `dae9758ea40f849b36d9891c859b7bf6df09d242`. Recomputed manifest/SHA256SUMS bytes both locally and directly from the pinned Git commit: hashes match workflow constants `59b252300f50244d06ea0d40e6d4e2318a02806bcfa5d719a2ca7186217fbb67` and `0b227baad42e6529cff939598903533171a24b078e792536cfcebbaadb38c0b4`.

Native archive identity agrees with the earlier independent package audit: inner ZIP SHA-256 `ec5203567cf15bcae28c6b1b4e908469fd075197bba6b67cfab2185f2b9d8927`, 178481506 bytes, runtime `da553781...`, run 36772521612 attempt 1. Personally hashed the 1993027-byte original evidence ZIP: `55f967466653acda8fe52545892590de663629f8ed28c8e697d7b0c9f07dcd3a`. Inspected actual native CI job log: full wrapper artifact ID 11123973383, size 180306034, digest `d3fac04b38713ad006ae33d4fc710fc0b51df28b850b74ef8511a6e8bc818cea`; small evidence artifact ID 11123858254 and hash/size match. The large wrapper's original bytes are not locally available to this reviewer; the new job must download/hash them before any release creation, as implemented.

Two pre-commit findings were reported and repaired by the lead:

- Executable Actions dependencies originally used mutable version tags in a write-privileged job. They now pin github-script to `f28e40c7f34bde8b3046d885e986cb6290c5673b` and diagnostic upload-artifact to `ea165f8d65b6e75b540449e92b4886f43607fa02`. Inspected `milestone-storage-pins-v0.4.json`: recorded connected GitHub tag-ref responses identify both as commit objects. Remote ref retrieval belongs to the lead; this reviewer inspected its evidence and exact workflow pins.
- The document originally claimed a failed/partial upload leaves only verified bytes. An upload whose subsequent read-back fails can leave an unverified asset. Repaired text explicitly describes unverified/incomplete leftovers, inspection, and refusal to overwrite/delete on retry. Failure must not be labeled complete preservation.

## Privileges, source and download boundaries

The workflow has no PR trigger, checkout, installation, game build, execution of downloaded code, signing/Steam credential or publication step. The single 15-minute Ubuntu job grants only contents:write and actions:read; default permissions are empty. Its repository/ref conditions constrain activation to the named production branch. Manual dispatch requires exact fixed choices and the confirmation input. The exact-path production-branch push is deliberately a bootstrap activation: committing this workflow there starts the fixed operation, even without dispatch. Approval of that activation is explicit here; the path filter is not a separate cryptographic guarantee of human review.

All actionable identities are fixed in reviewed source. The job rechecks the existing annotated tag/target, pinned metadata hashes, known development manifest, run success/path/repository/attempt, artifact names/sizes/expiry and optional API digests. It fully hashes both downloaded artifacts and the selected exact native ZIP before creating a release. Extraction reads one matching member and writes a fixed destination; it never executes artifacts or uses member paths as output paths. Fixed hashes and selected-member size are important controls in addition to traversal checks.

Token-bearing fetches target the literal api.github.com host and use manual first-hop redirect handling. The first signed destination must be HTTPS on an allowed GitHub/Azure suffix, and its fetch carries no Authorization header. Additional redirects use fetch's ordinary credential-free behavior; this is not a claim of independently validating every later redirect hop. Downloads enforce declared and streamed maximum bytes, three-minute request timeouts and a 200 MiB hard bound. Selected extraction has a two-minute timeout; initial disk floor is 500 MiB for the fixed roughly 361 MB output set. The hosted job's 15-minute cap limits total execution, but cannot guarantee the finally diagnostic completes if the runner is forcibly terminated.

## Independent non-mutating source probes

Compiled the full embedded JavaScript successfully. Executed its actual release/upload section against mocked filesystem/downloads and GitHub APIs, with no real network:

- First preservation requests draft=true/prerelease=true/make_latest=false, creates one draft and five assets, then verifies five read-backs.
- Exact matching rerun performs zero mutations and verifies all five existing assets.
- A published release, unrelated draft, changed draft state before upload and same-size mismatched existing asset each refuse without mutation.
- Failed first uploaded-asset hash read-back refuses with zero verified assets while that one mock upload remains, independently demonstrating the documentation correction.

Separately executed the actual download helpers against fake streams: token appears only on the fixed API fetch; signed fetch has no Authorization header; HTTP/lookalike destinations are rejected; excessive Content-Length and byte bounds are rejected; oversized streamed bodies are canceled and locks released. These probes test branch behavior and token/boundary construction, not GitHub API compatibility, live permissions, service reliability or successful durable storage.

## Idempotence and remaining acceptance gate

The serial concurrency group avoids simultaneous copies of this job. Existing release identity must match the pinned draft/prerelease/body marker. Existing same-name assets are never overwritten or deleted: sizes and downloaded bytes must match exactly. New uploads recheck draft state immediately before mutation, and final release state must remain draft. There is no release-update/publish or tag-mutation API call. External authorized administrators can still change/delete/publish a release; these checks do not make GitHub storage immutable or transactional against concurrent outside writers.

Two official native archives plus unchanged manifest/checksums and explicit coverage are uploaded. Four Linux/source/web/crossbuilt-Windows archives remain outside this remote operation; neither successful partial preservation nor this review establishes a full mirror of v0.4 or older versions. Draft releases avoid the Actions retention timer but still need independent backups. Existing mismatched/failed assets intentionally require diagnosis instead of automatic destructive repair.

After execution, require actual `passed-draft-partial-preservation`, five exact asset read-back hashes/IDs, expected tag/target and a still-draft release. Preserve diagnostic and release URL locally before artifact expiration; inspect partial/unverified assets on failures. Until that evidence exists, report the workflow as approved/configured, not as completed permanent preservation. The owner-authorized game production and known-defect repairs continue separately.
