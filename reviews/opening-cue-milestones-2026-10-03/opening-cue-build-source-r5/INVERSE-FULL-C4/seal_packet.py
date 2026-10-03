"""Own-packet source bookkeeping only; never invoke CI/runtime method phases."""
from pathlib import Path
import hashlib,json,time
ROOT=Path(__file__).parent
SHA=lambda b:hashlib.sha256(b).hexdigest()
def write(name,value):
    (ROOT/name).write_text(json.dumps(value,sort_keys=True,separators=(',',':'))+'\n')
def pins():
    return {p.relative_to(ROOT).as_posix():{'bytes':p.stat().st_size,'sha256':SHA(p.read_bytes())} for p in sorted(ROOT.rglob('*')) if p.is_file() and p.relative_to(ROOT).as_posix() not in ('MANIFEST.json','SOURCE-SEAL.json')}
def main():
    assert all(not p.is_symlink() and (p.is_file() or p.is_dir()) for p in ROOT.rglob('*'))
    checks=json.loads((ROOT/'SOURCE-CHECKS.json').read_bytes());assert checks['status']=='PASS_SOURCE_ONLY'
    meta=(ROOT/'METADATA.json').read_bytes();assert SHA(meta)=='bbc8830505d51278a76f9913ff7d1564c6632fdc32e746b2b6e09417ecbddf17'
    rows=pins()
    write('MANIFEST.json',{'schema':'exact-cue-candidate-build-source-v4','status':'PROPOSED_SOURCE_ONLY_NO_NEW_CI',
      'candidateSourceDigest':'993aa3681596c2488d4d394744e5beda2778ffcba3e1649736612304d20b50c5',
      'focusedParentSourceDigest':'65b31b3f21e34a624bdac962e4919c7dc1791e502eb6cfdb1612103b8036fe9c',
      'candidateMainSHA256':'87a9bd7c2319522f77db7ea9e2edc306bb6124b019306dc220087f6b9b7762f4',
      'sourceCount':104,'supportCount':30,'blobPins':57,'publicCount':65,'expectedOutputCount':70,
      'unchangedMetadataSHA256':SHA(meta),'gameSourceChangedByMethod':False,
      'sharedMethodR9SealSHA256':'59cd0e4c7fb4caf8996650e78798c7ef57317cef3238747a2ed7aef5c18c18ed','sharedMethodR9IndependentGateSHA256':'261b4fa2043b241006c3bae6b18309a2137135bc08ea877dc523941135eab42a',
      'sharedMethodAcceptance':'ROOT_ACCEPTED_SOURCE_ONLY_BEFORE_DERIVATION','adaptationAcceptance':'PENDING_AT_SEAL',
      'oldCMethodSealSHA256':'74d23f566d5f4ed5d4d7af69a3391d968d0581d194ef7888d892861d748b85d6','oldC3IndependentGateSHA256':'8a76292f5940b4d19747add07366c8313955f3a4b0c2a9b85a3564acc01d6901',
      'fullInverse':'Full frozen raw C3 packet19files435065B retained under INVERSE-FULL-C3 and original retained unchanged. Three duplicate full raw C3 runner/workflow/metadata inverse bodies183268B restore exactly; all copied and original bytes verified. All duplicate files counted.',
      'workflowDestination':'.github/workflows/rebuild-opening-cue-candidate.yml',
      'proposedReviewPrefix':'reviews/opening-cue-milestones-2026-10-02/build-method-source-r4/',
      'sourceCapBytes':1048576,'sourceAllowance':'Root authorized NEW C4 SOURCE1MiB before forthcoming closure; no retrospective approval of over-cap R7 or earlier historical packets.',
      'testMemoryAllowance':{'oldBytes':402653184,'newBytes':805306368,'rootAuthorizedRepair':True},'installBuildMemoryBytesUnchanged':402653184,'diskLogTimeReserveNative4096LifecycleInputOutputLimitsUnchanged':True,'originalNpmTestAndEightBodiesUnchanged':True,'rootSoleRemoteWriter':True,
      'actualFailureSite':'Prior actual test supervisors directly recorded sampled aggregate RSS cap, exit-15/closed; partial cancelled suites are not passes and outputs remain unsealed.',
      'noAcquisitionInstallBuildUnitBrowserGameplayExecutedByPacket':True,
      'canonicalAndRetainedStagesWritten':False,'filesExcludingManifestAndSeal':rows,
      'bytesExcludingManifestAndSeal':sum(x['bytes'] for x in rows.values())})
    sealed=dict(rows,**{'MANIFEST.json':{'bytes':(ROOT/'MANIFEST.json').stat().st_size,'sha256':SHA((ROOT/'MANIFEST.json').read_bytes())}})
    write('SOURCE-SEAL.json',{'schema':'source-seal-v1','manifestSHA256':sealed['MANIFEST.json']['sha256'],'sealedFiles':sealed,
      'sourceOnly':True,'independentR9BaseSourceAccepted':True,'independentC4AdaptationReviewPending':True,'actualCBuildAndBehaviorPending':True,'frozenUTCNS':time.time_ns()})
    total=sum(p.stat().st_size for p in ROOT.rglob('*') if p.is_file());assert total<=1048576,total
    print(json.dumps({'sourceBytes':total,'sourceCapBytes':1048576,'manifestSHA256':SHA((ROOT/'MANIFEST.json').read_bytes()),'sealSHA256':SHA((ROOT/'SOURCE-SEAL.json').read_bytes()),'runnerSHA256':SHA((ROOT/'runner.py').read_bytes()),'workflowSHA256':SHA((ROOT/'rebuild-opening-cue-candidate.yml').read_bytes())}))
if __name__=='__main__':main()
