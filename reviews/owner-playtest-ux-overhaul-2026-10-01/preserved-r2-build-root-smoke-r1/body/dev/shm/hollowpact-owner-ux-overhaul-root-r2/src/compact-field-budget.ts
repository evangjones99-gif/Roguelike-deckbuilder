/** SOURCE-ONLY design budget, not painted/hit geometry or runtime acceptance. */
export interface CompactBudget { canvasHeight: number; enemyBody: number; allyBody: number;
  divider: number; moveColumns: number; foldRows: number; enemyRows: number; allyRows: number }
const clamp = (value: number) => Math.max(0, Math.min(1, value));
/** Smooth design phases instead of a 960/961 media-query discontinuity. */
export function compactFieldBudget(width: number, allies: number, enemies: number,
  enemyIntentRows = 3): CompactBudget {
  const moveColumns = clamp((width - 800) / 140);
  const foldRows = clamp((width - 940) / 220);
  const sparseBody = 112 + 38 * clamp((width - 360) / 800);
  const denseBase = 64 + 8 * clamp((width - 360) / 440);
  const denseBody = denseBase + (150 - denseBase) * foldRows;
  const enemyBody = enemies <= 2 ? sparseBody : denseBody;
  const allyBody = allies <= 2 ? sparseBody : denseBody;
  const enemyRows = enemies <= 3 ? 1 : 2;
  const allyRows = allies <= 3 ? 1 : 2;
  const enemyCell = enemyIntentRows * 16 + enemyBody + 32;
  const allyCell = allyBody + 48;
  const extent = (cell: number, rows: number) => cell + (rows - 1) * (cell + 8) * (1 - foldRows);
  const needsDivider = allies >= 3;
  const divider = needsDivider ? 90 + (16 - 90) * foldRows : 16;
  const canvasHeight = Math.max(360, 16 + extent(enemyCell, enemyRows) + divider + extent(allyCell, allyRows));
  return { canvasHeight, enemyBody, allyBody, divider, moveColumns, foldRows, enemyRows, allyRows };
}
