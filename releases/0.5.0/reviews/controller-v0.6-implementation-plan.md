# Controller and keyboard implementation candidate — v0.6

30 September 2026. Author: UI/input implementation agent. This is an unshipped implementation assessment, not an independent acceptance report. Parent root owns main integration; independent technical/gameplay/visual reviewers must assess the new built runtime. The frozen v0.5 runtime was not edited.

## Candidate and provenance

Production-shaped TypeScript is isolated at `/workspace/scratch/controller-v06-production-input/adapter.ts`. No `src/input.ts` exists from this work. Candidate SHA256 `4ae4ca1a2dadb41f3a51b8eba35dd41efed5ececb00d912edfbec2e346f9f69d`; emitted JS `61547911bf036f9020eb6ea188496251e2e4f1f8e5b1f81961b6b149d157f52b`. Promotion must wait for root's v0.5 archive and explicit runtime ownership GO.

Actual browser probes ran Chromium `/usr/bin/chromium` against final v0.5 digest `d6221bf764bad593b04981e87bead7ba6868b72cf361d70671af5c91aac39416`. The scratch adapter was injected into those isolated pages. Closured main callbacks could not be called directly; the probe borrows actual DOM clicks plus explicit synthetic host context. These tests prove adapter routing and real current controls, not shipped main integration. Legacy and engineKind2 fixtures are isolated automated records, not human feedback.

Earlier observed runtime gaps remain documented separately in `reviews/controller-accessibility-v0.6-plan.md`. Preserve that report and its 9f80/CDF evidence. This candidate addresses the adapter half; focus removal, modal replacement, Enter repeat/modifier suppression and outcome focus are main-owned repairs.

## Integration contract

`createInputAdapter(host, options?)` returns `{ pollOnce(now), dispose() }`. Production uses the default Gamepad API reader and automatic RAF polling; injected readers and manual polling exist for deterministic tests.

Host callbacks:

- `getContext(): { phase, settling, dialog, targeting }`: return actual main state and presentation boolean. `dialog` is the current open native dialog or null. Do not infer locks from CSS, disable rules, storage or preview text. `phase` allows title plus engine phases.
- `activate(element)`: route through real main activation/click handling with canonical legality and presentation checks. Aria-disabled cards remain focusable for inspection; activation must still be rejected by main.
- `back()`: use main selection cancel/modal close/pause logic, retaining the correct source/origin focus. The adapter never directly closes a dialog.
- `inspect(element)`: inspect a live unit UID or displayed card definition without playing it. Root should resolve the identifier through current state/content, rather than trust mutable DOM text.
- `endTurn()`: use the normal main unspent-command confirmation and action legality route.
- `pause()`: use the safe main pause path even during a final-hit presentation, cancelling/snap-settling through the existing epoch logic when required. It must not queue stale combat actions.
- optional `onInputMode('keyboard' | 'controller' | 'pointer')`: presentation hints only; no storage or analytics. Trusted keyboard and pointer events update mode; controller intent updates it once that intent is accepted by the adapter.

Construct once after delegated main handlers exist. Dispose once before page teardown/HMR replacement, not on every render. Main remains sole authority over canonical state, RNG, saves and presentation epochs. No adapter callback may use a second engine path or modify a save directly.

## Interaction model

Standard-mapped controller: A choose, B back, X inspect, Y end turn, LB/RB previous/next region, Start safe pause, D-pad/left stick focus movement. No device-specific name or vendor mapping is guessed.

Regions use current visible DOM: hand, bindings, hostiles, turn controls and tools. Target selection narrows navigation to legal target elements. Open dialogs narrow navigation to their native controls. Unplayable hand cards remain reachable for X/I inspection. Left/right cycles the hand; up/down cycles each roster; right from bindings moves to hostiles, left reverses, and up from hand enters bindings. Other menus/dialogs use element rectangles and directional distance. Region focus is remembered by public stable DOM identifier, not random display name.

Keyboard H enters hand, B bindings, T hostiles/current targets, I inspects the focused card/unit. Arrow navigation applies only to relevant game buttons. Ctrl/Meta/Alt chords and input/select/textarea/contenteditable editing retain native behavior. E, Escape, Tab, Enter and Space remain main/native-owned: root must guard held activation repeats and preserve origin/phase/modal focus. Controller sliders dispatch the existing input event in bounded steps; selects use existing change events. Text entry remains keyboard/OS-owned.

Buttons use fresh press edges with 0.6/0.4 analog hysteresis. Confirm/back/inspect/end-turn/pause/regions never auto-repeat. Movement uses 350ms initial delay then100ms repeat. Left stick enters at0.55 and exits below0.30. Connection, API failure, hidden, disconnection, index change and presentation gates reset arming. Gameplay resumes only after all controls return neutral. A fresh Start can request safe pause while gameplay is gated; it cannot activate an opening modal through a held input.

## Local input and lifecycle

The adapter reads standard Gamepad button/axis state only while the page is visible. It never reads `Gamepad.id`, saves raw samples, writes localStorage, accesses the engine, or sends network requests. No persistent input-mode/device record exists. Lack of API, denied API, malformed input or optional callback exceptions leave keyboard/native controls available. Missing/failed API uses a500ms retry rather than a continuous error loop. RAF is independent of arena animation so reduced motion keeps controller input responsive. Hidden/dispose cancels scheduled callbacks; visibility/device events reset held inputs and require neutral release.

## Actual checks

Strict TypeScript compilation passed using the project's installed TS7 with `--ignoreConfig`, ES2022/DOM libraries. All13 meaningful decoder tests passed. Latest eight browser scenarios passed with no page errors and identical runtime source hashes before/after:

1. Region/spatial keyboard navigation and modifier preservation without save changes.
2. Legacy two-edge command: held A selects only once; a fresh A commits exactly the expected reducer state.
3. EngineKind2 immediate summon: exactly expected reducer state; held A does not play another card.
4. Actual inspect dialog, navigation confined to that dialog, host-owned back, unchanged save.
5. Actual unspent-command confirmation, held Y cannot confirm it.
6. Native keyboard slider step, controller slider's existing input handler, seed typing unaffected.
7. Explicit host boolean presentation gate blocks confirm while Start invokes safe pause; this gate is simulated, not a claim that main integration passed.
8. API SecurityError preserves keyboard; dispose disables adapter input.

Latest browser evidence: `/workspace/scratch/controller-v06-production-input/browser-evidence-1790806317616.json`. Probe source SHA `527b7d1f00e859ebdaa27085fdc129bccb0bcfcfca22732ca2a79f65908862da`; decoder tests SHA `f9b26aa7a8c7d62cb921118507025ed1e52269df984f427412562428bcd64adb`.

Lifecycle evidence `/workspace/scratch/controller-v06-production-input/lifecycle-evidence-1790806286751.json` proves actual foreground RAF polling with motion off, schedule disposal, slow retry on API refusal, and native typing into an empty `contenteditable` HTML attribute. Hide/resume logic uses explicit `Document.hidden` emulation: headless Chromium reported both tabs visible after bringToFront. The first attempt failed by wrongly expecting a visible foreground A press to remain inert; the second failed by assigning an invalid empty contentEditable IDL property. Both harness repairs are disclosed in the passing evidence. No physical controller, native background tab or Steam Deck result follows from this emulation.

## Required shipped-host acceptance

After root archives v0.5, promote the module without changing rules or saves. Build a new digest and run independent production checks, not the scratch shim:

- Fresh/held Enter and A through ally selection, changed target focus and immediate summon; no double activation across render or phase replacement.
- Removed target/source, Escape cancel, nested collection/dossier replacement, terminal motion on/off and pause/resume focus recovery.
- Actual final-kill lock: canonical save advances immediately, controller/keyboard cannot mutate stale combat, Start follows the real safe pause route, no stuck outcome.
- H/B/T/I, spatial and region navigation through hand, legal targets, menus, dialogs, unavailable-card inspection, text inputs and sliders. Ctrl/Meta/Alt plus E must not end a turn.
- Default Gamepad API absence/refusal/disconnect, held connection and hide/resume. Native hardware mapping, trusted controller audio activation, Windows and physical Steam Deck require their own declared-platform tests.
- All12 panels and intents remain visible/readable at1024/1280×720; focus outlines and previews stay visible; no unnecessary automatic scrolling.

Controller-only seed/free-text entry needs an OS keyboard or keyboard device; do not advertise a complete controller-only flow before that is assessed. Current mobile intent wrapping and small inspection targets are inherited documented gaps, not acceptance of accessibility perfection. No human enjoyment or commercial/Steam-ready claim is made.

## Final preparatory freeze

The new production-prototype artifact directory preserves the isolated adapter, tests, fixture/probe tools and raw evidence under `reviews/controller-v0.6-production-prototype/`. Its `manifest.json` hashes every preserved file. Older controller reports are unchanged.

A further nine menu checks passed: map/camp/shop/event/reward region changes restore focus without canonical changes; camp rest, shop purchase, event forage and reward skip exactly match reducer output, with no repeated action while A remains held. `menu-evidence-1790806546691.json` is the latest retained result (consult the artifact directory for exact timestamped name). The first menu harness attempt timed out when it tried to resume a saved victory: title deliberately hides Resume for victory/defeat. That failure is preserved; terminal menus remain unexercised by these scratch probes and must be reached normally in shipped-host tests. This is not a repaired game defect.
