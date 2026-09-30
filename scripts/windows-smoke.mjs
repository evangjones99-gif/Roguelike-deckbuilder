import {_electron as electron, expect} from '@playwright/test';
import {extractFile} from '@electron/asar';
import * as ResEdit from 'resedit';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';

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
    'No controller, audio listening, accessibility or full-campaign acceptance test'],
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
  mark('seed 117 first-run tutorial and battle through controls');
  await page.locator('[data-ui="new"]').click();
  await page.locator('#seed').fill('117');
  await page.locator('#new-game-form button[type="submit"]').click();
  await expect(page.locator('[data-ui="learned"]')).toBeVisible();
  await page.locator('[data-ui="learned"]').click();
  await page.locator('[data-action="travel"]').first().click();
  await page.locator('[data-ui="play-card"][data-card="cairnhound"]').first().click();
  await page.locator('.ally.ready').first().click();
  await page.locator('.enemy.valid-target').first().click();
  const saved = await readSave();
  const state = JSON.parse(saved);
  assert.equal(state.seed, 117);
  assert.equal(state.phase, 'battle');
  assert.ok(state.allies.some(unit => unit.acted), 'Command did not persist');
  evidence.state = {seed: state.seed, phase: state.phase, allies: state.allies.length, enemies: state.enemies.length, hp: state.hp};
  await page.screenshot({path: path.join(outputDir, 'battle.png')});
  mark('reload and resume exact combat save');
  await page.reload();
  await page.locator('[data-ui="resume"]').click();
  assert.equal(await readSave(), saved);
  assert.equal(await page.evaluate(key => localStorage.getItem(key), settingsKey), settings);

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
  assert.equal(feedback.context.run.seed, 117);
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
  console.log('Native Windows packaged launch, branding resources, portrait, tutorial/combat, persistence and negative-feedback download passed.');
} catch (error) {
  evidence.status = 'failed'; evidence.failedPhase = phase;
  evidence.failure = error.stack ?? String(error);
  if (page && !page.isClosed()) await page.screenshot({path: path.join(outputDir, 'failure.png')}).catch(() => {});
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
