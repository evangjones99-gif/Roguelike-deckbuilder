# Canonical encounter environment R2 — exterior integration proposal

Ready for separate independent gameplay, visual and technical review. **Unshipped; no author approval substitutes for that review.** This revision repairs R1's reload discontinuity. It derives the place from the original canonical encounter context rather than guessing from surviving enemies. No root source, engine, world RNG, catalog, save, economy, audio or hound animation timing was changed.

Runtime `0a71627717af936411ff3857d43aa95af0c7a9ec48d9b4eeeb6dec36d2aa2af0`,31 inputs. Original29-input runtime `0be4f01d416e6fc4cca3f19b6916b5b65993b9fd426a926a1ede6d8487834a35` retains27 exact inputs; only arena/art differ, and the pure `encounter-environment.ts` and original panorama are added. `SOURCE-BUILD-IDENTITY.json` records every actual dist hash and original source comparisons. The proposal began from root44b70; the identity readback root983066 has the same baseline29 runtime hashes. Mutable runtime text/config/package/build inputs are pinned as copies. Original immutable art/icon bytes are referenced read-only; dependencies are the already installed project tools. The candidate and its derived build live temporarily at `/tmp/hollowpact-encounter-art-v08-r2` (also `candidate`), while all unique source/evidence here is durable.

## Direction and compatibility

Generation2 uses `worldFormation({seed,node:floor,kind:route[0]})` for normal/elite encounters. Bosses use the existing `bossForSeed` directly because `worldFormation` intentionally rejects boss context. A necromancer anywhere in that original formation, or an entirely wraith/thrall original formation, selects the ossuary crypt. Other encounters retain the original abbey courtyard. This lookup is pure and does not consume any RNG stream or inspect the current enemy roster. Reward and defeat retain the encounter route; victory has released the route and reconstructs the seed-defined boss explicitly. Unrelated noncombat phases retain the preceding place in an existing arena.

Legacy schema2 normal/elite formations used shared RNG and cannot be reliably reconstructed from current saves. They conservatively keep the abbey even when a necromancer survives. Their seed-defined cantor boss still selects crypt. This explicit compatibility tradeoff preserves stable backgrounds through casualties/reinforcements/reloads and introduces no saved field, new storage key or migration. New-generation early normal encounters remain the abbey because their actual original pool contains a warlord.

The selected background is uniformly covered using the original renderer placement/shading; no source pixels are edited. The exact original RGB2069×760 panorama SHA is `ff9818614003e9432ee1868c2f60b336d0b5dfe63f5c01e380832f1e880c4b00`. Original generation/request/provenance remain in `/workspace/scratch/crypt-panorama-author-v08-r2`. It loads on demand at the relative BASE_URL path `art/ossuary-crypt-v08-r2.png`. Unused background errors do not create irrelevant notices, and an earlier crypt image completing after a new courtyard begins cannot paint over it. Existing fallback rendering/controls remain available. The aria label identifies the selected environment.

## Actual author evidence

`actual-host-r6.json`:16 actual built-web scenarios,12 accepted ordinary UI actions and12 real reloads. Original formations are created by the actual engine from valid unearned map checkpoints; hand reordering/lethal health/explicit lethal intent adjustments are recorded in their states. No earned campaign or human enjoyment is implied. Natural timers, ordinary pointer controls and read-only private Canvas instrumentation are used; no runtime debug/query bridge is added. Every accepted action's serialized save matches the unchanged `applyActionWithEvents` oracle exactly. Covered cases include:

- Seed2/node4 elite: kill the acolyte, leaving a dragon; real reload retains crypt.
- Original early courtyard: kill the warlord, leaving a thrall; reload retains abbey.
- Actual necromancer raises a thrall; original place and save survive reload.
- Legal final reward, real cantor-boss victory and hunter defeat, held final impact and settled phases, then reload.
- Legal reward → shop → leave → next battle reselection.
- Legacy normal/elite conservatism, legacy cantor/warlord boss identities and reload.
- Missing and delayed selected crypt, canonical ward controls, wide/mobile full HTML captures.

`asset-lifecycle-supplement.json`:4 further actual built-web scenarios and12 canonical UI actions. Unused crypt/courtyard failures produce no irrelevant selected-art notice. A missing or delayed prior crypt is followed through legal transitions into a courtyard; its error/completion neither changes that place nor the save.

`pure-world-probe.json`:432 actual engine-sampled contexts across24 seeds, both generations and9 supported node/kind pairs;109 select crypt. All frozen inputs serialize identically after the lookup; contrary/empty current rosters cannot affect the location. Terminal objects in that probe are presentation-only context observations, not asserted as valid saves. See `PROBE-COUNT-ERRATUM.md`: the original scope string's480 count is incorrect; actual rows/console contain432 and are preserved unchanged.

The strict pinned TypeScript/Vite build passes. The existing87 canonical rules checks remain separate from the new presentation probe. All32 frozen R1 files and27 frozen original R2 art-study files passed byte-hash readback after this work.

## Preserved failures and remaining gates

The original selector R1/c501, all32 frozen records and its root rejection remain untouched. Initial R2 seed search requested a formation absent from the later normal pool; the subsequent browser harness unconditionally reseeded the opening save on reload. That produced misleading casualty reload failures after actions had already committed correctly. The preserved pointer investigation succeeds and the corrected initialization guard fixes the harness; no UI/input code was changed. Another run correctly rejected an illegal immediate battle after node4 salvage; the final run follows the actual shop/leave route. All failed scripts/logs/data remain here. Do not present those as discarded gameplay regressions or as passes.

Actual production promotion still needs its own resulting identity, separate independent gameplay/visual/technical review and updated art inventory/credits/provenance. This candidate keeps original THIRD-PARTY/runtime inventory bytes; root must add the new image's declaration when integrating it and then test that changed identity. Native file/packaged delivery, physical controllers/Steam Deck, human listening/playtests, performance, distribution rights/AI disclosure, store/Steamworks and AAA craft are unverified here. Current sparse painted standees and mobile roster intrusion remain craft debt. The panorama's author and separate art-only acceptance do not prove this combined game is exceptional or fun.
