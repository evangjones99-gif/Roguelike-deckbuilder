import type {GameState, TransitionEvent, Action} from './engine';
export type RoutedCue = {cue:string;key:string;gain:number;priority:number;offset:number;aggregateHpLost?:number;aggregateBlocked?:number;affectedTargets?:number};
export function cuesForTransition(before:GameState,after:GameState,events:readonly TransitionEvent[],action:Action):RoutedCue[];
