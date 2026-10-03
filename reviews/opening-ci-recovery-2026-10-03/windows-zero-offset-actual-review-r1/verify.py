"""Read-only local checks of connector-observed Windows log/metadata/source; no artifact execution."""
from pathlib import Path
import hashlib,json,re
P=Path(__file__).parent
meta=json.loads((P/'API-METADATA.json').read_bytes())
run=37079181727;job=111075708058
head='764087166aa9655adfe33e25245c0bb93b14d166'
checkout='1a9a2c91fbc0a1999744fb9243299cf30ecf88ca'
assert meta['run']==run and meta['job']==job and meta['associatedHead']==head and meta['actualCheckout']==checkout
j=meta['jobs']['jobs'];assert len(j)==1 and j[0]['id']==job and j[0]['run_id']==run
assert j[0]['status']=='completed' and j[0]['conclusion']=='success'
assert len(j[0]['steps'])==26 and all(s['status']=='completed' and s['conclusion']=='success' for s in j[0]['steps'])
assert meta['associatedRuns']['workflow_runs'][0]['id']==run and meta['associatedRuns']['workflow_runs'][0]['conclusion']=='success'
artifacts=meta['artifacts']['artifacts'];assert len(artifacts)==10
for a in artifacts:assert a['workflow_run']['id']==run and a['workflow_run']['head_sha']==head
b=(P/'decoded-job.log').read_bytes();text=b.decode('utf-8');lines=text.splitlines()
assert len(b)==79889 and hashlib.sha256(b).hexdigest()=='712474ae3d6ef6e48a7eb29ecbac99e194a2f73437bf62ff4146aea7529f193b'
assert b.startswith(b'\xef\xbb\xbf') and b.count(b'\r\n')==897
assert checkout+':refs/remotes/pull/1/merge' in text and checkout in text
assert 'Merge '+head+' into 98660a7ef214c8a875b25482f64475c8d70e5efc' in text
assert 'Runtime source digest: 64c2a14ada2b24796535f9bb71d8a6acc534685365bcf4f5665b21bf18595353' in text
for value in ['tests 111','pass 111','fail 0','skipped 0']:assert value in text
success='Native Windows packaged launch, branding resources, keyboard focus/repeat guards, portrait, tutorial/combat, persistence and negative-feedback download passed.'
assert success in text and '##[error]Process completed with exit code' not in text
script=(P/'windows-smoke.actual-merge.mjs').read_bytes()
assert hashlib.sha1(f'blob {len(script)}\0'.encode()+script).hexdigest()=='1c098dc824950a0c70ac600ac29f8bae25db337c'
assert all(r['sha']=='1c098dc824950a0c70ac600ac29f8bae25db337c' for r in meta['sourceFetches']) and meta['sourceBodiesEqual']
assert script==Path('/workspace/scratch/windows-opening-smoke-source-r2/windows-smoke.proposed.mjs').read_bytes()
source=script.decode();allowed="assert.ok(['0% 0%', '0px 0px', '0% 0px', '0px 0%'].includes(evidence.portrait.backgroundPosition)"
assert allowed in source and source.index(allowed)<source.index("evidence.status = 'passed'")
assert 'Title hunter crop must stay at zero on both axes' in source
rows=[{'line':n+1,'rawLine':line} for n,line in enumerate(lines) if any(token in line for token in [checkout,'Merge '+head,'Runtime source digest:','ℹ tests','ℹ pass','ℹ fail','ℹ skipped',success,'Microsoft Windows Server 2022','Image: windows-2022'])]
result={'verdict':'ACTUAL_WINDOWS_JOB_AND_ZERO_OFFSET_SMOKE_PASS_QUALIFIED','run':run,'job':job,'associatedHead':head,'actualPR1MergeCheckout':checkout,'mergeBase':'98660a7ef214c8a875b25482f64475c8d70e5efc','runtimeSourceDigestPrinted':'64c2a14ada2b24796535f9bb71d8a6acc534685365bcf4f5665b21bf18595353','all26ReceivedStepSummariesSuccess':True,'ruleTests':{'tests':111,'passed':111,'failed':0,'skipped':0},'zeroOffsetAllowlistInExactTestedSource':True,'actualSerializedPositionPrinted':False,'receivedArtifactMetadataCount':10,'artifactBodyDownloads':0,'decodedLogBytes':len(b),'decodedLogSHA256':hashlib.sha256(b).hexdigest(),'decodedBOMAndCRLFRetained':True,'scriptSHA256':hashlib.sha256(script).hexdigest(),'scriptGitBlobSHA1':'1c098dc824950a0c70ac600ac29f8bae25db337c','exactSourceProposalMatch':True,'selectedEvidenceLines':rows,'qualification':'Decoded UTF8 bytes only, not original HTTP log archive. Metadata wrappers first page/latest jobs. Actual hosted Windows job reported success; artifact package/smoke.json/resources/captures not downloaded or independently audited. No broad/native readiness, release, default, art, gameplay or human-fun acceptance. B/C private build not tested: printed runtime64c2.'}
with (P/'CHECKS.json').open('x') as f:json.dump(result,f,indent=2,sort_keys=True);f.write('\n')
print(json.dumps({k:result[k] for k in ['verdict','run','job','decodedLogBytes']}))
