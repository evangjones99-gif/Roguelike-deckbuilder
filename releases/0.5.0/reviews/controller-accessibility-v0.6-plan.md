# v0.6 controller and keyboard accessibility assessment

This is a next-stage implementation plan and synthetic browser assessment. No runtime file was edited. It does not establish physical controller, Steam Input, Steam Deck, screen-reader product, native Windows controller, or human enjoyment acceptance.

## Inspected build and evidence

Read AGENTS.md, docs/CONTINUATION.md, docs/AAA-CRAFT-REVIEW.md, current engine evidence, src/main.ts/style.css/index.html and desktop/main.cjs. Desktop is an ordinary sandboxed Electron renderer (no privileged preload or Node integration); controller input should stay in that renderer using the standard Gamepad API. No new Electron permission, IPC, network or engine rule is required.

Initial production probes used v0.5.0 digest `9f80af0d0053b992c7f0f39d6de106a8f318619ea92e94c00354933e07ebcf04`. The parent then authorized collection width bounds/credits/notice repair and rebuilt digest `cdf4098ab5426281d75a22d4565b6d5b92667a42b9937e756a919a97227449af`. Both sets remain attributed separately. The keyboard probe was repeated at final cdf with unchanged findings; source main/style/index/desktop hashes matched the build provenance, and before/after probe hashes were unchanged. Browser: system Chromium via Playwright, 1280×720, localhost4173. Muted settings kept synthesized audio outside these checks.

Reproducible files under `reviews/controller-v0.6/`:

- `keyboard-probe.mjs`, `keyboard-evidence.json` (initial9f80), `keyboard-evidence-cdf.json` (finalcdf).
- `additional-keyboard-probe.mjs`, `additional-keyboard-evidence.json` (finalcdf).
- `controller-prototype.js`, `virtual-pad-probe.mjs`, `virtual-pad-evidence.json` (review-only injection at finalcdf).

The actual injected Gamepad API object is a synthetic standard-mapped data object, not a Chromium physical device. Prototype polling is advanced by deterministic manual ticks that read `navigator.getGamepads()`. The proposed production RAF lifecycle has not been installed or measured. Hidden/settling tests are explicit browser-property/class simulations, not native tab suspension or an actual terminal presentation hold.

## Actual findings

| Priority | Reproduction and observation | Proposed repair |
| --- | --- | --- |
| P2 | With focus on a binding, first Enter selects it and focuses the first enemy. Repeated `keyboard.down('Enter')` generates a repeat event that commits the command without releasing the key. Enemy HP goes16→11. | Prevent repeated Enter/Space default activation on game buttons. Preserve first activation, key-up behavior, native text entry and modified shortcuts. Gamepad confirm must require a new press edge. |
| P2 | Kill one enemy while others remain: render removes the focused UID, and activeElement becomes BODY. | Restore a connected semantic focus key; if the target vanished, choose a remaining ready binding, then hand/end-turn fallback. Never focus a detached element or issue an action during recovery. |
| P2 | Reduced-motion final command reaches salvage with BODY focus. Animated final command correctly focuses the salvage H1. | Use the same phase-heading focus helper after instantaneous and animated outcomes. Motion preference must not change keyboard orientation. |
| P2 | Deck→card inspection replaces an already-open dialog's content. The focused card disappears and activeElement becomes BODY while dialog remains open. | Explicitly focus the new dialog heading/first relevant control after modal replacement; preserve the original external opener for final close. |
| P2 | Ctrl+E on a binding opens 'Unspent commands remain'. The shortcut has no ctrl/meta/alt guard. | Only accept unmodified game shortcuts; keep browser/OS shortcuts intact. |
| P2 | After keyboard Resume, a full6+6 battle needs28 successive Tabs to reach the first hand card: combat record,12 unit buttons plus12 inspect buttons, then piles. | Add one-step regional focus shortcuts and controller bumpers; use spatial/group navigation without removing native Tab reachability. |
| P3 | ArrowRight on a binding does not move button focus; selection cancellation leaves focus on the enemy rather than the initiating binding/card. | Add scoped button navigation and restore selection origin on cancel. Leave arrows on input/select/textarea/range/radio widgets to native behavior. |
| Missing feature | Injected standard gamepad A press causes no focus or saved-state change in unmodified runtime. No gamepad handler exists. | Add a reversible standard-mapped renderer adapter after v0.5 archive. |

Native dialog behavior is partly sound: Settings opens on its close control; underlying Home cannot receive programmatic focus, and Escape restores Settings. Chromium's native Tab loop briefly yields BODY/browser chrome at the loop boundary, then returns to dialog controls; this did not make an underlying game control active. Controller navigation must nevertheless explicitly remain inside the open dialog. Essential unit and health names are present in accessible button labels; selection immediately focuses a legal target and its actual-event preview. Existing E repeat protection and canonical dispatch/presentation gates should be reused.

Dense inspect buttons are14×14px by current CSS. Controller X can improve access to them, but does not repair touch target size. Enlarging their hit area must be a separately measured layout change that preserves all12 visible names/stats/intents. This assessment has not certified WCAG conformance or screen-reader speech quality.

## Proposed implementation ownership and architecture

Implement a small `src/input-controller.ts` renderer module, then wire it from main.ts. Keep engine, saved GameState, RNG/world schedule and arena presentation unchanged. The module receives readonly interaction context and semantic callbacks; it does not apply actions, manipulate saved state, predict random draws, or infer future intents. Use ordinary DOM focus and the existing click/action routes. Main's reducer legality and settling lock remain the final gate even if the adapter fails.

Separate three pieces so they can be reviewed and reverted independently:

1. Pure input decoder: feature-detect Gamepad API, recognize standard mapping, bound finite axes/buttons, derive press edges and navigation intent. Hold confirm/back/end-turn/inspect/start/bumper buttons at one action per press. Connection, visibility resume and disconnect require a neutral release before arming. Use analog enter deadzone0.55/exit0.30 and dominant-axis direction; only direction movement repeats (350ms initial delay,100ms thereafter). Digital button values can use0.60 press/0.40 release hysteresis. Never auto-attack or replay a queued button after a phase/lock transition.
2. DOM navigation: native modal scope first; otherwise selected legal-target scope; otherwise semantic battle regions (hand, bindings, hostiles, turn controls, tools), or the current route/reward/camp/shop/event menu. Retain stable focus keys/UIDs and scroll focused cards into view. Spatial candidates use element rectangles and forward/perpendicular distance; no invisible or disabled native controls. Keep unavailable hand cards navigable for their explanation, but activation must follow the existing refusal/legality route. Never treat hidden canvas geometry as actionable targets.
3. Main integration/focus repair: share cancel/back, inspect, pause, end-turn and focus restoration with keyboard. A small centralized focus helper handles vanished UID, new phase, modal replacement and selection origin. Remove the actual repeat/modifier gaps above before adding new shortcuts.

Recommended standard mapping:

| Input | Intent |
| --- | --- |
| D-pad / left stick | Move focus; horizontal through hand/grid choices, vertical through unit rails; spatial navigation in menus/dialogs |
| LB/RB | Previous/next battle region; within targeting stay in legal-target scope; within a dialog stay in its own controls |
| A | Activate the focused eligible control once; selection and target commitment need separate presses |
| B | Close dialog, otherwise cancel selection and restore its origin, otherwise pause/back |
| X | Inspect focused creature/card using a shared semantic inspect callback; never play a hand card to inspect it |
| Y | Existing End-turn button route, including unspent-command confirmation; unavailable outside a battle/modal-free context |
| Start | Existing pause route; can expose safe return-to-title during a presentation hold, with the existing cancellation token |

For keyboard, keep Tab/Shift+Tab and existing E/Escape. Add unmodified H (hand), B (bindings), T (targets/hostiles), I (inspect focused item), plus spatial arrows only on relevant game buttons. These reduce the28-Tab route without replacing expert keyboard behavior. Ignore ctrl/meta/alt shortcuts and editable/native widgets. Radio/select/checkbox/range controls must retain native keyboard semantics. The controller can adjust a focused volume slider in modest explicit increments through the existing input event; it must never synthesize typing or submit a text field merely because A was pressed.

Text entry is a declared limit for the first pass: a controller can begin a campaign using the provided seed and choose difficulty, but custom seed/feedback text requires keyboard or an independently verified platform text-entry service. No Steam overlay/onscreen keyboard integration is currently available. Do not advertise universal controller-only text editing.

## Lifecycle, presentation and privacy

Poll on a lightweight independent RAF while visible and a standard device is active; do not depend on arena RAF, since reduced motion stops arena animation. Stop/reset on hidden, disconnect and dispose; remove listeners/timers on unload. Main exposes the actual settling flag, not a CSS-only assumption. Scene/dock activation remains blocked throughout final presentation; movement/activation may operate only in an intentionally opened safe modal. Clear stale origin/region references on new campaign/title/reset. Any focus-only failure must leave saves and playable keyboard/mouse controls intact.

Keep input local and transient. Read axes/buttons/index/mapping needed for interaction, without recording/exporting device IDs, hardware names, raw input streams, timestamps or controller profiles. No automatic storage, telemetry, network or feedback additions. Optional control preferences need explicit schema-valid settings only. Hints should be concise visible text ('A choose · B back · Y end turn'), switch after meaningful input, and retain accessible names/focus outlines at12px essential text. Do not shrink the six intent panels to make space. Gamepad-triggered WebAudio activation needs actual browser/native verification: injected DOM clicks are not proof of trusted hardware activation, and this muted prototype does not claim audio unlock.

## Review-only prototype results and limits

The injected prototype demonstrates local DOM feasibility:0.25 analog jitter did not move focus;0.8 direction moved a10→a11, held direction repeated to a12 only after the delay; navigation did not change save. Holding A after selection did not commit. Releasing/pressing A committed the focused command. B restored its source without changing save. Y opened the actual unspent-command dialog, and prototype directions stayed in that modal; B closed it without ending turn. Simulated hidden resume required release, simulated settling class blocked activation, and dispose rejected further input. No page errors occurred.

The prototype is deliberately unshipped. Its manual ticks, CSS lock simulation, synthetic Escape pause path and direct dialog close are demonstration hooks. Production must receive main's real context/callbacks, own its RAF lifecycle and preserve modal opener semantics. Card inspection and custom text entry are not implemented by the prototype. There is no full-run controller, hardware, audio, performance or Steam Deck acceptance yet.

## Acceptance before preserving a v0.6 input milestone

- Independent actual production-browser comparisons for keyboard repeat, modifiers, nonfinal removed target, modal replacement and both motion modes; verify focus remains useful and engine/save byte equality for the same intended actions.
- Injected standard API controller-only ordinary menu/campaign flow: tutorial, routes, bindings, targeted/immediate tools, target changes/cancel/inspection, end-turn confirmation, rewards/skip, selected training, shop/removal, events and terminal recap. Verify full canonical state against existing reducer expectations, with no hidden draw/world disclosures.
- Held A/Y across selection, terminal hold, dialog replacement and new phase cannot issue a second action. Connection-held buttons, disconnect/reconnect, actual background/visibility transitions, API-unavailable/throws, unknown mapping and disposal leave keyboard/mouse usable.
- Native input/radio/range/select/text editing and modified shortcuts remain intact. Inspect/cancel returns to the right source. All12 dense roster panels and essential12px text stay visible at1024/1280×720; modal grids remain readable at1920×1080 and narrow web layout.
- Record input loop cadence/CPU alongside a graphics soak; preserve prior release/results. Separate actual native Windows/XInput/Steam Input/physical controller and prospective-player evidence before making platform/controller quality claims.

## Reproduction on the matching preserved build

Run from repository root with Node and the already-installed Playwright/system Chromium. Each probe refuses an unexpected digest and uses exclusive evidence creation (`wx`); choose a new filename rather than overwrite prior evidence. Change HOLLOWPACT_REVIEW_URL only to a server of that exact build. Example final-cdf reruns:

```sh
HOLLOWPACT_EXPECTED_DIGEST=cdf4098ab5426281d75a22d4565b6d5b92667a42b9937e756a919a97227449af HOLLOWPACT_EVIDENCE_NAME=keyboard-reproduction-new.json node reviews/controller-v0.6/keyboard-probe.mjs
HOLLOWPACT_EVIDENCE_NAME=additional-reproduction-new.json node reviews/controller-v0.6/additional-keyboard-probe.mjs
HOLLOWPACT_EVIDENCE_NAME=pad-reproduction-new.json node reviews/controller-v0.6/virtual-pad-probe.mjs
```

No probe edits runtime files, imports the review controller into the shipping app, or sends feedback. Browser contexts contain synthetic saves/settings only.
