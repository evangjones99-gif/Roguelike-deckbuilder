# Audio presentation delay: authored source only

Only `/dev/shm/hollowpact-owner-ux-overhaul-root-r2/src/audio-host.ts` and the new `tests/audio-presentation-delay.test.ts` were edited. Starting host bytes are preserved in `audio-host-before.ts`, SHA256 `c054da07280183da53d6636ddc2419cb7fa37a39eb7f8d437cb4d0ad180bb6c1`. Resulting host SHA256 is `4e0d8ff4ed9d584ff38bb914cc7ae5b4987b2d73411659281ee84b6a4376547d`. The complete UTF-8 diff and dependency identity ledger are retained. No root main, arena/layout, hunter source, canonical reducer, player/routing source, native bridge, built output or Git was edited.

Final API:

```ts
HostAudio.transition(before, after, events, action, animated, presentationDelayMs = 0): void
contactCuePlan(before, after, events, action, animated, presentationDelayMs = 0): ContactCuePlan
interface ContactCuePlan { cues: RoutedCue[]; anchorOffsetSeconds: number }
```

The existing `contactCues` output and signature remain unchanged. `contactCuePlan` uses those same contact offsets and carries the renderer lead separately. Host scheduling passes the original cues to the existing player at `context.currentTime + plan.anchorOffsetSeconds`. This preserves the player's600ms contact-offset bound while allowing a longer accepted renderer queue lead. There is no floating offset subtraction and no guessed queue ceiling. ROOT confirmed renderer lead is finite nonnegative ceil milliseconds; expansion waits for prior holds plus320ms, unchanged geometry/reduced/hidden returns0, and root dispatch guards prevent allocation queue growth. Finite positive timing is accepted exactly for animated battle presentation. Negative/nonfinite, nonanimated and noncombat timing produce0. Omitted timing preserves existing deadlines.

Existing cancellation/epoch tickets, native inactivity/restoration barriers, hidden/mute checks, decode failure handling, cue priorities/voice limits,60ms late-cold refusal and local activation ownership stay in HostAudio/CuePlayer. The timing argument only affects optional presentation; the existing canonical read-only comparison still guards observer mutation. ROOT owns reading the renderer's delay immediately after playAction and passing it as the sixth argument.

Eight new checks are prepared: omitted/zero legacy and canonical-byte equivalence;320/800/1710ms unchanged relative cue offsets; invalid/reduced/noncombat immediacy; arrival bind/impact and enemy-phase wound grouping; actual CuePlayer scheduling beyond the600ms offset ceiling with an800ms anchor lead; asynchronous decode cancellation/mute/visibility/native restoration; inactive host refusal; and late-cold assets refusing stale shifted deadlines. They use actual reducer traces and player ticket/offset admission, with mocked hardware scheduling. They do not establish hearing, audiovisual perception, physical hardware or native platform acceptance.

The new Node checks bundle the actual audio host using esbuild and define Vite's local `import.meta.env.BASE_URL` as `/`; direct Node import of existing art.ts would otherwise require Vite's environment. This test transport changes no source and invents no gameplay/timing constants. Its runtime/typecheck resource window remains separately required. Earlier test source is preserved; final source is `audio-presentation-delay-R2.test.ts`, SHA256 `655ef6418818196b8d6f15125b9ae0e54cee2f1ca4443e09706556ebff9ba6fe`, with a supplement ledger recording the superseded initial source identity.

SOURCE ONLY: no Node, typecheck, test, esbuild, browser, native build or audio output execution occurred. Static inspection is not a passed test or acceptance. There were no runtime failures to hide; earlier independent technical review resource refusals remain in their separate retained packet. A separate independent reviewer must verify the timing implementation and root integration before selection. This author will not independently accept their own implementation.
