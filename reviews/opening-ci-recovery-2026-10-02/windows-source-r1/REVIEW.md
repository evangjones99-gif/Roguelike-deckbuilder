# Independent Windows checkout source review

Decision: ACCEPT the proposed narrow source repair for root's publication decision. Actual Windows checkout/build/smoke outcome remains unmeasured. This agent changed only its new packet, made no remote writes, triggered no CI and ran no local Windows command.

Reviewed repository evangjones99-gif/Roguelike-deckbuilder, branch codex/lanternbound-production, PR 1, supplied head a3ed18a56090d591ffd302dedd0f333cd3888cbc. The exact workflow was fetched at that head; blob 25bb08e1beb4e3cc1a346dfe65db4dfded8e345c. Before workflow SHA256 65e1c4531fa23ac32864846b509c47a0f7b93af60634bb80efeadd162380d4eb, 11,400 bytes. Proposed workflow SHA256 9ce0c28ed559413cca543589fb741b6e6b190fc0d6865f4f94834017320bb2e8, 11,841 bytes. Full before/after and exact unified diff are retained alongside this review.

## Failure evidence

Both actual jobs fail actions/checkout@v4 before actions/setup-node, npm ci, tests, build, packaging and executable smoke; the dedicated steps API independently reports all those later steps skipped. Successful always-upload steps do not mean a native package was built.

- Run 37048062806, job 110974304708: decoded-log payload 27,145 UTF-8 bytes, SHA256 04659e3d226296dc9a3f7fcaa301c50a1231a0b37de642992808cb54adbea4fa. Runner setup begins 2026-10-02T18:31:59.0514893Z; ten filename-too-long messages begin 18:32:46.0739330Z. Checkout used pull merge 8d03be7d78a3d0b733a504baa0841990d44b0715 and Git 2.55.0.windows.5.
- Earlier run 37045171775, job 110964691852: decoded-log payload 27,212 UTF-8 bytes, SHA256 3ad81eaf455b26244fffa5e30422cbaad3eb256f629d9d99ab755c4d90fad947; same ten retained evidence paths fail.

Exact returned decoded-log string bodies were re-encoded as UTF-8 without newline/BOM normalization: original U+FEFF and CRLF are retained. These are the raw exact bytes of the decoded tool payload; original HTTP response binary bytes are unavailable through this connector and are not independently certified. acquisition.json records initial retrieval UTC and identities. Preserve both .log files even where repository ignore rules require explicit inclusion; do not mistake an ignored file for absent evidence.

Failing review JPEG paths are under reviews/owner-playtest-ux-overhaul-2026-10-01/preserved-earned-2f1-independent-r1/body/tmp/standard-sol-owner-ux-gameplay-independent-r1/. With actual D:\a\Roguelike-deckbuilder\Roguelike-deckbuilder\ prefix, the ten filenames have absolute lengths 260–274 characters; maximum path component is only 53 characters. This fits the traditional full-path limit, not an oversized component. Original paths and bodies remain unchanged. Neither rename, deletion, sparse exclusion nor retirement is justified by this error.

## Primary source justification

Exact runner-version Git for Windows documentation, retained as git-for-windows-v2.55.0.windows.5-core.adoc, states core.longpaths enables long path (>260) support for builtin commands in Git for Windows and is disabled by default. It also states this does not provide equivalent support in Windows Explorer, cmd.exe or the Git tool chain. The failing operation is native git.exe checkout, a builtin command. The fix therefore directly addresses the observed operation, without claiming all subsequent tools support every retained path.

Source: https://github.com/git-for-windows/git/blob/v2.55.0.windows.5/Documentation/config/core.adoc

The actual checkout action SHA in the failed logs is 11d5960a326750d5838078e36cf38b85af677262. Its retained src/git-auth-helper.ts configureTempGlobalConfig implementation (lines 85 onward) copies the original HOME/os.homedir .gitconfig into the new temporary HOME before setting its child Git environment. Consequently the pre-checkout global configuration is copied into the action's temporary global configuration. A system-wide setting or admin elevation is unnecessary. This source mechanism supports the proposal; the new actual run still must verify it through successful checkout.

Source: https://github.com/actions/checkout/blob/11d5960a326750d5838078e36cf38b85af677262/src/git-auth-helper.ts

## Proposed change and static checks

Add one seven-line step immediately before checkout. It uses existing pwsh defaults, enables core.longpaths in the fresh hosted runner's ordinary global config, immediately checks the native command exit code, reads it back as a boolean, checks both readback exit status and true value, and prints only this non-secret setting. Explicit LASTEXITCODE checks avoid relying on PowerShell's native-command error preference. No credentials, registry/system policy or token permissions change. Existing contents: read, persist-credentials: false, runner, actions, runtime inputs, tests, native packaging and upload steps remain byte-identical.

Static verification reconstructed the after file from one exact insertion and proved deleting the insertion returns the complete before bytes. No local Git global configuration was changed by this agent. No YAML/PowerShell execution result is claimed; a Windows runner is the meaningful validation environment. The proposal is reversible by removing the single step. Subsequent failures should be retained as independent observations and repaired on their own evidence, not presented as regression-free proof from this source review.

## Packet and scope

The fixed before/after/diff plus exact primary sources total 78,369 bytes, below the assigned 96 KiB SOURCE cap. The separate raw decoded logs are evidence. The complete packet is far below the assigned 24 MiB ownership bound; no dependencies, framework, build output, historical evidence mutation or cleanup was introduced.

The generic GitHub Fetch action-job metadata URL was rejected as an unsupported endpoint. Both rejection responses are retained in job-metadata-fetch-rejections.json; the dedicated job-steps tool succeeded and its full responses are retained. No platform-wide readiness, successful native build, smoke interaction, complete 300-second session or human fun acceptance follows. This focused checkout repair only enables a fresh measurement toward the first-five-minute production goal.
