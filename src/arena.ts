import { drawHoundJaw, houndJawClosure } from './hound-jaw';
import { createBattlefieldLayout, normalizeLayoutConfig, sameLayoutConfig, interpolateCell, projectCell, interpolateRect, intersectRects, sameRect, transformedImageRect, unionRects, clipToViewport, type BattlefieldCell, type BattlefieldRect, type BattlefieldHunterGeometry, type ArenaLayoutConfig, type ArenaReadoutMetrics, type ArenaUnitRegion, type ArenaUnitViewport } from './battlefield-layout';
import { compactIntent } from './compact-intent';
export type { ArenaUnitRegion, ArenaUnitViewport, ArenaReadoutMetrics } from './battlefield-layout';
import { encounterEnvironment } from './encounter-environment';
import { observeHunter, hunterEventCues, hunterGeometry, paintHunterShadow, paintHunterSheet, HUNTER_ART_URL, hunterSourcePoint, hunterPose, type HunterPresentation } from './hunter-presence';
import type { Action, GameState, TransitionEvent } from './engine';
import { ARENA_ART, HOUND_POSES, portraitFor, animationFor, CREATURE_ATTACK_SEQUENCE, CREATURE_IMPACT_MS, CREATURE_REACTION_MS, CREATURE_DEATH_MS, type PortraitArt, type CreaturePose, type CreaturePoseFrame, type CreatureAnimationAtlas } from './art';

type Unit = GameState['allies'][number];
type Side = 'ally' | 'enemy';
type Point = { x: number; y: number };
type UnitRegionListener = (regions: readonly ArenaUnitRegion[]) => void;
type Figure = {
  uid: string;
  unit: Unit;
  art: PortraitArt | null;
  animation: CreatureAnimationAtlas | null;
  pose: CreaturePose;
  priorPose: CreaturePose | null;
  poseChanged: number;
  side: Side;
  facing: -1 | 1;
  slot: number;
  count: number;
  born: number;
  hit: number;
  dead: number | null;
  departing: boolean;
  deathAnchored: boolean;
  deathSizeBasis: { width: number; height: number; from: number; target: number } | null;
  phase: number;
  lastPoint: Point;
  layoutFrom: Point;
  layoutTarget: Point;
  layoutStarted: number;
  sizeFrom: number;
  sizeTarget: number;
  cellFrom: BattlefieldCell;
  cellTarget: BattlefieldCell;
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
    notice.textContent = 'Battlefield artwork unavailable. Combat controls remain available.';
    canvas.hidden = true; canvas.insertAdjacentElement('afterend', notice);
    const regions: readonly ArenaUnitRegion[] = Object.freeze([]);
    return { render(_state: GameState) {}, playAction(_action: Action, _before: GameState, _after: GameState, _events?: readonly TransitionEvent[]) {}, busyMs() { return 0; }, getPresentationBusyMs() { return 0; }, waitForPresentation() { return Promise.resolve(); }, cancelPresentation() {}, setSelected(_uid: string | null) {}, resize() {}, getUnitRegions() { return regions; }, getUnitViewport(): ArenaUnitViewport { return { width: 0, height: 0, canvasAvailable: false, requiredHeight: 0, layoutPending: false, hunterRect: { left: 0, top: 0, width: 0, height: 0 } }; }, setReadoutMetrics(_metrics: ArenaReadoutMetrics) {}, getActionPresentationDelayMs() { return 0; }, subscribeUnitRegions(listener: UnitRegionListener) { notifyRegionListener(listener, regions); return () => {}; }, dispose() { notice.remove(); canvas.hidden = false; } };
  }
  const ctx = context;
  let environment: 'courtyard' | 'crypt' = 'courtyard';
  function updateEnvironmentLabel() {
    const place = environment === 'crypt' ? 'ossuary crypt' : 'ruined abbey courtyard';
    canvas.setAttribute('aria-label', `An illustrated ${place}. Bound monsters face the forces of the hollow. Combat controls and information accompany each creature.`);
  }
  updateEnvironmentLabel();
  const motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
  const motionOff = () => motionQuery.matches || document.documentElement.dataset.reducedMotion === 'true';
  let reduced = motionOff();
  let disposed = false;
  let width = 900, height = 400, ratio = 1;
  let frame = 0, lastTimestamp = 0, time = 0;
  let selected: string | null = null;
  let active = false;
  let layoutConfig: ArenaLayoutConfig = { allies: 0, enemies: 0, intentRows: 3, statsRows: 1 };
  let measuredRows: ArenaReadoutMetrics = {};
  type Allocation = { config: ArenaLayoutConfig; slots: Map<string, number>; start: number; cueStart: number };
  let pendingAllocation: Allocation | null = null;
  let actionAllocationSlots = new Map<string, number>();
  let allocationTransitionEnd = -10, lastActionLeadMs = 0, lastActionCueStart = -10;
  let hunterFrom: BattlefieldHunterGeometry | null = null, hunterTarget: BattlefieldHunterGeometry | null = null, hunterStarted = -10;
  const fieldLayout = (config = layoutConfig) => createBattlefieldLayout(width, height, config);
  let previous: GameState | null = null;
  let hunter: HunterPresentation | null = null;
  const figures = new Map<string, Figure>();
  const regionListeners = new Set<UnitRegionListener>();
  let publishedRegions: readonly ArenaUnitRegion[] = Object.freeze([]);
  let publishedViewport = '';
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
    const relevantMissing = [...missing].some(url => (url !== ARENA_ART.courtyard && url !== ARENA_ART.crypt) || url === ARENA_ART[environment]);
    status.textContent = relevantMissing ? 'Some artwork is missing. Combat controls remain available.' : '';
  }
  // Environment art is requested on demand; unused crypt art cannot fail a courtyard.
  imageFor(ARENA_ART.companions); imageFor(ARENA_ART.adversaries);
  imageFor(HOUND_POSES.url);
  imageFor(HUNTER_ART_URL);
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
    const background = imageFor(ARENA_ART[environment]);
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

  function cellFor(side: Side, slot: number, config = layoutConfig): BattlefieldCell {
    const countKey = side === 'ally' ? 'allies' : 'enemies';
    const safe = config[countKey] > slot ? config : { ...config, [countKey]: slot + 1 };
    return fieldLayout(safe)[side][slot];
  }
  function shapeExtents(figure: Figure) {
    let left = .5, right = .5, top = .94 * 1.006, bottom = .06 * 1.006;
    const atlas = figure.animation, image = atlas && images.get(atlas.url);
    if (atlas) {
      left = right = top = bottom = 0;
      const ratio = image && loaded(image) ? image.naturalWidth / atlas.columns / (image.naturalHeight / atlas.rows) : 1;
      for (const frames of Object.values(atlas.poses)) for (const frame of frames ?? []) {
        const crop = frame.crop ?? { x: 0, y: 0, width: 1, height: 1 };
        const h = frame.scale ?? 1, w = h * ratio * crop.width / crop.height;
        const ax = frame.anchorX ?? atlas.anchorX, ay = frame.anchorY ?? atlas.anchorY;
        // Facing can flip during contact; reserve both full unchanged cell edges.
        const horizontal = w * Math.max(ax, 1 - ax) + .025;
        left = Math.max(left, horizontal); right = Math.max(right, horizontal);
        top = Math.max(top, h * ay * 1.006); bottom = Math.max(bottom, h * (1 - ay) * 1.006);
      }
      // Missing/loading art still paints a square heraldry cell at its own anchor.
      if (!image || !loaded(image)) { left = Math.max(left, .525); right = Math.max(right, .525);
        top = Math.max(top, .94 * 1.006); bottom = Math.max(bottom, .06 * 1.006); }
    } else { left += .025; right += .025; }
    return { left, right, top, bottom };
  }
  function feetFor(figure: Figure, cell: BattlefieldCell): Point {
    const shape = shapeExtents(figure), body = cell.bodyRect;
    const ratio = shape.top / Math.max(.001, shape.top + shape.bottom);
    return { x: body.left + body.width / 2, y: body.top + 2 + Math.max(0, body.height - 4) * ratio };
  }
  function fitSize(figure: Figure, body: BattlefieldRect) {
    const shape = shapeExtents(figure), ratio = shape.top / Math.max(.001, shape.top + shape.bottom);
    const vertical = Math.max(0, body.height - 4);
    return Math.max(0, Math.min((body.width / 2 - 4) / Math.max(shape.left, shape.right),
      vertical * ratio / Math.max(.001, shape.top), vertical * (1 - ratio) / Math.max(.001, shape.bottom)));
  }
  function targetPosition(figure: Figure): Point {
    return figure.dead !== null && time >= figure.dead ? figure.lastPoint : feetFor(figure, figure.cellTarget);
  }
  function targetSize(figure: Figure) { return fitSize(figure, figure.cellTarget.bodyRect); }
  function figureCell(figure: Figure): BattlefieldCell {
    return interpolateCell(figure.cellFrom, figure.cellTarget, layoutBlend(figure));
  }
  function hunterPlacement(): BattlefieldHunterGeometry {
    const target = hunterTarget ?? fieldLayout().hunter, from = hunterFrom ?? target;
    const raw = reduced ? 1 : clamp((time - hunterStarted) / .32, 0, 1), blend = raw * raw * (3 - 2 * raw);
    return { feet: { x: from.feet.x + (target.feet.x - from.feet.x) * blend,
      y: from.feet.y + (target.feet.y - from.feet.y) * blend },
      torso: { x: from.torso.x + (target.torso.x - from.torso.x) * blend,
        y: from.torso.y + (target.torso.y - from.torso.y) * blend },
      bodyHeight: from.bodyHeight + (target.bodyHeight - from.bodyHeight) * blend,
      bodyWidth: from.bodyWidth + (target.bodyWidth - from.bodyWidth) * blend,
      rect: interpolateRect(from.rect, target.rect, blend) };
  }
  function desiredAllocation(state: GameState): { config: ArenaLayoutConfig; slots: Map<string, number> } {
    const slots = new Map<string, number>();
    state.allies.slice(0, 6).forEach((unit, index) => slots.set(unit.uid, index));
    state.enemies.slice(0, 6).forEach((unit, index) => slots.set(unit.uid, index));
    const intentRows = Math.max(3, ...state.enemies.map(unit => compactIntent(state, unit).essentialRows), measuredRows.intentRows ?? 0);
    return { config: normalizeLayoutConfig({ allies: state.allies.length, enemies: state.enemies.length,
      intentRows, statsRows: measuredRows.statsRows ?? 1, identityRows: measuredRows.identityRows ?? 1 }), slots };
  }
  function allocationChanges(config: ArenaLayoutConfig, slots: Map<string, number>): boolean {
    const next = fieldLayout(config);
    if (Math.abs(next.requiredHeight - fieldLayout().requiredHeight) > .01 || !sameRect(next.hunter.rect, hunterPlacement().rect)) return true;
    for (const figure of figures.values()) {
      const slot = slots.get(figure.uid); if (slot === undefined || (figure.dead !== null && time >= figure.dead)) continue;
      const cell = next[figure.side][slot];
      if (!sameRect(figure.cellTarget, cell) || Math.abs(figure.sizeTarget - fitSize(figure, cell.bodyRect)) > .01) return true;
    }
    return false;
  }
  function applyAllocation(config: ArenaLayoutConfig, slots: Map<string, number>, start: number, animate: boolean) {
    const oldHunter = hunterPlacement(), nextConfig = normalizeLayoutConfig(config);
    const staged = animate;
    // A live UID crossing rows or a count change can sweep through another
    // owner's readout or the hunter's old center band. Commit that allocation
    // atomically after holds; the pre-cue stage still locks changing ownership.
    const reindexed = [...figures.values()].some(figure => slots.has(figure.uid) && slots.get(figure.uid) !== figure.slot);
    const tween = animate && !reindexed && nextConfig.allies === layoutConfig.allies && nextConfig.enemies === layoutConfig.enemies;
    layoutConfig = nextConfig;
    const next = fieldLayout();
    hunterFrom = tween ? oldHunter : next.hunter; hunterTarget = next.hunter; hunterStarted = tween ? start : time - 2;
    let moved = !sameRect(oldHunter.rect, next.hunter.rect);
    for (const figure of figures.values()) {
      const slot = slots.get(figure.uid); if (slot === undefined || (figure.dead !== null && time >= figure.dead)) continue;
      const oldCell = figureCell(figure), oldPoint = position(figure), oldSize = figureSize(figure);
      figure.slot = slot; figure.count = figure.side === 'ally' ? layoutConfig.allies : layoutConfig.enemies;
      const cell = next[figure.side][slot], point = feetFor(figure, cell), size = fitSize(figure, cell.bodyRect);
      const changed = !sameRect(oldCell, cell) || Math.abs(oldSize - size) > .01;
      const transition = tween && changed && figure.born < start;
      figure.cellFrom = transition ? oldCell : cell; figure.cellTarget = cell;
      figure.layoutFrom = transition ? oldPoint : point; figure.layoutTarget = point;
      figure.sizeFrom = transition ? oldSize : size; figure.sizeTarget = size;
      figure.layoutStarted = transition ? start : time - 2;
      figure.lastPoint = position(figure); moved ||= changed;
    }
    if (staged && moved) allocationTransitionEnd = Math.max(allocationTransitionEnd, start + .32);
    else if (!staged) allocationTransitionEnd = time;
  }
  function advanceAllocation() {
    if (pendingAllocation && time >= pendingAllocation.start) {
      const pending = pendingAllocation; pendingAllocation = null;
      applyAllocation(pending.config, pending.slots, pending.start, !reduced && !document.hidden);
    }
    if (!pendingAllocation && time >= allocationTransitionEnd && cueBusyMs() === 0 && active && previous) {
      const next = desiredAllocation(previous);
      if (!sameLayoutConfig(layoutConfig, next.config) || allocationChanges(next.config, next.slots))
        applyAllocation(next.config, next.slots, time, !reduced && !document.hidden);
    }
  }
  function setReadoutMetrics(metrics: ArenaReadoutMetrics) {
    const intentRows = metrics.intentRows ?? measuredRows.intentRows;
    const statsRows = metrics.statsRows ?? measuredRows.statsRows;
    const identityRows = metrics.identityRows ?? measuredRows.identityRows;
    if (intentRows === measuredRows.intentRows && statsRows === measuredRows.statsRows && identityRows === measuredRows.identityRows) return;
    measuredRows = { intentRows, statsRows, identityRows }; advanceAllocation(); draw();
  }
  function layoutBlend(figure: Figure) {
    if (reduced) return 1;
    const progress = clamp((time - figure.layoutStarted) / .32, 0, 1);
    return progress * progress * (3 - 2 * progress);
  }
  function position(figure: Figure): Point {
    if (figure.dead !== null && time >= figure.dead) return figure.lastPoint;
    const blend = layoutBlend(figure);
    return { x: figure.layoutFrom.x + (figure.layoutTarget.x - figure.layoutFrom.x) * blend, y: figure.layoutFrom.y + (figure.layoutTarget.y - figure.layoutFrom.y) * blend };
  }
  function figureSize(figure: Figure) {
    return Math.min(figure.sizeFrom + (figure.sizeTarget - figure.sizeFrom) * layoutBlend(figure),
      fitSize(figure, figureCell(figure).bodyRect));
  }
  function reconcileStrikeEndpoints() {
    for (const strike of strikes) {
      strike.from = strike.source ? sourcePoint(strike.source) : { x: width * .34, y: height * .82 };
      strike.to = combatPoint(strike.target);
    }
  }

  function sourcePoint(uid: string): Point {
    if (uid === 'hunter') {
      const sheet = images.get(HUNTER_ART_URL);
      return sheet && loaded(sheet) ? hunterSourcePoint(hunter,width,height,time,reduced,hunterPlacement()) : hunterGeometry(width,height,hunterPlacement()).torso;
    }
    return combatPoint(uid);
  }
  function pointFor(uid: string): Point {
    if (uid === 'hunter') return hunterGeometry(width, height,hunterPlacement()).feet;
    const figure = figures.get(uid);
    return figure ? position(figure) : { x: width * .42, y: height * .92 };
  }
  function combatPoint(uid: string): Point {
    if (uid === 'hunter') return hunterGeometry(width, height,hunterPlacement()).torso;
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
  function activeGesture(figure: Figure, sampleTime = time): Strike | null {
    // A caster action may resolve against many targets. Impacts remain separate,
    // while the body performs only its latest active gesture, never their sum.
    for (let i = strikes.length - 1; i >= 0; i--) {
      const strike = strikes[i], age = sampleTime - strike.born;
      const duration = figure.animation === HOUND_POSES && strike.kind === 'physical' ? attackDuration + .04 : attackDuration;
      if (strike.source === figure.uid && (strike.kind === 'physical' || strike.kind === 'magic') && age >= 0 && age < duration) return strike;
    }
    return null;
  }
  function figurePose(figure: Figure): CreaturePose {
    if (reduced) return 'idle';
    if (figure.dead !== null && time >= figure.dead) return 'death';
    const hitAge = time - figure.hit;
    if (hitAge >= 0 && hitAge < CREATURE_REACTION_MS / 1000) return 'reaction';
    const command = activeGesture(figure);
    if (!command) return 'idle';
    const age = time - command.born;
    // Hound contact holds40ms; its original recovery then runs in full.
    const poseAge = figure.animation === HOUND_POSES && command.kind === 'physical' && age >= impactTime
      ? Math.max(impactTime, age - .04) : age;
    return sequencePose(poseAge);
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
  function poseDimensions(image: HTMLImageElement, atlas: CreatureAnimationAtlas, pose: CreaturePoseFrame, size: number) {
    const crop = pose.crop ?? { x: 0, y: 0, width: 1, height: 1 };
    const height = size * (pose.scale ?? 1);
    return { width: height * (image.naturalWidth / atlas.columns * crop.width)
      / (image.naturalHeight / atlas.rows * crop.height), height,
      anchorX: pose.anchorX ?? atlas.anchorX, anchorY: pose.anchorY ?? atlas.anchorY };
  }
  function drawPose(image: HTMLImageElement, atlas: CreatureAnimationAtlas, frame: CreaturePoseFrame, size: number, alpha: number, jawClosure = 0) {
    const cellWidth = image.naturalWidth / atlas.columns, cellHeight = image.naturalHeight / atlas.rows;
    const crop = frame.crop ?? { x: 0, y: 0, width: 1, height: 1 };
    const sw = cellWidth * crop.width, sh = cellHeight * crop.height;
    const sx = frame.column * cellWidth + cellWidth * crop.x, sy = frame.row * cellHeight + cellHeight * crop.y;
    // Cell aspect follows the actual source image; anatomy is never stretched
    // merely to force an image-generator output into the preferred 3:2 sheet.
    const dimensions = poseDimensions(image, atlas, frame, size);
    const h = dimensions.height, w = dimensions.width;
    ctx.save(); ctx.globalAlpha *= alpha;
    if (jawClosure > 0 && atlas === HOUND_POSES && frame.column === 2 && frame.row === 0 && cellWidth === 512 && cellHeight === 512) {
      drawHoundJaw(ctx, image, jawClosure, frame.column*cellWidth, frame.row*cellHeight,
        cellWidth*crop.x, cellHeight*crop.y, sw, sh,
        -w * dimensions.anchorX, -h * dimensions.anchorY, w, h);
    } else ctx.drawImage(image, sx, sy, sw, sh, -w * dimensions.anchorX, -h * dimensions.anchorY, w, h);
    ctx.restore();
  }

  function motionFor(figure: Figure, sampleTime = time): Point {
    if (reduced || (figure.dead !== null && sampleTime >= figure.dead)) return { x: 0, y: 0 };
    const strike = activeGesture(figure, sampleTime);
    if (!strike || strike.kind !== 'physical') return { x: 0, y: 0 };
    const age = sampleTime - strike.born;
    let amount = 0;
    if (age < .14) amount = -Math.sin(age / .14 * Math.PI) * .035;
    // Reach the victim with the painted jaw/claws on the impact frame,
    // then withdraw through the attack hold and recovery pose.
    else if (age < impactTime) amount = Math.sin((age - .14) / (impactTime - .14) * Math.PI * .5) * .74;
    else if (figure.animation === HOUND_POSES) {
      // Keep the real240ms impact and hold its contact for40ms. Shift the
      // ORIGINAL80ms release and260ms return without compressing either.
      const recoveryAge = Math.max(impactTime, age - .04);
      if (recoveryAge < .32) amount = .74 - (recoveryAge - impactTime) / (.32 - impactTime) * .09;
      else amount = Math.max(0, 1 - (recoveryAge - .32) / .26) * .65;
    }
    else if (age < .32) amount = .74 - (age - impactTime) / (.32 - impactTime) * .09;
    else amount = Math.max(0, 1 - (age - .32) / .26) * .65;
    const movement = { x: (strike.to.x - strike.from.x) * amount, y: (strike.to.y - strike.from.y) * amount };
    // Only authored, loaded attack cells opt into anatomical reach. Keep the
    // ordinary curve for other species, missing pose art and anticipation.
    const atlas = figure.animation, frame = atlas?.poses.attack?.[0];
    const tip = frame?.contactTip, image = atlas && imageFor(atlas.url);
    if (!atlas || !frame || !tip || !image || !loaded(image) || age < .14) return movement;
    const size = figureSize(figure), point = position(figure);
    const cellWidth = image.naturalWidth / atlas.columns, cellHeight = image.naturalHeight / atlas.rows;
    const crop = frame.crop ?? { x: 0, y: 0, width: 1, height: 1 };
    const h = size * (frame.scale ?? 1), w = h * cellWidth * crop.width / (cellHeight * crop.height);
    const anchorX = frame.anchorX ?? atlas.anchorX, anchorY = frame.anchorY ?? atlas.anchorY;
    const dx = strike.to.x - strike.from.x, neutral = Math.max(4, size * .04);
    const facing = Math.abs(dx) > neutral ? (dx > 0 ? 1 : -1) : figure.facing;
    const breath = 1 + Math.sin(sampleTime * 1.35 + figure.phase) * .006;
    const tipX = ((tip.x - crop.x) / crop.width - anchorX) * w * facing;
    const tipY = ((tip.y - crop.y) / crop.height - anchorY) * h * breath;
    // Bound the entire sampled attack quad rather than hiding clipped anatomy.
    // Near an edge a few pixels of residual reach are preferable to crop loss.
    const margin = 2, left = w * anchorX + margin, right = width - w * (1 - anchorX) - margin;
    const top = h * anchorY * breath + margin, bottom = height - h * (1 - anchorY) * breath - margin;
    const rootX = clamp(strike.to.x - tipX, Math.min(left, right), Math.max(left, right));
    const rootY = clamp(strike.to.y - tipY, Math.min(top, bottom), Math.max(top, bottom));
    const correction = {
      x: rootX - point.x - (strike.to.x - strike.from.x) * .74,
      y: rootY - point.y - (strike.to.y - strike.from.y) * .74,
    };
    // Preserve already convincing short-range contact exactly. Ramp in only
    // when the authored nose would miss by more than its small visual margin.
    const peakGap = Math.hypot(point.x + (strike.to.x - strike.from.x) * .74 + tipX - strike.to.x,
      point.y + (strike.to.y - strike.from.y) * .74 + tipY - strike.to.y);
    const marginOfError = Math.max(3, size * .03);
    const blend = clamp((peakGap - marginOfError) / marginOfError, 0, 1);
    const strength = blend * blend * (3 - 2 * blend);
    const weight = amount / .74 * strength;
    return { x: movement.x + correction.x * weight, y: movement.y + correction.y * weight };
  }

  function prepareFigure(figure: Figure) {
    if (figure.dead !== null && time >= figure.dead && !figure.deathAnchored) {
      const atContact = motionFor(figure, figure.dead - .00001);
      figure.lastPoint = { x: figure.lastPoint.x + atContact.x, y: figure.lastPoint.y + atContact.y };
      figure.deathAnchored = true;
      // Freeze the actual collapse-layout size basis once at contact. Later
      // aspect changes project absolutely from here rather than accumulating
      // irreversible min-axis shrink across alternating viewport shapes.
      figure.deathSizeBasis = { width, height, from: figure.sizeFrom, target: figure.sizeTarget };
    }
    figure.lastPoint = position(figure);
    const currentPose = figurePose(figure);
    // Aim the painted anatomy with the accepted physical gesture. Keep its
    // last direction during reaction/collapse; counters and area casts never
    // invent a new facing. A settled living idle returns to its side profile.
    if (figure.dead === null || time < figure.dead) {
      const gesture = activeGesture(figure);
      if (gesture?.kind === 'physical' && !reduced) {
        const dx = gesture.to.x - gesture.from.x;
        const neutral = Math.max(4, figureSize(figure) * .04);
        if (Math.abs(dx) > neutral) figure.facing = dx > 0 ? 1 : -1;
      } else if (currentPose === 'idle') figure.facing = figure.side === 'enemy' ? -1 : 1;
    }
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
    if (time < figure.born) return;
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
  function figureTransform(figure: Figure) {
    const point = position(figure);
    const size = figureSize(figure);
    const deathAge = figure.dead === null ? -1 : time - figure.dead;
    const movement = motionFor(figure);
    const hitAge = time - figure.hit;
    const recoil = !reduced && hitAge > 0 && hitAge < CREATURE_REACTION_MS / 1000 ? Math.sin(hitAge * 45) * (1 - hitAge / (CREATURE_REACTION_MS / 1000)) * size * .025 : 0;
    const breath = !reduced && deathAge < 0 ? 1 + Math.sin(time * 1.35 + figure.phase) * .006 : 1;
    return { origin: { x: point.x + movement.x + recoil, y: point.y + movement.y }, breath };
  }
  function paintFigure(figure: Figure) {
    if (time < figure.born) return;
    const point = position(figure);
    const size = figureSize(figure);
    const deathAge = figure.dead === null ? -1 : time - figure.dead;
    const alpha = figureOpacity(figure);
    const transform = figureTransform(figure);
    const image = figure.art && imageFor(figure.art.url);
    const atlasImage = figure.animation && imageFor(figure.animation.url);
    const blend = poseBlend(figure);
    ctx.save(); ctx.globalAlpha = alpha;
    ctx.translate(transform.origin.x, transform.origin.y);
    // Mirror the original painted anatomy toward its actual resolved target.
    ctx.scale(figure.facing, transform.breath);
    if (atlasImage && loaded(atlasImage) && figure.animation) {
      const current = poseFrame(figure.animation, figure.pose, time - figure.poseChanged);
      const prior = figure.priorPose && blend < 1 ? poseFrame(figure.animation, figure.priorPose, 0) : null;
      if (prior) drawPose(atlasImage, figure.animation, prior, size, 1 - blend);
      const gesture = !reduced && figure.animation === HOUND_POSES && figure.pose === 'attack' ? activeGesture(figure) : null;
      const jawClosure = gesture?.kind === 'physical' ? houndJawClosure(time-gesture.born) : 0;
      if (current) drawPose(atlasImage, figure.animation, current, size, prior ? blend : 1, jawClosure);
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

  function getUnitViewport(): ArenaUnitViewport {
    return { width, height, canvasAvailable: !disposed, requiredHeight: fieldLayout().requiredHeight,
      layoutPending: !!pendingAllocation || time < allocationTransitionEnd, hunterRect: hunterPlacement().rect };
  }
  function getUnitRegions(): readonly ArenaUnitRegion[] {
    if (disposed) return Object.freeze([]);
    const busy = busyMs() > 0;
    // During terminal presentation the old figures still have useful readouts,
    // but are never legal controls. The reducer owns actual action legality.
    if (!active && !busy) return Object.freeze([]);
    const canonical = new Set([...(previous?.allies ?? []), ...(previous?.enemies ?? [])].map(unit => unit.uid));
    const result: ArenaUnitRegion[] = [];
    for (const figure of figures.values()) {
      const dead = figure.dead !== null;
      if (time < figure.born) continue;
      if ((dead || figure.departing) && !busy) continue;
      // A new binding has a readout from its first summon frame, even while
      // its paint fades in. Only a fully faded corpse loses its region.
      if (dead && figureOpacity(figure) <= 0) continue;
      const size = figureSize(figure), transform = figureTransform(figure);
      const rectFor = (w: number, h: number, ax: number, ay: number) =>
        transformedImageRect(transform.origin, figure.facing, transform.breath, w, h, ax, ay);
      // Portrait and missing-art heraldry share a semantic creature cell.
      // Atlas controls instead use actual source aspect, crop and anchors.
      let rect = rectFor(size, size, .5, .94);
      const atlas = figure.animation, image = atlas && images.get(atlas.url);
      if (atlas && image && loaded(image)) {
        const current = poseFrame(atlas, figure.pose, time - figure.poseChanged);
        const prior = figure.priorPose && poseBlend(figure) < 1 ? poseFrame(atlas, figure.priorPose, 0) : null;
        const boundsFor = (pose: CreaturePoseFrame) => {
          const d = poseDimensions(image, atlas, pose, size);
          return rectFor(d.width, d.height, d.anchorX, d.anchorY);
        };
        if (current) rect = boundsFor(current);
        if (prior) rect = current ? unionRects(rect, boundsFor(prior)) : boundsFor(prior);
      }
      rect = clipToViewport(rect, width, height);
      const cell = figureCell(figure), freeze = (value: BattlefieldRect) => Object.freeze({ ...value });
      const hitRect = clipToViewport(intersectRects(rect, cell.bodyRect), width, height);
      const sideUnits = figure.side === 'ally' ? previous?.allies : previous?.enemies;
      const canonicalIndex = sideUnits?.findIndex(unit => unit.uid === figure.uid) ?? -1;
      const summon = figure.unit.intent?.summon ? [...figure.unit.intent.summon] : undefined;
      if (summon) Object.freeze(summon);
      const readoutUnit = Object.freeze({ ...figure.unit, intent: figure.unit.intent ? Object.freeze({ ...figure.unit.intent, summon }) : undefined });
      result.push(Object.freeze({ uid: figure.uid, side: figure.side, slot: figure.slot,
        readoutUnit, canonicalIndex: canonicalIndex < 0 ? null : canonicalIndex,
        ...rect, feetX: transform.origin.x, feetY: transform.origin.y,
        cell: freeze(cell), bodyRect: freeze(cell.bodyRect), hitRect: freeze(hitRect),
        intentRect: freeze(cell.intentRect), inspectRect: freeze(cell.inspectRect),
        identityRect: freeze(cell.identityRect), statsRect: freeze(cell.statsRect), statusRect: freeze(cell.statusRect),
        disabled: !active || busy || dead || figure.departing || !canonical.has(figure.uid) || hitRect.width <= 0 || hitRect.height <= 0,
        dead, departing: figure.departing }));
    }
    return Object.freeze(result);
  }
  function notifyRegionListener(listener: UnitRegionListener, regions: readonly ArenaUnitRegion[]) {
    // An adapter error must not stop paint, presentation waiters or other users.
    try { listener(regions); } catch (error) { console.error('Battlefield geometry listener failed', error); }
  }
  function publishRegions() {
    const regions = getUnitRegions(), view = getUnitViewport();
    const viewport = `${width}/${height}/${!disposed}/${view.requiredHeight}/${view.layoutPending}/${view.hunterRect.left}/${view.hunterRect.top}/${view.hunterRect.width}/${view.hunterRect.height}`;
    const unchanged = regions.length === publishedRegions.length && regions.every((region, index) => {
      const prior = publishedRegions[index];
      return region.uid === prior.uid && region.side === prior.side && region.slot === prior.slot
        && region.left === prior.left && region.top === prior.top && region.width === prior.width && region.height === prior.height
        && region.feetX === prior.feetX && region.feetY === prior.feetY && region.disabled === prior.disabled
        && region.dead === prior.dead && region.departing === prior.departing
        && region.canonicalIndex === prior.canonicalIndex && JSON.stringify(region.readoutUnit) === JSON.stringify(prior.readoutUnit)
        && sameRect(region.cell, prior.cell) && sameRect(region.bodyRect, prior.bodyRect) && sameRect(region.hitRect, prior.hitRect)
        && sameRect(region.intentRect, prior.intentRect) && sameRect(region.inspectRect, prior.inspectRect)
        && sameRect(region.identityRect, prior.identityRect) && sameRect(region.statsRect, prior.statsRect) && sameRect(region.statusRect, prior.statusRect);
    });
    if (unchanged && viewport === publishedViewport) return;
    publishedRegions = regions; publishedViewport = viewport;
    for (const listener of [...regionListeners]) notifyRegionListener(listener, regions);
  }
  function subscribeUnitRegions(listener: UnitRegionListener): () => void {
    if (disposed) { notifyRegionListener(listener, Object.freeze([])); return () => {}; }
    regionListeners.add(listener); notifyRegionListener(listener, getUnitRegions());
    return () => { regionListeners.delete(listener); };
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
    if (disposed) return;
    advanceAllocation();
    if (document.hidden) { publishRegions(); return; }
    reconcileStrikeEndpoints();
    paintBackdrop(); ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
    if (back) ctx.drawImage(backplate, 0, 0, width, height);
    else { ctx.fillStyle = '#151a20'; ctx.fillRect(0, 0, width, height); }
    const ordered = [...figures.values()];
    ordered.forEach(prepareFigure);
    reconcileStrikeEndpoints();
    ordered.sort((a, b) => position(a).y + motionFor(a).y - position(b).y - motionFor(b).y);
    paintHunterShadow(ctx, hunter, width, height, hunterPlacement());
    ordered.forEach(paintFloor);
    const paintHunterBody = () => {
      const sheet = imageFor(HUNTER_ART_URL);
      if (sheet && loaded(sheet)) paintHunterSheet(ctx, hunter, width, height, time, reduced, sheet, hunterPlacement());
    };
    // The separate observer joins only paint depth, never Unit/formation maps.
    const hunterFoot = hunterGeometry(width,height,hunterPlacement()).feet.y;
    let hunterPainted = false;
    for (const figure of ordered) {
      if (!hunterPainted && position(figure).y + motionFor(figure).y > hunterFoot) {
        paintHunterBody(); hunterPainted = true;
      }
      paintFigure(figure);
    }
    if (!hunterPainted) paintHunterBody();
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
    publishRegions();
  }
  function settle() {
    strikes = []; pendingAllocation = null; actionAllocationSlots.clear(); allocationTransitionEnd = time; lastActionLeadMs = 0; lastActionCueStart = time;
    if (hunter) { hunter.cues = []; if (!hunter.dead) hunter.facing = 1; }
    for (const [uid, figure] of figures) {
      if (figure.dead !== null) figures.delete(uid);
      else { figure.born = time - 2; figure.hit = -10; figure.pose = 'idle'; figure.priorPose = null; figure.poseChanged = time - 2; figure.facing = figure.side === 'enemy' ? -1 : 1; figure.layoutFrom = { ...figure.layoutTarget }; figure.sizeFrom = figure.sizeTarget; figure.layoutStarted = time - 2; }
    }
    if (active && previous) { const desired = desiredAllocation(previous); applyAllocation(desired.config, desired.slots, time, false); }
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
    if (hunter) hunter.cues = hunter.cues.filter(cue => cue.end > time);
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
  function createFigure(unit: Unit, side: Side, slot: number, count: number, born = reduced ? time - 2 : time): Figure {
    const cell = cellFor(side, slot, pendingAllocation?.config ?? layoutConfig);
    const figure: Figure = { uid: unit.uid, unit, art: portraitFor(unit.species), animation: animationFor(unit.species), pose: 'idle', priorPose: null, poseChanged: time - 2, side, facing: side === 'enemy' ? -1 : 1, slot, count, born, hit: -10, dead: null, departing: false, deathAnchored: false, deathSizeBasis: null, phase: random() * 6.28, lastPoint: { x: 0, y: 0 }, layoutFrom: { x: 0, y: 0 }, layoutTarget: { x: 0, y: 0 }, layoutStarted: time - 2, sizeFrom: 0, sizeTarget: 0, cellFrom: cell, cellTarget: cell };
    const target = targetPosition(figure), size = targetSize(figure);
    figure.layoutFrom = target; figure.layoutTarget = target;
    figure.sizeFrom = size; figure.sizeTarget = size; figure.lastPoint = target;
    return figure;
  }

  function render(state: GameState) {
    if (disposed) return;
    const nextEnvironment = encounterEnvironment(state);
    if (nextEnvironment && nextEnvironment !== environment) {
      environment = nextEnvironment; updateEnvironmentLabel(); updateStatus(); backDirty = true;
    }
    hunter = observeHunter(state, hunter ?? undefined);
    active = state.phase === 'battle';
    const starting = active && (!previous || previous.phase !== 'battle');
    if (starting) {
      hunter = observeHunter(state); figures.clear(); strikes = []; pendingAllocation = null; actionAllocationSlots.clear();
      allocationTransitionEnd = time; measuredRows = {}; lastActionLeadMs = 0; lastActionCueStart = time;
      const initial = desiredAllocation(state); layoutConfig = initial.config;
      hunterFrom = hunterTarget = fieldLayout().hunter; hunterStarted = time - 2;
      resolvePresentationWaiters();
    }
    const seen = new Set<string>();
    for (const side of ['ally', 'enemy'] as const) {
      const units = side === 'ally' ? state.allies : state.enemies;
      units.slice(0, 6).forEach((unit, index) => {
        seen.add(unit.uid);
        let figure = figures.get(unit.uid);
        if (!figure) {
          const slot = pendingAllocation?.slots.get(unit.uid) ?? actionAllocationSlots.get(unit.uid) ?? index;
          const born = reduced ? time - 2 : actionAllocationSlots.has(unit.uid) ? lastActionCueStart : pendingAllocation?.cueStart ?? time;
          figure = createFigure(unit, side, slot, units.length, born);
          figures.set(unit.uid, figure);
        } else {
          if (unit.hp < figure.unit.hp) figure.hit = Math.max(figure.hit, time + lastActionLeadMs / 1000 + impactTime);
          figure.unit = unit; figure.side = side; figure.dead = null; figure.deathSizeBasis = null;
        }
      });
    }
    for (const [uid, figure] of figures) if (!seen.has(uid) && figure.dead === null) {
      // A cleared victory party is departing, not fabricated dead units.
      if (figure.side === 'ally' && (state.phase === 'reward' || state.phase === 'victory')) {
        figure.departing = true; continue;
      }
      if (reduced || (previous && previous.phase !== 'battle')) figures.delete(uid);
      else {
        const incoming = strikes.filter(strike => strike.target === uid && strike.kind !== 'heal' && strike.kind !== 'ward').at(-1);
        figure.dead = incoming ? Math.max(time, incoming.born + impactTime) : time + lastActionLeadMs / 1000 + .12;
        figure.unit = { ...figure.unit, hp: 0, block: 0 };
        figure.deathAnchored = false; figure.deathSizeBasis = null;
        figure.departing = figure.side === 'ally' && !active;
      }
    }
    previous = state;
    if (starting || reduced || document.hidden) {
      const desired = desiredAllocation(state);
      if (active) applyAllocation(desired.config, desired.slots, time, false);
    }
    reconcileStrikeEndpoints(); draw(); resolvePresentationWaiters();
  }
  function prepareActionAllocation(before: GameState, after: GameState, events: readonly TransitionEvent[] = []): number {
    const forecast = after.phase === 'battle' ? after : before;
    const desired = desiredAllocation(forecast), slots = new Map<string, number>();
    const occupied: Record<Side, Set<number>> = { ally: new Set(), enemy: new Set() };
    // Every held body reserves its original slot until its collapse finishes.
    // A full side may reuse a resolved victim's slot, but the new birth is
    // delayed below until that victim's complete hold has ended.
    for (const figure of figures.values()) {
      slots.set(figure.uid, figure.slot); occupied[figure.side].add(figure.slot);
    }
    const arrivals = events.filter((event): event is Extract<TransitionEvent, { type: 'summon' }> => event.type === 'summon');
    for (const side of ['ally', 'enemy'] as const) {
      const reclaimed = new Set<number>();
      const willDie = (figure: Figure) => figure.dead !== null || events.some(event => event.type === 'death' && event.target === figure.uid);
      const victims = [...figures.values()].filter(figure => figure.side === side && willDie(figure) &&
        ![...figures.values()].some(other => other.uid !== figure.uid && other.side === side && other.slot === figure.slot && !willDie(other)));
      const units = [...(side === 'ally' ? after.allies : after.enemies), ...arrivals.filter(event => event.side === side).map(event => event.unit)];
      for (const unit of units) if (!slots.has(unit.uid)) {
        const free = [0, 1, 2, 3, 4, 5].find(slot => !occupied[side].has(slot));
        const victim = victims.find(figure => !reclaimed.has(figure.slot));
        const slot = free ?? victim?.slot;
        if (slot === undefined) throw new Error('No legal presentation slot for accepted arrival');
        if (free === undefined) reclaimed.add(slot);
        slots.set(unit.uid, slot); occupied[side].add(slot);
      }
    }
    actionAllocationSlots = slots;
    const extent = (side: Side) => Math.max(0, ...[...slots].filter(([uid]) => figures.get(uid)?.side === side || arrivals.some(event => event.target === uid && event.side === side) || (side === 'ally' ? after.allies : after.enemies).some(unit => unit.uid === uid)).map(([, slot]) => slot + 1));
    const config = normalizeLayoutConfig({ allies: Math.max(layoutConfig.allies, extent('ally')),
      enemies: Math.max(layoutConfig.enemies, extent('enemy')),
      intentRows: Math.max(layoutConfig.intentRows, desired.config.intentRows), statsRows: Math.max(layoutConfig.statsRows, desired.config.statsRows),
      identityRows: Math.max(layoutConfig.identityRows ?? 1, desired.config.identityRows ?? 1) });
    const expanding = !sameLayoutConfig(config, layoutConfig);
    if (!expanding && !pendingAllocation) return 0;
    if (pendingAllocation) {
      pendingAllocation.config = config; pendingAllocation.slots = slots;
      return Math.max(0, pendingAllocation.cueStart - time);
    }
    if (!allocationChanges(config, slots)) { applyAllocation(config, slots, time, false); return 0; }
    const start = time + cueBusyMs() / 1000;
    pendingAllocation = { config, slots, start, cueStart: start + .32 };
    advanceAllocation(); publishRegions();
    return Math.max(0, start + .32 - time);
  }
  function reusedArrivalHold(after: GameState, events: readonly TransitionEvent[] = []): number {
    // Current rules cannot kill and reuse their own arrival side in one trace:
    // allied binds may burn enemies, enemy phases hit bindings/the hunter.
    // A legal reused slot therefore holds a previously scheduled old corpse.
    const arrivals = new Map<string, Side>();
    for (const event of events) if (event.type === 'summon') arrivals.set(event.target, event.side);
    for (const side of ['ally', 'enemy'] as const)
      for (const unit of side === 'ally' ? after.allies : after.enemies)
        if (!figures.has(unit.uid)) arrivals.set(unit.uid, side);
    let end = time;
    for (const [uid, side] of arrivals) {
      const slot = actionAllocationSlots.get(uid); if (slot === undefined) continue;
      for (const old of figures.values()) if (old.uid !== uid && old.side === side && old.slot === slot && old.dead !== null)
        end = Math.max(end, old.dead + deathDuration);
    }
    return Math.max(0, end - time);
  }
  function referencedFutureBirthHold(events: readonly TransitionEvent[] = []): number {
    // Canonical actions may touch an earlier accepted arrival before first
    // paint. Delay only this action's actually traced sources/targets, rather
    // than locking unrelated actions behind every optional presentation cue.
    let end = time;
    for (const event of events) for (const uid of [event.source, event.target]) {
      const figure = figures.get(uid);
      if (figure && figure.born > time) end = Math.max(end, figure.born);
    }
    return Math.max(0, end - time);
  }
  function queueStrike(source: string | null, target: string, kind: Strike['kind'], delay = 0) {
    const from = source ? sourcePoint(source) : { x: width * .34, y: height * .82 };
    const to = combatPoint(target);
    const strike: Strike = { source, target, from, to, born: time + delay, kind };
    strikes.push(strike);
    const targetFigure = figures.get(target); if (targetFigure && (kind === 'physical' || kind === 'magic' || kind === 'counter')) targetFigure.hit = time + delay + impactTime;
    return strike;
  }
  /** Observe an accepted rule action. This only schedules presentation effects. */
  function playAction(action: Action, before: GameState, after: GameState, events?: readonly TransitionEvent[]) {
    if (disposed) return;
    if (reduced || document.hidden || before.phase !== 'battle') {
      lastActionLeadMs = 0; lastActionCueStart = time;
      if (reduced || document.hidden) {
        strikes = []; pendingAllocation = null; actionAllocationSlots.clear(); if (hunter) hunter.cues = [];
      }
      render(after);
      if (reduced || document.hidden) { settle(); draw(); }
      return;
    }
    try {
    const referencedBirthLead = referencedFutureBirthHold(events);
    const allocationLead = prepareActionAllocation(before, after, events);
    // One action anchor controls birth, gestures, impacts, and the host's audio
    // anchor. Every referenced earlier newborn is visible by that anchor; no
    // later per-arrival hold may silently move only the painted body.
    const lead = Math.max(allocationLead, reusedArrivalHold(after, events), referencedBirthLead);
    lastActionLeadMs = Math.ceil(lead * 1000); lastActionCueStart = time + lead;
    if (events) {
      const actorDelays = new Map<string, number>();
      const lastHits = new Map<string, Strike>();
      const terminal = after.phase !== 'battle';
      const delayFor = (source: string, retaliation = false) => {
        if (retaliation) return lead + .04;
        if (action.type !== 'endTurn' || !before.enemies.some(unit => unit.uid === source)) return lead;
        if (!actorDelays.has(source)) actorDelays.set(source, actorDelays.size * (terminal ? .009 : .05));
        return lead + actorDelays.get(source)!;
      };
      for (const event of events) {
        const source = event.source === 'world' ? null : event.source;
        if (event.type === 'summon') {
          if (!figures.has(event.target)) {
            const units = event.side === 'ally' ? after.allies : after.enemies;
            const canonicalSlot = units.findIndex(unit => unit.uid === event.target);
            const occupied = new Set([...figures.values()].filter(figure => figure.side === event.side && figure.dead === null).map(figure => figure.slot));
            const slot = actionAllocationSlots.get(event.target) ?? ([0, 1, 2, 3, 4, 5].find(candidate => !occupied.has(candidate)) ?? (canonicalSlot >= 0 ? canonicalSlot : 0));
            const birth = lastActionCueStart;
            figures.set(event.target, createFigure(event.unit, event.side, slot, Math.max(units.length, slot + 1), birth));
          }
          queueStrike(source, event.target, 'ward', delayFor(event.source));
        } else if (event.type === 'hit') {
          // The trace proves this hit executed. Its pre-action intent identifies
          // ranged area casts without parsing localized labels or replaying intent.
          const caster = before.enemies.find(unit => unit.uid === event.source);
          const areaCast = event.kind === 'enemy' && caster?.intent?.target === 'all';
          const kind = event.kind === 'retaliation' ? 'counter' : event.kind === 'command' || (event.kind === 'enemy' && !areaCast && !/wraith|necromancer/.test(caster?.species ?? figures.get(event.source)?.unit.species ?? '')) ? 'physical' : 'magic';
          const strike = queueStrike(source, event.target, kind, delayFor(event.source, event.kind === 'retaliation'));
          lastHits.set(event.target, strike);
          const readout = figures.get(event.target);
          if (readout) readout.unit = { ...readout.unit, hp: event.afterHp, block: Math.max(0, readout.unit.block - event.blocked) };
        } else if (event.type === 'control' || event.type === 'buff') {
          // Intent cancellation and attack rallies are real resolved effects,
          // but do not create fabricated damage, recoil or attack movement.
          queueStrike(source, event.target, event.type, delayFor(event.source));
          const readout = figures.get(event.target);
          if (readout) readout.unit = event.type === 'control' ? { ...readout.unit, intent: event.after } : { ...readout.unit, attack: event.after };
        } else if (event.type === 'heal' || event.type === 'ward') {
          queueStrike(source, event.target, event.type === 'heal' ? 'heal' : 'ward', delayFor(event.source));
          const readout = figures.get(event.target);
          if (readout) readout.unit = event.type === 'heal' ? { ...readout.unit, hp: event.afterHp } : { ...readout.unit, block: readout.unit.block + event.amount };
        } else if (event.type === 'death' && event.target !== 'hunter') {
          const figure = figures.get(event.target), hit = lastHits.get(event.target);
          if (figure) {
            figure.dead = hit ? hit.born + impactTime : time + lead + .12;
            figure.unit = { ...figure.unit, hp: 0, block: 0 };
            figure.deathAnchored = false; figure.deathSizeBasis = null; figure.departing = false;
          }
        }
      }
      // A future rule that kills and reuses its own same-side slot needs an
      // explicit multi-phase timing contract. Fail optional presentation rather
      // than silently desynchronizing the already published common audio lead.
      for (const event of events) if (event.type === 'summon') {
        const arrival = figures.get(event.target); if (!arrival) continue;
        const overlapsHold = [...figures.values()].some(old => old.uid !== arrival.uid && old.side === arrival.side &&
          old.slot === arrival.slot && old.dead !== null && old.dead + deathDuration > arrival.born + .000001);
        if (overlapsHold) throw new Error('Accepted arrival needs an unsupported same-action slot hold');
      }
      if (hunter) {
        const gesture = events.find(e => e.target !== 'hunter' && e.type !== 'death' && figures.has(e.target) &&
          (e.source === 'hunter' || (e.type === 'hit' && e.kind === 'command')));
        if (gesture) { const dx = combatPoint(gesture.target).x - hunterGeometry(width,height,hunterPlacement()).feet.x;
          if (Math.abs(dx) > 4) hunter.facing = dx > 0 ? 1 : -1; }
        hunter.cues.push(...hunterEventCues(events, time, delayFor));
      }
      render(after); return;
    }
    if (action.type === 'attack') queueStrike(action.unit, action.target, 'physical', lead);
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
          queueStrike(null, unit.uid, kind, lead + i * .035);
        });
        else if ('target' in action && action.target) queueStrike(null, action.target, 'magic', lead);
      }
    }
    // Callers without a canonical trace still show state changes. They do not
    // manufacture enemy attacks from intents that may never have executed.
    render(after);
    } catch (error) {
      // An optional presentation failure cannot retain a geometry/input lock.
      pendingAllocation = null; actionAllocationSlots.clear(); allocationTransitionEnd = time; lastActionLeadMs = 0; lastActionCueStart = time;
      try {
        strikes = []; figures.clear(); if (hunter) hunter.cues = [];
        previous = null; render(after); settle(); draw();
      } catch { resolvePresentationWaiters(); }
      throw error;
    }
  }
  function cueBusyMs() {
    if (disposed || reduced || document.hidden) return 0;
    let end = time;
    for (const cue of hunter?.cues ?? []) end = Math.max(end, cue.end);
    for (const strike of strikes) end = Math.max(end, strike.born + .73);
    for (const figure of figures.values()) {
      if (figure.dead !== null) end = Math.max(end, figure.dead + deathDuration);
      else if (!figure.departing) end = Math.max(end, figure.born + .38, figure.hit + CREATURE_REACTION_MS / 1000, figure.layoutStarted + .32);
    }
    return Math.max(0, Math.ceil((end - time) * 1000));
  }
  function busyMs() {
    if (disposed || reduced || document.hidden) return 0;
    return Math.max(cueBusyMs(), Math.max(0, Math.ceil(((pendingAllocation?.cueStart ?? allocationTransitionEnd) - time) * 1000)));
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
    const bounds = canvas.getBoundingClientRect();
    const nextWidth = Math.max(1, bounds.width || 900), nextHeight = Math.max(1, bounds.height || 400);
    const nextRatio = Math.min(window.devicePixelRatio || 1, 1.5);
    const pixelWidth = Math.round(nextWidth * nextRatio), pixelHeight = Math.round(nextHeight * nextRatio);
    const geometryChanged = nextWidth !== width || nextHeight !== height;
    if (!geometryChanged && canvas.width === pixelWidth && canvas.height === pixelHeight && nextRatio === ratio) return;
    const priorWidth = width, priorHeight = height;
    const scaleX = nextWidth / priorWidth, scaleY = nextHeight / priorHeight;
    width = nextWidth; height = nextHeight; ratio = nextRatio;
    canvas.width = pixelWidth; canvas.height = pixelHeight;
    ctx.imageSmoothingEnabled = true; ctx.imageSmoothingQuality = 'high';
    backDirty = true;
    // A host layout change is not cancellation. Keep all semantic cue, impact,
    // collapse and waiter times; map their geometry into the new CSS viewport.
    // Living formations retain their interpolation progress. Removed figures
    // retain their contact position and shrink uniformly when either axis does,
    // so a death remnant never stretches or keeps an obsolete screen position.
    if (geometryChanged) for (const figure of figures.values()) {
      const reproject = (point: Point): Point => ({ x: point.x * scaleX, y: point.y * scaleY });
      figure.lastPoint = reproject(figure.lastPoint);
      figure.layoutFrom = reproject(figure.layoutFrom);
      figure.cellFrom = projectCell(figure.cellFrom, scaleX, scaleY);
      figure.cellTarget = cellFor(figure.side, figure.slot, figure.born > time ? pendingAllocation?.config ?? layoutConfig : layoutConfig);
      if (figure.dead !== null) {
        figure.layoutTarget = reproject(figure.layoutTarget);
        // Scheduled deaths also need a stable basis before their contact
        // frame. prepareFigure finalizes it once when the body anchors.
        const basis = figure.deathSizeBasis ??= { width: priorWidth, height: priorHeight, from: figure.sizeFrom, target: figure.sizeTarget };
        const scale = Math.min(width / basis.width, height / basis.height);
        figure.sizeFrom = basis.from * scale; figure.sizeTarget = basis.target * scale;
      } else {
        const target = targetPosition(figure), size = targetSize(figure);
        const scale = figure.sizeTarget > 0 ? size / figure.sizeTarget : Math.min(scaleX, scaleY);
        figure.layoutTarget = target;
        figure.sizeFrom *= scale; figure.sizeTarget = size;
      }
    }
    const projectHunter = (value: BattlefieldHunterGeometry): BattlefieldHunterGeometry => {
      const scale = Math.min(scaleX, scaleY), fullCell = value.bodyHeight * 512 / 418 * scale;
      const feet = { x: value.feet.x * scaleX, y: value.feet.y * scaleY };
      return { feet, torso: { x: value.torso.x * scaleX, y: value.torso.y * scaleY },
        bodyHeight: value.bodyHeight * scale, bodyWidth: value.bodyWidth * scale,
        rect: { left: feet.x - fullCell / 2, top: feet.y - fullCell * 502 / 512, width: fullCell, height: fullCell * 573 / 512 } };
    };
    if (geometryChanged) { if (hunterFrom) hunterFrom = projectHunter(hunterFrom); hunterTarget = fieldLayout().hunter; }
    reconcileStrikeEndpoints(); draw();
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
    getUnitRegions, getUnitViewport, subscribeUnitRegions, setReadoutMetrics,
    getActionPresentationDelayMs() { return lastActionLeadMs; },
    setSelected(uid: string | null) { selected = uid; draw(); },
    resize,
    dispose() {
      if (disposed) return; disposed = true; cancelAnimationFrame(frame); resolvePresentationWaiters();
      publishRegions(); regionListeners.clear();
      resizeObserver?.disconnect(); motionObserver.disconnect();
      motionQuery.removeEventListener('change', updateMotion);
      document.removeEventListener('visibilitychange', resume); window.removeEventListener('resize', resize);
      images.forEach(image => { image.onload = null; image.onerror = null; }); images.clear(); figures.clear(); strikes = [];
      status.remove(); backplate.width = 0; backplate.height = 0;
    },
  };
}
