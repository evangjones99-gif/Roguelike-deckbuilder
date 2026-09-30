# v0.4 UI implementation verification

This is developer verification using synthetic fixtures, not independent review or human enjoyment evidence. Old release/review artifacts remain preserved.

Target consequence previews use `applyActionWithEvents` on the current state and only display current resolved effects. A selected command or targeted card previews a legal target on focus or hover. Legal immediate cards preview before click, including Blood Price hunter death. Preview never saves, changes selection, plays sound, schedules combat presentation, or reveals future drawn cards/rewards/generated enemy intents. Committed actions still save canonical state before optional presentation. Cached preview text resets when the battle view changes.

Displayed consequences include actual HP loss, block absorbed/removed, capped healing (including zero healing at full health), ward, readying, current Silence cancellation, source retaliation/death, energy gained, contract clear and hunter-death priority. Binding/hostile slots retain exact identity. Danger uses readable text plus a restrained red tint. A polite status region announces the consequence; Escape still cancels. Focused legal targets remain authoritative when the pointer passes over non-target controls.

The save loader first performs ordinary strict validation. Only the engine's exact known repeated guard/Silence overflow recovery helper may produce a recovered campaign, which is validated again. The original raw text is saved under `hollowpact.run.v2.backup.silence` before the primary save is replaced. An existing different backup is preserved and the new backup receives a timestamp suffix. Backup write failure prevents later canonical writes from overwriting the original; recovered play remains available in memory with a neutral, explicit notice. Other corruption remains rejected.

## Actual checks

- `npx tsc --noEmit`: passed.
- Nine new Playwright browser cases passed against Vite development source at `http://localhost:5173`, using system Chromium with software-compatible Canvas2D, 1280×720 by default. Production bundle review belongs to the parent and independent reviewers.
- Actual spell preview incorporates living widow, Wraithglass, revenant resistance and armor: four HP lost, three damage blocked. Committing after preview produces the exact expected canonical state, including RNG.
- A final armored Warlord command previews both enemy death and actual lethal retaliation against the binding, then reaches salvage correctly.
- Hover/focus Blood Price warns of immediate hunter death while leaving save unchanged; click produces defeat.
- Blood Sutures preview reports the capped two HP restoration and two block in the damaged fixture.
- All twelve roster panels remain within roster bounds at 1024×720 with essential intents at 12px during the longer lethal-retaliation preview.
- Known inherited raw campaign is backed up exactly and recovered validly. Unrelated corruption is rejected without primary overwrite. Existing different backup is retained. A simulated backup quota failure preserves the original primary save even after recovered play advances.
- Additional screenshots at 1024×720, 1280×720, and 390×844 show no document horizontal overflow or browser errors. Preview text remains 12px, occupies 16px desktop/48px narrow within the 37px/63px guidance area. Screenshots and measured layout are in `reviews/screenshots-v0.4/`.

## Frozen owned source

- `src/main.ts`: `7b9162ee1005c3a016daa814d99d35b48ed7fa2eb0938f495337c5348c2458da`
- `src/style.css`: `527ca163bd46ca9edd11d8c1a543f170a59e389671fa83e83c34c0c0f2836a12`
- `index.html`: `897357d797f5bd82b62dd5fcc37f3be04700f5091cd5f8c430daecc5102bdfc8`
- `tests/browser/preview-v0.4.spec.ts`: `950a4e95c2df45da57a80aad4cd8e2e75e5bb1231582b1e712299716c9621bab`

No Steam, AAA, broad hardware, human fun, localization, or commercial readiness promotion is claimed. Root continues production and coordinates independent reviews.
