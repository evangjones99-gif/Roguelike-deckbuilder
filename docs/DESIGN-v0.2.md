# HOLLOWPACT — v0.2 candidate design

Proposed working title; clearance unverified. This is a reviewable implementation plan, not a claim that the features below have shipped. Preserve Lanternbound v0.1 and all of its independent reviews before applying the new direction.

## Player promise

Take dangerous contracts as a hardened hunter. Read the prey's next move, prepare the right tools, and command bound monsters to exploit openings. Build a deck with a distinct hunting method rather than always filling six slots and cycling the same buffs. The world is gritty and grounded; effects and choices remain plain English. Use original IP throughout.

## Evidence driving this iteration

The independent v0.1 gameplay review accepted a playable prototype and rejected commercial/Steam-ready promotion. Across its 864 seeded simulations, threat-aware starter policies could win without acquisition, and one untouched starter policy won all tested hard normal-route seeds. The reviewer found targeted combat decisions but little strategic variation, untargeted camp upgrades, excess late gold, fixed routes, and repeated elites/relics. These are sampled policy outcomes, not a proof that every build is solved. The visual reviewer found inconsistent card/model identities and preliminary attack/death feedback even after readability and motion defects were repaired. Preserve both reports as baseline evidence.

## Candidate scope and sequence

1. Replace the cozy world, names, palettes, creature proportions, UI voice, and card/arena identity consistently. Deliver the contract hunter fantasy with a small original roster before adding a large catalogue.
2. Add a real camp upgrade choice: select an eligible card from the actual deck, show its exact before/after stats or effect and cost, allow cancellation, and apply only the chosen upgrade. Duplicate cards must be distinguishable by deck entry; never silently upgrade the first eligible summon.
3. Establish two different viable plans beyond the current full-board buff loop. Give acquisition and removal a purpose, then test pressure, recovery, and the shop economy together.
4. Add a small number of announced enemy questions and contract/event outcomes. Reuse well-understood mechanics where appropriate; do not increase all enemy damage to disguise shallow progression.
5. Freeze source, review the real client and engine independently, preserve artifacts, and compare fresh holdout outcomes against baseline. Publish this milestone honestly as a candidate/prototype until broader release gates pass.

## Three proposed hunting plans

| Plan | Player decisions | Necessary payoff | Counterpressure |
| --- | --- | --- | --- |
| Pact | Keep a few strong monsters alive; choose protection versus immediate damage | Bound creatures that reward different command timings and roles rather than universal stacking buffs | Announced sweep or binding disruption creates a defense/redeployment decision |
| Hunt | Prepare a marked target, then spend precise damage during its opening | Mark/exposure payoff and a reliable hunter attack tool; rewards can improve focused damage without filling the board | A guard cycle makes timing matter; overkill wastes the opening |
| Seal | Use tools and spells to disrupt a dangerous move and convert that delay into damage | A limited interrupt/control resource and a fragile creature that rewards tool use | Multiple threats require selecting which move to disrupt; immunity must be visible and specific |

These are hypotheses. A renamed damage spell is not a different archetype. Each plan must change legal-action priorities, reward preferences, and response to at least one encounter. Retain skip rewards as a sensible deck-size choice. Do not force acquisition by making every starter card unusable.

## Tools, traps, and binding choices

Keep two primary card categories initially: bound creatures and hunter tools/spells. A trap can be a tool card rather than requiring a third category. Select one addition only after engine/UI ownership and testing are arranged.

| Option | Benefit | Cost/risk | Recommendation |
| --- | --- | --- | --- |
| Immediate seal/control tool | Fits current targeting, communicates a response to announced intent | Permanent stun could erase enemy counterplay; needs a bounded effect | First candidate: reduce or interrupt one explicitly eligible announced move, with visible duration |
| Mark/expose tool | Creates a hunter-centered focused-damage plan with simple targeting | Stacking can become another universal buff | Test one nonstacking, clearly scoped mark that expires predictably |
| Persistent trap | Strong preparation fantasy and route/encounter anticipation | Requires placed state, trigger timing, ownership, and UI; hidden triggers confuse play | Later experiment after immediate control/mark are understandable |
| Binding/recruitment reward | Makes winning a contract feed the creature deck and hunter identity | A giant random bestiary dilutes art quality and build purpose | Offer a small creature/tool choice tied to the completed contract; always permit refusal |
| Hunter weapon/relic slots | Visible identity and long-run commitment | New UI, save migration, balance interactions and progression cost | Defer until card plans already create distinct runs |

## Encounter prototypes

Iron Husk alternates a clearly shown guard turn with an exposed turn. The response is to prepare/defend through guard or break it with a stated tool, then exploit the opening. Hollow Cantor announces a binding-disruption or heavy attack with a visible eligible interrupt window; avoiding it costs a card/resource, so disabling every enemy is not automatic. Carrion Ravager pressures a named target and rewards removing that threat before its next action. The Bellwrought boss announces guard, breach, and charge states with exact effects; the player chooses focused damage, protection, or a limited interrupt. Exact values and timing are balance experiments, not established implementation contracts.

Provide enemies with a reason to exist beyond HP inflation. Every new rule needs readable intent text, tooltips, legal actions, saved state, simulation support, and an accessible HTML representation. Stable announced targets should remain stable during a turn unless a deliberate mechanic clearly explains the change.

## Contract map, economy, and learning

Use a compact route with visible contract danger and available recovery. Place a purchase/removal opportunity where earned gold can actually change later battles; compare income, prices, resting, innate healing, and upgrades as a system. Add two or three authored event choices with actual deck/resource tradeoffs before writing a large lore corpus. A contract can preview a dominant enemy trait so preparation is an informed choice.

Keep the forgiving learning difficulty. Explain command timing, summons, incoming damage, and tool targeting through clear neutral instruction. Plain language belongs in a mature game. Rename cheerful camp/event copy into believable field actions without obscuring costs or outcomes. The hunter's character emerges through short contract details, worn equipment, and consequences, not exposition between every click.

## Promotion evidence

Required for this candidate: source/artifacts with hashes; complete-run regression and save checks; actual client inspection of targeting and selected upgrades; card/arena registry consistency; motion/accessibility checks; no new critical blockers; and preserved release/review history. Independently compare alternate plan policies on fresh holdout seeds and report card/reward selections, damage, turns, healing, purchases, upgrade targets, and outcome variation. Keep training seeds separate from holdouts.

No specific win rate constitutes a fun score. Test whether a selected upgrade changes a later decision, whether rewards change the plan, and whether a control enemy has a visible usable answer. Obtain prospective-player feedback on threat comprehension, memorable monsters, rewarding acquisition, unnecessary clicks, and desire to replay before claiming high-quality human enjoyment. Steam readiness still requires platform/install, rights, store, Steamworks, and other gates in PRODUCTION.md.
