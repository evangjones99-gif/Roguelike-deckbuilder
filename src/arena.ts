import type { Action, GameState } from './engine';
import { ARENA_ART, portraitFor, type PortraitArt } from './art';

type Unit = GameState['allies'][number];
type Side = 'ally' | 'enemy';
type Point = { x: number; y: number };
type Figure = {
  uid: string;
  unit: Unit;
  art: PortraitArt | null;
  side: Side;
  slot: number;
  count: number;
  born: number;
  hit: number;
  dead: number | null;
  departing: boolean;
  phase: number;
  lastPoint: Point;
};
type Strike = {
  source: string | null;
  target: string;
  from: Point;
  to: Point;
  born: number;
  kind: 'physical' | 'magic' | 'heal' | 'ward';
};

/** Illustrated 2.5D battlefield: original painted cutouts, never advertised as rigs. */
export function createArena(canvas: HTMLCanvasElement) {
  const context = canvas.getContext('2d', { alpha: false });
  if (!context) {
    const notice = document.createElement('div');
    notice.className = 'arena-fallback'; notice.setAttribute('role', 'status');
    notice.textContent = 'Battlefield illustration unavailable. All cards, companions and enemy commands remain available in the panels.';
    canvas.hidden = true; canvas.insertAdjacentElement('afterend', notice);
    return { render(_state: GameState) {}, playAction(_action: Action, _before: GameState, _after: GameState) {}, setSelected(_uid: string | null) {}, resize() {}, dispose() { notice.remove(); canvas.hidden = false; } };
  }
  const ctx = context;
  canvas.setAttribute('aria-label', 'An illustrated ruined abbey courtyard. Bound monsters face the forces of the hollow. All combat controls are in the companion and enemy panels.');
  const motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
  const motionOff = () => motionQuery.matches || document.documentElement.dataset.reducedMotion === 'true';
  let reduced = motionOff();
  let disposed = false;
  let width = 900, height = 400, ratio = 1;
  let frame = 0, lastTimestamp = 0, time = 0;
  let selected: string | null = null;
  let active = false;
  let rowFormation = false;
  const formationCounts: Record<Side, number> = { ally: 0, enemy: 0 };
  let previous: GameState | null = null;
  const figures = new Map<string, Figure>();
  let strikes: Strike[] = [];
  const images = new Map<string, HTMLImageElement>();
  const backplate = document.createElement('canvas');
  const back = backplate.getContext('2d');
  let backDirty = true;
  const missing = new Set<string>();
  const status = document.createElement('div');
  status.className = 'arena-art-status'; status.setAttribute('role', 'status');
  Object.assign(status.style, { position: 'absolute', bottom: '8px', left: '12px', right: '12px', color: '#d3c4a5', fontSize: '11px', pointerEvents: 'none', textAlign: 'center' });
  canvas.insertAdjacentElement('afterend', status);
  let artSeed = 24071;
  const random = () => { artSeed = (artSeed * 1664525 + 1013904223) >>> 0; return artSeed / 4294967296; };
  const embers = Array.from({ length: 28 }, () => ({ x: random(), y: random(), phase: random() * 6.28, speed: .018 + random() * .027 }));

  function imageFor(url: string) {
    let image = images.get(url);
    if (!image) {
      image = new Image(); images.set(url, image);
      image.onload = () => { if (!disposed) { missing.delete(url); updateStatus(); backDirty = true; draw(); } };
      image.onerror = () => { if (!disposed) { missing.add(url); updateStatus(); draw(); } };
      image.src = url;
    }
    return image;
  }
  function updateStatus() {
    status.textContent = missing.size ? 'Some battlefield artwork could not load. Combat controls remain available.' : '';
  }
  for (const url of Object.values(ARENA_ART)) imageFor(url);
  const loaded = (image: HTMLImageElement) => image.complete && image.naturalWidth > 0;
  const clamp = (value: number, min: number, max: number) => Math.max(min, Math.min(max, value));

  function paintBackdrop() {
    if (!back || !backDirty) return;
    backDirty = false;
    backplate.width = canvas.width; backplate.height = canvas.height;
    back.setTransform(ratio, 0, 0, ratio, 0, 0);
    const sky = back.createLinearGradient(0, 0, 0, height);
    sky.addColorStop(0, '#202931'); sky.addColorStop(.46, '#303333'); sky.addColorStop(1, '#101314');
    back.fillStyle = sky; back.fillRect(0, 0, width, height);
    const background = imageFor(ARENA_ART.courtyard);
    if (loaded(background)) {
      const cover = Math.max(width / background.naturalWidth, height / background.naturalHeight);
      const w = background.naturalWidth * cover, h = background.naturalHeight * cover;
      back.drawImage(background, (width - w) / 2, (height - h) * .62, w, h);
    } else {
      // Atmospheric local fallback while imagery loads; never a broken image icon.
      back.fillStyle = '#151b20';
      for (let i = 0; i < 7; i++) {
        const x = width * (.06 + i * .148);
        back.fillRect(x, height * .12, width * .028, height * .58);
        back.beginPath(); back.moveTo(x - width * .03, height * .19); back.lineTo(x + width * .014, height * .08); back.lineTo(x + width * .06, height * .19); back.closePath(); back.fill();
      }
      back.strokeStyle = '#6b5740'; back.lineWidth = 1;
      back.beginPath(); back.ellipse(width * .5, height * .75, width * .29, height * .1, 0, 0, Math.PI * 2); back.stroke();
    }
    const shade = back.createLinearGradient(0, 0, 0, height);
    shade.addColorStop(0, 'rgba(8,12,16,.18)'); shade.addColorStop(.48, 'rgba(8,12,16,.02)'); shade.addColorStop(1, 'rgba(8,10,12,.43)');
    back.fillStyle = shade; back.fillRect(0, 0, width, height);
    const edge = back.createRadialGradient(width * .5, height * .55, width * .12, width * .5, height * .55, width * .68);
    edge.addColorStop(0, 'rgba(0,0,0,0)'); edge.addColorStop(1, 'rgba(0,0,0,.45)');
    back.fillStyle = edge; back.fillRect(0, 0, width, height);
  }

  function position(figure: Figure): Point {
    if (figure.dead !== null) return figure.lastPoint;
    const count = figure.count;
    if (rowFormation) return { x: width * (figure.slot + 1) / (count + 1), y: height * (figure.side === 'ally' ? .92 : .56) };
    // Staggered formations occupy two sides of a continuous courtyard floor.
    // Six companions fit without forcing tiny or overlapping horizontal stamps.
    const columns = Math.min(3, count);
    const column = figure.slot % 3;
    const row = count > 3 && figure.slot >= 3 ? 1 : 0;
    const offset = (column - (columns - 1) / 2);
    const sideCenter = figure.side === 'ally' ? .29 : .73;
    const x = sideCenter + offset * .135 + (row ? .025 : 0);
    const baseY = figure.side === 'ally' ? .88 : .71;
    const y = baseY + offset * .065 - (count > 3 && !row ? .16 : 0);
    return { x: width * x, y: height * y };
  }
  function figureSize(figure: Figure) {
    const boss = /dragon|crown/.test(figure.unit.species);
    const bulky = /colossus|golem/.test(figure.unit.species);
    const backRow = figure.count > 3 && figure.slot < 3;
    const max = rowFormation
      ? Math.min(height * (figure.side === 'ally' ? .38 : .43), width / (figure.count + 1) * .92)
      : Math.min(height * (figure.side === 'ally' ? .49 : .54), width * .235);
    return Math.min(max * (boss ? 1.3 : bulky ? 1.07 : 1) * (!rowFormation && backRow ? .86 : 1), height * .52);
  }
  function pointFor(uid: string): Point {
    const figure = figures.get(uid);
    return figure ? position(figure) : { x: width * .42, y: height * .92 };
  }
  function combatPoint(uid: string): Point {
    const figure = figures.get(uid);
    const point = pointFor(uid);
    return { x: point.x, y: point.y - (figure ? figureSize(figure) * .43 : height * .12) };
  }
  function shadow(point: Point, size: number, alpha: number) {
    ctx.save(); ctx.globalAlpha = alpha;
    const shade = ctx.createRadialGradient(point.x, point.y, 0, point.x, point.y, size * .5);
    shade.addColorStop(0, 'rgba(0,0,0,.85)'); shade.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = shade; ctx.translate(point.x, point.y); ctx.scale(1, .2);
    ctx.beginPath(); ctx.arc(0, 0, size * .55, 0, Math.PI * 2); ctx.fill(); ctx.restore();
  }
  function sigil(point: Point, size: number, color: string, alpha: number) {
    ctx.save(); ctx.strokeStyle = color; ctx.globalAlpha = alpha; ctx.lineWidth = 1.2;
    ctx.beginPath(); ctx.ellipse(point.x, point.y, size * .41, size * .10, 0, 0, Math.PI * 2); ctx.stroke();
    ctx.beginPath(); ctx.ellipse(point.x, point.y, size * .33, size * .075, 0, 0, Math.PI * 2); ctx.stroke();
    for (let i = 0; i < 6; i++) {
      const angle = i * Math.PI / 3;
      const x = point.x + Math.cos(angle) * size * .38, y = point.y + Math.sin(angle) * size * .088;
      ctx.beginPath(); ctx.moveTo(x - 2, y - 2); ctx.lineTo(x + 2, y + 2); ctx.moveTo(x - 2, y + 2); ctx.lineTo(x + 2, y - 2); ctx.stroke();
    }
    ctx.restore();
  }
  function paintFigure(figure: Figure) {
    const point = position(figure); figure.lastPoint = point;
    const size = figureSize(figure);
    const deathAge = figure.dead === null ? -1 : time - figure.dead;
    const summonAge = time - figure.born;
    const alpha = deathAge >= 0 ? clamp(1 - deathAge / .65, 0, 1) : reduced ? 1 : clamp(summonAge / .32, 0, 1);
    shadow(point, size, alpha);
    if (selected === figure.uid && deathAge < 0) sigil(point, size * 1.05, '#ecd099', .86);
    else if (!reduced && summonAge < .75 && deathAge < 0) sigil(point, size, '#c7c493', (1 - summonAge / .75) * .75);
    let lungeX = 0, lungeY = 0;
    if (!reduced) for (const strike of strikes) if (strike.source === figure.uid && strike.kind === 'physical') {
      const age = time - strike.born;
      if (age > 0 && age < .5) {
        const amount = Math.sin(age / .5 * Math.PI) * .18;
        lungeX += (strike.to.x - strike.from.x) * amount;
        lungeY += (strike.to.y - strike.from.y) * amount;
      }
    }
    const hitAge = time - figure.hit;
    const recoil = !reduced && hitAge > 0 && hitAge < .28 ? Math.sin(hitAge * 55) * (1 - hitAge / .28) * size * .025 : 0;
    const breath = !reduced && deathAge < 0 ? 1 + Math.sin(time * 1.35 + figure.phase) * .006 : 1;
    const image = figure.art && imageFor(figure.art.url);
    ctx.save(); ctx.globalAlpha = alpha;
    ctx.translate(point.x + lungeX + recoil, point.y + lungeY - (deathAge > 0 ? deathAge * size * .08 : 0));
    // Enemies face the bound party; the assets retain their painted anatomy.
    ctx.scale(figure.side === 'enemy' ? -1 : 1, breath);
    if (image && loaded(image) && figure.art) {
      const columns = figure.art.columns, rows = figure.art.rows;
      const sw = image.naturalWidth / columns, sh = image.naturalHeight / rows;
      ctx.drawImage(image, figure.art.column * sw, figure.art.row * sh, sw, sh, -size / 2, -size * .94, size, size);
    } else {
      // Clear, sober heraldry when art is missing. Names and rules stay in HTML.
      ctx.fillStyle = '#283037'; ctx.strokeStyle = figure.side === 'ally' ? '#b8bca0' : '#a36b61'; ctx.lineWidth = 2;
      ctx.beginPath(); ctx.moveTo(-size * .21, -size * .77); ctx.lineTo(size * .21, -size * .77); ctx.lineTo(size * .19, -size * .32); ctx.lineTo(0, -size * .12); ctx.lineTo(-size * .19, -size * .32); ctx.closePath(); ctx.fill(); ctx.stroke();
      ctx.fillStyle = '#bfac8b'; ctx.font = `500 ${Math.max(14, size * .15)}px Georgia, serif`; ctx.textAlign = 'center'; ctx.fillText('✦', 0, -size * .43);
    }
    ctx.restore();
    if (!reduced && deathAge >= 0 && deathAge < .9) {
      ctx.save(); ctx.globalAlpha = (1 - deathAge / .9) * .8;
      for (let i = 0; i < 18; i++) {
        const phase = figure.phase + i * 2.399;
        const travel = deathAge * (20 + (i % 7) * 8);
        ctx.fillStyle = figure.departing ? '#b8bea9' : i % 4 ? '#69655e' : '#d88d53';
        ctx.fillRect(point.x + Math.sin(phase) * (size * .16 + travel), point.y - size * (.2 + (i % 5) * .12) - travel, 1.5 + i % 2, 1.5 + i % 2);
      }
      ctx.restore();
    }
  }

  function paintStrikes() {
    if (reduced) return;
    for (const strike of strikes) {
      const age = time - strike.born;
      if (age < 0 || age > .72) continue;
      const color = strike.kind === 'heal' ? '#a4cbb6' : strike.kind === 'ward' ? '#b9c6da' : strike.kind === 'magic' ? '#ddbe80' : '#f3d3a4';
      const impact = .23;
      ctx.save(); ctx.strokeStyle = color; ctx.fillStyle = color; ctx.lineCap = 'round';
      if (age < impact) {
        const progress = age / impact;
        const endX = strike.from.x + (strike.to.x - strike.from.x) * progress;
        const endY = strike.from.y + (strike.to.y - strike.from.y) * progress - Math.sin(progress * Math.PI) * height * .07;
        ctx.globalAlpha = Math.sin(progress * Math.PI) * .85; ctx.lineWidth = strike.kind === 'physical' ? 2 : 3;
        ctx.beginPath(); ctx.moveTo(strike.from.x, strike.from.y); ctx.quadraticCurveTo((strike.from.x + endX) / 2, Math.min(strike.from.y, endY) - height * .03, endX, endY); ctx.stroke();
        ctx.beginPath(); ctx.arc(endX, endY, 3, 0, Math.PI * 2); ctx.fill();
      } else {
        const fade = 1 - (age - impact) / .49;
        const radius = 9 + (1 - fade) * 24;
        ctx.globalAlpha = fade * .9; ctx.lineWidth = 1.5;
        if (strike.kind === 'physical') {
          ctx.beginPath(); ctx.moveTo(strike.to.x - radius * .7, strike.to.y + radius); ctx.quadraticCurveTo(strike.to.x - radius, strike.to.y - radius, strike.to.x + radius * .7, strike.to.y - radius); ctx.stroke();
        } else { ctx.beginPath(); ctx.arc(strike.to.x, strike.to.y, radius, 0, Math.PI * 2); ctx.stroke(); }
        for (let i = 0; i < 10; i++) {
          const a = i * 2.399, r = radius * (1 + (i % 3) * .4);
          ctx.fillRect(strike.to.x + Math.cos(a) * r, strike.to.y + Math.sin(a) * r - (1 - fade) * 12, 2, 2);
        }
      }
      ctx.restore();
    }
  }
  function draw() {
    if (disposed || document.hidden) return;
    paintBackdrop(); ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
    if (back) ctx.drawImage(backplate, 0, 0, width, height);
    else { ctx.fillStyle = '#151a20'; ctx.fillRect(0, 0, width, height); }
    [...figures.values()].sort((a, b) => position(a).y - position(b).y).forEach(paintFigure);
    paintStrikes();
    if (!reduced) {
      ctx.save();
      for (const ember of embers) {
        const y = ((ember.y - time * ember.speed) % 1 + 1) % 1;
        const x = ember.x + Math.sin(time * .45 + ember.phase) * .015;
        ctx.globalAlpha = (.15 + Math.sin(time * .8 + ember.phase) * .12) * (1 - y * .4);
        ctx.fillStyle = '#e4a56c'; ctx.fillRect(x * width, y * height, 1.4, 1.4);
      }
      ctx.restore();
    }
  }
  function settle() {
    strikes = [];
    for (const [uid, figure] of figures) {
      if (figure.dead !== null) figures.delete(uid);
      else { figure.born = time - 2; figure.hit = -10; }
    }
  }
  function tick(timestamp: number) {
    frame = 0;
    if (disposed || reduced || document.hidden) return;
    // Draw on every display frame. A strict 1/30 threshold can skip a 33.3 ms
    // RAF pair because of timer rounding, degrading intended 30 Hz to 20 Hz.
    // Bound the simulation step so a stalled tab cannot jump effects forward.
    const dt = lastTimestamp ? clamp((timestamp - lastTimestamp) / 1000, 0, .05) : 0;
    lastTimestamp = timestamp; time += dt;
    strikes = strikes.filter(strike => time - strike.born < .8);
    for (const [uid, figure] of figures) if (figure.dead !== null && time - figure.dead > .9) figures.delete(uid);
    draw();
    frame = requestAnimationFrame(tick);
  }
  function resume() {
    cancelAnimationFrame(frame); frame = 0; lastTimestamp = 0;
    if (disposed) return;
    if (!document.hidden && !reduced) frame = requestAnimationFrame(tick);
    else draw();
  }
  function updateMotion() {
    const next = motionOff(); if (next === reduced) return;
    reduced = next; if (reduced) settle(); resume();
  }
  function render(state: GameState) {
    if (disposed) return;
    active = state.phase === 'battle';
    if (active && (!previous || previous.phase !== 'battle')) {
      figures.clear(); strikes = []; rowFormation = false;
      formationCounts.ally = 0; formationCounts.enemy = 0;
    }
    if (Math.max(state.allies.length, state.enemies.length) >= 4) rowFormation = true;
    const seen = new Set<string>();
    for (const side of ['ally', 'enemy'] as const) {
      const units = side === 'ally' ? state.allies : state.enemies;
      const occupied = new Set([...figures.values()].filter(figure => figure.side === side && figure.dead === null && units.some(unit => unit.uid === figure.uid)).map(figure => figure.slot));
      formationCounts[side] = Math.max(formationCounts[side], units.length);
      units.slice(0, 6).forEach((unit, index) => {
        seen.add(unit.uid);
        let figure = figures.get(unit.uid);
        if (!figure) {
          const slot = [0, 1, 2, 3, 4, 5].find(candidate => !occupied.has(candidate)) ?? index;
          occupied.add(slot);
          formationCounts[side] = Math.max(formationCounts[side], slot + 1);
          figure = { uid: unit.uid, unit, art: portraitFor(unit.species), side, slot, count: formationCounts[side], born: reduced ? time - 2 : time, hit: -10, dead: null, departing: false, phase: random() * 6.28, lastPoint: { x: 0, y: 0 } };
          figures.set(unit.uid, figure);
        } else {
          if (unit.hp < figure.unit.hp) figure.hit = Math.max(figure.hit, time + .2);
          figure.unit = unit; figure.side = side; figure.count = formationCounts[side]; figure.dead = null;
        }
        figure.lastPoint = position(figure);
      });
      // Death leaves a temporary visual gap; survivors do not slide over the
      // disappearing body or move the attacker's origin halfway through a hit.
      for (const figure of figures.values()) if (figure.side === side && figure.dead === null) {
        figure.count = formationCounts[side]; figure.lastPoint = position(figure);
      }
    }
    for (const [uid, figure] of figures) if (!seen.has(uid) && figure.dead === null) {
      if (reduced || (previous && previous.phase !== 'battle')) figures.delete(uid);
      else { figure.dead = time + .18; figure.departing = figure.side === 'ally' && !active; }
    }
    // A newly filled formation can move both parties while an earlier strike
    // is still in flight. Resolve presentation endpoints by UID again after
    // layout reconciliation, including retained death figures.
    for (const strike of strikes) {
      strike.from = strike.source ? combatPoint(strike.source) : { x: width * .34, y: height * .82 };
      strike.to = combatPoint(strike.target);
    }
    previous = state; draw();
  }
  function queueStrike(source: string | null, target: string, kind: Strike['kind'], delay = 0) {
    const from = source ? combatPoint(source) : { x: width * .34, y: height * .82 };
    const to = combatPoint(target);
    strikes.push({ source, target, from, to, born: time + delay, kind });
    const targetFigure = figures.get(target); if (targetFigure && kind !== 'heal' && kind !== 'ward') targetFigure.hit = time + delay + .23;
  }
  /** Observe an accepted rule action. This only schedules presentation effects. */
  function playAction(action: Action, before: GameState, after: GameState) {
    if (disposed || reduced || before.phase !== 'battle') return;
    if (action.type === 'attack') queueStrike(action.unit, action.target, 'physical');
    else if (action.type === 'play') {
      const summoned = after.allies.some(unit => !before.allies.some(old => old.uid === unit.uid));
      if (!summoned) {
        const allBefore = [...before.allies, ...before.enemies];
        const allAfter = [...after.allies, ...after.enemies];
        const targets = allBefore.filter(old => {
          const next = allAfter.find(unit => unit.uid === old.uid);
          return !next || next.hp !== old.hp || next.block !== old.block || next.attack !== old.attack;
        });
        if (targets.length) targets.forEach((unit, i) => {
          const next = allAfter.find(candidate => candidate.uid === unit.uid);
          const kind = next && next.hp > unit.hp ? 'heal' : before.allies.some(candidate => candidate.uid === unit.uid) ? 'ward' : 'magic';
          queueStrike(null, unit.uid, kind, i * .035);
        });
        else if ('target' in action && action.target) queueStrike(null, action.target, 'magic');
      }
    } else if (action.type === 'endTurn') {
      before.enemies.forEach((enemy, i) => {
        if (!enemy.intent || enemy.intent.damage <= 0) return;
        const target = enemy.intent.target;
        if (target === 'all') [...before.allies.map(unit => unit.uid), 'hunter'].forEach(uid => queueStrike(enemy.uid, uid, 'magic', i * .14));
        else queueStrike(enemy.uid, target, /wraith|necromancer|wisp|witch/.test(enemy.species) ? 'magic' : 'physical', i * .14);
      });
    }
    draw();
  }
  function resize() {
    if (disposed) return;
    const bounds = canvas.getBoundingClientRect(); width = Math.max(1, bounds.width || 900); height = Math.max(1, bounds.height || 400);
    ratio = Math.min(window.devicePixelRatio || 1, 1.5);
    const pixelWidth = Math.round(width * ratio), pixelHeight = Math.round(height * ratio);
    if (canvas.width === pixelWidth && canvas.height === pixelHeight) return;
    canvas.width = pixelWidth; canvas.height = pixelHeight;
    ctx.imageSmoothingEnabled = true; ctx.imageSmoothingQuality = 'high';
    backDirty = true;
    // Action endpoints use CSS pixels; settle on layout changes instead of
    // drawing effects aimed at a previous screen location.
    strikes = []; draw();
  }
  const resizeObserver = typeof ResizeObserver !== 'undefined' ? new ResizeObserver(resize) : null;
  resizeObserver?.observe(canvas);
  const motionObserver = new MutationObserver(updateMotion);
  motionObserver.observe(document.documentElement, { attributes: true, attributeFilter: ['data-reduced-motion'] });
  motionQuery.addEventListener('change', updateMotion);
  document.addEventListener('visibilitychange', resume); window.addEventListener('resize', resize);
  resize(); resume();
  return {
    render, playAction,
    setSelected(uid: string | null) { selected = uid; draw(); },
    resize,
    dispose() {
      if (disposed) return; disposed = true; cancelAnimationFrame(frame);
      resizeObserver?.disconnect(); motionObserver.disconnect();
      motionQuery.removeEventListener('change', updateMotion);
      document.removeEventListener('visibilitychange', resume); window.removeEventListener('resize', resize);
      images.forEach(image => { image.onload = null; image.onerror = null; }); images.clear(); figures.clear(); strikes = [];
      status.remove(); backplate.width = 0; backplate.height = 0;
    },
  };
}
