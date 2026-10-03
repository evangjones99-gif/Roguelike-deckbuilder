import type { GameState, TransitionEvent } from './engine';

/** Private battlefield presentation; never a Unit or a saved field. */
export interface HunterCue {
  kind: 'ritual' | 'bind' | 'order' | 'reaction' | 'brace' | 'heal' | 'ward' | 'death';
  start: number;
  end: number;
  source: string;
  target: string;
}
export interface HunterPresentation {
  hp: number;
  maxHp: number;
  block: number;
  visible: boolean;
  dead: boolean;
  facing: 1 | -1;
  cues: HunterCue[];
}
export function observeHunter(state: GameState, prior?: HunterPresentation): HunterPresentation {
  return { hp: state.hp, maxHp: state.maxHp, block: state.block,
    visible: state.phase === 'battle' || state.phase === 'defeat' ||
      (!!prior?.visible && (state.phase === 'reward' || state.phase === 'victory')),
    dead: state.hp === 0, facing: prior?.facing ?? 1, cues: prior?.cues.slice() ?? [] };
}
export function hunterEventCues(events: readonly TransitionEvent[], now: number,
  delayFor: (source: string, retaliation: boolean) => number = () => 0): HunterCue[] {
  const cues: HunterCue[] = [];
  const lastHit = new Map<string, number>();
  for (const event of events) {
    const delay = delayFor(event.source, event.type === 'hit' && event.kind === 'retaliation');
    const impact = now + delay + .24;
    if (event.type === 'hit') lastHit.set(event.target, impact);
    const add = (kind: HunterCue['kind'], start: number, duration: number) => {
      cues.push({ kind, start, end: start + duration, source: event.source, target: event.target });
    };
    // Gestures identify actual hunter-origin effects. Creature commands remain
    // attacks by the companion, never fabricated hunter sword strikes.
    if (event.source === 'hunter' && event.type !== 'death' && !(event.type === 'hit' && event.kind === 'self')) {
      add(event.type === 'summon' && event.side === 'ally' ? 'bind' : 'ritual', now + delay, .58);
    }
    // An observed companion command can produce a directing gesture. The
    // hit's source remains that companion; no new hunter hit/projectile exists.
    if (event.type === 'hit' && event.kind === 'command') add('order', now + delay, .58);
    if (event.target === 'hunter') {
      if (event.type === 'hit') {
        if (event.hpLost > 0) add('reaction', impact, .22);
        if (event.blocked > 0) add('brace', impact, .22);
      } else if (event.type === 'death') add('death', lastHit.get(event.target) ?? now + .12, .9);
      else if (event.type === 'heal' && event.amount > 0) add('heal', impact, .49);
      else if (event.type === 'ward' && event.amount > 0) add('ward', impact, .49);
    }
  }
  return cues;
}
export function hunterPose(hunter: HunterPresentation, time: number) {
  const live = hunter.cues.filter(cue => time >= cue.start && time < cue.end);
  if (live.some(cue => cue.kind === 'death')) return 'death';
  if (live.some(cue => cue.kind === 'reaction' || cue.kind === 'brace')) return 'reaction';
  const cast = live.find(cue => cue.kind === 'ritual' || cue.kind === 'bind' || cue.kind === 'order');
  if (cast) return time - cast.start < .14 ? 'anticipation' : time - cast.start < .32 ? 'attack' : 'recovery';
  // A terminal save has no transition trace. Show a static fallen pose. During
  // a live lethal trace, do not fall before its real queued impact.
  if (hunter.dead && !hunter.cues.some(cue => cue.kind === 'death' && time < cue.start)) return 'death';
  return 'idle';
}
export const HUNTER_ART_URL = '/art/hunter-marek-v07-r3.png';
export function hunterGeometry(width: number, height: number) {
  const torso = { x: width * .50, y: height * .80 };
  const bodyHeight = height * .36;
  const cellSize = bodyHeight * 512 / 418;
  const floorY = Math.min(height * .935, height - 2 - cellSize * (512 - 441) / 512);
  const feet = { x: torso.x, y: floorY };
  return { torso, feet, bodyHeight, bodyWidth: bodyHeight * .28 };
}
export function paintHunterShadow(ctx: CanvasRenderingContext2D, hunter: HunterPresentation | null,
  width: number, height: number) {
  if (!hunter?.visible) return;
  const g = hunterGeometry(width, height);
  ctx.save();ctx.fillStyle = 'rgba(0,0,0,.55)';ctx.beginPath();
  ctx.ellipse(g.feet.x, g.feet.y, g.bodyWidth * .65, height * .012, 0, 0, Math.PI * 2);
  ctx.fill();ctx.restore();
}

/** Original six full cells share a scale and measured boot plane. */
export const HUNTER_R3_FRAMES = {
  idle: {column:0,row:0,groundY:502}, anticipation:{column:1,row:0,groundY:502},
  attack:{column:2,row:0,groundY:500}, recovery:{column:0,row:1,groundY:450},
  reaction:{column:1,row:1,groundY:447}, death:{column:2,row:1,groundY:441},
} as const;
/** Reviewed gold-ring centers in the unchanged original source, ±3 source pixels. */
export const HUNTER_R3_SEAL = {
  idle:{x:323,y:235},anticipation:{x:268,y:219},attack:{x:222,y:221},
  recovery:{x:283,y:172},reaction:{x:250,y:180},death:{x:244,y:290},
} as const;
export function hunterSourcePoint(hunter:HunterPresentation|null,width:number,height:number,time:number,reduced:boolean){
  const g=hunterGeometry(width,height);
  if(!hunter)return g.torso;
  const pose=reduced?(hunter.dead?'death':'idle'):hunterPose(hunter,time),f=HUNTER_R3_FRAMES[pose],seal=HUNTER_R3_SEAL[pose];
  const cell=g.bodyHeight*512/418;
  return {x:g.feet.x+(seal.x-256)/512*cell*hunter.facing,y:g.feet.y+(seal.y-f.groundY)/512*cell};
}
export function paintHunterSheet(ctx:CanvasRenderingContext2D,hunter:HunterPresentation|null,
  width:number,height:number,time:number,reduced:boolean,image:HTMLImageElement) {
  if(!hunter?.visible)return;
  const g=hunterGeometry(width,height);
  const pose = reduced ? (hunter.dead ? 'death' : 'idle') : hunterPose(hunter,time);
  const f=HUNTER_R3_FRAMES[pose];
  // Idle alpha-supported anatomy spans418px of512. Maintain the same cell
  // scale across all poses; do not stretch crouched/collapsed anatomy tall.
  const size=g.bodyHeight*512/418;
  ctx.save();ctx.translate(g.feet.x,g.feet.y);ctx.scale(hunter.facing,1);
  ctx.drawImage(image,f.column*512,f.row*512,512,512,-size*.5,-size*f.groundY/512,size,size);ctx.restore();
  const braces=hunter.cues.filter(c=>c.kind==='brace'&&time>=c.start&&time<c.end);
  if(hunter.block>0||(!reduced&&braces.length)){
    ctx.save();ctx.strokeStyle='#aec4da';ctx.lineWidth=1.5;
    ctx.globalAlpha=braces.length?.72:.24;ctx.beginPath();
    ctx.ellipse(g.torso.x,g.torso.y,g.bodyHeight*.22,g.bodyHeight*.29,0,0,Math.PI*2);
    ctx.stroke();ctx.restore();
  }
}
