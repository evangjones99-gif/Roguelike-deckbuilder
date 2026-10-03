# Independent full-sized optional source-bundle restore supplement

**Accept the independently completed full-size restoration proof for the exact retained b065 research bundle through the frozen R2 verifier.** This supplements the earlier independent 17-case scoped utility acceptance and its preserved ENOSPC failure. It is not a new production producer execution, a source-bundle archive of the current official fdb hunter milestone, or game/native/Steam approval. No repository source, release, ref, original input or prior report was changed by this reviewer.

## Exact input and independent execution

Original input remains at `/tmp/hollowpact-v07-bundle-preflight-y4st1n0p/source.bundle`: **1,526,523,777 bytes**, SHA256 **04c31e64dab1b8503746b452717f6cea7a806135ec07c0fa4bcd03d65ab7561c**, source commit **b065d1044c9486b616f2eb2e95021de18c349ab7**, current tree **aaed2c69d8543f020a863afc3b969cee3148d339**. This original input is temporary storage, not a new durable backup. It was streamed-hashed both before and after this execution.

The executed frozen R2 helper `/workspace/scratch/release-bundle-v07/candidate-r2/source-bundle.mjs` has SHA256 **7d9af128cbe7d9bf2f30e9e3b8a1ab2aeb1f911346b48382df075a5136e38315**; its full-tree verifier has SHA256 **d5030d125819c2d87a681013361b2ed69caa9d2d7b46d60d327c11857202cc96**. Exact header-format/transaction/adversarial fixture acceptance belongs to the prior independent utility review; this supplement does not repeat or relabel its tests.

Fresh independent execution completed in **40.799 seconds** under `/tmp/hollowpact-fullsize-independent-r2-m0v8dy9w/restored.git`:

- Exact version-2 header and the two advertised `HEAD`/production-branch refs at b065 passed. Fresh bare `git bundle verify` accepted complete history without prerequisites; unbundle and explicit HEAD/branch restoration passed.
- `git fsck --full --strict` passed with empty diagnostic output. All **3,586** restored objects exactly match source reachability; independently enumerated all-object inventory contains **zero extra objects**. Sorted closure SHA256 is **aafbaef598420ad1e21075980ec63f73fce95d3a577a242258ab9d5e535fd3f4**.
- All **5,904** current-tree blob rows match the source and accepted author receipt: paths, modes, SHA1 object identities, byte sizes, and SHA256 of complete streamed raw Git bytes. Commit and full tree identities match. This is canonical Git content, not a claim about normalized working-file/CI text.
- A separate supplemental index comparison matches **all 3,132 canonical review-index rows** by path/OID/byte size/SHA256 to the independently restored tree; its complete current `reviews/` path set matches exactly.
- The restored bare's **22 regular files**, **1,526,665,801 total bytes**, have a complete path/mode/size/SHA256 inventory in the frozen compressed proof. Only this new derived bare was removed after the full successful inventory/proof and original-input rehash. `derived-bare-cleanup.json` records actual removal; the original input and prior failed restore metadata remain.

`full-restore-proof.json.gz` preserves the full object/blob/derived-file inventory losslessly: **490,144 bytes**, compressed SHA256 **c963bb9709e584b18c4b6be67e4eda42e4eddf9d47a71aabde8096c3854cea71**; decompressed **1,597,701 bytes**, SHA256 **ff65e50b40c55f52e095b2ff29dc83b6c8aa98d9227ff85373b48fd7c50cb337**. No large additional raw proof copy was created. Receipts and original replayable harnesses remain beside this report.

## Capacity reservation and observed usage

Root explicitly coordinated no concurrent heavy `/tmp` work for this bounded restore. Initial available temporary space was **4,288,847,872 bytes**. The refusal threshold reserved **two full bundle-sized new allocations plus 512 MiB**, a conservative **3,589,918,466-byte** budget, leaving another **698,929,406 bytes** beyond that budget. The original bundle was already present and therefore excluded from the additional-allocation budget. The durable workspace initially had **93,634,560 bytes** free; the new exterior proof is below 1 MB.

409 free-space samples at a nominal 0.1-second interval observed minimum `/tmp` free **2,762,117,120 bytes** and maximum net new allocation **1,526,730,752 bytes**. The 256 MiB emergency-abort margin was never reached. Following own-derived-bare cleanup, `/tmp` free returned to **4,288,847,872 bytes**. These are sampled observations of this execution, not proof of an absolute peak, a minimum required capacity, or an enforceable filesystem reservation against other users. Bundle creation, temporary ZIP audits, future source changes and concurrent operations can require additional space. Current official release capacity remains separately verified by root.

## Preserved failure and scope limits

The original independent ENOSPC attempt and its recoverability/cleanup evidence were left unchanged; successful retry does not erase that storage failure. The author preflight and prior independent report/index hashes are recorded before/after in `full-restore-receipt.json` and match exactly.

The first optional supplemental index harness incorrectly assumed all five previously audited raw/gzip counterpart paths existed as committed current-tree blobs. It failed on `reviews/gameplay-v0.2-experiments.json` after matching the 3,132 canonical file rows. Its original script and explicit failure remain. A new `check-index-r2.py` succeeds: three raw counterpart paths are absent from the current tree, two are present and match their recorded raw identities, and all five compressed paths are committed and match the canonical rows. No new gzip expansion, raw working-input restoration, or source ZIP audit was performed or claimed.

Acceptance is limited to this exact older full-size input, frozen R2 restore algorithm, fresh Linux-host Git restore/fsck, full byte/object comparison, and indexed committed content. It does not establish Windows consumer behavior, minimum storage requirements, permanent/offsite backup, full producer/archive transaction readiness, or preservation of unrelated refs/untracked files. Production promotion remains root's separately gated decision. Current official v0.7 ZIP archives were not created using this research bundle.
