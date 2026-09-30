# Lanternbound

A folklore monster hunter builds a deck of creature companions and spells, commands a summoned team, and follows dangerous contracts from a lantern-lit inn. Working title; original characters and procedural artwork.

Development prerelease. A playable milestone is not a Steam commercial-quality certification. See [production plan](docs/PRODUCTION.md), [project chat context](docs/CHAT-CONTEXT.md), [review evidence](reviews), and [release archives](releases).

## Run

Node 22 or later. `npm ci`, then `npm run dev`. Open the printed local address. `npm test` checks the renderer-free rules; `npm run build` checks TypeScript and creates an offline web build. `npm run simulate` runs reproducible policy comparisons. `npm run test:browser` tests the built production assets with system Chromium; adjust `playwright.config.ts` to your installed browser on other machines.

`npm run package:linux` or `npm run package:windows` builds an Electron desktop directory. `npm run desktop` launches the current built web assets locally. Linux environments need the usual Chromium GUI libraries. Packaging on this host does not verify Windows launch or Steam installation.

## Combat

Five energy and five fresh cards each turn. Summon creatures, cast spells, click a ready companion and then an enemy to command its free move. Newly summoned creatures can act immediately. All six slots share a turn; there are no range rules. Read the enemy's target and damage before ending the turn. Your hunter's health carries between battles. Living creatures stay outside deck cycling. This prototype provisionally returns dead creature cards to the shared discard pile.

Rewards can be skipped. Rest or strengthen your deck at camp, spend gold at shops, and choose safer contracts or elites before the boss. Saving happens locally after actions; no telemetry leaves your machine.

## Releases

Commit source and evidence, set a new package version, build matching desktop artifacts if required, then `npm run release -- VERSION`. Existing release directories cause an error. Every milestone preserves source, build, SHA-256 hashes, source commit, and reviews. A failed review blocks stable promotion. Older versions are retained, and candidates remain labelled as development builds.

All project code remains unlicensed pending the owner's distribution choice. Dependency attribution appears in [THIRD-PARTY.md](THIRD-PARTY.md). Steam publication requires the owner's Steamworks app/account setup and platform verification.
