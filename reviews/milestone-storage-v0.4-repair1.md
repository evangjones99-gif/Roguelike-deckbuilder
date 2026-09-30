# Milestone preservation compatibility repair 1

30 September 2026. The technical agent who originally reviewed preservation subsequently owns this narrowly authorized workflow repair. This report is repair-author verification; the lead's independent read-through and the next live job remain separate gates. The original `milestone-storage-v0.4.md` is preserved unchanged. No real release/upload API call was made by this agent.

## Actual failed execution

The first bootstrap PUSH run 36778210203, job 110101380808, head e5690118…, failed with `Download API status 415`. Inspected preserved actual job log and decoded `reviews/milestone-storage-v0.4/run-36778210203-1/report.json`: status failed, assets empty and no release ID. The failing archive download occurs before release lookup/creation in the inspected source, so this run supplies no release-preservation success. Diagnostic upload is distinct from a release mutation.

Decoded report is 413 bytes, SHA-256 `db5f21a5226e8d6cdbe67c93c1ccb9bf6f87bd267c43dfc8283fbb59d9cd47a2`; transfer metadata records a 414-byte diagnostic artifact with its own archive hash. These are different byte objects. Preserve both and the failed run rather than replacing its verdict with a successful source test.

## Verified contract and narrow repair

Used connected read-only GitHub access to inspect official documentation and generated Octokit endpoint docs:

- GitHub getting-started REST documentation, blob SHA `111973a7afcc90ea8fc0b033071b8dbda590cf0a`: ordinary API/Octokit requests use `Accept: application/vnd.github+json`.
- [Octokit Actions downloadArtifact](https://github.com/octokit/plugin-rest-endpoint-methods.js/blob/main/docs/actions/downloadArtifact.md), blob SHA `a873dff39e6de818f42bb223f0e7fbbb8dd7bb3f`: archive GET negotiates a redirect, with a Location URL valid for one minute and zip format.
- [Octokit getReleaseAsset](https://github.com/octokit/plugin-rest-endpoint-methods.js/blob/main/docs/repos/getReleaseAsset.md), blob SHA `c3b4ed71dab04f3cda42fab42b4abf7c6e5ec6c9`: binary release downloads explicitly need octet-stream negotiation and must handle either 200 or 302.

The original helper sent `application/octet-stream` to both endpoint families. The repair adds explicit `actions-artifact` and `release-asset` purposes at their two call sites: Actions archive requests now use GitHub JSON negotiation, release binary read-backs retain octet-stream. The archive after redirect is still treated as bytes and must match its exact pinned size/hash; JSON negotiation does not make metadata an acceptable substitute for the archive.

Purpose must match a numeric endpoint shape within the fixed repository; query strings, alternate paths and unknown purposes are rejected before fetching. The existing maximum byte bound is additionally checked before the first request. API diagnostics identify purpose, original validated path and status. Fetch/redirect errors are sanitized to that fixed endpoint context, so error text cannot echo a signed URL/query or token. First API fetch still uses manual redirects and Authorization only on api.github.com; signed fetch carries no credentials.

Final repaired workflow SHA-256: `90d317a7207b8a6e66e52b016d4e8024a4244730719b0157863ce0b71d31f81f`. Only the download helper and its two purpose arguments changed. Independently reconstructed the pre-repair workflow by reversing those exact edits and compared it byte-for-byte with Git HEAD: equal. Permissions, full action pins, tag/manifest/run/artifact identities, expiration checks, streamed bounds/timeouts, exact artifact/member hashes, selected fixed-path extraction, draft-only behavior, refusal/idempotence and all five read-back requirements are unchanged.

## Verification and source decision

Compiled the entire embedded JavaScript successfully, then exercised the actual repaired helpers with fake streams/fetches, without real network or mutation:

- Actions/archive header is JSON; release-asset header is octet-stream. Both supported 200 and credential-free 302 paths return expected bytes.
- Wrong endpoint purpose, a query-bearing path, zero ID, unknown purpose and excessive bound refuse before fetching.
- Simulated 415 now identifies only Actions purpose/status/fixed API path.
- A fake signed-fetch exception containing a sensitive URL/token marker is replaced with a sanitized fixed-path error.
- Declared/streamed oversize rejection, reader cancellation/release and HTTP/lookalike-host refusal still pass.

The unchanged release/upload section retains the original independently mocked draft/idempotence/refusal checks; no change bypasses a release or hash gate. This is meaningful source verification, not an actual successful GitHub download or durable-storage test. **Ready for the lead's independent source review and one live compatibility retry. Remote preservation remains failed/unproven until all five actual read-backs and final draft state pass.** No broader Accept fallback, disabled hash check, replacement upload, deletion or publication was introduced.

## Coverage terminology correction

The original frozen review called the fourth absent archive a crossbuilt Windows archive. In this preserved v0.4 milestone it is actually the archive repacked locally from verified native Windows bytes, distinct from the original exact CI-tested native ZIP. Correct remaining coverage is Linux/source/web/repacked-Windows archives, all four absent from this operation; only the exact native-tested ZIP, original evidence ZIP and three metadata files are targeted. This correction does not claim full remote mirroring, immutable storage, game polish, commercial/AAA readiness or Steam release.
