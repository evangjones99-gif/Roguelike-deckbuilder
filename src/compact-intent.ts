/** SOURCE-ONLY R3. Presentation data derived from frozen intentions/endTurn rules. */
import type { GameState, Unit } from './engine';

export interface CompactIntent {
  kind: 'attack' | 'guard' | 'raise' | 'silenced' | 'wait' | 'unknown';
  /** Render each line at >=12px/16px; never truncate or clamp essential lines. */
  lines: readonly string[];
  fullText: string;
  /** Geometry must reserve all rows, including compound loaded intents. */
  essentialRows: number;
}

function plannedGuard(unit: Unit, turn: number): number {
  if (unit.intent?.damage !== 0) return 0;
  if (unit.cardId === 'ironjaw' && turn % 2 === 1) return 14;
  if (unit.cardId === 'raider' && turn % 2 === 1) return 4;
  return unit.cardId === 'cindermaw' && turn % 3 === 1 ? 10 : 0;
}
function attackType(unit: Unit): string {
  switch (unit.cardId) {
    case 'thrall': return 'Claw';
    case 'raider': case 'ironjaw': return 'Cleave';
    case 'revenant': return 'Rend';
    case 'acolyte': return 'Curse';
    case 'brood': return unit.intent?.target === 'all' ? 'Breath' : 'Bite';
    case 'cantor': return unit.intent?.target === 'all' ? 'Tempest' : 'Litany';
    case 'cindermaw': return unit.intent?.target === 'all' ? 'Breath' : 'Maw';
    default: return 'Strike';
  }
}
/** Target identity is canonical array identity, never renderer slot/array order. */
export function compactIntent(state: GameState, unit: Unit): CompactIntent {
  const intent = unit.intent;
  const finish = (kind: CompactIntent['kind'], lines: string[], facts: string): CompactIntent =>
    Object.freeze({ kind, lines: Object.freeze(lines), essentialRows: lines.length,
      fullText: intent ? `${intent.label}. ${facts}` : facts });
  if (!intent) return finish('unknown', ['Intent unknown'], 'Intent unknown. Inspect this hostile.');
  const raised = intent.summon?.length ?? 0;
  const guard = plannedGuard(unit, state.turn);
  const silenced = /silenced/i.test(intent.label);
  const bindingIndex = state.allies.findIndex(ally => ally.uid === intent.target && ally.hp > 0);
  const target = bindingIndex >= 0 ? state.allies[bindingIndex] : undefined;
  const targetFull = intent.target === 'all' ? 'the hunter and every binding'
    : target ? `${target.name}, binding ${bindingIndex + 1}` : 'the hunter';
  if (intent.damage > 0) {
    const lines = [`${attackType(unit)} ${intent.damage}`];
    if (intent.target === 'all') lines.push('Hunter + all', 'bindings');
    else lines.push(target ? `→ Binding ${bindingIndex + 1}` : '→ Hunter');
    // endTurn's area branch never bypasses block. The single-target branch uses cardId.
    const bypass = unit.cardId === 'revenant' && intent.target !== 'all';
    if (bypass) lines.push('Ignores block');
    if (raised) lines.push(`+ ${raised} thrall${raised === 1 ? '' : 's'}`);
    return finish('attack', lines, `${intent.damage} damage to ${targetFull}${bypass ? ', ignoring block' : ''}.` +
      (target ? ' If that binding falls before this intent, the hit redirects to the hunter.' : '') +
      (raised ? ` Raises ${raised} Bone Thrall${raised === 1 ? '' : 's'} after the enemy phase if the hunter survives, within the six-hostile limit.` : ''));
  }
  const lines: string[] = [];
  if (guard) lines.push(`Guard ${guard}`, 'Self');
  if (raised) lines.push(`Raise ${raised} thrall${raised === 1 ? '' : 's'}`, 'Enemy side');
  if (silenced) lines.push('Silenced');
  if (!guard && !raised) {
    if (silenced) lines.push('No damage', 'No thralls');
    else lines.push('No attack');
  }
  return finish(guard ? 'guard' : raised ? 'raise' : silenced ? 'silenced' : 'wait', lines,
    `No attack damage.${guard ? ` Gains ${guard} block on this hostile; armor remains when silenced.` : ''}` +
    (raised ? ` Raises ${raised} Bone Thrall${raised === 1 ? '' : 's'} after the enemy phase if the hunter survives, within the six-hostile limit.` : ' No reinforcements.'));
}
