# R4 native ASAR path proposal

Actual R3 run36803389350 passed signature, silent installation, registry/cache isolation and exact staged/installed payload checks, then failed before launching the game when extracting the hunter PNG with a forward-slash multi-level ASAR path on Windows. The runtime ASAR e270 is unchanged from the retained portable package. No installed gameplay or uninstall acceptance is inferred.

Change only that extraction argument to native path.join('dist','art','hunter-marek-v07-r3.png'), which the installed @electron/asar Filesystem directory traversal expects on Windows. Preserve the exact PNG SHA assertion, all install/source/signature/cache/registry/gameplay/persistence/uninstall checks and the already reviewed R3 signature repair. Do not modify assets, engine, packaging, workflow or canonical0be inputs.

Independent source/library-path review and another actual Windows run are required. The Linux syntax/path check is not native installation evidence. Original R3 failed artifacts and ownership directories remain retained by the actual CI receipts.
