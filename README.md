# Hollowpact

A grim monster-binding roguelike deckbuilder. Play a contract hunter, deploy dangerous creatures, and defeat an armored warlord, a necromancer or an ember dragon. Working title; name clearance remains pending.

**v0.8.0 reviewed development checkpoint.** Optional local creature sound, original crypt encounters and a hunter pose width repair pass separately identified gameplay, visual and technical gates. Five hash-verified archives preserve the exact source bundle, offline web build, portable Linux build and actual-tested original Windows build/evidence. See [release identity](releases/0.8.0/manifest.json) and [independent archive audit](reviews/release-v0.8-final-independent/REVIEW.md). Production continues with scene coherence, articulated biting and corrected final-kill readouts. Sparse animation, repeated creature illustrations, stale health during the retained final-strike hold and human enjoyment remain open; AAA craft and Steam readiness are targets.

## Run

Node 22 or later. `npm ci`, then `npm run dev`. Open the printed local address. `npm test` checks the renderer-free rules; `npm run build` checks TypeScript and creates an offline web build. `npm run simulate` compares reproducible policies. `npm run test:browser` tests the built production assets with system Chromium; adjust `playwright.config.ts` to your installed browser on other machines.

`npm run desktop` launches current built assets. Package into a fresh independent output directory with the installed Electron builder, for example `npx electron-builder --linux dir --config.directories.output=/tmp/hollowpact-my-new-package`; build current assets first. Retained comparison directories and their aliases are immutable by usage contract. The Windows validation-only ASAR proxy must never be launched or repacked as a complete package. Linux needs the usual Chromium GUI libraries. Actual v0.8 Windows Server2022 portable QA and original binary inspection are [recorded separately](reviews/native-windows-v0.8-23477-binary-independent/REVIEW.md). Consumer installs, physical controllers, Steam Deck, listening and Steam installation still need their own evidence.

## Combat

Five energy and five fresh cards each turn. Play a creature, select its ready binding, then select an enemy to command it. Arrival-turn commands are allowed. Six slots per side, visible enemy intentions, no range rules. Living bindings stay outside deck cycling; fallen ones enter discard. Hunter health carries between fights; bindings reset.

Cairn Hounds punish exposed enemies. Fen Stalkers recover through damaging commands. Briar Colossi protect the hunter. Ash Widows strengthen targeted damage tools. Build around these roles, inspect the final quarry's traits, and select upgrades deliberately. Armored retaliation, delayed reinforcements and dragon breath require different answers.

Rewards can be skipped. Rest or choose a specific deck entry to train, buy or remove cards, and judge shrine bargains before accepting them. Saves and settings stay on the device; no telemetry is sent. The optional Field report downloads feedback locally. New campaigns use schema3/engineKind2; existing schema2 campaigns continue their original kind1 rules. Both use the historical run storage key. Known repeated-Silence damage is repaired only after the original text is backed up.

## Production and evidence

See [production plan](docs/PRODUCTION.md), [AAA review standard](docs/AAA-CRAFT-REVIEW.md), [current rules/save contract](docs/ENGINE-v0.5.md), [project chat context](docs/CHAT-CONTEXT.md), [independent reviews](reviews), and [continuation priorities](docs/CONTINUATION.md).

Art is original AI-generated illustration with [provenance](public/art/PROVENANCE.json). The arena uses animated 2.5D cutouts, not rigged 3D characters. Historical v0.1 remains preserved under its original Lanternbound title.

## Preserved releases

Commit source and evidence, set a fresh version, build matching desktop artifacts, then `npm run release -- VERSION`. Existing release directories cause an error. Each milestone preserves source, offline web/desktop candidates, SHA-256 hashes, source commit and reviews. Failed reviews block promotion to a stable/commercial build. Old versions and historical findings remain intact.

Project-authored source remains unlicensed pending the owner's distribution choice. [Attribution](THIRD-PARTY.md) records runtime dependencies and asset limitations. Steam publication requires a verified Steamworks account/AppID, depot and install tests, rights/disclosure review, and platform verification. No Steam upload or public launch has occurred.
