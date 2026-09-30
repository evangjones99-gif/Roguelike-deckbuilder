import test from 'node:test';
import assert from 'node:assert/strict';
import { PadDecoder, type PadState } from './adapter.ts';
function pad(): PadState { return {index:0,connected:true,mapping:'standard',axes:[0,0,0,0],buttons:Array.from({length:17},()=>({pressed:false,value:0}))}; }
function button(p:PadState,index:number,value:number,pressed=false) { (p.buttons as {pressed:boolean;value:number}[])[index]={pressed,value}; }
function axis(p:PadState,x:number,y:number) { (p.axes as number[])[0]=x;(p.axes as number[])[1]=y; }
function armed() { const p=pad(),d=new PadDecoder();assert.deepEqual(d.decode(p,0),[]);return {p,d}; }

test('connection-held confirm requires neutral release, then a fresh edge',()=>{
  const p=pad(),d=new PadDecoder();button(p,0,1,true);assert.deepEqual(d.decode(p,0),[]);assert.deepEqual(d.decode(p,1000),[]);
  button(p,0,0);assert.deepEqual(d.decode(p,1010),[]);button(p,0,1,true);assert.deepEqual(d.decode(p,1020),[{type:'confirm'}]);
});
test('confirm does not repeat across selection focus changes or long holds',()=>{
  const {p,d}=armed();button(p,0,1,true);assert.deepEqual(d.decode(p,10),[{type:'confirm'}]);
  for(const now of [20,350,1000,9000])assert.deepEqual(d.decode(p,now),[]);
  button(p,0,0);d.decode(p,9010);button(p,0,1,true);assert.deepEqual(d.decode(p,9020),[{type:'confirm'}]);
});
test('button value hysteresis does not chatter near the press threshold',()=>{
  const {p,d}=armed();button(p,0,.61);assert.deepEqual(d.decode(p,10),[{type:'confirm'}]);
  button(p,0,.5);assert.deepEqual(d.decode(p,20),[]);button(p,0,.41);assert.deepEqual(d.decode(p,30),[]);
  button(p,0,.39);d.decode(p,40);button(p,0,.59);assert.deepEqual(d.decode(p,50),[]);button(p,0,.61);assert.deepEqual(d.decode(p,60),[{type:'confirm'}]);
});
test('axis enter/exit deadzones ignore jitter and require threshold on reversal',()=>{
  const {p,d}=armed();axis(p,.25,0);assert.deepEqual(d.decode(p,10),[]);axis(p,.54,0);assert.deepEqual(d.decode(p,20),[]);
  axis(p,.8,0);assert.deepEqual(d.decode(p,30),[{type:'move',direction:'right'}]);axis(p,.4,0);assert.deepEqual(d.decode(p,100),[]);
  axis(p,-.4,0);assert.deepEqual(d.decode(p,200),[]);axis(p,-.6,0);assert.deepEqual(d.decode(p,210),[{type:'move',direction:'left'}]);
});
test('direction alone repeats after350ms, then100ms; reentry is immediate',()=>{
  const {p,d}=armed();button(p,13,1,true);assert.deepEqual(d.decode(p,20),[{type:'move',direction:'down'}]);
  assert.deepEqual(d.decode(p,369),[]);assert.deepEqual(d.decode(p,370),[{type:'move',direction:'down'}]);assert.deepEqual(d.decode(p,469),[]);assert.deepEqual(d.decode(p,470),[{type:'move',direction:'down'}]);
  button(p,13,0);d.decode(p,480);button(p,13,1,true);assert.deepEqual(d.decode(p,490),[{type:'move',direction:'down'}]);
});
test('simultaneous activation buttons produce a single prioritized intent',()=>{
  const {p,d}=armed();button(p,0,1,true);button(p,3,1,true);button(p,1,1,true);assert.deepEqual(d.decode(p,10),[{type:'back'}]);assert.deepEqual(d.decode(p,20),[]);
});
test('presentation gate suppresses confirm and requires release after reopening',()=>{
  const {p,d}=armed();button(p,0,1,true);assert.deepEqual(d.decode(p,10,false),[]);assert.deepEqual(d.decode(p,20,true),[]);
  button(p,0,0);d.decode(p,30,true);button(p,0,1,true);assert.deepEqual(d.decode(p,40,true),[{type:'confirm'}]);
});
test('safe pause may open while gated, but is not replayed into a modal',()=>{
  const {p,d}=armed();button(p,9,1,true);assert.deepEqual(d.decode(p,10,false),[{type:'pause'}]);assert.deepEqual(d.decode(p,20,true),[]);assert.deepEqual(d.decode(p,1000,true),[]);
});
test('disconnect, hidden reset and pad-index changes neutralize held input',()=>{
  const {p,d}=armed();button(p,0,1,true);assert.deepEqual(d.decode(p,10),[{type:'confirm'}]);d.reset();assert.deepEqual(d.decode(p,20),[]);
  button(p,0,0);d.decode(p,30);button(p,0,1,true);p.index=1;assert.deepEqual(d.decode(p,40),[]);assert.deepEqual(d.decode(null,50),[]);assert.deepEqual(d.decode(p,60),[]);
});
test('unsupported mapping, invalid timing and opposing dpad directions stay inert',()=>{
  const {p,d}=armed();p.mapping='';button(p,0,1,true);assert.deepEqual(d.decode(p,10),[]);p.mapping='standard';assert.deepEqual(d.decode(p,NaN),[]);assert.deepEqual(d.decode(p,-1),[]);
  button(p,0,0);d.decode(p,20);button(p,12,1,true);button(p,13,1,true);assert.deepEqual(d.decode(p,30),[]);
});
test('nonfinite axes/buttons are ignored, and decoder never reads a device identity',()=>{
  const {p,d}=armed();Object.defineProperty(p,'id',{get(){throw Error('Device identity must never be read');}});
  axis(p,Infinity,NaN);button(p,0,Infinity);assert.deepEqual(d.decode(p,10),[]);button(p,0,1,true);assert.deepEqual(d.decode(p,20),[{type:'confirm'}]);
});
test('decoding does not mutate borrowed browser snapshots',()=>{
  const {p,d}=armed();axis(p,.8,0);const bytes=JSON.stringify(p);for(let i=1;i<=100;i++)d.decode(p,i*17);assert.equal(JSON.stringify(p),bytes);
});

test('safe pause works after neutral presentation-lock frames, without arming gameplay',()=>{
  const {p,d}=armed();assert.deepEqual(d.decode(p,10,false),[]);assert.deepEqual(d.decode(p,20,false),[]);
  button(p,9,1,true);assert.deepEqual(d.decode(p,30,false),[{type:'pause'}]);assert.deepEqual(d.decode(p,40,false),[]);
  button(p,0,1,true);assert.deepEqual(d.decode(p,50,true),[]);
});
