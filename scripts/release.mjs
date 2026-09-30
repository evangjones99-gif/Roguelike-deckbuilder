import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {gunzipSync} from 'node:zlib';
import { execFileSync } from 'node:child_process';

const version = process.argv[2];
if (!version || !/^\d+\.\d+\.\d+(?:-[a-z0-9.]+)?$/.test(version)) throw new Error('Usage: npm run release -- 0.1.0');
const root = process.cwd();
const dest = path.join(root, 'releases', version);
if (fs.existsSync(dest)) throw new Error(`Release ${version} already exists. Choose a new version; releases are never overwritten.`);
// Reserve the entire build/archive transaction, not only the final directory.
const lock = path.join(root,'.release-lock');
try { fs.mkdirSync(lock); } catch { throw new Error('Another release owns .release-lock. Inspect its owner.json and process liveness before repairing a stale lock.'); }
fs.writeFileSync(path.join(lock,'owner.json'),JSON.stringify({pid:process.pid,version,startedAt:new Date().toISOString()})+'\n');
process.once('exit',()=>fs.rmSync(lock,{recursive:true,force:true}));
process.once('SIGINT',()=>process.exit(130));
process.once('SIGTERM',()=>process.exit(143));
const pkg = JSON.parse(fs.readFileSync('package.json', 'utf8'));
if (pkg.version !== version) throw new Error('package.json version must match release version');
const run = (cmd, args) => execFileSync(cmd, args, { cwd: root, stdio: 'inherit' });
run('npm', ['test']);
run('npm', ['run', 'build']);
const sourceCommit = execFileSync('git', ['rev-parse', 'HEAD'], { encoding: 'utf8' }).trim();
const dirty = execFileSync('git', ['status', '--porcelain'], { encoding: 'utf8' }).trim();
if (dirty) throw new Error('Commit source and evidence before archiving. Immutable release must identify a clean source commit.');
fs.mkdirSync(path.dirname(dest), { recursive: true });
fs.mkdirSync(dest); // Exclusive creation: never merge with a raced existing release.
try {
  fs.cpSync('dist', path.join(dest, 'web'), { recursive: true });
  run('zip', ['-qr', path.join(dest, `${pkg.name}-${version}-web.zip`), 'dist']);
  run('git', ['archive', '--format=zip', `--output=${path.join(dest, `${pkg.name}-${version}-source.zip`)}`, sourceCommit]);
  const desktops = [];
  const freshProvenance = JSON.parse(fs.readFileSync('dist/build-provenance.json','utf8'));
  for (const [dir, platform] of [['linux-unpacked', 'linux-x64'], ['win-unpacked', 'windows-x64']]) {
    const origin = path.join(root, 'build-desktop', dir);
    if (!fs.existsSync(origin)) continue;
    // Match the build's packaged app version before accepting it as this milestone.
    const asar = await import('@electron/asar');
    const packed = JSON.parse(asar.extractFile(path.join(origin, 'resources', 'app.asar'), 'package.json').toString());
    if (packed.version !== version) throw new Error(`Stale ${platform} desktop build: ${packed.version}`);
    const provenance = JSON.parse(asar.extractFile(path.join(origin, 'resources', 'app.asar'), 'dist/build-provenance.json').toString());
    if (provenance.sourceDigest !== freshProvenance.sourceDigest) throw new Error(`Stale ${platform} desktop source; rebuild matching source before release`);
    const archive = path.join(dest, `${pkg.name}-${version}-${platform}.${platform==='windows-x64'?'zip':'tar.gz'}`);
    if (platform==='windows-x64') execFileSync('zip', ['-qr', archive, '.'], {cwd:origin});
    else execFileSync('tar', ['-czf', archive, '-C', origin, '.']);
    desktops.push(platform);
  }
  fs.cpSync('reviews', path.join(dest, 'reviews'), { recursive: true, filter: source => {
    if (source.endsWith('.json') && fs.existsSync(source + '.gz')) {
      const raw = crypto.createHash('sha256').update(fs.readFileSync(source)).digest('hex');
      const packed = crypto.createHash('sha256').update(gunzipSync(fs.readFileSync(source + '.gz'))).digest('hex');
      if (raw !== packed) throw new Error(`Compressed review does not preserve source bytes: ${source}`);
      return false; // Keep the exact lossless compressed evidence, retain raw file locally.
    }
    return true;
  } });
  const archives = fs.readdirSync(dest).filter(f => /\.(zip|tar\.gz)$/.test(f));
  const digests = Object.fromEntries(archives.map(f => [f, crypto.createHash('sha256').update(fs.readFileSync(path.join(dest, f))).digest('hex')]));
  fs.writeFileSync(path.join(dest, 'SHA256SUMS'), Object.entries(digests).map(([f, h]) => `${h}  ${f}\n`).join(''));
  fs.writeFileSync(path.join(dest, 'manifest.json'), JSON.stringify({ version, status: 'development-prerelease', sourceCommit, runtimeSourceDigest:freshProvenance.sourceDigest, createdAt: new Date().toISOString(), platforms: ['web', ...desktops], artifacts: digests, steamPublished: false, reviews: 'See reviews/ for independent findings and promotion decisions; this manifest does not certify commercial quality.' }, null, 2) + '\n');
  console.log(`Archived ${version} at ${dest}`);
} catch (error) {
  // Preserve partial evidence rather than silently deleting a version directory.
  fs.writeFileSync(path.join(dest, 'INCOMPLETE.txt'), String(error) + '\nChoose a fresh version after repair. This directory is not a release.\n');
  throw error;
}
