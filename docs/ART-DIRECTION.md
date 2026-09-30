# HOLLOWPACT — v0.2 art direction

Working title; trademark and market clearance unverified. Aligned with the current `src/content.ts`, `src/art.ts`, `src/arena.ts`, local art provenance, and ENGINE-v0.2.md on 30 September 2026. Current presentation is an illustrated 2.5D prototype using generated local cutouts, not rigged 3D characters. Source inspection does not establish final commercial art quality or human enjoyment.

## Fantasy and tone

You are a scarred contract hunter, armed with iron seals, field medicine, targeted spells, and dangerous bound creatures. The current arena is a rain-soaked ruined abbey. Ruined keeps, flooded crypts, war-torn wilderness, and placed traps are future expansion ideas. Binding a monster is an uneasy practical bargain. Show competence, danger, and the cost of survival. Broad dark-fantasy influences are tonal references; create original designs and writing.

Give the hunter an identifiable presence: a battered hood or short weather cloak, practical mail/leather layers, bandaged forearm, worn knife, and a heavy seal gauntlet. Avoid an ungrounded heroic costume covered in decorative straps. The silhouette must read in one value thumbnail. A contract map is a marked field chart; camp is a temporary shelter; a merchant is a quartermaster. Learning difficulty stays welcoming through clear instruction and forgiving numbers, without changing the world into a children's story.

## Visual rules

| Element | Required treatment | Avoid |
| --- | --- | --- |
| Creatures | Distinct mass, anatomy, posture, weapons, and locomotion; scars, torn hide, crusted iron, or water damage with a reason | Chibi bodies, oversized friendly eyes, rounded plush faces, smiling woodland mascots |
| Materials | Weathered iron, soot, bone, wet stone, cracked hide, stained cloth; readable roughness contrast | Uniform glossy plastic, candy colors, decorative noise across every surface |
| Light | Cool directional moonlight or overcast light; localized ember or lantern warmth; dark contact shadows | A uniform black screen, permanent cheerful golden glow, bloom that hides silhouettes |
| Environment | A clear tactical clearing bordered by broken architecture or wilderness; restrained fog and sparse motion | Busy foreground vegetation blocking units, spectacle that obscures targets |
| Interface | Charcoal panels, restrained iron borders, off-white tactical text, worn paper in maps/contracts | Childlike bubbly typography, ornamental illegible text, small dim damage/intent text |
| Spell effects | Brief seals, iron filings, ash, restrained ember bursts; distinct shape for each function | Rainbow sparkle, constantly pulsing whole-screen effects, identical effects on every card |

Palette anchors: soot `#111516`, weathered iron `#394448`, cold slate `#64747A`, old parchment `#D1C5AB`, bone text `#E6DDCB`, ember `#C9844C`, dried blood `#813F3A`, restrained spectral teal `#648E89`. These are material anchors, not permission to make essential text low contrast. Damage, block, and readiness need explicit words/icons as well as color.

## Current binding roster and illustration registry

The implemented deck contains eight bindings across four families, with two loadouts per family, plus sixteen spells: 24 base cards, each with an enhanced form. Four companion illustrations represent the four families. The second loadout currently shares the same family art; this is eight cards, not eight independently illustrated species. `portraitFor` in `src/art.ts` supplies the same atlas cells to the cards and arena.

| Family and current cards | Art direction and current atlas identity | Implemented combat role |
| --- | --- | --- |
| Cairn Hound / Grave Hound | Spectral bone-plated hound; lean predatory anatomy, scarred hide | Commands deal +2 damage against enemies with no block |
| Fen Stalker / Fen Raker | Amphibious corpse-stalker; long limbs and muddy hide | A command dealing health damage heals the creature 2 HP |
| Briar Colossus / Ossuary Colossus | Heavy giant of bark, bone, and stone/iron; strong mass and grounded stance | Each command grants the hunter 2 block |
| Ash Widow / Ember Widow | Obsidian giant spider with ash/ember veins; jointed legs and low silhouette | Each living widow adds 2 damage to targeted damaging spells |

The stronger loadouts also differ in cost, stats, and binding effects described in the content source. Exact rules must be available in HTML; art alone cannot communicate these variants. Separate illustrations or variant markings can improve recognition later, but are not present merely because the card has a different name.

## Current adversaries and bosses

Eight enemy definitions use four adversary illustration cells. The three bosses are selected deterministically from the seed and previewed on the field chart. Reavers, acolytes, brood, and thralls reuse family illustrations; they are distinct rules and names, not eight unique rendered models.

| Current foes | Shared illustration | Implemented combat identity |
| --- | --- | --- |
| Ironjaw Reaver / Ironjaw Warlord | Plated warlord | Guard and cleaver cycle; command retaliation while armored; Warlord is a boss |
| Gloam Revenant / Bone Thrall | Spectral ruined knight | Revenant ignores block and resists targeted spell damage; thrall targets the weakest binding or hunter |
| Hollow Acolyte / Hollow Cantor | Funeral-robed necromancer | Announced Bone Thrall reinforcements and curses; Cantor is a boss with an area assault phase |
| Cindermaw Brood / Cindermaw | Ember-throated dark dragon | Brood bites and breathes; boss cycles armor, area breath, and a heavy hunter strike |

Atlas provenance is recorded in `public/art/PROVENANCE.json`, including generated originals, tool, hashes, and pending rights review before commercial distribution. The abbey background, two atlases, and pact insignia are local generated assets. Earlier concepts such as Ironback, Gravewing, Chain Revenant, and The Bellwrought were proposals and are not current roster entries. Expanding the roster requires a meaningful combat role and a consistent visual identity.

## Motion and interaction

The current Canvas 2D renderer moves painted cutouts and draws sigils, command lunges, directed strike traces, hit recoil, and short death fades/particles. This is transformed illustration feedback, not skeletal animation or simulated creature anatomy. Review that each effect points to the actual target and explains the outcome. Selection uses an arena sigil plus an HTML target state; never rely on glow alone. Reduced motion must keep outcome information readable while suppressing ambient movement and animated combat effects. Actual client behavior requires separate review.

Future rigged characters would require an explicit 3D pipeline, consistent geometry/materials, locomotion and attack rigs, performance budgets, provenance, and independent review. This is future work, not a feature implied by the current illustrated perspective. The current realistic style must be judged on visible anatomy, lighting, framing, consistency, and tactical readability, without an AAA claim.

## Review gates

Compare the preserved v0.1 and the candidate at the same desktop sizes and gameplay state. Inspect every core creature as a silhouette, in its card, and in the arena. Reject mismatched identities, hidden damage/intent, unreadable dark scenes, broken motion settings, or attacks with no visible target. Repeat at full six-unit occupancy and on a small viewport. Assess full enhanced card strings rather than one starter hand. Professional realism and purchase appeal remain unverified until the finished presentation is reviewed and prospective players respond to it.
