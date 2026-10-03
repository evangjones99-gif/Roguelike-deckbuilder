# Independent gameplay/input review — v0.6 initial candidate

30 September 2026. Production digest `d33ce538e38d98eba6ec06f90660252d53d3f3fc0122c7316b229f043489b52c`, Chromium `/usr/bin/chromium`, 1440×900. Independent gameplay reviewer; implementation source was not edited. **Input acceptance is withheld pending the independently reported composition/blur repairs.** The tested deliberate-activation and focus repairs pass. This is not an AAA, commercial-release, physical-controller or human-fun endorsement.

## Actual production evidence

The harness loads the shipped build and calls its normal controls. It injects only standard `navigator.getGamepads` samples, never an adapter, host context, settling flag or parallel reducer. Diagnostic states are explicitly synthetic, validated saved states. Expected outcomes come from the immutable v0.5 source archive; the engine, content, world sampler, arena, art, tool art and CSS hashes remain identical to final v0.5. Main `dba47ae29bca37d099d04fd0d3d2bcb05948d4d7426b5ab7a331448206d46496`, input `4ae4ca1a2dadb41f3a51b8eba35dd41efed5ececb00d912edfbec2e346f9f69d`. Exact initial source snapshots/hashes are in [source-d33](gameplay-v0.6-input/source-d33/hashes.json).

**37 unique diagnostic scenarios pass**, combining [original batch](gameplay-v0.6-input/production-r1.json), [native-control correction](gameplay-v0.6-input/native-r2.json), [refused-API correction](gameplay-v0.6-input/refused-r3.json) and [outcomes/navigation](gameplay-v0.6-input/extra-r1.json):

- Both generations: held Enter selects once, suppresses repeated target activation, then accepts a released fresh Enter; Escape returns to the source; fresh command exactly matches the reducer. Removing the focused hostile or losing the binding to retaliation recovers meaningful focus. Space releases summon once through a shrinking hand. Held controller A cannot command or summon twice.
- Both generations: replacement Deck→card dossier→Deck→close restores the original external opener. Keyboard inspect and controller back recover source focus. Y opens the actual unspent-command confirmation without confirming it while held; fresh A confirms exactly.
- Actual final-kill presentation holds: the canonical result saves immediately; stale E cannot change it; fresh Start safely snaps the real presentation and opens Pause. Reduced-motion results do not create the hold. Mutual death, hunter defeat and an earned final-boss victory recover focus with motion on/off.
- Native Ctrl/Meta/Alt chords, contenteditable typing, seed and textarea typing, select and keyboard/controller range changes retain their relevant behavior and canonical state. H/B/T/I, hand wrap, cross-roster arrows, region shoulder navigation and unavailable-card inspection work in the sampled cases. An unavailable card stays inspectable without playing.
- Absent/refused controller API preserves keyboard. Refusal produces four reads over 1,001ms, rather than a per-frame failure loop. Disconnect/reconnect with A held, explicit hidden/resume emulation and neutral release prevent unwanted actions; hidden polling stops.

Three separate [supplemental lifecycle probes](gameplay-v0.6-input/lifecycle-r1.json) also pass: held initial connection requires release, malformed/nonstandard input recovers without guessing a device mapping, and analog A hysteresis requires a real release before committing a second action. These are additional evidence, not retroactive changes to the initial 37-case batch.

## Complete campaigns

There are **298 accepted actual input actions**, each checked against exact archived pre/post canonical state hashes:

| Campaign | Actual inputs | Result | Earned decisions exercised |
|---|---|---|---|
| Fresh kind2 Hunter, seed47101 | 179; native keyboard only, including radio arrows and Tab/Enter/H/B/E | Victory,58HP | 10 travels,58 plays,82 commands,16 turns,4 rewards,3 events,2 buys,2 removes,2 shop departures |
| Resumed kind1 Veteran, seed6503 | 119; synthetic-pad activation, native Tab navigation; legally simulated70-action saved prefix | Victory,41HP | 5 travels,38 plays,57 commands,11 turns,2 rewards,3 buys,2 rests,1 shop departure |

See [fresh campaign](gameplay-v0.6-input/fresh-campaign-r2.json) and [legacy campaign](gameplay-v0.6-input/campaign-r1.json). No DOM click or focus teleport drives these campaign actions/navigation. Both mid-campaign reloads preserve the exact state and generation. Motion is on; presentation holds block stale actions and leave useful outcome focus. The reused frozen heuristic chooses decisions; these are automated policy replays, not reports of human enjoyment. Legacy progression is pad-activated and keyboard-navigated, **not** a controller-only campaign or physical hardware result.

The [archived v0.5 comparison](gameplay-v0.6-input/archived-baseline-r1.json) separately reproduces both inherited problems in both generations using the preserved web ZIP: a held Enter commits the newly focused target, and the removed hostile leaves focus on BODY. The new initial candidate prevents those behaviors in the matched fixtures. Baseline serving was isolated at5193; candidate4173 was not replaced.

## Acceptance limits and next gate

The independent technical reviewer reports that adapter `onKey` lacks `event.isComposing` filtering, although main filters it, and requests blur lifecycle disarming. My source snapshot independently confirms the adapter lacks that composition check and a blur listener. These were **not covered by my passing trusted-keyboard/native-editing cases**; those cases must not be cited as proof that IME composition or focus-loss lifecycle is safe. The production input gate remains withheld until the repair and affected actual-host probes pass. Consult [technical input review](technical-v0.6-input.md) for its direct reproduction and scope.

No physical controller, native IME, OS background-tab lifecycle, controller-only free-text entry, Steam Input, Steam Deck, Windows input test or assistive-technology session occurred here. Hidden-state tests explicitly override `Document.hidden`; they do not prove a real background tab. Performance is not measured during concurrent reviewer/root tests. Visual review owns visible outlines and panel geometry. Whole-campaign human pacing/fun and wider controller usability remain unproven. Existing source-generation balance/replay findings remain in the preserved v0.5 reviews; there is no new balance/ML/fun conclusion from this input change.

## Harness corrections and reproduction

All failed probe files and revisions are retained. Original refusal assertions incorrectly counted initial-load time, then assumed one API read per500ms while the implementation performs two slow checks per polling cycle. The final independent bound tests a bounded measured interval against per-frame retry, retaining actual four-read evidence. The native-control probe originally sought New directly in the scene topbar; the corrected probe reaches it through Pause. The fresh-campaign probe originally tried to Tab to an unchecked radio; native radio groups require arrow selection. That original run accepted zero fresh actions; its complete119-action legacy result remains valid. These corrections change browser assumptions, not game rules or policy decisions.

[Prespecification](gameplay-v0.6-input/plan.json) and [reference provenance](gameplay-v0.6-input/frozen-reference-provenance.json) precede the episodes. Exact harnesses, frozen reference modules and lossless fixture files are retained under `gameplay-v0.6-input`. They use `/workspace/scratch/gameplay-v06-input`: to reproduce, copy that retained artifact directory to a **fresh** matching scratch path, delete only newly chosen output filenames there, serve the matching production build, and run the appropriate `.mjs` with its exact64-character digest and a unique run name. Never overwrite preserved evidence. Reference generation intentionally refuses to replace existing files. Browser results include harness/reference hashes. [manifest.json](gameplay-v0.6-input/manifest.json) hashes all initial artifacts except itself; later candidate evidence must use separate files and source hashes.
