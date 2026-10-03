"""Root-only future fresh thirteen-sprite starter assembly; import has no side effects."""
from pathlib import Path
import argparse,hashlib,json,os,shutil
P=Path(__file__).parent
STAGE=Path('/workspace/scratch/starter-family-native128-stage-r1')
def require(ok,message):
    if not ok:raise ValueError(message)
def data(path):
    # Resolve held leaf aliases only for reads. No alias/body mutation.
    resolved=Path(path).resolve(strict=True)
    fd=os.open(resolved,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW)
    with os.fdopen(fd,'rb') as f:return f.read()
def sha(path):
    resolved=Path(path).resolve(strict=True);h=hashlib.sha256()
    fd=os.open(resolved,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW)
    with os.fdopen(fd,'rb') as f:
        for b in iter(lambda:f.read(65536),b''):h.update(b)
    return h.hexdigest()
def digest_map(v):return hashlib.sha256(json.dumps(dict(sorted(v.items())),separators=(',',':')).encode()).hexdigest()
def safe_relative(s):
    p=Path(s);require(not p.is_absolute() and '..' not in p.parts and s!='.','Unsafe relative leaf');return p
def document(pin):
    require(pin and set(pin)>={'path','sha256'},'Exact pin required');require(sha(pin['path'])==pin['sha256'],'Pinned document changed');return json.loads(data(pin['path']))
def media_leaf(s):return Path(s).suffix.lower() in ('.png','.wav') and s.startswith(('public/','desktop/','art/','audio/'))
def copy(source,destination):
    with Path(destination).open('xb') as f:f.write(data(source))
def trace(path):
    pending=list(Path(path).absolute().parts[1:]);root=Path('/');links=[]
    while pending:
        root/=pending.pop(0)
        if root.is_symlink():
            require(len(links)<16,'Alias depth exceeded');target=os.readlink(root)
            links.append({'path':str(root),'target':target,'finalLeaf':not pending})
            resolved=Path(target) if os.path.isabs(target) else root.parent/target
            pending=list(Path(os.path.normpath(resolved)).parts[1:])+pending;root=Path('/')
        elif pending:require(root.is_dir(),'Non-directory alias parent')
        else:require(root.is_file(),'Missing regular resolved body')
    return root,links
def pinned_donor_file(donor,relative,catalogue):
    logical=donor/safe_relative(relative);actual=trace(logical);entry=catalogue['leaves'].get(relative)
    decode=lambda p:catalogue['roots'][p[0]]+p[1]
    wanted=[{'path':decode(x[0]),'target':decode(x[1]),'finalLeaf':x[2]} for x in catalogue['chains'][entry[2]]] if entry else []
    require(actual[1]==wanted and str(actual[0])==(decode(entry[1]) if entry else str(logical)),'Donor full alias chain changed: '+relative)
    return actual
def assemble(activation_path):
    plan=json.loads(data(P/'PLAN.json'));activation=json.loads(data(activation_path))
    require(activation.get('rootAssemblyAuthorized') is True,'Root activation required')
    method=document(activation.get('methodGate'))
    require(str(method.get('decision','')).startswith('ACCEPT') and method.get('controlsPlanSHA256')==sha(P/'PLAN.json'),'Wrong independent controls gate')
    source=document(plan['starterSourceGate']);author=document(plan['sourcePlan']);final=document(plan['sourceFinal'])
    require(source.get('accepted') is True and source.get('sourceEngineeringEligible') is True and source.get('controlsPlanSHA256')==plan['sourcePlan']['sha256'] and source.get('authorFinalSHA256')==plan['sourceFinal']['sha256'] and source.get('candidateSourceDigest')==plan['expectedSourceDigest'] and source.get('fourFullByteInversesVerified') is True and source.get('all13NativeImageIdentitiesVerifiedWithoutDecode') is True,'Exact accepted starter tuple')
    required={'src/main.ts':'mainDecodedSHA256','src/coherent-native128.ts':'helperDecodedSHA256','src/art.ts':'artSHA256','public/art/coherent-native128-manual-crop-view-manifest.json':'manifestSHA256'}
    require(set(plan['replacements'])==set(required),'Only four declared substitutions')
    for relative,field in required.items():
        pp=plan['replacements'][relative];cp=author['candidateSources'][Path(relative).name]
        require(source[field]==pp['sha256']==cp['decodedSHA256'] and pp['bytes']==cp['decodedBytes'] and sha(pp['path'])==pp['sha256'] and not Path(pp['path']).is_symlink(),'Materialized source full identity changed')
    require(author['externalSixPNGs']==list(plan['newNativePNGs'].values()) and len(plan['newNativePNGs'])==6,'Exact six native source tuple')
    for pp in plan['newNativePNGs'].values():require(sha(pp['path'])==pp['sha256'] and Path(pp['path']).stat().st_size==pp['bytes'] and not Path(pp['path']).is_symlink(),'Native external body changed')
    for pp in author['exactGatePins'].values():document(pp)
    grant=document(plan['materializationGrant']);receipt=document(plan['materializationGuard'])
    require(grant.get('authorized') is True and grant.get('sourceMaterializationOnly') is True and grant['gateSHA256']==plan['starterSourceGate']['sha256'] and grant['planSHA256']==plan['sourcePlan']['sha256'] and receipt['exit_code']==0 and receipt['failure'] is None,'Exact prior Root materialization controls')
    require(all(str(Path(pp['path']).parent)==grant['exactOutputDirectory'] for pp in plan['replacements'].values()),'Wrong materialized directory')
    baseline=document(plan['donorFreeze']);donor=Path(baseline['stage'])
    require(str(donor)==plan['donorStage'] and baseline['sourceDigest']==plan['donorSourceDigest'] and baseline['outputsDigest']==plan['donorOutputsDigest'],'Wrong frozen donor')
    require(len(baseline['inputs'])==98 and len(baseline['outputs'])==64 and digest_map(baseline['inputs'])==baseline['sourceDigest'] and digest_map(baseline['outputs'])==baseline['outputsDigest'],'Full98/64 donor coherence')
    catalogue=document(plan['donorAliasCatalogue'])
    require(baseline['actualAliasCatalogue']=={'path':plan['donorAliasCatalogue']['path'],'sha256':plan['donorAliasCatalogue']['sha256'],'count':plan['donorAliasCount']} and catalogue['roots'][0]==str(donor) and len(catalogue['leaves'])==plan['donorAliasCount'],'Exact complete donor chain catalogue')
    for root in ['src','desktop','public']:require((donor/root).is_dir() and not (donor/root).is_symlink(),'Private donor directories required')
    actual={x.relative_to(donor).as_posix() for root in ['src','desktop','public'] for x in (donor/root).rglob('*') if x.is_file()}
    actual.update(['index.html','THIRD-PARTY.md','package.json','package-lock.json','tsconfig.json','vite.config.ts','scripts/build.mjs'])
    require(actual==set(baseline['inputs']),'Donor full input membership mismatch')
    require({x.relative_to(donor/'dist').as_posix() for x in (donor/'dist').rglob('*') if x.is_file()}==set(baseline['outputs']),'Donor full output membership mismatch')
    for root,mapping in [('',baseline['inputs']),('dist/',baseline['outputs'])]:
        for relative,expectedSHA in mapping.items():
            rel=root+relative;before=pinned_donor_file(donor,rel,catalogue)
            require(sha(donor/rel)==expectedSHA and pinned_donor_file(donor,rel,catalogue)==before,'Donor body/chain changed: '+rel)
    support=baseline['supportBodies'];require(len(support)==30,'Full support30 required')
    for relative,expectedSHA in support.items():safe_relative(relative);require(relative not in baseline['inputs'] and sha(donor/relative)==expectedSHA,'Support changed')
    inputs=dict(baseline['inputs']);inputs.update({r:x['sha256'] for r,x in plan['replacements'].items()});inputs.update({r:x['sha256'] for r,x in plan['newNativePNGs'].items()})
    require(inputs==plan['expectedInputs'] and len(inputs)==104 and digest_map(inputs)==plan['expectedSourceDigest'],'Full104 source prediction mismatch')
    inverse=dict(inputs)
    for r in plan['newNativePNGs']:del inverse[r]
    for r in plan['replacements']:inverse[r]=baseline['inputs'][r]
    require(inverse==baseline['inputs'],'Full104→98 map inverse')
    originalHeld={r:h for r,h in baseline['outputs'].items() if r.startswith(('art/','audio/'))};held=dict(originalHeld)
    require(len(originalHeld)==59,'Baseline59 output bodies')
    held.update({r[7:]:x['sha256'] for r,x in plan['replacements'].items() if r.startswith('public/')});held.update({r[7:]:x['sha256'] for r,x in plan['newNativePNGs'].items()})
    require(held==plan['expectedHeldOutputs'] and len(held)==65 and digest_map(held)==plan['expectedHeldOutputsDigest'],'Candidate65 output bodies')
    inverseHeld=dict(held)
    for r in plan['newNativePNGs']:del inverseHeld[r[7:]]
    inverseHeld['art/coherent-native128-manual-crop-view-manifest.json']=originalHeld['art/coherent-native128-manual-crop-view-manifest.json']
    require(inverseHeld==originalHeld,'Full65→59 output inverse')
    manifest=document(plan['replacements']['public/art/coherent-native128-manual-crop-view-manifest.json']);art=data(plan['replacements']['src/art.ts']['path']).decode();helper=data(plan['replacements']['src/coherent-native128.ts']['path']).decode()
    descriptor=json.loads(art.split('export const COHERENT_NATIVE128 = ',1)[1].split(' as const;',1)[0])
    oldManifest=json.loads(data(donor/'public/art/coherent-native128-manual-crop-view-manifest.json'))
    require(len(manifest['sprites'])==13 and manifest['sprites'][:7]==oldManifest['sprites'] and descriptor['sprites']==manifest['sprites'] and descriptor['manifestSha256']==plan['replacements']['public/art/coherent-native128-manual-crop-view-manifest.json']['sha256'] and manifest['animation'] is None,'Exact13 roles/digest descriptor')
    require('sprites.length !== 13' in helper and 'images.length === 13' in helper,'All13 readiness admission source')
    expectedAliases=sorted([r for r in inputs if media_leaf(r) and r not in plan['newNativePNGs']]+['dist/'+r for r in held if media_leaf(r)])
    require(expectedAliases==plan['expectedAliasKeys'],'Derived complete new alias domain')
    require(not STAGE.exists() and not STAGE.is_symlink(),'Fresh stage only; preserve partial failures')
    v=os.statvfs(STAGE.parent);require(v.f_bavail*v.f_frsize>=64*1048576,'Disk64 absent');STAGE.mkdir()
    for relative in sorted(inputs):
        destination=STAGE/safe_relative(relative);destination.parent.mkdir(parents=True,exist_ok=True)
        pp=plan['replacements'].get(relative) or plan['newNativePNGs'].get(relative);origin=pp['path'] if pp else donor/relative
        if media_leaf(relative) and relative not in plan['newNativePNGs']:destination.symlink_to(origin)
        else:copy(origin,destination)
    (STAGE/'node_modules').symlink_to(donor/'node_modules',target_is_directory=True)
    for relative in support:
        destination=STAGE/relative;destination.parent.mkdir(parents=True,exist_ok=True);require(not destination.exists(),'Support collision');copy(donor/relative,destination)
    observed={r:sha(STAGE/r) for r in sorted(inputs)};require(observed==inputs,'Fresh assembly full identity mismatch')
    for rel in inputs:
        real,chain=trace(STAGE/rel)
        if media_leaf(rel) and rel not in plan['newNativePNGs']:
            donorReal,donorChain=pinned_donor_file(donor,rel,catalogue);require(chain==[{'path':str(STAGE/rel),'target':str(donor/rel),'finalLeaf':True}]+donorChain and real==donorReal,'New input alias chain mismatch')
        else:
            require(not chain and real==STAGE/rel,'Code/JSON/new PNG must be private copies')
            origin=plan['replacements'].get(rel) or plan['newNativePNGs'].get(rel);origin=Path(origin['path']) if origin else donor/rel
            old=origin.stat();new=(STAGE/rel).stat();require((old.st_dev,old.st_ino)!=(new.st_dev,new.st_ino),'Private inode reused')
    assembly={'stage':str(STAGE),'inputs':observed,'inputCount':104,'sourceDigest':digest_map(observed),'baselineStage':str(donor),'baselineOutputs':baseline['outputs'],'baseline':plan['donorFreeze'],'expectedHeldOutputs':held,'supportBodies':support,'activationPath':str(Path(activation_path).absolute()),'activationSHA256':sha(activation_path),'sourceGate':activation['methodGate'],'starterSourceGate':plan['starterSourceGate'],'starterSourcePlan':plan['sourcePlan'],'donorAliasCatalogue':plan['donorAliasCatalogue'],'newPrivateNativeInputs':sorted(plan['newNativePNGs']),'expectedAliasKeys':expectedAliases,'qualification':plan['qualification']}
    control=STAGE/'.control';control.mkdir();(control/'ASSEMBLY.json').write_text(json.dumps(assembly,indent=2)+'\n');return assembly
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--activation',required=True)
    result=assemble(parser.parse_args().activation)
    print(json.dumps({'stage':result['stage'],'inputCount':result['inputCount'],'sourceDigest':result['sourceDigest'],'buildRun':False}))
