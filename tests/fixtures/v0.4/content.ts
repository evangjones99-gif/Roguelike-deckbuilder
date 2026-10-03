import type { CardDef } from "./engine";
const summon = (
  id: string,
  name: string,
  species: string,
  cost: number,
  hp: number,
  attack: number,
  effect: string,
  passive: string,
  text: string,
  color: string,
): CardDef => ({
  id,
  name,
  species,
  type: "summon",
  cost,
  hp,
  attack,
  effect,
  passive,
  text,
  color,
});
const spell = (
  id: string,
  name: string,
  cost: number,
  effect: string,
  value: number,
  text: string,
  color = "#bda580",
): CardDef => ({ id, name, type: "spell", cost, effect, value, text, color });
const HOUND = "Commands deal 2 extra damage to enemies with no block.";
const STALKER = "After a command deals damage, heal this creature 2 HP.";
const COLOSSUS = "After commanding this creature, gain 2 hunter block.";
const WIDOW =
  "Your targeted damaging spells deal 2 extra damage while this creature lives.";
const base: CardDef[] = [
  summon(
    "cairnhound",
    "Cairn Hound",
    "hound",
    1,
    7,
    3,
    "hunter-ward",
    HOUND,
    "Bind a spectral hound. On binding: gain 2 hunter block.",
    "#c4c6b5",
  ),
  summon(
    "gravehound",
    "Grave Hound",
    "hound",
    2,
    11,
    4,
    "draw",
    HOUND,
    "Bind a scarred grave hound. On binding: draw 1 card.",
    "#adaf9b",
  ),
  summon(
    "fenstalker",
    "Fen Stalker",
    "stalker",
    2,
    10,
    4,
    "none",
    STALKER,
    "Bind an amphibious corpse-stalker.",
    "#7f9386",
  ),
  summon(
    "fenraker",
    "Fen Raker",
    "stalker",
    3,
    14,
    6,
    "hunter-heal",
    STALKER,
    "Bind a veteran stalker. On binding: heal the hunter 2 HP.",
    "#79887a",
  ),
  summon(
    "briarcolossus",
    "Briar Colossus",
    "colossus",
    3,
    18,
    4,
    "none",
    COLOSSUS,
    "Bind a giant of bark, bone and iron.",
    "#8d8776",
  ),
  summon(
    "ossuarycolossus",
    "Ossuary Colossus",
    "colossus",
    4,
    24,
    6,
    "pack-ward",
    COLOSSUS,
    "Bind an ossuary giant. On binding: all creatures gain 3 block.",
    "#a39b88",
  ),
  summon(
    "ashwidow",
    "Ash Widow",
    "spider",
    2,
    7,
    2,
    "none",
    WIDOW,
    "Bind an ash-veined spider.",
    "#af816f",
  ),
  summon(
    "emberwidow",
    "Ember Widow",
    "spider",
    3,
    11,
    3,
    "enemy-burn",
    WIDOW,
    "Bind an ember-veined widow. On binding: deal 2 damage to every enemy.",
    "#bc8267",
  ),
  spell("scour", "Scour", 1, "damage", 6, "Deal 6 damage to an enemy."),
  spell(
    "ironward",
    "Iron Ward",
    1,
    "block",
    7,
    "Gain 7 hunter block.",
    "#aaaeb0",
  ),
  spell(
    "sutures",
    "Blood Sutures",
    1,
    "heal",
    6,
    "Heal a creature 6 HP and give it 2 block.",
    "#ac7367",
  ),
  spell(
    "edict",
    "Pack Edict",
    2,
    "rally",
    2,
    "All bound creatures gain 2 attack this battle.",
    "#a098b3",
  ),
  spell(
    "witchfire",
    "Witchfire",
    2,
    "aoe",
    4,
    "Deal 4 damage to every enemy.",
    "#b58463",
  ),
  spell(
    "killcommand",
    "Kill Command",
    1,
    "ready",
    2,
    "Ready a creature to command again; give it 2 block.",
    "#bda580",
  ),
  spell(
    "gravetithe",
    "Grave Tithe",
    2,
    "siphon",
    7,
    "Deal 7 damage to an enemy. Heal the hunter 3 HP.",
    "#a098b3",
  ),
  spell("survey", "Forbidden Survey", 1, "draw", 2, "Draw 2 cards.", "#bab8a6"),
  spell(
    "bloodprice",
    "Blood Price",
    0,
    "energy",
    1,
    "Gain 1 energy. Lose 3 hunter HP.",
    "#ac7367",
  ),
  spell(
    "aegis",
    "Black Aegis",
    2,
    "shelter",
    5,
    "Hunter and all bound creatures gain 5 block.",
    "#929e9b",
  ),
  spell(
    "harpoon",
    "Chain Harpoon",
    2,
    "pack",
    4,
    "Deal 4 damage plus 2 per bound creature to an enemy.",
    "#bab8a6",
  ),
  spell(
    "covenant",
    "Flesh Covenant",
    2,
    "communion",
    2,
    "Heal the hunter 2 HP per bound creature.",
    "#ac7367",
  ),
  spell(
    "sunder",
    "Sundering Hex",
    1,
    "shred",
    3,
    "Remove all block from an enemy, then deal 3 damage.",
    "#aaaeb0",
  ),
  spell(
    "silence",
    "Silence the Dead",
    2,
    "control",
    0,
    "Cancel an enemy's announced damage and reinforcements this turn. Armor still resolves.",
    "#a098b3",
  ),
  spell(
    "resonance",
    "Grave Resonance",
    2,
    "solo",
    10,
    "Deal 10 damage to an enemy. Deal 4 extra if you have no bound creatures.",
    "#a098b3",
  ),
  spell(
    "draught",
    "Bleak Draught",
    2,
    "hunterheal",
    7,
    "Heal the hunter 7 HP.",
    "#ac7367",
  ),
];
function upgradeText(c: CardDef): string {
  const v = (c.value ?? 0) + 2;
  const text: Record<string, string> = {
    damage: `Deal ${v} damage to an enemy.`,
    block: `Gain ${v} hunter block.`,
    heal: `Heal a creature ${v} HP and give it 2 block.`,
    rally: `All bound creatures gain ${v} attack this battle.`,
    aoe: `Deal ${v} damage to every enemy.`,
    ready: `Ready a creature to command again; give it ${v} block.`,
    siphon: `Deal ${v} damage to an enemy. Heal the hunter 3 HP.`,
    draw: `Draw ${v} cards.`,
    energy: `Gain ${v} energy. Lose 3 hunter HP.`,
    shelter: `Hunter and all bound creatures gain ${v} block.`,
    pack: `Deal ${v} damage plus 2 per bound creature to an enemy.`,
    communion: `Heal the hunter ${v} HP per bound creature.`,
    shred: `Remove all block from an enemy, then deal ${v} damage.`,
    control: c.text + " Enhanced: costs 1 energy.",
    solo: `Deal ${v} damage to an enemy. Deal 4 extra if you have no bound creatures.`,
    hunterheal: `Heal the hunter ${v} HP.`,
  };
  return text[c.effect!];
}
export const CARDS: Record<string, CardDef> = Object.fromEntries(
  base.flatMap((c) => [
    [c.id, c],
    [
      c.id + "+",
      {
        ...c,
        id: c.id + "+",
        name: c.name + " +",
        cost: c.effect === "control" ? 1 : c.cost,
        hp: c.hp === undefined ? undefined : c.hp + 3,
        attack: c.attack === undefined ? undefined : c.attack + 1,
        value: c.value === undefined ? undefined : c.value + 2,
        text:
          c.type === "summon"
            ? c.text + " Enhanced: +3 HP, +1 attack."
            : upgradeText(c),
      },
    ],
  ]),
);
export const BASE_CARD_IDS = base.map((c) => c.id);
export const STARTER_DECK = [
  "cairnhound",
  "cairnhound",
  "fenstalker",
  "ashwidow",
  "briarcolossus",
  "scour",
  "scour",
  "ironward",
  "ironward",
  "sutures",
  "sunder",
  "survey",
];
export const SHOP_PRICES = { summon: 55, spell: 40, remove: 35 };
export const RELICS: Record<string, { name: string; text: string }> = {
  "moon-charm": {
    name: "Wraithglass Shard",
    text: "All spell damage increases by 1.",
  },
  "ember-seed": {
    name: "Ossuary Nail",
    text: "Your bound creatures have 2 additional HP.",
  },
  "brass-bell": {
    name: "Black Contract Seal",
    text: "Gain 1 additional energy on the first turn of each battle.",
  },
  "blood-vial": {
    name: "Surgeon's Reliquary",
    text: "Heal the hunter 2 HP after every victory.",
  },
  "war-brand": {
    name: "Iron War Brand",
    text: "Your bound creatures gain 1 attack on binding.",
  },
  "grave-coin": {
    name: "Dead Man's Coin",
    text: "Gain 1 extra energy each turn that begins without bound creatures.",
  },
};
export const EVENT_CHOICES: Record<string, { name: string; text: string }> = {
  offering: {
    name: "Take the wraithglass oath",
    text: "Lose 8 HP. Receive Wraithglass Shard (+1 spell damage).",
  },
  forage: { name: "Strip the ruined armor", text: "Gain 25 gold." },
  purge: {
    name: "Burn an old contract",
    text: "Remove the first unenhanced Scour. Lose 4 HP. Requires at least six cards.",
  },
  bargain: { name: "Pay the surgeon", text: "Pay 30 gold. Recover 16 HP." },
  leave: { name: "Leave the crypt", text: "Continue without payment." },
};
export interface EnemyDef {
  name: string;
  species: string;
  hp: number;
  attack: number;
  color: string;
  passive?: string;
}
export const ENEMIES: Record<string, EnemyDef> = {
  raider: {
    name: "Ironjaw Reaver",
    species: "warlord",
    hp: 16,
    attack: 4,
    color: "#a6a59c",
    passive:
      "While armored, commands reflect 1 damage through creature block. Spells never trigger retaliation.",
  },
  revenant: {
    name: "Gloam Revenant",
    species: "wraith",
    hp: 15,
    attack: 5,
    color: "#8f9aab",
    passive:
      "Strikes ignore block. Targeted damaging spells deal 2 less damage to this enemy.",
  },
  acolyte: {
    name: "Hollow Acolyte",
    species: "necromancer",
    hp: 24,
    attack: 5,
    color: "#929085",
    passive:
      "Alternates raising one Bone Thrall and cursing the hunter. Six enemy slots limit reinforcements.",
  },
  brood: {
    name: "Cindermaw Brood",
    species: "dragon",
    hp: 28,
    attack: 6,
    color: "#ac7862",
    passive:
      "Alternates a bite at the front creature and a breath attack against all targets.",
  },
  thrall: {
    name: "Bone Thrall",
    species: "thrall",
    hp: 7,
    attack: 3,
    color: "#b2ac95",
    passive:
      "Attacks the weakest bound creature, or the hunter if none remain.",
  },
  ironjaw: {
    name: "Ironjaw Warlord",
    species: "warlord",
    hp: 112,
    attack: 9,
    color: "#a6a59c",
    passive:
      "While armored, commands reflect 2 damage through creature block. Use Sundering Hex or spells to break armor safely.",
  },
  cantor: {
    name: "Hollow Cantor",
    species: "necromancer",
    hp: 92,
    attack: 9,
    color: "#929085",
    passive:
      "Raises two Bone Thralls, curses the hunter, then assaults all targets. Silence cancels announced reinforcements.",
  },
  cindermaw: {
    name: "Cindermaw",
    species: "dragon",
    hp: 125,
    attack: 10,
    color: "#ac7862",
    passive:
      "Cycles armored wings, breath against all targets, then a heavy hunter strike. Prepare block before the breath.",
  },
};
export const BOSS_IDS = ["ironjaw", "cantor", "cindermaw"] as const;
/** Fixed from the run seed, so the player can plan for the final contract. */
export function bossForSeed(seed: number): string {
  return BOSS_IDS[(seed >>> 0) % BOSS_IDS.length];
}
