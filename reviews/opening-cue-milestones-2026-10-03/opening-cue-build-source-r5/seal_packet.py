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
    meta=(ROOT/'METADATA.json').read_bytes();assert SHA(meta)=='5c8cd7ba6b1ab63fa61bbe62c534e786fcdf76cf0ff8f2fb54dc58be14ab2694'
    rows=pins()
    write('MANIFEST.json',{'schema':'exact-cue-candidate-build-source-v5','status':'PROPOSED_SOURCE_ONLY_NO_NEW_CI',
      'candidateSourceDigest':'993aa3681596c2488d4d394744e5beda2778ffcba3e1649736612304d20b50c5',
      'focusedParentSourceDigest':'65b31b3f21e34a624bdac962e4919c7dc1791e502eb6cfdb1612103b8036fe9c',
      'candidateMainSHA256':'87a9bd7c2319522f77db7ea9e2edc306bb6124b019306dc220087f6b9b7762f4',
      'sourceCount':104,'supportCount':32,'blobPins':59,'directBlobPins':56,'stageInputCount':136,'publicCount':65,'expectedOutputCount':70,
      'candidateMetadataSHA256':SHA(meta),'oldC4MetadataSHA256':'bbc8830505d51278a76f9913ff7d1564c6632fdc32e746b2b6e09417ecbddf17','onlyMetadataRowsAdded':'Two exact original fixture support rows plus their direct Gitpins; all other metadata fields and original134stage bodies/57pins retained.','gameSourceChangedByMethod':False,
      'sharedMethodR10SealSHA256':'83188dc11eb1259cc961cf38e69cc7232040d08d6a7f209e5f817e599872f4bc','sharedMethodR10IndependentGateSHA256':'664f78f61f5669c4c2870ca629e228fa944087727384268b95aa66f68d671aee',
      'sharedMethodAcceptance':'ROOT_ACCEPTED_SOURCE_ONLY_BEFORE_DERIVATION','adaptationAcceptance':'PENDING_AT_SEAL',
      'oldCMethodSealSHA256':'8581a39c88c3ce906678fad6392e14ea080dfeb4a338064e7983ea65f26d560c','oldC4IndependentGateSHA256':'1a19b4c0666e7a4cb56eaa0410e3b89d151c799d196c09b927e330d846ee6a5b',
      'fullInverse':'Full frozen raw C4 packet recursive39files893061B retained under INVERSE-FULL-C4 and original retained unchanged. Three duplicate full raw C4 runner/workflow/metadata inverse bodies183268B restore exactly; all copied and original bytes verified. All duplicate files counted.',
      'workflowDestination':'.github/workflows/rebuild-opening-cue-candidate.yml',
      'proposedReviewPrefix':'reviews/opening-cue-milestones-2026-10-02/build-method-source-r5/',
      'sourceCapBytes':2097152,'sourceAllowance':'Root authorized NEW C5 SOURCE2MiB before forthcoming closure; no retrospective approval of over-cap R7 or earlier historical packets.',
      'testMemoryBytesUnchanged':805306368,'fixtureClosureAllowance':{'support':[30,32],'stage':[134,136],'directBlobs':[54,56],'allBlobs':[57,59],'exactOriginalFixturesSHA256':'2e4e82387617f1a013d159869a8a1facd20c4b4f6728501c6f43da4616c714da'},'installBuildMemoryBytesUnchanged':402653184,'diskLogTimeReserveNative4096LifecycleSourceOutputLimitsUnchanged':True,'originalNpmTestAndEightBodiesUnchanged':True,'rootSoleRemoteWriter':True,
      'actualFailureSite':'Prior tests completed within768MiB with exit1/reasonnull/cleanclosure;107tests104pass3fail0cancelled, all3 directENOENT for two exactoriginalfixture paths. No output sealed or caller eligible.',
      'noAcquisitionInstallBuildUnitBrowserGameplayExecutedByPacket':True,
      'canonicalAndRetainedStagesWritten':False,'filesExcludingManifestAndSeal':rows,
      'bytesExcludingManifestAndSeal':sum(x['bytes'] for x in rows.values())})
    sealed=dict(rows,**{'MANIFEST.json':{'bytes':(ROOT/'MANIFEST.json').stat().st_size,'sha256':SHA((ROOT/'MANIFEST.json').read_bytes())}})
    write('SOURCE-SEAL.json',{'schema':'source-seal-v1','manifestSHA256':sealed['MANIFEST.json']['sha256'],'sealedFiles':sealed,
      'sourceOnly':True,'independentR10BaseSourceAccepted':True,'independentC5AdaptationReviewPending':True,'actualCBuildAndBehaviorPending':True,'frozenUTCNS':time.time_ns()})
    total=sum(p.stat().st_size for p in ROOT.rglob('*') if p.is_file());assert total<=2097152,total
    print(json.dumps({'sourceBytes':total,'sourceCapBytes':2097152,'manifestSHA256':SHA((ROOT/'MANIFEST.json').read_bytes()),'sealSHA256':SHA((ROOT/'SOURCE-SEAL.json').read_bytes()),'runnerSHA256':SHA((ROOT/'runner.py').read_bytes()),'workflowSHA256':SHA((ROOT/'rebuild-opening-cue-candidate.yml').read_bytes())}))
if __name__=='__main__':main()
