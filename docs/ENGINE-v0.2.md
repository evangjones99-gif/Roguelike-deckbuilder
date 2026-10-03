# HOLLOWPACT v0.2 — engine and gameplay iteration

This release replaces the folklore tone with an original grim contract-hunter setting. The v0.1 sources, baseline reviews and released build remain archived. v0.2 is a prototype milestone; automated completion, tactical variety and new art do not establish AAA craft or human enjoyment.

## Save and renderer contract

`GameState.schema` is now `2`. Historical schema-1 saves are rejected by this engine and remain usable with the archived v0.1 build. The client uses a separate v0.2 save key. The reducer still clones accepted actions, returns the original state for illegal actions, and has no timers, I/O, renderer dependencies or ambient randomness.

`CardDef.passive?: string` and `Unit.passive?: string` expose exact readable creature/enemy rule descriptions. Enemy `intent` additionally supports `summon?: string[]`: reinforcement ids announced before resolution. Raising intents have zero direct damage and describe the number of Bone Thralls. `camp` now accepts `index?: number`; a train action is legal only with an actual unenhanced deck index. `legalActions` returns one train action per eligible copy. Rest remains an untargeted 18-HP recovery action.

`bossForSeed(seed)` in content selects Ironjaw Warlord, Hollow Cantor or Cindermaw by normalized seed modulo three. Its result does not change with earlier RNG consumption; the UI can reveal the final contract early so builds can prepare deliberately.

`stats.turns` now counts each actual player turn, including the initial and terminal turn of every encounter. v0.1 counted completed nonterminal end turns, which understated pacing. Compare pacing measurements with this semantic difference in mind.

## Creature roles and build decisions

Eight summon cards use four original creature families, with two contract loadouts each. Every live creature owns exactly one deck copy outside the piles. A dead creature returns that copy to shared discard; duplicates remain independent real copies. Creature stats and all battle-only bonuses reset at the next contract.

| Family | Rule | Strategic purpose |
|---|---|---|
| Cairn / Grave Hound | Commands deal +2 damage against enemies with no block. | Executes exposed foes and necromancer servants; wants armor broken first. |
| Fen Stalker / Fen Raker | A command that deals health damage heals this creature 2 HP. | Endures focused creature damage; hitting only block provides no recovery. |
| Briar / Ossuary Colossus | Every command grants the hunter 2 block. | Durable protection and control support; commands cost opportunity even when blocked. |
| Ash / Ember Widow | Each living widow adds 2 damage to targeted damaging spells. | Spell amplification and armor-safe attacks; low creature attack and no boost to area spells. |

There are sixteen base spells. Pack Edict now costs two energy, making pack growth compete with defense and control. Sundering Hex removes all enemy block before damage and avoids retaliation. Silence the Dead cancels announced damage and reinforcements for one turn, while armor still resolves. Grave Resonance deals an additional four damage when there are no bound creatures, creating a useful solo opening and a payoff for creature removal. Widow amplification, the solo payoff, pack-scaled Chain Harpoon, targeted recovery, area damage and readying commands ask different deck questions. These are designed distinctions; independent playtesting must establish their viability and clarity.

No hidden poison/keyword counters were added. A resolving spell enters discard after its effect and cannot draw itself. Forbidden Survey costs one energy. Blood Price is a visible three-HP risk. Maximum hand size remains twelve and maximum creature count six.

## Enemy plans and counterplay

All intents are computed at player-turn start and stay stable through ordinary binding and commands. Silence deliberately updates the affected announcement, showing its canceled effect. A dead creature target falls back to the hunter; it never secretly retargets another creature. Hunter death takes precedence over victory.

- Ironjaw Reavers and the Warlord alternate guarding and cleaver strikes. While block remains, a command reflects one/two damage through the attacking creature's block. Spells do not trigger it. Sundering Hex creates a safe command window, and exposed-target hounds exploit it. Retaliation can kill a creature and immediately returns its card copy to discard.
- Gloam Revenants strike through block and reduce targeted spell damage by two. Commands and untargeted Witchfire avoid that spell resistance, making target choice differ from an armored Ironjaw foe.
- Hollow Acolytes alternate raising one Bone Thrall and cursing the hunter. The Cantor raises two, curses the hunter, then assaults all targets. Silence or killing the raising source prevents its reinforcements. Raised creatures appear after the existing enemy roster finishes and receive visible intentions for the next player turn. They never attack immediately without a player response window. The six-enemy limit caps pressure.
- Cindermaw Brood alternate front-creature bites and area breath. The Cindermaw boss guards, breathes against all targets, then delivers a heavy hunter strike. Targeted healing, Black Aegis and attack/control timing compete around those windows.
- Bone Thralls attack the weakest creature or the hunter when none remain. Clearing servants and killing their source are separate tactical choices.

Four elite formations combine these roles: armored reaver/revenant/acolyte, brood/acolyte, two reavers/revenant, or acolyte/two revenants. A single familiar enemy silhouette can therefore ask different tactical questions in a formation. Enemy armor expires after the player gets one turn to react and before the next enemy actions; a silenced attack does not accidentally become a guard. Guard resolution uses enemy identity and turn phase, never parsed UI text.

## Progression and recovery

The ten-node trail preserves the accessible finite structure, with battle/event, camp/shop and normal/elite alternatives. Final contracts vary by seed. Five crypt choices offer an HP-paid relic, gold, HP-paid removal of an unenhanced Scour, paid recovery, or safe departure. The first base Scour removed by the purge is stated explicitly; camp upgrades are player-targeted rather than inferred from deck order.

Six relics now support spell damage, creature endurance, opening energy, victory recovery, creature attack or turn-start energy without creatures. Three possible elite visits cannot guarantee the complete catalogue. Normal and elite victories restore two/three HP respectively; Surgeon's Reliquary adds two. Camp rest remains 18 HP, and a 30-gold surgeon bargain restores 16. These narrower automatic heals allow more purposeful recovery while retaining Story accessibility.

Shop prices stay 55 gold for summons, 40 for spells and 35 for removal, with at least five cards retained. Rewards are optional and unique within each offer; purchases remove their item from current stock. Normal/elite wins grant 25/40 gold. Story/Contract/Nightmare difficulty controls enemy health and damage scaling; bosses gain twelve additional HP per difficulty level, while thralls receive a smaller health increment so repeated reinforcements stay manageable. These are transparent deterministic rules, not dynamic difficulty or live ML mutation.

## Validation and evidence boundaries

Save validation rejects schema-1 and presentation-only menu states; malformed or nonfinite bounded fields; unknown own-property card/enemy/relic ids; forged passive descriptions; duplicate or unallocated unit ids; illegal reinforcement types/counts; broken card-copy conservation; incompatible phases, floors and routes; and dead-end final-node battle/reward saves. Generated mid-combat states, including a dead intent target awaiting hunter fallback, remain valid. It is structural validation for local saves, not a cryptographic anti-cheat system.

`npx tsx --test tests/engine.test.ts` includes focused regressions for each creature role, retaliation and copy conservation, silence versus armor, reinforcement cancellation and response windows, six-slot caps, all boss cycles/selection, targeted duplicate upgrades, relic support, recovery/economy, serialized replays and corrupt saves. Three hundred seeded legal-random runs validate every intermediate state across three difficulties. `npx tsx scripts/simulate.ts 100 2` runs the fixed-policy balance harness at difficulty two; difficulty is its optional second CLI argument after seed count.

Initial seeds 1–100 yielded fixed heuristic wins of 100/100 Story, 100/100 Contract and 95/100 Nightmare, compared with random wins of 3/100, 0/100 and 0/100. There were no incomplete runs. This demonstrates deterministic completion and a tactical policy advantage in this sample. It does not prove optimal balance, independent build viability, AAA quality or fun. Fresh independent holdouts, browser/controller/visual review and observed human sessions remain separate release gates. The v0.1 baseline artifacts are retained for comparison; no improvement should be claimed solely from higher win rates or more content.
