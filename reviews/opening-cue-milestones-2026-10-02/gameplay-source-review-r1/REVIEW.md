# Independent gameplay SOURCE review: milestone cues R1

**ACCEPT the proposed source behavior within its stated in-memory, first-contract scope. No misleading cue or gameplay/save invariant defect found in the changed source. REJECT any claim that this review establishes a build, runtime success, natural late-binding frequency, human fun, visual/native128 quality or platform acceptance.** This is independent source reasoning; the author’s own source-traced cases and grammar receipts were not treated as gameplay evidence. No game/server/browser/build or source module was executed by this reviewer.

Candidate `/workspace/scratch/opening-cue-milestones-source-r1/src/main.ts` exact SHA256 `87a9bd7c2319522f77db7ea9e2edc306bb6124b019306dc220087f6b9b7762f4`. Parent B `/workspace/scratch/starter-static-recovered-stage-r1/src/main.ts` `d1e71626b4c70679f4ba692b62ccb2aea0dbe5ce74e9a1426b6208fc26a45fe2`. Candidate MANIFEST.json `1dcad690ed1402393bfe15a467544b97e596d3918356a821dfec485f98baa24d`; FORWARD.patch `f7a35bf1d5409540d17ca9a1b67812707aa4cc8a92bd86c5439c13dd4c5a39c8`. Parent engine.ts reviewed previously `7dca47973c0d78a130730450215569fa7747a1cb043764b16217c1b9c0ce6bf8`. Parent aggregate identities remain source65b31b3f21e34a624bdac962e4919c7dc1791e502eb6cfdb1612103b8036fe9c/output960e723da3b98d31e99e2b4ce6ee2195dd9fea1bfce9c8254b3cb65c04b7b49d; this candidate is not an output rebuild.

Read candidate patch, independently compared exact parent/candidate source with diff, inspected all milestone assignments/references, and traced save load/recovery, accepted dispatch, new/retry, render/terminal, preview, selection/cancellation and resume paths. The changed game source is main.ts only. This reviewer wrote only this new review directory. Own text under64KiB; no candidate/parent/stage/packet writes and no copied full source.

## Later-turn binding and first Order

Candidate main.ts812-813 replaces turn1 gating with first-contract scope, `binding !== done`, no living allies and a currently legal summon. Therefore a fresh run whose first turn lacks a summon, or lacks energy for one, does not falsely complete the milestone. A naturally later legal summon can expose `Bind your first creature.` while pending. This is a source branch capability, not an observed draw frequency or actual later-turn run.

Successful canonical dispatch is the only ordinary-play updater (main.ts405-411). After the unchanged-state rejection, an actual ally summon event in opening battle marks binding done. A completed summon may trigger arrival effects or terminal cleanup; using the event rather than surviving roster preserves the milestone even when the resulting canonical field is empty. Merely previewing the same reducer result does not pass through dispatch. A spell with no ally summon event cannot complete binding.

Main.ts815-821 shows generic READY/free-Order guidance while no committed opening Order is known, a currently legal attack exists and a targeted card is not selected. Selecting a READY binding changes the wording to Choose a hostile/Order costs no energy. Canceling does not finish the lesson. Ending a turn without commanding leaves orderDone false; when a surviving/replacement READY ally can attack on a later turn the cue remains eligible. A committed attack, including an all-blocked strike or retaliation-death, marks orderDone true because the command was issued; HP damage and survival are not requirements. Re-readiness on a subsequent turn or ready spell does not revive that completed lesson in the same window.

## Purity, failed actions and terminal correctness

- `consequencePreview` at main.ts568-570 calls applyActionWithEvents on the current canonical state, returns the clone/result description and has no milestone update. The engine only clones legal accepted actions; existing reducer/save rules are not edited.
- `cancelSelection` at250-254 clears selection and renders/restores focus; drag cancellation uses the unchanged tactile controller. Inspect/modal close/hover and first-target comparisons contain no milestone assignment. Selection itself also does not assign the record.
- Dispatch rejects settling/disposed/layout-pending states before action application and rejects an unchanged result before milestone updates. Thus an unavailable action or a canceled selection cannot falsely mark binding/Order complete. Legal attack identity is still enforced by the existing reducer; this change does not grant an extra command or remove an energy requirement.
- The milestone assignments happen after canonical replacement but before optional animation/audio and before the terminal hold. Optional presentation failure cannot undo the committed lesson or become the sole source of its completion.
- `render()` main.ts483-489 hides dock outside battle and calls renderBattle only for battle (including the existing fallback branch). Reward/victory/defeat does not introduce a binding/Order affordance; an existing temporary final-strike hold remains presentation of the completed fight. Every new cue still requires floor1 and an actual legal summon/attack. Later floors suppress both lessons.

No milestone data is placed in GameState, reducer, save(), localStorage, draw ordering, action generation or consequence arithmetic. save() main.ts209-212 still stores only canonical `state`. This is a transient presentation change. CSS, input ownership, focus restoration, native query/defaults, audio, motion and art bodies are unchanged by the exact diff. Source reasoning does not prove pixel layout or actual focus behavior after a build.

## New run, same-window resume and reload history

| Case | Independently traced result |
| --- | --- |
|New campaign/same-seed retry|start() main.ts444-449 resets pending binding/orderDonefalse after createGame, before initial battle render. Same seed does not reuse the old lesson record. A reducer start also resets it.|
|Return to title/resume in same window|menu/resume at main.ts1319-1323 change presentation/replace the existing savedRun but do not reset the record. save() always assigns savedRun to the same current canonical state, even if persistent storage fails. Milestones therefore remain associated with the current window's run. Opening/canceling a new-run dialog alone does not reset them.|
|Validated or recovered save with living allies|load initialization main.ts127-130 marks binding done, so an existing binding is never labeled as a first binding. Recovery follows the same initialization.|
|Loaded save with no allies and cardsPlayed0|Pending is justified by actual rules: a summon increments cardsPlayed. No committed binding can have existed in an ordinary run with zero cards played. First-binding wording waits for a legal summon.|
|Loaded save with no allies and cardsPlayed>0|History is unknown, including a prior binding that died. The cue says `Bind a creature.`, not `Bind your first creature.` A subsequent committed ally summon makes it done. It does not guess history from truncated log/discard.|
|Loaded save with any acted ally|An acted ally proves a command was committed under current rules; orderDone true suppresses the lesson.|
|Loaded save with READY allies and unknown earlier Orders|An earlier turn/ready spell may have reset acted. orderDone false can repeat the generic current READY/free-Order reminder. The wording does not claim this is the first historic Order, and the legal-attack predicate makes the affordance true. This is a deliberate persistence limitation, not a reliable recovery of historical completion.|
|Loaded terminal/map/later-floor state|No battle render/first-contract affordance is falsely exposed. A fresh retry correctly resets, while later floors remain excluded.|

The implementation must be described accurately as persistent **within one window's current run**, with conservative generic reload guidance. It does not preserve exact lesson history across reload. If exact once-per-run behavior across reload becomes a requirement, this version does not meet that stronger requirement; it would need separately scoped persistence or trustworthy history. Current generic reload behavior is not misleading.

## Acceptance boundary and next evidence

No source blocker found. The concrete hypothesis is that first-contract legal-binding/free-Order guidance survives a naturally late first binding and an intentionally unspent first command, then retires after actual committed milestones without changing game rules or saved state. Source branches support it and avoid false first-binding claims on unknown reload history.

Both prior actual R3 and R4 had a first-turn binding; neither validated this candidate or natural late behavior. Ongoing actual R5 is frozen B and remains unreviewed until Root's closure notice. Candidate build/type verification, actual interaction/cancel/save purity, terminal/reload legibility and target/input/pixel behavior remain unverified. Grammar parsing alone cannot supply those approvals. Five minutes of fun, observed novice timing, art/native originality/coherence and platform/default acceptance are expressly unaccepted.
