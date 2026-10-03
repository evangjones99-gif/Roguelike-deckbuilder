# Arena v0.4 candidate: floor contact and shadow depth

Proposal from the renderer owner; not implemented runtime and not an accepted visual verdict. v0.3 runtime remains frozen for independent comparison. Preserve the v0.3 images and fixtures.

Observed limitation: hound attack feet are painted28 sourcepixels above the shared ground anchor, while the shadow retains its grounded footprint/opacity. Shadows are drawn immediately before each body; in dense formations a later actor's shadow can darken an already-painted nearer limb. Attack targeting is correct, but the imagery can read as cutouts rather than a creature pouncing through a courtyard.

First bounded implementation, after root opens v0.4:

1. Extend pose-frame metadata with explicit apparent altitude and floor footprint, authored per frame. Keep the existing crop/ground anchors and never infer anatomy by scanning alpha during rendering. For hound attack use28/384×1.1 apparent elevation as the initial measured reference, not extra body displacement on top of the airborne paint.
2. Resolve contact-anchored death positions before any painting, then draw all shadows/summon sigils in a floor pass followed by depth-sorted bodies. Retain source/targetUID endpoint remapping, smooth formation transitions and existing canonical-event scheduling.
3. Widen/soften/reduce an airborne shadow slightly and tighten it through grounded recovery. Use a restrained dust cue at landing, based on the authored pose transition, without changing game state or UI hold deadlines. No extra loops after reduced motion, hidden, resize or disposal settlement.
4. Compare the current70ms pose blend with30ms attack/reaction-specific blend using timed images. Keep whichever shows clearer single-head/single-limb anatomy; a quicker blend is a hypothesis, not an automatic improvement. Add authored in-between artwork only for a measured continuity gap.

Acceptance evidence: same legal state/actions at1280×540 and narrowviewport; record idle,100ms anticipation,240ms impact,350ms recovery,580ms settled, early/middle/deathend. Include surviving target, mutual lethal retaliation, weak-binding target fallback,3→4 formation and12 actors. Check shadow-foot separation, real jaw/claw contact, dead-sourcecounter, overlay targets and pointer readability. Manual/OS reduced motion must remain pixel-stable; every pending promise must resolve on cancellation/hidden/resize/dispose. Compare actual production draw cadence and draw cost without other heavy renders; reject a measured regression. Seek independent visual review against frozenv0.3.

More painted poses for the frequently encountered warlord should follow: a standing humanoid fading on death is still below the hound's grounded collapse. Generation should reuse the original warlord identity, light direction and padded3×2 layout, with explicit per-pose ground/muzzle/contact anchors measured before source integration. Avoid widening this first contact improvement into an unverified 3D replacement.
