# HOLLOWPACT — Steam store draft

Prepared from the v0.2 candidate source and production documents on 30 September 2026. Working title; trademark and market clearance unverified. **Internal draft only: not published, not Steam-approved, and not a commercial-readiness verdict.** Reconcile every claim with the frozen release build before submission.

## Hook and short description

**Bind dangerous creatures. Hunt worse things.**

> HOLLOWPACT is a grim roguelike deckbuilder. Read enemy intentions, break armor, silence reinforcements, and command dangerous bound creatures. Shape your deck, choose your upgrades, and prepare for one of three final contracts.

The quoted short description is 227 characters, within the requested 300-character limit. Recount after edits or localization.

## About this game — proposed full copy

**The contract is yours. So are the consequences.**

Enter a ruined abbey as a hunter who binds monsters to fight monsters. Each turn gives you five energy, a fresh hand, and a decision: deploy another creature, protect what you have, or spend your tools to stop the next threat.

**Read the quarry. Choose the answer.**

Enemy intentions reveal incoming strikes, armor, and reinforcements. Break an Ironjaw's guard before committing your creatures. Silence a necromancer before it raises the dead. Prepare protection before Cindermaw's breath lands. You choose each creature's target, and new bindings can act immediately.

**Build around the monsters you command.**

Hounds punish exposed prey. Stalkers recover through damaging commands. Colossi protect their hunter. Widows strengthen targeted spells. Combine these roles with damage, control, recovery, and command tools—or explore a leaner deck that rewards fighting without bindings.

**Make every stop count.**

Take a reward or refuse it to keep your deck tight. Trade with the quartermaster, remove a card, or train a specific binding or tool. At a field shelter, improving your deck means passing up treatment. In the crypt, read the price of a bargain before accepting it.

**Know what waits at the end.**

Your final quarry is revealed on the field chart: Ironjaw Warlord, Hollow Cantor, or Cindermaw. Prepare for its known trait as you follow a ten-contract campaign. Three difficulty settings let you learn the hunt or face greater pressure.

Original dark-fantasy illustrations frame the battles, with directed command effects and local save/resume. The current presentation uses animated 2.5D cutouts.

This copy describes current candidate mechanics. It contains no promised release date, duration, price, player rating, platform badge, or untested enjoyment claim. Adapt it to the eventual commercial scope; do not silently market a later feature roadmap as included content.

## Feature claim matrix

“In candidate” means present in inspected source, not certified through a complete final-platform test. Mechanic details: ENGINE-v0.2.md and `src/content.ts`. Presentation details: ART-DIRECTION.md, `src/art.ts`, `src/arena.ts`, and `public/art/PROVENANCE.json`.

| Claim | Current status | Publication gate |
| --- | --- | --- |
| Single-player, turn-based deckbuilding and commanded creatures | In candidate | Complete final packaged campaign using the actual controls |
| 24 base cards: eight bindings across four families and sixteen spells; enhanced forms | In content | Audit release registry and upgrade descriptions; count enhanced forms separately |
| Three final bosses and visible enemy intentions | In candidate; boss fixed by normalized seed | Inspect every boss cycle and final-quarry preview in the frozen client |
| Selected upgrades, optional rewards, shop/removal, crypt bargains | In candidate | Test duplicate-card selection, exact costs, cancellation, and save/resume |
| Three difficulty settings | In candidate; client names Initiate/Hunter/Veteran | Verify labels and scaling; validate learning comprehension with prospective players |
| Original grim illustrations and directed battle effects | Local generated assets and Canvas 2D cutout effects | Art provenance/rights gate plus independent visual review on the packaged build |
| Save/resume and device-local settings | In candidate; schema 2 uses separate storage from v0.1 | Restart, corrupt-save, completed-run, and update tests on each advertised OS |
| Keyboard and mouse interaction; motion and audio settings | In client source | Actual keyboard traversal, targeting, cancellation, readability, and settings tests |
| Windows / Linux support | Packaging configured; final platform support unverified | Clean-machine launch, full run, persistence, performance, and Steam depot tests per OS |
| Controller support or Steam Deck compatibility | Planned, unverified | Implement complete navigation/gameplay, then test hardware; no badges now |
| Rigged 3D models, anatomical animation, more biomes | Future production work | Completed assets, runtime integration, provenance, performance, and independent review |
| Capturing defeated monsters, placed traps, weapon slots | Future design experiments | Implement, validate, and update the copy only when included in the release |
| Steam achievements, Cloud, multiplayer, Workshop, localization | Not implemented or verified | Omit feature checkboxes unless the shipped integration and coverage are tested |
| “AAA,” “Steam-ready,” “players love it,” proven distinct builds | Unsupported claims | Do not use as store badges or endorsements; simulation and agent opinions are not human results |

## Screenshot plan

Capture the frozen production build at a consistent readable desktop resolution, with the cursor and debug overlays removed. Use representative live states and the game's actual UI. Preserve originals and build identity. Do not substitute concept art for gameplay screenshots or composite impossible hands/encounters.

1. **Core combat:** abbey arena, two different bindings, a selected legal target, visible hand, energy, and enemy intentions.
2. **Armor counterplay:** Ironjaw guard and Sundering Hex in hand; visible retaliation rule in the enemy panel.
3. **Necromancer pressure:** Cantor or acolyte raising intent, Bone Thralls, and Silence the Dead available. Show a real resulting state in a separate image if needed.
4. **Creature roles:** a mixed party with readable hound, stalker, colossus, and widow traits; avoid crowding away tactical text.
5. **Selected upgrade:** actual before/after chooser with deck-entry identity and return option.
6. **Field chart:** route choices and the final-quarry forecast; show available recovery and resources.
7. **Final contract:** Cindermaw's breath or heavy-strike intent with meaningful protection/damage choices.

Choose a small strong final set after independent review. Screenshots must represent the version buyers receive, including shared family illustrations and current cutout presentation.

## Gameplay trailer shot list

Target approximately 45–60 seconds; timings are an editorial plan, not an estimate of run length. Use actual captured gameplay, legible crops, restrained transitions, and audio from a reviewed final mix. Keep essential action sound audible under music; music requires documented rights.

| Time | Shot | Message |
| --- | --- | --- |
| 0–5s | Open directly on a command hitting its chosen target in the abbey | “Bind dangerous creatures. Hunt worse things.” |
| 5–14s | Bind a hound; break armor with Sundering Hex; command the exposed foe | Readable setup and payoff |
| 14–23s | Raising intent; cast Silence; show canceled reinforcement | Control answers a visible threat |
| 23–33s | Widow-assisted spell, stalker recovery, colossus command protection | Four roles with different decisions |
| 33–41s | Specific card upgrade, reward refusal, quartermaster trade | Shape the hunting plan |
| 41–52s | Short real excerpts from each of the three bosses | Different final contracts |
| 52–60s | Pact insignia and title over restrained abbey imagery | Title and accurate availability; add wishlist call only after the page is live |

Do not depict creature capture, controller play, rigged animation, multiple explorable biomes, or future content as current gameplay. Avoid fake review quotations and award laurels.

## Capsule and key-art brief

One strong composition: scarred hunter in a practical weather cloak holding an iron seal, with a threatening hound or widow and the ruined abbey behind. Keep the creature dangerous, the hunter capable, and the silhouette readable at small sizes. The title must remain clear on dark stone. Use soot, weathered iron, cold slate, bone, and restrained ember accents; no cheerful woodland mascot or franchise costume/weapon.

This is a proposed marketing illustration, not an in-game character-model claim. The current pact insignia is a starting element, not a completed capsule set. Export each required Steam capsule/library variant from the current Steamworks templates and validate their safe areas and artwork rules before delivery. Confirm title clearance first; retain editable masters, asset provenance, and licenses. Do not put unsupported feature badges, scores, pricing, or review quotes into the artwork.

## AI disclosure and rights gate

Proposed factual disclosure for review against the current Steamworks Content Survey:

> AI assistance was used during development for code and for pre-generated original creature, environment, and insignia illustrations. The game displays these local illustrations as animated 2.5D cutouts. It does not generate content live during play.

Complete the actual survey's fields accurately; this draft is not a survey submission. Disclose additional generated writing/audio/assets if they enter the final build, and reconcile the survey, credits, store claims, and release inventory. Do not claim solely human-authored artwork or live AI features.

Before commercial distribution: verify title/trademark clearance; confirm the owner's authority to distribute project-authored code and assets; review generated outputs and any input references; resolve the pending art rights review; audit dependency notices and preserve Electron/Chromium licenses; secure music, voice, font, trailer, and marketing-art rights where used. THIRD-PARTY.md is an inventory, not legal clearance. Do not reuse franchise creatures, logos, dialogue, or branded presentation.

## Platform testing and release checklist

- Freeze the candidate source and matching artifacts; record commit, hashes, review results, and known issues. Keep v0.1 and subsequent milestone archives intact.
- Resolve commercial scope, price, developer/publisher attribution, title clearance, source/asset rights, credits, and AI disclosure.
- Complete independent gameplay, visual/accessibility, technical, save, and packaging reviews of that same candidate. Resolve critical defects and obtain prospective-player feedback before enjoyment claims.
- Choose supported operating systems from evidence. Test clean installs, launch, full runs, alt-tab/fullscreen, offline play, settings, restart/resume, updates, and uninstall behavior on each. A cross-built Windows executable is not a Windows runtime test; historical v0.1 Linux evidence does not certify v0.2.
- Measure performance and memory on named hardware before supplying minimum/recommended requirements. Test supported display sizes and text readability; validate keyboard/mouse and reduced motion. Keep controller, Steam Deck, and accessibility badges unclaimed until their complete paths are tested.
- Verify a real Steamworks account and AppID, build/depot branches, launch options, install/update behavior, and entitlement on a clean Steam client. The Electron `appId` is not a Steam AppID.
- Finish current-template capsule/library art, actual-build screenshots, trailer, descriptions, support contact, mature-content questionnaire, and language coverage. No invented rating certificate or untranslated-language checkbox.
- Reconcile feature checkboxes with the matrix above. Test any subsequently added achievements, Cloud, controller integration, or localization before enabling its store claim.
- Submit the store page and build through the real Steamworks review process; retain actual feedback and repair findings. Verify release scheduling and required account-specific steps in the portal; do not infer approval from local packaging.
- Release only a reviewed stable candidate with accurate notes and known limitations. Preserve rollback artifacts and save compatibility decisions; collect opt-in player feedback and prioritize verified defects and meaningful improvements.

No account identifiers, publication, Steam approval, platform certification, or public launch are asserted by this draft.
