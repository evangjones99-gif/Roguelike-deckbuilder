# Composition/blur repair promotion — v0.6

Root authorized promotion after the initial d33 technical/gameplay/visual reviews froze. This implementation checkpoint records the exact reviewed repair, not acceptance of the next built host.

`src/input.ts` now matches the12-file frozen repair candidate byte-for-byte: b69d87d1a5a71a15d3b29cdfcdbb3f0b33e739f3aa5d8ba82d9cfb470bbdb415. `tests/input.test.ts` matches that candidate with its production source import:144b3ae24aca4a2edec1562c28f6c32ab8efb3aaaee78d7e410d59d071361c22. The original13 test bodies remain unchanged; four lifecycle regressions are added. All17 tests and whole-project strict TypeScript pass. `input-v0.6-focus-promotion/checks.json` retains the actual tool outputs.

Composition keys now return before game shortcuts. Visible-window blur resets/suspends controller polling and cancels scheduled work. Focus re-arms only after neutral release. Initial focus is read once with a guarded fallback; later focus events govern it. Keyboard/native editing remains available.

The earlier12-file focus-repair manifest was reverified unchanged, as were its original failure disclosures. Initial independent d33 failures remain intact. This agent wrote only input.ts, input.test.ts and new report/evidence; root owns main/style/hints, package and production browser tests. No build was run by this promotion. New-digest independent review and actual native focus/controller behavior remain pending. Synthetic events/headless measurements do not establish physical controller, Windows or Steam Deck acceptance.
