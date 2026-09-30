# Independent technical/release recheck — source v0.1.0

Date: 30 September 2026. Reviewer: independent release_audit agent. Original review remains preserved in technical-v0.1.md.

Decision: **The five original technical findings are repaired. Eligible for a clearly labelled development archive after final source freeze, rebuild and artifact correspondence checks. Commercial Steam readiness remains rejected.** This review does not certify fun, graphics quality, Windows launch, Linux launch or Steam installation.

## Inspected identity

| File | SHA-256 |
| --- | --- |
| src/engine.ts | ed14d3e3394d760284694a56d50f4303ad320ecd65cfe25b14e23d1279c74fe5 |
| src/content.ts | c64b68b7813ca4e923faf7b23ca36f871522772efc713fa1134bcbcfe06a9a71 |
| scripts/release.mjs | aaeb31791aea7295d52d87d2c1f56260d5fc4484f24562a292d26bb37bdc23e4 |
| scripts/build.mjs | fdec7ccc54f95c52ad30b99979877a6cf67c1d514b61bbf4ede87193f7e94d27 |
| desktop/main.cjs | 4863c478b2278f9cdbaf997af57c69ac8176a632933375f77e1bf159944a725d |

Independently recomputed the current runtime source digest and compared it with web build provenance and Linux packaged app.asar provenance. All three matched at inspection: `d9549190576b2d75969d265759fe09b3100e6361bba07b0f4028a1a21b5b867e`. UI/font repairs were still ongoing; this digest is an observation at inspection, not permission to ship a subsequently changed or stale binary. Final artifacts must be rebuilt and match the final frozen digest.

## Repairs verified

- **Save phase/route:** 23/23 engine tests pass. Independently reran the original corrupt-JSON reproductions: menu save rejected; ordinary battle at floor 10 rejected. validateState now restricts encounter route to ROUTES[floor-1], while supported legal states retain existing conservation checks.
- **Same-version stale desktop:** release compares packaged build-provenance sourceDigest with freshly built web provenance. In an isolated fixture with app.asar version 0.1.0 but deliberately mismatched provenance, release exited nonzero with `Stale linux-x64 desktop source`, produced no desktop archive, preserved INCOMPLETE.txt, and released its lock.
- **Distributable notices:** web dist contains the exact bytes of installed Three.js MIT LICENSE at licenses/THREE-LICENSE.txt. Extracted the Linux app.asar notice and verified identical bytes. CREDITS.md is included in web and Linux asar. Linux unpacked LICENSE.electron.txt and LICENSES.chromium.html match installed Electron notices byte for byte; the Electron notice is renamed by packaging rather than absent. Full commercial dependency/rights review remains a later gate.
- **Release concurrency/preservation:** release reserves .release-lock before tests/build and exclusively creates the final version directory. In an isolated fixture, two concurrent invocations yielded one successful archive and one lock rejection; the rejected process did not run npm or remove the owner's lock. The owner lock disappeared on normal completion. Sequential invocation at the same version was rejected and the archived web zip hash remained unchanged.
- **Playable build entry:** index.html, main.ts and build output now exist. The previous unresolved index.html entry is resolved at source/output inspection. Actual current build invocation and GUI smoke are being performed by the integration owner; this reviewer did not independently launch a desktop executable.

Safe release probes were confined to `/workspace/scratch/release-audit-fixtures-2kr2lfr6`. Fixtures use a harmless fake npm command to exercise transaction ordering without invoking real game builds or modifying real release directories; real zip/git archive operations ran on fixture contents. The stale-artifact fixture used a real ASAR package and actual release script rejection path. This evidence validates those mechanisms, not game compilation.

## Additional observations

Renderer source escapes loaded unit names, intent labels, logs and route/identity attributes before interpolating HTML. Save loading runs validateState and has a visible fresh-start path on rejection. Desktop source still disables Node integration, enables context isolation/sandboxing, denies external windows/navigation and filters remote requests. No privileged preload was found. No new security blocker was established by static inspection; this is not a runtime penetration test.

A minor UI reporting issue was sent to the integration owner: renderOutcome labels stats.battles as 'Contracts won', but beginBattle increments the counter on battle entry. A defeat can therefore count the lost contract as won. Relabel as contracts faced or add a real wins counter. This is not a progression or archive blocker.

The provenance comparison establishes correspondence of declared runtime source files; it is not tamper-proof attestation. Source and packaging must remain frozen during final build/archive. The release lock coordinates release-script instances, not arbitrary developers or standalone packaging commands.

## Development archive and remaining limits

A development archive may be preserved with honest labels once final freeze/build tests, matching Linux/Windows provenance, independent gameplay/visual decisions and actual archive verification are recorded. Keep the rejected original review and this recheck together. Never rename this decision into a commercial-quality endorsement.

Windows package/launch was not reviewed here. Linux launch, save/resume through the packaged executable, Chromium GUI dependencies and installation on a clean supported system remain distinct checks. Steamworks account/AppID, depot/install testing, store review, controller/Steam Deck support, final rights/disclosures, human enjoyment and purchase appeal remain unverified. No Steam publication is claimed.
