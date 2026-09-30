/** Local, original generated artwork. Atlases are sampled; originals stay intact. */
export const ARENA_ART = {
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
}

export function portraitFor(species: string): PortraitArt | null {
  const name = species.toLowerCase();
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
  anchorX?: number;
  anchorY?: number;
  scale?: number;
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
  poses: {
    idle: [{ column: 0, row: 0, anchorY: (446 - 96) / 384, scale: 1.1, crop: { x: 32 / 512, y: 96 / 512, width: 448 / 512, height: 384 / 512 } }],
    anticipation: [{ column: 1, row: 0, anchorY: (440 - 96) / 384, scale: 1.1, crop: { x: 32 / 512, y: 96 / 512, width: 448 / 512, height: 384 / 512 } }],
    attack: [{ column: 2, row: 0, anchorY: (446 - 96) / 384, scale: 1.1, crop: { x: 32 / 512, y: 96 / 512, width: 448 / 512, height: 384 / 512 } }],
    recovery: [{ column: 0, row: 1, anchorY: (400 - 96) / 384, scale: 1.1, crop: { x: 32 / 512, y: 96 / 512, width: 448 / 512, height: 384 / 512 } }],
    reaction: [{ column: 1, row: 1, anchorY: (394 - 96) / 384, scale: 1.1, crop: { x: 32 / 512, y: 96 / 512, width: 448 / 512, height: 384 / 512 } }],
    death: [{ column: 2, row: 1, anchorY: (397 - 96) / 384, scale: 1.1, crop: { x: 32 / 512, y: 96 / 512, width: 448 / 512, height: 384 / 512 } }],
  },
};

/** More species can acquire pose sheets without changes to the pure engine. */
export function animationFor(species: string): CreatureAnimationAtlas | null {
  return /hound/.test(species.toLowerCase()) ? HOUND_POSES : null;
}
