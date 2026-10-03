# HOLLOWPACT — v0.2 candidate design

Working title; clearance unverified. Aligned with the current `src/content.ts`, client source, and ENGINE-v0.2.md on 30 September 2026. This document distinguishes implemented candidate mechanics from future experiments. The preserved Lanternbound v0.1 artifacts and reviews remain the historical baseline. Current source is a prototype candidate, not evidence of public Steam release, AAA quality, or human enjoyment.

## Player promise

Take dangerous contracts as a hardened hunter. Read the prey's next move, prepare the right tools, and command bound monsters to exploit openings. Build a deck with a distinct hunting method rather than always filling six slots and cycling the same buffs. The world is gritty and grounded; effects and choices remain plain English. Use original IP throughout.

## Evidence driving this iteration

The independent v0.1 gameplay review accepted a playable prototype and rejected commercial/Steam-ready promotion. Across its 864 seeded simulations, threat-aware starter policies could win without acquisition, and one untouched starter policy won all tested hard normal-route seeds. The reviewer found targeted combat decisions but little strategic variation, untargeted camp upgrades, excess late gold, fixed routes, and repeated elites/relics. These are sampled policy outcomes, not a proof that every build is solved. The visual reviewer found inconsistent card/model identities and preliminary attack/death feedback even after readability and motion defects were repaired. Preserve both reports as baseline evidence.

## Implemented candidate scope

The candidate uses original grim contract-hunter names, a local generated ruined-abbey background, and illustrated 2.5D creature cutouts. The current content is **eight bindings across four role families plus sixteen spells**, making 24 base cards with enhanced forms. Four elite formations, six relics, five crypt event choices, and three seed-selected bosses broaden the finite ten-node campaign. ART-DIRECTION.md records exact families and shared illustrations; do not equate card count with unique illustrated species.

Camp training selects a real eligible deck index, so duplicates can be enhanced independently. The client shows a per-copy before/after comparison and permits cancellation. Creature enhancement adds 3 HP and 1 attack. Most spells increase their effect value by 2; enhanced Silence the Dead instead reduces its energy cost from 2 to 1. Training consumes the shelter choice; resting remains an alternative.

The engine remains a deterministic renderer-independent reducer with five energy, five fresh cards, six creature slots, and free manual commands including the binding turn. Kill Command explicitly readies a creature for another command. Living bindings keep their own source card out of the piles, dead bindings return that copy to discard, and temporary stats reset each fight. Save schema 2 and a separate client save key distinguish this candidate from archived v0.1. ENGINE-v0.2.md is the detailed mechanics and validation reference.

## Four implemented binding roles

| Family and cards | Implemented payoff | Intended decision |
| --- | --- | --- |
| Hounds: Cairn Hound / Grave Hound | Commands deal +2 damage against unblocked enemies | Break armor first or execute an already exposed enemy |
| Stalkers: Fen Stalker / Fen Raker | Commands dealing health damage heal the creature 2 HP | Choose a target that yields recovery; block-only hits do not heal |
| Colossi: Briar Colossus / Ossuary Colossus | Each command grants the hunter 2 block | Allocate commands for protection as well as damage |
| Widows: Ash Widow / Ember Widow | Each living widow adds 2 targeted spell damage | Protect fragile amplifiers; targeted and area spells have different payoffs |

These roles exist in the reducer. Their ability to sustain distinct viable builds remains a review question. The twelve-card starter contains all four families, so acquisition needs to change commitment and action priorities rather than merely introduce a role the starter already has.

## Current tools and build hypotheses

The two primary card categories remain bindings and tools/spells. Current tools include targeted/area damage, block, creature healing, permanent-in-battle pack growth, command readying, draw, energy for an HP cost, hunter recovery, armor removal, and one-turn control. There are no placed traps, mark counters, poison counters, weapon slots, or persistent binding-disruption debuffs in this candidate.

| Candidate build hypothesis | Existing support | What independent playtesting must establish |
| --- | --- | --- |
| Exposed-prey commands | Sundering Hex removes block before damage; hounds exploit unblocked targets; Pack Edict and Kill Command support creature damage | Armor removal and command timing change target priorities without making every deck identical |
| Spell amplification/control | Widows amplify targeted spells; Silence the Dead cancels announced damage and reinforcements for this turn, while armor still resolves | Protecting widows and paying control costs compete meaningfully with damage and defense |
| Enduring bindings | Stalker recovery, colossus hunter block, Blood Sutures, Black Aegis, and Flesh Covenant | Recovery has a tactical price and does not trivialize all sustained threats |
| Sparse/solo hunter | Grave Resonance deals +4 damage with no bound creatures; Dead Man's Coin grants turn-start energy without creatures | A sparse deck is viable beyond a good opening turn and offers useful acquisition/removal decisions |

Rewards can be refused to preserve deck size. There is no scripted capture system tied to the defeated creature: victory currently offers optional card acquisition. The above plans are supported design hypotheses, not proven independent archetypes or human preferences.

## Implemented encounter questions

Ironjaw Reavers and the Ironjaw Warlord alternate guard and strikes; commands reflect damage while their block remains, while spells avoid retaliation. Sundering Hex opens a safe command window. Gloam Revenants ignore block and reduce targeted damaging spells by 2, favoring commands or untargeted Witchfire. Hollow Acolytes announce one Bone Thrall reinforcement; the Hollow Cantor boss raises two, curses, and then assaults all targets. Killing the source or using Silence prevents announced reinforcement. New thralls receive next-turn intents and a player response window. Bone Thralls threaten the weakest binding or the hunter when no bindings remain.

Cindermaw Brood alternate a front-creature bite with area breath. The Cindermaw boss cycles guard, area breath, and a heavy hunter strike. Healing, group protection, and control timing provide different responses. Ironjaw Warlord, Hollow Cantor, and Cindermaw are the three final bosses. The normalized seed selects the boss independently of earlier RNG consumption, and the client previews its name and known trait on the field chart.

Earlier proposal names such as Iron Husk, Carrion Ravager, and The Bellwrought are not implemented encounters. The Cantor does not apply a persistent binding-disruption mechanic. Exact current HP, damage, and passive text live in `src/content.ts`; intent cycles and resolution are documented in ENGINE-v0.2.md.

Provide enemies with a reason to exist beyond HP inflation. Every new rule needs readable intent text, tooltips, legal actions, saved state, simulation support, and an accessible HTML representation. Stable announced targets should remain stable during a turn unless a deliberate mechanic clearly explains the change.

## Current progression and recovery

The ten-node route retains battle/event, camp/shop, and normal/elite alternatives. The single crypt event offers five choices: trade 8 HP for Wraithglass Shard, take 25 gold, pay 4 HP to remove the first unenhanced Scour, pay 30 gold for 16 HP recovery, or leave. The purge names its deterministic target; it is not arbitrary selected-card removal. Shops offer optional bindings/tools and selected-card removal, priced at 55/40/35 gold, retaining at least five cards. Rewards and purchases avoid duplicates within the offer/stock, while deck duplicates remain allowed.

Normal/elite victories award 25/40 gold and recover 2/3 HP. The surgeon relic adds 2 victory recovery, and camp resting restores 18 HP. Six relics support spell damage, creature endurance, opening energy, victory recovery, creature attack, or solo turn-start energy. Three possible elite visits cannot award the whole catalogue. These are current retunings; whether gold timing, acquisition, and recovery become more purposeful needs comparative testing rather than an assumption based on content count.

The client labels difficulties Initiate, Hunter, and Veteran, corresponding to engine levels 0/1/2. ENGINE-v0.2.md uses the earlier internal Story/Contract/Nightmare labels for those same levels. Keep the forgiving learning setting and neutral explanations of energy, cycling, commands, target fallback, and announced reinforcement. Dark tone must not obscure actual costs or outcomes. The hunter's character should emerge through contract details and field actions rather than exposition between every click.

## Future experiments, not current features

Placed traps could strengthen preparation but require saved placement state, visible triggers, and clear timing. A nonstacking mark could add another focused-damage option, but hounds already reward exposed targets and armor removal, so duplication needs a reason. Weapon slots and captured-prey acquisition would add identity at the cost of UI/save complexity. More biomes, unique variant illustrations, and rigged characters are separate production tasks. Do not add these before reviewing current role viability, economy, clarity, and presentation. Expand only where evidence identifies a missing choice or visual weakness.

## Promotion evidence

Required for this candidate: source/artifacts with hashes; complete-run regression and save checks; actual client inspection of targeting and selected upgrades; card/arena registry consistency; motion/accessibility checks; no new critical blockers; and preserved release/review history. Independently compare alternate plan policies on fresh holdout seeds and report card/reward selections, damage, turns, healing, purchases, upgrade targets, and outcome variation. Keep training seeds separate from holdouts.

No specific win rate constitutes a fun score. Test whether a selected upgrade changes a later decision, whether rewards change the plan, and whether a control enemy has a visible usable answer. Obtain prospective-player feedback on threat comprehension, memorable monsters, rewarding acquisition, unnecessary clicks, and desire to replay before claiming high-quality human enjoyment. Steam readiness still requires platform/install, rights, store, Steamworks, and other gates in PRODUCTION.md.
