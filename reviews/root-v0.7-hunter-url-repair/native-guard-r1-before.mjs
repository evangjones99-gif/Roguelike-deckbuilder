import {_electron as electron, expect} from '@playwright/test';
import {extractFile} from '@electron/asar';
import * as ResEdit from 'resedit';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';
import {tsImport} from 'tsx/esm/api';

const version = JSON.parse(fs.readFileSync('package.json', 'utf8')).version;
const run = `run-${process.env.GITHUB_RUN_ID ?? 'local'}-${process.env.GITHUB_RUN_ATTEMPT ?? Date.now()}`;
const outputDir = path.resolve('reviews', 'windows-native', version, run);
fs.mkdirSync(outputDir, {recursive: true});
const executablePath = path.resolve(process.argv[2] ?? 'build-desktop/win-unpacked/Hollowpact.exe');
const packageDir = path.dirname(executablePath);
const hash = value => crypto.createHash('sha256').update(value).digest('hex');
const evidence = {
  version, status: 'running', platform: process.platform, architecture: process.arch,
  node: process.version, osRelease: os.release(), executablePath,
  commit: process.env.GITHUB_SHA ?? null, runId: process.env.GITHUB_RUN_ID ?? null,
  steps: [], errors: [],
  limits: ['Synthetic automated QA, not human feedback or a fun rating',
    'One native Windows hosted-runner x64 configuration; no broad hardware or performance qualification',
    'Test-only main-process download save-path hook bypasses the native chooser',
    'Unsigned directory package; no installer, SmartScreen, Steam depot, update or Steam Deck test',
    'CDP trusted-key dispatch is automated input, not a physical keyboard/controller test',
    'No physical controller, audio listening, broad accessibility or full-campaign acceptance test'],
};
let app;
let page;
let profile;
let phase = 'platform precondition';
const mark = name => { evidence.steps.push(name); phase = name; };
const saveKey = 'hollowpact.run.v2';
const settingsKey = 'hollowpact.settings.v2';
const readSave = () => page.evaluate(key => localStorage.getItem(key), saveKey);
function files(directory) {
  return fs.readdirSync(directory, {withFileTypes: true}).flatMap(entry =>
    entry.isDirectory() ? files(path.join(directory, entry.name)) : [path.join(directory, entry.name)]);
}
function inspectPE(file) {
  // Read-only parser: never writes/re-signs the executable under test.
  const exe = ResEdit.NtExecutable.from(fs.readFileSync(file), {ignoreCert: true});
  const resources = ResEdit.NtExecutableResource.from(exe).entries;
  return {
    icons: resources.filter(entry => entry.type === 3).map(entry => ({
      id: entry.id, language: entry.lang, sha256: hash(Buffer.from(entry.bin)),
    })),
    iconGroups: ResEdit.Resource.IconGroupEntry.fromEntries(resources).map(group => ({
      id: group.id, language: group.lang, sizes: group.icons.map(icon => [icon.width, icon.height]),
    })),
    versions: ResEdit.Resource.VersionInfo.fromEntries(resources).map(info => ({
      fixed: info.fixedInfo,
      strings: info.getAllLanguagesForStringValues().map(language => info.getStringValues(language)),
    })),
  };
}
async function launch() {
  const environment = {...process.env};
  delete environment.ELECTRON_RUN_AS_NODE;
  app = await electron.launch({executablePath, args: [`--user-data-dir=${profile}`], env: environment, timeout: 60000});
  page = await app.firstWindow({timeout: 30000});
  page.setDefaultTimeout(15000);
  page.on('pageerror', error => evidence.errors.push(error.message));
  page.on('request', request => {
    if (/^https?:/i.test(request.url())) evidence.errors.push(`Unexpected renderer network request: ${request.url()}`);
  });
  await page.waitForLoadState('domcontentloaded');
  const preferences = await app.evaluate(({BrowserWindow, app}) => ({
    userData: app.getPath('userData'),
    webPreferences: BrowserWindow.getAllWindows()[0].webContents.getLastWebPreferences(),
  }));
  assert.equal(path.resolve(preferences.userData).toLowerCase(), profile.toLowerCase());
  assert.equal(preferences.webPreferences.sandbox, true);
  assert.equal(preferences.webPreferences.contextIsolation, true);
  assert.equal(preferences.webPreferences.nodeIntegration, false);
  evidence.security = {sandbox: true, contextIsolation: true, nodeIntegration: false, launchSandboxDisabled: false};
}
try {
  assert.equal(process.platform, 'win32', 'This test requires native Windows; Linux packaging is not a Windows launch result');
  assert.equal(process.arch, 'x64');
  mark('validate packaged provenance and executable resources');
  const expected = JSON.parse(fs.readFileSync('dist/build-provenance.json', 'utf8'));
  const asarPath = path.join(packageDir, 'resources', 'app.asar');
  const runtime = JSON.parse(extractFile(asarPath, 'dist/build-provenance.json').toString());
  assert.equal(runtime.version, version);
  assert.equal(runtime.sourceDigest, expected.sourceDigest);
  assert.deepEqual(runtime.hashes, expected.hashes);
  evidence.runtimeSourceDigest = runtime.sourceDigest;
  // Canonical expected results must use the exact packaged rules, not an unrelated checkout.
  const engineDependencies = ['src/engine.ts', 'src/content.ts', 'src/world-rng.ts'];
  evidence.canonicalEngineSource = {};
  for (const file of engineDependencies) {
    const sha256 = hash(fs.readFileSync(file));
    assert.equal(sha256, runtime.hashes[file], `Canonical engine dependency differs from packaged runtime: ${file}`);
    evidence.canonicalEngineSource[file] = sha256;
  }
  const {applyAction, legalActions} = await tsImport(pathToFileURL(path.resolve('src/engine.ts')).href, import.meta.url);
  evidence.packageFiles = Object.fromEntries(files(packageDir).sort().map(file =>
    [path.relative(packageDir, file).replaceAll('\\', '/'), hash(fs.readFileSync(file))]));
  evidence.executableSHA256 = evidence.packageFiles[path.basename(executablePath)];
  evidence.asarSHA256 = hash(fs.readFileSync(asarPath));
  evidence.resources = inspectPE(executablePath);
  assert.ok(evidence.resources.icons.length > 0 && evidence.resources.iconGroups.length > 0, 'Missing executable icon resources');
  const stockIcons = inspectPE(path.resolve('node_modules/electron/dist/electron.exe')).icons;
  assert.notDeepEqual(evidence.resources.icons.map(icon => icon.sha256).sort(), stockIcons.map(icon => icon.sha256).sort(), 'Executable retains stock Electron icons');
  const versionStrings = evidence.resources.versions.flatMap(info => info.strings);
  assert.ok(versionStrings.some(info => info.ProductName === 'Hollowpact'), 'Wrong executable product name');
  assert.ok(versionStrings.some(info => info.FileVersion?.replace(/\.0$/, '') === version || info.FileVersion === version), 'Wrong executable file version');
  assert.ok(versionStrings.some(info => info.ProductVersion?.replace(/\.0$/, '') === version || info.ProductVersion === version), 'Wrong executable product version');

  profile = fs.mkdtempSync(path.join(os.tmpdir(), 'hollowpact-windows-'));
  mark('launch fresh packaged executable with sandbox enabled');
  await launch();
  mark('decode packaged hunter portrait');
  evidence.portrait = await page.locator('.title-hunter').evaluate(async element => {
    const match = getComputedStyle(element).backgroundImage.match(/^url\(["']?(.*?)["']?\)$/);
    if (!match) throw new Error('Hunter portrait background URL absent');
    const image = new Image(); image.src = match[1]; await image.decode();
    return {width: image.naturalWidth, height: image.naturalHeight, protocol: new URL(image.src).protocol};
  });
  assert.deepEqual(evidence.portrait, {width: 1199, height: 1312, protocol: 'file:'});
  await page.screenshot({path: path.join(outputDir, 'title.png')});
  mark('set and persist sound, volume and reduced-motion preferences through controls');
  await page.locator('[data-ui="settings"]').click();
  await page.locator('#mute').uncheck();
  await page.locator('#motion').uncheck();
  await page.locator('#volume').press('Home');
  await page.locator('#volume').press('ArrowRight');
  await expect(page.locator('html')).toHaveAttribute('data-reduced-motion', 'true');
  await page.locator('[data-ui="close"]').first().click();
  const settings = await page.evaluate(key => localStorage.getItem(key), settingsKey);
  assert.deepEqual(JSON.parse(settings), {mute: true, volume: 0.01, motion: false});
  mark('seed 121 first-run tutorial and battle through controls');
  // Observe the asset actually used by the shipped renderer. A separately
  // decoded relative URL would miss an accidental root-relative runtime URL.
  await page.evaluate(() => {
    window.__nativeHunterDraws = [];
    const original = CanvasRenderingContext2D.prototype.drawImage;
    window.__nativeHunterDrawRestore = () => {
      CanvasRenderingContext2D.prototype.drawImage = original;
    };
    CanvasRenderingContext2D.prototype.drawImage = function(image, ...args) {
      if (image instanceof HTMLImageElement && image.src.endsWith('/art/hunter-marek-v07-r3.png') &&
          window.__nativeHunterDraws.length < 128) {
        const matrix = this.getTransform(), rect = this.canvas.getBoundingClientRect();
        const [,,sw,sh,dx,dy,dw,dh] = args;
        const quad = args.length === 8 ? [[dx,dy],[dx+dw,dy],[dx+dw,dy+dh],[dx,dy+dh]].map(([x,y]) => ({
          x: (matrix.a*x + matrix.c*y + matrix.e) * rect.width / this.canvas.width,
          y: (matrix.b*x + matrix.d*y + matrix.f) * rect.height / this.canvas.height,
        })) : [];
        window.__nativeHunterDraws.push({url: image.src, width: image.naturalWidth,
          height: image.naturalHeight, source: args.slice(0, 4), canvas: this.canvas.id,
          viewport: {width: rect.width, height: rect.height}, quad});
      }
      return original.call(this, image, ...args);
    };
  });
  await page.locator('[data-ui="new"]').click();
  await page.locator('#seed').fill('121');
  await page.locator('#new-game-form button[type="submit"]').click();
  await expect(page.locator('[data-ui="learned"]')).toBeVisible();
  await page.locator('[data-ui="learned"]').click();
  await page.locator('[data-action="travel"]').first().click();
  const beforeBinding = JSON.parse(await readSave());
  const bindingIndex = beforeBinding.hand.indexOf('cairnhound');
  assert.ok(bindingIndex >= 0, 'Actual starter hand has no Cairn Hound');
  const expectedBinding = applyAction(beforeBinding, {type: 'play', index: bindingIndex});
  await page.locator('[data-ui="play-card"][data-card="cairnhound"]').first().click();
  assert.deepEqual(JSON.parse(await readSave()), expectedBinding, 'Binding differs from exact packaged canonical rules');
  mark('verify actual packaged hunter sheet draws from a local full cell');
  await expect.poll(() => page.evaluate(() => window.__nativeHunterDraws.length)).toBeGreaterThan(0);
  evidence.hunterFigure = await page.evaluate(() => {
    const draws = window.__nativeHunterDraws;
    window.__nativeHunterDrawRestore();
    delete window.__nativeHunterDrawRestore;
    delete window.__nativeHunterDraws;
    return {method: 'Test-only observation of actual runtime Canvas2D drawImage; original drawing is delegated unchanged', draws};
  });
  for (const draw of evidence.hunterFigure.draws) {
    assert.equal(new URL(draw.url).protocol, 'file:');
    assert.ok(new URL(draw.url).pathname.endsWith('/dist/art/hunter-marek-v07-r3.png'),
      'Runtime hunter URL escaped the packaged dist directory');
    assert.equal(draw.width, 1536); assert.equal(draw.height, 1024);
    assert.equal(draw.source.length, 4);
    assert.equal(draw.source[2], 512); assert.equal(draw.source[3], 512);
    assert.equal(draw.quad.length, 4);
    for (const point of draw.quad) {
      assert.ok(Number.isFinite(point.x) && Number.isFinite(point.y));
      assert.ok(point.x >= -0.01 && point.x <= draw.viewport.width + 0.01 &&
        point.y >= -0.01 && point.y <= draw.viewport.height + 0.01,
        'Packaged hunter full-cell draw leaves the actual canvas viewport');
    }
  }
  mark('verify packaged regional keyboard and nested modal focus');
  const uncommandedSave = await readSave();
  const uncommanded = JSON.parse(uncommandedSave);
  const sourceUnit = uncommanded.allies.find(unit => !unit.acted);
  assert.ok(sourceUnit, 'Actual starter binding must have an unspent command');
  const sourceControl = page.locator(`[data-unit="${sourceUnit.uid}"]`);
  evidence.keyboard = {method: 'Playwright CDP trusted renderer-key dispatch into sandboxed packaged executable',
    physicalKeyboard: false, physicalController: false, beforeSaveSHA256: hash(uncommandedSave), held: []};
  await page.evaluate(() => {
    window.__nativeKeyboardTrace = [];
    window.__nativeKeyboardHandler = event => {
      if (['Enter', ' '].includes(event.key) && window.__nativeKeyboardTrace.length < 64)
        window.__nativeKeyboardTrace.push({key: event.key, type: event.type, trusted: event.isTrusted,
          repeat: event.repeat, prevented: event.defaultPrevented});
    };
    document.addEventListener('keydown', window.__nativeKeyboardHandler, true);
  });
  await page.keyboard.press('h');
  assert.equal(await page.evaluate(() => document.activeElement.matches('.hand-cards button')), true);
  const handFocus = await page.evaluate(() => document.activeElement.dataset.focus);
  assert.ok(uncommanded.hand.length > 1, 'Actual starter hand must offer more than one remaining card');
  await page.keyboard.press('ArrowRight');
  const nextHandFocus = await page.evaluate(() => document.activeElement.dataset.focus);
  assert.notEqual(nextHandFocus, handFocus, 'Right arrow did not navigate the actual hand');
  await page.keyboard.press('b');
  await expect(sourceControl).toBeFocused();
  await page.keyboard.press('t');
  assert.equal(await page.evaluate(() => document.activeElement.matches('.enemy')), true);
  const hostileFocus = await page.evaluate(() => document.activeElement.dataset.unit);
  await page.keyboard.press('b');
  await expect(sourceControl).toBeFocused();
  assert.equal(await readSave(), uncommandedSave, 'Focus navigation changed the canonical save');
  evidence.keyboard.regional = {handFocus, nextHandFocus, binding: sourceUnit.uid, hostileFocus, saveUnchanged: true};

  await page.keyboard.press('i');
  await expect(page.locator('#dialog-title')).toContainText(sourceUnit.name);
  await expect(page.locator('#dialog-title')).toBeFocused();
  await page.keyboard.press('Escape');
  await expect(sourceControl).toBeFocused();
  const deckOpener = page.locator('#topbar [data-ui="deck"]');
  await deckOpener.focus();
  await page.keyboard.press('Enter');
  await expect(page.locator('#dialog-title')).toBeFocused();
  await page.keyboard.press('Tab');
  assert.equal(await page.evaluate(() => document.querySelector('#dialog').contains(document.activeElement)), true);
  await page.locator('#dialog .game-card[data-card="scour"]').first().focus();
  await page.keyboard.press('Enter');
  await expect(page.locator('#dialog-title')).toHaveText('Scour');
  await expect(page.locator('#dialog-title')).toBeFocused();
  await page.keyboard.press('Escape');
  await expect(deckOpener).toBeFocused();
  assert.equal(await readSave(), uncommandedSave, 'Inspection/modal replacement changed the canonical save');
  evidence.keyboard.modal = {unitOriginRestored: true, nestedDossierTitleFocused: true, deckOriginRestored: true,
    oneNativeTabInsideDialog: true, saveUnchanged: true};

  mark('verify held Enter and Space cannot follow selection into a command');
  for (const activation of ['Enter', 'Space']) {
    await sourceControl.focus();
    try {
      // Repeated down calls use Playwright's pressed-key tracking to dispatch autoRepeat=true.
      await page.keyboard.down(activation);
      await page.keyboard.down(activation);
      await page.keyboard.down(activation);
      assert.equal(await readSave(), uncommandedSave, `Held ${activation} committed a command before release`);
    } finally { await page.keyboard.up(activation); }
    await expect(sourceControl).toHaveAttribute('aria-pressed', 'true');
    assert.equal(await page.evaluate(() => document.activeElement.matches('.enemy.valid-target')), true);
    assert.equal(await readSave(), uncommandedSave, `Held ${activation} followed target focus into a command`);
    const selectedTarget = await page.evaluate(() => document.activeElement.dataset.unit);
    await page.keyboard.press('Escape');
    await expect(sourceControl).toBeFocused();
    await expect(sourceControl).toHaveAttribute('aria-pressed', 'false');
    assert.equal(await readSave(), uncommandedSave, `Cancel after ${activation} changed the save`);
    evidence.keyboard.held.push({activation, selectedTarget, saveUnchangedUntilFreshActivation: true,
      cancelRestoresSource: true});
  }
  mark('verify deliberate fresh keyboard command matches packaged rules');
  await sourceControl.focus();
  await page.keyboard.press('Enter');
  const targetUid = await page.evaluate(() => document.activeElement.dataset.unit);
  const command = {type: 'attack', unit: sourceUnit.uid, target: targetUid};
  assert.ok(legalActions(uncommanded).some(action => JSON.stringify(action) === JSON.stringify(command)),
    'Keyboard-selected target is not a legal canonical command');
  const expectedCommand = applyAction(uncommanded, command);
  await page.keyboard.press('Enter');
  assert.deepEqual(JSON.parse(await readSave()), expectedCommand, 'Fresh keyboard command differs from packaged canonical rules');
  evidence.keyboard.trace = await page.evaluate(() => {
    document.removeEventListener('keydown', window.__nativeKeyboardHandler, true);
    return window.__nativeKeyboardTrace;
  });
  assert.ok(evidence.keyboard.trace.every(event => event.trusted), 'Keyboard probe used untrusted DOM key dispatch');
  for (const key of ['Enter', ' ']) assert.ok(evidence.keyboard.trace.some(event =>
    event.key === key && event.repeat && event.prevented), `Missing prevented trusted repeat for ${key}`);
  evidence.keyboard.command = {...command, exactCanonicalState: true, afterSaveSHA256: hash(await readSave())};
  await page.screenshot({path: path.join(outputDir, 'keyboard-command.png')});
  const saved = await readSave();
  const state = JSON.parse(saved);
  assert.equal(state.seed, 121);
  assert.equal(state.schema, 3);
  assert.equal(state.engineKind, 2);
  assert.equal(state.phase, 'battle');
  assert.ok(state.allies.some(unit => unit.acted), 'Command did not persist');
  evidence.state = {seed: state.seed, phase: state.phase, allies: state.allies.length, enemies: state.enemies.length, hp: state.hp};
  await page.screenshot({path: path.join(outputDir, 'battle.png')});
  mark('reload and resume exact combat save');
  await page.reload();
  await page.locator('[data-ui="resume"]').click();
  assert.equal(await readSave(), saved);
  assert.equal(await page.evaluate(key => localStorage.getItem(key), settingsKey), settings);

  mark('decode packaged warleader/tool sheets and render actual starter equipment paintings');
  evidence.decorativeArt = await page.evaluate(async () => {
    const result = {};
    for (const file of ['warleader-poses.png', 'tool-vignettes.png']) {
      const image = new Image(); image.src = new URL(`art/${file}`, document.baseURI).href;
      await image.decode();
      result[file] = {width: image.naturalWidth, height: image.naturalHeight, protocol: new URL(image.src).protocol};
    }
    return result;
  });
  assert.deepEqual(evidence.decorativeArt['warleader-poses.png'], {width:1536,height:1024,protocol:'file:'});
  assert.deepEqual(evidence.decorativeArt['tool-vignettes.png'], {width:1774,height:887,protocol:'file:'});
  await page.locator('[data-ui="deck"]').click();
  for (const id of ['scour', 'ironward', 'sutures']) {
    await expect(page.locator(`dialog [data-card="${id}"] .card-art`).first()).toHaveClass(/illustration-ready/);
  }
  assert.equal(await readSave(), saved);
  await page.locator('[data-ui="close"]').click();

  mark('export explicit synthetic negative feedback through native will-download');
  const destination = path.join(outputDir, 'synthetic-negative-feedback.json');
  await app.evaluate(({session}, destination) => {
    globalThis.__windowsFeedback = {state: 'pending'};
    session.defaultSession.once('will-download', (_event, item) => {
      item.setSavePath(destination);
      item.once('done', (_event, state) => { globalThis.__windowsFeedback = {state}; });
    });
  }, destination);
  const storage = await page.evaluate(() => JSON.stringify({...localStorage}));
  const negative = '[AUTOMATED WINDOWS QA — not a human opinion] <script>window.nativeAudit=1</script> Target unclear.';
  await page.locator('[data-ui="feedback"]').click();
  await page.locator('#feedback-confusion').fill(negative);
  await page.locator('#feedback-choice').fill('None in this synthetic interaction check.');
  await page.locator('#feedback-replay').selectOption('no');
  await page.locator('#feedback-form button[type="submit"]').click();
  await expect.poll(() => app.evaluate(() => globalThis.__windowsFeedback.state), {timeout: 15000}).toBe('completed');
  const feedback = JSON.parse(fs.readFileSync(destination, 'utf8'));
  assert.equal(feedback.context.build.sourceDigest, runtime.sourceDigest);
  assert.equal(feedback.context.build.version, version);
  assert.equal(feedback.context.run.seed, 121);
  assert.equal(feedback.responses.confusion, negative);
  assert.equal(feedback.responses.replayIntent, 'no');
  assert.equal(await page.evaluate(() => JSON.stringify({...localStorage})), storage);
  assert.equal(await page.evaluate(() => window.nativeAudit), undefined);
  evidence.feedback = {download: 'completed', storageUnchanged: true, reportSHA256: hash(fs.readFileSync(destination)), synthetic: true};
  mark('relaunch packaged executable and resume persistent profile');
  await app.close(); app = undefined;
  await launch();
  await page.locator('[data-ui="resume"]').click();
  assert.equal(await readSave(), saved);
  assert.equal(await page.evaluate(key => localStorage.getItem(key), settingsKey), settings);
  assert.equal(await page.evaluate(() => localStorage.getItem('hollowpact.tutorial.v2')), 'yes');
  await page.screenshot({path: path.join(outputDir, 'relaunch-resumed.png')});
  assert.deepEqual(evidence.errors, []);
  evidence.status = 'passed';
  console.log('Native Windows packaged launch, branding resources, keyboard focus/repeat guards, portrait, tutorial/combat, persistence and negative-feedback download passed.');
} catch (error) {
  evidence.status = 'failed'; evidence.failedPhase = phase;
  evidence.failure = error.stack ?? String(error);
  if (page && !page.isClosed()) {
    if (evidence.keyboard && !evidence.keyboard.trace)
      evidence.keyboard.trace = await page.evaluate(() => window.__nativeKeyboardTrace ?? []).catch(() => []);
    await page.screenshot({path: path.join(outputDir, 'failure.png')}).catch(() => {});
  }
  console.error(evidence.failure);
  process.exitCode = 1;
} finally {
  if (app) await app.close().catch(error => {
    evidence.errors.push(`Close failed: ${error.message}`); evidence.status = 'failed'; process.exitCode = 1;
  });
  if (profile) {
    try { fs.rmSync(profile, {recursive: true, force: true, maxRetries: 5, retryDelay: 200}); }
    catch (error) {
      evidence.errors.push(`Temporary profile cleanup failed: ${error.message}`);
      evidence.status = 'failed'; process.exitCode = 1;
    }
  }
  fs.writeFileSync(path.join(outputDir, 'smoke.json'), JSON.stringify(evidence, null, 2) + '\n');
}
