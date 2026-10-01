function renderEvent() {
  const symbols: Record<string, string> = { offering: 'moon', forage: 'gold', purge: 'battle', bargain: 'heart', leave: 'shield' };
  const recovery = Math.min(16, state.maxHp - state.hp);
  const consequences: Record<string, string> = { offering: `${state.hp} → ${state.hp - 8} health`, forage: `${state.gold} → ${state.gold + 25} gold`, purge: `${state.deck.length} → ${state.deck.length - 1} cards · lose 4 health`, bargain: `${state.gold} → ${state.gold - 30} gold · +${recovery} health`, leave: 'Continue unchanged' };
  const unavailable: Record<string, string> = {
    offering: state.relics.includes('moon-charm') ? 'Wraithglass Shard already owned' : 'Requires at least 9 health',
    purge: state.hp <= 4 ? 'Requires at least 5 health' : state.deck.length <= 5 ? 'Keep at least 5 cards' : 'No unenhanced Scour to remove',
    bargain: state.gold < 30 ? 'Requires 30 gold' : 'Already at full health',
  };
  $('scene-ui').innerHTML = `<div class="page-panel event-panel"><div class="page-intro"><span class="eyebrow">A SHRINE WITHOUT A GOD</span><h1>Some bargains outlive their makers.</h1><p>Read the price. Claim only what your campaign needs.</p></div><div class="choice-grid event-choices">${Object.entries(EVENT_CHOICES).map(([id, choice]) => {
    const available = can({ type: 'event', choice: id });
    return `<button class="choice-card" data-action="event" data-choice="${id}" ${available ? '' : 'disabled'}>${icon(symbols[id])}<h2>${escape(choice.name)}</h2><p>${escape(choice.text)}</p><span>${escape(available ? consequences[id] || '' : unavailable[id] || 'Unavailable')}${available ? icon('arrow') : ''}</span></button>`;
  }).join('')}</div></div>`;
}
