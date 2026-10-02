"""Future Root-only measured strict-build freeze. Import performs no finalization."""
from pathlib import Path
import argparse,json
from assemble import trace,pinned_donor_file
from assemble import sha,require,digest_map,STAGE,media_leaf,copy,data,document
def finalize(evidence):
    evidence=Path(evidence).absolute();require(not evidence.exists(),'Fresh seal folder required')
    build_result=evidence.parent/'build-outer-r1/RESULT.json'
    result=json.loads(data(build_result));require(result.get('normal') is True and all(result['checks'].values()),'Bounded strict build/owned closure not normal')
    assembly=json.loads(data(STAGE/'.control/ASSEMBLY.json'));require(assembly['stage']==str(STAGE) and assembly['inputCount']==104,'Wrong assembly')
    provenance=json.loads(data(STAGE/'dist/build-provenance.json'));require(provenance['sourceDigest']==assembly['sourceDigest'] and provenance['hashes']==assembly['inputs'],'Strict build identity mismatch')
    require((STAGE/'dist').is_dir() and not (STAGE/'dist').is_symlink(),'Fresh private outputs required')
    for relative,expected in assembly['inputs'].items():require(sha(STAGE/relative)==expected,'Input changed during build')
    for relative,expected in assembly['supportBodies'].items():require(sha(STAGE/relative)==expected,'Support changed during build')
    donor=Path(assembly['baselineStage']);held=assembly['expectedHeldOutputs']
    for r,h in assembly['baselineOutputs'].items():require(sha(donor/'dist'/r)==h,'Baseline output changed during build')
    baseline=document(assembly['baseline']);catalogue=document(assembly['donorAliasCatalogue'])
    for r in baseline['inputs']:pinned_donor_file(donor,r,catalogue)
    for r in baseline['outputs']:pinned_donor_file(donor,'dist/'+r,catalogue)
    for r,h in baseline['inputs'].items():require(sha(donor/r)==h,'Baseline input changed during build')
    built={x.relative_to(STAGE/'dist').as_posix() for x in (STAGE/'dist').rglob('*') if x.is_file()}
    require(len(built)==5 and {'CREDITS.md','build-provenance.json','index.html'}<=built,'Five new measured code outputs required')
    require(sum(x.startswith('assets/') and x.endswith('.css') for x in built)==1 and sum(x.startswith('assets/') and x.endswith('.js') for x in built)==1,'One CSS and JS bundle required')
    require(len(held)==65,'Exact65 retained/new art/audio outputs required')
    for relative,expected in held.items():
        destination=STAGE/'dist'/relative;require(not destination.exists() and not destination.is_symlink(),'Output collision; never overwrite')
        origin=STAGE/'public'/relative;require(sha(origin)==expected,'Candidate held body changed');destination.parent.mkdir(parents=True,exist_ok=True)
        if media_leaf(relative):destination.symlink_to(origin)
        else:copy(origin,destination)
        require(sha(destination)==expected,'Mounted/copied output identity mismatch')
    inputs={r:sha(STAGE/r) for r in sorted(assembly['inputs'])};require(inputs==assembly['inputs'],'Final source identity changed')
    outputs={x.relative_to(STAGE/'dist').as_posix():sha(x) for x in sorted((STAGE/'dist').rglob('*')) if x.is_file()}
    require(len(inputs)==104 and len(outputs)==70 and all(outputs[r]==h for r,h in held.items()),'Full104/70 identity mismatch')
    freeze={'stage':str(STAGE),'sourceDigest':digest_map(inputs),'inputs':inputs,'outputsDigest':digest_map(outputs),'outputs':outputs,'inputCount':104,'outputCount':70,'assemblySHA256':sha(STAGE/'.control/ASSEMBLY.json'),'supportBodies':assembly['supportBodies'],'buildResourceClosure':{'path':str(build_result),'sha256':sha(build_result)},'qualification':assembly['qualification'],'actualBrowserRun':False,'acceptedDefault':False,'animationProved':False}
    aliases={};roots=[str(STAGE),str(donor)]+[r for r in catalogue['roots'] if r not in [str(STAGE),str(donor)]]
    encode=lambda path:next([i,path[len(root):]] for i,root in sorted(enumerate(roots),key=lambda item:-len(item[1])) if path==root or path.startswith(root+'/'))
    chains=[]
    for rel,expectedSHA in list(inputs.items())+[('dist/'+r,h) for r,h in outputs.items()]:
        real,links=trace(STAGE/rel)
        if not links:continue
        if rel.startswith('dist/'):
            origin=STAGE/'public'/rel[5:];originReal,originLinks=trace(origin)
            require(links==[{'path':str(STAGE/rel),'target':str(origin),'finalLeaf':True}]+originLinks and real==originReal,'Full mounted output alias chain mismatch')
        else:
            originReal,originLinks=pinned_donor_file(donor,rel,catalogue)
            require(links==[{'path':str(STAGE/rel),'target':str(donor/rel),'finalLeaf':True}]+originLinks and real==originReal,'Full fresh input chain mismatch')
        chain=[[encode(x['path']),encode(x['target']),x['finalLeaf']] for x in links]
        if chain not in chains:chains.append(chain)
        aliases[rel]=[expectedSHA,encode(str(real)),chains.index(chain)]
    require(set(aliases)==set(assembly['expectedAliasKeys']),'Complete derived fresh alias leaf domain required')
    evidence.mkdir()
    aliasPath=evidence/'ACTUAL-ALIAS-CATALOGUE.json'
    aliasPath.write_text(json.dumps({'format':'exact-complete-current-leaf-chains-build-evidence-v1','stage':str(STAGE),'roots':roots,'chains':chains,'leaves':aliases,'qualification':'Complete observed first links; workflow holds, not OS readonly or a caller launch grant.'},separators=(',',':'))+'\n')
    freeze['actualAliasCatalogue']={'path':str(aliasPath),'sha256':sha(aliasPath),'count':len(aliases)}
    (evidence/'RUNTIME-FREEZE.json').write_text(json.dumps(freeze,indent=2)+'\n');(evidence/'ASSEMBLY-IDENTITY.json').write_text(json.dumps({'path':str(STAGE/'.control/ASSEMBLY.json'),'sha256':freeze['assemblySHA256']})+'\n');return freeze
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--evidence',required=True);f=finalize(parser.parse_args().evidence)
    print(json.dumps({k:f[k] for k in ['stage','sourceDigest','outputsDigest','inputCount','outputCount']}))
