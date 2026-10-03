"""Own-packet source bookkeeping only; never invoke CI/runtime method phases."""
from pathlib import Path
import hashlib,json,time
ROOT=Path(__file__).parent
SHA=lambda b:hashlib.sha256(b).hexdigest()
def write(name,value):
    (ROOT/name).write_text(json.dumps(value,sort_keys=True,separators=(',',':'))+'\n')
def pins():
    return {p.name:{'bytes':p.stat().st_size,'sha256':SHA(p.read_bytes())} for p in sorted(ROOT.iterdir()) if p.name not in ('MANIFEST.json','SOURCE-SEAL.json')}
def main():
    assert all(p.is_file() and not p.is_symlink() for p in ROOT.iterdir())
    checks=json.loads((ROOT/'SOURCE-CHECKS.json').read_bytes());assert checks['status']=='PASS_SOURCE_ONLY'
    meta=(ROOT/'METADATA.json').read_bytes();assert SHA(meta)=='bbc8830505d51278a76f9913ff7d1564c6632fdc32e746b2b6e09417ecbddf17'
    rows=pins()
    write('MANIFEST.json',{'schema':'exact-cue-candidate-build-source-v2','status':'PROPOSED_SOURCE_ONLY_NO_NEW_CI',
      'candidateSourceDigest':'993aa3681596c2488d4d394744e5beda2778ffcba3e1649736612304d20b50c5',
      'focusedParentSourceDigest':'65b31b3f21e34a624bdac962e4919c7dc1791e502eb6cfdb1612103b8036fe9c',
      'candidateMainSHA256':'87a9bd7c2319522f77db7ea9e2edc306bb6124b019306dc220087f6b9b7762f4',
      'sourceCount':104,'supportCount':30,'blobPins':57,'publicCount':65,'expectedOutputCount':70,
      'unchangedMetadataSHA256':SHA(meta),'gameSourceChangedByMethod':False,
      'sharedMethodR6SealSHA256':'ba7cab54f2083374efb1a9fbd8328bcd6bd6a223a1aa3c08dd201b5a3cd6fdcc',
      'sharedMethodAcceptance':'PENDING_AT_SEAL','adaptationAcceptance':'PENDING_AT_SEAL',
      'oldCMethodSealSHA256':'b2f095b052d6ebad7d28db5c7556c072956fb354d2b8890d72df4d0c00c5c0b8',
      'fullInverse':'Exact old C runner and metadata gzip bodies; full old C workflow gzip template plus complete exact old C runner indentation substitution. All three size/SHA256 identities verified.',
      'workflowDestination':'.github/workflows/rebuild-opening-cue-candidate.yml',
      'proposedReviewPrefix':'reviews/opening-cue-milestones-2026-10-02/build-method-source-r2/',
      'sourceCapBytes':327680,'sourceAllowance':'Root authorized320KiB for this unsealed successor family; no retroactive approval of earlier over-cap packets.',
      'runtimeBudgetsCommandsLifecycleUnchanged':True,'rootSoleRemoteWriter':True,
      'actualFailureSite':'NOT_OBSERVED; source-backed disappearing-entry possibility is inference only.',
      'noAcquisitionInstallBuildUnitBrowserGameplayExecutedByPacket':True,
      'canonicalAndRetainedStagesWritten':False,'filesExcludingManifestAndSeal':rows,
      'bytesExcludingManifestAndSeal':sum(x['bytes'] for x in rows.values())})
    sealed=dict(rows,**{'MANIFEST.json':{'bytes':(ROOT/'MANIFEST.json').stat().st_size,'sha256':SHA((ROOT/'MANIFEST.json').read_bytes())}})
    write('SOURCE-SEAL.json',{'schema':'source-seal-v1','manifestSHA256':sealed['MANIFEST.json']['sha256'],'sealedFiles':sealed,
      'sourceOnly':True,'independentBaseAndCandidateReviewsPending':True,'actualCBuildAndBehaviorPending':True,'frozenUTCNS':time.time_ns()})
    total=sum(p.stat().st_size for p in ROOT.iterdir());assert total<=327680,total
    print(json.dumps({'sourceBytes':total,'sourceCapBytes':327680,'manifestSHA256':SHA((ROOT/'MANIFEST.json').read_bytes()),'sealSHA256':SHA((ROOT/'SOURCE-SEAL.json').read_bytes()),'runnerSHA256':SHA((ROOT/'runner.py').read_bytes()),'workflowSHA256':SHA((ROOT/'rebuild-opening-cue-candidate.yml').read_bytes())}))
if __name__=='__main__':main()
