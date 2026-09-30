# Native Windows candidate validation

`.github/workflows/windows-validation.yml` configures one Windows Server 2022 x64 GitHub-hosted job, Node 24.19.0, locked `npm ci`, rules tests, production build, directory packaging and actual packaged Electron launch. It runs for pull requests, pushes to main and manual dispatch. Production-branch pushes use the open PR trigger, avoiding separate push and PR jobs for the same update. Contents permission is read-only; checkout credentials are not persisted. Repeated runs for the same PR or ref cancel their previous counterpart. The timeout is 20 minutes. No Steam credentials, signing secrets, paid services or publication step are used.

Configuration is not evidence of a successful native run. At creation, the authors are using Linux; no local native Windows launch has been performed. Inspect the completed Actions job and uploaded `smoke.json` before claiming success. A Linux crossbuild remains a separate package with separate provenance and limitations.

The [first observed Windows run](https://github.com/evangjones99-gif/Roguelike-deckbuilder/actions/runs/36770068258) passed 54 rules tests and the production build, then failed before launch: electron-builder parsed a repeated dotted short option as a config filename `.forceCodeSigning=false` and reported ENOENT. That run supplies no packaged-launch evidence. The retry generates an explicit JSON configuration and passes its path with `--config`, avoiding that parser failure. Node is pinned to the Linux builder's 24.19.0 version; separate source hashing fixes normalize checkout line endings and path separators. Compare the retry's actual commit/digest with its corresponding source, rather than attributing a build of an earlier commit to newer working files.

## Executable resources and signing

The checked-in electron-builder 26.15 schema accepts `win.signAndEditExecutable: true`, `win.signExecutable: false` and `forceCodeSigning: false`. The workflow generates `build-desktop/windows-native-config.json` by copying `package.json`'s build configuration and replacing these options. This retains icon/name/version editing while disabling code signing. `CSC_IDENTITY_AUTO_DISCOVERY=false` prevents certificate discovery. The executable parser uses `resedit`, currently supplied by the locked electron-builder dependency tree; dependency upgrades must preserve that import or promote it to an explicit dependency. It reads actual PE icon and version resources, checks that icon bytes differ from stock Electron and requires the current version plus the Hollowpact product name. Native PowerShell records file metadata and an extracted icon PNG for review, and requires `Get-AuthenticodeSignature` to report `NotSigned`. Resource presence is not a visual branding review or signing acceptance.

## Actual runtime checks

`scripts/windows-smoke.mjs` refuses to run outside native Windows x64. It checks ASAR build provenance against the current production build, hashes the packaged files, launches `Hollowpact.exe` with the normal sandbox enabled and a temporary profile, and verifies context isolation/disabled Node integration. It decodes the real packaged hunter portrait, changes settings through controls, starts seed 117, accepts the first-run tutorial, summons and commands the Cairn Hound, then verifies exact save/settings persistence through reload and full process relaunch.

The feedback check enters explicitly labeled synthetic negative feedback and selects “no” replay intent. A test-only Playwright main-process `will-download` handler selects the native download destination; production gains no privileged API. The check reads the actual downloaded JSON, validates seed/version/digest and negative text, and verifies unchanged storage and inert script-like input. These records are automated QA and must stay separate from human feedback datasets.

Each attempt writes evidence to `reviews/windows-native/<version>/run-<runId>-<attempt>/`. Failed runtime checks also preserve a diagnostic report and screenshot where possible. Uploads include native review evidence, the unsigned candidate ZIP, generated/effective builder configuration and production provenance. ZIP/executable hashes and Git commit/run identity accompany the artifact. Upload retention is 30 days; download and preserve a reviewed candidate in the existing release process before expiration. The workflow does not modify historical release archives or automatically publish/tag a release.

## Practical limits and reproduction

From a native Windows x64 checkout with Node 24.19.0 installed:

```powershell
npm ci
npm test
npm run build
node -e "const fs=require('node:fs'); const {build}=require('./package.json'); const config={...build,win:{...build.win,signAndEditExecutable:true,signExecutable:false},forceCodeSigning:false}; fs.mkdirSync('build-desktop',{recursive:true}); fs.writeFileSync('build-desktop/windows-native-config.json',JSON.stringify(config,null,2)+'\n');"
npx --no-install electron-builder --win dir --x64 --config build-desktop/windows-native-config.json
node scripts/windows-smoke.mjs build-desktop/win-unpacked/Hollowpact.exe
```

This validates one hosted-runner configuration and a short combat flow. It does not qualify real target GPUs, frame pacing, audio quality, controller navigation, complete campaigns, native download chooser behavior, clean consumer installation, SmartScreen, installer/uninstaller, updates, Steam depots or Steam Deck. The unsigned directory ZIP is a review candidate, not a commercial readiness certificate. Preserve failures and correct them before recording the platform as passed.
