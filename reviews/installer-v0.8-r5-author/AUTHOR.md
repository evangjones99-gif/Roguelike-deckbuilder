# R5 strict semantic dialog close

Actual R4 run36804006841 installs, verifies exact source/payload/image/signature and launches the sandboxed game, then stops at settings close because both the header Close dialog and body Return intentionally use data-ui=close. It has no campaign/export/persistence/uninstall acceptance.

Select the exact accessible button name Close dialog at the one existing settings close operation, preserving strict uniqueness and all settings/report steps. No first(), force, broad wait, source UI change or reduced assertion. Report export still closes the entire app exactly as before. Every other source/ownership/cache/registry/signature/image/gameplay/persistence/uninstall gate remains unchanged. Independent static review and native retry remain required. Root separately audits the preserved0be web UI route; web automation is not native installer acceptance.

Root working game45bd is a frozen uncommitted0.8 candidate. The tooling commit stages only helper/reviews/docs, leaving its committed tree at old pinned29-input0be. CI must not be attributed to the working game. Earlier two-close preparation assumption/failure is retained here.
