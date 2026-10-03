import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { sha256File } from './sha256-file.mjs';
import { reviewIndex } from './review-index.mjs';

const version = process.argv[2];
if (!version || !/^\d+\.\d+\.\d+(?:-[a-z0-9.]+)?$/.test(version)) throw new Error('Usage: npm run release -- 0.1.0');
const optional = process.argv.slice(3);
if (optional.length > 1 || (optional.length === 1 && optional[0] !== '--source-format=bundle')) throw new Error('Only the fixed opt-in --source-format=bundle is supported; omit it for unchanged ZIP mode');
const sourceFormat = optional.length ? 'bundle' : 'zip';
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
  // Retain old milestones in place. The current source needs its canonical
  // reviews/assets, rather than recursively bundling prior release copies.
  const sourceRoots = execFileSync('git', ['ls-tree', '-z', '--name-only', sourceCommit], {encoding: 'utf8'})
    .split('\0').filter(entry => entry && entry !== 'releases');
  if (!sourceRoots.length) throw new Error('Source archive has no included tracked roots');
  let bundleIndex = null;
  if (sourceFormat === 'bundle') {
    const {createSourceBundle} = await import('./source-bundle.mjs');
    bundleIndex = await createSourceBundle(root,sourceCommit,dest,pkg.name,version,sourceRoots);
  } else {
    run('git', ['archive', '--format=zip', `--output=${path.join(dest, `${pkg.name}-${version}-source.zip`)}`, sourceCommit, '--', ...sourceRoots]);
  }
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
    // Retain validation of every present desktop; bundle mode uses only the
    // separately accepted original native Windows ZIP, never a new repack.
    if (sourceFormat === 'bundle' && platform === 'windows-x64') continue;
    const archive = path.join(dest, `${pkg.name}-${version}-${platform}.${platform==='windows-x64'?'zip':'tar.gz'}`);
    if (platform==='windows-x64') execFileSync('zip', ['-qr', archive, '.'], {cwd:origin});
    else execFileSync('tar', ['-czf', archive, '-C', origin, '.']);
    desktops.push(platform);
  }
  const evidenceIndex = bundleIndex ?? await reviewIndex(root, sourceCommit, path.join(dest, `${pkg.name}-${version}-source.zip`));
  fs.mkdirSync(path.join(dest,'reviews'));
  fs.writeFileSync(path.join(dest,'reviews','INDEX.json'),JSON.stringify(evidenceIndex,null,2)+'\n');
  const archives = fs.readdirSync(dest).filter(f => /\.(zip|tar\.gz)$/.test(f) || (sourceFormat === 'bundle' && /-source\.bundle$/.test(f)));
  const digests = Object.fromEntries(await Promise.all(archives.map(async f => [f, await sha256File(path.join(dest, f))])));
  fs.writeFileSync(path.join(dest, 'SHA256SUMS'), Object.entries(digests).map(([f, h]) => `${h}  ${f}\n`).join(''));
  fs.writeFileSync(path.join(dest, 'manifest.json'), JSON.stringify({ version, status: 'development-prerelease', sourceCommit, runtimeSourceDigest:freshProvenance.sourceDigest, ...(sourceFormat === 'bundle' ? {sourceArchiveFormat:'git-bundle-v2',sourceBundleVerification:'source-bundle-verification.json',archivePlan:'Producer stores web ZIP, source bundle and available validated Linux tar. Root separately adds the accepted original native Windows ZIP and original CI evidence, producing five archives; this producer does not invent native proof or repack Windows.'} : {}),sourceArchiveScope: sourceFormat === 'bundle' ? 'Exact current complete Git tree and all commit/tree/blob ancestry reachable only from pinned HEAD/production branch, independently restored and fsck/blob verified. Other refs/annotated tags, non-ancestor rejected experiments and working files are excluded. Temporary same-commit ZIP used only for canonical review auditing; no official source ZIP is claimed.' : 'All tracked top-level entries except releases/. Canonical reviews, art inputs, datasets and game/build sources are included. Prior milestones remain unchanged at their original paths and commits.', createdAt: new Date().toISOString(), platforms: ['web', ...desktops], artifacts: digests, steamPublished: false, reviews: 'See reviews/INDEX.json and canonical reviews/ in the source commit/archive. Prior full local milestone copies remain unchanged. This manifest does not certify commercial quality.' }, null, 2) + '\n');
  console.log(`Archived ${version} at ${dest}`);
} catch (error) {
  // Preserve partial evidence rather than silently deleting a version directory.
  fs.writeFileSync(path.join(dest, 'INCOMPLETE.txt'), String(error) + '\nChoose a fresh version after repair. This directory is not a release.\n');
  throw error;
}
