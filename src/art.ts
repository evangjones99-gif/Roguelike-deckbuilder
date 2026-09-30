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
