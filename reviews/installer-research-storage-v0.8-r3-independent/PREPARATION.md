# Independent storage-flow review preparation

This directory is reviewer-owned and not a production workflow. The first run targets the frozen rejected R2 proposal and intentionally preserves its assertion failure. The unchanged candidate storage loop reached its success diagnostic in a simulated storage fixture, then the independent four-case status assertion rejected its falsely failed R5 case.

The fixture executes the candidate main, origin/artifact metadata guards, identity, tag/draft checks, exclusive local receipt writes, storage ordering, asset-set checks and failure sanitization. Original small evidence ZIPs go through the actual candidate Python verifier (CRC, exact member hashes, native status and pinned identity). Stored evidence/coverage bytes go through the actual binary response/stream/hash helpers.

The five large wrappers, raw parts, original-installer reconstruction and original-installer size/hash/read-back are explicitly mocked. Capacity is explicitly mocked as 4 GiB. All GitHub APIs and binary responses are in-process fixtures. No native installer or downloaded artifact code executes; no live API write occurs. Candidate report fields such as `fullReadBackVerified` inside a simulated result are candidate diagnostic outputs, not independent large-original read-back evidence.

The R2 raw failure is append-only. A separately frozen repair will receive a fresh output directory and successful/complete/partial/refusal tests. This preparation does not accept or activate a proposal.
