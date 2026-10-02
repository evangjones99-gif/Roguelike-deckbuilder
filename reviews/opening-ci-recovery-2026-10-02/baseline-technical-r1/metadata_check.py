import pathlib,json,hashlib
P=pathlib.Path('/workspace/scratch/empty-intent-fresh-ci-source-r1');O=pathlib.Path('/workspace/scratch/empty-intent-fresh-ci-technical-r1')
def load(p):return json.loads(pathlib.Path(p).read_bytes())
m=load(P/'METADATA.json');a=load('/workspace/scratch/opening-baseline-runtime-map-source-r1/EMPTY-INPUTS98-INDUCED.json');mapping=load('/workspace/scratch/opening-baseline-runtime-map-source-r1/MAP.json');feas=load('/workspace/scratch/empty-intent-fresh-build-feasibility-r1/PROCEDURE.json');b=load('/workspace/scratch/opening-runtime-transfer-source-r2/PINSET.json')
assert len(m['source'])==98 and len(m['support'])==30 and len(m['blobPins'])==53
assert {r['path']:r['sha256'] for r in m['source']}==a
assert hashlib.sha256(json.dumps(a,sort_keys=True,separators=(',',':')).encode()).hexdigest()==m['sourceDigest']=='76e5ba02635900ad242b047f9aa5e11adbc67b9e99f9cb67b35884405d21bc40'
assert {r['path']:(r['sha256'],r['bytes'],r['archive']) for r in m['support']}=={r['path']:(r['expectedSHA256'],r['bytes'],'ce0f') for r in feas['supportPins']}
assert m['tools']==feas['installedToolLockPins'] and m['scripts']==feas['originalScriptPins']
assert not {r['path'] for r in m['source']}&{r['path'] for r in m['support']}
blobs={r['sha256']:r for r in m['blobPins']};assert len(blobs)==53
original_b={r['sha256']:{k:r[k] for k in ['gitPath','gitBlobSHA1','bytes','sha256']} for group in b.values() for r in group}
assert all({k:blobs[h][k] for k in r}==r for h,r in original_b.items())
eight='8cdf546a8429e949fe88611d781aca341566f473135fbcbe44b5373beabd7aa8';assert blobs[eight]['bytes']==5085419 and blobs[eight]['gitBlobSHA1']=='f768057141601502417dc8e31ba7e9cf678b616b'
witness={r['path']:r for r in mapping['emptyInput98InducedMap']}
shared=load('/workspace/scratch/starter-runtime-recovery-map-source-r1/MAP.json')['requiredBodies']
for r in m['source']:
 if 'blob' in r:assert r['blob']==r['sha256'] and blobs[r['blob']]['bytes']==r['bytes']
 else:
  direct=witness[r['path']]['archiveWitnesses']
  additional=[dict(w,sha256=v['expectedSHA256']) for v in shared if v['scope']=='inputs' and v['path']==r['path'] and v['expectedSHA256']==r['sha256'] for w in v['acquisitionReferences'] if w['kind']=='archive-index-hash-witness']
  assert any(w['archive']==r['archive'] and w['sha256']==r['sha256'] and w['bytes']==r['bytes'] and w['member']=='blobs/'+r['sha256'] and w.get('storage')=='newBlob' for w in direct+additional)
r={'draftMetadataOnly':True,'metadataSHA256':hashlib.sha256((P/'METADATA.json').read_bytes()).hexdigest(),'source98ExactMapHashPins':True,'support30ExactFeasibilityPins':True,'all53GitBlobPinsExact':True,'eachSourceBodyExactSizeWitnessOrCanonicalPin':True,'toolAndScriptPinsExactFeasibility':True,'methodOrNetworkExecuted':False,'qualification':'Unsealed draft metadata inspected; rebind final seal/hash at final review. Original map witness is metadata, not full source restoration.'}
(O/'METADATA-PROOF.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
