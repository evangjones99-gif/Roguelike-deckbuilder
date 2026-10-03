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
    write('MANIFEST.json',{'schema':'exact-cue-candidate-build-source-v3','status':'PROPOSED_SOURCE_ONLY_NO_NEW_CI',
      'candidateSourceDigest':'993aa3681596c2488d4d394744e5beda2778ffcba3e1649736612304d20b50c5',
      'focusedParentSourceDigest':'65b31b3f21e34a624bdac962e4919c7dc1791e502eb6cfdb1612103b8036fe9c',
      'candidateMainSHA256':'87a9bd7c2319522f77db7ea9e2edc306bb6124b019306dc220087f6b9b7762f4',
      'sourceCount':104,'supportCount':30,'blobPins':57,'publicCount':65,'expectedOutputCount':70,
      'unchangedMetadataSHA256':SHA(meta),'gameSourceChangedByMethod':False,
      'sharedMethodR8SealSHA256':'06a21194db443ea1d03165ee5b69e1a378ce5120bfee466c52ff9a9ff8644c35','sharedMethodR8IndependentGateSHA256':'11b8facb99e9957da95a24835eb0a86ef73ff97e360be03ee6705b0d2c29739e',
      'sharedMethodAcceptance':'ROOT_ACCEPTED_SOURCE_ONLY_BEFORE_DERIVATION','adaptationAcceptance':'PENDING_AT_SEAL',
      'oldCMethodSealSHA256':'1082268d8489252d23c69b12dcb04d6157c29dce1bf09561d530001ff9474c43',
      'fullInverse':'Three complete raw old C2 runner/workflow/metadata bodies; all full sizes/SHA256 identities verified. Entire frozen old C2 packet19files274135B also verified unchanged.',
      'workflowDestination':'.github/workflows/rebuild-opening-cue-candidate.yml',
      'proposedReviewPrefix':'reviews/opening-cue-milestones-2026-10-02/build-method-source-r3/',
      'sourceCapBytes':655360,'sourceAllowance':'Root authorized NEW C3 SOURCE640KiB before forthcoming closure; no retrospective approval of over-cap R7 or earlier historical packets.',
      'memoryDiskLogTimeLifecycleInputOutputLimitsUnchanged':True,'nativeAuditFileCountAllowance':{'old':100,'new':4096,'scope':'Three fixed selected Linux x64 native packages','rootAuthorizedRepair':True},'rootSoleRemoteWriter':True,
      'actualFailureSite':'Generic inventory count cap observed after diagnostic06 @typescript native; prior cap100 branch is source/order inference only. No retained traceback observes exact callsite.',
      'noAcquisitionInstallBuildUnitBrowserGameplayExecutedByPacket':True,
      'canonicalAndRetainedStagesWritten':False,'filesExcludingManifestAndSeal':rows,
      'bytesExcludingManifestAndSeal':sum(x['bytes'] for x in rows.values())})
    sealed=dict(rows,**{'MANIFEST.json':{'bytes':(ROOT/'MANIFEST.json').stat().st_size,'sha256':SHA((ROOT/'MANIFEST.json').read_bytes())}})
    write('SOURCE-SEAL.json',{'schema':'source-seal-v1','manifestSHA256':sealed['MANIFEST.json']['sha256'],'sealedFiles':sealed,
      'sourceOnly':True,'independentR8BaseSourceAccepted':True,'independentC3AdaptationReviewPending':True,'actualCBuildAndBehaviorPending':True,'frozenUTCNS':time.time_ns()})
    total=sum(p.stat().st_size for p in ROOT.iterdir());assert total<=655360,total
    print(json.dumps({'sourceBytes':total,'sourceCapBytes':655360,'manifestSHA256':SHA((ROOT/'MANIFEST.json').read_bytes()),'sealSHA256':SHA((ROOT/'SOURCE-SEAL.json').read_bytes()),'runnerSHA256':SHA((ROOT/'runner.py').read_bytes()),'workflowSHA256':SHA((ROOT/'rebuild-opening-cue-candidate.yml').read_bytes())}))
if __name__=='__main__':main()
