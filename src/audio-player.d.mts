export function mixGraph(context: BaseAudioContext, destination?: AudioNode): { master: GainNode; compressor: DynamicsCompressorNode; ceiling: WaveShaperNode };
export class CuePlayer {
 constructor(assetBase?: string);
 context: AudioContext | null; enabled: boolean; muted: boolean; volume: number; epoch: number; active: Set<unknown>;
 enable(): Promise<boolean>; cancel(): void; settings(mute:boolean,volume:number):void; dispose():Promise<void>;
 load(cue:string,variant:number):Promise<AudioBuffer>;
 play(cue:string,gain?:number,offset?:number):Promise<boolean>;
 playBatchAt(cues:{cue:string;gain:number;offset:number}[], anchor:number):Promise<boolean[]>;
}
