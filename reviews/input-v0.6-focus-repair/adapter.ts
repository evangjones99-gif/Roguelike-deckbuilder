/** Local renderer input adapter. No engine, save, network, or device identity access. */
export type InputMode = 'keyboard' | 'controller' | 'pointer';
export type Direction = 'up' | 'down' | 'left' | 'right';
export type Phase = 'title' | 'map' | 'battle' | 'reward' | 'camp' | 'shop' | 'event' | 'victory' | 'defeat';
export interface InputContext {
  phase: Phase;
  settling: boolean;
  dialog: HTMLElement | null;
  targeting: boolean;
}
export interface InputHost {
  getContext(): InputContext;
  activate(element: HTMLElement): void;
  back(): void;
  inspect(element: HTMLElement): void;
  endTurn(): void;
  pause(): void;
  onInputMode?(mode: InputMode): void;
}
export interface PadState {
  index: number;
  connected: boolean;
  mapping: string;
  axes: readonly number[];
  buttons: readonly { pressed?: boolean; value?: number }[];
}
export type InputIntent =
  | { type: 'move'; direction: Direction }
  | { type: 'region'; step: -1 | 1 }
  | { type: 'confirm' | 'back' | 'inspect' | 'endTurn' | 'pause' };
const finite = (value: unknown, fallback = 0) => typeof value === 'number' && Number.isFinite(value) ? value : fallback;
const axisDirection = (x: number, y: number): Direction => Math.abs(x) > Math.abs(y) ? x > 0 ? 'right' : 'left' : y > 0 ? 'down' : 'up';

/** Pure device decoder; activation never repeats. Independent of arena motion. */
export class PadDecoder {
  private index: number | null = null;
  private armed = false;
  private pauseReady = false;
  private held: boolean[] = [];
  private direction: Direction | null = null;
  private repeatAt = 0;
  private lastTime = -1;
  reset(): void {
    this.index = null; this.armed = false; this.pauseReady = false; this.held = [];
    this.direction = null; this.repeatAt = 0; this.lastTime = -1;
  }
  decode(pad: PadState | null, now: number, allowed = true): InputIntent[] {
    if (!pad || !pad.connected || pad.mapping !== 'standard' || !Number.isInteger(pad.index) || pad.index < 0 || pad.index > 31 || !Number.isFinite(now) || now < 0) {
      this.reset(); return [];
    }
    if (this.index !== pad.index || now < this.lastTime) { this.reset(); this.index = pad.index; }
    this.lastTime = now;
    const held = Array.from({length: 17}, (_, i) => {
      const button = pad.buttons[i];
      return button?.pressed === true || finite(button?.value) >= (this.held[i] ? .4 : .6);
    });
    const x = Math.max(-1, Math.min(1, finite(pad.axes[0]))), y = Math.max(-1, Math.min(1, finite(pad.axes[1])));
    const neutral = !held.some(Boolean) && Math.max(Math.abs(x), Math.abs(y)) < .3;
    const edge = (index: number) => held[index] && !this.held[index];
    // A paused presentation may open the host's safe pause route, but cannot queue gameplay.
    if (!allowed) {
      const pause = (this.armed || this.pauseReady) && edge(9);
      if (neutral) this.pauseReady = true;
      if (pause) this.pauseReady = false;
      this.armed = false; this.held = held; this.direction = null; this.repeatAt = 0;
      return pause ? [{type: 'pause'}] : [];
    }
    if (!this.armed) {
      this.held = held;
      if (neutral) { this.armed = true; this.pauseReady = true; }
      return [];
    }
    let intent: InputIntent | null = null;
    if (edge(1)) intent = {type: 'back'};
    else if (edge(9)) intent = {type: 'pause'};
    else if (edge(0)) intent = {type: 'confirm'};
    else if (edge(2)) intent = {type: 'inspect'};
    else if (edge(3)) intent = {type: 'endTurn'};
    else if (edge(4)) intent = {type: 'region', step: -1};
    else if (edge(5)) intent = {type: 'region', step: 1};
    const vertical = held[12] !== held[13] ? held[12] ? 'up' : 'down' : null;
    const horizontal = held[14] !== held[15] ? held[14] ? 'left' : 'right' : null;
    let direction: Direction | null = vertical || horizontal;
    if (!direction && Math.max(Math.abs(x), Math.abs(y)) >= .55) direction = axisDirection(x,y);
    else if (!direction && Math.max(Math.abs(x), Math.abs(y)) >= .3 && this.direction) {
      const retained = this.direction === 'left' ? x < 0 : this.direction === 'right' ? x > 0 : this.direction === 'up' ? y < 0 : y > 0;
      direction = retained ? this.direction : null;
    }
    if (direction && !intent && (direction !== this.direction || now >= this.repeatAt)) {
      intent = {type: 'move', direction};
      this.repeatAt = now + (direction !== this.direction ? 350 : 100);
    }
    if (!direction) this.repeatAt = 0;
    this.direction = direction;
    this.held = held;
    return intent ? [intent] : [];
  }
}

export interface InputOptions {
  document?: Document;
  window?: Window;
  readPads?: () => readonly (PadState | null)[];
  autoPoll?: boolean;
}
interface Region { key: string; nodes: HTMLElement[] }
export interface InputAdapter { pollOnce(now: number): void; dispose(): void }

export function createInputAdapter(host: InputHost, options: InputOptions = {}): InputAdapter {
  const doc = options.document || document, win = options.window || window;
  const decoder = new PadDecoder();
  // Seed focus once; lifecycle events govern thereafter. Never poll unstable hasFocus values.
  let windowFocused = true;
  try { windowFocused = doc.hasFocus(); } catch { /* Missing focus API retains event-based fallback. */ }
  let disposed = false, mode: InputMode | null = null;
  let frame: number | null = null, idleTimer: number | null = null;
  const remembered = new Map<string, string>();
  const readPads = options.readPads || (() => win.navigator.getGamepads?.() || []);
  const context = (): InputContext | null => { try { return host.getContext(); } catch { return null; } };
  const call = (callback: () => void) => { try { callback(); } catch { /* Optional input cannot compromise canonical UI/state. */ } };
  const markMode = (next: InputMode) => {
    if (mode === next) return;
    mode = next; call(() => host.onInputMode?.(next));
  };
  const visible = (node: HTMLElement) => {
    if ((node instanceof HTMLButtonElement || node instanceof HTMLInputElement || node instanceof HTMLSelectElement || node instanceof HTMLTextAreaElement) && node.disabled) return false;
    return node.getClientRects().length > 0 && win.getComputedStyle(node).visibility !== 'hidden' && !node.closest('[hidden],[inert],[aria-hidden="true"]');
  };
  const nodes = (root: ParentNode, selector: string) => Array.from(root.querySelectorAll<HTMLElement>(selector)).filter(visible);
  const focusKey = (node: HTMLElement) => node.dataset.focus || (node.id ? `id:${node.id}` : node.dataset.unit ? `unit:${node.dataset.unit}` : node.dataset.ui ? `ui:${node.dataset.ui}:${node.dataset.card || ''}` : '');
  const focus = (node: HTMLElement | undefined, region?: Region) => {
    if (!node || !node.isConnected || !visible(node)) return false;
    node.focus({preventScroll: true});
    node.scrollIntoView({block: 'nearest', inline: 'nearest', behavior: 'auto'});
    if (region) remembered.set(region.key, focusKey(node));
    return doc.activeElement === node;
  };
  function regions(ctx: InputContext): Region[] {
    if (ctx.dialog) return [{key:'dialog',nodes:nodes(ctx.dialog,'button,input:not([type="hidden"]),select,textarea,[tabindex="0"]')}];
    if (ctx.targeting) return [{key:'targets',nodes:nodes(doc,'.unit.valid-target,.hunter-hud.valid-target button')}];
    if (ctx.phase === 'battle') return [
      {key:'hand',nodes:nodes(doc,'.hand-cards button')},
      {key:'bindings',nodes:nodes(doc,'.ally')},
      {key:'hostiles',nodes:nodes(doc,'.enemy')},
      {key:'turn',nodes:nodes(doc,'.turn-controls button')},
      {key:'tools',nodes:nodes(doc,'#topbar button,#hud button,.pile-buttons button,[data-ui="log"],#footer button')},
    ].filter(region=>region.nodes.length);
    return [
      {key:'main',nodes:nodes(doc.querySelector('#scene-ui') || doc,'button,input:not([type="hidden"]),select,textarea')},
      {key:'tools',nodes:nodes(doc,'#topbar button,#hud button,#footer button')},
    ].filter(region=>region.nodes.length);
  }
  function current(list: Region[]): { region: Region; index: number } | null {
    const region = list.find(item=>item.nodes.includes(doc.activeElement as HTMLElement)) || list[0];
    if (!region?.nodes.length) return null;
    return {region,index: Math.max(0,region.nodes.indexOf(doc.activeElement as HTMLElement))};
  }
  function focusRegion(list: Region[], key: string) {
    const region = list.find(item=>item.key === key);
    return region ? focus(region.nodes.find(node=>focusKey(node) === remembered.get(key)) || region.nodes[0],region) : false;
  }
  function switchRegion(ctx: InputContext, step: -1 | 1) {
    const list = regions(ctx), active = current(list);
    if (!active) return;
    const index = list.indexOf(active.region), destination = list[(index + step + list.length) % list.length];
    focusRegion(list,destination.key);
  }
  function adjustWidget(node: HTMLElement, direction: Direction): boolean {
    if (node instanceof HTMLInputElement && node.type === 'range') {
      const step = Number(node.step), increment = Math.max(1,Math.round(10/(Number.isFinite(step)&&step>0?step:1)));
      try { if (direction === 'up' || direction === 'right') node.stepUp(increment); else node.stepDown(increment); }
      catch { return false; }
      node.dispatchEvent(new Event('input',{bubbles:true})); return true;
    }
    if (node instanceof HTMLSelectElement) {
      const directionStep = direction === 'up' || direction === 'left' ? -1 : 1;
      let next = node.selectedIndex + directionStep;
      while(next >= 0 && next < node.options.length && node.options[next].disabled) next += directionStep;
      if (next >= 0 && next < node.options.length) {
        node.selectedIndex = next; node.dispatchEvent(new Event('input',{bubbles:true})); node.dispatchEvent(new Event('change',{bubbles:true}));
      }
      return true;
    }
    return false;
  }
  function move(ctx: InputContext, direction: Direction, controller: boolean) {
    const list = regions(ctx), active = current(list);
    if (!active) return;
    if (controller && adjustWidget(doc.activeElement as HTMLElement,direction)) return;
    if (!active.region.nodes.includes(doc.activeElement as HTMLElement)) { focusRegion(list,active.region.key); return; }
    const {region,index} = active;
    if (region.key === 'hand' && (direction === 'left' || direction === 'right')) {
      focus(region.nodes[(index+(direction === 'right'?1:-1)+region.nodes.length)%region.nodes.length],region);return;
    }
    if (['bindings','hostiles','targets'].includes(region.key) && (direction === 'up' || direction === 'down')) {
      focus(region.nodes[(index+(direction === 'down'?1:-1)+region.nodes.length)%region.nodes.length],region);return;
    }
    if (!ctx.targeting && !ctx.dialog) {
      const destination = region.key === 'bindings' && direction === 'right' ? 'hostiles' : region.key === 'hostiles' && direction === 'left' ? 'bindings' : region.key === 'hand' && direction === 'up' ? 'bindings' : null;
      if (destination && focusRegion(list,destination)) return;
    }
    const from = region.nodes[index].getBoundingClientRect(), x = from.x+from.width/2, y = from.y+from.height/2;
    const dx = direction === 'right'?1:direction === 'left'?-1:0, dy = direction === 'down'?1:direction === 'up'?-1:0;
    const ranked = region.nodes.filter(node=>node !== region.nodes[index]).map(node=>{
      const r = node.getBoundingClientRect(), rx = r.x+r.width/2-x, ry = r.y+r.height/2-y;
      return {node,forward:rx*dx+ry*dy,cross:Math.abs(rx*dy-ry*dx)};
    }).filter(item=>item.forward>1).sort((a,b)=>(a.forward+a.cross*2)-(b.forward+b.cross*2));
    if (ranked.length) focus(ranked[0].node,region);
  }
  function process(ctx: InputContext, intent: InputIntent) {
    if (ctx.settling && !ctx.dialog && intent.type !== 'pause') return;
    if (intent.type === 'pause') { if (!ctx.dialog) call(()=>host.pause()); return; }
    if (intent.type === 'back') { call(()=>host.back()); return; }
    if (intent.type === 'move') { move(ctx,intent.direction,true); return; }
    if (intent.type === 'region') { switchRegion(ctx,intent.step); return; }
    if (intent.type === 'endTurn') { if (!ctx.dialog && ctx.phase === 'battle') call(()=>host.endTurn()); return; }
    const list = regions(ctx), element = doc.activeElement as HTMLElement;
    if (!list.some(region=>region.nodes.includes(element))) { const first = current(list); if(first)focusRegion(list,first.region.key); return; }
    if (intent.type === 'inspect') { call(()=>host.inspect(element)); return; }
    if (element instanceof HTMLButtonElement || element instanceof HTMLInputElement && ['checkbox','radio'].includes(element.type)) call(()=>host.activate(element));
  }
  function pollOnce(now: number): void {
    if (disposed) return;
    if (doc.hidden || !windowFocused) { decoder.reset(); return; }
    const ctx = context(); if (!ctx) { decoder.reset(); return; }
    let pad: PadState | null = null;
    try {
      const pads = readPads();
      for (let i=0;i<Math.min(8,pads.length);i++) if (pads[i]?.connected && pads[i]?.mapping === 'standard') { pad=pads[i];break; }
      for (const intent of decoder.decode(pad,now,!ctx.settling || !!ctx.dialog)) { markMode('controller');process(ctx,intent); }
    } catch { decoder.reset(); }
  }
  function cancelSchedule() {
    if (frame !== null) win.cancelAnimationFrame(frame);
    if (idleTimer !== null) win.clearTimeout(idleTimer);
    frame=null;idleTimer=null;
  }
  function schedule() {
    if (disposed || options.autoPoll === false || doc.hidden || !windowFocused || frame !== null || idleTimer !== null) return;
    frame=win.requestAnimationFrame(now=>{
      frame=null;pollOnce(now);
      if (disposed || doc.hidden || !windowFocused) return;
      let hasPad=false;try{const pads=readPads();hasPad=Array.from(pads).slice(0,8).some(pad=>pad?.connected&&pad.mapping==='standard');}catch{ /* Retry slowly; retain keyboard. */ }
      if(hasPad)schedule();else idleTimer=win.setTimeout(()=>{idleTimer=null;schedule();},500);
    });
  }
  function onVisibility() { decoder.reset();cancelSchedule();if(!doc.hidden)schedule(); }
  function onWindowBlur() { windowFocused = false; decoder.reset();cancelSchedule(); }
  function onWindowFocus() { windowFocused = true; decoder.reset();cancelSchedule();schedule(); }
  function onDeviceChange() { decoder.reset();cancelSchedule();schedule(); }
  function onPointer() { markMode('pointer'); }
  function onFocus() {
    const ctx=context(); if(!ctx)return;
    const element=doc.activeElement as HTMLElement;
    const region=regions(ctx).find(item=>item.nodes.includes(element));
    if(region)remembered.set(region.key,focusKey(element));
  }
  function onKey(event: KeyboardEvent) {
    if (disposed || event.isComposing) return;
    if (event.isTrusted) markMode('keyboard');
    if (event.ctrlKey || event.metaKey || event.altKey) return;
    const element = event.target instanceof HTMLElement ? event.target : null;
    if (element?.isContentEditable || element?.closest('input,select,textarea')) return;
    const ctx=context(); if(!ctx || ctx.settling && !ctx.dialog)return;
    const key=event.key.toLowerCase();
    if (key==='i' && !event.repeat && element && (element.matches('[data-unit],[data-card]'))) { event.preventDefault();call(()=>host.inspect(element));return; }
    const keys: Record<string,string>={h:'hand',b:'bindings',t:ctx.targeting?'targets':'hostiles'};
    if(!ctx.dialog&&ctx.phase==='battle'&&keys[key]&&!event.repeat&&focusRegion(regions(ctx),keys[key])) {event.preventDefault();return;}
    const arrows: Record<string,Direction>={arrowup:'up',arrowdown:'down',arrowleft:'left',arrowright:'right'};
    if(arrows[key] && element instanceof HTMLButtonElement && regions(ctx).some(region=>region.nodes.includes(element))) {event.preventDefault();move(ctx,arrows[key],false);}
  }
  doc.addEventListener('focusin',onFocus);doc.addEventListener('keydown',onKey);doc.addEventListener('pointerdown',onPointer);doc.addEventListener('visibilitychange',onVisibility);
  win.addEventListener('blur',onWindowBlur);win.addEventListener('focus',onWindowFocus);
  win.addEventListener('gamepadconnected',onDeviceChange);win.addEventListener('gamepaddisconnected',onDeviceChange);
  schedule();
  return {pollOnce,dispose(){if(disposed)return;disposed=true;decoder.reset();cancelSchedule();remembered.clear();doc.removeEventListener('focusin',onFocus);doc.removeEventListener('keydown',onKey);doc.removeEventListener('pointerdown',onPointer);doc.removeEventListener('visibilitychange',onVisibility);win.removeEventListener('blur',onWindowBlur);win.removeEventListener('focus',onWindowFocus);win.removeEventListener('gamepadconnected',onDeviceChange);win.removeEventListener('gamepaddisconnected',onDeviceChange);}};
}
