# Independent merged relic / Bone Thrall gameplay gate — v0.9 development

**Accept the exact merged candidate for scoped development integration.** This is a fresh independent browser gameplay gate, not an AAA, human-enjoyment, hardware-controller, native-installer or Steam-release verdict. The unrelated earlier component approvals were inspected for scope and were not substituted for these merged-build tests.

## Frozen build identity and scope

Candidate `/tmp/hollowpact-relic-bone-v09-root-r1`, HTTP port 4605, source digest `4bfa417ad790dd88a18868e10e7574666ae8bfc3187bdab1df4947c31231de61`: 78 actual source files and 56 complete output files. Retained baseline `/tmp/hollowpact-final-kill-v09-root-r1`, port 4610, digest `8a33f950ed57093a222baf9b7883a5c1ccf2deb2e8412429ef0fe05d370467cb`: 77 actual sources and 55 outputs. Both identify as development 0.9.0. The reviewer independently recomputed declared source hashes and ordered provenance digests, hashed every local output, and compared every complete HTTP body to its local file. Before/after identity JSON receipts are byte-identical for both builds.

Only existing `src/main.ts`, `src/art.ts`, `THIRD-PARTY.md` and `public/art/PROVENANCE.json` differ; only `public/art/bone-thrall-v09-r1.png` is added. The new PNG is 1,610,163 bytes, SHA256 `3697dd4cc89f1550e0688b34bb421939988c90ab78832ce83d53ddb81b372dfd`, 1254×1254 RGBA. `src/art.ts` SHA256 is `2e9a5429e01498e02b4ae333e7240e7e5abbb1a6d0418d2932a7afccc17b262f`. Engine, content, input, arena and style bytes are unchanged. The portrait-specific fallback position uses the new focal coordinates without changing catalogue or combat rules. Provenance labels remain development inputs with rights clearance pending.

No frozen source, output, art input or existing review was written. This packet records hash-based references to the retained media/dependencies; it is not a standalone rebuild bundle. No fresh reviewer rebuild or native execution occurred.

## Own actual execution

`RESULTS.json` contains 18 accepted browser contexts: twelve paired baseline/candidate contexts spanning ordinary raised-Thrall turns, terminal kills and rewards; six additional candidate contexts spanning map relic inspection, missing new-image requests and unavailable arena Canvas. Engine kind 1/schema 2 was tested at 390×844 and engine kind 2/schema 3 at 1280×844. This is not a full schema-by-viewport matrix. Chromium ran muted/software rendering, with motion enabled for the terminal observations and reduced elsewhere.

These contexts produced 20 actual canonical gameplay actions, 60 exact serialized-save checkpoints and 18 actual reloads. Six baseline/candidate pairs have identical complete action/state/event records and serialized-save hashes. The independently created diagnostic fixtures validate card/state conservation but use assigned relics, selected encounters and modified terminal stats; they were not earned campaign runs or human playtests. Their actual UI actions execute normal production handlers and normal engine transitions.

The Acolyte genuinely raises a new Bone Thrall on the first actual end-turn; that unit acts on the second actual end-turn. Its dossier reports catalogue-exact passive, health, attack and announced intent. Candidate Canvas draw records use the new 1254-pixel skeletal portrait; its CSS dossier points to the same PNG at 65%/13% focal coordinates. Baseline retains the old armored specter while producing identical gameplay and saves.

All four paired terminal contexts naturally expose the held field after the actual command kill. The actual raised Thrall displays `0 of 8 health`, `Quarry down` and `0%` health meter; the field is busy while canonical reward state is already saved. Settled and reloaded saves remain canonical. `HELD-SUPPLEMENT.json` adds one fresh candidate schema-3 terminal context, one actual attack, four save checkpoints and one reload. Its naturally held DOM confirms every scene/dock button is disabled; after the hold, reward relic inspection works and returns focus. There are five actual held observations across these contexts. No artificial timing override or unavailable performance/native claim is made.

Candidate map, reward and post-kill reward contexts expose the persistent `Inspect relic effects` cue with six owned-relic buttons. Enter opens Dead Man’s Coin with exact catalogue text; Escape restores the same semantic button; inspection leaves complete localStorage unchanged. Two reward contexts exercise the actual standard-gamepad adapter using a synthetic neutral/A/B edge sequence: Iron War Brand opens and closes, origin focus returns, and storage stays unchanged. This is adapter coverage, not physical controller certification.

The six candidate relic contexts also refuse a prototype-key mutation without opening a dossier or changing storage. Four additional fresh contexts in `OWNERSHIP.json` test both schemas with zero relics or one owned Black Contract Seal: a DOM-injected known but unowned Wraithglass Shard and a prototype key are both refused; storage remains unchanged. Those are adversarial DOM diagnostics, not player-facing features.

Together the records contain 23 accepted fresh contexts: 18 main + one held-control supplement + four ownership guards. The main and supplemental gameplay records total 21 actual actions, 64 save checkpoints and 19 reloads. There were no recorded page errors or horizontal overflow in the accepted main/supplemental contexts.

## Fault handling and viewed visual evidence

Missing-new-PNG requests were independently aborted for both schemas. No draw of that PNG occurs, but name, health, passive, intent, end-turn actions, saves and reloads remain usable. The CSS dossier image area becomes an empty dark frame; it does not itself provide the Canvas heraldry fallback. The separate no-Canvas injection returns null only for the arena: its canvas is hidden and a visible child notice with role `status` states that illustration is unavailable while panels remain usable. Both schemas complete ordinary turns and preserve saves; the CSS dossier portrait remains visible because its image path was not blocked.

The reviewer actually viewed five retained images: baseline normal dossier, candidate normal dossier, candidate missing-image dossier, candidate no-Canvas dossier and candidate mobile reward. The skeletal Thrall now matches the unit’s identity better than the retained armored-specter portrait, with essential dossier text visible in each fault case. This remains one cutout with inherited sparse movement, not articulated creature animation or an AAA graphics claim.

The mobile reward screenshot preserves the inspect cue and all six relic controls with a visible focus outline and reachable salvage. It also exposes an inherited fixed-card-height defect: long hound descriptions partially clip the `Add to deck` footer. Related clipping was already recorded against both builds in the earlier relic review; this merge changes no card CSS. This is a concrete next layout priority, not proof that reward-card craft meets the release target. This particular diagnostic screenshot has no newly captured baseline pixel pair, so no pixel-equality claim is made.

## Preserved harness failures and limitations

The 18 accepted main records were accumulated across corrections to the independent harness on unchanged frozen source/output bytes; they are not represented as one uninterrupted passing invocation. Every initial failure and script remains in this packet:

- R1 changed `data-relic` to a prototype key and then tried to restore it through the now-nonmatching selector. Three completed records remain in `FAILURE-r1.json`. R2 uses stable `data-focus` for mutation/restoration.
- R2 wrongly expected the null-context fallback class on the wrapper. Actual fallback is a child status notice. Fourteen completed records remain in `FAILURE-r2.json`.
- R3 accidentally rewrote the retained-results read path to nonexistent `FAILURE-r3.json`; it failed with ENOENT before browser execution. The script/log remain; no synthetic failure JSON is invented.
- R4’s unbraced no-Canvas check applied the hidden-canvas expectation to the missing-image case as well. Missing-image rendering correctly keeps Canvas visible. Sixteen completed records remain in `FAILURE-r4.json`; R5 scopes the assertion correctly and completes only the remaining two contexts, then validates the full six pairs.

These were harness defects, not repaired product defects. Ownership and held-control supplements passed separately. All reviewer browser contexts and owned execution sessions were closed. Acceptance applies only to these exact source/output hashes and observed development behaviors; it does not certify full-run enjoyment, sound quality, universal accessibility, physical controller support, native platforms, final asset rights or Steam readiness.
