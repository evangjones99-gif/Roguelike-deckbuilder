# Agent UI playtest working observations (not final)

Synthetic agent experience; not a human participant, human enjoyment consensus, hearing test, native hardware test or AAA approval. Runtime 23477f68c99d6d60b0b3f82b286a8d33bb6da6f2ca92c103fbecf5663634959f, v0.8.0, seed242113, Hunter difficulty1. Visible UI choices only. No engine/oracle/policy imports or hidden draw/discard inspection. Observations remain tentative until the legitimate campaign outcome.

Specific craft priorities:
- Final-kill hold displays dead quarry with positive pre-action health. Elite decisions078–082 and dragon107–111 include actual lethal preview/action, midhold at450ms and retained screenshots; all timestamps use browser performance.now. Narrative status says Quarry down while numeric state remains4/21 or9/35. Preserve dramatic hold but make outcome labels and displayed values consistent. No multiple-survivor defeat claim from this campaign yet.
- Shrines at contracts2 and5 repeat all five options verbatim; Leave is dominated by free25gold in the displayed prices. Greater event variety and an actual visible tradeoff could help.
- First elite repeats the opening Reaver/Revenant group, adding a second Reaver and health. Second elite introduces Hollow Acolyte summoning, a more distinct tactical prompt. Review encounter differentiation before changing global difficulty.
- Reward relic effect was discovered through public Deck inventory rather than visible reward announcement. Show name and effect where earned.
- Pointer remains over the replacement hand slot and guidance immediately describes another card after a play, while the announcer names the actual played card. Do not misdiagnose this as wrong-card execution; it is confirmation clarity.
- Three-turn clears sometimes end in a short cleanup turn after the decisive setup. Assess in prospective human tests; tool/controller wall time cannot measure human pacing.

Positive scoped tactical evidence:
- Revenant block ignoring and spell resistance made warding insufficient and Widow amplification/creature commands useful.
- Spell-breaking Reaver armor before commanding avoided counterdamage.
- Known Cantor summon/area patterns informed Ember Widow, Witchfire and Black Aegis acquisition, then Witchfire training. Dragon AoE and front bite demonstrated a concrete preparation payoff and impending companion loss avoided through a lethal targeted spell.
- Hunter health spent for Wraithglass plus later treatment created a tangible preparation cost. Harpoon choice trades deck dilution for scaling with bindings.

Harness failures preserved as separate files. Initial nonTTY stdin closed before campaign; fresh R2 is original UI-created campaign. New wrong data-action selector and wrong aria attribute each timed out; ambiguous modal close selector subsequently queued blocked background clicks. These are harness mistakes, not product crashes. A ps -C node check falsely missed Node processes named MainThread, so an initially reported process interruption was corrected. No save recovery/injection occurred.
