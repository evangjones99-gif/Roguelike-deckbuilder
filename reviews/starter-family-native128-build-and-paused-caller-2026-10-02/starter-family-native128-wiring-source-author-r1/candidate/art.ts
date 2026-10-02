/** Local, original generated artwork. Atlases are sampled; originals stay intact. */
export const ARENA_ART = {
  crypt: `${import.meta.env.BASE_URL}art/ossuary-crypt-v08-r2.png`,
  courtyard: `${import.meta.env.BASE_URL}art/abbey-courtyard.png`,
  companions: `${import.meta.env.BASE_URL}art/companions-atlas.png`,
  adversaries: `${import.meta.env.BASE_URL}art/adversaries-atlas.png`,
} as const;

export interface PortraitArt {
  url: string;
  column: number;
  row: number;
  columns: number;
  rows: number;
  /** Per-asset face framing; original body pixels are unchanged. */
  focal?: readonly [number, number];
}

export function portraitFor(species: string): PortraitArt | null {
  const name = species.toLowerCase();
  if (name === 'thrall') return { url: `${import.meta.env.BASE_URL}art/bone-thrall-v09-r1.png`, column: 0, row: 0, columns: 1, rows: 1, focal: [65, 13] };
  let url: string = ARENA_ART.companions;
  let column = 0;
  let row = 0;
  if (/warlord|imp|brute/.test(name)) url = ARENA_ART.adversaries;
  else if (/necromancer|witch/.test(name)) { url = ARENA_ART.adversaries; column = 1; }
  else if (/wraith|thrall|wisp|ghost/.test(name)) { url = ARENA_ART.adversaries; row = 1; }
  else if (/dragon|crown/.test(name)) { url = ARENA_ART.adversaries; column = 1; row = 1; }
  else if (/spider/.test(name)) { column = 1; row = 1; }
  else if (/colossus|sentinel|golem|stag|turtle/.test(name)) row = 1;
  else if (/stalker|reed|moth|rook|owl/.test(name)) column = 1;
  else if (!/hound|wolf|fox|moss|cat|otter|hare/.test(name)) return null;
  return { url, column, row, columns: 2, rows: 2 };
}

/** An extensible pose-sheet contract, independent of rule state and rendering. */
export type CreaturePose = 'idle' | 'anticipation' | 'attack' | 'recovery' | 'reaction' | 'death';
export interface CreaturePoseFrame {
  column: number;
  row: number;
  /** A pose may contain several painted frames; single-frame poses hold. */
  holdMs?: number;
  /** Authored contact landmark in fractions of the whole source cell. */
  contactTip?: { x: number; y: number };
  anchorX?: number;
  anchorY?: number;
  scale?: number;
  /** Painted apparent elevation; do not apply it as extra body translation. */
  ground?: { altitude: number; footprint: number; contact: number };
  /** Fractions of one grid cell; source sampling preserves original pixels. */
  crop?: { x: number; y: number; width: number; height: number };
}
export interface CreatureAnimationAtlas {
  url: string;
  columns: number;
  rows: number;
  anchorX: number;
  anchorY: number;
  poses: Partial<Record<CreaturePose, readonly CreaturePoseFrame[]>>;
  /** Pose-specific painted-frame dissolve duration; zero gives a solid cel cut. */
  blendMs?: Partial<Record<CreaturePose, number>>;
}
export interface CreatureSequenceStep { pose: CreaturePose; durationMs: number }
export const CREATURE_ATTACK_SEQUENCE: readonly CreatureSequenceStep[] = [
  { pose: 'anticipation', durationMs: 140 },
  { pose: 'attack', durationMs: 180 },
  { pose: 'recovery', durationMs: 260 },
];
export const CREATURE_IMPACT_MS = 240;
export const CREATURE_REACTION_MS = 220;
export const CREATURE_DEATH_MS = 900;

export const HOUND_POSES: CreatureAnimationAtlas = {
  url: `${import.meta.env.BASE_URL}art/hound-poses.png`,
  columns: 3, rows: 2,
  anchorX: .5, anchorY: .94,
  // Sparse painted poses stay solid; a dissolve creates doubled anatomy.
  blendMs: { idle: 0, anticipation: 0, attack: 0, recovery: 0, reaction: 0, death: 0 },
  poses: {
    idle: [{ column: 0, row: 0, anchorY: (446 - 96) / 384, scale: 1.1, crop: { x: 32 / 512, y: 96 / 512, width: 448 / 512, height: 384 / 512 } }],
    anticipation: [{ column: 1, row: 0, anchorY: (440 - 96) / 384, scale: 1.1, crop: { x: 32 / 512, y: 96 / 512, width: 448 / 512, height: 384 / 512 } }],
    attack: [{ column: 2, row: 0, contactTip: { x: 432 / 512, y: 255 / 512 }, ground: { altitude: 28 / 384 * 1.1, footprint: 1.12, contact: .68 }, anchorY: (446 - 96) / 384, scale: 1.1, crop: { x: 32 / 512, y: 96 / 512, width: 448 / 512, height: 384 / 512 } }],
    recovery: [{ column: 0, row: 1, anchorY: (400 - 96) / 384, scale: 1.1, crop: { x: 32 / 512, y: 96 / 512, width: 448 / 512, height: 384 / 512 } }],
    reaction: [{ column: 1, row: 1, anchorY: (394 - 96) / 384, scale: 1.1, crop: { x: 32 / 512, y: 96 / 512, width: 448 / 512, height: 384 / 512 } }],
    death: [{ column: 2, row: 1, anchorY: (397 - 96) / 384, scale: 1.1, crop: { x: 32 / 512, y: 96 / 512, width: 448 / 512, height: 384 / 512 } }],
  },
};

const warleaderCrop = { x: 0, y: 32 / 512, width: 1, height: 448 / 512 };
export const WARLEADER_POSES: CreatureAnimationAtlas = {
  url: `${import.meta.env.BASE_URL}art/warleader-poses.png`,
  columns: 3, rows: 2, anchorX: .5, anchorY: (474 - 32) / 448,
  blendMs: { idle: 0, anticipation: 0, attack: 0, recovery: 0, reaction: 0, death: 0 },
  poses: {
    idle: [{ column: 0, row: 0, anchorY: (474 - 32) / 448, scale: 1.1, crop: warleaderCrop }],
    anticipation: [{ column: 1, row: 0, anchorY: (473 - 32) / 448, scale: 1.1, crop: warleaderCrop }],
    attack: [{ column: 2, row: 0, anchorY: (476 - 32) / 448, scale: 1.1, crop: warleaderCrop }],
    recovery: [{ column: 0, row: 1, anchorY: (406 - 32) / 448, scale: 1.1, crop: warleaderCrop }],
    reaction: [{ column: 1, row: 1, anchorY: (405 - 32) / 448, scale: 1.1, crop: warleaderCrop }],
    // Anchor the gauntlet/body contact plane, rather than the lower blade tip.
    death: [{ column: 2, row: 1, anchorY: (406 - 32) / 448, scale: 1.1, crop: warleaderCrop }],
  },
};

/** More species can acquire pose sheets without changes to the pure engine. */
export function animationFor(species: string): CreatureAnimationAtlas | null {
  const name = species.toLowerCase();
  if (/hound/.test(name)) return HOUND_POSES;
  return /warlord/.test(name) ? WARLEADER_POSES : null;
}

/** Four shared equipment families. Crops sample an unchanged original sheet. */
export type ToolArtFamily = 'hook' | 'plate' | 'sewing' | 'pack';
export interface ToolArtWindow { rect: readonly [number, number, number, number]; anchor: readonly [number, number] }
export const TOOL_ART_URL = `${import.meta.env.BASE_URL}art/tool-vignettes.png`;
export const TOOL_ART_WINDOWS: Record<ToolArtFamily, { large: ToolArtWindow; hand: ToolArtWindow }> = {
  hook: { large: { rect: [2, 2, 883, 439.5], anchor: [.5, .5] }, hand: { rect: [2, 170, 610, 240], anchor: [.5, 1] } },
  plate: { large: { rect: [889, 2, 883, 439.5], anchor: [.5, .5] }, hand: { rect: [957, 45, 575, 355], anchor: [.5, .48] } },
  sewing: { large: { rect: [2, 445.5, 883, 439.5], anchor: [.5, .5] }, hand: { rect: [130, 538.5, 620, 270], anchor: [.5, .7] } },
  pack: { large: { rect: [889, 445.5, 883, 439.5], anchor: [.5, .5] }, hand: { rect: [889, 445.5, 883, 439.5], anchor: [.5, .81] } },
};
const toolFamilies: Record<string, ToolArtFamily> = { scour: 'hook', harpoon: 'hook', ironward: 'plate', aegis: 'plate', sutures: 'sewing', edict: 'pack' };
export function toolArtFor(cardId: string): ToolArtFamily | null {
  return toolFamilies[cardId.replace(/\+$/, '')] ?? null;
}

/** Unselected static native128 reference trial; no pose/attack animation contract. */
export const COHERENT_NATIVE128 = {"manifest":"coherent-native128-manual-crop-view-manifest.json","manifestSha256":"1e0699b76dc3543b5374df5ff8e33aa81254c6d05c94fe7483247d183308b8af","palette":["#11151d","#23313b","#3c515b","#667e82","#9aa8a1","#c5c8ac","#e7ddba","#483931","#735548","#a47b55","#d4ad6c","#632f37","#a5544a","#367e82","#72beb6"],"sprites":[{"name":"cairn-hound-rear-three-quarter","category":"body","intended_view":"rear three-quarter ally","filename":"cairn-hound-rear-three-quarter-manual-crop-native128-draft.png","sha256":"fac6409c4218db7984c25c51abc9adb9aec870e1e20df52939171e700cb2829e","native_dimensions":[128,128],"native_bounds":[12,19,116,120],"ground_anchor":[64,120],"mirror":false},{"name":"ironjaw-reaver-front-three-quarter","category":"body","intended_view":"front three-quarter enemy","filename":"ironjaw-reaver-front-three-quarter-manual-crop-native128-draft.png","sha256":"90badaa9e35a71f849947a7c45970c19db8f5163eb36aa3370df89631e818f32","native_dimensions":[128,128],"native_bounds":[8,13,120,120],"ground_anchor":[64,120],"mirror":false},{"name":"gloam-revenant-front-three-quarter","category":"body","intended_view":"front three-quarter enemy","filename":"gloam-revenant-front-three-quarter-manual-crop-native128-draft.png","sha256":"6434bdf7ebd56dd67d2032a1d078164467ac4a1d44bf9037dd7f9e1a374b53e7","native_dimensions":[128,128],"native_bounds":[19,16,109,120],"ground_anchor":[64,120],"mirror":false},{"name":"marek-hunter-rear-three-quarter","category":"body","intended_view":"rear three-quarter hunter","filename":"marek-hunter-rear-three-quarter-manual-crop-native128-draft.png","sha256":"7c1f0d50e6db26b03d8eb17969b5858319463e60067cb4d9473abbe2a5adc2f9","native_dimensions":[128,128],"native_bounds":[10,14,118,120],"ground_anchor":[64,120],"mirror":false},{"name":"cairn-hound-front-portrait","category":"portrait","intended_view":"front head/chest","filename":"cairn-hound-front-portrait-manual-crop-native128-draft.png","sha256":"c53064c273e91b43eb49b8dba508b069af42d3d05b80644694e4591136ee1021","native_dimensions":[128,128],"native_bounds":[9,8,119,120],"ground_anchor":[64,120],"mirror":false},{"name":"marek-hunter-front-portrait","category":"portrait","intended_view":"front head/chest","filename":"marek-hunter-front-portrait-manual-crop-native128-draft.png","sha256":"a1ab99f2c559b02ac1bd4767327fe098908b7c703da085f8d5cddb7fc7977d1c","native_dimensions":[128,128],"native_bounds":[8,19,120,120],"ground_anchor":[64,120],"mirror":false},{"name":"ironjaw-reaver-fallen-grounded","category":"body","intended_view":"fallen enemy corpse, static","filename":"ironjaw-reaver-fallen-grounded-native128-draft.png","sha256":"68b7858fa43a285a6b1bbc5d7daf4bac55cb189ec051fa9d52353d91b77db2e2","native_dimensions":[128,128],"native_bounds":[8,61,119,120],"ground_anchor":[64,120],"mirror":false},{"name":"ash-widow-correction-rear-three-quarter","category":"body","intended_view":"rear three-quarter requested; visible head/eight legs pending native visual review","filename":"ash-widow-correction-rear-three-quarter-manual-crop-native128-draft.png","sha256":"e02e10cb6b02404b87d22053321e3b0268fa6729c09f6d4b3df3bedc6eb9d462","native_dimensions":[128,128],"native_bounds":[8,43,120,120],"ground_anchor":[64,120],"mirror":false},{"name":"ash-widow-correction-front-portrait","category":"portrait","intended_view":"front portrait requested; eight legs/head identity pending native visual review","filename":"ash-widow-correction-front-portrait-manual-crop-native128-draft.png","sha256":"21bead977286b45053242fb8b37d225838e2d78b448e22d1b2a8373a61f72a8d","native_dimensions":[128,128],"native_bounds":[8,41,119,120],"ground_anchor":[64,120],"mirror":false},{"name":"fen-stalker-rear-three-quarter","category":"body","intended_view":"requested rear three-quarter amphibious ally; facing pending","filename":"fen-stalker-rear-three-quarter-manual-crop-native128-draft.png","sha256":"fffd1824d6872a022b45b2dfe56ff08061d774c59836e587db605cc7b96fa263","native_dimensions":[128,128],"native_bounds":[12,32,115,120],"ground_anchor":[64,120],"mirror":false},{"name":"fen-stalker-front-portrait","category":"portrait","intended_view":"front head/chest","filename":"fen-stalker-front-portrait-manual-crop-native128-draft.png","sha256":"a39d0f56f3c7f46278a99f5d80290fad9ab9ee9ddf93c93df2c9c311843bdb52","native_dimensions":[128,128],"native_bounds":[8,12,120,120],"ground_anchor":[64,120],"mirror":false},{"name":"briar-colossus-rear-three-quarter","category":"body","intended_view":"requested rear three-quarter bark/bone ally","filename":"briar-colossus-rear-three-quarter-manual-crop-native128-draft.png","sha256":"2a87f31ed0b7e9e6156a776100e994d7b467c522d36bffb7769e1fce895f5f4f","native_dimensions":[128,128],"native_bounds":[17,8,111,120],"ground_anchor":[64,120],"mirror":false},{"name":"briar-colossus-front-portrait","category":"portrait","intended_view":"front head/chest","filename":"briar-colossus-front-portrait-manual-crop-native128-draft.png","sha256":"4ff2356ad27ee3f23d227743c2d79b1fe16e083ec02f205448a953599ab48275","native_dimensions":[128,128],"native_bounds":[14,8,113,120],"ground_anchor":[64,120],"mirror":false}]} as const;
