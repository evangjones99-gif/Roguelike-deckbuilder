# Independent shipping audio technical/native review

**Verdict: accept the frozen audio proposal for controlled source integration, subject to testing the resulting combined playable build.** This is scoped engineering acceptance; AAA craft, human enjoyment, audible quality and Steam release are unverified.

Reviewed runtime **efe13ff6d9f8464cdbaaf156e5f4bdf86b6ea4f725dfe3468cd501c12ab78df1**, 74 exact runtime inputs and 54 outputs. I did not author this proposal or edit its files or production source. I verified all **152** declared author freeze/addendum files, recomputed the complete source identity independently, and restored every output into a new `/tmp/hollowpact-audio-independent-v08-r1/dist` using the original retained v0.7 web archive, four-member delta and39 pinned WAVs. Output hashes and embedded provenance all match the frozen proposal. My host uses independently copied exact desktop main/lifecycle/icon bytes. No fresh build success is inferred from reconstruction.

The actual current production0be source remains byte exact for all29 baseline inputs. Candidate26 unchanged baseline inputs and its three changes (`src/main.ts`, `desktop/main.cjs`, attribution inventory) match the declared scope;45 added inputs comprise39 WAVs, five audio/type modules and one lifecycle module. The engine, content, world randomness, saves, input adapter, arena, hunter and stylesheet are unchanged. I inspected the actual semantic main hunks, private lifecycle and player/routing modules, preserving my inspected code bytes and their hashes. No lab query, global audio gate, test history, preload, IPC or mutable diagnostic bridge is introduced. The original request/navigation/new-window restrictions, title/icon/dimensions and sandbox/context-isolation/no-Node preferences remain. `no-user-gesture-required` is an explicit autoplay-policy change needed for native controller activation, not a retained baseline preference; activation is still gated in source and was exercised below.

The lifecycle uses separate document and visibility generations. Loading/renderer loss invalidate readiness and immediately mute native output. Visibility transitions immediately mute, serialize the fixed renderer event and unmute only when the latest visible/local/ready generation receives the synchronous cancellation epoch. Missing or rejected receipt fails closed. These renderer events convey cancellation only, with no main arguments or privileged capability. Cancellation retires voices using the existing12ms fade/stop; a receipt is not measured physical silence.

## My actual execution

`native-independent-r1` executes the actual shipping-shaped main against the independently reconstructed local file build in installed Electron. It passes **12 distinct own checks**, not the author's test run:

1. Neutral initial page exposes no renderer Node, lab/global gate or AudioContext, and retains configured isolation/security.
2. Four rapid actual hide/show cycles remain context-free without renderer user activation.
3. Accepted synthetic standard-controller Resume creates a running context and decodes39 real local WAV buffers with `navigator.userActivation.hasBeenActive=false`.
4. The actual historical mutually lethal command saves the exact canonical result. I reject **every** native inactive delivery, hide the real window, then restore it. A strictly newer active receipt precedes native unmute. Releasing six held real decoded hound/iron buffers produces **zero stale source starts**, while the canonical save remains byte exact.
5. Controller sound-mute settings and canonical final-kill save survive actual native hide/show.
6. Suppressed active renderer acknowledgement stays native-muted; a later real acknowledgement recovers.
7. Actual active JavaScript delivery rejection also stays muted; the next acknowledged generation recovers.
8. A privileged main diagnostic load of `about:blank` invalidates readiness and remains muted.
9. A180ms externally injected ready-delivery delay with two real hide/show cycles establishes a current-document barrier, with no context or browser user activation.
10. Actual `forcefullyCrashRenderer()` mutes and invalidates readiness.
11. Actual local-file reload after that fault recovers without unsolicited context/user activation.
12. Response bodies for all39 requested WAVs match the frozen output hashes. Observed requests are local files plus the explicit diagnostic foreign-document load; no remote media request appears.

Every renderer read/mutation uses raw CDP `Runtime.evaluate` with `userGesture:false`; no Playwright evaluator's implicit activation is used for these conclusions. AudioContext/fetch/source wrappers observe real browser decoding/scheduling but are externally injected test instruments, absent from shipped bytes. Synthetic gamepad and focus events, main-function delivery faults and crash are qualified interventions. The two recorded page errors belong to deliberate missing-receipt and foreign-document faults. Hosts are closed.

I additionally replay **eight retained legacy engine fixtures** through the unchanged current candidate reducer, including two ready-overlapping commands. All expected states/events match, validators pass and the audio contact observer preserves canonical inputs. These are diagnostic schema2 fixture/oracle checks, not new campaign or human playtests. My first fixture harness failed before running any fixture because Node/tsx lacks Vite's `import.meta.env.BASE_URL`; its source and log remain. The separate R2 harness uses esbuild with the explicit Vite base definition, corrects the transition-field assumption to the fixture's `state` key, and passes. No source fix or game regression is attributed to that harness failure.

The author's nine current native checks,87 rules tests and strict-build logs remain separately attributed. My12 checks are not a rebranding of those records. The author report mentions Git44b while its source-diff record pins983; those commits share the same baseline0be runtime, independently verified here. Future documentation should consistently identify the exact prepared metadata commit without changing the runtime evidence.

## Remaining gates

This run is an unpackaged Linux development Electron host on Xorg dummy97/software rendering and `--no-sandbox`, in a unique explicitly observed `/tmp` profile. Preference assertions are not native OS sandbox certification. No window manager means physical minimize is unverified; hide/show is the measured API behavior. Physical controller, speakers/listening, sound timbre, synchronization as heard, consumer Windows/Linux installations, Steam Deck, rights/store AI disclosure, AAA production values and human fun remain open. This review does not cover a later audio/encounter/hound combined merge or a newly packaged executable. Test and independently review those resulting bytes before milestone release.

Source-only inspection cannot prove arbitrary future availability or all races. Optional audio failure remains deliberately nonfatal to canonical gameplay.39 synthesized signals provide creature-specific routing; their perceived quality needs real listening feedback. The approval is for controlled integration of these exact bytes, not commercial readiness.
