"""Independent read-only reaggregation; does not rerun or adopt the learned policy."""
import hashlib
import json
from pathlib import Path

p = Path('reviews/ml-policy-0.5-r1')
report = json.loads((p/'report.json').read_text())
episodes = json.loads((p/'episodes.json').read_text())
plan = json.loads((p/'plan.json').read_text())
hashes = {}
for name, key in [('episodes.json', 'datasetSha256'), ('training-episodes.jsonl', 'trainingDatasetSha256'), ('plan.json', 'planSha256'), ('policy.json', 'policySha256')]:
    hashes[name] = hashlib.sha256((p/name).read_bytes()).hexdigest()
    assert hashes[name] == report[key]
training = [json.loads(line) for line in (p/'training-episodes.jsonl').read_text().splitlines()]
assert len(training) == 592
assert set(plan['trainSeeds']).isdisjoint(plan['testSeeds'])
summaries = {}
for policy, rows in episodes.items():
    assert len(rows) == 96
    assert [r['seed'] for r in rows] == list(range(47101, 47197))
    for r in rows:
        assert r['saveSchema'] == 3 and r['rulesGeneration'] == 2
        assert r['phase'] in ['victory', 'defeat'] and not r['stalled'] and r['failure'] is None
        expected = (100 if r['win'] else 0) + r['floor']*3 + r['hp']*.1 - r['steps']*.002
        assert abs(expected-r['score']) < 1e-8
    summaries[policy] = dict(wins=sum(r['win'] for r in rows), meanHp=sum(r['hp'] for r in rows)/96,
                            meanActions=sum(r['steps'] for r in rows)/96, meanTurns=sum(r['turns'] for r in rows)/96)
    for field, column in [('wins','wins'), ('meanHp','meanHpIncludingDefeats'), ('meanActions','meanSteps'), ('meanTurns','meanTurns')]:
        assert abs(summaries[policy][field]-report['summaries'][policy][column]) < 1e-8
base = {r['seed']: r for r in episodes['heuristic']}
learned = {r['seed']: r for r in episodes['learned']}
rescues = [s for s in base if not base[s]['win'] and learned[s]['win']]
losses = [s for s in base if base[s]['win'] and not learned[s]['win']]
assert rescues == [47179] and losses == []
trade = json.loads((p/'paired-tradeoffs.json').read_text())
both = [s for s in base if base[s]['win'] and learned[s]['win']]
assert len(both) == trade['bothWinningPairs'] == 95
for name, predicate in [('lowerFinalHpSeeds', lambda a,b:b['hp']<a['hp']), ('higherFinalHpSeeds',lambda a,b:b['hp']>a['hp']),
                        ('sameFinalHpSeeds',lambda a,b:b['hp']==a['hp']), ('moreActionsSeeds',lambda a,b:b['steps']>a['steps']),
                        ('moreTurnsSeeds',lambda a,b:b['turns']>a['turns'])]:
    assert [s for s in both if predicate(base[s], learned[s])] == trade[name]
for file, h in report['rulesSourceHashes'].items():
    assert hashlib.sha256(Path(file).read_bytes()).hexdigest() == h
out = Path('reviews/gameplay-v0.5-runtime/ml-independent-reaggregation.json')
assert not out.exists()
out.write_text(json.dumps(dict(
    method='Independent read-only reaggregation, not a new simulation or mutation-search reproduction.',
    qualification='One difficulty, collection and procurement policy; no human fun measure or runtime ML adoption.',
    inputHashes=hashes, sourceHashes=report['rulesSourceHashes'], trainingRows=592, evaluationRows=288,
    disjointSeedRanges=True, allDeclaredSummaryFieldsRecomputed=True, allEvaluationObjectiveValuesRecomputed=True,
    summaries=summaries, rescues=rescues, newLosses=losses, tradeoffCohort='95 pairs in which both policies win',
    lowerFinalHpSeeds=trade['lowerFinalHpSeeds'], moreActionsSeeds=trade['moreActionsSeeds'],
    negativeInterpretation='One extra win, but26 both-winning seeds have lower final HP; overall mean actions/turns rise. Not a universal improvement.'
), indent=2)+'\n')
print(json.dumps(dict(summaries=summaries, rescues=rescues, newLosses=losses)))
