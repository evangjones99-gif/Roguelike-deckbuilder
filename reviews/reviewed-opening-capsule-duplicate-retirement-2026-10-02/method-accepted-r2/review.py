import os,json,hashlib,ast,dis,resource,time,difflib
from pathlib import Path
P=Path(__file__).parent;S=Path('/workspace/scratch');beg=time.monotonic();pins={}
def raw(p):
 fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME)
 with os.fdopen(fd,'rb') as f:return f.read()
def pin(p,h=None):
 b=raw(p);z=hashlib.sha256(b).hexdigest();assert h is None or z==h,str(p);pins[str(p)]=z;return b
old=pin(S/'retire-opening-capsule-duplicates-root-r1.py','ad37576f647b0018a3e6e4d14ac88c5460f394b4d1800c20db70425bed18a6a8');new=pin(S/'retire-opening-capsule-duplicates-root-r2.py','b1131f6cede49fceb01fcdfb87a251c95519561355acddd03045fba8e4fe7d71');assert len(new)==6762
der=json.loads(pin(S/'retirement-method-root-r2-derivation.json'));assert der['previousMethodSHA256']==pins[str(S/'retire-opening-capsule-duplicates-root-r1.py')] and der['newMethodSHA256']==pins[str(S/'retire-opening-capsule-duplicates-root-r2.py')] and der['oldRejectionSHA256']=='3e841ceb07c2ee5c5165070fb11646a441353636d31b557e414baa141c7f15ab'
prior=json.loads(pin(S/'opening-capsule-duplicate-retirement-method-independent-r1/GATE.json',der['oldRejectionSHA256']));assert prior['exactTwoPathActionMethodEligible'] is False and not prior['actionExecuted']
ops=[
 ('import os,sys,json,stat,hashlib,subprocess,time\n','import os,sys,json,stat,hashlib,subprocess,time,resource\nSTARTED=time.monotonic()\ndef check():\n if time.monotonic()-STARTED>40:raise RuntimeError("Finite40s action deadline exceeded; any earlier per-path progress remains recorded")\n if resource.getrusage(resource.RUSAGE_SELF).ru_maxrss>24576:raise RuntimeError("Own24MiB action ceiling exceeded")\n'),
 ('while b:=f.read(65536):h.update(b)','while b:=f.read(65536):check();h.update(b)'),
 ('def write(p,v):\n','def write(p,v):\n check()\n'),
 (" assert __debug__ and len(sys.argv)==7,'GATE GATE_SHA PUSH_RECEIPT PUSH_SHA ACTION_GRANT GRANT_SHA'"," if not __debug__:raise RuntimeError('Optimized Python erases safety assertions; action refused')\n check()\n assert len(sys.argv)==7,'GATE GATE_SHA PUSH_RECEIPT PUSH_SHA ACTION_GRANT GRANT_SHA'"),
 ("cwd=R,text=True).strip();assert head==push['localHEAD'];assert not subprocess.check_output(['git','status','--porcelain'],cwd=R)","cwd=R,text=True,timeout=10).strip();assert head==push['localHEAD'];assert not subprocess.check_output(['git','status','--porcelain'],cwd=R,timeout=10)"),
 (" assert subprocess.check_output(['git','ls-remote','origin','refs/heads/codex/lanternbound-production'],cwd=R,text=True).split()[0]==head"," age=time.time_ns()-push['remoteVerifiedAtNs'];assert 0<=age<=120*1000000000;assert grant['confirmedPushSHA256']==sys.argv[4]\n check()"),
 (' for ident,old,new,h,n in PAIRS:\n',' for ident,old,new,h,n in PAIRS:\n  check()\n'),
 ('cwd=R,check=True,stdout=subprocess.DEVNULL)','cwd=R,check=True,stdout=subprocess.DEVNULL,timeout=10)'),
 ("opening-capsule-duplicate-retirement-action-root-r1","opening-capsule-duplicate-retirement-action-root-r2"),
 (' for row in records:\n',' for row in records:\n  check()\n'),
 ("met(new)==row['canonicalMetadata'];old.unlink()","met(new)==row['canonicalMetadata'];check();old.unlink()")]
expected=old.decode()
for a,b in ops:assert expected.count(a)==1;expected=expected.replace(a,b,1)
assert expected.encode()==new;restored=new.decode()
for a,b in reversed(ops):assert restored.count(b)==1;restored=restored.replace(b,a,1)
assert restored.encode()==old
t=ast.parse(new);c0=compile(new,str(S/'retire-opening-capsule-duplicates-root-r2.py'),'exec',optimize=0);c1=compile(new,str(S/'retire-opening-capsule-duplicates-root-r2.py'),'exec',optimize=1)
main=next(x for x in t.body if isinstance(x,ast.If) and ast.unparse(x.test)=="__name__ == '__main__'")
assert isinstance(main.body[0],ast.If) and ast.unparse(main.body[0].test)=='not __debug__' and isinstance(main.body[0].body[0],ast.Raise)
optimized=list(dis.get_instructions(c1));raises=[x.offset for x in optimized if x.opname=='RAISE_VARARGS'];assert raises
loads=[x.offset for x in optimized if x.argval in ['pinned','unlink'] and x.opname in ['LOAD_NAME','LOAD_METHOD','LOAD_ATTR']];assert not loads or min(raises)<min(loads)
gitcalls=[x for x in ast.walk(t) if isinstance(x,ast.Call) and isinstance(x.func,ast.Attribute) and isinstance(x.func.value,ast.Name) and x.func.value.id=='subprocess' and x.func.attr in ['check_output','run']]
assert len(gitcalls)==3
for x in gitcalls:assert any(z.arg=='timeout' and isinstance(z.value,ast.Constant) and z.value.value==10 for z in x.keywords)
assert not any('ls-remote' in ast.unparse(x) for x in gitcalls)
preference=json.loads(pin(S/'opening-cue-duplicate-retirement-independent-r2/GATE.json','596577259f0b2455c03b3b3d160700f4c7f1f6a90c049e1ba2347752976ddd8c'));location=json.loads(pin(S/'opening-cue-duplicate-retirement-independent-r1/LOCATION-MAP.json','7aa54ca2c8ab29604d5d334e5cac825b2bd6145fecbe90a656e255f771cdafb4'))
for x in preference['basis'].values():pin(Path(x['path']),x['sha256'])
assert preference['actionAuthority'] is False and len(preference['exactCandidates'])==len(location['entries'])==2
for x in preference['exactCandidates']:
 row=next(y for y in location['entries'] if y['sha256']==x['sha256']);assert row['oldScratchLogicalPath']==x['scratchPath'] and row['preferredCanonicalPhysicalPath']==x['canonicalPath'] and row['bytes']==x['bytes']
assert new.decode().count('old.unlink()')==1 and 'check();old.unlink()' in new.decode()
assert "while b:=f.read(65536):check();h.update(b)" in new.decode() and "def write(p,v):\n check()" in new.decode()
assert new.decode().index("write(out/'PRE.json'")<new.decode().index('old.unlink()')
assert 'max 40' not in new.decode() # no cap relaxation hidden in changed spans
assert resource.getrusage(resource.RUSAGE_SELF).ru_maxrss<=24576
proof={'full11ReplacementByteInverse':True,'oldSourceSHA256':der['previousMethodSHA256'],'newSourceSHA256':der['newMethodSHA256'],'optimizedPythonExplicitRaiseBeforeAnyAuthorizationOrUnlink':True,'compiledSourceOnly':True,'moduleImportedOrExecuted':False,'localGitCalls':3,'allLocalGitTimeoutsSeconds':10,'networkCallsRemoved':True,'wholeCheckSeconds':40,'ownRSSCheckKiB':24576,'exactTwoPathAndMetadataChecksOutsideReviewedSpansUnchanged':True,'freshPushReceiptAgeSecondsMax':120,'grantBindsExactPushSHA256':True,'postWriteTerminalCheck':'Final RESULT fsync then digest(RESULT) calls check() in each chunk before terminal stdout; partial/provisional completed RESULT cannot establish acceptance if helper/outer guard exits nonzero.'}
out={'decision':'ACCEPT_EXACT_R2_TWO_PATH_RETIREMENT_METHOD_CONDITIONAL_ON_FRESH_PUBLISHED_CONTROLS_PUSH_AND_ROOT_GRANT','exactTwoPathActionMethodEligible':True,'methodSHA256':der['newMethodSHA256'],'methodBytes':6762,'derivationSHA256':pins[str(S/'retirement-method-root-r2-derivation.json')],'oldRejectedMethodAndGateRetained':True,'proof':proof,'twoExactCandidates':preference['exactCandidates'],'futureActionRequirements':['Published exact preference/provenance/location map/producer decision, old method rejection and new method/gate controls; current checkpoint and all current repo changes committed and pushed.','Fresh upstream finite Git pipeline independently confirms remote with bounded command, stores actual timestamp/head/clean receipt; no historical06007 receipt substituted.','Grant binds exact reviewed method/gate, producer decision and push receiptSHA; remoteVerifiedAtNs at helper entry must be neither future nor older120s; localHEAD equals receipt and local repository clean.','Fresh ordinary action guard64+512 or separately granted finite combinedGit/action128+512 with original64MiB initial disk admission; source actors paused, sole writer. No native/browser resource waiver.','Exact full old/canonical archive SHA/size/full metadata+xattrs/private nlink1/distinctinode/namespace parent checks before both paths; mismatches stop.','Durable PRE before either unlink, per-path POST canonical full fresh SHA/metadata, observed elapsed/resource/closure normal0, and independent actual POST needed; Root RESULT completed field alone insufficient.'],'partialProgressLimits':'Two sequential unlinks are not an atomic transaction. On deadline/error after first unlink, preserve PRE/any POST and outer failure; independently inspect exact remaining namespace/body state. No automatic restore, global FD/consumer absence, old inode/time reconstruction or net recovery promise.','timeLimitQualification':'40s cooperative checks after bounded regular reads/writes and phase transitions, before each unlink; local Git calls timeout10s. No guarantee of preempting arbitrary blocked filesystem syscalls or unobserved external activity. Root outer finite phase/normal terminal proof remains required.','historicalReaderQualification':preference['historicalPathQualification'],'sourceOnlyNoAction':True,'archiveBodiesReadOrDecoded':False,'canonicalMutation':False,'preferenceChanged':False,'gameArtDefaultRuntimeApproved':False,'roleDisclosure':'Prior independent preservation Root-manifest/COMPLETE reviewer and older converter/witness/helper role; distinct preference author and Root action author. This reviews method corrections, not own art or retention policy approval.','pins':pins,'ownMaxRSSKiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'elapsedSeconds':time.monotonic()-beg}
(P/'AUDIT.json').open('x').write(json.dumps(out,separators=(',',':'))+'\n');print(json.dumps({k:out[k] for k in ['decision','methodSHA256','ownMaxRSSKiB','elapsedSeconds']}))
