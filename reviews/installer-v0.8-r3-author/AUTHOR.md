# R3 signature host proposal

The actual R2 native run36802452392 compiled its installer but failed before installation when Windows PowerShell could not autoload Microsoft.PowerShell.Security. This is a failed preflight, not installer acceptance.

Only the signature helper changes: invoke PowerShell7 (`pwsh.exe`), the actual workflow host used by the existing portable validation's successful signature oracle, and explicitly import its built-in security module with terminating errors. Preserve the real Get-AuthenticodeSignature call, literal environment-carried path, NotSigned assertions, fixed-source/runtime/ownership guards and all install/gameplay/uninstall requirements. Registry queries still use their original Windows PowerShell .NET implementation. No signature assertion is removed or process failure accepted.

This aligns interpreter/module execution; the inherited module-path incompatibility remains a hypothesis, not a diagnosed root cause. No PSModulePath manipulation, environment dump, signing, publication, install operation or native test has run for this proposal. Fresh independent review and actual native execution are required.

The earlier shell-only draft stopped on a false assumption about the portable workflow host. Its partial files/failure remain at installer-shell-repair-v08-r3. This new proposal does not change either workflow.
