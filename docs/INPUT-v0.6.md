# Development input contract

Version0.6 adds keyboard focus recovery and a local standard-mapped Gamepad adapter to the existing native controls. It does not change either supported rules generation, saved schemas, action legality or combat damage. Browser diagnostics use synthetic standard-pad samples; physical controllers, Steam Input/Deck, actual IMEs and operating-system accessibility require separate tests.

## Keyboard

Tab retains native control/form traversal. Enter and Space activate buttons normally; holding either cannot follow a newly focused target into an accidental command. Escape cancels selection and restores its source, closes the current dossier and restores its external opener, or uses the existing safe pause route. E uses the existing end-turn confirmation flow. Typing and composition inside native editable controls retain their normal behavior; modified shortcuts are not intercepted.

Outside selection, H focuses the hand, B the bindings, T the hostiles, I inspects the focused known card/unit, and arrows navigate the current region. During selection the navigable region is the actual legal targets, including the hunter when appropriate; T focuses that region. Hand navigation wraps horizontally, roster navigation wraps vertically, and spatial direction prefers nearby controls. These controls derive from visible enabled native elements rather than copied gameplay state.

## Standard-mapped Gamepad

| Input | Action |
|---|---|
| A | Activate the focused enabled control |
| B | Back/cancel/close through the same safe host route |
| X | Inspect the focused known card/unit |
| Y | Existing end-turn flow during battle |
| D-pad / left stick | Navigate visible controls |
| LB / RB | Previous/next available region |
| Start | Safe pause route; during an active presentation, settle the already-saved result |

Activation, inspection, back, end turn and region changes are fresh edges, never held repeats. Only directional navigation repeats, after350ms and then every100ms. Button value thresholds use0.6 entry/0.4 release hysteresis; stick direction uses0.55 entry/0.30 release. Connecting, changing index, hiding/blur, returning from an unavailable/settling context or resetting the adapter requires neutral controls before gameplay activation. A held A on refocus cannot commit a move. Nonstandard mappings are ignored.

Gamepad polling suspends while hidden or unfocused and is disposed with the renderer lifecycle. Missing/refused APIs keep keyboard and mouse available with a bounded retry. The adapter keeps no device ID, controller history or gameplay/save reference; hints change presentation only. Saves and optional feedback stay local with no default telemetry.

## Evidence

Initial input candidate d33 and its composition/blur boundary failures remain immutable in reviews. Repaired input-only1788 and combined contact candidatea502 each have their own gameplay/visual/technical identities. Root81 rule and35 actual production-browser checks pass on a502; these include held-input, source/modal focus, synthetic composition/neutral rearming and wide-short twelve-intent containment. Native packaging, consumer installation and real hardware are separate gates. Consult CONTINUATION.md and release manifests for the actual final preserved identity, rather than treating this document as certification.
