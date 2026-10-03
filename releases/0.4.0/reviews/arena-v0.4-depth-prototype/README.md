# Isolated painted-depth candidate

This is a renderer-author experiment prepared while v0.3 is frozen for independent review. Files here are **not imported by the game**. No promotion or independent quality verdict is implied. Production arena SHA`ec0b44aadc869dbf3903f3c6c3d1d0ef96f2c00caed4c75c444be790250620ea` and art SHA`c8ecd30136abb54d865fa80e27649da0049db3c65f879cbfa2a80d2269a14d1d` remain unchanged.

Candidate changes: prepare contact/pose state before painting; floor-shadow/sigil pass before depth-sorted bodies; hound attack apparent altitude metadata28/384×1.1, shadow footprint1.12 and contact opacity0.68 blended over existing70ms transition. The apparent altitude records elevation already painted into the asset; it does not add duplicate body displacement. Other poses retain grounded shadow defaults. No landing dust or blend-duration experiment has been implemented yet.

The first comparison (`first-comparison/`) was informative: baseline and candidate images were byte-identical at all attack timestamps and in full12/mutual-lethal cases, even though recorded shadow radius/alpha differed. The inherited shadow function created a radial gradient at absolute ground coordinates and then transformed a locally centered ellipse. The gradient and filled shape did not share a working local origin. The current isolated candidate translates/scales first, then creates and fills a radial gradient at local(0,0), making actual floor shadows visible. This is a measured visual difference, not proof of artistic improvement. First comparison source/results/images are preserved rather than hidden.

`comparison-harness.mjs` loads actual local Vite source/art on5173, with two canvases1280×540 sharing a controlled16.67ms RAF clock. It captures baseline and candidate at100ms anticipation,240ms contact,350ms recovery,580ms settle, plus grounded mutual lethal retaliation420ms and12-actor contact. Both use the same engine result/events; no game rules change. Controlled timing is not a real displayFPS benchmark. This experiment uses `/usr/bin/chromium --disable-gpu`; paths reflect the execution workspace. Typecheck used `tsc` with DOM/ES2022/Bundler/strict/skipLibCheck/noEmit plus included Vite declarations. `env.d.ts`/type-only engine import use absolute development-workspace paths and are not distribution assets.

Raw `comparison.json` records actual gradient calls, canonical events, source-factory distinction, wait/reduced-motion checks and errors. Candidate/baseline pixel difference bounds after local-gradient repair:

| Capture | Changed-pixel bounding box |
| --- | --- |
| Idle |240,355–1073,501|
| Anticipation100ms |225,355–1073,504|
| Contact240ms |642,355–1073,431|
| Recovery350ms |555,355–1073,446|
| Settle580ms |240,355–1073,501|
|12-actor contact |100,281–1180,515|
| Mutual death420ms |631,355–1073,433|

Both presentation busy values match in mutual death (761ms remaining at420ms); both reduced-motion waits settle to0 and remain byte-identical during500ms controlled advancement. Console errors: none. Pixel difference bounds were measured using Pillow ImageChops; no artwork was edited. Viewed candidate contact and12-actor captures: restrained floor darkening is visible beneath feet, without painting new shadow over nearer creature bodies. This author observation requires independent comparative assessment; don't turn it into an AAA claim.

Next checks before promotion: independent frozenv0.3 comparison, narrow/full-party silhouettes, virtual hunter attacks and corpsecontact, natural-frame cadence/drawcost, hidden/resize/dispose/cancel promises, and production UI integration. Reject if added shadows obscure tactical silhouettes, over-darken the floor, damage performance or interrupt bounded final-hit presentation. Consider authored landing cues and shorter pose-specific crossfades only after this narrower candidate earns acceptance.
