/** Canvas-relative CSS pixels shared by paint and accessible DOM controls. */
export type BattlefieldSide = 'ally' | 'enemy';
export interface BattlefieldPoint { x: number; y: number }
export interface BattlefieldRect { left: number; top: number; width: number; height: number }
export interface ArenaUnitRegion extends BattlefieldRect {
  uid: string;
  side: BattlefieldSide;
  slot: number;
  feetX: number;
  feetY: number;
  /** Presentation availability only. The reducer remains action authority. */
  disabled: boolean;
  dead: boolean;
  departing: boolean;
}
export interface ArenaUnitViewport {
  width: number;
  height: number;
  canvasAvailable: boolean;
}

const ALLY_X = [.21, .79, .33, .67, .09, .91] as const;

/** Existing formations, preserved here rather than duplicated in the UI. */
export function formationPosition(width: number, height: number, side: BattlefieldSide,
  slot: number, count: number): BattlefieldPoint {
  return side === 'ally'
    ? { x: width * ALLY_X[slot], y: height * .89 }
    : { x: width * (slot + 1) / (count + 1), y: height * .50 };
}

export function formationSize(width: number, height: number, side: BattlefieldSide,
  count: number, species: string): number {
  const boss = /dragon|crown/.test(species);
  const bulky = /colossus|golem/.test(species);
  const max = Math.min(height * (side === 'ally' ? count <= 2 ? .43 : .38 : .43),
    side === 'ally' ? width * (count <= 2 ? .23 : count <= 4 ? .14 : .12)
      : width / (count + 1) * .92);
  return Math.min(max * (boss ? 1.3 : bulky ? 1.07 : 1), height * .52);
}

/** The same source-cell rectangle and transform used by drawImage. */
export function transformedImageRect(origin: BattlefieldPoint, facing: -1 | 1,
  breath: number, width: number, height: number, anchorX: number, anchorY: number): BattlefieldRect {
  const a = -width * anchorX * facing, b = width * (1 - anchorX) * facing;
  return { left: origin.x + Math.min(a, b), top: origin.y - height * anchorY * breath,
    width: Math.abs(b - a), height: height * breath };
}

export function unionRects(a: BattlefieldRect, b: BattlefieldRect): BattlefieldRect {
  const left = Math.min(a.left, b.left), top = Math.min(a.top, b.top);
  const right = Math.max(a.left + a.width, b.left + b.width);
  const bottom = Math.max(a.top + a.height, b.top + b.height);
  return { left, top, width: right - left, height: bottom - top };
}

/** Paint outside the canvas is clipped; its controls use the same viewport. */
export function clipToViewport(rect: BattlefieldRect, width: number, height: number): BattlefieldRect {
  const left = Math.max(0, Math.min(width, rect.left));
  const top = Math.max(0, Math.min(height, rect.top));
  const right = Math.max(left, Math.min(width, rect.left + rect.width));
  const bottom = Math.max(top, Math.min(height, rect.top + rect.height));
  return { left, top, width: right - left, height: bottom - top };
}
