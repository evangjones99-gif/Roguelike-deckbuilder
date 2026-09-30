import './style.css';
import packageInfo from '../package.json';
import { applyAction, createGame, CARDS, legalActions, validateState, cardTarget, type GameState, type Action, type CardDef } from './engine';
import { createArena } from './arena';

const SAVE_KEY = 'lanternbound.run.v1';
const SETTINGS_KEY = 'lanternbound.settings.v1';
const TUTORIAL_KEY = 'lanternbound.tutorial.v1';
const VERSION = packageInfo.version;
type Selection = { kind: 'attack'; uid: string } | { kind: 'card'; index: number } | null;
type Settings = { mute: boolean; volume: number; motion: boolean };
const $ = <T extends HTMLElement>(id: string) => document.getElementById(id) as T;
const escape = (s: string | number) => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]!));
let state = createGame(Date.now() >>> 0);
let title = true;
let selected: Selection = null;
let savedRun: GameState | null = null;
let saveNotice = '';
let toastTimeout: ReturnType<typeof setTimeout>;
let settings: Settings = { mute: false, volume: .25, motion: !window.matchMedia('(prefers-reduced-motion: reduce)').matches };
try {
  const stored = localStorage.getItem(SETTINGS_KEY);
  if (stored) {
    const value = JSON.parse(stored);
    if (typeof value.mute === 'boolean' && typeof value.volume === 'number' && Number.isFinite(value.volume) && typeof value.motion === 'boolean') settings = { mute: value.mute, volume: Math.max(0, Math.min(1, value.volume)), motion: value.motion };
  }
  const save = localStorage.getItem(SAVE_KEY);
  if (save) {
    const value: unknown = JSON.parse(save);
    if (validateState(value)) { savedRun = value as GameState; state = savedRun; }
    else saveNotice = 'An incompatible save was found. Start a fresh trail to continue.';
  }
} catch { saveNotice = 'Your save could not be read. A fresh trail is still available.'; }

const icons: Record<string, string> = {
  lantern: '<path d="M9 5V3h6v2M7 8h10l2 11H5L7 8ZM8 8V5h8v3M9 21h6M12 10v6M10 14h4"/>',
  heart: '<path d="M12 20 3.7 12A5.2 5.2 0 0 1 12 5a5.2 5.2 0 0 1 8.3 7L12 20Z"/>',
  shield: '<path d="m12 3 8 3v6c0 4-4 7-8 9-4-2-8-5-8-9V6l8-3Z"/>',
  energy: '<path d="m13 2-9 12h7l-1 8 10-13h-7l0-7Z"/>',
  gold: '<circle cx="12" cy="12" r="8"/><path d="M12 7v10M15 8h-4a2 2 0 0 0 0 4h2a2 2 0 0 1 0 4H9"/>',
  book: '<path d="M12 5v15M12 6C8 3 5 3 2 4v15c3-1 6-1 10 1 4-2 7-2 10-1V4c-3-1-6-1-10 2Z"/>',
  settings: '<path d="m9 3-1 3-3 1v4l-2 2 2 3v3l4 1 3 2 3-2 4-1v-3l2-3-2-2V7l-3-1-1-3H9Z"/><circle cx="12" cy="12" r="3"/>',
  arrow: '<path d="M4 12h16m-6-6 6 6-6 6"/>',
  camp: '<path d="m12 3 10 17H2L12 3Zm0 7-5 10m5-10 5 10M8 3l8 17M16 3 8 20"/>',
  battle: '<path d="m4 3 3 1 13 13-3 3L4 7V3Zm16 0-3 1L4 17l3 3L20 7V3ZM3 16l5 5m8 0 5-5"/>',
  elite: '<path d="m3 6 4 3 5-6 5 6 4-3-3 13H6L3 6ZM7 21h10"/>',
  shop: '<path d="M4 8h16l-2-5H6L4 8ZM5 8v12h14V8M9 20v-8h6v8"/>',
  event: '<path d="M5 4c4-2 10-2 14 0l-1 16c-4 2-8 2-12 0L5 4Zm6 5a2 2 0 1 1 3 2c-1 0-2 1-2 3m0 3h.01"/>',
  boss: '<path d="M4 8 2 3l6 4m12 1 2-5-6 4M6 8c-4 3-2 11 6 13 8-2 10-10 6-13H6ZM8 12l2 2m6-2-2 2M9 18h6"/>',
  close: '<path d="m6 6 12 12M18 6 6 18"/>',
  check: '<path d="m5 12 4 4L19 6"/>',
  sound: '<path d="M3 9h4l5-5v16l-5-5H3V9Zm13-2c3 3 3 7 0 10m3-13c5 5 5 11 0 16"/>',
  moon: '<path d="M20 15A9 9 0 0 1 9 3c-8 2-9 14-2 17 5 3 11 0 13-5Z"/>',
};
const icon = (name: string, cls = '') => `<svg class="icon ${cls}" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">${icons[name] || icons.lantern}</svg>`;

function creature(species = 'spirit', color = '#91bba7'): string {
  let drawing: string;
  if (/fox|wolf|hound/i.test(species)) drawing = '<path d="m17 29-3-19 17 10 17-10-3 19c8 7 8 20-14 28-22-8-22-21-14-28Z"/><path d="m21 32 8 4m12-4-8 4m-5 10h6l-3 5-3-5Z"/>';
  else if (/deer|stag/i.test(species)) drawing = '<path d="M22 27 18 16 8 11m10 5-1-9m23 20 4-11 10-5m-10 5 1-9M20 27h22l-3 24-8 8-8-8-3-24Z"/><path d="m25 36 3 2m9-2-3 2m-6 11h6"/>';
  else if (/bird|owl|raven|crow/i.test(species)) drawing = '<path d="m15 21-3-12 13 7h14l13-7-3 12c10 25-1 35-17 38-16-3-27-13-17-38Z"/><circle cx="23" cy="30" r="7"/><circle cx="41" cy="30" r="7"/><path d="m28 41 4 6 4-6m-15 10 11 5 11-5"/>';
  else if (/mushroom|fung|moss|sprite/i.test(species)) drawing = '<path d="M9 31c0-27 46-27 46 0H9Zm17 0-4 24c5 5 15 5 20 0l-4-24"/><circle cx="23" cy="20" r="3"/><circle cx="41" cy="23" r="4"/><path d="M28 43v2m8-2v2m-6 5h4"/>';
  else if (/bear|badger/i.test(species)) drawing = '<circle cx="15" cy="16" r="7"/><circle cx="49" cy="16" r="7"/><path d="M13 22c0-17 38-17 38 0v18c0 22-38 22-38 0V22Z"/><path d="M23 32h3m12 0h3m-16 10h14l-7 9-7-9Z"/>';
  else drawing = '<path d="M12 40c-2-17 10-30 20-30s22 13 20 30l6 15-15-4-11 8-11-8-15 4 6-15Z"/><path d="M23 31v5m18-5v5m-13 7 4 3 4-3"/>';
  return `<svg class="creature-glyph" viewBox="0 0 64 64" aria-hidden="true" style="--creature:${escape(color)}" fill="none" stroke="currentColor" stroke-width="2.3" stroke-linejoin="round" stroke-linecap="round">${drawing}</svg>`;
}

let arena: ReturnType<typeof createArena> | null = null;
try { arena = createArena($<HTMLCanvasElement>('arena')); }
catch { $('arena-wrap').classList.add('arena-fallback'); }
window.addEventListener('resize', () => arena?.resize());

let audio: AudioContext | null = null;
function sound(kind: 'click' | 'summon' | 'attack' | 'reward' | 'end' = 'click') {
  if (settings.mute || settings.volume <= 0) return;
  try {
    audio ||= new AudioContext();
    void audio.resume();
    const notes = kind === 'summon' ? [220, 330, 440] : kind === 'reward' ? [392, 494, 587] : kind === 'attack' ? [130, 90] : kind === 'end' ? [220, 165] : [440];
    notes.forEach((note, i) => {
      const osc = audio!.createOscillator();
      const gain = audio!.createGain();
      const start = audio!.currentTime + i * .075;
      osc.type = kind === 'attack' ? 'triangle' : 'sine';
      osc.frequency.setValueAtTime(note, start);
      gain.gain.setValueAtTime(0, start);
      gain.gain.linearRampToValueAtTime(settings.volume * .18, start + .012);
      gain.gain.exponentialRampToValueAtTime(.001, start + .25);
      osc.connect(gain); gain.connect(audio!.destination);
      osc.start(start); osc.stop(start + .26);
    });
  } catch { /* Sound is optional; rules never depend on audio support. */ }
}
function setMotion() {
  document.documentElement.classList.toggle('reduced-motion', !settings.motion);
  // Arena also respects this preference via the document attribute.
  document.documentElement.dataset.reducedMotion = String(!settings.motion);
}
function notify(text: string) {
  clearTimeout(toastTimeout);
  $('toast').textContent = text;
  $('toast').classList.add('visible');
  toastTimeout = setTimeout(() => $('toast').classList.remove('visible'), 4000);
}
function save() {
  savedRun = state;
  try { localStorage.setItem(SAVE_KEY, JSON.stringify(state)); }
  catch { notify('This browser cannot store your trail. Keep this window open to continue.'); }
}
function actions(): Action[] { return legalActions(state); }
function can(action: Action): boolean { return actions().some(a => JSON.stringify(a) === JSON.stringify(action)); }
function dispatch(action: Action) {
  const previous = state;
  const next = applyAction(state, action);
  if (JSON.stringify(next) === JSON.stringify(previous)) { notify('That action is not available right now.'); return; }
  state = next;
  selected = null;
  if (action.type === 'play') sound(CARDS[previous.hand[action.index]]?.type === 'summon' ? 'summon' : 'attack');
  else if (action.type === 'attack') sound('attack');
  else if (action.type === 'reward' || action.type === 'buy') sound('reward');
  else if (action.type === 'endTurn') sound('end');
  else sound();
  save(); render();
  $('announcer').textContent = `${state.log[state.log.length - 1] || 'Choice made.'} ${state.phase === 'battle' ? `${state.energy} energy left. Hunter health ${state.hp} of ${state.maxHp}.` : ''}`;
  if (previous.phase === 'battle' && state.phase === 'reward') notify('The clearing is safe. Choose a new card, or keep your deck focused.');
}
function start(seed: number, difficulty: number) {
  state = createGame(seed, difficulty);
  title = false; selected = null; save(); render(); sound('summon');
  try { if (!localStorage.getItem(TUTORIAL_KEY)) openTutorial(); } catch { openTutorial(); }
}
function parseSeed(input: string): number {
  if (/^\d+$/.test(input.trim())) return Number(input) >>> 0;
  let hash = 2166136261;
  for (const char of input.trim() || String(Date.now())) hash = Math.imul(hash ^ char.charCodeAt(0), 16777619);
  return hash >>> 0;
}

function renderHeader() {
  $('topbar').innerHTML = `<button class="wordmark" data-ui="home" aria-label="Lanternbound main menu">${icon('lantern')}<span>LANTERNBOUND<small>A WOODLAND DECKBUILDING ADVENTURE</small></span></button><nav aria-label="Game tools"><button class="nav-button" data-ui="deck" aria-label="Deck">${icon('book')}<span>Deck${title ? '' : ` <span class="subtle">${state.deck.length}</span>`}</span></button><button class="nav-button" data-ui="help" aria-label="How to play"><span class="help-symbol">?</span><span>How to play</span></button><button class="icon-button" data-ui="settings" aria-label="Settings">${icon('settings')}</button></nav>`;
}
function renderHud() {
  $('hud').hidden = title;
  if (title) { $('hud').innerHTML = ''; return; }
  $('hud').innerHTML = `<div class="hunter-hud ${isTarget('hunter') ? 'valid-target' : ''}"><button class="hunter-icon" data-unit="hunter" aria-label="Hunter: ${state.hp} of ${state.maxHp} health${isTarget('hunter') ? ', select as target' : ''}">${icon('lantern')}</button><div class="hunter-health"><div><strong>The lantern keeper</strong><span>${icon('heart')} ${state.hp}<small> / ${state.maxHp}</small></span></div><div class="health-track"><i style="width:${state.hp / state.maxHp * 100}%"></i></div></div>${state.block > 0 ? `<span class="block-count">${icon('shield')}${state.block}<small>Block</small></span>` : ''}</div><div class="journey-hud"><span class="eyebrow">${state.phase === 'battle' ? 'WOODLAND CONTRACT' : 'YOUR JOURNEY'}</span><strong>Clearing ${(state.phase === 'map' ? state.floor + 1 : state.floor)} <span class="subtle">/ 10</span>${state.phase === 'battle' ? `<span class="turn-label">Turn ${state.turn}</span>` : ''}</strong></div><div class="resources"><span class="resource gold">${icon('gold')}<strong>${state.gold}</strong><small>Gold</small></span>${state.phase === 'battle' ? `<span class="resource energy">${icon('energy')}<strong>${state.energy}</strong><small>Energy</small></span>` : `<span class="resource relic">${icon('moon')}<strong>${state.relics.length}</strong><small>Charms</small></span>`}</div>`;
}
function render() {
  const focusKey = document.activeElement instanceof HTMLElement ? document.activeElement.dataset.focus : undefined;
  setMotion();
  $('app').className = title ? 'on-title' : `phase-${state.phase}`;
  renderHeader(); renderHud();
  $('dock').hidden = title || state.phase !== 'battle';
  $('arena-wrap').classList.toggle('muted-arena', title || state.phase !== 'battle');
  if (title) renderTitle();
  else if (state.phase === 'battle') renderBattle();
  else if (state.phase === 'map') renderMap();
  else if (state.phase === 'reward') renderRewards();
  else if (state.phase === 'camp') renderCamp();
  else if (state.phase === 'shop') renderShop();
  else if (state.phase === 'event') renderEvent();
  else renderOutcome();
  $('footer').innerHTML = `<span>v${VERSION} <span class="footer-dot">·</span> Playable prototype</span><span>${title ? 'Made for quiet evenings & brave little choices' : `Seed ${state.seed} <span class="footer-dot">·</span> Trail saved locally`}</span><button data-ui="fullscreen" class="text-button">Fullscreen</button>`;
  arena?.setSelected(selected?.kind === 'attack' ? selected.uid : null);
  arena?.render(state);
  if (focusKey) document.querySelector<HTMLElement>(`[data-focus="${CSS.escape(focusKey)}"]`)?.focus({ preventScroll: true });
  requestAnimationFrame(() => arena?.resize());
}

function renderTitle() {
  $('scene-ui').innerHTML = `<div class="title-scene"><div class="title-copy"><div class="eyebrow line-eyebrow">A LANTERN LIT ROGUELIKE</div><h1>Every forest<br>has its <em>stories.</em></h1><p>Gather a band of woodland companions.<br>Weave a little magic. Find your way home.</p><div class="title-actions">${savedRun && !['victory','defeat'].includes(savedRun.phase) ? `<button data-ui="resume" class="button primary">${icon('lantern')}Continue trail${icon('arrow')}<small>Clearing ${savedRun.phase === 'map' ? savedRun.floor + 1 : savedRun.floor} · ${savedRun.hp} health</small></button>` : ''}<button data-ui="new" class="button ${savedRun && !['victory','defeat'].includes(savedRun.phase) ? 'secondary' : 'primary'}">Begin a new trail ${icon('arrow')}</button></div>${saveNotice ? `<p class="save-notice" role="status">${escape(saveNotice)}</p>` : ''}<div class="title-details"><span>Turn based strategy</span><i></i><span>Original woodland companions</span><i></i><span>One short, seeded journey</span></div></div><div class="title-art" aria-hidden="true"><div class="moon-disc"></div><svg viewBox="0 0 420 440" class="hero-lantern"><defs><linearGradient id="brass" x1="0" x2="1" y1="0" y2="1"><stop stop-color="#f9df9c"/><stop offset="1" stop-color="#8b632a"/></linearGradient><radialGradient id="glow"><stop stop-color="#fff2b0"/><stop offset=".6" stop-color="#ecaf58"/><stop offset="1" stop-color="#9a6528"/></radialGradient></defs><g fill="none" stroke="url(#brass)" stroke-width="8"><path d="M178 104V78c0-50 64-50 64 0v26"/><path d="M150 140c-12-12-5-40 15-40h90c20 0 27 28 15 40"/><path d="m140 157-28 190m168-190 28 190M160 160l-12 183m112-183 12 183"/></g><path fill="url(#glow)" opacity=".85" d="M156 160h108l22 175H134l22-175Z"/><path fill="#58422a" d="m136 335-29 17v15h206v-15l-29-17H136Zm11-211-25 24v16h176v-16l-25-24H147Z"/><path fill="url(#brass)" d="M125 147h170v13H125Zm-16 205h202v17H109Zm21 23h160v12H130Z"/><path fill="#fff2ba" d="M210 314c-37-30-21-53 0-77-7 25 37 45 0 77Z"/><path fill="#654a2a" d="M196 308h28v22h-28Z"/><g stroke="#a2b996" stroke-width="3" fill="none"><path d="M42 395C12 365 18 313 59 297m-12 79-23-19m20-6 22-22m311 61c22-40 19-78-22-103m23 67 24-23m-25-3-20-21"/></g><g fill="#c8d0a6"><path d="m49 387 14-13-5-16-16 12Zm-15-43 15-7-5-17-18 11Zm341 25-17-12 6-17 19 13Zm-6-55-20-7 6-16 20 10Z"/></g></svg><div class="art-caption">Carry the light.<span>The woods remember.</span></div></div></div>`;
}
const routes: Record<string, { name: string; tag: string; description: string }> = {
  battle: { name: 'Woodland clearing', tag: 'CONTRACT', description: 'Face forest creatures. Earn gold and choose a new card.' },
  elite: { name: 'The old hunting grounds', tag: 'HARD CONTRACT', description: 'A fiercer fight. More gold, and a woodland charm.' },
  camp: { name: 'A fire among the ferns', tag: 'REST OR TRAIN', description: 'Restore 18 health, or improve one card in your deck.' },
  shop: { name: 'The travelling peddler', tag: 'TRADE', description: 'Buy a companion or spell. Remove a card to focus your deck.' },
  event: { name: 'The moonlit shrine', tag: 'ENCOUNTER', description: 'A quiet place with a gift, a bargain, and a choice.' },
  boss: { name: 'Heart of the hollow', tag: 'FINAL CONTRACT', description: 'The keeper of the deep woods awaits. Prepare your companions.' },
};
function renderMap() {
  $('scene-ui').innerHTML = `<div class="page-panel map-panel"><div class="page-intro"><span class="eyebrow">CHAPTER ${Math.min(3, Math.floor(state.floor / 3) + 1)} · THE HOLLOW WOODS</span><h1>The trail bends onward.</h1><p>A little light is enough for the next step. Choose your clearing.</p></div><div class="trail-progress" aria-label="Journey progress">${Array.from({ length: 10 }, (_, i) => `<span class="trail-node ${i < state.floor ? 'passed' : i === state.floor ? 'current' : ''}" title="Clearing ${i + 1}">${i < state.floor ? icon('check') : i === 9 ? icon('boss') : `<i></i>`}</span>`).join('')}</div><div class="route-grid">${state.route.map((route, i) => { const r = routes[route] || routes.battle; return `<button class="route-card ${route === 'boss' ? 'boss-route' : ''}" data-action="travel" data-choice="${escape(route)}" data-focus="route-${i}"><span class="route-symbol">${icon(route)}</span><span class="eyebrow">${r.tag}</span><h2>${r.name}</h2><p>${r.description}</p><span class="route-bottom">Take this path ${icon('arrow')}</span></button>`; }).join('')}</div><div class="map-note">${icon('lantern')}Health carries between clearings. Your deck and companions reset for each fight.</div>${relicsLine()}</div>`;
}
const relicInfo: Record<string, { name: string; text: string }> = {
  'moon-charm': { name: 'Moon Charm', text: 'All damage spells deal 1 extra damage.' },
  'ember-seed': { name: 'Ember Seed', text: 'New companions gain 2 maximum health.' },
  'brass-bell': { name: 'Brass Bell', text: 'Gain 1 extra energy on the first turn of each fight.' },
};
function relicsLine() {
  return state.relics.length ? `<div class="relic-strip">${state.relics.map(r => `<span title="${escape(relicInfo[r]?.text || r)}">${icon('moon')} ${escape(relicInfo[r]?.name || r)}</span>`).join('')}</div>` : '';
}
function isTarget(uid: string) {
  if (!selected) return false;
  return actions().some(a => selected?.kind === 'attack' ? a.type === 'attack' && a.unit === selected.uid && a.target === uid : selected?.kind === 'card' && a.type === 'play' && a.index === selected.index && a.target === uid);
}
function targetName(uid: string): string {
  if (uid === 'hunter') return 'you';
  if (uid === 'all') return 'everyone';
  return state.allies.find(a => a.uid === uid)?.name || state.enemies.find(a => a.uid === uid)?.name || 'you';
}
function roster(side: 'allies' | 'enemies'): string {
  const units = state[side];
  const enemy = side === 'enemies';
  return `<section class="roster ${enemy ? 'enemy-roster' : 'ally-roster'}" aria-label="${enemy ? 'Enemies' : 'Your companions'}"><div class="roster-heading"><span class="eyebrow">${enemy ? 'THE WOODS PUSH BACK' : 'YOUR COMPANIONS'}</span><span>${units.length} / 6 ${enemy ? 'enemies' : 'companions'}${enemy ? '' : ' · One free command each turn'}</span></div><div class="unit-grid">${Array.from({ length: 6 }, (_, i) => {
    const unit = units[i];
    if (!unit) return `<div class="empty-slot" aria-label="Empty ${enemy ? 'enemy' : 'companion'} slot ${i + 1}"><span>+</span><small>${enemy ? 'Quiet woods' : 'Summon here'}</small></div>`;
    const target = isTarget(unit.uid);
    const chosen = selected?.kind === 'attack' && selected.uid === unit.uid;
    const ready = !enemy && !unit.acted;
    const intent = unit.intent;
    const targetText = intent ? intent.damage > 0 ? `${intent.damage} damage → ${targetName(intent.target)}${/ignores block/.test(intent.label) ? ' · ignores block' : ''}` : intent.label : 'Intent unknown';
    return `<button class="unit ${enemy ? 'enemy' : 'ally'} ${target ? 'valid-target' : ''} ${chosen ? 'selected' : ''} ${ready ? 'ready' : ''}" data-unit="${escape(unit.uid)}" data-focus="unit-${escape(unit.uid)}" aria-label="${escape(unit.name)}. ${unit.hp} of ${unit.maxHp} health, ${unit.attack} attack${unit.block ? `, ${unit.block} block` : ''}. ${enemy ? escape(targetText) : unit.acted ? 'Already commanded this turn.' : 'Ready to attack; select, then choose an enemy.'}${target ? ' Select as target.' : ''}" aria-pressed="${chosen}"><div class="unit-top">${creature(unit.species, unit.color)}<div><strong>${escape(unit.name)}</strong><span class="unit-stats">${icon('heart')} ${unit.hp}<small>/${unit.maxHp}</small><span>${icon('battle')}${unit.attack}</span>${unit.block ? `<span class="block-small">${icon('shield')}${unit.block}</span>` : ''}</span></div></div><div class="health-track"><i style="width:${unit.hp / unit.maxHp * 100}%"></i></div><div class="unit-status ${enemy ? 'intent' : ''}">${enemy ? `${icon('battle')}<span>${escape(targetText)}</span>` : target ? 'SELECT TARGET' : unit.acted ? `${icon('check')} Command used` : chosen ? 'CHOOSE AN ENEMY' : 'Ready · Click to command'}</div></button>`;
  }).join('')}</div></section>`;
}
function renderBattle() {
  const currentSelection = selected;
  const selectionText = currentSelection?.kind === 'attack' ? `Command ${state.allies.find(a => a.uid === currentSelection.uid)?.name || 'companion'}: choose an enemy.` : selected?.kind === 'card' ? `${CARDS[state.hand[selected.index]].name}: choose ${cardTarget(state.hand[selected.index]) === 'ally' ? 'a friendly target' : 'an enemy'}.` : 'Play a card. Then command each ready companion by selecting it and an enemy.';
  $('scene-ui').innerHTML = `<div class="battle-ui"><div class="battle-guidance ${selected ? 'targeting' : ''}"><span>${icon(selected ? 'battle' : 'lantern')}${escape(selectionText)}</span>${selected ? '<button class="text-button" data-ui="cancel">Cancel <kbd>Esc</kbd></button>' : `<button class="text-button" data-ui="log">Battle journal ${icon('book')}</button>`}</div>${roster('enemies')}<div class="arena-caption" aria-hidden="true"><span>THE HOLLOW WOODS</span><i></i><small>${selected ? 'Follow the light to your target' : 'A little courage. A little magic.'}</small></div>${roster('allies')}</div>`;
  const playable = actions().filter(a => a.type === 'play');
  $('dock').innerHTML = `<div class="hand-area"><div class="hand-heading"><span class="eyebrow">YOUR HAND <span>${state.hand.length}</span></span><div class="pile-buttons"><button data-ui="draw">Draw <strong>${state.draw.length}</strong></button><button data-ui="discard">Discard <strong>${state.discard.length}</strong></button></div></div><div class="hand-cards">${state.hand.map((id, index) => renderCard(CARDS[id], { handIndex: index, disabled: !playable.some(a => a.type === 'play' && a.index === index), selected: selected?.kind === 'card' && selected.index === index })).join('')}${!state.hand.length ? '<div class="empty-hand">Your hand is empty.<br>Command your companions, then end your turn.</div>' : ''}</div></div><div class="turn-controls"><div class="energy-orb">${icon('energy')}<strong>${state.energy}</strong><span>energy left</span></div><button class="button end-turn" data-action="endTurn" data-focus="end-turn">End turn ${icon('arrow')}<small>Enemies act · draw 5 · refill energy</small></button><span class="keyboard-hint"><kbd>E</kbd> End turn <span>·</span> <kbd>Esc</kbd> Cancel</span></div>`;
}

function renderCard(card: CardDef, opts: { handIndex?: number; disabled?: boolean; selected?: boolean; reward?: boolean; shop?: boolean; inspect?: boolean } = {}): string {
  const action = opts.handIndex !== undefined ? 'data-ui="play-card"' : opts.reward ? 'data-action="reward"' : opts.shop ? 'data-action="buy"' : 'data-ui="inspect"';
  const price = card.type === 'summon' ? 55 : 40;
  const target = cardTarget(card.id);
  return `<button class="game-card ${card.type} ${opts.selected ? 'selected' : ''} ${opts.disabled ? 'unplayable' : ''} ${opts.handIndex === undefined ? 'large-card' : ''}" ${action} data-index="${opts.handIndex ?? ''}" data-card="${escape(card.id)}" data-focus="${opts.handIndex !== undefined ? `card-${opts.handIndex}` : `card-${escape(card.id)}`}" aria-disabled="${!!opts.disabled}" ${opts.disabled && opts.handIndex === undefined ? 'disabled' : ''} aria-label="${escape(card.name)}, ${card.cost} energy. ${escape(card.text)}${opts.disabled ? '. Currently unavailable.' : ''}"><span class="card-cost">${card.cost}</span><span class="card-art" style="--card-color:${escape(card.color)}">${card.type === 'summon' ? creature(card.species, card.color) : icon(card.effect === 'block' ? 'shield' : card.effect === 'heal' ? 'heart' : card.effect === 'draw' ? 'book' : 'energy')}<span class="card-art-ring"></span></span><span class="card-name">${escape(card.name)}</span><span class="card-kind">${card.type === 'summon' ? 'COMPANION' : `SPELL${target === 'none' ? '' : ' · CHOOSE TARGET'}`}</span><span class="card-description">${escape(card.type === 'summon' ? card.text.replace(/ Enhanced:.*$/, '') : card.text)}</span>${card.type === 'summon' ? `<span class="card-stats">${icon('battle')} ${card.attack} Attack <span>${icon('heart')} ${card.hp} Health</span></span>` : ''}${opts.reward ? `<span class="card-choose">Add to deck ${icon('arrow')}</span>` : opts.shop ? `<span class="card-choose">${icon('gold')} ${price} gold ${icon('arrow')}</span>` : ''}</button>`;
}
function renderRewards() {
  $('scene-ui').innerHTML = `<div class="page-panel reward-panel"><div class="page-intro"><span class="eyebrow">THE CLEARING IS SAFE</span><h1>A new story for your deck.</h1><p>Choose one card to keep. A smaller deck makes your favourite cards easier to find.</p></div><div class="reward-cards">${state.rewards.map(id => renderCard(CARDS[id], { reward: true })).join('')}</div><button class="button secondary" data-action="reward" data-card="">Keep my deck as it is ${icon('arrow')}</button><span class="panel-footnote">Your next hand awaits in the next clearing.</span></div>`;
}
function renderCamp() {
  $('scene-ui').innerHTML = `<div class="page-panel"><div class="page-intro"><span class="eyebrow">A FIRE AMONG THE FERNS</span><span class="page-emblem">${icon('camp')}</span><h1>Rest your weary lantern.</h1><p>The fire is warm, and the woods can wait. Choose one.</p></div><div class="choice-grid"><button class="choice-card" data-action="camp" data-choice="rest">${icon('heart')}<h2>A moment of rest</h2><p>Restore <strong>18 health</strong>, up to your maximum.</p><span>${state.hp} → ${Math.min(state.maxHp, state.hp + 18)} health ${icon('arrow')}</span></button><button class="choice-card" data-action="camp" data-choice="train">${icon('book')}<h2>Practise by the fire</h2><p>Permanently improve the first untrained companion in your deck, or a spell if all companions are trained.</p><span>Strengthen your deck ${icon('arrow')}</span></button></div></div>`;
}
function renderShop() {
  const buys = actions().filter((a): a is Extract<Action, { type: 'buy' }> => a.type === 'buy');
  const stock = state.rewards.length ? state.rewards : buys.map(a => a.card);
  $('scene-ui').innerHTML = `<div class="page-panel shop-panel"><div class="page-intro"><span class="eyebrow">THE TRAVELLING PEDDLER</span><h1>Something for the road?</h1><p>A fair trade, a lighter deck, and a little conversation.</p></div><div class="reward-cards">${stock.map(id => renderCard(CARDS[id], { shop: true, disabled: !can({ type: 'buy', card: id }) })).join('')}</div><div class="shop-bottom"><button class="button secondary" data-ui="remove" ${actions().some(a => a.type === 'remove') ? '' : 'disabled'}>Remove a card <span>${icon('gold')}35</span></button><button class="button primary" data-action="leave">Back to the trail ${icon('arrow')}</button></div><span class="panel-footnote">Companions cost 55 gold · Spells cost 40 gold · Remove a card for 35 gold</span></div>`;
}
function renderEvent() {
  const choices = [
    { id: 'offering', icon: 'moon', name: 'Leave a little light', text: 'Lose 8 health. Gain the Moon Charm: damage spells deal 1 extra damage.', consequence: `${state.hp} → ${Math.max(0, state.hp - 8)} health` },
    { id: 'forage', icon: 'gold', name: 'Gather what is given', text: 'Find 25 gold among the roots. No price to pay.', consequence: `${state.gold} → ${state.gold + 25} gold` },
    { id: 'leave', icon: 'lantern', name: 'Let the shrine sleep', text: 'Leave the forest undisturbed, and continue your journey.', consequence: 'Continue quietly' },
  ];
  $('scene-ui').innerHTML = `<div class="page-panel event-panel"><div class="page-intro"><span class="eyebrow">THE MOONLIT SHRINE</span><span class="page-emblem">${icon('moon')}</span><h1>The roots hold a secret.</h1><p>In the hollow of an old tree, a silver charm catches your lantern light.<br>A tiny voice offers a bargain. You can also gather the coins at its feet.</p></div><div class="choice-grid three-choices">${choices.map(c => `<button class="choice-card" data-action="event" data-choice="${c.id}" ${can({ type: 'event', choice: c.id }) ? '' : 'disabled'}>${icon(c.icon)}<h2>${c.name}</h2><p>${c.text}</p><span>${c.consequence}${icon('arrow')}</span></button>`).join('')}</div></div>`;
}
function renderOutcome() {
  const won = state.phase === 'victory';
  $('scene-ui').innerHTML = `<div class="page-panel outcome-panel"><span class="outcome-emblem">${icon(won ? 'lantern' : 'moon')}</span><div class="page-intro"><span class="eyebrow">${won ? 'THE LANTERN STILL BURNS' : 'THE WOODS GROW QUIET'}</span><h1>${won ? 'You brought the light home.' : 'Every trail teaches a story.'}</h1><p>${won ? 'The hollow is peaceful again. Your little band did something brave.' : 'The forest kept this lantern. Another keeper, another deck, another chance.'}</p></div><div class="recap"><div><strong>${state.stats.battles}</strong><span>Contracts faced</span></div><div><strong>${state.stats.cardsPlayed}</strong><span>Cards played</span></div><div><strong>${state.stats.damageDealt}</strong><span>Damage dealt</span></div><div><strong>${state.stats.turns}</strong><span>Turns taken</span></div></div>${relicsLine()}<div class="outcome-actions"><button class="button primary" data-ui="new">Follow a new trail ${icon('arrow')}</button><button class="button secondary" data-ui="retry">Replay seed ${state.seed}</button></div><span class="panel-footnote">Difficulty: ${state.difficulty === 0 ? 'Story trail' : 'Hunter trail'} · Final health: ${state.hp}/${state.maxHp} · Deck: ${state.deck.length} cards</span></div>`;
}

function openDialog(name: string, content: string, wide = false) {
  const dialog = $<HTMLDialogElement>('dialog');
  dialog.className = wide ? 'wide-dialog' : '';
  dialog.innerHTML = `<div class="dialog-head"><h2 id="dialog-title">${name}</h2><button class="icon-button" data-ui="close" aria-label="Close dialog">${icon('close')}</button></div><div class="dialog-body">${content}</div>`;
  if (!dialog.open) dialog.showModal();
}
function closeDialog() { $<HTMLDialogElement>('dialog').close(); }
function openNew() {
  openDialog('A fresh trail', `<p class="dialog-copy">Every seed is its own little story. Use the same seed to revisit the same woods.</p><form id="new-game-form"><label class="field-label" for="seed">Trail seed <small>Any number or words</small></label><input id="seed" name="seed" type="text" maxlength="64" value="${Math.floor(Math.random() * 9999999)}" autocomplete="off"/><fieldset class="difficulty-options"><legend>Choose your trail</legend><label><input type="radio" name="difficulty" value="0" checked/><span><strong>Story trail</strong><small>Gentler fights. Space to learn your cards.</small></span></label><label><input type="radio" name="difficulty" value="1"/><span><strong>Hunter trail</strong><small>Stronger creatures for a thoughtful challenge.</small></span></label></fieldset>${!title && !['victory','defeat'].includes(state.phase) || savedRun && !['victory','defeat'].includes(savedRun.phase) ? '<p class="abandon-notice">Beginning a new trail replaces your current saved run.</p>' : ''}<button class="button primary full-width" type="submit">Light the lantern ${icon('arrow')}</button></form>`);
}
function openTutorial() {
  openDialog('Carry the light', `<p class="dialog-copy">You are a lantern keeper. Keep your health above zero and defeat the creatures at the heart of the hollow.</p><div class="tutorial-steps"><div><span>1</span><section><h3>Play your hand</h3><p>Each turn gives you <strong>5 energy</strong> and <strong>5 cards</strong>. The number in a card’s corner is its energy cost. Unplayed cards go to discard at turn end; empty draw piles reshuffle.</p></section></div><div><span>2</span><section><h3>Gather your companions</h3><p>Companion cards summon into one of <strong>6 friendly slots</strong>. Companions stay through the fight. A fallen companion returns to discard and can be drawn again.</p></section></div><div><span>3</span><section><h3>Command, then choose a target</h3><p><strong>Click a ready companion, then an enemy.</strong> Each companion attacks once per turn, for free—even on the turn it arrives. Spells that need a target wait for your choice.</p></section></div><div><span>4</span><section><h3>Read what happens next</h3><p>Each enemy shows its planned damage and target. <strong>End turn</strong> lets enemies act and starts your next turn. Block absorbs damage and expires at your next turn. Piercing light ignores block. If an enemy’s marked companion falls, that enemy targets you instead. Your health carries between fights.</p></section></div></div><div class="tutorial-shortcuts"><kbd>E</kbd> End turn <kbd>Esc</kbd> Cancel / pause <kbd>Tab</kbd> Navigate <kbd>Enter</kbd> Choose</div><button class="button primary full-width" data-ui="learned">I’m ready for the woods ${icon('arrow')}</button>`, true);
}
function openDeck(pile: 'deck' | 'draw' | 'discard' = 'deck', removing = false) {
  const ids = state[pile];
  const counts = new Map<string, number>();
  ids.forEach(id => counts.set(id, (counts.get(id) || 0) + 1));
  openDialog(removing ? 'Lighten your deck · 35 gold' : `${pile === 'deck' ? 'Your travelling deck' : pile === 'draw' ? 'Draw pile' : 'Discard pile'} · ${ids.length} cards`, `${removing ? '<p class="dialog-copy">Choose one card to remove permanently. This costs 35 gold.</p>' : `<p class="dialog-copy">${pile === 'draw' ? 'Grouped by card, without revealing draw order.' : pile === 'discard' ? 'These cards return when your draw pile reshuffles.' : 'Your companions and spells for this journey. Living companions stay out of the draw pile until they fall.'}</p>`}<div class="deck-grid">${Array.from(counts).map(([id, count]) => `<div class="deck-entry">${removing ? `<button class="remove-card" data-action="remove" data-index="${state.deck.indexOf(id)}">${creature(CARDS[id].species, CARDS[id].color)}<span><strong>${escape(CARDS[id].name)}</strong><small>${count} in deck · ${CARDS[id].cost} energy</small><p>${escape(CARDS[id].text)}</p></span>${icon('close')}</button>` : `${renderCard(CARDS[id], { inspect: true })}<span class="copy-count">${count} ${count === 1 ? 'copy' : 'copies'}</span>`}</div>`).join('') || '<p class="empty-pile">This pile is empty.</p>'}</div>${pile === 'deck' && !removing && state.relics.length ? `<h3 class="charms-heading">Woodland charms</h3><div class="charm-list">${state.relics.map(r => `<p>${icon('moon')}<span><strong>${escape(relicInfo[r]?.name || r)}</strong><small>${escape(relicInfo[r]?.text || '')}</small></span></p>`).join('')}</div>` : ''}`, true);
}
function openSettings() {
  openDialog('Make yourself comfortable', `<div class="setting-row"><label for="mute"><strong>Sound effects</strong><small>Soft, synthesized notes for your actions.</small></label><input type="checkbox" id="mute" ${!settings.mute ? 'checked' : ''}/></div><div class="setting-row"><label for="volume"><strong>Volume</strong><small id="volume-value">${Math.round(settings.volume * 100)}%</small></label><input type="range" id="volume" min="0" max="100" value="${settings.volume * 100}"/></div><div class="setting-row"><label for="motion"><strong>Ambient motion</strong><small>Creature idles, lantern glow, and fireflies.</small></label><input type="checkbox" id="motion" ${settings.motion ? 'checked' : ''}/></div><p class="settings-note">Your preferences are stored on this device. The arena is decorative; all game information is available in the companion and enemy panels.</p><button class="button secondary full-width" data-ui="close">Back to the woods</button>`);
}
function openPause() {
  openDialog('A moment by the lantern', `<p class="dialog-copy">Your trail saves after every choice. You can return whenever you like.</p><div class="pause-buttons"><button class="button primary" data-ui="close">Continue ${icon('arrow')}</button><button class="button secondary" data-ui="menu">Return to title</button><button class="text-button" data-ui="new">Start a fresh trail</button></div>`);
}

function selectCard(index: number) {
  const id = state.hand[index];
  const card = CARDS[id];
  if (!card) return;
  if (selected?.kind === 'card' && selected.index === index) { selected = null; render(); return; }
  const available = actions().filter((a): a is Extract<Action, { type: 'play' }> => a.type === 'play' && a.index === index);
  if (!available.length) {
    notify(state.energy < card.cost ? `You need ${card.cost} energy to play ${card.name}.` : card.type === 'summon' && state.allies.length >= 6 ? 'All six companion slots are full.' : 'This card needs a valid target.');
    return;
  }
  if (cardTarget(id) === 'none') dispatch({ type: 'play', index });
  else { selected = { kind: 'card', index }; sound(); render(); document.querySelector<HTMLElement>('.unit.valid-target, .hunter-hud.valid-target button')?.focus(); }
}
function selectUnit(uid: string) {
  if (selected && isTarget(uid)) {
    if (selected.kind === 'attack') dispatch({ type: 'attack', unit: selected.uid, target: uid });
    else dispatch({ type: 'play', index: selected.index, target: uid });
    return;
  }
  if (selected?.kind === 'card') { notify('Choose a highlighted target, or press Escape to cancel.'); return; }
  if (selected?.kind === 'attack' && selected.uid === uid) { selected = null; render(); return; }
  const ally = state.allies.find(u => u.uid === uid);
  if (ally) {
    if (ally.acted) { notify(`${ally.name} has already been commanded this turn.`); return; }
    if (!actions().some(a => a.type === 'attack' && a.unit === uid)) { notify('No enemy is available to attack.'); return; }
    selected = { kind: 'attack', uid }; sound(); render(); document.querySelector<HTMLElement>('.enemy.valid-target')?.focus();
  } else if (uid !== 'hunter') {
    const enemy = state.enemies.find(u => u.uid === uid);
    if (enemy) notify(`${enemy.name} plans ${enemy.intent?.damage || 0} damage to ${targetName(enemy.intent?.target || 'hunter')}. Select a ready companion or a targeted spell to attack.`);
  }
}

function handleClick(event: MouseEvent) {
  const button = (event.target as HTMLElement).closest<HTMLElement>('button');
  if (!button || button.hasAttribute('disabled')) return;
  if (button.dataset.unit) { selectUnit(button.dataset.unit); return; }
  if (button.dataset.action) {
    const type = button.dataset.action;
    let action: Action | null = null;
    if (type === 'travel') action = { type, choice: button.dataset.choice! };
    if (type === 'endTurn') {
      const ready = state.allies.filter(a => !a.acted);
      if (ready.length) {
        openDialog('Ready companions are waiting', `<p class="dialog-copy">${ready.length} companion${ready.length === 1 ? ' has' : 's have'} not attacked this turn. Their commands are free.</p><div class="pause-buttons"><button class="button primary" data-ui="close">Let me command them</button><button class="button secondary" data-ui="confirm-end">End turn anyway ${icon('arrow')}</button></div>`); return;
      }
      action = { type };
    }
    if (type === 'reward') action = { type, card: button.dataset.card || null };
    if (type === 'camp') action = { type, choice: button.dataset.choice as 'rest' | 'train' };
    if (type === 'buy') action = { type, card: button.dataset.card! };
    if (type === 'remove') { action = { type, index: Number(button.dataset.index) }; closeDialog(); }
    if (type === 'leave') action = { type };
    if (type === 'event') action = { type, choice: button.dataset.choice! };
    if (action) dispatch(action);
    return;
  }
  switch (button.dataset.ui) {
    case 'new': openNew(); break;
    case 'resume': if (savedRun) { state = savedRun; title = false; selected = null; render(); sound(); } break;
    case 'retry': closeDialog(); start(state.seed, state.difficulty); break;
    case 'home': if (!title) openPause(); break;
    case 'menu': closeDialog(); title = true; selected = null; render(); break;
    case 'settings': openSettings(); break;
    case 'help': openTutorial(); break;
    case 'learned': try { localStorage.setItem(TUTORIAL_KEY, 'yes'); } catch { /* Optional preference. */ } closeDialog(); break;
    case 'close': closeDialog(); break;
    case 'deck': openDeck(); break;
    case 'draw': openDeck('draw'); break;
    case 'discard': openDeck('discard'); break;
    case 'remove': openDeck('deck', true); break;
    case 'play-card': selectCard(Number(button.dataset.index)); break;
    case 'cancel': selected = null; render(); break;
    case 'confirm-end': closeDialog(); dispatch({ type: 'endTurn' }); break;
    case 'inspect': {
      const card = CARDS[button.dataset.card!];
      if (card) openDialog(card.name, `<div class="inspect-card">${renderCard(card)}</div><p class="dialog-copy">${escape(card.text)}${card.type === 'summon' ? ' Companions can attack once each turn at no energy cost, including the turn they arrive.' : ''}</p><button class="button secondary full-width" data-ui="deck">Return to deck</button>`);
      break;
    }
    case 'log': openDialog('The battle journal', `<ol class="battle-log">${state.log.slice().reverse().map(line => `<li>${escape(line)}</li>`).join('') || '<li>Your story has just begun.</li>'}</ol>`); break;
    case 'fullscreen': if (!document.fullscreenElement) void document.documentElement.requestFullscreen?.().catch(() => notify('Fullscreen is unavailable in this window.')); else void document.exitFullscreen(); break;
  }
}
document.addEventListener('click', handleClick);
document.addEventListener('submit', event => {
  if ((event.target as HTMLElement).id !== 'new-game-form') return;
  event.preventDefault();
  const form = event.target as HTMLFormElement;
  const data = new FormData(form);
  closeDialog(); start(parseSeed(String(data.get('seed') || '')), Number(data.get('difficulty') || 0));
});
document.addEventListener('input', event => {
  const input = event.target as HTMLInputElement;
  if (!['mute','volume','motion'].includes(input.id)) return;
  if (input.id === 'mute') settings.mute = !input.checked;
  if (input.id === 'motion') settings.motion = input.checked;
  if (input.id === 'volume') { settings.volume = Number(input.value) / 100; $('volume-value').textContent = `${input.value}%`; }
  setMotion();
  try { localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings)); } catch { /* Game is usable without persistent settings. */ }
  if (input.id !== 'motion') sound();
});
document.addEventListener('keydown', event => {
  if ($<HTMLDialogElement>('dialog').open) return;
  if (event.target instanceof HTMLInputElement || event.target instanceof HTMLTextAreaElement) return;
  if (event.key === 'Escape') { event.preventDefault(); if (selected) { selected = null; render(); } else if (!title) openPause(); }
  if (event.key.toLowerCase() === 'e' && !event.repeat && !title && state.phase === 'battle') { event.preventDefault(); document.querySelector<HTMLButtonElement>('[data-action="endTurn"]')?.click(); }
});
$<HTMLDialogElement>('dialog').addEventListener('click', event => {
  const dialog = $<HTMLDialogElement>('dialog');
  if (event.target === dialog) { const r = dialog.getBoundingClientRect(); if (event.clientX < r.left || event.clientX > r.right || event.clientY < r.top || event.clientY > r.bottom) closeDialog(); }
});
window.addEventListener('beforeunload', () => arena?.dispose());
render();
