/** Prespecified evolutionary policy research. Synthetic outcomes never label human fun. */
import { createGame, applyAction, legalActions, validateState, CARDS,
  type GameState, type Action } from '../src/engine';
import { createHash } from 'node:crypto';
import { mkdirSync, writeFileSync, appendFileSync, existsSync, readFileSync,
  copyFileSync, readdirSync, constants } from 'node:fs';
import { dirname, join } from 'node:path';

const sources = ['src/engine.ts', 'src/content.ts', 'src/world-rng.ts', 'scripts/learn-policy.ts'];
const digest = (bytes: string | Buffer) => createHash('sha256').update(bytes).digest('hex');
const sourceHash = (path: string) => digest(readFileSync(path));
const hashes = () => Object.fromEntries(sources.map(path => [path, sourceHash(path)]));
const trainSeeds = Array.from({ length: 16 }, (_, i) => 46101 + i);
const testSeeds = Array.from({ length: 96 }, (_, i) => 47101 + i);
const baseWeights = [2.8, 4.5, 2.2, 0.65, 0.9, 0.3, -0.8, 3];
const featureNames = ['enemyHpReduction', 'hunterHpChange', 'companionAttackChange',
  'companionHpChange', 'effectiveHunterBlockChange', 'energyChange', 'endTurn', 'terminalProgress'];
const args = process.argv.slice(2), mode = args[0]?.startsWith('--') ? args.shift() : '--run';
const output = args[0] ?? 'reviews/ml-policy-0.5-r1';
if (!['--run', '--plan-only', '--execute-plan'].includes(mode!)) throw Error('Unknown experiment mode');
function writeNew(name: string, value: unknown) {
  writeFileSync(join(output, name), JSON.stringify(value, null, 2) + '\n', { flag: 'wx' });
}
function makePlan() {
  if (existsSync(output)) throw Error('Refusing any existing experiment directory: ' + output);
  const plan = {
    revision: 1, method: 'seeded six-generation/six-mutant linear evolutionary search',
    saveSchema: 3, rulesGeneration: 2, difficulty: 1, trainSeeds, testSeeds,
    generations: 6, mutantsPerGeneration: 6, mutationSeed: 38291,
    actionRandomness: 'episode-local xorshift32 seeded (runSeed XOR 0x51ab19c9), zero replaced by one; independent of mutation RNG',
    baseWeights, features: featureNames, maxAcceptedActionsPerEpisode: 700,
    objective: '(win ? 100 : 0) + floor*3 + hp*0.1 - acceptedActions*0.002',
    evaluation: ['legal-random', 'base-linear', 'frozen-learned-linear'],
    preregisteredComparison: 'Report completion, HP, turns, steps, stalls, paired rescues/new losses and all invalid-state/source failures. No nonregression or human-fun threshold.',
    rulesSourceHashes: hashes(),
    scope: 'Frozen rules provenance only. Main/art/CSS and final graphical build digest are not part of this experiment.',
    limitations: ['One difficulty, one starting collection and one fixed noncombat linear-policy procurement rule.',
      'Random actions are a weak synthetic baseline, not a human comparator.',
      'Transition scoring uses a detached reducer preview; no human preferences or synthetic fun labels.',
      'No automatic rules, prices or economy changes are authorized by outcomes.'],
  };
  mkdirSync(output, { recursive: true });
  writeNew('plan.json', plan); // Before any source snapshot or episode.
  for (const file of sources) {
    const destination = join(output, 'source', file);
    mkdirSync(dirname(destination), { recursive: true });
    copyFileSync(file, destination, constants.COPYFILE_EXCL);
  }
  writeFileSync(join(output, 'source/package.json'), '{"type":"module","private":true}\n', { flag: 'wx' });
  return plan;
}
function files(path: string): string[] {
  return readdirSync(path, { withFileTypes: true }).flatMap(entry => entry.isDirectory()
    ? files(join(path, entry.name)) : [join(path, entry.name)]);
}
const plan = mode === '--execute-plan'
  ? JSON.parse(readFileSync(join(output, 'plan.json'), 'utf8')) as ReturnType<typeof makePlan>
  : makePlan();
if (mode === '--plan-only') {
  console.log(JSON.stringify({ output, plannedOnly: true, rulesSourceHashes: plan.rulesSourceHashes }));
  process.exit(0);
}
// Execution may consume only its pristine, source-matching plan once. Partial runs stay immutable.
const expected = [join(output, 'plan.json'), join(output, 'source/package.json'),
  ...sources.map(file => join(output, 'source', file))].sort();
if (JSON.stringify(files(output).sort()) !== JSON.stringify(expected))
  throw Error('Refusing nonpristine experiment output or prior execution');
if (plan.saveSchema !== 3 || plan.rulesGeneration !== 2 ||
    JSON.stringify(plan.trainSeeds) !== JSON.stringify(trainSeeds) ||
    JSON.stringify(plan.testSeeds) !== JSON.stringify(testSeeds) ||
    plan.generations !== 6 || plan.mutantsPerGeneration !== 6 || plan.difficulty !== 1 ||
    plan.mutationSeed !== 38291 || plan.maxAcceptedActionsPerEpisode !== 700 ||
    plan.objective !== '(win ? 100 : 0) + floor*3 + hp*0.1 - acceptedActions*0.002' ||
    JSON.stringify(plan.baseWeights) !== JSON.stringify(baseWeights) ||
    JSON.stringify(plan.features) !== JSON.stringify(featureNames)) throw Error('Plan contract mismatch');
function guardSources() {
  for (const source of sources) {
    if (sourceHash(source) !== plan.rulesSourceHashes[source] ||
        sourceHash(join(output, 'source', source)) !== plan.rulesSourceHashes[source])
      throw Error('Frozen source changed: ' + source);
  }
}
guardSources();
const planHash = sourceHash(join(output, 'plan.json'));
writeNew('execution-started.json', { planHash, scriptHash: sourceHash('scripts/learn-policy.ts'),
  nodeVersion: process.version, rulesSourceHashes: plan.rulesSourceHashes });
for (const name of ['training-episodes.jsonl', 'failures.jsonl'])
  writeFileSync(join(output, name), '', { flag: 'wx' });
function randomStream(initial: number) {
  let rng = initial >>> 0 || 1;
  return () => { rng ^= rng << 13; rng ^= rng >>> 17; rng ^= rng << 5; return (rng >>> 0) / 4294967296; };
}
const mutationRandom = randomStream(38291);
const sum = (s: GameState, field: 'hp' | 'attack') => s.allies.reduce((n, u) => n + u[field], 0);
const enemyHp = (s: GameState) => s.enemies.reduce((n, u) => n + u.hp, 0);
const incoming = (s: GameState) => s.enemies.reduce((n, u) => n +
  (u.intent?.target === 'hunter' || u.intent?.target === 'all' ? u.intent.damage : 0), 0);
function features(s: GameState, a: Action, n: GameState): number[] {
  const remainsBattle = n.phase === 'battle';
  return [(enemyHp(s) - (remainsBattle ? enemyHp(n) : 0)) / 10, (n.hp - s.hp) / 10,
    remainsBattle ? (sum(n, 'attack') - sum(s, 'attack')) / 5 : 0,
    remainsBattle ? (sum(n, 'hp') - sum(s, 'hp')) / 15 : 0,
    remainsBattle ? (Math.min(n.block, incoming(s)) - Math.min(s.block, incoming(s))) / 10 : 0,
    remainsBattle ? (n.energy - s.energy) / 5 : 0, a.type === 'endTurn' ? 1 : 0,
    n.phase === 'reward' || n.phase === 'victory' ? 1 : n.phase === 'defeat' ? -2 : 0];
}
function cardValue(a: Action): number {
  if (a.type !== 'reward' || a.card === null) return 0;
  const c = CARDS[a.card];
  return c.type === 'summon' ? (c.attack ?? 0) * 2 + (c.hp ?? 0) * 0.25 - c.cost * 0.5 :
    ({ rally: 15, communion: 14, ready: 13, pack: 11, siphon: 10, aoe: 8, draw: 7,
      block: 4, damage: 5, energy: 1, heal: 3, shelter: 5 }[c.effect as 'rally'] ?? 4);
}
function outside(s: GameState, actions: Action[]): Action {
  if (s.phase === 'map') return actions.find(a => a.type === 'travel' && a.choice === 'camp') ??
    actions.find(a => a.type === 'travel' && a.choice === 'battle') ?? actions[0];
  if (s.phase === 'camp') return actions.find(a => a.type === 'camp' &&
    a.choice === (s.hp < s.maxHp - 14 ? 'rest' : 'train')) ?? actions[0];
  if (s.phase === 'event') return actions.find(a => a.type === 'event' && a.choice === 'forage') ?? actions[0];
  if (s.phase === 'shop') return actions.find(a => a.type === 'leave') ?? actions[0];
  if (s.phase === 'reward') {
    if (s.deck.length >= 19) return actions.find(a => a.type === 'reward' && a.card === null)!;
    return actions.slice().sort((a, b) => cardValue(b) - cardValue(a))[0];
  }
  return actions[0];
}
function choose(s: GameState, w: readonly number[], random: (() => number) | null): Action {
  const actions = legalActions(s);
  if (random) return actions[Math.floor(random() * actions.length)];
  if (s.phase !== 'battle') return outside(s, actions);
  let chosen = actions[0], best = -Infinity;
  for (const a of actions) {
    const n = applyAction(s, a);
    if (n === s || !validateState(n)) throw Error('Invalid legal preview');
    const f = features(s, a, n);
    let score = f.reduce((value, x, i) => value + x * w[i], 0);
    if (a.type === 'attack') score += 0.15;
    if (score > best) { best = score; chosen = a; }
  }
  return chosen;
}
type Episode = { seed: number; saveSchema: 3; rulesGeneration: 2; phase: string; win: boolean;
  floor: number; hp: number; steps: number; turns: number; cards: number; damage: number;
  stalled: boolean; failure: null; score: number; trajectorySha256: string; randomActionSeed: number | null };
function episode(seed: number, w: readonly number[], randomMode = false): Episode {
  guardSources();
  let s = createGame(seed, 1), steps = 0;
  if (!validateState(s) || s.schema !== 3 || s.engineKind !== 2)
    throw Error('Invalid initial generation at seed ' + seed);
  const actionSeed = (seed ^ 0x51ab19c9) >>> 0 || 1;
  const random = randomMode ? randomStream(actionSeed) : null;
  const trajectory = createHash('sha256').update(JSON.stringify(s));
  while (s.phase !== 'victory' && s.phase !== 'defeat' && steps < 700) {
    const actions = legalActions(s); if (!actions.length) break;
    const before = JSON.stringify(s), a = choose(s, w, random), n = applyAction(s, a);
    if (n === s || JSON.stringify(s) !== before || !validateState(n) ||
        n.schema !== 3 || n.engineKind !== 2) throw Error('Invalid accepted state at seed ' + seed + ' action ' + steps);
    trajectory.update(JSON.stringify({ action: a, state: n }));
    s = n; steps++;
  }
  const win = s.phase === 'victory';
  return { seed, saveSchema: 3, rulesGeneration: 2, phase: s.phase, win, floor: s.floor,
    hp: s.hp, steps, turns: s.stats.turns, cards: s.stats.cardsPlayed, damage: s.stats.damageDealt,
    stalled: s.phase !== 'victory' && s.phase !== 'defeat', failure: null,
    score: (win ? 100 : 0) + s.floor * 3 + s.hp * 0.1 - steps * 0.002,
    trajectorySha256: trajectory.digest('hex'), randomActionSeed: randomMode ? actionSeed : null };
}
let context: Record<string, unknown> = { stage: 'initial' };
try {
  const mean = (e: Episode[]) => e.reduce((n, x) => n + x.score, 0) / e.length;
  function training(w: number[], generation: number, candidate: number): Episode[] {
    const weightsSha256 = digest(JSON.stringify(w));
    return trainSeeds.map(seed => {
      context = { stage: 'training', generation, candidate, seed, weightsSha256 };
      const e = episode(seed, w);
      appendFileSync(join(output, 'training-episodes.jsonl'), JSON.stringify({ ...context, ...e }) + '\n');
      return e;
    });
  }
  let learned = baseWeights.slice(), best = mean(training(learned, 0, -1));
  const history = [{ generation: 0, trainingScore: best, weights: learned.slice() }];
  for (let generation = 1; generation <= 6; generation++) {
    const center = learned.slice();
    for (let candidate = 0; candidate < 6; candidate++) {
      const w = center.map(x => Math.max(-6, Math.min(8,
        x + (mutationRandom() * 2 - 1) * (1.6 / generation + 0.2))));
      const score = mean(training(w, generation, candidate));
      if (score > best) { best = score; learned = w; }
    }
    history.push({ generation, trainingScore: best, weights: learned.slice() });
    console.log('Generation ' + generation + ': training score ' + best.toFixed(3));
  }
  guardSources();
  const frozenWeights = Object.freeze(learned.slice());
  writeNew('policy.json', { kind: 'linear-transition-policy', features: featureNames,
    weights: frozenWeights, trainingSeeds: trainSeeds, mutationSeed: 38291,
    saveSchema: 3, rulesGeneration: 2, planHash, rulesSourceHashes: plan.rulesSourceHashes });
  const policySha256 = sourceHash(join(output, 'policy.json'));
  function evaluate(name: string, w: readonly number[], random = false): Episode[] {
    return testSeeds.map(seed => {
      context = { stage: 'evaluation', policy: name, seed };
      if (sourceHash(join(output, 'policy.json')) !== policySha256) throw Error('Frozen policy changed');
      return episode(seed, w, random);
    });
  }
  const results = { random: evaluate('random', baseWeights, true),
    heuristic: evaluate('base-linear', baseWeights), learned: evaluate('learned', frozenWeights) };
  const summaries = Object.fromEntries(Object.entries(results).map(([name, episodes]) => [name, {
    episodes: episodes.length, wins: episodes.filter(e => e.win).length,
    winRate: episodes.filter(e => e.win).length / episodes.length,
    meanFloor: episodes.reduce((n, e) => n + e.floor, 0) / episodes.length,
    meanHpIncludingDefeats: episodes.reduce((n, e) => n + e.hp, 0) / episodes.length,
    meanSteps: episodes.reduce((n, e) => n + e.steps, 0) / episodes.length,
    meanTurns: episodes.reduce((n, e) => n + e.turns, 0) / episodes.length,
    stalled: episodes.filter(e => e.stalled).length, failures: 0,
  }]));
  const rescuedSeeds = testSeeds.filter((_, i) => !results.heuristic[i].win && results.learned[i].win),
    newlyLostSeeds = testSeeds.filter((_, i) => results.heuristic[i].win && !results.learned[i].win);
  guardSources();
  if (sourceHash(join(output, 'policy.json')) !== policySha256) throw Error('Frozen policy changed after evaluation');
  const dataset = JSON.stringify(results, null, 2) + '\n';
  writeFileSync(join(output, 'episodes.json'), dataset, { flag: 'wx' });
  writeNew('report.json', { method: plan.method, saveSchema: 3, rulesGeneration: 2,
    objective: plan.objective, planSha256: planHash, policySha256,
    rulesSourceHashes: plan.rulesSourceHashes, datasetSha256: digest(dataset),
    trainingDatasetSha256: sourceHash(join(output, 'training-episodes.jsonl')),
    trainSeeds, testSeeds, trainingEpisodes: 592, evaluationEpisodes: 288,
    history, summaries, pairedLearnedVsBase: { rescuedSeeds, newlyLostSeeds },
    failures: 0, sourceGuardPassed: true, limitations: plan.limitations });
  console.log(JSON.stringify(summaries, null, 2));
} catch (error) {
  const currentSourceHashes = Object.fromEntries(sources.map(path => {
    try { return [path, sourceHash(path)]; }
    catch (readError) { return [path, 'unreadable: ' + String(readError)]; }
  }));
  const failure = { ...context, message: String(error), currentSourceHashes };
  appendFileSync(join(output, 'failures.jsonl'), JSON.stringify(failure) + '\n');
  writeNew('failed-run.json', { failure, planHash,
    instruction: 'Keep this partial output immutable. A new experiment requires a new directory.' });
  throw error;
}
