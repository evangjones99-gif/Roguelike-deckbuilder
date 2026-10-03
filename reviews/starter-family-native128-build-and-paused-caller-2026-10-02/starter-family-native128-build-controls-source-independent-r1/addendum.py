import json,hashlib,resource,os
from pathlib import Path
P=Path(__file__).parent
q=Path('/workspace/scratch/starter-family-native128-materialized-source-root-r1/coherent-native128.ts');fd=os.open(q,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME)
with os.fdopen(fd,'rb') as f:b=f.read()
assert hashlib.sha256(b).hexdigest()=='17b0ae71bd36d9803d5dd4ddea2e8070a200bbe11ea08ada4ad142bd292c42a9'
assert 'if (config.allies > 2 || config.enemies > 2 || !Number.isFinite(ratio) || ratio <= 0) return null;' in b.decode()
gatehash=hashlib.sha256((P/'GATE.json').read_bytes()).hexdigest();assert gatehash=='d13ac39e58c37413ee9ac5ee8889bb03c9379bf5579e0d4491072c6de5c308a5'
x={'scope':'NON_MUTATING_QUALIFICATION_OF_SEALED_STARTER_BUILD_CONTROLS_SOURCE_GATE','gateSHA256':gatehash,'materializedHelperSHA256':hashlib.sha256(b).hexdigest(),'nativeLayoutMaximumAllies':2,'nativeLayoutMaximumEnemies':2,'sourceReadbackLiteralGuardVerified':True,'engineeringDecisionUnchanged':True,'qualification':'Unchanged native128Layout returns null beyond two allies or two enemies although engine summon cap is six. Decoding all13 assets and recognizing starter IDs does not establish all-count native presentation or continuity. Intended later private comparison is firstCairn+Ash at most2 allies, hand Ash/Fen/Briar portraits; existing all-or-baseline admission latch/geometry fallback can retain painted mode. Third binding/native continuity remains a distinct later hypothesis, not covered/approved by these build controls.','runtimeControlsOrOriginalGateMutation':False,'newMatrixOrActualBuildApproval':False,'ownMaxRSSKiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
assert x['ownMaxRSSKiB']<=24576
(P/'SCOPE-ADDENDUM.json').open('x').write(json.dumps(x,separators=(',',':'))+'\n')
assert sum(z.stat().st_size for z in P.rglob('*') if z.is_file())+8192<=131072
print(json.dumps({'addendumSHA256':hashlib.sha256((P/'SCOPE-ADDENDUM.json').read_bytes()).hexdigest(),'unchangedGateSHA256':gatehash,'ownMaxRSSKiB':x['ownMaxRSSKiB']}))
