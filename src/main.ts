import './style.css';
import packageInfo from '../package.json';
import { applyActionWithEvents, createGame, CARDS, legalActions, validateState, recoverLegacySilenceSave, cardTarget, type GameState, type Action, type Unit, type CardDef } from './engine';
import { createArena } from './arena';
import { portraitFor, toolArtFor } from './art';
import { createToolIllustrations } from './tool-art';
import { ENEMIES, RELICS, SHOP_PRICES, EVENT_CHOICES, bossForSeed } from './content';

const SAVE_KEY = 'hollowpact.run.v2';
const SAVE_BACKUP_KEY = `${SAVE_KEY}.backup.silence`;
let pendingRecoveryBackup: string | null = null;
function preserveRecoveryOriginal(): boolean {
  if (pendingRecoveryBackup === null) return true;
  let key = SAVE_BACKUP_KEY;
  const existing = localStorage.getItem(key);
  if (existing !== null && existing !== pendingRecoveryBackup) {
    const prefix = `${SAVE_BACKUP_KEY}.${Date.now()}`;
    key = prefix;
    let suffix = 1;
    while (localStorage.getItem(key) !== null) key = `${prefix}.${suffix++}`;
  }
  localStorage.setItem(key, pendingRecoveryBackup);
  pendingRecoveryBackup = null;
  return true;
}
const SETTINGS_KEY = 'hollowpact.settings.v2';
const TUTORIAL_KEY = 'hollowpact.tutorial.v2';
const VERSION = packageInfo.version;
const BUILD_ID = import.meta.env.VITE_BUILD_ID || 'development';
const HUNTER_NAME = 'Marek Voss';
type ArenaPresentation = ReturnType<typeof createArena> & { busyMs?: () => number; waitForPresentation?: () => Promise<void>; cancelPresentation?: () => void };
let settlingCombat = false;
let presentationEpoch = 0;
let presentationDeadline: ReturnType<typeof setTimeout> | null = null;
let disposed = false;
type Selection = { kind: 'attack'; uid: string } | { kind: 'card'; index: number } | null;
type Settings = { mute: boolean; volume: number; motion: boolean };
const $ = <T extends HTMLElement>(id: string) => document.getElementById(id) as T;
const escape = (s: string | number) => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]!));
let state = createGame(Date.now() >>> 0);
let title = true;
// CSS custom-property URLs resolve at their consuming stylesheet; use a document-based absolute URL.
const ART_BASE = new URL(`${import.meta.env.BASE_URL}art/`, document.baseURI).href;
const toolIllustrations = createToolIllustrations();
document.documentElement.style.setProperty('--courtyard-art', `url("${ART_BASE}abbey-courtyard.png")`);
document.documentElement.style.setProperty('--hunter-art', `url("${ART_BASE}hunter-portrait.png")`);
let selected: Selection = null;
let savedRun: GameState | null = null;
let saveNotice = '';
let toastTimeout: ReturnType<typeof setTimeout>;
let settings: Settings = { mute: false, volume: .25, motion: !window.matchMedia('(prefers-reduced-motion: reduce)').matches };
try {
  const stored = localStorage.getItem(SETTINGS_KEY);
  if (stored) {
    const value = JSON.parse(stored);
    if (value !== null && typeof value === 'object' && !Array.isArray(value) && typeof value.mute === 'boolean' && typeof value.volume === 'number' && Number.isFinite(value.volume) && typeof value.motion === 'boolean') settings = { mute: value.mute, volume: Math.max(0, Math.min(1, value.volume)), motion: value.motion };
  }
} catch { /* Unreadable preferences use defaults without hiding the campaign. */ }
try {
  const save = localStorage.getItem(SAVE_KEY);
  if (save) {
    const value: unknown = JSON.parse(save);
    if (validateState(value)) { savedRun = value as GameState; state = savedRun; }
    else {
      const recovered = recoverLegacySilenceSave(value);
      if (recovered && validateState(recovered)) {
        savedRun = recovered; state = recovered; pendingRecoveryBackup = save;
        saveNotice = 'Recovered a repeated Silence status label. Your run is preserved.';
        try {
          preserveRecoveryOriginal();
          localStorage.setItem(SAVE_KEY, JSON.stringify(recovered));
        } catch {
          saveNotice = pendingRecoveryBackup === null ? 'Recovered the repeated Silence status. A backup is preserved; the browser could not store the updated campaign.' : 'Recovered the repeated Silence status for this window. The original save is unchanged; the browser could not create a backup.';
        }
      } else {
        const candidate = value && typeof value === 'object' ? value as Record<string, unknown> : null;
        saveNotice = candidate && (typeof candidate.schema === 'number' && candidate.schema > 3 || candidate.schema === 3 && candidate.engineKind !== 2)
          ? 'This campaign uses an unsupported rules version. Its saved data is unchanged. Start a new campaign to continue.'
          : 'An incompatible save was found. Start a new campaign to continue.';
      }
    }
  }
} catch { saveNotice = 'Your save could not be read. A new campaign is still available.'; }

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

function creature(species = 'wraith', _color = '#aeb8b8'): string {
  const portrait = portraitFor(species);
  if (!portrait) return `<span class="portrait portrait-unknown" aria-hidden="true">${icon('shield')}</span>`;
  const focal: Record<string, [number, number]> = { hound: [79,39], stalker: [69,32], colossus: [43,22], spider: [55,54], warlord: [55,19], necromancer: [53,19], wraith: [44,20], thrall: [44,20], dragon: [73,37] };
  const [x,y] = focal[species] || [50,35];
  return `<span class="portrait-frame" aria-hidden="true" style="--portrait-x:${x}%;--portrait-y:${y}%"><span class="portrait" style="background-image:url('${escape(portrait.url)}');background-size:${(portrait.columns || 2) * 100}% ${(portrait.rows || 2) * 100}%;background-position:${portrait.column * 100}% ${portrait.row * 100}%"></span></span>`;
}

const spellSymbol = (effect?: string) => ({ block: 'shield', shelter: 'shield', heal: 'heart', communion: 'heart', hunterheal: 'heart', damage: 'battle', aoe: 'elite', ready: 'arrow', control: 'moon', draw: 'book', rally: 'boss', siphon: 'moon', pack: 'battle', shred: 'battle' } as Record<string, string>)[effect || ''] || 'energy';
function cardRules(card: CardDef): string {
  if (card.type === 'spell') return card.text.replace(/ Enhanced: costs 1 energy\./, '');
  const trigger = card.text.replace(/ Enhanced:.*$/, '').replace(/^Bind[^.]*\.\s*/, '');
  return [trigger, card.passive].filter(Boolean).join(' ');
}
let arena: ReturnType<typeof createArena> | null = null;
try { arena = createArena($<HTMLCanvasElement>('arena')); }
catch { $('arena-wrap').classList.add('arena-fallback'); }
const sceneObserver = new ResizeObserver(() => arena?.resize());
sceneObserver.observe($('arena-wrap'));
window.addEventListener('resize', () => arena?.resize());

let audio: AudioContext | null = null;
function sound(kind: 'click' | 'summon' | 'attack' | 'reward' | 'end' = 'click') {
  if (settings.mute || settings.volume <= 0) return;
  try {
    audio ||= new AudioContext();
    void audio.resume();
    const context = audio;
    const start = context.currentTime;
    const master = context.createGain();
    master.gain.value = settings.volume * .2;
    master.connect(context.destination);
    const tone = (frequency: number, type: OscillatorType, duration: number, strength: number, delay = 0, endFrequency = frequency) => {
      const osc = context.createOscillator(), gain = context.createGain();
      const at = start + delay;
      osc.type = type;
      osc.frequency.setValueAtTime(frequency, at);
      osc.frequency.exponentialRampToValueAtTime(Math.max(20, endFrequency), at + duration);
      gain.gain.setValueAtTime(.001, at);
      gain.gain.linearRampToValueAtTime(strength, at + .006);
      gain.gain.exponentialRampToValueAtTime(.001, at + duration);
      osc.connect(gain); gain.connect(master);
      osc.start(at); osc.stop(at + duration + .01);
    };
    const grit = (duration: number, frequency: number, strength: number, delay = 0, filterType: BiquadFilterType = 'bandpass') => {
      const buffer = context.createBuffer(1, Math.ceil(context.sampleRate * duration), context.sampleRate);
      const data = buffer.getChannelData(0);
      for (let i = 0; i < data.length; i++) data[i] = Math.random() * 2 - 1;
      const source = context.createBufferSource(), filter = context.createBiquadFilter(), gain = context.createGain();
      const at = start + delay;
      source.buffer = buffer; filter.type = filterType; filter.frequency.value = frequency; filter.Q.value = .8;
      gain.gain.setValueAtTime(strength, at);
      gain.gain.exponentialRampToValueAtTime(.001, at + duration);
      source.connect(filter); filter.connect(gain); gain.connect(master);
      source.start(at); source.stop(at + duration);
    };
    if (kind === 'attack') {
      tone(96, 'sine', .24, .9, 0, 38); // body of the impact
      grit(.17, 1250, .65);
      tone(410, 'triangle', .19, .15, .018, 260);
      tone(1037, 'sine', .13, .08, .02, 690); // iron edge
    } else if (kind === 'summon') {
      tone(73, 'sine', .45, .75, 0, 49);
      tone(146, 'triangle', .32, .17, .025, 109);
      grit(.33, 330, .3, .015, 'lowpass');
      [0, .055, .13].forEach((delay, i) => { grit(.06, 2800, .16, delay); tone(660 + i * 137, 'sine', .1, .06, delay); });
    } else if (kind === 'reward') {
      [0, .075, .14].forEach((delay, i) => { tone(890 + i * 210, 'sine', .15, .15, delay); grit(.035, 4200, .14, delay); });
    } else if (kind === 'end') {
      tone(110, 'sine', .32, .7, 0, 42); grit(.2, 650, .3, .012, 'lowpass');
    } else {
      grit(.035, 1700, .18); tone(175, 'triangle', .06, .13, 0, 95);
    }
    // Every source ends within half a second; no idle audio loop or network asset.
    setTimeout(() => master.disconnect(), 700);
  } catch { /* Audio is optional; rule resolution never waits for playback. */ }
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
function clearToast() {
  clearTimeout(toastTimeout);
  $('toast').classList.remove('visible');
  $('toast').textContent = '';
}
function save() {
  savedRun = state;
  try { preserveRecoveryOriginal(); localStorage.setItem(SAVE_KEY, JSON.stringify(state)); }
  catch { notify('This browser cannot store the campaign. Keep this window open to continue.'); }
}
function actions(): Action[] { return legalActions(state); }
function can(action: Action): boolean { return actions().some(a => JSON.stringify(a) === JSON.stringify(action)); }
function mayAnimateCombat(): boolean {
  return settings.motion && !document.hidden && !window.matchMedia('(prefers-reduced-motion: reduce)').matches;
}
function cancelPresentation() {
  presentationEpoch++;
  settlingCombat = false;
  if (presentationDeadline !== null) clearTimeout(presentationDeadline);
  presentationDeadline = null;
  $('app').classList.remove('settling-combat');
  $('scene-ui').removeAttribute('aria-busy');
  try { (arena as ArenaPresentation | null)?.cancelPresentation?.(); } catch { /* Presentation cannot alter a saved result. */ }
}
function announceOutcome() {
  $('announcer').textContent = state.phase === 'reward' ? 'Contract cleared. Salvage ready. Choose one card or leave the salvage.' : state.phase === 'victory' ? 'Final contract cleared. Campaign complete. Your contract report is ready.' : state.phase === 'defeat' ? 'The hunter has fallen. Your contract report is ready.' : state.log[state.log.length - 1] || 'Choice made.';
}
function finishPresentation(epoch: number) {
  if (disposed || !settlingCombat || epoch !== presentationEpoch) return;
  settlingCombat = false;
  if (presentationDeadline !== null) clearTimeout(presentationDeadline);
  presentationDeadline = null;
  $('scene-ui').removeAttribute('aria-busy');
  render();
  announceOutcome();
  if (!$<HTMLDialogElement>('dialog').open) {
    const heading = document.querySelector<HTMLElement>('#scene-ui .page-intro h1');
    if (heading) { heading.tabIndex = -1; heading.focus({ preventScroll: true }); }
  }
}
function holdFinalStrike(): boolean {
  if (!mayAnimateCombat() || !arena) return false;
  let busy = 0;
  try { busy = Math.max(0, Math.min(1200, Number((arena as ArenaPresentation).busyMs?.() || 0))); } catch { return false; }
  if (!Number.isFinite(busy) || busy <= 0) return false;
  const epoch = ++presentationEpoch;
  settlingCombat = true;
  $('app').classList.add('settling-combat');
  $('scene-ui').setAttribute('aria-busy', 'true');
  // Rules and saves already reflect the result. The old field exists only for the final impact.
  document.querySelectorAll<HTMLButtonElement>('#scene-ui button, #dock button').forEach(button => { button.disabled = true; });
  const guidance = document.querySelector<HTMLElement>('.battle-guidance>span');
  if (guidance) guidance.textContent = state.phase === 'defeat' ? 'The pact breaks. The final impact is resolving.' : 'Contract cleared. Final strike resolving.';
  const cancel = document.querySelector<HTMLElement>('.battle-guidance>button');
  if (cancel) cancel.hidden = true;
  document.querySelectorAll<HTMLElement>('.unit .unit-status').forEach(status => { status.textContent = state.phase === 'defeat' ? 'Contract failed' : status.closest('.enemy') ? 'Quarry down' : 'Order complete'; });
  const caption = document.querySelector<HTMLElement>('.arena-caption>small');
  if (caption) caption.textContent = state.phase === 'defeat' ? 'PACT BROKEN' : 'WARRANT CLOSED';
  const endButton = document.querySelector<HTMLElement>('[data-action="endTurn"]');
  if (endButton) endButton.textContent = state.phase === 'defeat' ? 'Contract failed' : 'Contract cleared';
  document.querySelectorAll('.unit.selected, .unit.valid-target').forEach(unit => unit.classList.remove('selected', 'valid-target'));
  $('announcer').textContent = state.phase === 'defeat' ? 'The hunter has fallen.' : 'Contract cleared.';
  presentationDeadline = setTimeout(() => finishPresentation(epoch), Math.min(1200, Math.ceil(busy) + 30));
  try {
    const waiting = (arena as ArenaPresentation).waitForPresentation?.();
    if (waiting) void waiting.then(() => finishPresentation(epoch), () => finishPresentation(epoch));
  } catch { finishPresentation(epoch); }
  return true;
}
function dispatch(action: Action) {
  if (settlingCombat || disposed) return;
  const previous = state;
  const { state: next, events } = applyActionWithEvents(state, action);
  if (JSON.stringify(next) === JSON.stringify(previous)) { notify('That action is not available right now.'); return; }
  if (next.phase !== previous.phase || action.type === 'travel') clearToast();
  // Persist the canonical result before optional animation/audio runs.
  state = next;
  selected = null;
  save();
  let effectFailed = false;
  try { arena?.playAction?.(action, previous, next, events); } catch { effectFailed = true; }
  if (action.type === 'play') sound(CARDS[previous.hand[action.index]]?.type === 'summon' ? 'summon' : 'attack');
  else if (action.type === 'attack') sound('attack');
  else if (action.type === 'reward' || action.type === 'buy') sound('reward');
  else if (action.type === 'endTurn') sound('end');
  else sound();
  const terminalCombat = previous.phase === 'battle' && ['reward', 'victory', 'defeat'].includes(state.phase);
  if (terminalCombat && !effectFailed && holdFinalStrike()) return;
  render();
  if (terminalCombat) announceOutcome();
  else $('announcer').textContent = `${state.log[state.log.length - 1] || 'Choice made.'} ${state.phase === 'battle' ? `${state.energy} energy left. Hunter health ${state.hp} of ${state.maxHp}.` : ''}`;
}

function start(seed: number, difficulty: number) {
  cancelPresentation();
  clearToast();
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
  $('topbar').innerHTML = `<button class="wordmark" data-ui="home" aria-label="Hollowpact main menu">${icon('shield')}<span>HOLLOWPACT<small>CONTRACTS · CREATURES · CONSEQUENCES</small></span></button><nav aria-label="Game tools"><button class="nav-button" data-ui="deck" aria-label="Deck">${icon('book')}<span>Deck${title ? '' : ` <span class="subtle">${state.deck.length}</span>`}</span></button><button class="nav-button" data-ui="help" aria-label="How to play"><span class="help-symbol">?</span><span>How to play</span></button><button class="nav-button" data-ui="feedback" aria-label="Field report">${icon('event')}<span>Field report</span></button><button class="icon-button" data-ui="settings" aria-label="Settings">${icon('settings')}</button></nav>`;
}
function renderHud() {
  $('hud').hidden = title;
  if (title) { $('hud').innerHTML = ''; return; }
  $('hud').innerHTML = `<div class="hunter-hud ${isTarget('hunter') ? 'valid-target' : ''}"><button class="hunter-icon hunter-photo" data-ui="hunter" aria-label="Inspect Marek Voss. Hunter: ${state.hp} of ${state.maxHp} health${isTarget('hunter') ? ', select as target' : ''}"></button><div class="hunter-health"><div><strong>${HUNTER_NAME}</strong><span>${icon('heart')} ${state.hp}<small> / ${state.maxHp}</small></span></div><div class="health-track"><i style="width:${state.hp / state.maxHp * 100}%"></i></div></div>${state.block > 0 ? `<span class="block-count">${icon('shield')}${state.block}<small>Block</small></span>` : ''}</div><div class="journey-hud"><span class="eyebrow">${state.phase === 'battle' ? 'ACTIVE CONTRACT' : 'THE CAMPAIGN'}</span><strong>Contract ${(state.phase === 'map' ? state.floor + 1 : state.floor)} <span class="subtle">/ 10</span>${state.phase === 'battle' ? `<span class="turn-label">Turn ${state.turn}</span>` : ''}</strong></div><div class="resources"><span class="resource gold">${icon('gold')}<strong>${state.gold}</strong><small>Gold</small></span>${state.phase === 'battle' ? `<span class="resource energy">${icon('energy')}<strong>${state.energy}</strong><small>Energy</small></span>` : `<span class="resource relic">${icon('moon')}<strong>${state.relics.length}</strong><small>Relics</small></span>`}</div>`;
}
function render() {
  if (settlingCombat) return;
  const focusKey = document.activeElement instanceof HTMLElement ? document.activeElement.dataset.focus : undefined;
  setMotion();
  $('app').className = title ? 'on-title' : `phase-${state.phase}${state.phase === 'battle' && Math.max(state.allies.length, state.enemies.length) >= 3 ? ' dense-battle' : ''}`;
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
  $('footer').innerHTML = `<span>v${VERSION} <span class="footer-dot">·</span> Playable prototype</span><span>${title ? 'Original dark fantasy · Working title' : `Seed ${state.seed} <span class="footer-dot">·</span> Contract saved locally`}</span><button data-ui="fullscreen" class="text-button">Fullscreen</button>`;
  try { arena?.setSelected(selected?.kind === 'attack' ? selected.uid : null); arena?.render(state); } catch { $('arena-wrap').classList.add('arena-fallback'); }
  if (focusKey) document.querySelector<HTMLElement>(`[data-focus="${CSS.escape(focusKey)}"]`)?.focus({ preventScroll: true });
  toolIllustrations.refresh();
}

function renderTitle() {
  $('scene-ui').innerHTML = `<div class="title-scene"><div class="title-copy"><div class="eyebrow line-eyebrow">A DARK FANTASY DECKBUILDING CAMPAIGN</div><h1>HOLLOW<span>PACT</span></h1><div class="title-rule"></div><p>The dead do not honour treaties.<br>Bind what you can. Hunt what you must.</p><div class="title-details"><span>Command bound monsters</span><i></i><span>Read the enemy</span><i></i><span>Survive ten contracts</span></div></div><section class="title-contract"><div class="hunter-intro"><button class="hunter-photo title-hunter" data-ui="hunter" aria-label="Inspect Marek Voss"></button><div><span class="eyebrow">MAREK VOSS · PACT HUNTER</span><p>Scarred hands. Iron seals.<br>A name the dead remember.</p></div></div><span class="eyebrow">FIELD ORDERS · THE BLACK MARCH</span><h2>Your next contract awaits.</h2><p>Build a deck of dangerous creatures and practical tools. Choose your targets. Make each command count.</p><div class="title-actions">${savedRun && !['victory','defeat'].includes(savedRun.phase) ? `<button data-ui="resume" class="button primary">Resume contract ${icon('arrow')}<small>Contract ${savedRun.phase === 'map' ? savedRun.floor + 1 : savedRun.floor} · ${savedRun.hp} health</small></button>` : ''}<button data-ui="new" class="button ${savedRun && !['victory','defeat'].includes(savedRun.phase) ? 'secondary' : 'primary'}">Begin a new contract ${icon('arrow')}</button></div>${saveNotice ? `<p class="save-notice" role="status">${escape(saveNotice)}</p>` : ''}<div class="contract-note">ONE HUNTER. SIX BINDINGS. NO WASTED ORDERS.</div></section></div>`;
}

const routes: Record<string, { name: string; tag: string; description: string }> = {
  battle: { name: 'A debt in blood', tag: 'HUNT CONTRACT', description: 'Clear the hostile ground. Earn gold and choose a creature or tool.' },
  elite: { name: 'Black seal warrant', tag: 'ELITE CONTRACT', description: 'An armed threat with a dangerous trait. Greater pay and a recovered relic.' },
  camp: { name: 'Field shelter', tag: 'TREAT OR TRAIN', description: 'Restore 18 health, or choose a card to improve permanently.' },
  shop: { name: 'The quartermaster', tag: 'SUPPLY & REMOVE', description: 'Trade gold for bindings and tools. Remove a card to sharpen your plan.' },
  event: { name: 'A shrine without a god', tag: 'FIELD ENCOUNTER', description: 'Blood, salvage, or silence. Read the price before you choose.' },
  boss: { name: 'The final warrant', tag: 'BOSS CONTRACT', description: 'One last quarry. Guard phases, heavy strikes, and no safe retreat.' },
};

function renderMap() {
  const region = state.floor < 3 ? 'RUINED ABBEY' : state.floor < 7 ? 'DROWNED BORDERLANDS' : 'THE ASH MARCH';
  $('scene-ui').innerHTML = `<div class="page-panel map-panel"><div class="page-intro"><span class="eyebrow">FIELD CHART · ${region}</span><h1>Choose your next ground.</h1><p>Health and equipment carry forward. Every detour has a cost.</p></div><div class="trail-progress" aria-label="Ten-contract campaign progress">${Array.from({ length: 10 }, (_, i) => `<span class="trail-node ${i < state.floor ? 'passed' : i === state.floor ? 'current' : ''}" title="Contract ${i + 1}">${i < state.floor ? icon('check') : i === 9 ? icon('boss') : `<i></i>`}</span>`).join('')}</div><div class="route-grid">${state.route.map((route, i) => { const r = routes[route] || routes.battle; const boss = ENEMIES[bossForSeed(state.seed)]; return `<button class="route-card ${route === 'boss' ? 'boss-route' : ''}" data-action="travel" data-choice="${escape(route)}" data-focus="route-${i}"><span class="route-symbol">${icon(route)}</span><span class="eyebrow">${r.tag}</span><h2>${route === 'boss' ? escape(boss.name) : r.name}</h2><p>${route === 'boss' ? escape(boss.passive || r.description) : r.description}</p><span class="route-bottom">Accept ${icon('arrow')}</span></button>`; }).join('')}</div><div class="map-note">${icon('shield')}Bindings and temporary bonuses reset each fight. Your deck, gold, and hunter health persist.</div>${relicsLine()}<div class="quarry-forecast">Final quarry: <strong>${escape(ENEMIES[bossForSeed(state.seed)].name)}</strong><button class="text-button" data-ui="inspect-quarry">Inspect known traits ${icon('book')}</button></div></div>`;
}
const relicInfo = RELICS;

function relicsLine() {
  return state.relics.length ? `<div class="relic-strip">${state.relics.map(r => `<span title="${escape(relicInfo[r]?.text || r)}">${icon('moon')} ${escape(relicInfo[r]?.name || r)}</span>`).join('')}</div>` : '';
}
function isTarget(uid: string) {
  if (!selected) return false;
  return actions().some(a => selected?.kind === 'attack' ? a.type === 'attack' && a.unit === selected.uid && a.target === uid : selected?.kind === 'card' && a.type === 'play' && a.index === selected.index && a.target === uid);
}
function unitLabel(unit: Unit): string {
  const binding = state.allies.findIndex(a => a.uid === unit.uid);
  if (binding >= 0) return `${unit.name} · binding ${binding + 1}`;
  const hostile = state.enemies.findIndex(a => a.uid === unit.uid);
  return hostile >= 0 ? `${unit.name} · hostile ${hostile + 1}` : unit.name;
}
function targetName(uid: string): string {
  if (uid === 'hunter') return 'hunter';
  if (uid === 'all') return 'all targets';
  const target = [...state.allies, ...state.enemies].find(unit => unit.uid === uid);
  return target ? unitLabel(target) : 'hunter';
}

function compactTargetName(uid: string): string {
  if (uid === 'hunter') return 'hunter';
  if (uid === 'all') return 'all targets';
  const binding = state.allies.findIndex(unit => unit.uid === uid);
  if (binding >= 0) return `binding ${binding + 1}`;
  const hostile = state.enemies.findIndex(unit => unit.uid === uid);
  return hostile >= 0 ? `hostile ${hostile + 1}` : 'hunter';
}
// Consequences come from the same pure reducer as committed actions. Never expose drawn cards or rewards.
const previewCache = new Map<string, { text: string; danger: boolean }>();
let activePreviewKey = '';
function selectionGuidance(): string {
  const choice = selected;
  const unit = choice?.kind === 'attack' ? state.allies.find(u => u.uid === choice.uid) : undefined;
  if (choice?.kind === 'attack') return `${unit ? unitLabel(unit) : 'Creature'} selected. Focus or hover a hostile target to read the outcome.`;
  if (choice?.kind === 'card') return `${CARDS[state.hand[choice.index]].name}: focus or hover ${cardTarget(state.hand[choice.index]) === 'ally' ? 'a bound creature' : 'a hostile target'} to read the outcome.`;
  return 'Deploy a binding or play a tool. Select a ready creature, then its target.';
}
function consequencePreview(action: Action): { text: string; danger: boolean } {
  const { state: after, events } = applyActionWithEvents(state, action);
  const target = 'target' in action ? action.target : undefined;
  const sourceUnit = action.type === 'attack' ? state.allies.find(u => u.uid === action.unit) : undefined;
  const label = action.type === 'attack' ? sourceUnit ? unitLabel(sourceUnit) : 'Command' : action.type === 'play' ? CARDS[state.hand[action.index]].name : 'Order';
  const parts: string[] = [];
  const who = (uid: string): string => {
    if (uid === 'hunter') return 'hunter';
    const existing = [...state.allies, ...state.enemies].some(u => u.uid === uid);
    if (existing) return compactTargetName(uid);
    const summoned = events.filter(e => e.type === 'summon' && e.side === 'ally');
    const index = summoned.findIndex(e => e.target === uid);
    return index >= 0 ? `binding ${state.allies.length + index + 1}` : 'target';
  };
  if (action.type === 'play' && CARDS[state.hand[action.index]].type === 'summon') parts.push('binds a creature ready to command');
  const affected = target ? [target] : [...new Set(events.filter(e => e.type === 'hit' && e.target !== 'hunter').map(e => e.target))];
  for (const uid of affected) {
    const hits = events.filter(e => e.type === 'hit' && e.target === uid);
    const lost = hits.reduce((sum, e) => sum + (e.type === 'hit' ? e.hpLost : 0), 0);
    const blocked = hits.reduce((sum, e) => sum + (e.type === 'hit' ? e.blocked : 0), 0);
    const dead = events.some(e => e.type === 'death' && e.target === uid);
    const prefix = target ? '' : `${who(uid)}: `;
    if (hits.length) parts.push(`${prefix}${lost} health damage${dead ? ' (lethal)' : ''}${blocked ? `, ${blocked} blocked` : ''}`);
    const prior = [...state.allies, ...state.enemies].find(u => u.uid === uid);
    const next = [...after.allies, ...after.enemies].find(u => u.uid === uid);
    // Sundering can remove armor before a hit. Read the resolved result rather than reconstructing damage rules.
    if (prior && (next || dead)) {
      const removed = Math.max(0, prior.block - (next?.block || 0));
      if (removed > blocked) parts.push(`removes ${removed} block`);
    }
    if (prior && next && prior.acted && !next.acted) parts.push('command readied');
    if (prior?.intent && next?.intent && JSON.stringify(prior.intent) !== JSON.stringify(next.intent)) parts.push(next.intent.label);
  }
  const totals = new Map<string, { heal: number; ward: number }>();
  for (const event of events) if (event.type === 'heal' || event.type === 'ward') {
    const value = totals.get(event.target) || { heal: 0, ward: 0 };
    value[event.type === 'heal' ? 'heal' : 'ward'] += event.amount;
    totals.set(event.target, value);
  }
  const supportGroups = new Map<string, { ids: string[]; heal: number; ward: number }>();
  for (const [uid, values] of totals) {
    const side = uid === 'hunter' ? 'hunter' : who(uid).startsWith('binding') ? 'bindings' : 'targets';
    const key = `${side}:${values.heal}:${values.ward}`;
    const group = supportGroups.get(key) || { ids: [], ...values };
    group.ids.push(uid); supportGroups.set(key, group);
  }
  for (const values of supportGroups.values()) {
    const prefix = values.ids.length === 1 ? values.ids[0] === target ? '' : `${who(values.ids[0])}: ` : `${values.ids.length} bindings: `;
    const each = values.ids.length > 1 ? ' each' : '';
    if (values.heal) parts.push(`${prefix}restores ${values.heal} health${each}`);
    if (values.ward) parts.push(`${prefix}gains ${values.ward} block${each}`);
  }
  if (action.type === 'play') {
    const effect = CARDS[state.hand[action.index]].effect;
    if (effect === 'heal' && target && !totals.get(target)?.heal) parts.push('restores 0 health (already full)');
    if (['hunterheal','communion','siphon','hunter-heal'].includes(effect || '') && !totals.get('hunter')?.heal) parts.push(`hunter restores 0 health${state.hp === state.maxHp ? ' (already full)' : ''}`);
    const energyGain = after.energy - state.energy + CARDS[state.hand[action.index]].cost;
    if (energyGain > 0) parts.push(`gains ${energyGain} energy`);
  }
  const retaliation = events.filter(e => e.type === 'hit' && e.kind === 'retaliation');
  for (const hit of retaliation) if (hit.type === 'hit') parts.push(`${who(hit.target)} takes ${hit.hpLost} retaliation${events.some(e => e.type === 'death' && e.target === hit.target) ? ' (lethal)' : ''}`);
  const hunterHits = events.filter(e => e.type === 'hit' && e.target === 'hunter');
  const hunterLoss = hunterHits.reduce((sum, e) => sum + (e.type === 'hit' ? e.hpLost : 0), 0);
  if (hunterHits.length) parts.push(`hunter loses ${hunterLoss} health`);
  if (after.phase === 'defeat') parts.push('HUNTER DIES · campaign ends');
  else if (state.phase === 'battle' && ['reward', 'victory'].includes(after.phase)) parts.push(after.phase === 'victory' ? 'final contract cleared' : 'contract cleared');
  if (!parts.length) parts.push(action.type === 'play' ? cardRules(CARDS[state.hand[action.index]]) : 'order available');
  return { text: `${label}${target ? ` → ${compactTargetName(target)}` : ''}: ${parts.join(' · ')}`, danger: after.phase === 'defeat' || retaliation.some(hit => events.some(e => e.type === 'death' && e.target === hit.target)) };
}
function showConsequenceFor(element: Element | null): boolean {
  if (title || settlingCombat || state.phase !== 'battle') return false;
  const button = element?.closest<HTMLButtonElement>('[data-unit], [data-ui="play-card"]');
  let action: Action | undefined;
  if (button?.dataset.unit && selected) {
    const choice = selected;
    action = actions().find(a => choice.kind === 'attack' ? a.type === 'attack' && a.unit === choice.uid && a.target === button.dataset.unit : a.type === 'play' && a.index === choice.index && a.target === button.dataset.unit);
  } else if (button?.dataset.ui === 'play-card') {
    const index = Number(button.dataset.index);
    if (cardTarget(state.hand[index]) === 'none') action = actions().find(a => a.type === 'play' && a.index === index);
  }
  const output = document.getElementById('consequence-preview');
  if (!output) return false;
  const key = action ? JSON.stringify(action) : '';
  if (key === activePreviewKey) return !!action;
  activePreviewKey = key;
  let result: { text: string; danger: boolean } | null = null;
  try { result = action ? previewCache.get(key) || consequencePreview(action) : null; }
  catch { activePreviewKey = ''; output.textContent = 'Read the card and target traits before giving the order.'; return false; }
  if (result) previewCache.set(key, result);
  output.textContent = result?.text || selectionGuidance();
  output.dataset.preview = result ? 'consequence' : 'instruction';
  output.closest('.battle-guidance')?.classList.toggle('danger-preview', !!result?.danger);
  return !!action;
}
function roster(side: 'allies' | 'enemies'): string {
  const units = state[side];
  const enemy = side === 'enemies';
  const dense = units.length >= 3;
  return `<section class="roster ${enemy ? 'enemy-roster' : 'ally-roster'} ${dense ? 'dense-roster' : ''}" aria-label="${enemy ? 'Enemies' : 'Bound creatures'}"><div class="roster-heading"><span class="eyebrow">${enemy ? 'HOSTILE CONTACTS' : 'YOUR BINDINGS'}</span><span>${units.length} / 6</span></div><div class="unit-grid">${Array.from({ length: 6 }, (_, i) => {
    const unit = units[i];
    if (!unit) return `<div class="empty-slot" aria-label="Empty ${enemy ? 'enemy' : 'binding'} slot ${i + 1}"><span>—</span><small>${enemy ? 'No contact' : `Binding ${i + 1} empty`}</small></div>`;
    const target = isTarget(unit.uid);
    const chosen = selected?.kind === 'attack' && selected.uid === unit.uid;
    const intent = unit.intent;
    const targetText = intent ? intent.damage > 0 ? `${intent.damage} damage → ${targetName(intent.target)}${/ignores block/.test(intent.label) ? ' · ignores block' : ''}` : intent.label : 'Intent unknown';
    const visibleIntent = dense && intent && intent.damage > 0 ? `${intent.damage} damage → ${compactTargetName(intent.target)}${/ignores block/.test(intent.label) ? ' · ignores block' : ''}` : targetText;
    return `<article class="unit-frame"><button class="unit ${enemy ? 'enemy' : 'ally'} ${target ? 'valid-target' : ''} ${chosen ? 'selected' : ''} ${!enemy && !unit.acted ? 'ready' : ''}" data-unit="${escape(unit.uid)}" data-focus="unit-${escape(unit.uid)}" aria-label="${escape(unitLabel(unit))}. ${unit.hp} of ${unit.maxHp} health, ${unit.attack} attack${unit.block ? `, ${unit.block} block` : ''}. ${enemy ? escape(targetText) : unit.acted ? 'Command spent.' : 'Ready; select, then choose an enemy.'}${target ? ' Select as target.' : ''}" aria-pressed="${chosen}"><div class="unit-top">${creature(unit.species, unit.color)}<div><strong>${escape(unit.name)}<span class="unit-slot" aria-hidden="true" title="${enemy ? 'Hostile' : 'Binding'} ${i + 1}">${enemy ? 'H' : 'B'}${i + 1}</span></strong><span class="unit-stats">${icon('heart')} ${unit.hp}<small>/${unit.maxHp}</small><span>${icon('battle')}${unit.attack}</span>${unit.block ? `<span class="block-small">${icon('shield')}${unit.block}</span>` : ''}</span></div></div><div class="health-track"><i style="width:${unit.hp / unit.maxHp * 100}%"></i></div><div class="unit-status ${enemy ? 'intent' : ''}">${enemy ? `${icon('battle')}<span title="${escape(targetText)}">${escape(visibleIntent)}</span>` : target ? 'SELECT TARGET' : unit.acted ? `${icon('check')} ${dense ? 'Spent' : 'Command spent'}` : chosen ? (dense ? 'Choose target' : 'CHOOSE HOSTILE TARGET') : (dense ? 'Ready' : 'Ready to command')}</div></button><button class="unit-inspect" data-ui="inspect-unit" data-uid="${escape(unit.uid)}" aria-label="Inspect ${escape(unitLabel(unit))}" title="Inspect traits and intent">i</button></article>`;
  }).join('')}</div>${enemy ? '<div class="rail-note">Intents resolve in order.<br>A fallen marked creature redirects the hit to the hunter.</div>' : '<div class="rail-note">One free command per turn.<br>New bindings can act immediately.</div>'}</section>`;
}
function renderBattle() {
  previewCache.clear();
  activePreviewKey = '';
  const selectionText = selectionGuidance();
  $('scene-ui').innerHTML = `<div class="battle-ui"><div class="battle-guidance ${selected ? 'targeting' : ''}"><span id="consequence-preview" role="status" aria-live="polite" aria-atomic="true">${escape(selectionText)}</span>${selected ? '<button class="text-button" data-ui="cancel">Cancel <kbd>Esc</kbd></button>' : `<button class="text-button" data-ui="log">Combat record ${icon('book')}</button>`}</div>${roster('allies')}<div class="arena-caption" aria-hidden="true"><span>THE BLACK MARCH</span><small>${selected ? 'TARGET ACQUIRED · GIVE THE ORDER' : 'READ THE THREAT. BREAK THE LINE.'}</small></div>${roster('enemies')}</div>`;
  const playable = actions().filter(a => a.type === 'play');
  $('dock').innerHTML = `<div class="hand-area"><div class="hand-heading"><span class="eyebrow">AVAILABLE CARDS <span>${state.hand.length}</span></span><div class="pile-buttons"><button data-ui="draw">Draw <strong>${state.draw.length}</strong></button><button data-ui="discard">Discard <strong>${state.discard.length}</strong></button></div></div><div class="hand-cards">${state.hand.map((id, index) => renderCard(CARDS[id], { handIndex: index, disabled: !playable.some(a => a.type === 'play' && a.index === index), selected: selected?.kind === 'card' && selected.index === index })).join('')}${!state.hand.length ? '<div class="empty-hand">No cards in hand.<br>Use remaining commands, then end your turn.</div>' : ''}</div></div><div class="turn-controls"><div class="energy-orb">${icon('energy')}<strong>${state.energy}</strong><span>energy</span></div><button class="button end-turn" data-action="endTurn" data-focus="end-turn">End turn ${icon('arrow')}<small>Enemy intents resolve · draw 5 · refill energy</small></button><span class="keyboard-hint"><kbd>E</kbd> End turn <span>·</span> <kbd>Esc</kbd> Cancel</span></div>`;
}

function renderCard(card: CardDef, opts: { handIndex?: number; disabled?: boolean; selected?: boolean; reward?: boolean; shop?: boolean; inspect?: boolean } = {}): string {
  const action = opts.handIndex !== undefined ? 'data-ui="play-card"' : opts.reward ? 'data-action="reward"' : opts.shop ? 'data-action="buy"' : 'data-ui="inspect"';
  const price = SHOP_PRICES[card.type];
  const target = cardTarget(card.id);
  const art = toolArtFor(card.id);
  return `<button class="game-card ${card.type} ${opts.selected ? 'selected' : ''} ${opts.disabled ? 'unplayable' : ''} ${opts.handIndex === undefined ? 'large-card' : ''}" ${action} data-index="${opts.handIndex ?? ''}" data-card="${escape(card.id)}" data-focus="${opts.handIndex !== undefined ? `card-${opts.handIndex}` : `card-${escape(card.id)}`}" aria-disabled="${!!opts.disabled}" ${opts.disabled && opts.handIndex === undefined ? 'disabled' : ''} aria-label="${escape(card.name)}, ${card.cost} energy. ${escape(cardRules(card))}${opts.disabled ? '. Currently unavailable.' : ''}"><span class="card-cost">${card.cost}</span><span class="card-art ${art ? 'tool-painted' : ''}" style="--card-color:${escape(card.color)}">${art ? `<canvas data-tool-art="${art}" aria-hidden="true"></canvas>` : ''}${card.type === 'summon' ? creature(card.species, card.color) : icon(card.effect === 'block' ? 'shield' : card.effect === 'heal' ? 'heart' : card.effect === 'draw' ? 'book' : 'energy')}<span class="card-art-ring"></span></span><span class="card-name">${escape(card.name)}</span><span class="card-kind">${card.type === 'summon' ? 'BINDING' : `TOOL${target === 'none' ? '' : ' · CHOOSE TARGET'}`}</span><span class="card-description">${escape(cardRules(card))}</span>${card.type === 'summon' ? `<span class="card-stats">${icon('battle')} ${card.attack} Attack <span>${icon('heart')} ${card.hp} Health</span></span>` : ''}${opts.reward ? `<span class="card-choose">Add to deck ${icon('arrow')}</span>` : opts.shop ? `<span class="card-choose">${icon('gold')} ${price} gold ${icon('arrow')}</span>` : ''}</button>`;
}
function renderRewards() {
  $('scene-ui').innerHTML = `<div class="page-panel reward-panel"><div class="page-intro"><span class="eyebrow">WARRANT CLOSED</span><h1>Take what keeps you alive.</h1><p>Claim one binding or tool. Refuse the reward to keep a tighter deck.</p></div><div class="reward-cards">${state.rewards.map(id => renderCard(CARDS[id], { reward: true })).join('')}</div><button class="button secondary" data-action="reward" data-card="">Leave the salvage ${icon('arrow')}</button><span class="panel-footnote">Permanent addition. Temporary combat bonuses have ended.</span></div>`;
}
function renderCamp() {
  const trainAvailable = actions().some(a => a.type === 'camp' && a.choice === 'train');
  $('scene-ui').innerHTML = `<div class="page-panel"><div class="page-intro"><span class="eyebrow">FIELD SHELTER</span><h1>Prepare for the next warrant.</h1><p>There is time for treatment or training. Choose one.</p></div><div class="choice-grid"><button class="choice-card" data-action="camp" data-choice="rest">${icon('heart')}<h2>Dress your wounds</h2><p>Restore <strong>18 hunter health</strong>, up to your maximum.</p><span>${state.hp} → ${Math.min(state.maxHp, state.hp + 18)} health ${icon('arrow')}</span></button><button class="choice-card" data-ui="train" ${trainAvailable ? '' : 'disabled'}>${icon('book')}<h2>Refine a binding or tool</h2><p>Select a card from your deck. Read the exact improvement before committing.</p><span>${trainAvailable ? 'Choose an upgrade' : 'All cards are already improved'} ${icon('arrow')}</span></button></div></div>`;
}
function openTraining() {
  const eligible = actions().filter((a): a is Extract<Action, { type: 'camp' }> => a.type === 'camp' && a.choice === 'train');
  openDialog('Choose one permanent upgrade', `<p class="dialog-copy">Training ends your time in this shelter. Each entry is one real card in your deck; duplicates can be trained separately. Cancel to return without committing.</p><div class="upgrade-grid">${eligible.map(a => {
    const index = (a as Extract<Action, { type: 'camp' }> & { index?: number }).index;
    if (index === undefined) return '';
    const card = CARDS[state.deck[index]], upgraded = CARDS[card.id + '+'];
    return `<button class="upgrade-entry" data-action="camp" data-choice="train" data-index="${index}"><div class="upgrade-heading">${card.type === 'summon' ? creature(card.species, card.color) : icon('energy')}<span><strong>${escape(card.name)}</strong><small>Deck entry ${index + 1} · ${card.cost} energy</small></span>${icon('arrow')}</div><div class="upgrade-comparison">${card.type === 'summon' ? `<p><span>Attack</span><strong>${card.attack} → ${upgraded.attack}</strong></p><p><span>Health</span><strong>${card.hp} → ${upgraded.hp}</strong></p><small>${escape(card.text)}</small>` : `<p><span>Current</span><small>${escape(card.text)}</small></p><p><span>Improved</span><small>${escape(upgraded.text)}</small></p>`}</div><span class="upgrade-confirm">Train this card ${icon('check')}</span></button>`;
  }).join('')}</div><button class="button secondary full-width" data-ui="close">Return to shelter</button>`, true);
}

function renderShop() {
  const buys = actions().filter((a): a is Extract<Action, { type: 'buy' }> => a.type === 'buy');
  const stock = state.rewards.length ? state.rewards : buys.map(a => a.card);
  $('scene-ui').innerHTML = `<div class="page-panel shop-panel"><div class="page-intro"><span class="eyebrow">THE QUARTERMASTER</span><h1>Tools have a price.</h1><p>Buy what your plan needs. Leave the rest.</p></div><div class="reward-cards">${stock.map(id => renderCard(CARDS[id], { shop: true, disabled: !can({ type: 'buy', card: id }) })).join('')}</div><div class="shop-bottom"><button class="button secondary" data-ui="remove" ${actions().some(a => a.type === 'remove') ? '' : 'disabled'}>Remove a card <span>${icon('gold')}35</span></button><button class="button primary" data-action="leave">Return to the campaign ${icon('arrow')}</button></div><span class="panel-footnote">Bindings cost 55 gold · Tools cost 40 gold · Remove a card for 35 gold</span></div>`;
}
function renderEvent() {
  const symbols: Record<string, string> = { offering: 'moon', forage: 'gold', purge: 'battle', bargain: 'heart', leave: 'shield' };
  const consequences: Record<string, string> = { offering: `${state.hp} → ${Math.max(0, state.hp - 8)} health`, forage: `${state.gold} → ${state.gold + 25} gold`, purge: `${state.deck.length} → ${state.deck.length - 1} cards · lose 4 health`, bargain: `30 gold → +16 health`, leave: 'Continue unchanged' };
  $('scene-ui').innerHTML = `<div class="page-panel event-panel"><div class="page-intro"><span class="eyebrow">A SHRINE WITHOUT A GOD</span><h1>Some bargains outlive their makers.</h1><p>Read the price. Claim only what your campaign needs.</p></div><div class="choice-grid event-choices">${Object.entries(EVENT_CHOICES).map(([id, choice]) => `<button class="choice-card" data-action="event" data-choice="${id}" ${can({ type: 'event', choice: id }) ? '' : 'disabled'}>${icon(symbols[id])}<h2>${escape(choice.name)}</h2><p>${escape(choice.text)}</p><span>${escape(consequences[id] || '')}${icon('arrow')}</span></button>`).join('')}</div></div>`;
}

function renderOutcome() {
  const won = state.phase === 'victory';
  $('scene-ui').innerHTML = `<div class="page-panel outcome-panel"><span class="outcome-emblem">${icon(won ? 'lantern' : 'moon')}</span><div class="page-intro"><span class="eyebrow">${won ? 'FINAL WARRANT CLOSED' : 'CONTRACT FAILED'}</span><h1>${won ? 'The last mark is dead.' : 'The contract claimed its hunter.'}</h1><p>${won ? 'You survived ten contracts. The bindings held. Collect your pay.' : 'Read the combat record, rebuild your method, and take another warrant.'}</p></div><div class="recap"><div><strong>${state.stats.battles}</strong><span>Contracts faced</span></div><div><strong>${state.stats.cardsPlayed}</strong><span>Cards played</span></div><div><strong>${state.stats.damageDealt}</strong><span>Damage dealt</span></div><div><strong>${state.stats.turns}</strong><span>Turns taken</span></div></div>${relicsLine()}<div class="outcome-actions"><button class="button primary" data-ui="new">Take a new contract ${icon('arrow')}</button><button class="button secondary" data-ui="retry">Replay seed ${state.seed}</button></div><span class="panel-footnote">Difficulty: ${['Initiate', 'Hunter', 'Veteran'][state.difficulty]} · Final health: ${state.hp}/${state.maxHp} · Deck: ${state.deck.length} cards</span></div>`;
}

function openDialog(name: string, content: string, wide = false) {
  const dialog = $<HTMLDialogElement>('dialog');
  dialog.className = wide ? 'wide-dialog' : '';
  dialog.innerHTML = `<div class="dialog-head"><h2 id="dialog-title">${escape(name)}</h2><button class="icon-button" data-ui="close" aria-label="Close dialog">${icon('close')}</button></div><div class="dialog-body">${content}</div>`;
  if (!dialog.open) dialog.showModal();
  toolIllustrations.refresh();
}
function closeDialog() { $<HTMLDialogElement>('dialog').close(); }
function openNew() {
  if (settlingCombat) { cancelPresentation(); render(); }
  openDialog('A new campaign', `<p class="dialog-copy">The seed fixes the campaign. Reuse it to test a different deck and method.</p><form id="new-game-form"><label class="field-label" for="seed">Campaign seed <small>Any number or words</small></label><input id="seed" name="seed" type="text" maxlength="64" value="${Math.floor(Math.random() * 9999999)}" autocomplete="off"/><fieldset class="difficulty-options"><legend>Contract difficulty</legend><label><input type="radio" name="difficulty" value="0" checked/><span><strong>Initiate</strong><small>Lower pressure. Learn command timing and target priorities.</small></span></label><label><input type="radio" name="difficulty" value="1"/><span><strong>Hunter</strong><small>Stronger opposition. Less room for wasted orders.</small></span></label><label><input type="radio" name="difficulty" value="2"/><span><strong>Veteran</strong><small>Highest enemy pressure. Every binding must earn its place.</small></span></label></fieldset>${!title && !['victory','defeat'].includes(state.phase) || savedRun && !['victory','defeat'].includes(savedRun.phase) ? '<p class="abandon-notice">Beginning a new campaign replaces your current campaign.</p>' : ''}<button class="button primary full-width" type="submit">Accept the warrant ${icon('arrow')}</button></form>`);
}
function openTutorial() {
  openDialog('Know your tools. Read your quarry.', `<p class="dialog-copy">Keep the hunter alive and defeat the final contract. The arena shows the fight; the side panels show the exact rules.</p><div class="tutorial-steps"><div><span>1</span><section><h3>Spend energy deliberately</h3><p>Start each turn with <strong>5 energy and 5 cards</strong>. A card’s corner shows its cost. Unplayed cards enter discard at turn end. When draw runs out, discard reshuffles.</p></section></div><div><span>2</span><section><h3>Deploy a binding</h3><p>Creature cards occupy one of <strong>6 binding slots</strong>. They remain through the fight. Their cards stay out of your piles while alive; fallen creatures return to discard.</p></section></div><div><span>3</span><section><h3>Give an explicit command</h3><p><strong>Select a ready creature, then an enemy.</strong> One free command per creature each turn, including its arrival turn. Targeted tools also wait for your choice. Use each creature’s <strong>Inspect button (i)</strong> to read traits.</p></section></div><div><span>4</span><section><h3>Read every intent</h3><p>Enemy panels show their next target, damage, guard, or reinforcements. Intents resolve in order when you <strong>End turn</strong>. If a marked creature falls, its attacker hits the hunter. Block expires at your next turn; some enemies explicitly ignore it.</p></section></div></div><div class="tutorial-shortcuts"><kbd>E</kbd> End turn <kbd>Esc</kbd> Cancel / pause <kbd>Tab</kbd> Navigate <kbd>Enter</kbd> Choose</div><button class="button primary full-width" data-ui="learned">Accept field orders ${icon('arrow')}</button>`, true);
}
function openUnit(unit: Unit) {
  const passive = (unit as Unit & { passive?: string }).passive;
  const enemy = state.enemies.some(u => u.uid === unit.uid);
  const intent = unit.intent;
  openDialog(unitLabel(unit), `<div class="unit-dossier">${creature(unit.species, unit.color)}<div><span class="eyebrow">${enemy ? 'HOSTILE DOSSIER' : 'BOUND CREATURE'}</span><h3>${escape(unitLabel(unit))}</h3><p>${unit.hp}/${unit.maxHp} health · ${unit.attack} attack${unit.block ? ` · ${unit.block} block` : ''}</p></div></div>${passive ? `<div class="dossier-rule"><h3>Trait</h3><p>${escape(passive)}</p></div>` : ''}${intent ? `<div class="dossier-rule"><h3>Next intent</h3><p>${escape(intent.label)}</p>${intent.damage > 0 ? `<strong>${intent.damage} damage to ${escape(targetName(intent.target))}.</strong>` : ''}</div>` : `<div class="dossier-rule"><h3>Binding effect</h3><p>${escape(CARDS[unit.cardId]?.text || 'One free command per turn.')}</p><strong>${unit.acted ? 'Command spent this turn.' : 'Ready to command this turn.'}</strong></div>`}<button class="button secondary full-width" data-ui="close">Return to the fight</button>`);
}

function openDeck(pile: 'deck' | 'draw' | 'discard' = 'deck', removing = false) {
  const ids = state[pile];
  const counts = new Map<string, number>();
  ids.forEach(id => counts.set(id, (counts.get(id) || 0) + 1));
  // Draw categories must depend only on public identities/counts, never pile position.
  const grouped = Array.from(counts);
  if (pile === 'draw') grouped.sort(([a], [b]) => a < b ? -1 : a > b ? 1 : 0);
  openDialog(removing ? 'Lighten your deck · 35 gold' : `${pile === 'deck' ? 'Campaign deck' : pile === 'draw' ? 'Draw pile' : 'Discard pile'} · ${ids.length} cards`, `${removing ? '<p class="dialog-copy">Choose one card to remove permanently. This costs 35 gold.</p>' : `<p class="dialog-copy">${pile === 'draw' ? 'Grouped by card, without revealing draw order.' : pile === 'discard' ? 'These cards return when your draw pile reshuffles.' : 'Bindings and tools for this campaign. Living bindings stay out of the draw pile until they fall.'}</p>`}<div class="deck-grid">${grouped.map(([id, count]) => `<div class="deck-entry">${removing ? `<button class="remove-card" data-action="remove" data-index="${state.deck.indexOf(id)}">${creature(CARDS[id].species, CARDS[id].color)}<span><strong>${escape(CARDS[id].name)}</strong><small>${count} in deck · ${CARDS[id].cost} energy</small><p>${escape(CARDS[id].text)}</p></span>${icon('close')}</button>` : `${renderCard(CARDS[id], { inspect: true })}<span class="copy-count">${count} ${count === 1 ? 'copy' : 'copies'}</span>`}</div>`).join('') || '<p class="empty-pile">This pile is empty.</p>'}</div>${pile === 'deck' && !removing && state.relics.length ? `<h3 class="charms-heading">Recovered relics</h3><div class="charm-list">${state.relics.map(r => `<p>${icon('moon')}<span><strong>${escape(relicInfo[r]?.name || r)}</strong><small>${escape(relicInfo[r]?.text || '')}</small></span></p>`).join('')}</div>` : ''}`, true);
}
function openHunter() {
  openDialog(HUNTER_NAME, `<div class="hunter-dossier"><div class="hunter-photo dossier-hunter" aria-hidden="true"></div><section><span class="eyebrow">THE IRON WITNESS · CONTRACT HUNTER</span><h3>${HUNTER_NAME}</h3><p>A field knife. A heavy seal gauntlet. Scars that never quite closed.</p><p>Voss binds what others bury, and answers every warrant in person.</p></section></div><div class="dossier-rule"><h3>Your part in the pact</h3><p>Keep the hunter alive. Tools spend energy; bound creatures take your commands. Hunter health persists between contracts.</p><strong>${title && !savedRun ? 'A fresh campaign begins with 65 health.' : `${state.hp}/${state.maxHp} hunter health · ${state.block} block.`}</strong></div><button class="button secondary full-width" data-ui="close">Return</button>`);
}
type FeedbackContext = {
  build: { version: string; sourceDigest: string | null; channel: 'development' | 'packaged' };
  screen: string;
  run: { seed: number; difficulty: number; phase: GameState['phase']; contract: number; hunterHealth: number; maximumHealth: number; saveSchema: GameState['schema']; rulesGeneration: 1 | 2; deck: string[]; relics: string[]; stats: GameState['stats'] } | null;
};
let feedbackContext: FeedbackContext | null = null;
function openFeedback() {
  feedbackContext = {
    build: { version: VERSION, sourceDigest: BUILD_ID === 'development' ? null : BUILD_ID, channel: BUILD_ID === 'development' ? 'development' : 'packaged' },
    screen: title ? 'title' : state.phase,
    run: title && !savedRun ? null : {
      seed: state.seed, difficulty: state.difficulty, phase: state.phase, contract: state.floor, hunterHealth: state.hp, maximumHealth: state.maxHp,
      saveSchema: state.schema, rulesGeneration: state.schema === 3 ? state.engineKind : 1,
      deck: state.deck.slice(), relics: state.relics.slice(),
      stats: { cardsPlayed: state.stats.cardsPlayed, damageDealt: state.stats.damageDealt, turns: state.stats.turns, battles: state.stats.battles },
    },
  };
  openDialog('Your field report', `<p class="dialog-copy">Optional notes from your campaign. Nothing is sent. Save a report to your device, then share it only if you choose.</p><form id="feedback-form"><div class="feedback-fields"><div><label class="field-label" for="feedback-confusion">What was unclear? <small>Optional</small></label><textarea id="feedback-confusion" name="confusion" maxlength="1000" rows="3" placeholder="A rule, target, or moment that was hard to read…"></textarea></div><div><label class="field-label" for="feedback-choice">Which choices felt meaningful or pointless, if any? <small>Optional</small></label><textarea id="feedback-choice" name="interestingChoice" maxlength="1000" rows="3" placeholder="A meaningful choice, a pointless choice, or none…"></textarea></div></div><label class="field-label" for="feedback-replay">Would you take another campaign? <small>Optional</small></label><select id="feedback-replay" name="replayIntent"><option value="unanswered">Prefer not to answer</option><option value="yes">Yes</option><option value="maybe">Maybe</option><option value="no">No</option></select><p class="feedback-context">The saved report includes game version${feedbackContext.run ? `, campaign seed ${state.seed}, deck, and contract progress` : ''} so your notes have context.</p><button class="button primary full-width" type="submit">Save field report ${icon('arrow')}</button></form>`, true);
}
function exportFeedback(form: HTMLFormElement) {
  if (!feedbackContext) return;
  const data = new FormData(form);
  const text = (name: string) => String(data.get(name) || '').trim().slice(0, 1000);
  const replay = String(data.get('replayIntent') || 'unanswered');
  const report = {
    schema: 1, kind: 'voluntary-player-feedback', source: 'local-export', createdAt: new Date().toISOString(),
    context: feedbackContext,
    responses: { confusion: text('confusion'), interestingChoice: text('interestingChoice'), replayIntent: ['yes','maybe','no','unanswered'].includes(replay) ? replay : 'unanswered' },
  };
  const blob = new Blob([JSON.stringify(report, null, 2) + '\n'], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `hollowpact-field-report-v${VERSION}${feedbackContext.run ? `-seed-${feedbackContext.run.seed}` : ''}.json`;
  document.body.append(link); link.click(); link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1500);
  const status = document.createElement('p'); status.className = 'feedback-saved'; status.setAttribute('role', 'status'); status.textContent = 'Report prepared. Your browser will save the file; nothing was sent.';
  form.querySelector('.feedback-saved')?.remove(); form.append(status);
}
function openSettings() {
  openDialog('Make yourself comfortable', `<div class="setting-row"><label for="mute"><strong>Sound effects</strong><small>Impacts, iron, binding chains, and field signals.</small></label><input type="checkbox" id="mute" ${!settings.mute ? 'checked' : ''}/></div><div class="setting-row"><label for="volume"><strong>Volume</strong><small id="volume-value">${Math.round(settings.volume * 100)}%</small></label><input type="range" id="volume" min="0" max="100" value="${settings.volume * 100}"/></div><div class="setting-row"><label for="motion"><strong>Ambient motion</strong><small>Fog, creature motion, and combat effects.</small></label><input type="checkbox" id="motion" ${settings.motion ? 'checked' : ''}/></div><p class="settings-note">Preferences are stored on this device. Exact targets, intents, and traits are available in the binding and enemy panels.</p><button class="button secondary full-width" data-ui="close">Return</button>`);
}
function openPause() {
  openDialog('Campaign paused', `<p class="dialog-copy">Your campaign saves after every accepted action. Resume whenever you need.</p><div class="pause-buttons"><button class="button primary" data-ui="close">Continue ${icon('arrow')}</button><button class="button secondary" data-ui="menu">Return to title</button><button class="text-button" data-ui="new">Start a new campaign</button></div>`);
}

function selectCard(index: number) {
  const id = state.hand[index];
  const card = CARDS[id];
  if (!card) return;
  if (selected?.kind === 'card' && selected.index === index) { selected = null; render(); return; }
  const available = actions().filter((a): a is Extract<Action, { type: 'play' }> => a.type === 'play' && a.index === index);
  if (!available.length) {
    notify(state.energy < card.cost ? `You need ${card.cost} energy to play ${card.name}.` : card.type === 'summon' && state.allies.length >= 6 ? 'All six binding slots are full.' : 'This card needs a valid target.');
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
    if (ally.acted) { notify(`${unitLabel(ally)} has already been commanded this turn.`); return; }
    if (!actions().some(a => a.type === 'attack' && a.unit === uid)) { notify('No enemy is available to attack.'); return; }
    selected = { kind: 'attack', uid }; sound(); render(); document.querySelector<HTMLElement>('.enemy.valid-target')?.focus();
  } else if (uid !== 'hunter') {
    const enemy = state.enemies.find(u => u.uid === uid);
    if (enemy) notify(`${unitLabel(enemy)} plans ${enemy.intent?.damage || 0} damage to ${targetName(enemy.intent?.target || 'hunter')}. Select a ready companion or a targeted spell to attack.`);
  }
}

function handleClick(event: MouseEvent) {
  const button = (event.target as HTMLElement).closest<HTMLElement>('button');
  if (!button || button.hasAttribute('disabled')) return;
  if (settlingCombat && (button.dataset.unit || button.dataset.action || ['play-card','cancel','train','remove','inspect-unit','inspect-quarry','inspect','draw','discard','deck','log'].includes(button.dataset.ui || ''))) return;
  if (button.dataset.unit) { selectUnit(button.dataset.unit); return; }
  if (button.dataset.action) {
    const type = button.dataset.action;
    let action: Action | null = null;
    if (type === 'travel') action = { type, choice: button.dataset.choice! };
    if (type === 'endTurn') {
      const ready = state.allies.filter(a => !a.acted);
      if (ready.length) {
        openDialog('Unspent commands remain', `<p class="dialog-copy">${ready.length} creature${ready.length === 1 ? ' has' : 's have'} not attacked this turn. Their commands are free.</p><div class="pause-buttons"><button class="button primary" data-ui="close">Return to commands</button><button class="button secondary" data-ui="confirm-end">End turn anyway ${icon('arrow')}</button></div>`); return;
      }
      action = { type };
    }
    if (type === 'reward') action = { type, card: button.dataset.card || null };
    if (type === 'camp') { action = { type, choice: button.dataset.choice as 'rest' | 'train', ...(button.dataset.index !== undefined ? { index: Number(button.dataset.index) } : {}) } as Action; if (button.dataset.choice === 'train') closeDialog(); }
    if (type === 'buy') action = { type, card: button.dataset.card! };
    if (type === 'remove') { action = { type, index: Number(button.dataset.index) }; closeDialog(); }
    if (type === 'leave') action = { type };
    if (type === 'event') action = { type, choice: button.dataset.choice! };
    if (action) dispatch(action);
    return;
  }
  switch (button.dataset.ui) {
    case 'new': openNew(); break;
    case 'resume': if (savedRun) { cancelPresentation(); clearToast(); state = savedRun; title = false; selected = null; render(); sound(); } break;
    case 'retry': closeDialog(); start(state.seed, state.difficulty); break;
    case 'home': if (!title) openPause(); break;
    case 'menu': closeDialog(); cancelPresentation(); clearToast(); title = true; selected = null; render(); break;
    case 'settings': openSettings(); break;
    case 'hunter': openHunter(); break;
    case 'feedback': openFeedback(); break;
    case 'help': openTutorial(); break;
    case 'learned': try { localStorage.setItem(TUTORIAL_KEY, 'yes'); } catch { /* Optional preference. */ } closeDialog(); break;
    case 'close': closeDialog(); break;
    case 'deck': openDeck(); break;
    case 'draw': openDeck('draw'); break;
    case 'discard': openDeck('discard'); break;
    case 'remove': openDeck('deck', true); break;
    case 'train': openTraining(); break;
    case 'inspect-quarry': { const boss = ENEMIES[bossForSeed(state.seed)]; openDialog(boss.name, `<div class="unit-dossier">${creature(boss.species, boss.color)}<div><span class="eyebrow">FINAL QUARRY · FIXED BY SEED</span><h3>${escape(boss.name)}</h3></div></div><div class="dossier-rule"><h3>Known trait</h3><p>${escape(boss.passive || '')}</p></div><button class="button secondary full-width" data-ui="close">Return to field chart</button>`); break; }
    case 'inspect-unit': { const unit = [...state.allies, ...state.enemies].find(u => u.uid === button.dataset.uid); if (unit) openUnit(unit); break; }
    case 'play-card': selectCard(Number(button.dataset.index)); break;
    case 'cancel': selected = null; render(); break;
    case 'confirm-end': closeDialog(); dispatch({ type: 'endTurn' }); break;
    case 'inspect': {
      const card = CARDS[button.dataset.card!];
      if (card) openDialog(card.name, `<div class="inspect-card">${renderCard(card)}</div><p class="dialog-copy">${escape(cardRules(card))}${card.type === 'summon' ? ' Bound creatures can be commanded once each turn for free, including their arrival turn.' : ''}</p><button class="button secondary full-width" data-ui="deck">Return to deck</button>`);
      break;
    }
    case 'log': openDialog('Combat record', `<ol class="battle-log">${state.log.slice().reverse().map(line => `<li>${escape(line)}</li>`).join('') || '<li>No combat recorded.</li>'}</ol>`); break;
    case 'fullscreen': if (!document.fullscreenElement) void document.documentElement.requestFullscreen?.().catch(() => notify('Fullscreen is unavailable in this window.')); else void document.exitFullscreen(); break;
  }
}
document.addEventListener('click', handleClick);
document.addEventListener('focusin', event => showConsequenceFor(event.target instanceof Element ? event.target : null));
document.addEventListener('pointerover', event => {
  if (!showConsequenceFor(event.target instanceof Element ? event.target : null)) showConsequenceFor(document.activeElement);
});
document.addEventListener('pointerout', event => {
  const from = event.target instanceof Element ? event.target.closest('[data-unit], [data-ui="play-card"]') : null;
  if (from && !(event.relatedTarget instanceof Node && from.contains(event.relatedTarget))) showConsequenceFor(document.activeElement);
});
document.addEventListener('submit', event => {
  if ((event.target as HTMLElement).id === 'feedback-form') { event.preventDefault(); exportFeedback(event.target as HTMLFormElement); return; }
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
  if (settlingCombat && !mayAnimateCombat()) finishPresentation(presentationEpoch);
  try { localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings)); } catch { /* Game is usable without persistent settings. */ }
  if (input.id !== 'motion') sound();
});
document.addEventListener('keydown', event => {
  if ($<HTMLDialogElement>('dialog').open) return;
  if (event.target instanceof HTMLInputElement || event.target instanceof HTMLTextAreaElement || event.target instanceof HTMLSelectElement) return;
  if (event.key === 'Escape') { event.preventDefault(); if (selected) { selected = null; render(); } else if (!title) openPause(); }
  if (event.key.toLowerCase() === 'e' && !settlingCombat && !event.repeat && !title && state.phase === 'battle') { event.preventDefault(); document.querySelector<HTMLButtonElement>('[data-action="endTurn"]')?.click(); }
});
$<HTMLDialogElement>('dialog').addEventListener('click', event => {
  const dialog = $<HTMLDialogElement>('dialog');
  if (event.target === dialog) { const r = dialog.getBoundingClientRect(); if (event.clientX < r.left || event.clientX > r.right || event.clientY < r.top || event.clientY > r.bottom) closeDialog(); }
});
document.addEventListener('visibilitychange', () => { if (settlingCombat) finishPresentation(presentationEpoch); });
window.matchMedia('(prefers-reduced-motion: reduce)').addEventListener('change', event => { if (event.matches && settlingCombat) finishPresentation(presentationEpoch); });
window.addEventListener('beforeunload', () => { disposed = true; cancelPresentation(); sceneObserver.disconnect(); toolIllustrations.dispose(); arena?.dispose(); });
render();
