import type { GameState } from './engine';
import { ENEMIES, bossForSeed } from './content';
import { worldFormation } from './world-rng';

export type EncounterEnvironment = 'courtyard' | 'crypt';

/** Pure presentation lookup: reconstruct the original kind2 formation without
 * consuming a stream, reading casualties, or adding anything to the save. */
export function encounterEnvironment(state: GameState): EncounterEnvironment | null {
  if (!['battle', 'reward', 'victory', 'defeat'].includes(state.phase)) return null;
  const kind = state.phase === 'victory' ? 'boss' : state.route[0];
  if (kind !== 'battle' && kind !== 'elite' && kind !== 'boss') return 'courtyard';
  // Legacy encounters used the shared mutable RNG. Their original normal/elite
  // formation is not recoverable from a surviving roster. Use a stable abbey;
  // the seed-defined boss remains reconstructible in either generation.
  if (state.schema === 2 && kind !== 'boss') return 'courtyard';
  const original = kind === 'boss' ? [bossForSeed(state.seed)]
    : worldFormation({ seed: state.seed, node: state.floor, kind });
  const species = original.map(id => ENEMIES[id].species);
  return species.includes('necromancer') ||
    (species.length > 0 && species.every(name => name === 'wraith' || name === 'thrall'))
    ? 'crypt' : 'courtyard';
}
