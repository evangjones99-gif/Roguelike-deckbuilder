/** Presentation geometry only. Neither pointer nor legal action moves. */
export interface GhostProtectedRect {
  readonly key: string;
  readonly left: number; readonly top: number;
  readonly width: number; readonly height: number;
}
export interface GhostObstacle extends GhostProtectedRect {
  readonly others?: readonly GhostProtectedRect[];
}
export type GhostSide = 'left' | 'right' | 'above' | 'below';
type Rect = { left: number; top: number; width: number; height: number };
type Placement = { x: number; y: number; labelX: number; labelY: number; side?: GhostSide };

export function placeGhostBesideTarget(input: {
  x: number; y: number; labelX: number; labelY: number;
  width: number; height: number; labelWidth: number; labelHeight: number;
  screenWidth: number; screenHeight: number;
  obstacle: GhostObstacle; others?: readonly GhostProtectedRect[]; preferredSide?: GhostSide;
}): Placement | null {
  const { obstacle, width, height, labelWidth, labelHeight, screenWidth, screenHeight } = input;
  const validRectangle = (rectangle: GhostProtectedRect) => rectangle && typeof rectangle.key === 'string'
    && rectangle.key.length > 0 && [rectangle.left, rectangle.top, rectangle.width, rectangle.height].every(Number.isFinite)
    && rectangle.width > 0 && rectangle.height > 0;
  if (![input.x, input.y, input.labelX, input.labelY, width, height, labelWidth, labelHeight,
    screenWidth, screenHeight].every(Number.isFinite)
    || width <= 0 || height <= 0 || labelWidth < 0 || labelHeight < 0 || screenWidth <= 0 || screenHeight <= 0
    || !validRectangle(obstacle) || (input.others !== undefined && !Array.isArray(input.others))) return null;
  const others = input.others ?? [];
  if (!others.every(validRectangle)) return null;
  const clear = { left: obstacle.left - 12, top: obstacle.top - 12,
    width: obstacle.width + 24, height: obstacle.height + 24 };
  const visible = (wanted: number, extent: number, space: number) => {
    const margin = Math.min(8, Math.max(0, (space - extent) / 2));
    return Math.max(margin, Math.min(Math.max(margin, space - extent - margin), wanted));
  };
  const intersection = (a: Rect, b: Rect): Rect => {
    const left = Math.max(a.left, b.left), top = Math.max(a.top, b.top);
    return { left, top, width: Math.max(0, Math.min(a.left + a.width, b.left + b.width) - left),
      height: Math.max(0, Math.min(a.top + a.height, b.top + b.height) - top) };
  };
  const area = (rectangle: Rect) => rectangle.width * rectangle.height;
  // Union within each protected rectangle prevents double counting ghost/label.
  const overlap = (p: Placement, rectangle: Rect) => {
    const card = intersection({ left: p.x, top: p.y, width, height }, rectangle);
    const label = intersection({ left: p.labelX, top: p.labelY, width: labelWidth, height: labelHeight }, rectangle);
    return area(card) + area(label) - area(intersection(card, label));
  };
  const baseline: Placement = { x: input.x, y: input.y, labelX: input.labelX, labelY: input.labelY };
  const baselineTarget = overlap(baseline, clear);
  const baselineOthers = others.map(rectangle => overlap(baseline, rectangle));
  const position = (x: number, y: number, side: GhostSide): Placement => {
    x = visible(x, width, screenWidth); y = visible(y, height, screenHeight);
    const labelX = Math.max(8, Math.min(screenWidth - labelWidth - 8, x + (width - labelWidth) / 2));
    const below = y + height + 8;
    const labelY = Math.max(8, Math.min(screenHeight - labelHeight - 8,
      below + labelHeight <= screenHeight - 8 ? below : y - labelHeight - 8));
    return { x, y, labelX, labelY, side };
  };
  const extra = Math.max(0, (labelWidth - width) / 2);
  const candidates = [
    position(clear.left - width - extra, input.y, 'left'),
    position(clear.left + clear.width + extra, input.y, 'right'),
    position(input.x, clear.top - height - labelHeight - 8, 'above'),
    position(input.x, clear.top + clear.height + labelHeight + 8, 'below'),
  ].filter(p => {
    const target = overlap(p, clear);
    if (target > baselineTarget || others.some((rectangle, index) => overlap(p, rectangle) > baselineOthers[index])) return false;
    // A clear primary target can still permit a strict improvement elsewhere.
    return baselineTarget > 0 ? target < baselineTarget
      : others.some((rectangle, index) => overlap(p, rectangle) < baselineOthers[index]);
  });
  const preferred = candidates.find(p => p.side === input.preferredSide && overlap(p, clear) === 0
    && others.every(rectangle => overlap(p, rectangle) === 0));
  if (preferred) return preferred;
  const distance = (p: Placement) => (p.x - input.x) ** 2 + (p.y - input.y) ** 2;
  return candidates.reduce((best, p) => overlap(p, clear) < overlap(best, clear)
    || (overlap(p, clear) === overlap(best, clear) && distance(p) < distance(best)) ? p : best,
  candidates[0] ?? baseline);
}
