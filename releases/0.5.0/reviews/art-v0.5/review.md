# Independent tool-art study for v0.5

**Decision: accept this sheet as a promising, limited art-family candidate for subsequent integration review. Reject blanket mapping to every tool and any AAA/commercial-quality claim. No runtime asset or rule was changed by this study.**

The wet chained hook, scratched iron plate, red-thread sewing kit and fang tied to three bone effigies have substantially more material identity than the current generic lightning/heart/shield symbols. They fit Marek's practical, grim contract-hunter equipment and the ruined abbey. The compositions retain distinct cool iron versus warm thread/ivory palettes. This is reviewer judgment from actual viewed images, not a player preference result or proof of fun.

## Evidence and limits

I viewed the original 1774×887 RGB sheet, the actual unchanged v0.4 Blood Sutures/Pack Edict cards captured in a separate browser context, and the rendered large, paired, narrow, crop-comparison and recommended mockups. `current-*.png` are actual game UI; `prototype.html` is an explicitly labeled independent replica of card geometry/typography. It uses the original sheet as a CSS background; no Pillow, pixel editing, art regeneration or runtime changes. Source hash: `0f5ee14a3f868b9480aaad480d949337cf38ad8e2f258e58857e7cd18f93d0f4`.

Chromium `/usr/bin/chromium` / Playwright captured 1440×900, 1280×900 and 390×900 layouts. All 36 mockup cards kept their cost badges and 12px rules within card bounds; no document horizontal overflow or page/request failures. This does **not** establish integrated mobile-hand geometry, game frame rate, keyboard behavior, or a runtime fallback. The mockup samples 180×48 and 155×41.33 banners to preserve 3.75:1; current actual hand can differ slightly with viewport. The production reference is v0.4, not an unreleased v0.5 game. Exact served reference provenance and core hashes are retained in `current-reference.json` / `capture.json`.

## Mapping and crop recommendation

| Art family | Supported mapping | Reject or defer |
|---|---|---|
| Chained hook, upper left | Scour; Chain Harpoon as clearly shared family | Witchfire, Grave Tithe and other distinct magic mechanics |
| Black iron plate, upper right | Iron Ward; Black Aegis as shared defense family | Claiming the same plate makes the two effects visually unique |
| Needle, red thread, bandage, lower left | Blood Sutures | Blood Price: sacrifice for energy differs from healing; Bleak Draught deserves a vessel |
| Fang and three bound effigies, lower right | Pack Edict | Kill Command singles out one creature; a three-creature composition implies a different scope |

Large 2:1 banners can use each whole quadrant with a two-source-pixel inset to exclude the baked divider: `[x,y,width,height]` = `[2,2,883,439.5]`, `[889,2,883,439.5]`, `[2,445.5,883,439.5]`, `[889,445.5,883,439.5]`. Center cover anchor `(0.5,0.5)` works for all four. The hook and needle remain small at 205px; don't mistake full-resolution texture detail for immediate card recognition.

For shallow hand banners, I prefer the **recommended.png** result. Use a distinct hand crop rather than a single background-position for both sizes:

| Family | Source rectangle `[x,y,w,h]` | Cover anchor `(x,y)` |
|---|---|---|
| Hook | `[2,170,610,240]` | `(0.5,1.0)` |
| Plate | `[957,45,575,355]` | `(0.5,0.48)` |
| Sewing | `[130,538.5,620,270]` | `(0.5,0.70)` |
| Pack | `[889,445.5,883,439.5]` | `(0.5,0.81)` |

Anchor fractions refer to **available crop travel**, not a point on the source. For box `W,H`, rectangle `x,y,w,h` and anchor `ax,ay`, use `s=max(W/w,H/h)`, original sheet background-size `(1774*s,887*s)` and background-position `(-x*s-(w*s-W)*ax, -y*s-(h*s-H)*ay)`. Exact sampled windows are saved in `capture.json`; the prototype preserves the less effective full-cell and tighter alternatives for comparison.

## Remaining craft concerns and integration gates

The tighter hook/plate/sewing windows use more of the shallow banner for their identifying object. Pack works better wide and low: the three effigies survive, whereas high crops become mostly fang/glove. Cost badges remain opaque and legible, although their upper-left placement occludes part of the left effigy at very small size. Don't shift cost placement solely to rescue an illustration without testing all cards.

Pack's small ivory figures can look like tabletop miniatures; that softens threat. They must read as binding ritual objects, never as replacement enemy designs. Shared ruins and repeated gloves add coherence but also repetition. Four paintings are four art families, not a complete uniquely illustrated tool deck. Plate still has the weakest immediate object silhouette in the shallow crop; a future purpose-composed banner would outperform increasingly aggressive cropping.

Keep rules on opaque parchment and preserve the dark opaque cost badge. The parchment is readable, but the beige bulk, large empty lower area on short rules, tiny TOOL labels and generic category symbols remain below premium card craft. Additional art alone does not solve these. Unavailable-state dimming already reduces material contrast; test actual selected, unavailable, focused and upgraded cards in the integrated build. Keep decorative illustration hidden from assistive text, retain explicit accessible card name/cost/rules, and retain a meaningful family symbol if an image fails. Require exact full-deck text/stat containment across the previous five widths, actual loaded asset paths, no seam bleed at mobile geometry, and an unchanged rule/save/RNG result before promotion.

## Reproduction

Serve the project root read-only on a separate local port: `python -m http.server 5185 --bind 127.0.0.1`. Run `node reviews/art-v0.5/capture.mjs`. The initial `file://` attempt was blocked by Chromium administrator policy; the successful evidence uses HTTP. `current-card-reference.mjs` uses the preserved validated full-deck fixture in an isolated context against port 4173, explicitly synthetic rather than a naturally reached run. No frozen historical review file was touched.

Report and study files frozen for the parent archive. Next action belongs to the parent: limited integration followed by a fresh independent production review. This is an art-study checkpoint, not a game release endorsement.
