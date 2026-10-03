# Independent technical/release review — source v0.1.0

Date: 30 September 2026. Reviewer: independent release_audit agent. Decision: **REPAIR REQUIRED before prototype promotion; commercial Steam readiness rejected.** This is a source review while UI/arena work is still in progress. No distributable or Steam depot was supplied or tested. Findings are not a claim about subjective fun.

## Candidate identity and scope

At inspection, package.json reports 0.1.0; source is uncommitted work against initial commit 98660a7. These hashes identify the actual inspected rules:

| File | SHA-256 |
| --- | --- |
| src/engine.ts | dfe48bdc5f765545535e6edeb30fe8faabe9184a3473817b0935291ddd50237d |
| src/content.ts | c64b68b7813ca4e923faf7b23ca36f871522772efc713fa1134bcbcfe06a9a71 |
| scripts/release.mjs | 6e7b4274edf97c2a7010596d606328f16f0b7ad7689e347cca91359fc06741b3 |
| desktop/main.cjs | 4863c478b2278f9cdbaf997af57c69ac8176a632933375f77e1bf159944a725d |

Read engine, content, engine tests, simulation, release script, desktop shell, package/build configuration, attribution, README and production/engine documents. Did not edit implementation. UI and actual runtime presentation require separate review.

## Evidence

- `npm test`: 20/20 pass. Existing coverage includes purity, serialized deterministic actions, card conservation, command limits, targeting/fallback, enemy cycles, temporary-stat resets, economy, rewards, death and victory.
- Independent extra simulations: random legal policies on seeds 1001–1300 at each difficulty 0, 1, 2 (900 complete runs), using invariant validation after every action. No invariant failures or incomplete runs. Difficulty 0: 6 wins/294 losses; difficulty 1: 0/300; difficulty 2: 0/300. Random-policy losses do not establish unfairness, and successful termination does not establish enjoyment.
- Independent corrupt-JSON probes found two validator weaknesses described below. These are not ordinary reachable gameplay states; they matter because validateState explicitly guards loaded saves.
- `npm run build`: TypeScript passed, Vite failed because index.html did not yet exist. UI development was explicitly ongoing. Therefore no export/launch claim is verified by this review.
- No dist/ or build-desktop/ artifacts existed when packaging was inspected.

## Actionable findings

### P1 — Desktop artifact identity is checked only by version

`scripts/release.mjs:25–34` accepts an existing app.asar when its package version equals the requested version. An earlier desktop build made from different source but the same development version is accepted against the newly recorded sourceCommit. The archived web and desktop games can consequently implement different rules despite one release manifest. This breaks the review-to-artifact chain.

Repair: build desktop artifacts from the frozen source during release, or embed and compare source commit plus relevant built-file hashes. Reject stale same-version artifacts. Re-review the actual archives after repair.

### P1 — Web distribution lacks required Three.js license notice

`THIRD-PARTY.md` correctly says to preserve Three.js's MIT license, but `scripts/release.mjs:21–22` distributes only dist and no reviewed build step copies that license into dist. A link in source documentation is not the full copyright/license notice shipped with the bundled library.

Repair: include a distributable attribution/license file with the full Three.js notice in web output, and verify notices in both unpacked desktop platforms. Electron runtime LICENSE/LICENSES.chromium.html exist in the installed toolchain, but their presence in a final artifact is unverified. Complete dependency/provenance review before commercial distribution.

### P2 — Validator accepts impossible floor/encounter combinations

`validateState`, especially `src/engine.ts:797–843`, checks broad battle/reward route names but does not constrain a floor to the routes available at the preceding node. Reproduction:

1. Start seed 77 and travel to the first battle.
2. Set floor=10 while retaining route=['battle']; keep one existing enemy with HP=1.
3. Set hand=['spark'], draw to deck with one spark removed, discard=[]. This preserves card multiplicity.
4. JSON stringify/parse the state: validateState returns true.
5. Play spark at the enemy: the legal reducer returns reward at floor 10, and validateState returns false.

Repair: validate encounter phases against the allowed route at ROUTES[floor-1], including boss-only floor 10, and require valid terminal combinations. Add a regression for an accepted-save-to-invalid-state transition. Valid saves should remain valid after legal actions.

### P2 — Accepted menu save has no continuation in legalActions

`validateState` accepts a JSON clone of createGame(77) changed only to phase='menu'. `legalActions` returns []; the state is neither victory nor defeat. The actual reducer emits no menu state, and no supported menu-save workflow is documented. If such a save is restored into the run UI it may appear as an active state without a continuation.

Repair: reject unsupported menu saves, or implement/document a complete explicit menu-state restoration path. Re-review with the actual UI; this source review does not claim a confirmed UI softlock.

### P2 — Concurrent release invocations can violate preservation

`scripts/release.mjs:10` checks destination existence before tests/builds; `:19` uses recursive mkdir later. Two release invocations can both pass the initial existence check, then write into the same directory. Ordinary sequential reruns are correctly rejected, but an orchestration race can overwrite archive evidence.

Repair: atomically reserve the destination with nonrecursive mkdir and/or use an exclusive release lock; never permit two writers to an existing version directory. Keep failed reservation/build evidence without treating it as a published release.

## Positive observations and limits

Rules are deterministic, bounded, renderer-independent, and preserve incoming states. Living summons own real deck copies. Energy-costed draw and delayed spell discard avoid obvious self-draw loops. The tested runs terminate. Enemy intents remain stable and target fallback is documented rather than silently retargeting. Desktop shell disables Node integration, enables context isolation/sandboxing, denies new windows/navigation and blocks remote requests. No privileged preload or renderer IPC was found. These are useful protections; no packaged security or Chromium runtime audit was performed.

Release tooling correctly rejects sequential reuse of a version directory, refuses dirty-source archiving, hashes archived artifacts, records a source commit and preserves failed partial output. Manifest honestly declares development-prerelease and steamPublished=false. Reviews and source are archived. The script archives candidates; it does not enforce independent-review approval or stable promotion, so a failed review must remain visibly blocking in the production process.

The documentation correctly acknowledges missing Steamworks access, platform/install tests, human playtests, controller/Steam Deck evidence, store assets, rights and final dependency/AI provenance review. UNLICENSED project source is an owner decision to resolve; it is not proof the owner lacks rights to release their own game. No Steam account, AppID, uploaded depot, clean-machine install, Windows launch or purchase-quality evidence was verified. Commercial readiness remains rejected until those gates have actual evidence.

## Re-review requirements

Repair the artifact identity, distributable notices and validator findings; finish UI integration; produce a frozen build. Run regression and browser checks, inspect actual packaged files, and test startup/save/resume on declared platforms. Preserve this original review and add new evidence identifying repaired file hashes/build identity. Agent agreement must not substitute for human enjoyment or platform verification.
