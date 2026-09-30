# Native packaged keyboard validation extension — v0.6

Author harness checkpoint,30 September2026. Ownership: scripts/windows-smoke.mjs and this new report only. No runtime, module, test, package or workflow files changed. Script is frozen for root diff review at SHA256ed7551494d735b5f00d3071fe425e0a390d33322e3488b4b7b9a54cbbd9ac370.

## Existing native baseline

Read the actual Windows0.5.0 run36782560136-1 smoke.json, workflow and fixtures. Its nine successful stages cover packaged provenance/resources, sandboxed launch, portrait, preferences, seed121/tutorial/combat, reload, art/deck, negative local feedback download and relaunch persistence. Those historical files remain unchanged. The current script keeps all nine stage names and assertions; first command activation now uses trusted keyboard controls instead of the previous two mouse clicks.

Native CI is windows-2022/x64 Node24.19.0, packaging the actual Electron executable with resource checks and sandbox enabled. No Windows result was produced in this Linux session. The existing workflow will invoke the revised script on real packaged bytes and retain smoke.json/failure.png and package/runtime hashes. Its win32/x64 preconditions remain unchanged.

## Added checks

After the actual first Cairn Hound binding and before committing its command, the harness stores the current canonical save. H/Right/B/T/B must navigate actual hand/binding/hostile controls without changing it. I opens the binding dossier and Escape restores the binding. Enter from the deck opener, then Enter from Scour, replaces modal content with a focused dossier title; Escape restores the original deck opener. One native Tab inside the deck dialog is checked, without claiming a complete accessibility audit.

Repeated keyboard.down calls for Enter and Space dispatch trusted Chromium autoRepeat events. Neither hold may follow selection focus into a command; key release produces exactly one selection, and Escape restores the source with unchanged save. A separate fresh Enter selection and fresh Enter confirmation must match the complete canonical reducer state. The actual renderer trace must include trusted prevented repeats for both keys. Held keys release in finally even on an assertion failure. The outer failure handler also captures the bounded trace before closing the renderer, retaining a failed guard alongside its stack, phase and screenshot.

The expected reducer is loaded through the already-installed tsx/esm/api, with pathToFileURL(path.resolve('src/engine.ts')).href and import.meta.url. Before import, engine.ts, content.ts and world-rng.ts hashes must each match packaged runtime provenance. This prevents expected results coming from an unrelated checkout. No new dependency was installed or added.

The trace is bounded to64 test-only Enter/Space keydown records, lives only in the isolated automation profile and is removed after the segment. It is recorded in CI smoke.json as automated input evidence; it is not gameplay telemetry or human feedback. No virtual Gamepad API or physical-controller claim is added. CDP trusted events still do not establish a physical keyboard, native IME, controller, Steam Deck, hardware performance, audio listening or full accessibility acceptance.

## Actual local checks and limits

node --check scripts/windows-smoke.mjs passed, as did git diff --check. Existing tsx URL-based engine/dependency resolution was exercised successfully on Linux; Windows resolution is pending the native job. The exact added segment was extracted from the revised script and executed, with every assertion retained, in Chromium1440×900 against production web digest a502ed48dfb625257acea8d747439bce23be2c2ec346013b6c1a4fd9c8cb14f5. The parent explicitly authorized this non-native rehearsal. No packaged executable or ASAR was launched in that rehearsal. All three added stages passed without page errors; no failed rehearsal attempt or weakened assertion occurred. Temporary browser/screenshot files were closed/removed.

Observed result below preserves the real outcome and key trace. Labels containing packaged/native are copied from the harness segment and describe the future CI context; this run's transport was headless Linux Chromium over HTTP, not Windows. The production runtime/source was unchanged.

```json
{
  "kind": "Non-native exact added native-harness segment rehearsal",
  "windows": false,
  "physicalKeyboard": false,
  "sourceDigest": "a502ed48dfb625257acea8d747439bce23be2c2ec346013b6c1a4fd9c8cb14f5",
  "passed": true,
  "steps": [
    "verify packaged regional keyboard and nested modal focus",
    "verify held Enter and Space cannot follow selection into a command",
    "verify deliberate fresh keyboard command matches packaged rules"
  ],
  "errors": [],
  "keyboard": {
    "method": "Playwright CDP trusted renderer-key dispatch into sandboxed packaged executable",
    "physicalKeyboard": false,
    "physicalController": false,
    "beforeSaveSHA256": "503f5f206a1b17ca96e57916067e58e5fdf4f579c9d70b6e0d997d6d3142c41f",
    "held": [
      {"activation":"Enter","selectedTarget":"e1","saveUnchangedUntilFreshActivation":true,"cancelRestoresSource":true},
      {"activation":"Space","selectedTarget":"e1","saveUnchangedUntilFreshActivation":true,"cancelRestoresSource":true}
    ],
    "regional": {"handFocus":"card-0","nextHandFocus":"card-1","binding":"a3","hostileFocus":"e1","saveUnchanged":true},
    "modal": {"unitOriginRestored":true,"nestedDossierTitleFocused":true,"deckOriginRestored":true,"oneNativeTabInsideDialog":true,"saveUnchanged":true},
    "trace": [
      {"key":"Enter","type":"keydown","trusted":true,"repeat":false,"prevented":false},
      {"key":"Enter","type":"keydown","trusted":true,"repeat":false,"prevented":false},
      {"key":"Enter","type":"keydown","trusted":true,"repeat":false,"prevented":false},
      {"key":"Enter","type":"keydown","trusted":true,"repeat":true,"prevented":true},
      {"key":"Enter","type":"keydown","trusted":true,"repeat":true,"prevented":true},
      {"key":" ","type":"keydown","trusted":true,"repeat":false,"prevented":false},
      {"key":" ","type":"keydown","trusted":true,"repeat":true,"prevented":true},
      {"key":" ","type":"keydown","trusted":true,"repeat":true,"prevented":true},
      {"key":"Enter","type":"keydown","trusted":true,"repeat":false,"prevented":false},
      {"key":"Enter","type":"keydown","trusted":true,"repeat":false,"prevented":false}
    ],
    "command": {"type":"attack","unit":"a3","target":"e1","exactCanonicalState":true,"afterSaveSHA256":"27968c3637426cd739de234aa59cfd7644d0b397d46973749c876702e3f6f2f8"}
  }
}
```

Root must review the diff before push/native CI. The first actual Windows run must retain any failure and compare provenance without accepting this rehearsal as platform evidence. All earlier v0.5/v0.6 reviews, frozen prototype/repair records and releases remain unchanged.
