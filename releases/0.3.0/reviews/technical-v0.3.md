# Independent technical review — v0.3 acceptance draft

Date: 30 September 2026. Reviewer: independent release_audit agent. **Status: acceptance criteria only; no v0.3 source/build approval yet.** Source changes are underway. Existing v0.2 approval remains limited to its preserved development artifact, not AAA or Steam readiness.

Baseline: releases/0.2.0/manifest.json identifies source commit d7604f220c3c6e242ef63ac526c1f493d542db26 and runtime digest 006db8571a5c1697b21bcbe51434161e53bb75580c5b72bed852efdd4da7bee9. Inspected baseline engine/content hashes remain 21bafb33832ec2d3ee1ca4ead9486825510bd380b62e143a8736465f1ad4110b and 2f45160b3e577a7cd44381cb361c4407661a68819ff827a24b8ab34ce15c4234. Final review must record the actual frozen candidate hashes and assessed artifacts.

## Final-kill feedback and presentation suspension

Acceptance requires immediate canonical reducer commitment and save after the action, including reward, victory or defeat. Delaying the displayed next scene must be presentation-only. Animation snapshots, dying units and transient controls must never enter the saved GameState, mutate previous/next rule objects, replay damage, repeat rewards or change seeded results. Reload during a presentation hold must restore the canonical post-action state.

The final action should communicate source, impact and target removal before the next scene replaces it. Any hold must have a documented brief upper bound and reach the next scene even if rendering fails. Reduced motion, unavailable arena and unsupported assets must have an immediate usable path. Render/effect errors must not interrupt accepted action commitment/save; the v0.2 dispatch called arena.playAction before state assignment/save, so the new flow must defensively isolate that optional side effect.

While a resolution presentation is active, mouse actions, target selection, end-turn keyboard shortcuts and duplicate clicks must not apply stale combat input or advance the new reward unintentionally. Busy presentation must be represented accessibly. Title/new campaign/retry/reset/disposal must invalidate pending callbacks so an old timer cannot overwrite a newer campaign. A hidden tab must not cause an unbounded hold: test visibility changes and return after the deadline. Changing motion preference must settle or cancel the hold coherently.

Required focused evidence: ordinary last-enemy kill into reward; boss last-kill into victory; hunter death/retaliation into defeat; near-simultaneous duplicate input; reload before presentation finishes; title/reset then old callback; hidden/resumed tab; reduced motion; missing/throwing arena. Compare stored state with the reducer's exact immediate result. Root owns execution; reviewer must distinguish inspected test source from tests personally run.

## Optional local human feedback export

Feedback must be explicitly voluntary, clearly distinguished from agent/simulation evidence, and usable without changing a campaign, difficulty or settings. Opening, cancelling, empty submissions and export failure must not lose or advance a run. Ratings must not manufacture a positive result through preselected praise or forced submission.

The export should contain a versioned, compact allowlist: candidate identity, voluntarily provided answers, and disclosed contextual run information needed to interpret them. Bound free text and rating values. Do not automatically add usernames, machine paths, identifiers, browser/device fingerprint data or unrelated localStorage. If including a seed or run summary, show what will be included. Render free text as text, preserving the earlier dossier injection repair.

There must be no background upload, telemetry endpoint, email/Slack sending, filesystem privilege, Node integration or new privileged preload/IPC. Browser Blob download is sufficient if it works in both production browser and packaged Electron. Verify the user-initiated offline download, parse the resulting JSON, inspect its exact keys and text, test escaping and failed storage/download paths, and revoke temporary object URLs without breaking downloads. An exported response is an individual report, not proof of broad enjoyment; actual prospective-player feedback still must be gathered.

## Pose atlases and art provenance

New poses must preserve species/card identity, full anatomy, stable scale/origin and clear slot ownership. Distinguish attack, impact and recovery; do not animate the wrong source or remap surviving units over a dying body. Six-per-side occupancy must remain readable. Reduced-motion mode must settle to static accurate presentation. Missing image/pose must fall back to the current usable art and accessible HTML rules, not prevent a run.

Every new runtime image/atlas and metadata record must be included in public build provenance with exact hashes, dimensions, mode, cell/pose layout and mapping. Preserve generation originals, repair inputs and rejected comparisons separately, matching MANIFEST and reference hashes. Exact prompts should remain distinguishable from brief summaries. Source/build digest matching must cover all public art and consumed credits. Atlas pose frames are not rigged 3D character animation and must not be advertised as such.

## Release and commercial gate

Freeze source, review and art inputs before building. Existing exclusive release locking, non-overwriting version directories, clean source commit, packaged-version/digest checks, archive hashes, lossless compressed review verification and old-version preservation must remain intact. v0.2 archives/reviews must not be replaced by v0.3 evidence. Verify web/Linux/Windows provenance against independently recomputed source input hashes after final changes. Retain source art references and distribution notices.

Window/remote-request/Node sandbox restrictions must remain unchanged unless an actual authorized requirement and review justify alteration. Windows cross-build PE resource editing/signing remain skipped with signAndEditExecutable=false; native Windows metadata/icon, signing and launch are outstanding commercial checks. Linux --no-sandbox/Xvfb smoke remains limited evidence. No clean-machine update, normal sandboxed launch, controller/Steam Deck, target-hardware soak or Steam publication is established by an archive.

AAA quality and exceptional human enjoyment remain unapproved. New poses, better transitions or an export button can satisfy a measured development improvement, but they cannot substitute for rigged-animation/audio craft where required by the production target, independent comparative graphics/performance evidence, human playtesting, rights/store review or actual Steam installation. Final approval must be earned against the frozen candidate and report regressions honestly.

## Independent source audit after implementation — 30 September 2026

**Decision: inspected source passes the technical gate for a development candidate. Final visual/frozen-package correspondence and native feedback download checks remain pending. AAA/commercial Steam promotion remains unapproved.** Original acceptance criteria above are preserved. Per the latest owner instruction in AGENTS.md, convincing 2.5D painted animation is an accepted production route; full 3D/rigged runtime models are not a required technology gate. Craft, performance and actual player evidence remain required regardless of that route.

Independently recomputed current frozen build-input digest and compared it with actual production web provenance:

`1ef47ce481c3f8722e624fe6df1540d2957462c20c8ba7213c77ed4583a7f258`

Both values match. This supersedes preliminary 50c4/0956 and the 936821 candidate; the last change addressed independently observed clipped deck-card statistics through CSS. Native artifacts must match the final digest, not an earlier GO message.

| Inspected file | SHA-256 |
| --- | --- |
| src/engine.ts | 4b24a1bd90a05326ec76db361001bf034af6f6ed0e5f86bcab295e9ae0a5f5af |
| src/content.ts | 2f45160b3e577a7cd44381cb361c4407661a68819ff827a24b8ab34ce15c4234 |
| src/main.ts | e39ff4c16dc8dcb164d42dad4e84f1190354876f27b220628dc7150b16531371 |
| src/arena.ts | ec0b44aadc869dbf3903f3c6c3d1d0ef96f2c00caed4c75c444be790250620ea |
| src/art.ts | c8ecd30136abb54d865fa80e27649da0049db3c65f879cbfa2a80d2269a14d1d |
| scripts/build.mjs | 10aebb7f8c3e580ad8e816e523ca34abe37982caa802b333b60d9b7773831d21 |
| scripts/release.mjs | 5e5869b05c111637f40e47dc2bfb0721bff3ef4d1b6c6fc2a06b14767953fc58 |
| public/art/PROVENANCE.json | 2affea707126fe795107c66e4f5b3611e79994f08a59b9cdc70107c6f12ac6d6 |

### Save/presentation safety

Accepted actions now commit state and save before optional arena/audio effects. No animation fields enter GameState, schema 2 remains supported, and feedback does not modify localStorage. The presentation hold has a 1200 ms cap, an epoch guard, disabled stale combat buttons, keyboard/action gating and aria-busy. Start, title, retry, unload, visibility changes and motion changes cancel or settle presentation. Effect exceptions are caught after canonical persistence. Canvas-unavailable fallback reports zero busy time.

Personally ran four additional production-browser diagnostic scenarios on the preliminary QA build with this lifecycle logic: a valid seed-121 single-target final-kill fixture committed the exact reducer reward state before the hold; hidden-tab change settled it without save changes; switching OS reduced motion settled within 400 ms; starting seed 42 during a hold remained exactly createGame(42) after old callbacks had time to fire; unavailable Canvas2D skipped the hold and exposed salvage. No page errors occurred. These diagnostics tested presentation lifecycle, not human enjoyment or final packaged-executable behavior. Preliminary CSS/art refinements were still in progress; the later final CSS-only card-height patch did not alter these control paths.

Reload during hold, stale E commands, reduced motion and literal loaded-name escaping have meaningful focused browser regressions in source. The integration owner reports 49 passing rule/event tests and eight production-browser tests on the 936821 build before the final card-height CSS repair, including a complete control-driven campaign and save/reload equality. That suite execution is attributed to the integration owner; this reviewer ran the extra diagnostics and source probes described here. Final affected visual checks remain separate.

### Event API and regression repaired

The additive applyActionWithEvents API returns transient resolution observations while preserving the ordinary reducer and saved state. Sources/targets follow actually resolved hits, fallback, early hunter death, retaliation, reinforcement and recovery. Summon/intent snapshots are detached from saved state.

This audit found a real presentation regression: control/rally initially emitted no observations, and the authoritative empty event path suppressed the previous Silence/Pack Edict visual cues. Reported it independently; owner authorized narrow repair. Inspected repaired code emits typed control and buff observations and renders nondamaging cues. Those cues are excluded from recoil/physical movement, avoiding invented damage.

Personally probed travel, hound summon, Silence and Pack Edict on final engine source against the archived v0.2 reducer. Every resulting state serialized identically; incoming states stayed unchanged. Events included control/buff as appropriate. Mutating the returned control intent snapshot did not change the returned saved state. Existing broader paired-replay and event regressions are inspected source/integration-owner execution evidence, not an independently claimed full suite here.

A separate arena review found physical reach/contact timing disagreed with impact timing. The subsequent source repair aligns its movement peak and impact; visual reviewer owns actual pixel/timing confirmation. No unreported gameplay/economy rebalance ships as part of this source audit.

### Feedback, asset loading and security

Field report is optional and user initiated, with unanswered replay intent as default and bounded 1000-character text. Context uses a compact explicit allowlist: build/version/channel, screen, seed/difficulty/phase/progress/health, deck/relics and numeric statistics. No arbitrary names/logs, machine identifiers, paths or unrelated stored values are copied. Free text is JSON data; status uses textContent. There is no upload request, telemetry service, renderer Node integration, new preload or IPC. Report creation/cancel cannot advance a campaign. Production build embeds the same source digest used by provenance for later report attribution.

The local Blob download path still needs confirmation in actual packaged Electron. This audit does not claim a failed download can be detected in every browser, or that the presence of an export button constitutes collected human feedback. Integration browser regression checks negative answers, literal script text, no external requests and unchanged storage.

Owner QA found CSS image URLs resolved incorrectly relative to built /assets/ CSS and left hunter art blank. Inspected repair constructs document-absolute art URLs. Personally verified computed hunter/courtyard CSS URLs point at /art/ and both requests returned HTTP 200 in the production browser. Offline file-protocol correspondence remains the package gate.

### Art provenance and history

Personally verified all six runtime images against recorded hash, dimensions and mode; every preservedSource matches runtime bytes. All seven v0.3 art-source MANIFEST records match, including rejected atlas inputs and repair requests. All preserved reference paths resolve. Independently measured alpha greater than 64 in each hound pose: all six opaque bounds fit the actual crop rectangle [32,96]–[480,480] inside its cell. This proves checked containment only, not convincing anatomy/motion, seam quality or visual craft.

Hunter and six-pose hound outputs are original AI-assisted artwork with pending rights review and retained source inputs. Metadata explicitly identifies illustrated pose transitions, not skeletal animation. Historical v0.2's four archive checksums were independently rechecked and all passed. No old release/review was replaced.

### Remaining gates

No unresolved source blocker was established after the reported repairs. Before preserving v0.3, independently verify final web/Linux/Windows digests and actual ASAR versions, notices and art; run native Linux interaction/export checks; preserve focused visual/performance findings and archive checksums. Windows launch/native PE metadata/icon/signing, normal sandboxed clean installs/updates, controller/Steam Deck, hardware soak, rights/title/store/AI disclosure, Steam depot testing and real prospective-player evidence remain outstanding commercial gates. Source/agent approval cannot establish exceptional human enjoyment or AAA craft.

## Final package and local export gate — 30 September 2026

**Final technical decision: approve the matching v0.3.0 development candidate for preservation. No unresolved technical archive blocker remains in the inspected source/artifacts. Commercial Steam and AAA promotion remain unapproved.** This decision supplements rather than replaces the criteria, provisional checks and repaired findings above.

Independently recomputed current build inputs again: source, production web, actual Linux ASAR and actual Windows ASAR all identify `1ef47ce481c3f8722e624fe6df1540d2957462c20c8ba7213c77ed4583a7f258`. Both packaged package.json versions are 0.3.0. Both app.asar files have SHA-256 `ce5ae2673965aad150eed9f332ef903fa0aa4a75af1bada1e010b0dc951cf9ce`.

Compared actual extracted bytes for all 12 production dist files with the current web build, including JavaScript, CSS, all artwork, credits and provenance. Every file matches in both platforms; desktop/main.cjs and icon bytes also match source. Packaged provenance's individual source hashes match independently hashed inputs. This verifies actual bundled assets in addition to declared digests.

Actual packaged desktop code preserves nodeIntegration=false, contextIsolation=true and sandbox=true, blocks external requests/windows/navigation and contains no privileged preload or renderer bridge. Electron license notices match installed runtime bytes on both targets, and nonempty Chromium notices are present. Packaging verification does not certify absence of vulnerabilities in the entire Electron/Chromium dependency runtime.

Read reviews/linux-desktop-0.3.0-smoke.json: matching runtime identity, empty errors, successful launch/map/summon/command on the constrained Linux host. Read reviews/linux-feedback-0.3.0-smoke.json and inspected the executing test script: actual native download reports completed, downloaded report identifies the matching packaged build/seed 121, preserves negative replay intent and literal synthetic script text, and leaves storage unchanged with no page errors. Native hunter portrait decoded at 1199×1312. The script's save-path selection hook is test-only through Playwright's main-process evaluation; production shell gains no privileged download API. Execution belongs to the integration owner; this reviewer independently checked package bytes, identities, script behavior and recorded evidence.

These native checks run under Xvfb with --no-sandbox. Normal sandboxed clean-machine installs/updates and declared target hardware remain unverified. Windows has only been cross-packaged and inspected; no native Windows launch was tested. signAndEditExecutable=false remains explicit: PE executable icon/version resource editing and signing were skipped on this host without Wine. Finish native Windows branding/metadata/signing and platform testing before commercial claims.

Archive with the clean frozen source/reviews, exclusive release process and checksum verification; preserve v0.1/v0.2 and all rejected findings. The owner-authorized foreground process continues after this checkpoint. Better presentation and an optional export route do not constitute received human feedback, exceptional enjoyment, Steam publication or AAA craft approval.

## Post-gate finding: reachable invalid campaign save — 30 September 2026

**Revised decision: preserve v0.3.0 only as a known-defective development archive. The save-reliability gate fails; stable/polished playable-quality, commercial Steam and AAA promotion are blocked.** The earlier approval above records the evidence available at that checkpoint and is superseded by this finding. Historical preservation remains useful for comparison and reproduction; it is not an approval of campaign-resume reliability.

Independently replayed the complete evidence in `reviews/solo-v0.3/silence-overflow-campaign.json` without state injection: seed 1989, Initiate, 119 actions. Every action belongs to `legalActions`, every reducer call accepts its action, all inputs remain unchanged, and current v0.3 and archived v0.2 states serialize identically after every step. The first invalid state is action 119; the recorded before/after states match this replay exactly. Frozen engine SHA-256 remains `4b24a1bd90a05326ec76db361001bf034af6f6ed0e5f86bcab295e9ae0a5f5af`.

At floor 10, turn 3, three legitimate Silence casts against Ironjaw's guard intent grow its label from 35 to 62 to 89 to 116 characters. The final accepted action is `{type:"play",index:2,target:"e34"}`. Its preceding state passes `validateState`; its resulting state fails. `src/engine.ts`'s control effect appends ` · silenced (armor remains)` on every cast whenever the label includes `block`, while the same file's save validator rejects intent labels longer than 100 characters. This is an inherited reducer defect, not a newly introduced presentation/event discrepancy.

The consequence reaches normal persistence: `src/main.ts` saves accepted state directly, but on reload accepts saved campaigns only through `validateState`. Reloading between this cast and a later intent refresh rejects a legitimately played campaign and displays the incompatible-save/new-campaign notice. Continuing without reload may later refresh the label; that does not satisfy reliable resume. Fix the repeated-status operation to be idempotent before any v0.4 promotion, preserve guard armor and gameplay rules, and add a regression that replays this entire legal campaign while validating every accepted resulting state and the saved/reloaded final state. Consider explicit recovery of already-written affected schema-2 saves rather than silently discarding legitimate campaigns.

Also independently detected that the initial evidence's `.gz` is semantically equivalent compact JSON but is not byte-identical to its pretty-printed raw `.json`. The release script's lossless-compression guard correctly rejects that pair. Regenerate compression from exact raw bytes and recheck before archiving; this is evidence packaging, separate from the runtime save defect. No implementation was edited by this reviewer.
