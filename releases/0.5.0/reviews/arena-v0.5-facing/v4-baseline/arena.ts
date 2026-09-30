import type { Action, GameState, TransitionEvent } from './engine';
import { ARENA_ART, HOUND_POSES, portraitFor, animationFor, CREATURE_ATTACK_SEQUENCE, CREATURE_IMPACT_MS, CREATURE_REACTION_MS, CREATURE_DEATH_MS, type PortraitArt, type CreaturePose, type CreaturePoseFrame, type CreatureAnimationAtlas } from './art';

type Unit = GameState['allies'][number];
type Side = 'ally' | 'enemy';
type Point = { x: number; y: number };
type Figure = {
  uid: string;
  unit: Unit;
  art: PortraitArt | null;
  animation: CreatureAnimationAtlas | null;
  pose: CreaturePose;
  priorPose: CreaturePose | null;
  poseChanged: number;
  side: Side;
  slot: number;
  count: number;
  born: number;
  hit: number;
  dead: number | null;
  departing: boolean;
  deathAnchored: boolean;
  phase: number;
  lastPoint: Point;
  layoutFrom: Point;
  layoutTarget: Point;
  layoutStarted: number;
  sizeFrom: number;
  sizeTarget: number;
};
type Strike = {
  source: string | null;
  target: string;
  from: Point;
  to: Point;
  born: number;
  kind: 'physical' | 'magic' | 'heal' | 'ward' | 'counter' | 'control' | 'buff';
};

/** Illustrated 2.5D battlefield: original painted cutouts, never advertised as rigs. */
export function createArena(canvas: HTMLCanvasElement) {
  const context = canvas.getContext('2d', { alpha: false });
  if (!context) {
    const notice = document.createElement('div');
    notice.className = 'arena-fallback'; notice.setAttribute('role', 'status');
    notice.textContent = 'Battlefield illustration unavailable. All cards, companions and enemy commands remain available in the panels.';
    canvas.hidden = true; canvas.insertAdjacentElement('afterend', notice);
    return { render(_state: GameState) {}, playAction(_action: Action, _before: GameState, _after: GameState, _events?: readonly TransitionEvent[]) {}, busyMs() { return 0; }, getPresentationBusyMs() { return 0; }, waitForPresentation() { return Promise.resolve(); }, cancelPresentation() {}, setSelected(_uid: string | null) {}, resize() {}, dispose() { notice.remove(); canvas.hidden = false; } };
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
  const presentationWaiters = new Set<() => void>();
  const attackDuration = CREATURE_ATTACK_SEQUENCE.reduce((total, step) => total + step.durationMs, 0) / 1000;
  const impactTime = CREATURE_IMPACT_MS / 1000;
  const deathDuration = CREATURE_DEATH_MS / 1000;
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
      image.onerror = () => { if (!disposed) { if (url !== HOUND_POSES.url) missing.add(url); updateStatus(); draw(); } };
      image.src = url;
    }
    return image;
  }
  function updateStatus() {
    status.textContent = missing.size ? 'Some battlefield artwork could not load. Combat controls remain available.' : '';
  }
  for (const url of Object.values(ARENA_ART)) imageFor(url);
  imageFor(HOUND_POSES.url);
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
        const x = width * (.06 + i * .058);
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

  function targetPosition(figure: Figure): Point {
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
  function targetSize(figure: Figure) {
    const boss = /dragon|crown/.test(figure.unit.species);
    const bulky = /colossus|golem/.test(figure.unit.species);
    const backRow = figure.count > 3 && figure.slot < 3;
    const max = rowFormation
      ? Math.min(height * (figure.side === 'ally' ? .38 : .43), width / (figure.count + 1) * .92)
      : Math.min(height * (figure.side === 'ally' ? .49 : .54), width * .235);
    return Math.min(max * (boss ? 1.3 : bulky ? 1.07 : 1) * (!rowFormation && backRow ? .86 : 1), height * .52);
  }
  function layoutBlend(figure: Figure) {
    if (reduced) return 1;
    const progress = clamp((time - figure.layoutStarted) / .32, 0, 1);
    return progress * progress * (3 - 2 * progress);
  }
  function position(figure: Figure): Point {
    if (figure.dead !== null) return figure.lastPoint;
    const blend = layoutBlend(figure);
    return { x: figure.layoutFrom.x + (figure.layoutTarget.x - figure.layoutFrom.x) * blend, y: figure.layoutFrom.y + (figure.layoutTarget.y - figure.layoutFrom.y) * blend };
  }
  function figureSize(figure: Figure) {
    return figure.sizeFrom + (figure.sizeTarget - figure.sizeFrom) * layoutBlend(figure);
  }
  function reconcileStrikeEndpoints() {
    for (const strike of strikes) {
      strike.from = strike.source ? combatPoint(strike.source) : { x: width * .34, y: height * .82 };
      strike.to = combatPoint(strike.target);
    }
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
    // The floor ellipse and gradient share one transformed local origin.
    ctx.translate(point.x, point.y); ctx.scale(1, .2);
    const shade = ctx.createRadialGradient(0, 0, 0, 0, 0, size * .5);
    shade.addColorStop(0, 'rgba(0,0,0,.85)'); shade.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = shade;
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
  function sequencePose(age: number): CreaturePose {
    let remaining = age * 1000;
    for (const step of CREATURE_ATTACK_SEQUENCE) {
      if (remaining < step.durationMs) return step.pose;
      remaining -= step.durationMs;
    }
    return 'idle';
  }
  function figurePose(figure: Figure): CreaturePose {
    if (reduced) return 'idle';
    if (figure.dead !== null && time >= figure.dead) return 'death';
    const hitAge = time - figure.hit;
    if (hitAge >= 0 && hitAge < CREATURE_REACTION_MS / 1000) return 'reaction';
    const command = strikes.filter(strike => strike.source === figure.uid && (strike.kind === 'physical' || strike.kind === 'magic') && time >= strike.born && time - strike.born < attackDuration).at(-1);
    return command ? sequencePose(time - command.born) : 'idle';
  }
  function poseFrame(atlas: CreatureAnimationAtlas, pose: CreaturePose, age: number): CreaturePoseFrame | null {
    const frames = atlas.poses[pose] ?? atlas.poses.idle;
    if (!frames?.length) return null;
    const total = frames.reduce((sum, frame) => sum + (frame.holdMs ?? 100), 0);
    let remaining = ((Math.max(0, age) * 1000) % total);
    for (const frame of frames) { if (remaining < (frame.holdMs ?? 100)) return frame; remaining -= frame.holdMs ?? 100; }
    return frames[frames.length - 1];
  }
  function poseBlend(figure: Figure) {
    const duration = (figure.animation?.blendMs?.[figure.pose] ?? 70) / 1000;
    return reduced || duration <= 0 ? 1 : clamp((time - figure.poseChanged) / duration, 0, 1);
  }
  function drawPose(image: HTMLImageElement, atlas: CreatureAnimationAtlas, frame: CreaturePoseFrame, size: number, alpha: number) {
    const cellWidth = image.naturalWidth / atlas.columns, cellHeight = image.naturalHeight / atlas.rows;
    const crop = frame.crop ?? { x: 0, y: 0, width: 1, height: 1 };
    const sw = cellWidth * crop.width, sh = cellHeight * crop.height;
    const sx = frame.column * cellWidth + cellWidth * crop.x, sy = frame.row * cellHeight + cellHeight * crop.y;
    // Cell aspect follows the actual source image; anatomy is never stretched
    // merely to force an image-generator output into the preferred 3:2 sheet.
    const h = size * (frame.scale ?? 1), w = h * sw / sh;
    ctx.save(); ctx.globalAlpha *= alpha;
    ctx.drawImage(image, sx, sy, sw, sh, -w * (frame.anchorX ?? atlas.anchorX), -h * (frame.anchorY ?? atlas.anchorY), w, h);
    ctx.restore();
  }

  function motionFor(figure: Figure, sampleTime = time): Point {
    if (reduced || (figure.dead !== null && sampleTime >= figure.dead)) return { x: 0, y: 0 };
    let x = 0, y = 0;
    for (const strike of strikes) if (strike.source === figure.uid && strike.kind === 'physical') {
      const age = sampleTime - strike.born;
      if (age >= 0 && age < attackDuration) {
        let amount = 0;
        if (age < .14) amount = -Math.sin(age / .14 * Math.PI) * .035;
        // Reach the victim with the painted jaw/claws on the impact frame,
        // then withdraw through the attack hold and recovery pose.
        else if (age < impactTime) amount = Math.sin((age - .14) / (impactTime - .14) * Math.PI * .5) * .74;
        else if (age < .32) amount = .74 - (age - impactTime) / (.32 - impactTime) * .09;
        else amount = Math.max(0, 1 - (age - .32) / .26) * .65;
        x += (strike.to.x - strike.from.x) * amount;
        y += (strike.to.y - strike.from.y) * amount;
      }
    }
    return { x, y };
  }

  function prepareFigure(figure: Figure) {
    if (figure.dead !== null && time >= figure.dead && !figure.deathAnchored) {
      const atContact = motionFor(figure, figure.dead - .00001);
      figure.lastPoint = { x: figure.lastPoint.x + atContact.x, y: figure.lastPoint.y + atContact.y };
      figure.deathAnchored = true;
    }
    figure.lastPoint = position(figure);
    const currentPose = figurePose(figure);
    if (currentPose !== figure.pose) {
      figure.priorPose = figure.pose; figure.pose = currentPose; figure.poseChanged = time;
    }
  }
  function figureOpacity(figure: Figure) {
    const age = figure.dead === null ? -1 : time - figure.dead;
    return age >= 0 ? clamp(1 - Math.max(0, age - .3) / (deathDuration - .3), 0, 1)
      : reduced ? 1 : clamp((time - figure.born) / .32, 0, 1);
  }
  function paintFloor(figure: Figure) {
    const point = position(figure), size = figureSize(figure), movement = motionFor(figure);
    const deathAge = figure.dead === null ? -1 : time - figure.dead;
    const summonAge = time - figure.born;
    const current = figure.animation && poseFrame(figure.animation, figure.pose, time - figure.poseChanged);
    const prior = figure.animation && figure.priorPose && poseFrame(figure.animation, figure.priorPose, 0);
    const blend = poseBlend(figure);
    const footprint = (prior?.ground?.footprint ?? 1) + ((current?.ground?.footprint ?? 1) - (prior?.ground?.footprint ?? 1)) * blend;
    const contact = (prior?.ground?.contact ?? 1) + ((current?.ground?.contact ?? 1) - (prior?.ground?.contact ?? 1)) * blend;
    shadow({ x: point.x + movement.x, y: point.y + movement.y }, size * footprint, figureOpacity(figure) * contact);
    if (selected === figure.uid && deathAge < 0) sigil(point, size * 1.05, '#ecd099', .86);
    else if (!reduced && summonAge < .75 && deathAge < 0) sigil(point, size, '#c7c493', (1 - summonAge / .75) * .75);
  }
  function paintFigure(figure: Figure) {
    const point = position(figure);
    const size = figureSize(figure);
    const deathAge = figure.dead === null ? -1 : time - figure.dead;
    const alpha = figureOpacity(figure);
    const movement = motionFor(figure);
    const hitAge = time - figure.hit;
    const recoil = !reduced && hitAge > 0 && hitAge < CREATURE_REACTION_MS / 1000 ? Math.sin(hitAge * 45) * (1 - hitAge / (CREATURE_REACTION_MS / 1000)) * size * .025 : 0;
    const breath = !reduced && deathAge < 0 ? 1 + Math.sin(time * 1.35 + figure.phase) * .006 : 1;
    const image = figure.art && imageFor(figure.art.url);
    const atlasImage = figure.animation && imageFor(figure.animation.url);
    const blend = poseBlend(figure);
    ctx.save(); ctx.globalAlpha = alpha;
    ctx.translate(point.x + movement.x + recoil, point.y + movement.y);
    // Enemies face the bound party; the assets retain their painted anatomy.
    ctx.scale(figure.side === 'enemy' ? -1 : 1, breath);
    if (atlasImage && loaded(atlasImage) && figure.animation) {
      const current = poseFrame(figure.animation, figure.pose, time - figure.poseChanged);
      const prior = figure.priorPose && blend < 1 ? poseFrame(figure.animation, figure.priorPose, 0) : null;
      if (prior) drawPose(atlasImage, figure.animation, prior, size, 1 - blend);
      if (current) drawPose(atlasImage, figure.animation, current, size, prior ? blend : 1);
    } else if (image && loaded(image) && figure.art) {
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
    if (!reduced && deathAge >= 0 && deathAge < deathDuration) {
      ctx.save(); ctx.globalAlpha = (1 - deathAge / deathDuration) * .8;
      for (let i = 0; i < 18; i++) {
        const phase = figure.phase + i * 2.399;
        const travel = deathAge * (20 + (i % 7) * 8);
        ctx.fillStyle = figure.departing ? '#b8bea9' : i % 4 ? '#69655e' : '#d88d53';
        ctx.fillRect(point.x + Math.sin(phase) * (size * .16 + travel), point.y - size * (.2 + (i % 5) * .12) - travel, 1.5 + i % 2, 1.5 + i % 2);
      }
      ctx.restore();
    }
  }

  function visibleCombatPoint(uid: string): Point {
    const point = combatPoint(uid), figure = figures.get(uid);
    if (!figure) return point;
    const movement = motionFor(figure);
    return { x: point.x + movement.x, y: point.y + movement.y };
  }

  function paintStrikes() {
    if (reduced) return;
    for (const strike of strikes) {
      const age = time - strike.born;
      if (age < 0 || age > .72) continue;
      const to = visibleCombatPoint(strike.target);
      const color = strike.kind === 'control' ? '#aca4da' : strike.kind === 'buff' ? '#d7bc77' : strike.kind === 'counter' ? '#c7d0d6' : strike.kind === 'heal' ? '#a4cbb6' : strike.kind === 'ward' ? '#b9c6da' : strike.kind === 'magic' ? '#ddbe80' : '#f3d3a4';
      const impact = impactTime;
      ctx.save(); ctx.strokeStyle = color; ctx.fillStyle = color; ctx.lineCap = 'round';
      if (age < impact) {
        const progress = age / impact;
        const endX = strike.from.x + (to.x - strike.from.x) * progress;
        const endY = strike.from.y + (to.y - strike.from.y) * progress - Math.sin(progress * Math.PI) * height * .07;
        ctx.globalAlpha = Math.sin(progress * Math.PI) * .85; ctx.lineWidth = strike.kind === 'physical' ? 2 : 3;
        ctx.beginPath(); ctx.moveTo(strike.from.x, strike.from.y); ctx.quadraticCurveTo((strike.from.x + endX) / 2, Math.min(strike.from.y, endY) - height * .03, endX, endY); ctx.stroke();
        ctx.beginPath(); ctx.arc(endX, endY, 3, 0, Math.PI * 2); ctx.fill();
      } else {
        const fade = 1 - (age - impact) / .49;
        const radius = 9 + (1 - fade) * 24;
        ctx.globalAlpha = fade * .9; ctx.lineWidth = 1.5;
        if (strike.kind === 'physical' || strike.kind === 'counter') {
          ctx.beginPath(); ctx.moveTo(to.x - radius * .7, to.y + radius); ctx.quadraticCurveTo(to.x - radius, to.y - radius, to.x + radius * .7, to.y - radius); ctx.stroke();
        } else { ctx.beginPath(); ctx.arc(to.x, to.y, radius, 0, Math.PI * 2); ctx.stroke(); }
        for (let i = 0; i < 10; i++) {
          const a = i * 2.399, r = radius * (1 + (i % 3) * .4);
          ctx.fillRect(to.x + Math.cos(a) * r, to.y + Math.sin(a) * r - (1 - fade) * 12, 2, 2);
        }
      }
      ctx.restore();
    }
  }
  function draw() {
    if (disposed || document.hidden) return;
    reconcileStrikeEndpoints();
    paintBackdrop(); ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
    if (back) ctx.drawImage(backplate, 0, 0, width, height);
    else { ctx.fillStyle = '#151a20'; ctx.fillRect(0, 0, width, height); }
    const ordered = [...figures.values()];
    ordered.forEach(prepareFigure);
    reconcileStrikeEndpoints();
    ordered.sort((a, b) => position(a).y + motionFor(a).y - position(b).y - motionFor(b).y);
    ordered.forEach(paintFloor);
    ordered.forEach(paintFigure);
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
      else { figure.born = time - 2; figure.hit = -10; figure.pose = 'idle'; figure.priorPose = null; figure.poseChanged = time - 2; figure.layoutFrom = { ...figure.layoutTarget }; figure.sizeFrom = figure.sizeTarget; figure.layoutStarted = time - 2; }
    }
    resolvePresentationWaiters();
  }
  function tick(timestamp: number) {
    frame = 0;
    if (disposed || reduced || document.hidden) return;
    // Draw on every display frame. A strict 1/30 threshold can skip a 33.3 ms
    // RAF pair because of timer rounding, degrading intended 30 Hz to 20 Hz.
    // Bound the simulation step so a stalled tab cannot jump effects forward.
    const dt = lastTimestamp ? clamp((timestamp - lastTimestamp) / 1000, 0, .05) : 0;
    lastTimestamp = timestamp; time += dt;
    strikes = strikes.filter(strike => time - strike.born < .78);
    for (const [uid, figure] of figures) if (figure.dead !== null && time - figure.dead >= deathDuration) figures.delete(uid);
    draw(); resolvePresentationWaiters();
    frame = requestAnimationFrame(tick);
  }
  function resume() {
    cancelAnimationFrame(frame); frame = 0; lastTimestamp = 0;
    if (disposed) return;
    if (document.hidden) settle();
    if (!document.hidden && !reduced) frame = requestAnimationFrame(tick);
    else draw();
  }
  function updateMotion() {
    const next = motionOff(); if (next === reduced) return;
    reduced = next; if (reduced) settle(); resume();
  }
  function createFigure(unit: Unit, side: Side, slot: number, count: number): Figure {
    const figure: Figure = { uid: unit.uid, unit, art: portraitFor(unit.species), animation: animationFor(unit.species), pose: 'idle', priorPose: null, poseChanged: time - 2, side, slot, count, born: reduced ? time - 2 : time, hit: -10, dead: null, departing: false, deathAnchored: false, phase: random() * 6.28, lastPoint: { x: 0, y: 0 }, layoutFrom: { x: 0, y: 0 }, layoutTarget: { x: 0, y: 0 }, layoutStarted: time - 2, sizeFrom: 0, sizeTarget: 0 };
    const target = targetPosition(figure), size = targetSize(figure);
    figure.layoutFrom = target; figure.layoutTarget = target;
    figure.sizeFrom = size; figure.sizeTarget = size; figure.lastPoint = target;
    return figure;
  }

  function render(state: GameState) {
    if (disposed) return;
    active = state.phase === 'battle';
    if (active && (!previous || previous.phase !== 'battle')) {
      figures.clear(); strikes = []; resolvePresentationWaiters(); rowFormation = false;
      formationCounts.ally = 0; formationCounts.enemy = 0;
    }
    const oldPositions = new Map([...figures].map(([uid, figure]) => [uid, position(figure)]));
    const oldSizes = new Map([...figures].map(([uid, figure]) => [uid, figureSize(figure)]));
    if (Math.max(state.allies.length, state.enemies.length, formationCounts.ally, formationCounts.enemy) >= 4) rowFormation = true;
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
          figure = createFigure(unit, side, slot, formationCounts[side]);
          figures.set(unit.uid, figure);
        } else {
          if (unit.hp < figure.unit.hp) figure.hit = Math.max(figure.hit, time + impactTime);
          figure.unit = unit; figure.side = side; figure.count = formationCounts[side]; figure.dead = null;
        }
      });
      // Death leaves a temporary visual gap; survivors do not slide over the
      // disappearing body or move the attacker's origin halfway through a hit.
      for (const figure of figures.values()) if (figure.side === side && figure.dead === null) {
        figure.count = formationCounts[side];
      }
    }
    for (const [uid, figure] of figures) if ((seen.has(uid) || (figure.side === 'ally' && (state.phase === 'reward' || state.phase === 'victory'))) && figure.dead === null) {
      const target = targetPosition(figure), size = targetSize(figure);
      if (!oldPositions.has(uid)) {
        figure.layoutFrom = target; figure.layoutTarget = target;
        figure.sizeFrom = size; figure.sizeTarget = size; figure.layoutStarted = time - 2;
      } else if (Math.abs(target.x - figure.layoutTarget.x) > .1 || Math.abs(target.y - figure.layoutTarget.y) > .1 || Math.abs(size - figure.sizeTarget) > .1) {
        figure.layoutFrom = oldPositions.get(uid)!; figure.layoutTarget = target;
        figure.sizeFrom = oldSizes.get(uid)!; figure.sizeTarget = size;
        figure.layoutStarted = reduced ? time - 2 : time;
      }
      figure.lastPoint = position(figure);
    }
    for (const [uid, figure] of figures) if (!seen.has(uid) && figure.dead === null) {
      // Winning rule state deliberately releases the party. Keep its surviving
      // painted figures while the last enemy falls; victory is not their death.
      if (figure.side === 'ally' && (state.phase === 'reward' || state.phase === 'victory')) {
        figure.departing = true; continue;
      }
      if (reduced || (previous && previous.phase !== 'battle')) figures.delete(uid);
      else {
        const incoming = strikes.filter(strike => strike.target === uid && strike.kind !== 'heal' && strike.kind !== 'ward').at(-1);
        figure.dead = incoming ? Math.max(time, incoming.born + impactTime) : time + .12;
        figure.deathAnchored = false;
        figure.departing = figure.side === 'ally' && !active;
      }
    }
    // A newly filled formation can move both parties while an earlier strike
    // is still in flight. Resolve presentation endpoints by UID again after
    // layout reconciliation, including retained death figures.
    reconcileStrikeEndpoints();
    previous = state; draw(); resolvePresentationWaiters();
  }
  function queueStrike(source: string | null, target: string, kind: Strike['kind'], delay = 0) {
    const from = source ? combatPoint(source) : { x: width * .34, y: height * .82 };
    const to = combatPoint(target);
    const strike: Strike = { source, target, from, to, born: time + delay, kind };
    strikes.push(strike);
    const targetFigure = figures.get(target); if (targetFigure && (kind === 'physical' || kind === 'magic' || kind === 'counter')) targetFigure.hit = time + delay + impactTime;
    return strike;
  }
  /** Observe an accepted rule action. This only schedules presentation effects. */
  function playAction(action: Action, before: GameState, after: GameState, events?: readonly TransitionEvent[]) {
    if (disposed) return;
    if (reduced || before.phase !== 'battle') { render(after); return; }
    if (events) {
      const actorDelays = new Map<string, number>();
      const lastHits = new Map<string, Strike>();
      const terminal = after.phase !== 'battle';
      const delayFor = (source: string, retaliation = false) => {
        if (retaliation) return .04;
        if (action.type !== 'endTurn' || !before.enemies.some(unit => unit.uid === source)) return 0;
        if (!actorDelays.has(source)) actorDelays.set(source, actorDelays.size * (terminal ? .009 : .05));
        return actorDelays.get(source)!;
      };
      for (const event of events) {
        const source = event.source === 'hunter' || event.source === 'world' ? null : event.source;
        if (event.type === 'summon') {
          if (!figures.has(event.target)) {
            const occupied = new Set([...figures.values()].filter(figure => figure.side === event.side && figure.dead === null).map(figure => figure.slot));
            const slot = [0, 1, 2, 3, 4, 5].find(candidate => !occupied.has(candidate)) ?? 0;
            formationCounts[event.side] = Math.max(formationCounts[event.side], slot + 1);
            figures.set(event.target, createFigure(event.unit, event.side, slot, formationCounts[event.side]));
          }
          queueStrike(source, event.target, 'ward', delayFor(event.source));
        } else if (event.type === 'hit') {
          const kind = event.kind === 'retaliation' ? 'counter' : event.kind === 'command' || (event.kind === 'enemy' && !/wraith|necromancer/.test(figures.get(event.source)?.unit.species ?? '')) ? 'physical' : 'magic';
          const strike = queueStrike(source, event.target, kind, delayFor(event.source, event.kind === 'retaliation'));
          lastHits.set(event.target, strike);
        } else if (event.type === 'control' || event.type === 'buff') {
          // Intent cancellation and attack rallies are real resolved effects,
          // but do not create fabricated damage, recoil or attack movement.
          queueStrike(source, event.target, event.type, delayFor(event.source));
        } else if (event.type === 'heal' || event.type === 'ward') {
          queueStrike(source, event.target, event.type === 'heal' ? 'heal' : 'ward', delayFor(event.source));
        } else if (event.type === 'death' && event.target !== 'hunter') {
          const figure = figures.get(event.target), hit = lastHits.get(event.target);
          if (figure) {
            figure.dead = hit ? hit.born + impactTime : time + .12;
            figure.deathAnchored = false; figure.departing = false;
          }
        }
      }
      render(after); return;
    }
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
    }
    // Callers without a canonical trace still show state changes. They do not
    // manufacture enemy attacks from intents that may never have executed.
    render(after);
  }
  function busyMs() {
    if (disposed || reduced || document.hidden) return 0;
    let end = time;
    for (const strike of strikes) end = Math.max(end, strike.born + .73);
    for (const figure of figures.values()) {
      if (figure.dead !== null) end = Math.max(end, figure.dead + deathDuration);
      else if (!figure.departing) end = Math.max(end, figure.born + .38, figure.hit + CREATURE_REACTION_MS / 1000, figure.layoutStarted + .32);
    }
    return Math.max(0, Math.ceil((end - time) * 1000));
  }
  function resolvePresentationWaiters() {
    if (busyMs() !== 0) return;
    const pending = [...presentationWaiters]; presentationWaiters.clear();
    pending.forEach(resolve => resolve());
  }
  function waitForPresentation(): Promise<void> {
    if (!busyMs()) return Promise.resolve();
    return new Promise(resolve => presentationWaiters.add(resolve));
  }
  function cancelPresentation() { settle(); draw(); }

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
    for (const figure of figures.values()) if (figure.dead === null) {
      const target = targetPosition(figure), size = targetSize(figure);
      figure.layoutFrom = target; figure.layoutTarget = target;
      figure.sizeFrom = size; figure.sizeTarget = size; figure.lastPoint = target;
    }
    settle(); draw();
  }
  const resizeObserver = typeof ResizeObserver !== 'undefined' ? new ResizeObserver(resize) : null;
  resizeObserver?.observe(canvas);
  const motionObserver = new MutationObserver(updateMotion);
  motionObserver.observe(document.documentElement, { attributes: true, attributeFilter: ['data-reduced-motion'] });
  motionQuery.addEventListener('change', updateMotion);
  document.addEventListener('visibilitychange', resume); window.addEventListener('resize', resize);
  resize(); resume();
  return {
    render, playAction, busyMs, getPresentationBusyMs: busyMs, waitForPresentation, cancelPresentation,
    setSelected(uid: string | null) { selected = uid; draw(); },
    resize,
    dispose() {
      if (disposed) return; disposed = true; cancelAnimationFrame(frame); resolvePresentationWaiters();
      resizeObserver?.disconnect(); motionObserver.disconnect();
      motionQuery.removeEventListener('change', updateMotion);
      document.removeEventListener('visibilitychange', resume); window.removeEventListener('resize', resize);
      images.forEach(image => { image.onload = null; image.onerror = null; }); images.clear(); figures.clear(); strikes = [];
      status.remove(); backplate.width = 0; backplate.height = 0;
    },
  };
}
