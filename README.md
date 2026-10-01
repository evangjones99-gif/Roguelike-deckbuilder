# Hollowpact

A grim monster-binding roguelike deckbuilder. Play a contract hunter, deploy dangerous creatures, and defeat an armored warlord, a necromancer or an ember dragon. Working title; name clearance remains pending.

**Current branch: v0.9.0 development build. Latest sealed checkpoint: v0.8.0.** The current focus is the first five minutes: quick entry, meaningful bindings, clear commands and responsive PC interaction. The working build now has bottom-hand hover/drag/play/cancel feedback, direct creature controls with full names/intents, and arrow navigation aligned with the near/far field. Scoped mouse, keyboard, save/Continue, rules and build evidence is in [continuation](docs/CONTINUATION.md). The confirmed art direction is original gritty pixel art; replacement creature sprites remain experimental, so the current game still uses illustrated 2.5D art. Handcrafted polish and human enjoyment are targets under review. Native consumer installs and Steam qualification remain open. Earlier checkpoint identities and archives are retained in [release history](releases/0.8.0/manifest.json).

## Run

Use Node 22 or later. In the repository terminal:

```sh
git switch codex/lanternbound-production
git pull --ff-only
npm ci
npm run dev -- --host 0.0.0.0
```

In a GitHub Codespace, open **Ports → 5173 → Open in Browser** (use the port printed by Vite if 5173 is occupied). On a local computer, open the address printed in the terminal. Keep the terminal running while playing. Choose **Take a contract → Accept the warrant**, leaving **Initiate** selected for the opening. Click or drag a BINDING card from the bottom hand into the field, then select its ready creature and an enemy for a free command. **Esc** cancels an active selection or opens Pause when none is active. **B/H/T** focus bindings/hand/hostiles; in the direct field, Left/Right move along creatures and Up/Down move between sides and the hand. Your campaign saves in that browser; use the same browser/address to resume. **Field report** optionally saves your notes as a local JSON file; nothing is sent automatically.

`npm test` checks rules and presentation contracts; `npm run build` checks TypeScript and creates an offline web build. `npm run simulate` compares reproducible policies. `npm run test:browser` tests the built production assets with system Chromium; adjust `playwright.config.ts` to your installed browser on other machines.

`npm run desktop` launches current built assets. Package into a fresh independent output directory with the installed Electron builder, for example `npx electron-builder --linux dir --config.directories.output=/tmp/hollowpact-my-new-package`; build current assets first. Retained comparison directories and their aliases are immutable by usage contract. The Windows validation-only ASAR proxy must never be launched or repacked as a complete package. Linux needs the usual Chromium GUI libraries. Actual v0.8 Windows Server2022 portable QA and original binary inspection are [recorded separately](reviews/native-windows-v0.8-23477-binary-independent/REVIEW.md). Consumer installs, physical controllers, Steam Deck, listening and Steam installation still need their own evidence.

## Combat

Five energy and five fresh cards each turn. Play a creature, select its ready binding, then select an enemy to command it. Arrival-turn commands are allowed. Six slots per side, visible enemy intentions, no range rules. Living bindings stay outside deck cycling; fallen ones enter discard. Hunter health carries between fights; bindings reset.

Hover or focus a legal target to read the outcome before committing. Targeted previews name the creature and explain applied spell resistance; cancelling preserves your cards and energy. After an animated creature command, its issued source, target and result stay readable until you deliberately preview another action.

Cairn Hounds punish exposed enemies. Fen Stalkers recover through damaging commands. Briar Colossi protect the hunter. Ash Widows strengthen targeted damage tools. Build around these roles, inspect the final quarry's traits, and select upgrades deliberately. Armored retaliation, delayed reinforcements and dragon breath require different answers.

Rewards can be skipped. Rest or choose a specific deck entry to train, buy or remove cards, and judge shrine bargains before accepting them. Saves and settings stay on the device; no telemetry is sent. The optional Field report downloads feedback locally. New campaigns use schema3/engineKind2; existing schema2 campaigns continue their original kind1 rules. Both use the historical run storage key. Known repeated-Silence damage is repaired only after the original text is backed up.

## Production and evidence

See [production plan](docs/PRODUCTION.md), [AAA review standard](docs/AAA-CRAFT-REVIEW.md), [current rules/save contract](docs/ENGINE-v0.5.md), [project chat context](docs/CHAT-CONTEXT.md), [independent reviews](reviews), and [continuation priorities](docs/CONTINUATION.md).

Art is original AI-generated illustration with [provenance](public/art/PROVENANCE.json). The arena uses animated 2.5D cutouts, not rigged 3D characters. Historical v0.1 remains preserved under its original Lanternbound title.

## Preserved releases

Commit source and evidence, set a fresh version, build matching desktop artifacts, then `npm run release -- VERSION`. Existing release directories cause an error. Each milestone preserves source, offline web/desktop candidates, SHA-256 hashes, source commit and reviews. Failed reviews block promotion to a stable/commercial build. The owner now permits selective retirement of older artifacts when a thorough independent review prefers a verified successor and the producer judges removal wise. Record coverage and any loss of container encodings; keep unique inputs, datasets, historical findings/manifests and useful rollback baselines. Retained versions are never silently overwritten.

Project-authored source remains unlicensed pending the owner's distribution choice. [Attribution](THIRD-PARTY.md) records runtime dependencies and asset limitations. Steam publication requires a verified Steamworks account/AppID, depot and install tests, rights/disclosure review, and platform verification. No Steam upload or public launch has occurred.
