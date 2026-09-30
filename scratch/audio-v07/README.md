# Original combat audio research · v0.7 scratch

**Author research only. No sound was promoted to `src/` or `public/`. No listening was performed.** This lab preserves thirty original stereo WAV prototypes, deterministic synthesis source, current-source input hashes, actual signal measurements and browser evidence. There are no third-party recordings, paid services, telemetry or claimed use of unavailable Windows research/demo files.

## Finding in the current game

The inspected `sound()` in `src/main.ts` creates five generic Web Audio categories: click, summon, attack, reward and turn end. Attacks share the same low tone/noise/metal edge; all spells also take the attack branch. Enemy resolution mostly takes the generic turn-end branch, so different actual enemy attacks and hunter wounds lack their own material identity. Synthesized grit uses unseeded `Math.random()`. Settings are honored before source creation and audio is optional, but existing tails are not immediately tracked/stopped when mute or zero volume is changed. `current-sound-source.txt` and `INPUTS.json` preserve the actual inspected implementation and hashes. This is a source finding, not a listening judgment.

## Concrete sound direction

| Cue | Intended original material and role | Prototype boundary |
| --- | --- | --- |
| Bind seal | Short chain tension, irregular iron resonances, pressure sealing shut | Avoid melodic confirmation bells; authored organic chain texture still needs listening |
| Summon arrival | Air displaced into a low body impact, followed by binding hardware | A layered arrival, not a generic UI click; align impact to presentation before integration |
| Hound bite | Brief breath/rough throat pressure, tooth/contact transient and dry crushing body | Procedural noise is not an anatomically convincing animal recording |
| Warlord iron impact | Hard edge, inharmonic iron decay, heavy cloth/armor body | Modal resonances can read as synthetic chimes; reject that if heard |
| Wraith magic | Cold air drawn inward, narrow pressure bands, unstable low beating | No cheerful arpeggio or heroic spell flourish |
| Dragon breath | Sustained turbulent broadband pressure with low body and hot crackle | Prototype flame texture, not a convincing voiced dragon roar |
| Hunter wound | Armor/cloth body contact and a short disrupted breath | Route only actual hunter HP loss, never a fully blocked attack |
| Camp settle | Quiet kit/cloth handling and a restrained ember texture | Short accepted-action cue, not an authored environment ambience or music score |
| UI confirm / back | Small dry leather/iron signals with distinct pitch/timing | Lower level than combat; do not imply an attack when navigating |

Three seeded variations exist for every cue. `render.mjs` creates the entire sound from original noise, envelopes, low/high filtering, irregular modal resonances and short stereo early reflections. Sample peaks are normalized by role; no borrowed recording or external audio model input is involved. This is a technical prototype, and synthesized material may remain below the intended studio craft bar.

## Event routing and mix proposal

`routing.mjs` consumes ordered resolved events and previous/next unit identities without applying or predicting rules. It identifies hound, warlord, wraith/necromancer and dragon attack materials, routes summon/control/ward observations, and emits hunter-wound cues only when `hpLost > 0`. A seven-target source produces one breath body rather than seven stacked breaths. Source/kind/card grouping is provisional: repeated attack clusters within one transition may need finer presentation identity. The fallback for unknown attackers is currently an iron impact, which may be wrong for a particular spell/creature and needs authored coverage before production use. Synthetic routing fixtures are labeled in the UI and evidence.

The controller creates an AudioContext only after a user gesture, caches local decoded buffers, honors persisted lab-only mute/volume settings and stops tails within a short fade. It caps concurrent source voices at eight, has no idle loop, and groups a loaded event batch against one shared audio-clock start. Prototype bus compression prevents large dynamic jumps but is **not** a measured brick-wall limiter; loud combined events, perceived balance and headphone fatigue remain unverified. The output is original stereo PCM16 at 48 kHz. All source buffers end naturally or are disposed, and audio failure remains separate from canonical game state.

Production integration would observe the existing actual-event stream only after canonical rules/save completion. Align actual contact timing with arena event packets rather than delaying rules to wait for audio. Prioritize hunter damage and a distinct source body, prevent multitarget duplication, and choose texture by actual attacker/effect rather than broad action type. Preserve the production settings keys and migration behavior; this lab deliberately uses its own `hollowpact.audio-lab.v07` preference key. Do not promote the scratch routing fallback, mix or files without independent listening and timing review plus packaged offline activation/settings checks.

## Actual checks and their limits

`signal-measurements.json` records all thirty actual generated WAV hashes, durations, sample peaks, RMS, DC means and zero clipped PCM samples. `ffmpeg-loudness.json` contains actual EBU R128 / true-peak analysis for every WAV. The measured maximum true peak is **−8.4 dBFS**, even though nominal sample peaks top out at −10 dBFS; interpolation matters. Very short UI clips fall below the integrated loudness gating window. RMS and LUFS do not establish pleasing timbre or a correct in-game mix.

`browser-evidence.json` records actual isolated headless Chromium checks: no autoplay/context before activation, a running context after a gesture, all thirty WAVs decoding, mute/zero-volume rejection and stopped tails, lab settings surviving reload, one dragon body for a seven-target fixture, no wound on a full block, an eight-voice concurrency cap, disposal and zero remote requests/page errors. `browser-fixture.png` preserves the actual control fixture. The first test harness exposed a missing-file HTTP-header error; the server now reads bytes before writing success headers. No production code was involved.

The first `check-routing.mjs` attempt failed because seed 117's current schema-3 initial battle hand did not contain the requested legal Cairn Hound summon. `routing-first-attempt.mjs` and `routing-first-attempt-failure.json` preserve that test/source failure; it produced no actual-event evidence. The corrected fixture uses documented seed 1 for actual schema-3 hound summon/command observations. It also recomputes four preserved legacy schema-2 dragon fixtures through the current dual-generation reducer, checks their canonical state/event equality, and verifies observer input/RNG preservation, one body for seven targets, two for two separate dragon sources, and no hunter-wound cue when fully blocked. `source-fixtures.json` preserves those inputs and `actual-event-evidence.json` records actual results. This is reducer/observer evidence, not integrated or heard game audio. Native packaged decode, actual presentation synchronization, alternate sample rates/devices, stereo positioning, speaker/headphone listening, organic creature identity, overlap loudness and player preferences remain open.

## Reproduce without runtime changes

From the repository root:

```sh
node scratch/audio-v07/render.mjs
node scratch/audio-v07/check-browser.mjs
node --import tsx scratch/audio-v07/check-routing.mjs
```

To audition manually, serve this scratch directory locally and open `index.html`, then activate audio intentionally. Every media request is local; there is no external service. Preserve this checkpoint before future source/parameter changes and record whether a reviewer actually heard the cues. A graph that decodes and has headroom can still sound poor.
