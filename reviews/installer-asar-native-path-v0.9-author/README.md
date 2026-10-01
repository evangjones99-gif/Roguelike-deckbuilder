# Frozen exterior installer path proposal

Read AUTHOR.md, PROPOSED-THREE-FILE.patch and the original Windows failure references in INPUTS-PRE.json. Proposed helper/test/smoke files live under proposed/scripts; baseline files retain exact root originals. All other copied companions are unchanged. Root and old packets are untouched.

Actual evidence: guards-r1.log49passing tests; WIN32-LOOKUP-DIAGNOSTIC.json unchanged installed library source with only Win32 path linking (Linux simulation); ACTUAL-LINUX-PRODUCER-GATE.json exact retained6a89/60leaf/78source/56output payload. Native Windows installer acceptance is pending and not implied by this evidence.

No dependencies are downloaded/copied. proposed/node_modules is an absolute reference to the existing root installed tools. Original small Windows ZIP/receipts and full producer archive are exact external references, not copied into this bounded packet. Test fixture originals remain untouched in TMP with hashes in TEST-FIXTURE-REFERENCES.json; TMP is not durable archival evidence. All raw logs and proposed source are durable.

A reviewer should create separately owned output paths; scripts intentionally use exclusive output creation and must not overwrite this packet. Portable guard command uses root cwd for real WAV/current-source reads:

    cd /workspace/Roguelike-deckbuilder
    node --test /workspace/scratch/installer-asar-native-path-author-v09-r1/proposed/scripts/windows-installer-guards.test.mjs /workspace/scratch/installer-asar-native-path-author-v09-r1/proposed/scripts/windows-installer-current-validation.test.mjs /workspace/scratch/installer-asar-native-path-author-v09-r1/proposed/scripts/windows-installer-transfer.test.mjs

The diagnostic requires the installed Node --experimental-vm-modules flag, whose warning is retained. It proves library traversal, not Windows file extraction. Independent review may reject the repair. No QA activation or platform claim is authorized by this packet alone.
