# Painted depth and contact — next runtime research

The owner now favors painted 2.5D animation and depth effects. Keep the rejected articulated hound as a preserved laboratory asset; it should not replace current sprites. These recommendations come from reading current `src/art.ts`/`src/arena.ts`, viewing `public/art/hound-poses.png`, and using the independent atlas inspection and visual review. They are proposals, not implemented or reviewed runtime changes. Heavy Blender work is paused for uncontended production-browser comparison.

## Existing strengths to retain

The repaired six-pose sheet preserves the grim creature identity much better than the procedural rig. The renderer already has per-pose crops/anchors, aspect-preserving sampling, stable logical slots, depth sorting by moving ground position, directed lunges/impact traces, a shadow that follows movement, and death anchored at its contact position. Reduced motion retains a static accessible battlefield. Do not replace these with generic scaling/rotation that destroys anatomy.

Current sequence: 140ms anticipation, 180ms attack, 260ms recovery; impact at 240ms; reaction 220ms; death 900ms. These give a concrete temporal contract for painting and review.

## Contact measurements from actual assets

The independent inspection measured a 1536×1024 sheet with 512×512 cells. Current crop height is 384 source pixels, displayed at `1.1 × size`. The table compares configured full-cell anchor Y with the lowest significant-alpha pixel. This is a conservative pixel proxy, not an authored anatomical foot marker.

| Pose | Anchor Y | Significant pixel bottom | Ground implication |
| --- | ---: | ---: | --- |
| Idle | 446 | 447 | Near the ground origin |
| Anticipation | 440 | 441 | Near the ground origin despite crouched torso |
| Attack | 446 | 418 | Lowest painted pixels are ~28 source pixels above the anchor: about `0.080 × size` |
| Recovery | 400 | 401 | Near the ground origin |
| Reaction | 394 | 395 | Near the ground origin |
| Death | 397 | 398 | Collapsed body stays near the ground origin |

The attack's apparent elevation is useful pounce depth, not a reason to forcibly align every pose's alpha bottom. At a nominal size of 200px it is about 16px. Its ground shadow should communicate that elevation; current shadow radius/opacity is identical across poses. Preserve recovery/death grounding and verify all transitions with actual timed captures.

## First candidate: coherent ground shadow and landing

Add explicit per-frame contact metadata rather than inferring anatomy from alpha every render: ground-anchor location, apparent altitude, footprint width, and contact weight. Begin with hound only. Cache any expensive masks/tints when art loads or the canvas resizes. Avoid per-frame pixel reads or whole-canvas filters.

During attack, keep the shadow on the projected floor, soften/widen it slightly and reduce its opacity as the body rises. During recovery, return to the idle footprint and briefly tighten/darken contact at landing. A restrained floor dust/ash cue can reinforce landing, with reduced motion suppressing movement while preserving the outcome. Keep these effects at the actual command contact position, not the original slot or a newly compacted slot.

Separate all ground shadows/sigils into a floor pass before painting depth-sorted bodies. The current inline `paintFigure` shadow can place a later unit's shadow over an already painted neighbor. Measure the benefit in dense/staggered formations before adopting the extra pass. Selection sigils may stay as slot markers if that meaning is consistent; do not let a stationary sigil look like an airborne creature's shadow.

The current code creates its radial gradient in canvas coordinates before scaling the circular path into an ellipse. The isolated candidate instead creates the gradient in the translated/scaled local footprint space, so its falloff follows the ellipse. This may soften an otherwise clipped footprint; verify actual Canvas output before treating the change as accepted. Keep the baseline's original transform order in the fixture.

## Second candidate: depth without losing tactical clarity

- Keep foot/ground Y as the depth-sort key, including lunge offset. A tall creature's head must not decide whether its feet occlude a nearer body.
- Preserve size/readability floors in six-slot formations. Use small controlled perspective differences, not a large shrink of rear enemies. Boss scale should remain an intentional creature-size difference.
- Test a restrained cached cool tint/contrast reduction for distant figures and a faint fog layer between formations. Do not blur names, intentions, target highlights, or silhouettes into the background.
- Preserve the existing baked lighting direction. Additional warm rim effects should match the courtyard braziers and be limited to contact/summon moments; a constant bright outline makes units look like stickers.
- Keep attack traces beneath essential target information and timed to the actual 240ms impact. A muzzle/claw contact marker per pose can aim close-range effects better than always using `0.43 × size` above the foot origin.

The existing backdrop is painted. A camera/parallax effect would need coherent foreground/floor/background layers and aligned actors; moving only the background is not credible depth. Prioritize contact/occlusion first rather than inventing a camera feature from one flattened image.

## Third candidate: pose continuity

The current 70ms crossfade draws two different painted bodies for a substantial portion of a 140ms anticipation. Inspect for double heads/limbs at battle size. Keep blend duration pose-specific: a short switch or one authored in-between may read better at attack/impact, while idle/recovery can tolerate a subtle blend. This is an experiment; do not change timing solely from arithmetic.

Before adding many frames, specify stable identity, consistent facing, known ground/muzzle markers, a shared crop/scale, the same light direction, and a clear frame-count/timing contract. Generate or paint in-betweens for a specific gap: wind-up→push-off, airborne attack→contact, or landing→settle. Preserve repaired source atlases and compare at the exact same timestamps. Six independent poses are not a full articulated motion cycle.

## Comparative review fixture

Use the same frozen source, resolution, state and actions for baseline/candidate. Capture idle, 100ms wind-up, 240ms impact, 350ms recovery, 580ms settled, and death at early/mid/end times. Include hound versus armored target, retaliation killing an attacker, a lethal enemy hit, and maximum formations. Check shadow/feet separation, corpse location, double-image silhouettes, obscured targets, and reduced-motion/hidden-tab behavior.

Measure actual production Canvas draws, frame gaps, CPU/long tasks, and first-load image decode without Blender competing for resources. Verify tactical inputs and presentation timing remain correct. Request independent visual review; author approval or higher FPS alone does not establish professional animation quality or human enjoyment.

`shadow-prototype.html` and `capture_shadow_prototype.mjs` are isolated comparison sources outside runtime. They use actual atlases/crops/anchors and source-shadow transform order, then compare altitude-aware local-gradient/floor-pass rendering. Launch the dedicated static server and browser capture only after the lead releases the production FPS-comparison pause. Static fixture draw times are not runtime FPS evidence.
