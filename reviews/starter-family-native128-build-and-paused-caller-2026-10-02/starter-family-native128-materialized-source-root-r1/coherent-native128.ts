import type { GameState, Unit } from './engine';
import { CARDS } from './content';
import { COHERENT_NATIVE128 } from './art';
import { normalizeLayoutConfig, type ArenaLayoutConfig, type BattlefieldLayout, type BattlefieldCell } from './battlefield-layout';
/** SOURCE PROPOSAL ONLY: no imports, startup, engine/save/input access or asset fetch.
 * Not compiled or browser-tested. Integration must publish this exact geometry.
 */
export interface CssRect { left: number; top: number; width: number; height: number }
export interface Point { x: number; y: number }
export interface Native128Placement {
  backingRect: CssRect;
  cssRect: CssRect;
  cssFeet: Point;
  scale: number;
}
export interface Native128Sprite {
  /** Supplied only from the future exact converted/cleaned manifest. */
  image: HTMLImageElement;
  anchor: readonly [64, 120];
  /** Integer manually authored native landmark; null means no known contact. */
  contact?: readonly [number, number];
}

/** CSS geometry stays in the existing layout; draw geometry uses backing pixels.
 * Returning null is a real layout failure, never permission to shrink fractionally.
 */
export function placeNative128(body: CssRect, feet: Point, ratio: number): Native128Placement | null {
  if (![body.left, body.top, body.width, body.height, feet.x, feet.y, ratio].every(Number.isFinite)
      || ratio <= 0 || body.width <= 0 || body.height <= 0) return null;
  const left = Math.ceil(body.left * ratio), top = Math.ceil(body.top * ratio);
  const right = Math.floor((body.left + body.width) * ratio);
  const bottom = Math.floor((body.top + body.height) * ratio);
  const scale = Math.floor(Math.min(right - left, bottom - top) / 128);
  if (scale < 1) return null;
  const edge = 128 * scale;
  const x = Math.max(left, Math.min(right - edge, Math.round(feet.x * ratio) - 64 * scale));
  const y = Math.max(top, Math.min(bottom - edge, Math.round(feet.y * ratio) - 120 * scale));
  const backingRect = { left: x, top: y, width: edge, height: edge };
  return { backingRect, scale,
    cssRect: { left: x / ratio, top: y / ratio, width: edge / ratio, height: edge / ratio },
    cssFeet: { x: (x + 64 * scale) / ratio, y: (y + 120 * scale) / ratio } };
}

/** Draw the genuinely authored facing, without the arena's mirror/breath transform.
 * Set an identity transform because placement is already in backing coordinates.
 */
export function drawNative128(ctx: CanvasRenderingContext2D, sprite: Native128Sprite,
  placement: Native128Placement): boolean {
  const image = sprite.image;
  if (!image.complete || image.naturalWidth !== 128 || image.naturalHeight !== 128) return false;
  const p = placement.backingRect;
  if (![p.left, p.top, p.width, p.height, placement.scale].every(Number.isInteger)
      || placement.scale < 1 || p.width !== 128 * placement.scale || p.height !== p.width) return false;
  ctx.save();
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.imageSmoothingEnabled = false;
  ctx.globalAlpha = 1;
  ctx.drawImage(image, 0, 0, 128, 128, p.left, p.top, p.width, p.height);
  ctx.restore();
  return true;
}

/** Contact is derived from the SAME snapped quad; never an inherited512px crop. */
export function nativeLandmark(placement: Native128Placement, point: readonly [number, number],
  ratio: number): Point | null {
  if (ratio <= 0 || !Number.isFinite(ratio) || !point.every(Number.isInteger)
      || point[0] < 0 || point[0] > 128 || point[1] < 0 || point[1] > 128) return null;
  return { x: (placement.backingRect.left + point[0] * placement.scale) / ratio,
    y: (placement.backingRect.top + point[1] * placement.scale) / ratio };
}

/** Optional directly authored native32 masonry tile as SOURCE indices only.
 * Indices use the tentative shared palette:1 darkest,2 dark,3 base,4 light.
 * No bitmap, randomness, filtering, background extraction or perspective warp.
 */
export function floorIndex32(x: number, y: number): 1 | 2 | 3 | 4 {
  if (!Number.isInteger(x) || !Number.isInteger(y) || x < 0 || y < 0 || x >= 32 || y >= 32)
    throw new RangeError('Native floor coordinates must be integers0..31');
  // Staggered slabs: one vertical joint in the upper band, edge joint below.
  if (y === 0 || y === 16 || (y < 16 && x === 16) || (y >= 16 && x === 0)) return 1;
  if (y === 15 || y === 31 || (y < 16 && x === 15) || (y >= 16 && x === 31)) return 2;
  // Top/left light clusters, consistent with the requested light direction.
  if (y === 1 || y === 17 || (y < 16 && (x === 0 || x === 17)) || (y >= 16 && x === 1)) return 4;
  // Two explicitly placed short cracks; no noisy generated stone texture.
  if ((y === 8 && x >= 4 && x <= 6) || (y === 9 && x === 6)
      || (y === 24 && x >= 23 && x <= 25) || (y === 25 && x === 23)) return 2;
  return 3;
}

/** Cache in the opt-in backplate, not redraw every tile for every animation frame.
 * Palette must be supplied by the same future approved scene manifest.
 */
export function drawFloorTile32(ctx: CanvasRenderingContext2D, palette: readonly string[],
  backingX: number, backingY: number, integerScale: number): void {
  if (palette.length !== 15 || ![backingX, backingY, integerScale].every(Number.isInteger)
      || integerScale < 1) throw new RangeError('Invalid shared palette/integer floor placement');
  ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1;
  ctx.imageSmoothingEnabled = false;
  for (let y = 0; y < 32; y++) {
    let x = 0;
    while (x < 32) {
      const index = floorIndex32(x, y), start = x;
      while (x < 32 && floorIndex32(x, y) === index) x++;
      ctx.fillStyle = palette[index - 1];
      ctx.fillRect(backingX + start * integerScale, backingY + y * integerScale,
        (x - start) * integerScale, integerScale);
    }
  }
  ctx.restore();
}

const BASE = new URL(`${import.meta.env.BASE_URL}art/`, document.baseURI);
const starterBodyKey = (cardId: string): number | null => {
  const id = cardId.endsWith('+') ? cardId.slice(0, -1) : cardId;
  return id === 'cairnhound' ? 0 : id === 'ashwidow' ? 7 : id === 'fenstalker' ? 9 : id === 'briarcolossus' ? 11 : null;
};
const starterPortraitKey = (cardId: string): number | null => {
  const body = starterBodyKey(cardId);
  return body === null ? null : body === 0 ? 4 : body + 1;
};
const keyFor = (unit: Unit, side: 'ally' | 'enemy'): number | null => side === 'ally'
  ? starterBodyKey(unit.cardId)
  : unit.cardId === 'raider' ? (unit.hp <= 0 ? 6 : 1) : unit.cardId === 'revenant' ? 2 : null;
/** All-or-baseline decoding; no render/reducer/input callback on asset arrival. */
export function createCoherentNative128(requested: boolean) {
  let ready = false, disposed = false;
  const images: HTMLImageElement[] = [], urls: string[] = [];
  const abort = new AbortController();
  const digest = async (bytes: ArrayBuffer) => Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256', bytes)), n => n.toString(16).padStart(2, '0')).join('');
  async function load() {
    try {
      const response = await fetch(new URL(COHERENT_NATIVE128.manifest, BASE), { signal: abort.signal });
      if (!response.ok) throw new Error('Native manifest unavailable');
      const bytes = await response.arrayBuffer();
      if (await digest(bytes) !== COHERENT_NATIVE128.manifestSha256) throw new Error('Native manifest identity');
      const manifest = JSON.parse(new TextDecoder().decode(bytes));
      if (COHERENT_NATIVE128.sprites.length !== 13) throw new Error('Native thirteen-image contract');
      if (manifest.animation !== null || manifest.palette?.transparent_index !== 0
          || JSON.stringify(manifest.palette.opaque_colors) !== JSON.stringify(COHERENT_NATIVE128.palette)
          || JSON.stringify(manifest.dimensions) !== '[128,128]'
          || JSON.stringify(manifest.sprites) !== JSON.stringify(COHERENT_NATIVE128.sprites)) throw new Error('Native manifest contract');
      for (const row of COHERENT_NATIVE128.sprites) {
        const imageResponse = await fetch(new URL(row.filename, BASE), { signal: abort.signal });
        if (!imageResponse.ok) throw new Error('Native image unavailable');
        const data = await imageResponse.arrayBuffer();
        if (await digest(data) !== row.sha256) throw new Error('Native image identity');
        if (disposed) return;
        const url = URL.createObjectURL(new Blob([data], { type: 'image/png' })); urls.push(url);
        const image = new Image(); image.src = url; await image.decode();
        if (image.naturalWidth !== 128 || image.naturalHeight !== 128) throw new Error('Native image dimensions');
        const probe = document.createElement('canvas'); probe.width = probe.height = 128;
        const context = probe.getContext('2d', { willReadFrequently: true });
        if (!context) throw new Error('Native pixel validation unavailable');
        context.drawImage(image, 0, 0);
        const pixels = context.getImageData(0, 0, 128, 128).data;
        const allowed = new Set(COHERENT_NATIVE128.palette.map(hex => parseInt(hex.slice(1), 16)));
        for (let i = 0; i < pixels.length; i += 4) {
          if (pixels[i + 3] !== 0 && pixels[i + 3] !== 255) throw new Error('Native binary alpha');
          if (pixels[i + 3] === 255 && !allowed.has((pixels[i] << 16) | (pixels[i + 1] << 8) | pixels[i + 2])) throw new Error('Native shared palette');
        }
        probe.width = probe.height = 0; images.push(image);
      }
      if (!disposed && images.length === 13) ready = true;
    } catch { ready = false; /* Whole baseline; missing/invalid data is never mixed. */ }
  }
  if (requested) void load();
  return {
    requested, get ready() { return ready && !disposed; },
    supports(state: GameState) {
      return state.phase === 'battle' && state.allies.every(u => keyFor(u, 'ally') !== null)
        && state.enemies.every(u => keyFor(u, 'enemy') !== null)
        && state.hand.every(id => CARDS[id]?.type !== 'summon' || starterPortraitKey(id) !== null);
    },
    unit(unit: Unit, side: 'ally' | 'enemy'): Native128Sprite | null {
      const key = keyFor(unit, side); return ready && key !== null ? { image: images[key], anchor: [64, 120] } : null;
    },
    hunter(): Native128Sprite | null { return ready ? { image: images[3], anchor: [64, 120] } : null; },
    portrait(kind: 'hound' | 'hunter') { return ready && !disposed ? images[kind === 'hound' ? 4 : 5].src : ''; },
    cardPortrait(cardId: string) { const key = starterPortraitKey(cardId); return ready && !disposed && key !== null ? images[key].src : ''; },
    palette: COHERENT_NATIVE128.palette,
    dispose() { disposed = true; ready = false; abort.abort(); urls.forEach(url => URL.revokeObjectURL(url)); images.length = 0; },
  };
}
export type CoherentNative128 = ReturnType<typeof createCoherentNative128>;
/** Sparse, two-rank presentation only. Inadequate space selects the entire baseline. */
export function native128Layout(width: number, height: number, ratio: number, input: ArenaLayoutConfig): BattlefieldLayout | null {
  const config = normalizeLayoutConfig(input);
  if (config.allies > 2 || config.enemies > 2 || !Number.isFinite(ratio) || ratio <= 0) return null;
  const edge = 128 * Math.ceil(ratio) / ratio;
  const intent = config.intentRows * 16, identity = (config.identityRows ?? 1) * 16, stats = config.statsRows * 16;
  const inspect = identity + stats, enemyHeight = intent + edge + inspect;
  const allyHeight = edge + inspect + 16, requiredHeight = enemyHeight + 12 + allyHeight;
  if (width < 800 || height + .01 < requiredHeight) return null;
  const make = (side: 'ally' | 'enemy'): BattlefieldCell[] => {
    const count = side === 'ally' ? config.allies : config.enemies, result: BattlefieldCell[] = [];
    const top = side === 'ally' ? height - allyHeight : 0, before = side === 'enemy' ? intent : 0;
    const band = side === 'ally' ? (width - edge - 48) / 2 : (width - 32) / Math.max(1, count);
    for (let slot = 0; slot < count; slot++) {
      const center = side === 'ally' ? (slot === 0 ? 8 + band / 2 : width - 8 - band / 2) : 16 + band * (slot + .5);
      const bodyRect = { left: Math.round((center - edge / 2) * ratio) / ratio, top: Math.round((top + before) * ratio) / ratio, width: edge, height: edge };
      // Fixed native backing quad is also the full accessible target rectangle.
      const left = center - Math.min(240, band - 8) / 2, readoutWidth = Math.min(240, band - 8);
      const inspectRect = { left, top: bodyRect.top + edge, width: readoutWidth, height: inspect };
      result.push({ left: left, top, width: readoutWidth, height: side === 'ally' ? allyHeight : enemyHeight, bodyRect,
        intentRect: { left, top, width: readoutWidth, height: side === 'enemy' ? intent : 0 }, inspectRect,
        identityRect: { ...inspectRect, height: identity }, statsRect: { ...inspectRect, top: inspectRect.top + identity, height: stats },
        statusRect: { left, top: inspectRect.top + inspect, width: readoutWidth, height: side === 'ally' ? 16 : 0 } });
    }
    return result;
  };
  const hunterRect = { left: Math.round((width - edge) / 2 * ratio) / ratio, top: Math.round((height - allyHeight) * ratio) / ratio, width: edge, height: edge };
  const feet = { x: hunterRect.left + edge / 2, y: hunterRect.top + edge * 120 / 128 };
  return { requiredHeight, ally: make('ally'), enemy: make('enemy'), hunter: { feet, torso: { x: feet.x, y: hunterRect.top + edge * .45 }, bodyHeight: edge, bodyWidth: edge, rect: hunterRect } };
}
export function native128In(body: CssRect, ratio: number) {
  const p = placeNative128(body, { x: body.left + body.width / 2, y: body.top + body.height * 120 / 128 }, ratio);
  return p && p.cssRect.width >= 128 && p.cssRect.height >= 128 ? p : null;
}
/** Deliberately authored semantic native32 tool symbols. Names/rules remain live text. */
export function pixelToolSymbol(effect: string): string {
  const shapes: Record<string, readonly (readonly [number, number, number, number])[]> = {
    damage: [[6,23,4,4],[10,19,4,4],[14,15,4,4],[18,11,4,4],[22,5,4,6],[7,15,3,8],[11,23,8,3]],
    block: [[7,5,18,3],[7,8,3,14],[22,8,3,14],[10,22,12,3],[13,25,6,3],[15,10,3,12]],
    heal: [[13,5,6,22],[5,13,22,6]],
    draw: [[4,7,11,18],[17,7,11,18],[15,9,2,18],[6,11,7,2],[19,11,7,2],[6,16,7,2],[19,16,7,2]],
    rally: [[7,4,3,25],[10,5,15,12],[13,17,9,3]],
    ready: [[5,14,16,4],[17,7,4,18],[21,11,4,10],[25,15,3,2]],
    aoe: [[5,18,5,9],[11,11,5,16],[17,5,5,22],[23,14,4,13]],
    siphon: [[7,5,18,3],[10,8,3,11],[19,8,3,11],[13,19,6,3],[15,22,2,5],[9,27,14,2]],
    energy: [[17,3,6,9],[11,12,12,5],[11,17,6,11],[7,12,4,5]],
  };
  const chosen = shapes[effect] ?? [[6,5,20,3],[6,8,3,18],[23,8,3,18],[9,26,14,3],[12,12,8,3],[12,18,8,3]];
  return `<svg class="coherent-tool-symbol" aria-hidden="true" viewBox="0 0 32 32" width="32" height="32" shape-rendering="crispEdges">${chosen.map(([x,y,w,h]) => `<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${COHERENT_NATIVE128.palette[6]}"/>`).join('')}</svg>`;
}

/** CANDIDATE SOURCE ONLY: broken courtyard depth, not accepted art or animation.
 * All rectangles use the creature scene's shared palette and integer backing grid.
 * A low ruined-wall horizon stays below the far row's native120px foot anchor.
 * Cache this complete backplate on canvas-size change; no actor/layout authority.
 */
export function drawNativeCourtyard(ctx: CanvasRenderingContext2D, palette: readonly string[],
  backingWidth: number, backingHeight: number, integerScale: number): void {
  if (palette.length !== 15 || ![backingWidth, backingHeight, integerScale].every(Number.isInteger)
      || backingWidth < 1 || backingHeight < 1 || integerScale < 1)
    throw new RangeError('Invalid shared courtyard palette/integer extent');
  const width = Math.ceil(backingWidth / integerScale), height = Math.ceil(backingHeight / integerScale);
  // A low distant parapet leaves the plane dominant; it is not another brick wall.
  const horizon = Math.min(18, Math.floor(height * .10));
  const vanishX = Math.floor(width * .54), vanishY = Math.max(0, horizon - 6);
  const nearPitch = Math.max(24, Math.round(width / 5));
  ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1;
  ctx.imageSmoothingEnabled = false;
  // Logical integer spans scale once; no paths, gradients, alpha blends or new colours.
  const rect = (x: number, y: number, w: number, h: number, color: number) => {
    const left = Math.max(0, Math.round(x) * integerScale), top = Math.max(0, Math.round(y) * integerScale);
    const right = Math.min(backingWidth, Math.round(x + w) * integerScale);
    const bottom = Math.min(backingHeight, Math.round(y + h) * integerScale);
    if (right <= left || bottom <= top) return;
    ctx.fillStyle = palette[color]; ctx.fillRect(left, top, right - left, bottom - top);
  };
  ctx.fillStyle = palette[0]; ctx.fillRect(0, 0, backingWidth, backingHeight);
  const parapet: readonly (readonly [number, number, number])[] = [
    [.00,.16,5],[.16,.15,8],[.31,.07,3],[.64,.12,4],[.76,.13,7],[.89,.11,5],
  ];
  for (const [start, span, rise] of parapet) {
    const x = Math.round(width * start), w = Math.ceil(width * span);
    const y = Math.max(0, horizon - rise);
    rect(x,y,w,horizon-y,1);
    // Only a few dim top-left chips; no repeating vertical masonry courses.
    rect(x+1,y,Math.min(w-1,9),1,2);
  }
  rect(0,horizon,width,height-horizon,2);
  rect(0,horizon,width,1,1);
  // Receding ground joints share one vanishing region. This changes paint only,
  // not sprite positions, their projected floor, hit regions or scene geometry.
  const rayX = (nearX: number, y: number) => vanishX
    + Math.floor((nearX-vanishX)*(y-vanishY)/(height-vanishY));
  for (let column=-7; column<=7; column++) {
    const nearX = vanishX + column*nearPitch;
    for (let y=horizon+2; y<height; y++) rect(rayX(nearX,y),y,1,1,1);
  }
  // Spacing compresses toward the distance; the old rectangular block rows did
  // not converge. Thin low-contrast joints keep creatures/readouts dominant.
  const depth = [0,2,5,10,18,29,44,64,82,100] as const;
  const courses = depth.map(value => horizon + Math.floor((height-horizon)*value/100));
  for (let row=1; row<courses.length-1; row++) {
    const y = courses[row];
    if (y<=horizon || y>=height || y===courses[row-1]) continue;
    rect(0,y,width,1,1);
  }
  // Sparse shallow stone wear lies between the same ray joints, rather than
  // filling each course with bright rectangular bricks. Upper-left clusters
  // use the existing cold-stone light; lower-right recesses stay subdued.
  const wear: readonly (readonly [number,number])[] = [[3,-2],[5,1],[7,-1],[8,2]];
  for (const [row,column] of wear) {
    const top = courses[row]+2, bottom = courses[row+1]-1;
    if (bottom<=top || top>=height) continue;
    const nearLeft=vanishX+column*nearPitch, nearRight=nearLeft+nearPitch;
    for (let y=top; y<Math.min(bottom,top+3); y++) {
      const left=rayX(nearLeft,y)+3, right=rayX(nearRight,y)-3;
      rect(left,y,Math.max(0,Math.floor((right-left)/3)),1,3);
    }
    const ry=bottom-1, left=rayX(nearLeft,ry), right=rayX(nearRight,ry);
    rect(right-6,ry,Math.min(4,Math.max(0,right-left-2)),1,1);
  }
  // Grounded low rubble is sparse and flattened, with irregular integer spans.
  const rubble: readonly (readonly [number,number,number])[] = [
    [.05,.36,5],[.12,.70,7],[.02,.90,9],[.90,.43,5],[.82,.79,7],[.96,.94,8],
  ];
  for (const [fraction,depthFraction,w] of rubble) {
    const x=Math.round(width*fraction), y=horizon+Math.floor((height-horizon)*depthFraction);
    rect(x+1,y,w-2,1,8); rect(x,y+1,w,1,7);
    rect(x+1,y,Math.min(3,w-2),1,9);
  }
  ctx.restore();
}
