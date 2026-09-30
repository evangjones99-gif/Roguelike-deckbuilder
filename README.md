# Hollowpact

A grim monster-binding roguelike deckbuilder. Play a contract hunter, deploy dangerous creatures, and defeat an armored warlord, a necromancer or an ember dragon. Working title; name clearance remains pending.

**v0.4 reviewed development milestone.** Repeated Silence no longer breaks campaign saves; narrow legacy recovery preserves the exact original save before replacement. Target previews show actual damage, armor, recovery and retaliation without revealing future draws. Corrected contact shadows and solid illustrated pose changes improve creature readability. Independent reviews accept development preservation; archive hashes and source identity are recorded under releases/0.4.0 after archival. AAA studio craft and human enjoyment remain unproven; sparse animation still needs work. Known draw-inspector ordering and multi-target dragon-motion defects are recorded for the immediate next repairs.

## Run

Node 22 or later. `npm ci`, then `npm run dev`. Open the printed local address. `npm test` checks the renderer-free rules; `npm run build` checks TypeScript and creates an offline web build. `npm run simulate` compares reproducible policies. `npm run test:browser` tests the built production assets with system Chromium; adjust `playwright.config.ts` to your installed browser on other machines.

`npm run package:linux` or `npm run package:windows` builds an Electron desktop directory. `npm run desktop` launches current built assets. Linux needs the usual Chromium GUI libraries. A native Windows Server 2022 runner has launched the v0.4 package and checked branding, persistence and offline feedback; see [native evidence](docs/NATIVE-WINDOWS.md). This does not establish clean consumer installs, Steam Deck or Steam installation.

## Combat

Five energy and five fresh cards each turn. Play a creature, select its ready binding, then select an enemy to command it. Arrival-turn commands are allowed. Six slots per side, visible enemy intentions, no range rules. Living bindings stay outside deck cycling; fallen ones enter discard. Hunter health carries between fights; bindings reset.

Cairn Hounds punish exposed enemies. Fen Stalkers recover through damaging commands. Briar Colossi protect the hunter. Ash Widows strengthen targeted damage tools. Build around these roles, inspect the final quarry's traits, and select upgrades deliberately. Armored retaliation, delayed reinforcements and dragon breath require different answers.

Rewards can be skipped. Rest or choose a specific deck entry to train, buy or remove cards, and judge shrine bargains before accepting them. Saves and settings stay on the device; no telemetry is sent. The optional Field report downloads feedback locally. v0.4 retains schema-2 storage keys and preserves earlier saves. Known repeated-Silence damage is repaired only after the original text is backed up.

## Production and evidence

See [production plan](docs/PRODUCTION.md), [AAA review standard](docs/AAA-CRAFT-REVIEW.md), [current rules](docs/ENGINE-v0.2.md), [project chat context](docs/CHAT-CONTEXT.md), [independent reviews](reviews), and [continuation priorities](docs/CONTINUATION.md).

Art is original AI-generated illustration with [provenance](public/art/PROVENANCE.json). The arena uses animated 2.5D cutouts, not rigged 3D characters. Historical v0.1 remains preserved under its original Lanternbound title.

## Preserved releases

Commit source and evidence, set a fresh version, build matching desktop artifacts, then `npm run release -- VERSION`. Existing release directories cause an error. Each milestone preserves source, offline web/desktop candidates, SHA-256 hashes, source commit and reviews. Failed reviews block promotion to a stable/commercial build. Old versions and historical findings remain intact.

Project-authored source remains unlicensed pending the owner's distribution choice. [Attribution](THIRD-PARTY.md) records runtime dependencies and asset limitations. Steam publication requires a verified Steamworks account/AppID, depot and install tests, rights/disclosure review, and platform verification. No Steam upload or public launch has occurred.
