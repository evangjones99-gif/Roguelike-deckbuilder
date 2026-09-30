# Hollowpact 0.3 development milestone

This candidate makes combat consequences visible without delaying or changing the rules. It retains schema-2 saves, the current combat balance and all historical release evidence.

## Changes under review

- Final strikes save their canonical result immediately, hold the combat view for bounded impact/death feedback, then reveal salvage or the ending. Stale commands are disabled; reload resumes the saved result. Reduced motion skips the hold.
- An additive resolved-event API reports actual damage, absorbed armor, recovery, retaliation, reinforcements and death. Presentation follows executed actions, including early hunter death and fallback targets, rather than guessing from announced intentions. Ordinary and event-producing reducers remain byte equivalent to the archived v0.2 rules across paired replay tests.
- Cairn Hounds receive six illustrated poses with consistent crop/ground metadata. Other creatures retain their illustrated fallback. Formation transitions interpolate positions and keep effect endpoints attached. These are 2.5D pose transitions, not rigged runtime creatures.
- Original scarred hunter Marek Voss appears in the title, hunter HUD and inspection dossier.
- A voluntary Field report exports confusion, meaningful or pointless choices and replay intent as local JSON with exact build/run context. It sends nothing and does not change the save. Automated QA feedback is labelled synthetic; it is not human enjoyment evidence.

## Evidence and limits

Independent gameplay, visual and technical reports determine whether this candidate earns an archive. Consult their final build hashes and rechecks. The Blender hound rig lab is preserved separately and rejected for runtime promotion because its anatomy, surfaces and motion fall below the art direction.

The rules suite passes 49 checks, including 120 complete archived-rule equivalence replays. Eight production-browser checks pass, with three affected checks repeated after the final collection-layout repair. Independent motion-enabled controls cover full victory and defeat; Linux packaged launch/combat and actual local feedback download pass. Windows packages match the same runtime source, but native launch remains unverified.

Further investigation found an inherited save-validity defect through 119 legal campaign actions on Initiate seed 1989: repeated Silence against an Ironjaw guard appends redundant intent text beyond the validator's length bound. The v0.2 and v0.3 reducers produce the same state, so this is not introduced by the presentation change. This development checkpoint preserves the exact replay and known defect; it must not be promoted commercially. The first next-cycle repair makes the status label idempotent and verifies that every saved state in that replay remains readable.

The removal-cost investigation found that cheaper removal can improve some solo-policy outcomes while harming individual seeds and confounding world generation through deck-dependent RNG consumption. No speculative economy patch ships in this milestone. Next work isolates world generation and previews actual target consequences before further balance decisions.

This remains a development build. AAA craft, human fun, native Windows/Steam Deck support, distribution rights and Steam publication remain unverified. Archiving this version is followed immediately by the next meaningful improvement.
