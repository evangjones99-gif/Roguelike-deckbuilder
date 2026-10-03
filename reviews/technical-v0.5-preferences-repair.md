# Independent v0.5 preferences repair recheck

Decision: **accept the preferences-loading repair and close that specific inherited P2 finding on this inspected interim candidate.** This does not approve the pending arena-facing repair, final combined source, native packages, Steam commercial readiness or AAA quality. The original CDF review remains byte-identical (SHA256 `178f1ea1b99b719386fa93d8112474867f5fd466e155c6a7c15941f39bc81d7a`), with the original finding and evidence intact.

Inspected main source SHA256: `7847bbac18cba3009ea993e68384e2bb1a8399eea4544424fb4823e025dd5526`. Actual production server at port4173 reported interim digest `997b4623b0ff3a9c4d317d03d7c3ff74dc60d3e375e9cf062c14b4239c09d1d1` before and after review; its provenance records the same main hash as current source. No implementation was modified by this reviewer.

Source change: preferences parsing now has its own guarded try/catch and explicit non-null object/non-array check. Invalid, missing or unreadable preferences use existing defaults. Campaign loading follows in a separate try and retains its original validation, unsupported-generation classification and narrow recovery/backup ordering. The preferences loader performs no set/remove operation: it does not replace malformed preference bytes. The repair neither changes supported save formats nor treats invalid campaigns as valid.

Personally executed `tests/browser/preferences-v0.5.spec.ts` against actual production with an isolated output directory: **4/4 passed (18.4s)**. Schema2/kind1 and schema3/kind2, each with null and malformed JSON preferences, retain their exact whitespace-preserved campaign text on Resume, accept End Turn into the exact canonical reducer state, preserve generation, reload that accepted state unchanged and retain the original invalid preferences. No uncaught page errors.

Seven additional reviewer inline production probes passed:

| Probe | Actual outcome |
|---|---|
| Valid legacy campaign, array preferences | Resume available; exact campaign/preferences bytes retained |
| Valid new campaign, primitive preferences | Resume available; exact bytes retained |
| Valid new campaign, incomplete preferences object | Resume available; exact bytes retained |
| Unknown schema4/kind3, null preferences | No Resume; truthful unsupported-version notice; exact campaign retained |
| Malformed campaign JSON, malformed preferences JSON | No Resume; campaign-read notice; exact raw campaign retained |
| Synthetic settings-only getItem SecurityError | Valid campaign still resumable and unchanged |
| Synthetic campaign setItem QuotaExceededError after accepted End Turn | Storage failure notice; original campaign/preferences retained; no uncaught errors |

Storage exceptions are deliberately injected diagnostics, not proof of a native platform permission/quota condition. The quota probe confirms error handling/raw retention; the four paired cases establish actual canonical accepted-state/reload behavior. The corrected loader still cannot resume data when the campaign itself is unreadable; that is appropriate and distinct from a preferences-only failure.

The separately inspected Playwright output isolation change preserves traces and avoids concurrent cleanup collisions; no test assertion was relaxed. Broad engine/world/art model tests were not repeated because this repair changes only loader separation and guards. Final combined digest/native correspondence and independent visual approval remain separate gates.

