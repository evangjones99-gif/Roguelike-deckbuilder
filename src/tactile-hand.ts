/** Original local card presentation. Root owns identity, legality and reducer.
 * No engine/storage/audio/controller access; no device vibration or art request. */
export interface TactileCardSource {
  readonly key: string;
  readonly cardId: string;
  readonly revision: string;
  readonly handIndex: number;
}
export interface TactilePoint { readonly x: number; readonly y: number }
export interface TactileDestination {
  readonly kind: 'target' | 'deploy' | 'field';
  readonly key: string;
}
export interface TactilePreview { readonly legal: boolean; readonly label: string }
export interface TactileHandHost {
  /** Snapshot the exact card occurrence and current canonical hand revision. */
  identify(card: HTMLElement): TactileCardSource | null;
  /** Must check revision AND occurrence/index/cardId against current state. */
  isCurrent(source: TactileCardSource): boolean;
  /** Root includes modal, turn/presentation lock, energy and phase admission. */
  isInteractionAllowed(source: TactileCardSource): boolean;
  /** Root uses semantic UID/renderer hit ownership or explicit deploy area.
   * This lookup and getPreview must never dispatch, select or mutate rules. */
  resolveDestination(source: TactileCardSource, point: TactilePoint): TactileDestination | null;
  getPreview(source: TactileCardSource, destination: TactileDestination | null): TactilePreview;
  /** Called at most once per released drag, after fresh identity/legality checks.
   * Revalidate the exact legal action here; return true only if reducer accepts.
   * Never reinterpret a stale source index as the current card at that index. */
  commit(source: TactileCardSource, destination: TactileDestination): boolean;
  /** UI feedback only. null clears any root-owned preview. */
  onPreview?(source: TactileCardSource | null, destination: TactileDestination | null, preview: TactilePreview | null): void;
  onError?(error: unknown): void;
}
export interface TactileHandOptions { cardSelector?: string }
export interface TactileHandController { isDragging(): boolean; cancel(): void; dispose(): void }
type Session = {
  sequence: number; pointerId: number; pointerType: string; card: HTMLElement; source: TactileCardSource;
  down: TactilePoint; point: TactilePoint; grab: TactilePoint; width: number; height: number;
  dragging: boolean; released: boolean; attempted: boolean; ghost: HTMLElement | null; label: HTMLElement | null;
  previewKey: string;
};
const owners = new WeakMap<HTMLElement, TactileHandController>();

export function attachTactileHand(root: HTMLElement, host: TactileHandHost, options: TactileHandOptions = {}): TactileHandController {
  owners.get(root)?.dispose();
  const document = root.ownerDocument, view = document.defaultView;
  if (!view) throw new Error('Tactile hand needs an attached document');
  const window = view;
  const selector = options.cardSelector ?? '.hand-cards .game-card[data-index],.game-card[data-index]';
  const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const priorAttribute = root.getAttribute('data-tactile-hand');
  root.setAttribute('data-tactile-hand', '');
  let active: Session | null = null, disposed = false, frame = 0, sequence = 0;
  type Barrier = { sequence: number; source: HTMLElement; pointerType: string; point: TactilePoint; until: number };
  const suppressed = new Map<number, Barrier>();
  const cancelledPointers = new Map<number, { sequence: number; source: HTMLElement; pointerType: string }>();
  const pressSequences = new Map<number, number>();
  const effects = new Set<{ ghost: HTMLElement; source: HTMLElement; timer: number }>();
  const point = (event: PointerEvent): TactilePoint => Object.freeze({ x: event.clientX, y: event.clientY });
  const reduced = () => motion.matches || document.documentElement.dataset.reducedMotion === 'true';
  const guarded = <T>(fn: () => T, fallback: T): T => {
    try { return fn(); } catch (error) { try { host.onError?.(error); } catch {} return fallback; }
  };
  const sourceSnapshot = (card: HTMLElement): TactileCardSource | null => {
    const source = guarded(() => host.identify(card), null);
    if (!source || typeof source.key !== 'string' || !source.key || typeof source.cardId !== 'string' || !source.cardId
      || typeof source.revision !== 'string' || !source.revision || !Number.isInteger(source.handIndex) || source.handIndex < 0) return null;
    return Object.freeze({ key: source.key, cardId: source.cardId, revision: source.revision, handIndex: source.handIndex });
  };
  const permitted = (session: Session) => !disposed && !document.hidden && session.card.isConnected && root.contains(session.card)
    && !document.querySelector('dialog[open]') && guarded(() => host.isCurrent(session.source), false) === true
    && guarded(() => host.isInteractionAllowed(session.source), false) === true;
  const clearEffects = () => {
    for (const effect of effects) { window.clearTimeout(effect.timer); removeGhost(effect.ghost); effect.source.classList.remove('tactile-return'); }
    effects.clear();
  };
  const pruneReleasedBarriers = () => {
    const now = performance.now();
    for (const [pointerId, barrier] of suppressed) if (now > barrier.until) suppressed.delete(pointerId);
    // Pending canceled releases deliberately have no elapsed timeout. A held
    // mouse survives another primary touch and an arbitrarily delayed release.
  };
  const releaseBarrier = (session: Session) => {
    session.released = true; cancelledPointers.delete(session.pointerId);
    suppressed.set(session.pointerId, { sequence: session.sequence, source: session.card, pointerType: session.pointerType, point: session.point, until: performance.now() + 700 });
  };
  const removeGhost = (ghost: HTMLElement) => { (ghost.closest('.tactile-layer') ?? ghost).remove(); };
  const clearPreview = () => { guarded(() => host.onPreview?.(null, null, null), undefined); };
  const observer = new MutationObserver(() => { if (active && !permitted(active)) finish('cancel'); });
  const releaseCapture = (session: Session) => {
    try { if (session.card.hasPointerCapture(session.pointerId)) session.card.releasePointerCapture(session.pointerId); } catch {}
  };
  function finish(reason: 'accepted' | 'return' | 'cancel' | 'tap' | 'scroll', released = false) {
    const session = active; if (!session) return;
    active = null; observer.disconnect(); window.cancelAnimationFrame(frame); frame = 0;
    if (session.dragging || reason === 'cancel') {
      if (released || session.released) releaseBarrier(session);
      else cancelledPointers.set(session.pointerId, { sequence: session.sequence, source: session.card, pointerType: session.pointerType });
    }
    releaseCapture(session);
    session.card.classList.remove('tactile-pressed', 'tactile-source');
    root.classList.remove('tactile-dragging');
    clearPreview();
    const ghost = session.ghost;
    if (!ghost) return;
    if (session.label) session.label.hidden = true;
    if (reason === 'cancel' || reduced()) { removeGhost(ghost); return; }
    if (reason === 'accepted') {
      ghost.classList.add('tactile-accepted');
      const effect = { ghost, source: session.card, timer: 0 };
      effect.timer = window.setTimeout(() => { removeGhost(ghost); effects.delete(effect); }, 120);
      effects.add(effect); return;
    }
    if (!session.card.isConnected) { removeGhost(ghost); return; }
    const rect = session.card.getBoundingClientRect();
    if (!rect.width || !rect.height) { removeGhost(ghost); return; }
    ghost.classList.add('tactile-returning');
    ghost.style.transform = `translate3d(${rect.left}px,${rect.top}px,0)`;
    session.card.classList.add('tactile-return');
    const effect = { ghost, source: session.card, timer: 0 };
    effect.timer = window.setTimeout(() => { removeGhost(ghost); session.card.classList.remove('tactile-return'); effects.delete(effect); }, 160);
    effects.add(effect);
  }
  function makeGhost(session: Session) {
    const ghost = document.createElement('div'); ghost.className = 'tactile-ghost'; ghost.setAttribute('aria-hidden', 'true'); ghost.inert = true;
    const phase = session.card.closest('.phase-battle');
    if (phase) for (const name of ['phase-battle', 'direct-field', 'dense-battle']) if (phase.classList.contains(name)) ghost.classList.add(name);
    ghost.style.width = `${session.width}px`; ghost.style.height = `${session.height}px`;
    const copy = session.card.cloneNode(true) as HTMLElement;
    copy.classList.remove('tactile-pressed', 'tactile-source', 'tactile-return'); copy.classList.add('tactile-ghost-card');
    for (const node of [copy, ...copy.querySelectorAll<HTMLElement>('*')]) {
      for (const attribute of [...node.attributes]) if (/^(id|name|tabindex|autofocus|form|data-(ui|action|unit|uid|focus|index))$/.test(attribute.name) || attribute.name.startsWith('on')) node.removeAttribute(attribute.name);
      node.setAttribute('tabindex', '-1');
    }
    copy.querySelectorAll('script,iframe,object,embed,link,audio,video').forEach(node => node.remove());
    const originalCanvases = session.card.querySelectorAll('canvas'), copies = copy.querySelectorAll('canvas');
    originalCanvases.forEach((canvas, index) => {
      const target = copies[index]; if (!target) return;
      target.width = canvas.width; target.height = canvas.height;
      try { target.getContext('2d')?.drawImage(canvas, 0, 0); } catch { /* Decorative copy cannot block a valid input. */ }
    });
    const layer = document.createElement('div'); layer.className = 'tactile-layer'; layer.setAttribute('aria-hidden', 'true'); layer.inert = true;
    const label = document.createElement('div'); label.className = 'tactile-preview';
    // Retain the actual hand style context; the wrapper is inert and has no
    // layout/scroll padding. Cost/rules text remains cloned ordinary DOM.
    const surface = document.createElement('div'); surface.className = 'hand-cards'; surface.append(copy);
    ghost.append(surface); layer.append(ghost, label); document.body.append(layer); session.ghost = ghost; session.label = label;
  }
  function readPreview(session: Session) {
    const resolved = guarded(() => host.resolveDestination(session.source, session.point), null);
    const destination = resolved && ['target', 'deploy', 'field'].includes(resolved.kind) && typeof resolved.key === 'string' && resolved.key
      ? Object.freeze({ kind: resolved.kind, key: resolved.key }) : null;
    const supplied = guarded(() => host.getPreview(session.source, destination), { legal: false, label: 'Return to hand' });
    const preview = Object.freeze({ legal: destination !== null && supplied?.legal === true, label: typeof supplied?.label === 'string' ? supplied.label.slice(0, 300) : 'Return to hand' });
    return { destination, preview };
  }
  function update(session: Session) {
    if (!session.ghost) return;
    // Keep the visual copy readable at screen edges. Targeting still uses the
    // actual pointer in readPreview; this never changes the action destination.
    const visibleCoordinate = (wanted: number, extent: number, space: number) => {
      const margin = Math.min(8, Math.max(0, (space - extent) / 2));
      return Math.max(margin, Math.min(Math.max(margin, space - extent - margin), wanted));
    };
    const x = visibleCoordinate(session.point.x - session.grab.x, session.width, window.innerWidth);
    const y = visibleCoordinate(session.point.y - session.grab.y, session.height, window.innerHeight);
    session.ghost.style.transform = `translate3d(${x}px,${y}px,0)`;
    const { destination, preview } = readPreview(session);
    session.ghost.dataset.legal = String(preview.legal);
    if (session.label) {
      session.label.textContent = preview.label;
      session.label.style.maxWidth = `${Math.max(0, Math.min(260, window.innerWidth - 16))}px`;
      const label = session.label.getBoundingClientRect();
      const left = Math.max(8, Math.min(window.innerWidth - label.width - 8, x + (session.width - label.width) / 2));
      const below = y + session.height + 8;
      const desiredTop = below + label.height <= window.innerHeight - 8 ? below : y - label.height - 8;
      const top = Math.max(8, Math.min(window.innerHeight - label.height - 8, desiredTop));
      // The label follows the visible copy; targeting remains pointer-based.
      session.label.style.transform = `translate3d(${left}px,${top}px,0)`;
    }
    const key = JSON.stringify([destination?.kind, destination?.key, preview.legal, preview.label]);
    if (key !== session.previewKey) { session.previewKey = key; guarded(() => host.onPreview?.(session.source, destination, preview), undefined); }
  }
  function animate() {
    const session = active; if (!session?.dragging) return;
    if (!permitted(session)) { finish('cancel'); return; }
    update(session); if (active === session) frame = window.requestAnimationFrame(animate);
  }
  function observePress(event: PointerEvent) {
    if (disposed || event.button !== 0 || !event.isPrimary) return;
    pruneReleasedBarriers();
    // Observe presses anywhere, not just in the hand. The next ordinary board
    // click from this pointer must not inherit its completed drag's barrier.
    // An unrelated device's primary press never clears this pointer's records.
    pressSequences.set(event.pointerId, ++sequence);
    cancelledPointers.delete(event.pointerId); suppressed.delete(event.pointerId);
  }
  function down(event: PointerEvent) {
    if (disposed || event.button !== 0 || !event.isPrimary) return;
    if (active) { finish('cancel'); return; }
    const card = event.target instanceof Element ? event.target.closest<HTMLElement>(selector) : null;
    if (!card || !root.contains(card) || card.closest('dialog') || card.matches(':disabled,[aria-disabled="true"]')) return;
    const source = sourceSnapshot(card); if (!source) return;
    const rect = card.getBoundingClientRect(), down = point(event);
    if (!rect.width || !rect.height) return;
    const session: Session = { sequence: pressSequences.get(event.pointerId) ?? ++sequence, pointerId: event.pointerId, pointerType: event.pointerType, card, source, down, point: down,
      grab: Object.freeze({ x: down.x - rect.left, y: down.y - rect.top }), width: rect.width, height: rect.height,
      dragging: false, released: false, attempted: false, ghost: null, label: null, previewKey: '' };
    if (!permitted(session)) return;
    clearEffects(); active = session; card.classList.add('tactile-pressed');
    observer.observe(document.documentElement, { subtree: true, childList: true, attributes: true,
      attributeFilter: ['open', 'hidden', 'disabled', 'aria-busy', 'data-index', 'data-card', 'data-revision', 'data-reduced-motion'] });
    // No preventDefault/capture before threshold: ordinary click and pan-x work.
  }
  function move(event: PointerEvent) {
    const session = active; if (!session || event.pointerId !== session.pointerId) return;
    if (!permitted(session) || session.pointerType === 'mouse' && !(event.buttons & 1)) { finish('cancel'); return; }
    session.point = point(event);
    if (!session.dragging) {
      const dx = event.clientX - session.down.x, dy = event.clientY - session.down.y;
      if (session.pointerType === 'touch') {
        if (Math.abs(dx) >= 12 && Math.abs(dx) >= Math.abs(dy)) { finish('scroll'); return; }
        if (dy >= 12) { finish('scroll'); return; }
        if (dy > -12 || Math.abs(dy) < Math.abs(dx) * 1.25) return;
      } else if (Math.hypot(dx, dy) < 7) return;
      session.dragging = true;
      try { session.card.setPointerCapture(session.pointerId); } catch { finish('cancel'); return; }
      makeGhost(session); session.card.classList.remove('tactile-pressed'); session.card.classList.add('tactile-source'); root.classList.add('tactile-dragging');
      update(session); if (active === session && !disposed) frame = window.requestAnimationFrame(animate);
    }
    event.preventDefault();
  }
  function up(event: PointerEvent) {
    pressSequences.delete(event.pointerId);
    const cancelled = cancelledPointers.get(event.pointerId);
    if (cancelled) { cancelledPointers.delete(event.pointerId); suppressed.set(event.pointerId, { ...cancelled, point: point(event), until: performance.now() + 700 }); event.preventDefault(); return; }
    const session = active; if (!session || event.pointerId !== session.pointerId) return;
    session.point = point(event);
    if (!session.dragging) {
      if (!permitted(session)) { releaseBarrier(session); event.preventDefault(); finish('cancel', true); }
      else finish('tap', true);
      return;
    }
    event.preventDefault();
    // Install before any root callback: commit/preview may synchronously cancel,
    // change revision, rerender children, or trigger another release callback.
    releaseBarrier(session);
    // Release resolves afresh; cached hover, DOM index or painted ghost is never authority.
    if (!permitted(session) || active !== session) { if (active === session) finish('return', true); return; }
    const { destination, preview } = readPreview(session);
    let accepted = false;
    if (active === session && !session.attempted && destination && preview.legal && permitted(session) && active === session) {
      session.attempted = true;
      accepted = guarded(() => host.commit(session.source, destination), false) === true;
    }
    if (active === session) finish(accepted ? 'accepted' : 'return', true);
  }
  function pointerCancel(event: PointerEvent) {
    if (active?.pointerId === event.pointerId) finish('cancel');
    // Pointercancel is a terminal UA marker; unlike Escape it cannot later
    // produce that gesture's ordinary native click. Retire only this pointer.
    cancelledPointers.delete(event.pointerId);
    pressSequences.delete(event.pointerId);
  }
  function lostCapture(event: PointerEvent) { if (active?.dragging && active.pointerId === event.pointerId) finish('cancel'); }
  function click(event: MouseEvent) {
    if (event.detail === 0) return;
    pruneReleasedBarriers();
    let pointerId: number | undefined;
    if (event instanceof PointerEvent && suppressed.has(event.pointerId)) pointerId = event.pointerId;
    else if (!(event instanceof PointerEvent) && event.target instanceof Node) {
      const target = event.target;
      // Older hosts may deliver MouseEvent with no pointerId, even when a
      // synchronous commit replaced the source DOM before the native click.
      // Match the released location (within CSS-pixel rounding) and optional
      // device hint. This bounded compatibility heuristic needs real-UA tests;
      // it cannot reconstruct pointer/session identity absent from MouseEvent.
      const capabilities = (event as MouseEvent & { sourceCapabilities?: { firesTouchEvents?: boolean } | null }).sourceCapabilities;
      const touchHint = capabilities?.firesTouchEvents;
      pointerId = [...suppressed].find(([, barrier]) => {
        if (touchHint !== undefined && touchHint !== (barrier.pointerType === 'touch')) return false;
        return barrier.source.contains(target) || Math.abs(event.clientX - barrier.point.x) <= 2 && Math.abs(event.clientY - barrier.point.y) <= 2;
      })?.[0];
    }
    if (pointerId === undefined) return;
    suppressed.delete(pointerId); event.preventDefault(); event.stopImmediatePropagation();
  }
  function key(event: KeyboardEvent) {
    if (event.ctrlKey || event.metaKey || event.altKey || event.isComposing || event.key !== 'Escape' || !active?.dragging) return;
    event.preventDefault(); event.stopImmediatePropagation(); finish('cancel');
  }
  function cancel() { finish('cancel'); clearEffects(); }
  function visibility() { if (document.hidden) cancel(); }
  function nativeDrag(event: DragEvent) { if (active && event.target instanceof Node && active.card.contains(event.target)) event.preventDefault(); }
  document.addEventListener('pointerdown', observePress, true);
  root.addEventListener('pointerdown', down);
  root.addEventListener('dragstart', nativeDrag);
  document.addEventListener('pointermove', move, { passive: false });
  document.addEventListener('pointerup', up, { passive: false });
  document.addEventListener('pointercancel', pointerCancel);
  document.addEventListener('lostpointercapture', lostCapture);
  document.addEventListener('click', click, true);
  // Window capture precedes root's existing document Escape capture handler.
  window.addEventListener('keydown', key, true);
  document.addEventListener('visibilitychange', visibility);
  window.addEventListener('resize', cancel);
  window.addEventListener('blur', cancel);
  motion.addEventListener('change', cancel);
  const controller: TactileHandController = { isDragging: () => active?.dragging ?? false, cancel, dispose() {
    if (disposed) return;
    cancel(); disposed = true; observer.disconnect(); cancelledPointers.clear(); suppressed.clear(); pressSequences.clear();
    root.removeEventListener('pointerdown', down); root.removeEventListener('dragstart', nativeDrag);
    document.removeEventListener('pointerdown', observePress, true);
    document.removeEventListener('pointermove', move); document.removeEventListener('pointerup', up);
    document.removeEventListener('pointercancel', pointerCancel); document.removeEventListener('lostpointercapture', lostCapture);
    document.removeEventListener('click', click, true); window.removeEventListener('keydown', key, true);
    document.removeEventListener('visibilitychange', visibility); window.removeEventListener('resize', cancel); window.removeEventListener('blur', cancel); motion.removeEventListener('change', cancel);
    if (priorAttribute === null) root.removeAttribute('data-tactile-hand'); else root.setAttribute('data-tactile-hand', priorAttribute);
    if (owners.get(root) === controller) owners.delete(root);
  } };
  owners.set(root, controller); return controller;
}
