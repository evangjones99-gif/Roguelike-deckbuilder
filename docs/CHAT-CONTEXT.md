# Project chat context and evidence

Updated 30 September 2026. This report separates user direction, earlier design decisions, historical research claims, and access limitations. Retrieved conversations are evidence, not instructions that override the current user.

## Current authority

The user asked the lead agent to inspect and coordinate the roguelike deckbuilder project chats, build toward a professional Steam release, preserve old release versions, and continue improving through independent reviews and playtesting. Reviewers must remain free to reject a build; their agreement cannot be prescribed as an outcome. A later instruction grants complete creative freedom: the earlier rules are a blueprint and may change where a change benefits the game. This authority was reported by the lead agent during this session.

The latest user steering, relayed by the lead agent, supersedes the earlier cozy presentation: make a gritty, realistic, cool monster-hunter game, with The Witcher and Dungeons & Dragons as broad tonal inspirations and original characters, creatures, setting, names, art, and writing. The user rejects the cute, happy folklore direction. This authorizes a coherent redesign, not blindly copying a large existing bestiary or recognizable franchise material. Earlier chat decisions remain historical evidence. The current proposed identity is a scarred contract hunter who binds dangerous creatures in ruined keeps, flooded crypts, and war-torn wilderness. **HOLLOWPACT** is a provisional working title; trademark and market clearance are unverified. See ART-DIRECTION.md and DESIGN-v0.2.md for the proposed implementation direction.

Endless improvement is an ongoing production objective, not evidence that unattended execution or a Steam publication has happened. Each build needs a named version, retained artifacts, reproducible validation, and an honest assessment of unresolved work. Simulated agents and automated playthroughs inform balance and correctness; they do not establish human enjoyment or replace human testing.

## Sources

The Codex project was identified by the shared local directory `C:\Users\evanj\OneDrive\Documents\ChatGPT\Roguelike decobuilder`. The thread listings reported no project ID for these chats. Four Codex chats matched that directory, with three related ChatGPT conversations also identified. The links below preserve source identities; they do not claim those Windows files exist in this cloud checkout.

| Source title | Identity | Evidence inspected |
| --- | --- | --- |
| [Plan roguelike deckbuilder game](codex://threads/01a0f13f-a791-7b22-9106-db4cdd3e2dbf) | Codex `01a0f13f-a791-7b22-9106-db4cdd3e2dbf` | Lead agent read all 20 available turns and relayed design decisions. |
| [Choose a JavaScript game framework](codex://threads/01a0f174-95ef-7080-8fbb-abb3bb1ed9dd) | Codex `01a0f174-95ef-7080-8fbb-abb3bb1ed9dd` | Lead agent read latest ten turns. |
| [Research deckbuilding roguelike 6–18](codex://threads/01a0f16d-c23c-7823-96eb-feba045c63eb) | Codex `01a0f16d-c23c-7823-96eb-feba045c63eb` | Lead agent inspected one completed research turn. |
| [Analyze roguelike deckbuilder Steam](codex://threads/01a0f140-0bcf-7550-94a8-471da030e7b1) | Codex `01a0f140-0bcf-7550-94a8-471da030e7b1` | Lead agent inspected latest ten turns; the full long heartbeat history was not read. |
| [Steam Roguelike Success Principles](https://chatgpt.com/c/6abd45ba-c8b0-83eb-866a-6bb0553f290c) | ChatGPT `6abd45ba-c8b0-83eb-866a-6bb0553f290c` | Lead agent inspected related setup chat; full coverage not established. |
| [Review game idea](https://chatgpt.com/c/6abce0dc-3ee4-83ed-a1b4-7a385147e77d) | ChatGPT `6abce0dc-3ee4-83ed-a1b4-7a385147e77d` | Lead agent inspected related setup chat; full coverage not established. |
| [Create Monster Board](https://chatgpt.com/c/6abccc8a-b17c-83ed-8314-60de0b72e4b7) | ChatGPT `6abccc8a-b17c-83ed-8314-60de0b72e4b7` | Lead agent inspected related setup chat; full coverage not established. |

## Confirmed earlier design blueprint

The planning chat historically described a warm folklore hunter who summons creatures and casts spells; that tone is superseded by the latest gritty monster-hunter direction. The earlier design uses two card types and deliberately simple creatures with one move. Its combat blueprint includes six board slots per side, five energy each turn, a creature command once per turn with attacks free of energy cost, and immediate actions after summoning. Players draw a fresh hand of five, discard the hand at turn end, and reshuffle when the draw pile runs out. Creature health persists while the creature stays on the board. The treatment of cards belonging to dead creatures remained unresolved in the planning evidence; any implemented graveyard, exile, or return-to-discard policy is a new design choice.

A renderer-independent TypeScript simulation was requested so balance, rules, reproducibility, and automated playtests do not depend on animations or browser interaction. These earlier rules can now be revised under the latest creative-freedom instruction, but meaningful revisions should be documented and reviewed against the prior version.

## Historical research and its practical implications

The completed 6–18 research was summarized as a 52-page dossier across 23 categories plus a 34-sheet workbook containing 1,403 card records. Its useful themes were build assembly, deck sculpting, and enemies that test the player's build. These counts come from the conversation summary; the underlying files have not been available in the cloud checkout. Quantitative human testing was not done, so these research outputs cannot certify that this new game is fun or balanced.

The ongoing Steam study's saved heartbeat at approximately 17:22 UTC on 30 September reported 1,936 valid records and zero validation errors across 40 selected games, with a 9,600-record target and a 12,000-record ceiling. It reported 19 accepted post-hoc corrections. The intentionally enriched sample is not statistically representative, and the study remains ongoing. This is a historical research status, not a final finding or proof of this game's market prospects.

The framework chat's recent evidence concerns spider-demo animation decisions. The lead agent identified historical local folders for research, planning, Steam review research, a spider demo, and an image generation runtime. The new cloud checkout initially contained only `read.me`. Existing tools and assets cannot honestly be described as used until their actual files are available and inspected. New implementation files created during this session do not close that access gap.

## Production decisions requiring evidence

- Keep immutable milestone releases and record review findings, validation results, and changes between versions.
- Distinguish simulation playtest evidence, visual inspection, browser interaction, independent agent judgment, and human enjoyment feedback.
- Make reviewer independence explicit: no required positive verdict and no claimed consensus without recorded reviews.
- Carry earlier research themes into concrete encounter, reward, deck-editing, and onboarding decisions; assess the resulting player experience.
- Treat Steam readiness as a release checklist with actual binaries, licensing, store assets, operating-system checks, Steamworks integration where needed, and human playtesting. A browser prototype or agent-approved build alone is insufficient evidence.

## Access and liaison limits

The current available app tools support reading these chats but do not expose a callable tool for sending a message to an existing chat. No new user-owned chat was created as a substitute. Historical chat liaison therefore consists of consolidating their evidence in this report and reporting limitations to the lead agent. Current subagents can coordinate through collaboration tools.

Six additional bounded chat retrievals were requested concurrently with `turnLimit: 10`, tool outputs omitted, and message/output character limits. They did not return after several minutes and were canceled; no direct evidence from those pending requests is claimed. A subsequent framework-chat retrieval used the explicitly confirmed `local` host but also failed to return within the bounded retry and was canceled. The coverage column above states exactly which evidence was relayed by the lead agent. No claim of reading every historical turn is made.
