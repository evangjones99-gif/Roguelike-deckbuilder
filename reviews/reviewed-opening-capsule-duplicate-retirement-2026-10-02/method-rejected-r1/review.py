import os,json,hashlib,ast,dis,types,resource,time
from pathlib import Path
P=Path(__file__).parent;S=Path('/workspace/scratch');beg=time.monotonic();pins={}
def raw(p):
 fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME)
 with os.fdopen(fd,'rb') as f:return f.read()
def pin(p,h):
 b=raw(p);assert hashlib.sha256(b).hexdigest()==h,str(p);pins[str(p)]=h;return b
method=S/'retire-opening-capsule-duplicates-root-r1.py';mh='ad37576f647b0018a3e6e4d14ac88c5460f394b4d1800c20db70425bed18a6a8';b=pin(method,mh);assert len(b)==6294
t=ast.parse(b);code0=compile(b,str(method),'exec',optimize=0);code1=compile(b,str(method),'exec',optimize=1)
def instructions(code):
 out=list(dis.get_instructions(code))
 for x in code.co_consts:
  if isinstance(x,types.CodeType):out+=instructions(x)
 return out
i0=instructions(code0);i1=instructions(code1)
asserts0=sum(x.opname=='LOAD_ASSERTION_ERROR' for x in i0);asserts1=sum(x.opname=='LOAD_ASSERTION_ERROR' for x in i1)
unlink0=[x.offset for x in i0 if x.opname in ['LOAD_METHOD','LOAD_ATTR'] and x.argval=='unlink'];unlink1=[x.offset for x in i1 if x.opname in ['LOAD_METHOD','LOAD_ATTR'] and x.argval=='unlink']
assert asserts0>0 and asserts1==0 and len(unlink0)==len(unlink1)==1
assert not any(x.argval=='__debug__' for x in i1)
main=next(x for x in t.body if isinstance(x,ast.If) and ast.unparse(x.test)=="__name__ == '__main__'")
assert isinstance(main.body[0],ast.Assert) and '__debug__' in ast.unparse(main.body[0])
assert not any(isinstance(x,ast.If) and '__debug__' in ast.unparse(x.test) for x in ast.walk(t))
network=[]
for x in ast.walk(t):
 if isinstance(x,ast.Call) and isinstance(x.func,ast.Attribute) and x.func.attr=='check_output' and 'ls-remote' in ast.unparse(x):
  assert not any(z.arg=='timeout' for z in x.keywords);network.append({'line':x.lineno,'call':ast.unparse(x)})
assert len(network)==1
assert not any(isinstance(x,ast.Attribute) and x.attr=='monotonic' for x in ast.walk(t))
assert not any(isinstance(x,ast.Name) and x.id in ['SIGALRM','alarm','setitimer'] for x in ast.walk(t))
preference=json.loads(pin(S/'opening-cue-duplicate-retirement-independent-r2/GATE.json','596577259f0b2455c03b3b3d160700f4c7f1f6a90c049e1ba2347752976ddd8c'))
for x in preference['basis'].values():pin(Path(x['path']),x['sha256'])
loc=json.loads(raw(S/'opening-cue-duplicate-retirement-independent-r1/LOCATION-MAP.json'));assert len(loc['entries'])==2
for x in preference['exactCandidates']:
 e=next(e for e in loc['entries'] if e['sha256']==x['sha256']);assert e['oldScratchLogicalPath']==x['scratchPath'] and e['preferredCanonicalPhysicalPath']==x['canonicalPath'] and e['bytes']==x['bytes']
assert preference['actionAuthority'] is False and preference['retireCanonicalArchiveOrOtherMaterials'] is False
source=b.decode();assert source.count('old.unlink()')==1 and "write(out/'PRE.json'" in source and source.index("write(out/'PRE.json'")<source.index('old.unlink()')
assert source.count("('f912',S/")==1 and source.count("('ce0f',S/")==1
for x in preference['exactCandidates']:
 assert x['scratchPath'].split('/workspace/scratch/',1)[1] in source and x['canonicalPath'].split('/workspace/Roguelike-deckbuilder/',1)[1] in source and x['sha256'] in source
assert "oldmeta==entry['originalScratchMetadata']" in source and "oldmeta['st_nlink']==1" in source
assert 'os.O_NOFOLLOW|os.O_NOATIME' in source and "'xattrs'" in source and "for parent in p.parents:assert not parent.is_symlink()" in source
assert "met(old)==row['oldMetadata'] and met(new)==row['canonicalMetadata']" in source and "digest(new)==row['sha256'] and met(new)==row['canonicalMetadata']" in source
assert 'no global FD/consumer absence' in source and 'old inode/time reconstruction' in source
assert not any(isinstance(x,ast.Call) and isinstance(x.func,ast.Attribute) and x.func.attr in ['remove','rmdir','rmtree'] for x in ast.walk(t))
assert resource.getrusage(resource.RUSAGE_SELF).ru_maxrss<=24576
result={'decision':'REJECT_EXACT_TWO_PATH_RETIREMENT_SOURCE_METHOD_OPERATIONAL_GUARDS','exactTwoPathActionMethodEligible':False,'methodSHA256':mh,'methodBytes':6294,'preferenceGateSHA256':'596577259f0b2455c03b3b3d160700f4c7f1f6a90c049e1ba2347752976ddd8c','locationMapSHA256':'7aa54ca2c8ab29604d5d334e5cac825b2bd6145fecbe90a656e255f771cdafb4','blockingFindings':[{'id':'optimization-removes-authorization','lines':[23,24,26,41,52,53],'finding':'assert __debug__ is itself erased under optimization. compile(optimize=1) removes all assertions including grant/gate/body/meta checks while the same one unlink call remains. Inherited PYTHONOPTIMIZE can enable this even with python -B.','requiredCorrection':'Unconditional if-not-__debug__ RuntimeError guard before any action; future exact Root invocation must also control optimization env. Re-review fresh method pins.'},{'id':'unbounded-network-phase','line':31,'finding':'Fresh git ls-remote lacks subprocess timeout and there is no whole monotonic ceiling/signal timer. Ordinary resource guard cannot terminate a resource-light blocked network child on elapsed time alone.','requiredCorrection':'Bound Git calls and full phase with reviewed finite deadlines/closure and preserve partial receipts on failure; no relaxation of work/reserve/disk/ownership scope.'}],'compileOnlyWitness':{'ordinaryAssertionLoads':asserts0,'optimizedAssertionLoads':asserts1,'ordinaryUnlinkCalls':len(unlink0),'optimizedUnlinkCalls':len(unlink1),'moduleImportedOrExecuted':False},'unboundedRemoteSource':network,'soundIntendedScope':'Literal two scratch archives only, canonical bodies untouched, exact published map/proposal/producer decision plus gate/grant/current clean head/remote checks intended; fresh full double body hashes/full old metadata+xattrs/private nlink1/distinctinode/parent symlink checks; fsynced PRE before sequential unlink, path-local POST after canonical recheck. These checks are effective only without optimization.','exceptionQualification':'No transactional two-path atomicity: failure after first unlink can leave partial progress. Durable PRE and any completed per-path POST support later independent namespace inspection, not automatic restoration. Root ordinary guard records exception; no all-FD/consumer absence or old-inode/time reconstruction claimed.','publicationDependencyQualification':'Published proposal/map/decision and exact new method gate/current clean confirmed push remain prerequisites; historic preference is not action authority. Root must publish all controls and new checkpoint then obtain separate fresh action grant. Source review does not verify future not-yet-published receipts.','archiveBodyReadsPerformed':False,'actionExecuted':False,'protectedZIPOpened':False,'canonicalOrOriginalMutation':False,'preferenceVerdictChanged':False,'noArtDefaultGameplayAcceptance':True,'roleDisclosure':'Reviewer checked the newer preservation Root manifest and actual COMPLETE, with older converter/witness/helper involvement. Different author owns retirement preference and Root authors this action method. This verdict concerns destructive method guards only.','pins':pins,'ownMaxRSSKiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'elapsedSeconds':time.monotonic()-beg}
(P/'AUDIT.json').open('x').write(json.dumps(result,separators=(',',':'))+'\n');print(json.dumps({k:result[k] for k in ['decision','compileOnlyWitness','ownMaxRSSKiB','elapsedSeconds']}))
