import type { Unit } from './engine';
import { compactFieldBudget } from './compact-field-budget';
/** Canvas-relative CSS pixels shared by paint and accessible DOM controls. */
export type BattlefieldSide = 'ally' | 'enemy';
export interface BattlefieldPoint { x: number; y: number }
export interface BattlefieldRect { left: number; top: number; width: number; height: number }
export interface ArenaLayoutConfig { allies: number; enemies: number; intentRows: number; statsRows: number; identityRows?: number }
export interface ArenaReadoutMetrics { intentRows?: number; statsRows?: number; identityRows?: number }
export interface BattlefieldCell extends BattlefieldRect {
  bodyRect: BattlefieldRect;
  intentRect: BattlefieldRect;
  inspectRect: BattlefieldRect;
  identityRect: BattlefieldRect;
  statsRect: BattlefieldRect;
  statusRect: BattlefieldRect;
}
export interface BattlefieldHunterGeometry {
  feet: BattlefieldPoint; torso: BattlefieldPoint; bodyHeight: number; bodyWidth: number;
  /** Conservative union of all unchanged full512px cells, not an alpha contour. */
  rect: BattlefieldRect;
}
export interface BattlefieldLayout {
  requiredHeight: number;
  ally: readonly BattlefieldCell[];
  enemy: readonly BattlefieldCell[];
  hunter: BattlefieldHunterGeometry;
}
export interface ArenaUnitRegion extends BattlefieldRect {
  uid: string; side: BattlefieldSide; slot: number;
  feetX: number; feetY: number;
  /** Presentation availability only. The reducer remains action authority. */
  disabled: boolean; dead: boolean; departing: boolean;
  readoutUnit: Readonly<Unit>; canonicalIndex: number | null;
  /** Stable owned cell/readouts; the inherited rectangle is the actual moving paint quad. */
  cell: BattlefieldRect; bodyRect: BattlefieldRect; hitRect: BattlefieldRect;
  intentRect: BattlefieldRect; inspectRect: BattlefieldRect; identityRect: BattlefieldRect;
  statsRect: BattlefieldRect; statusRect: BattlefieldRect;
}
export interface ArenaUnitViewport {
  width: number; height: number; canvasAvailable: boolean;
  requiredHeight: number; layoutPending: boolean; hunterRect: BattlefieldRect;
}
const PAD = 8, GAP = 8, READOUT_MAX_WIDTH = 240;
const mix = (a: number, b: number, blend: number) => a + (b - a) * blend;
export function normalizeLayoutConfig(config: ArenaLayoutConfig): ArenaLayoutConfig {
  const count = (value: number) => Math.max(0, Math.min(6, Math.floor(value)));
  const rows = (value: number) => Number.isFinite(value) ? Math.max(1, Math.ceil(value)) : 1;
  return { allies: count(config.allies), enemies: count(config.enemies),
    intentRows: Math.max(3, rows(config.intentRows)), statsRows: rows(config.statsRows), identityRows: rows(config.identityRows ?? 1) };
}
export function sameLayoutConfig(a: ArenaLayoutConfig, b: ArenaLayoutConfig): boolean {
  return a.allies === b.allies && a.enemies === b.enemies && a.intentRows === b.intentRows && a.statsRows === b.statsRows && (a.identityRows ?? 1) === (b.identityRows ?? 1);
}
export function createBattlefieldLayout(width: number, height: number, input: ArenaLayoutConfig): BattlefieldLayout {
  const config = normalizeLayoutConfig(input);
  const budget = compactFieldBudget(width, config.allies, config.enemies, config.intentRows);
  const identityHeight = (config.identityRows ?? 1) * 16;
  const extraReadout = (config.statsRows - 1) * 16 + identityHeight - 16;
  const rowExtent = (rows: number) => 1 + (rows - 1) * (1 - budget.foldRows);
  const requiredHeight = budget.canvasHeight + extraReadout * (rowExtent(budget.enemyRows) + rowExtent(budget.allyRows));
  const canvasHeight = Math.max(height, requiredHeight);
  const inspectHeight = identityHeight + config.statsRows * 16;
  const intentHeight = config.intentRows * 16;
  const enemyCellHeight = intentHeight + budget.enemyBody + inspectHeight;
  const allyCellHeight = budget.allyBody + inspectHeight + 16;
  const extent = (cell: number, rows: number) => cell + (rows - 1) * (cell + GAP) * (1 - budget.foldRows);
  const enemyBottom = PAD + extent(enemyCellHeight, budget.enemyRows);
  const allyTop = canvasHeight - PAD - extent(allyCellHeight, budget.allyRows);
  const centerGap = mix(88, 120, budget.foldRows);
  function cells(side: BattlefieldSide): BattlefieldCell[] {
    const count = side === 'ally' ? config.allies : config.enemies;
    const bodyHeight = side === 'ally' ? budget.allyBody : budget.enemyBody;
    const cellHeight = side === 'ally' ? allyCellHeight : enemyCellHeight;
    const top = side === 'ally' ? allyTop : PAD;
    const result: BattlefieldCell[] = [];
    for (let slot = 0; slot < count; slot++) {
      let cellWidth: number, centerX: number, row = 0;
      if (count <= 2) {
        if (side === 'ally') {
          cellWidth = (width - PAD * 2 - centerGap - GAP * 2) / 2;
          centerX = slot === 0 ? PAD + cellWidth / 2 : width - PAD - cellWidth / 2;
        } else {
          cellWidth = (width - PAD * 2 - GAP * (count - 1)) / count;
          centerX = PAD + cellWidth / 2 + slot * (cellWidth + GAP);
        }
      } else {
        row = Math.floor(slot / 3);
        const columnsInRow = Math.min(3, count - row * 3), column = slot % 3;
        const narrowWidth = (width - PAD * 2 - GAP * 2) / 3;
        const narrowX = PAD + (width - PAD * 2) * (column + .5) / columnsInRow;
        // Both phases use the same final ordered columns. Rows remain separated
        // until column motion completes; folding therefore cannot cross owners.
        const leftCount = Math.ceil(count / 2), rightCount = count - leftCount;
        const bandWidth = (width - PAD * 2 - 120 - GAP * 2) / 2;
        const wideWidth = (bandWidth - GAP * (leftCount - 1)) / leftCount;
        const onLeft = slot < leftCount, groupCount = onLeft ? leftCount : rightCount;
        const groupColumn = onLeft ? slot : slot - leftCount;
        const bandLeft = onLeft ? PAD : width / 2 + 60 + GAP;
        const groupWidth = groupCount * wideWidth + (groupCount - 1) * GAP;
        const wideX = bandLeft + (bandWidth - groupWidth) / 2 + wideWidth / 2 + groupColumn * (wideWidth + GAP);
        cellWidth = mix(narrowWidth, wideWidth, budget.moveColumns);
        centerX = mix(narrowX, wideX, budget.moveColumns);
      }
      const cellTop = top + row * (cellHeight + GAP) * (1 - budget.foldRows);
      const left = centerX - cellWidth / 2;
      const bodyTop = cellTop + (side === 'enemy' ? intentHeight : 0);
      const inspectTop = bodyTop + bodyHeight;
      // Preserve the allocated body/paint/hit cell. Only attached readouts tighten.
      const readoutWidth = Math.min(READOUT_MAX_WIDTH, cellWidth);
      const readoutLeft = centerX - readoutWidth / 2;
      result.push({ left, top: cellTop, width: cellWidth, height: cellHeight,
        bodyRect: { left, top: bodyTop, width: cellWidth, height: bodyHeight },
        intentRect: { left: readoutLeft, top: cellTop, width: readoutWidth, height: side === 'enemy' ? intentHeight : 0 },
        inspectRect: { left: readoutLeft, top: inspectTop, width: readoutWidth, height: inspectHeight },
        identityRect: { left: readoutLeft, top: inspectTop, width: readoutWidth, height: identityHeight },
        statsRect: { left: readoutLeft, top: inspectTop + identityHeight, width: readoutWidth, height: config.statsRows * 16 },
        statusRect: { left: readoutLeft, top: inspectTop + inspectHeight, width: readoutWidth, height: side === 'ally' ? 16 : 0 } });
    }
    return result;
  }
  const fullCell = mix(78, 112, budget.foldRows);
  const packedTop = config.allies >= 3
    ? mix(enemyBottom + 1, allyTop + 8, budget.foldRows) : allyTop + 8;
  const feet = { x: width / 2, y: packedTop + fullCell * 502 / 512 };
  const bodyHeight = fullCell * 418 / 512;
  const hunter = { feet, torso: { x: feet.x, y: feet.y - bodyHeight * .38 },
    bodyHeight, bodyWidth: bodyHeight * .28,
    rect: { left: feet.x - fullCell / 2, top: packedTop, width: fullCell, height: fullCell * 573 / 512 } };
  return { requiredHeight, ally: cells('ally'), enemy: cells('enemy'), hunter };
}
export function interpolateRect(a: BattlefieldRect, b: BattlefieldRect, blend: number): BattlefieldRect {
  return { left: mix(a.left, b.left, blend), top: mix(a.top, b.top, blend),
    width: mix(a.width, b.width, blend), height: mix(a.height, b.height, blend) };
}
/** Horizontal readout ownership is derived after every cell transform.
 * Keep transformed vertical extents and body geometry exactly as supplied. */
function centerCellReadouts(cell: BattlefieldCell): BattlefieldCell {
  const width = Math.min(READOUT_MAX_WIDTH, cell.width);
  const left = cell.left + (cell.width - width) / 2;
  const center = (rect: BattlefieldRect): BattlefieldRect => ({ ...rect, left, width });
  return { ...cell, intentRect: center(cell.intentRect), inspectRect: center(cell.inspectRect),
    identityRect: center(cell.identityRect), statsRect: center(cell.statsRect), statusRect: center(cell.statusRect) };
}
export function interpolateCell(a: BattlefieldCell, b: BattlefieldCell, blend: number): BattlefieldCell {
  return centerCellReadouts({ ...interpolateRect(a, b, blend),
    bodyRect: interpolateRect(a.bodyRect, b.bodyRect, blend),
    intentRect: interpolateRect(a.intentRect, b.intentRect, blend),
    inspectRect: interpolateRect(a.inspectRect, b.inspectRect, blend),
    identityRect: interpolateRect(a.identityRect, b.identityRect, blend),
    statsRect: interpolateRect(a.statsRect, b.statsRect, blend),
    statusRect: interpolateRect(a.statusRect, b.statusRect, blend) });
}
export function projectCell(cell: BattlefieldCell, scaleX: number, scaleY: number): BattlefieldCell {
  const project = (r: BattlefieldRect): BattlefieldRect => ({ left: r.left * scaleX, top: r.top * scaleY,
    width: r.width * scaleX, height: r.height * scaleY });
  return centerCellReadouts({ ...project(cell), bodyRect: project(cell.bodyRect), intentRect: project(cell.intentRect),
    inspectRect: project(cell.inspectRect), identityRect: project(cell.identityRect),
    statsRect: project(cell.statsRect), statusRect: project(cell.statusRect) });
}
export function intersectRects(a: BattlefieldRect, b: BattlefieldRect): BattlefieldRect {
  const left = Math.max(a.left, b.left), top = Math.max(a.top, b.top);
  return { left, top, width: Math.max(0, Math.min(a.left + a.width, b.left + b.width) - left),
    height: Math.max(0, Math.min(a.top + a.height, b.top + b.height) - top) };
}
export function sameRect(a: BattlefieldRect, b: BattlefieldRect): boolean {
  return a.left === b.left && a.top === b.top && a.width === b.width && a.height === b.height;
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
