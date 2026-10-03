# Independent technical review — Hollowpact source v0.2.0

Date: 30 September 2026. Reviewer: independent release_audit agent. Earlier technical reviews and the v0.1 release remain preserved.

**Decision: approve the inspected source for a labelled development candidate, with final artifact verification pending. Reject commercial Steam/AAA promotion.** No unresolved source blocker was established in this audit after the repairs below. This is a technical decision, not agreement that human players find the game fun or that the animation/audio meet a major commercial studio's craft standard.

## Inspected source identity

| File | SHA-256 |
| --- | --- |
| src/engine.ts | 21bafb33832ec2d3ee1ca4ead9486825510bd380b62e143a8736465f1ad4110b |
| src/content.ts | 2f45160b3e577a7cd44381cb361c4407661a68819ff827a24b8ab34ce15c4234 |
| src/main.ts | 8a7700763ad6872d6fedade008330e28bae22da29611bf6226422746e285a324 |
| src/arena.ts | 61e8e03ddbd02ed139ac05d95aa191bc66f8a4d09fc445d041397b36fcf77f91 |
| src/art.ts | 3127ed46b8ec4aecbcc8218c8a78ded3e3f57c922d04b330c7f8fe0c51be1e85 |
| scripts/build.mjs | 33474430ff025548222d9d79133279773c0d3d7ffeb37f30ff2ac2af9a58db46 |
| scripts/release.mjs | bf033b93004e525482440a903a86112431bc0a6ae9255c0fa71f38efbd7a573b |
| scripts/desktop-smoke.mjs | a343a45da3c8f6562d6a08e965a24a4c939834d30b418e700a1a17b6a3183f16 |
| desktop/main.cjs | 1e54b1170ff4169285ff1757c0e768db2f144f7be919b4911a47394426cb75ae |
| public/art/PROVENANCE.json | 70de10054240d345ddaa1ad40bde39b25e0fd4008bd86a0a45cefde1798c0928 |

Read current rules/content, renderer/save/inspection paths, Canvas2D arena/art registry, desktop shell, build/release/smoke scripts, package configuration, regression source, attribution and production/AAA documents. No implementation edits. Integration owner is responsible for final suite/build/browser/native execution; this reviewer does not claim to have independently run those v0.2 suites or launched a v0.2 executable.

## Independent evidence and repairs

**Accepted-save HTML injection repaired.** Independently constructed a JSON-roundtripped valid battle save whose enemy name was `<img src=x onerror="document.body.dataset.audit=1">` (51 characters). validateState correctly accepts structurally valid arbitrary names, so renderer escaping is essential. The initial openUnit → openDialog path interpolated that loaded name unescaped into a dialog heading. Reported it to the owner. Inspected repaired openDialog now uses escape(name); roster, dossier body and log paths also escape loaded strings. A focused browser regression now checks literal heading text, absence of injected img elements and absence of the marker. Its execution belongs to final integration evidence; static repair is verified here.

**Packaged smoke identity repaired.** Initial smoke script still referenced the old Lanternbound executable, Mossling and schema-1 storage key. Inspected current script references Hollowpact/Cairn Hound/schema-2 key. It extracts provenance from the executable's actual app.asar, checks version and sourceDigest against the production build before launch, and records that packaged digest. It no longer labels an arbitrary current dist digest as evidence of the launched binary.

**Build input coverage repaired.** Build provenance recursively includes public artwork and records source-file hashes. This audit found THIRD-PARTY.md was copied into CREDITS.md without being a hashed build input, allowing stale desktop credits to pass source comparison. Inspected repaired runtimeSources now includes THIRD-PARTY.md. This closes the reported omission; final archive matching must still run on frozen inputs.

**Art/provenance verified.** Independently checked all four registered PNG files: courtyard, companion atlas, adversary atlas and pact seal. Each file matched its recorded SHA-256, dimensions and color mode, with no unregistered public PNG. Built art copies at inspection matched the public source bytes. Registry and URLs are local and use Vite BASE_URL for offline packaging. Documentation honestly describes illustrated 2.5D cutouts, not rigged 3D characters. Recorded prompts are briefs plus references to exact requests in the chat; retain the underlying generation records for a portable commercial provenance audit.

**Older release retained and intact.** Ran sha256sum -c against releases/0.1.0/SHA256SUMS. All four historical source/web/Linux/Windows archives passed. This establishes integrity against the preserved manifest at audit time; no older release was edited or removed.

## Rules/save review

Schema 2 intentionally rejects schema 1 and unsupported menu saves. Separate hollowpact.run.v2 storage prevents overwriting the previous key; application rebranding also changes the normal Electron profile location. Historical builds remain the supported route for historical runs. This is development-version separation, not a commercial save migration implementation.

The reducer remains seeded, renderer-independent and cloned on accepted actions. Card-copy conservation includes live bindings, with death returning one source copy. Indexed camp training supports exact duplicate copies. Phase/floor/route validation retains the earlier final-node repair. Passive descriptions and reinforcement identities/counts are checked. Reinforcements resolve from a fixed enemy roster after existing enemies, allowing a visible response window. Silence cancels damage/reinforcements without turning canceled attacks into arbitrary guard actions; guard armor uses identity/turn rules. Six-enemy/six-binding limits bound encounters. Existing regression source exercises these mechanics. Structural validation is not anti-cheat or a proof that every accepted numerical boundary represents a reachable campaign.

## Packaging/security and final archive gate

Exclusive release lock and exclusive destination creation remain in place; existing version directories are refused. Prior independent fixture evidence for concurrent rejection, stale same-version rejection and preserved incomplete output remains in technical-v0.1-recheck.md. Current release compares packaged version and source digest, hashes archived artifacts, requires clean committed source, retains reviews and marks development-prerelease/steamPublished=false.

Desktop source retains nodeIntegration=false, contextIsolation=true and sandbox=true, no privileged preload, denied new windows/navigation and blocked remote requests. Current arena uses Canvas2D, and unused Three.js was removed; attribution preserves the historical Three.js use rather than falsely claiming it remains bundled. Electron/Chromium notices must be checked in final packages.

During QA, current web/source digests differed and desktop directories still held version 0.1.0. The owner explicitly had final rebuilds pending. Those interim artifacts are not approved v0.2 distributions. Before archiving: finish final regression/browser checks, rebuild both targets, independently confirm both ASAR versions/digests against frozen source and production web output, record Linux smoke identity/limitations, preserve notices, then verify archive hashes. Append that evidence rather than overwriting this snapshot.

## Commercial/AAA decision

Commercial promotion remains rejected: no verified Windows launch or clean-machine installs/updates, normal sandboxed Linux launch, controller/Steam Deck coverage, target-hardware frame-time/memory soak, real Steam depot/install/store review, final rights/name clearance/AI disclosure, or prospective-player enjoyment evidence was inspected. Source quality, illustrations and successful automated play do not close those gates. v0.2 may be archived as a development milestone; it must not be advertised as AAA or Steam-released on this review's authority.

## Final artifact recheck — 30 September 2026

**Technical source/artifact correspondence gate passed for the v0.2 development archive.** All inspected source hashes above remained unchanged. Independently recomputed the complete frozen build-input digest, rather than trusting the reported value:

`9b1ef1c2e7979ec20cf98941df43283b0c243c5a34bb4913e10faec4e2bea5bf`

The production web provenance and both actual Linux/Windows app.asar provenance records equal that digest; web and both packaged versions are 0.2.0. Independently extracted packaged art and provenance: all four PNGs match registered source hashes in both platforms, and the provenance JSON matches public source bytes. Production web art also matches. CREDITS.md matches current THIRD-PARTY.md in web and both packages. Both Electron LICENSE.electron.txt files match the installed runtime notice, and Chromium notices are present on both platforms.

Read reviews/linux-desktop-0.2.0-smoke.json: its packaged source digest equals the independently recomputed digest and its errors array is empty. The integration owner reports four passing production-browser tests, including a complete run with exact save/reload state and the accepted-name injection regression. This reviewer verified their source/artifact linkage and inspected the regression source; the integration owner executed the browser and desktop tests.

The Linux smoke uses Xvfb and --no-sandbox, so it proves the recorded interaction on that constrained host, not normal sandboxed clean-machine installation or hardware performance. Windows packaging is verified here; Windows launch remains untested. No Steam installation/publication or human enjoyment evidence is added by this recheck.

Final archive creation must retain the frozen source/reviews and verify archive checksums. Commercial Steam/AAA promotion remains rejected for the previously listed gaps. No new runtime test was necessary for this correspondence recheck.

## Repaired motion candidate and evidence preservation recheck — 30 September 2026

The earlier correspondence decision above identifies the previous candidate. Preserve it as history: a subsequent independent visual review found a measured approximately 21.6 FPS draw cadence caused by frame-cap quantization. The arena was repaired to draw on requestAnimationFrame directly with bounded elapsed time. This reviewer inspected the changed scheduling source and independently rechecked packaging; visual/performance measurements belong to the visual reviewer. No claim of AAA animation quality follows from this repair.

The newly inspected files are:

| File | SHA-256 |
| --- | --- |
| src/main.ts | 9fe8938578533af5896ccfcabef86dff5986a44e8ea6f949417a596d4aa39a7d |
| src/arena.ts | bff20f7b8e91ae17316142ac9185bfebe9c9de2b994a102570726e5a4734046b |
| scripts/release.mjs | 5e5869b05c111637f40e47dc2bfb0721bff3ef4d1b6c6fc2a06b14767953fc58 |
| public/art/PROVENANCE.json | 2294fc01876886fbacbd8b4e81ac88764dc4919f0220da2fd2a5bc95ec201143 |

Engine/content and build-script hashes remain as originally reviewed. Independently recomputed frozen input digest:

`006db8571a5c1697b21bcbe51434161e53bb75580c5b72bed852efdd4da7bee9`

Web and both actual Linux/Windows ASARs are version 0.2.0 and match that digest. Both ASAR files have SHA-256 `5c1446a7985b582de1b88aa6245c243791706dc9a3ed71c8872028703bc40da0`. All packaged artwork, public provenance, credits and Electron notices still match source; Chromium notices remain present. The updated Linux smoke digest matches and its errors array is empty. **Technical correspondence gate passes for this repaired development candidate.** Commercial/AAA rejection remains in effect.

The release script now substitutes .json.gz evidence only after comparing SHA-256 of raw JSON with decompressed gzip bytes; mismatch or invalid gzip throws into the existing incomplete-release handling. Raw source files remain locally intact. Independently decompressed all three real traces and compared exact bytes, not parsed JSON semantics:

| Raw trace | Raw bytes | Gzip bytes | Exact match |
| --- | ---: | ---: | --- |
| gameplay-v0.2-pilot.json | 65,679,217 | 1,272,712 | Yes |
| gameplay-v0.2-experiments.json | 76,133,528 | 1,526,956 | Yes |
| gameplay-v0.2-quarry-holdout.json | 4,044,229 | 83,803 | Yes |

The three ignore entries are exact current-version raw paths; historical evidence paths remain unaffected. Lossless compressed files can therefore preserve the evidence without duplicating large raw traces in the archive. This was a static filter review plus checks of the actual evidence files, not a full release execution.

Independently verified all six files listed in assets/art-sources/v0.2/MANIFEST.json against recorded SHA-256. The four preservedSource references resolve, match their original generated outputs byte for byte and match runtime artwork hashes. Both preservedReferenceInput files resolve, match original repair inputs, and match referenceInputSha256. Original/reference images are now portable source-archive assets rather than solely workspace paths. Exact generation requests remain chat records; README correctly calls stored briefs summaries.

Windows packaging explicitly sets signAndEditExecutable=false. This host cross-build skipped PE resource editing and signing without Wine; custom executable metadata/icon and signing remain pending a native Windows builder before commercial release. A configured PNG icon and matching ASAR do not establish finished Windows executable branding, successful Windows launch or installer trust. Linux smoke limitations, clean-machine/platform/install gates and all other commercial/AAA gaps remain unchanged.
