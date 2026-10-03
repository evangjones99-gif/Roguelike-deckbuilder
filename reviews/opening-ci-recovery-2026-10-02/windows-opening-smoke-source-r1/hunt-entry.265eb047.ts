/** Concise hunt entry presentation. No engine, storage, network or audio ownership. */
import './hunt-entry.css';

export type HuntDifficulty = 0 | 1 | 2;
export interface SavedHuntSummary { contract: number; hp: number; maxHp?: number }
export interface HuntTitleOptions {
  saved?: SavedHuntSummary | null;
  saveNotice?: string;
  soundEnabled: boolean;
}
export interface HuntContractOptions {
  seed: string;
  difficulty: HuntDifficulty;
  replaceSaved?: SavedHuntSummary | null;
}
export type HuntContractResult =
  | { ok: true; seed: string; difficulty: HuntDifficulty; replacesSaved: boolean }
  | { ok: false; message: string };
export interface HuntEntryHost {
  uiCue?: (back?: boolean) => void;
  audioEnabled: () => boolean;
  /** Off by default: existing confirmation cues are too strong for every hover. */
  hoverAudio?: boolean;
}
const entities: Record<string, string> = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };
const html = (value: unknown): string => String(value).replace(/[&<>"']/g, char => entities[char]!);
const count = (value: number): string => Number.isFinite(value) ? String(Math.max(0, Math.trunc(value))) : '—';
const arrow = '<span class="hunt-action-arrow" aria-hidden="true">↗</span>';
const pressure = [
  { name: 'Initiate', hint: 'Lower enemy pressure.' },
  { name: 'Hunter', hint: 'Greater enemy pressure.' },
  { name: 'Veteran', hint: 'Highest enemy pressure.' }
] as const;

/** Root decides whether a save is active; terminal campaigns are not resume buttons. */
export function renderHuntTitle(options: HuntTitleOptions): string {
  const saved = options.saved;
  return `<section class="hunt-entry" data-hunt-entry aria-labelledby="hunt-wordmark">
    <div class="hunt-entry-art" aria-hidden="true"></div>
    <div class="hunt-entry-copy">
      <p class="hunt-kicker">The Black March</p>
      <h1 class="hunt-wordmark" id="hunt-wordmark">HOLLOW<span>PACT</span></h1>
      <p class="hunt-invitation">Hunt the horrors.<br>Make them fight for you.</p>
      <div class="hunt-title-actions">
        ${saved ? `<button type="button" class="hunt-action hunt-primary" data-ui="resume">Continue the hunt ${arrow}<small>Contract ${count(saved.contract)} · ${count(saved.hp)} health</small></button>` : ''}
        <button type="button" class="hunt-action ${saved ? 'hunt-secondary' : 'hunt-primary'}" data-ui="new">${saved ? 'New hunt' : 'Take a contract'} ${arrow}</button>
      </div>
      ${options.saveNotice ? `<p class="hunt-save-notice" role="status">${html(options.saveNotice)}</p>` : ''}
      <button type="button" class="hunt-hunter-name" data-ui="hunter"><span>Marek Voss</span><small>Pact hunter</small></button>
    </div>
    <nav class="hunt-entry-tools" aria-label="Hunt tools">
      <button type="button" data-ui="settings">Settings <span class="hunt-sound-status">· Sound ${options.soundEnabled ? 'on' : 'off'}</span></button>
      <button type="button" data-ui="help">How to play</button>
      <button type="button" data-ui="feedback">Field report</button>
      <button type="button" data-ui="fullscreen">Fullscreen</button>
    </nav>
  </section>`;
}

/** Pass one freshly generated seed per opening; no random source inside this renderer. */
export function renderHuntContract(options: HuntContractOptions): string {
  const difficulty = pressure[options.difficulty] ? options.difficulty : 0;
  return `<form class="hunt-contract" data-hunt-entry id="new-game-form">
    <p class="hunt-contract-invitation">Choose your pressure. Take the hunt.</p>
    <fieldset class="hunt-pressure"><legend>Contract difficulty</legend>
      ${pressure.map((choice, index) => `<label class="hunt-pressure-choice"><input type="radio" name="difficulty" value="${index}" ${difficulty === index ? 'checked' : ''}/><span><strong>${choice.name}</strong><small>${choice.hint}</small></span></label>`).join('')}
    </fieldset>
    <div class="hunt-optional-controls">
      <button type="button" class="hunt-disclosure" data-hunt-disclosure="hunt-seed-panel" aria-controls="hunt-seed-panel" aria-expanded="false">Set a seed <span aria-hidden="true">+</span></button>
      <button type="button" class="hunt-disclosure" data-hunt-disclosure="hunt-rules-panel" aria-controls="hunt-rules-panel" aria-expanded="false">Your starting kit <span aria-hidden="true">+</span></button>
    </div>
    <div class="hunt-detail" id="hunt-seed-panel" hidden>
      <label for="seed">Campaign seed</label>
      <input type="text" name="seed" id="seed" value="${html(options.seed)}" maxlength="64" autocomplete="off" spellcheck="false" aria-describedby="hunt-seed-note"/>
      <p id="hunt-seed-note">Reuse a seed to replay the same campaign. Numbers or words; blank makes a fresh hunt.</p>
    </div>
    <div class="hunt-detail" id="hunt-rules-panel" hidden>
      <p><strong>65 health. 12 cards.</strong></p>
      <p>Bind creatures. Command each once per turn, for free. Spend energy on cards.</p>
    </div>
    ${options.replaceSaved ? `<label class="hunt-replace"><input type="checkbox" name="replaceSaved" value="yes" required/><span>Replace my saved hunt<small>Contract ${count(options.replaceSaved.contract)} · ${count(options.replaceSaved.hp)} health. This cannot be undone.</small></span></label>` : ''}
    <p class="hunt-form-error" id="hunt-form-error" role="alert" tabindex="-1" hidden></p>
    <div class="hunt-contract-actions"><button type="submit" class="hunt-action hunt-primary">Accept contract ${arrow}</button><button type="button" class="hunt-action hunt-secondary" data-ui="close">Cancel</button></div>
  </form>`;
}

/** Validate complete typed singleton fields BEFORE root closes a dialog or saves. */
export function readHuntContractForm(form: HTMLFormElement, options: { replacementRequired: boolean }): HuntContractResult {
  const reject = (message: string): HuntContractResult => ({ ok: false, message });
  let fields: FormData;
  try { fields = new FormData(form); }
  catch { return reject('Choose your hunt again.'); }
  const allowed = new Set(options.replacementRequired ? ['seed', 'difficulty', 'replaceSaved'] : ['seed', 'difficulty']);
  for (const name of fields.keys()) if (!allowed.has(name)) return reject('Close this form and choose your hunt again.');
  const seeds = fields.getAll('seed'), difficulties = fields.getAll('difficulty');
  if (seeds.length !== 1 || typeof seeds[0] !== 'string' || seeds[0].length > 64) return reject('Use one seed of 64 characters or fewer.');
  if (difficulties.length !== 1 || !['0', '1', '2'].some(value => difficulties[0] === value)) return reject('Choose one difficulty.');
  const replacement = fields.getAll('replaceSaved');
  if (options.replacementRequired && (replacement.length !== 1 || replacement[0] !== 'yes')) return reject('Check “Replace my saved hunt” to begin.');
  if (!options.replacementRequired && replacement.length) return reject('Close this form and choose your hunt again.');
  return { ok: true, seed: seeds[0], difficulty: Number(difficulties[0]) as HuntDifficulty, replacesSaved: options.replacementRequired };
}

export function showHuntContractError(form: HTMLFormElement, message: string): void {
  const error = form.querySelector<HTMLElement>('#hunt-form-error');
  if (!error) return;
  error.textContent = message; error.hidden = false; error.focus();
}
export function focusHuntContract(form: HTMLFormElement): void {
  form.querySelector<HTMLInputElement>('input[name="difficulty"]:checked')?.focus();
}

const attached = new WeakMap<HTMLElement, () => void>();
/** Ordinary buttons work with the existing keyboard/controller adapter; no nested modal. */
export function attachHuntEntry(root: HTMLElement, host: HuntEntryHost): () => void {
  attached.get(root)?.();
  let disposed = false, lastCue = -Infinity, lastHover = -Infinity;
  const audioEnabled = (): boolean => { try { return host.audioEnabled(); } catch { return false; } };
  const cue = (back = false, hover = false): void => {
    if (disposed || !host.uiCue || !audioEnabled()) return;
    const now = performance.now();
    if (now - lastCue < 160 || hover && now - lastHover < 650) return;
    lastCue = now; if (hover) lastHover = now;
    // Root's dialog-open cancellation completes before this optional local cue.
    queueMicrotask(() => { if (!disposed && audioEnabled()) { try { host.uiCue?.(back); } catch { /* Optional sound cannot interrupt entry. */ } } });
  };
  const owned = (event: Event): HTMLElement | null => {
    const target = event.target instanceof Element ? event.target : null;
    const element = target?.closest<HTMLElement>('[data-hunt-entry]');
    return element && root.contains(element) ? element : null;
  };
  const click = (event: MouseEvent): void => {
    const container = owned(event); if (!container) return;
    const button = event.target instanceof Element ? event.target.closest<HTMLButtonElement>('button') : null;
    if (!button || button.disabled || !container.contains(button)) return;
    const id = button.dataset.huntDisclosure;
    if (id) {
      const panel = container.querySelector<HTMLElement>(`#${id === 'hunt-seed-panel' ? 'hunt-seed-panel' : id === 'hunt-rules-panel' ? 'hunt-rules-panel' : 'unmatched-hunt-panel'}`);
      if (!panel) return;
      const expanded = button.getAttribute('aria-expanded') !== 'true';
      panel.hidden = !expanded; button.setAttribute('aria-expanded', String(expanded));
      const mark = button.querySelector<HTMLElement>('[aria-hidden="true"]'); if (mark) mark.textContent = expanded ? '−' : '+';
      if (expanded && id === 'hunt-seed-panel') panel.querySelector<HTMLInputElement>('#seed')?.focus();
      cue(!expanded); return;
    }
    cue(button.dataset.ui === 'close');
  };
  const change = (event: Event): void => {
    if (!owned(event) || !(event.target instanceof HTMLInputElement)) return;
    if (['difficulty', 'replaceSaved'].includes(event.target.name)) cue();
  };
  const hover = (event: PointerEvent): void => {
    if (!host.hoverAudio || !event.isTrusted || event.pointerType !== 'mouse' || !owned(event)) return;
    const target = event.target instanceof Element ? event.target.closest<HTMLElement>('button,.hunt-pressure-choice') : null;
    if (!target || event.relatedTarget instanceof Node && target.contains(event.relatedTarget)) return;
    cue(false, true);
  };
  root.addEventListener('click', click); root.addEventListener('change', change); root.addEventListener('pointerover', hover);
  const dispose = (): void => {
    if (disposed) return; disposed = true;
    root.removeEventListener('click', click); root.removeEventListener('change', change); root.removeEventListener('pointerover', hover);
    if (attached.get(root) === dispose) attached.delete(root);
  };
  attached.set(root, dispose); return dispose;
}
