# Independent actual v0.5 native package gate

Decision: **accept these exact Linux and native Windows binaries for the v0.5 DEVELOPMENT milestone, with the platform/test limitations and known presentation/input defects below.** The actual native Windows result earns a scoped platform gate; it is not an inferred crossbuild result. Reject polished/AAA/Steam commercial promotion. No source, package, executable, release or CI workflow was modified by this reviewer.

## Artifact identities

Frozen runtime digest `d6221bf764bad593b04981e87bead7ba6868b72cf361d70671af5c91aac39416`, version0.5.0.

Native run `36782560136`, attempt1, job `110116125198`. Personally performed a read-only connected GitHub run GET: completed/success, pull_request event, head `5d1b9ed735349f83fdd14dfb331004d23be30357`. The actual CI checkout recorded in package/transfer/smoke evidence is PR merge commit `eee00c2d2f30d5eae24d7d73566ab43f3a9f8d4f`; this is correctly distinguished from the head/source checkpoint.

| Actual artifact | Identity |
|---|---|
| Original CI native Windows ZIP | 183592465 bytes; SHA256 `2343c5f16239c3f10c1248c44f279322e0bb579047098b379fc438cdb168e769` |
| Actual native Hollowpact.exe | SHA256 `d9421d46864f7be6eea4162db8f6f5f48aaa1c7787d38c7ba0abe0a0d9461d95` |
| Linux and Windows app.asar | Both SHA256 `15f5f6eebf3a41829e7dd8f268869fbd667996bddc1cb69d960e5bfdf04ae757` |
| Native synthetic negative feedback JSON | SHA256 `84e516d2b0614b3e73d7d62d70b4c3c1d3807f850c835ed3fbb9cd91a03b2af3` |

Inspected Windows bytes at `/workspace/scratch/native-windows-v05/run-36782560136-1/native-extracted`; Linux at `build-desktop/linux-unpacked`. The independently verified original Windows ZIP is in that scratch run's parent directory. These identities approve bytes, rather than a replaceable working-directory name.

## Personally executed correspondence audit

- Verified **all9 transferred ZIP wrappers** against recorded size/SHA256; **all8 inner parts**, indices, sizes and SHA256; streamed concatenation and reconstructed original archive against both transfer and native-package records.
- Verified **all72 actual extracted Windows files** against the file hashes recorded by the native smoke test, with no missing/extra files. Inspected ZIP entries:72 regular files and no absolute/traversal/drive-qualified names.
- Verified both ASAR versions, complete **26-source provenance maps** against actual frozen source, and the compact ordered map digest. Compared **all14 dist files** plus **2 desktop files** inside each ASAR with the actual production web/desktop bytes: exact. That includes all8 public paintings, provenance, build identity, compiled code/CSS, index and credits.
- Parsed the actual Windows PE read-only. **7 icon resources**, one group covering16/24/32/48/64/128/256 sizes, all resource hashes/groups/version fields equal native-recorded evidence. ProductName/FileDescription are Hollowpact, FileVersion0.5.0, ProductVersion0.5.0.0. Certificate directory offset/size are zero; actual Get-AuthenticodeSignature evidence reports NotSigned.
- Actual native builder config explicitly enables resource editing and disables signing. The source package's Linux-crossbuild default `signAndEditExecutable:false` must not be misapplied to this tested native executable.
- Electron MIT LICENSE is present on both platforms,1096 bytes, exact to installed Electron LICENSE. Chromium notices are present: Linux20111209 bytes, Windows20472830 bytes. Linux notices equal the installed Linux runtime file; Windows notices match the native CI package-file hash. Platform-specific notice content differs, so cross-platform notice byte equality is not asserted. Presence and correspondence are not a complete legal audit.
- Independently hashed/parsed actual Windows negative-feedback download: correct build digest/version, schema3/kind2 context, negative replay answer and preserved script-like text. Source export is local JSON and the recorded download retains storage unchanged. No human feedback or enjoyment score is invented.
- Viewed actual native executable-icon and battle PNGs: Hollowpact branding, hunter/creatures, equipment painting, available cards and controls appear in the recorded native application.
- Rechecked earlier technical reports' hashes: original CDF and preferences repair remain unchanged; final source report is preserved.

Machine-readable results: `technical-v0.5-native-evidence/audit.json` and the independently queried selected run fields in `api-run.json`.

## Actual runtime evidence and limits

Inspected native CI job log: **64 rules tests pass, zero failures**, production digestd622, and successful native smoke. Windows smoke records win32/x64, Node24.19.0, Windows10.0.20348, **9 executed phases**, no errors/network requests. It verifies sandbox/contextIsolation enabled, Node integration disabled, launch without sandbox-disable flags, fresh-profile settings/tutorial/seed121 battle, exact save reload and process relaunch, file-protocol hunter/warleader/tool image decoding, actual starter painted card controls and completed native local negative-feedback download. The packaging source was inspected alongside the retained report; configuration alone is not treated as execution.

This reviewer executes on Linux and independently audits native bytes/results; I did not personally execute Windows. Windows evidence establishes one hosted native configuration, reduced-motion early combat and synthetic QA. It does not establish listening quality, motion-on full campaign on Windows, consumer installation/SmartScreen, broad GPUs/hardware, native chooser UX (test sets download path), controllers, accessibility, Steam/Deck/depot/update acceptance or human enjoyment.

Inspected actual **finald622** Linux fresh-profile reports `linux-desktop-0.5.0-d6221bf764ba-96481-1790806028690-smoke.json` and `linux-feedback-0.5.0-d6221bf764ba-1790805960196-smoke.json`: successful reduced-motion tutorial/combat and local negative export, correct schema/generation/digest, unchanged storage and no errors. Their Xvfb/software graphics and **--no-sandbox test override** remain explicit; normal sandboxed clean-machine Linux launch is unverified. Older CDF version-named smoke files remain historical and are not used as final evidence.

Independent final gameplay/visual reviews approve development preservation on d622. They explicitly retain inherited held-Enter/focus recovery P2s and long-range hound air-bite contact (~97.8px short in extreme-column diagnostics), alongside sparse cel animation, generic spell effects and interface craft limits. Neither new native launch success nor source correctness closes those product defects. Immediate next milestone must repair intentional keyboard activation/focus and reach-aware contact with paired regression evidence.

Commercial generated-art/source rights, real-player comprehension/enjoyment and platform/publication gates remain unresolved. Existing durable v0.4 draft storage is separate, partial/mutable access; this review creates no v0.5 external release and certifies no permanent hosting.

