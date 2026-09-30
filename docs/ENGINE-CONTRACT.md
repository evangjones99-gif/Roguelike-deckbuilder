# Lanternbound — integration contract

Working title. This is an original folklore monster hunter who casts spells and commands summoned companions. Cozy lantern light; dangerous woodland contracts. Plain English, two card types. All rules renderer-free TypeScript; deterministic seeded runs.

Engine owner creates `src/engine.ts`, `src/content.ts`, tests and simulation script. UI owner creates `src/main.ts`, `src/style.css`, `index.html`. Arena owner creates `src/arena.ts`. Root owns packaging, documentation, release tooling and integration. Do not edit another owner's files without coordination.

## Exports from engine.ts

`CardDef`: `{ id:string; name:string; type:'summon'|'spell'; cost:number; text:string; color:string; species?:string; hp?:number; attack?:number; effect?:string; value?:number }`.

`Unit`: `{ uid:string; cardId:string; name:string; species:string; hp:number; maxHp:number; attack:number; block:number; acted:boolean; intent?:{ damage:number; target:string; label:string }; color:string }`.

`GameState`: `{ schema:1; seed:number; rng:number; phase:'menu'|'map'|'battle'|'reward'|'camp'|'shop'|'event'|'victory'|'defeat'; hp:number; maxHp:number; block:number; energy:number; gold:number; floor:number; turn:number; deck:string[]; draw:string[]; discard:string[]; hand:string[]; allies:Unit[]; enemies:Unit[]; rewards:string[]; relics:string[]; route:string[]; log:string[]; nextUid:number; difficulty:number; stats:{ cardsPlayed:number; damageDealt:number; turns:number; battles:number }; }`

`Action` union: `{type:'start';seed:number;difficulty?:number}` | `{type:'travel';choice:string}` | `{type:'play';index:number;target?:string}` | `{type:'attack';unit:string;target:string}` | `{type:'endTurn'}` | `{type:'reward';card:string|null}` | `{type:'camp';choice:'rest'|'train'}` | `{type:'buy';card:string}` | `{type:'remove';index:number}` | `{type:'leave'}` | `{type:'event';choice:string}`.

Exports: `CARDS:Record<string,CardDef>`, `createGame(seed:number,difficulty?:number):GameState` begins map, `applyAction(state:GameState,action:Action):GameState` pure cloned reducer (invalid actions leave state unchanged), `legalActions(state:GameState):Action[]`, `validateState(state:unknown):boolean` runtime safe save validation, `cardTarget(cardId:string):'enemy'|'ally'|'none'`.

Route: at map, `route` strings from 'battle','elite','camp','shop','event','boss'; travel with route item. Root/UI formats labels. Battles replenish energy to five and fresh hand of five; six slots per side. Living ally's source card is excluded from draw/discard. Dead summon to shared discard is provisional, documented. Manual one free command including summon turn. No ranges. Enemy target+damage visible, stable for the turn. Battlefield resets/deck restored each battle; hunter HP persists. Simultaneous hunter death loses (provisional). Win all enemies defeated, lose hunter HP<=0. Reward choose one or skip. Camp rest or enhance deck. Finite 8-12 node run with boss and distinct build effects. No grind/premium mechanics.

## Arena module

`export function createArena(canvas:HTMLCanvasElement): { render(state:GameState):void; setSelected(uid:string|null):void; resize():void; dispose():void }`.

Three.js fixed perspective woodland arena, 6 horizontal positions for each side. Stylized recognizable original creature silhouettes built from geometry; warm lights, stone table, portals, trees, fireflies. Not spheres-only demo. Units animate idle and short appearance/hit motion using observed state diffs. All essential game information and target interactions in accessible HTML overlays/roster owned by UI. Canvas purely visual; gracefully handle missing WebGL. Reduced motion via matchMedia. Stop animation when document hidden. No external network assets. Arena imports only types from engine. Do not mutate state. Own arena.ts only.

## UI

Build polished complete run UI: title/tutorial, fresh/resume, seed, map paths, battle cards and six-slot companion/enemy rosters, clearly readable intent including target, energy, health, block, draw/discard/deck viewer, manual attack/target mode and cancel; log. Reward, camp, shop, event, win/lose recap. Save after accepted actions to localStorage with validateState; corrupt saves ignored with visible notice. Settings audio mute, volume, motion; keyboard focus/cancel/end turn, fullscreen. Confirm abandon of active run. Synthesized audio after gesture, simple impact/summon feedback; do not tie reducer timing to animation. Show v0.1.0 prototype honestly. root can update version later. Use CSS polished warm parchment/teal/gold on deep forest. No external fonts/assets.
