import ast,base64,difflib,errno,hashlib,json,os,pathlib,resource,stat,time
P=pathlib.Path(__file__).parent;R=pathlib.Path('/workspace/Roguelike-deckbuilder');S=pathlib.Path('/workspace/scratch');T=S/'opening-turn-payoff-wording-stage-r1';fallback=[];started=time.monotonic()
def body(p):
 try:fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME)
 except OSError as e:
  if e.errno!=errno.EPERM:raise
  fallback.append(str(p));fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW)
 with os.fdopen(fd,'rb') as f:
  a=os.fstat(f.fileno());assert stat.S_ISREG(a.st_mode);b=f.read();z=os.fstat(f.fileno());assert (a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns)==(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns)
 return b
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):return sha(body(p))
def put(name,x):
 data=(json.dumps(x,indent=2)+'\n').encode();assert sum(q.stat().st_size for q in P.rglob('*') if q.is_file())+len(data)+8192<=96*1024
 with (P/name).open('xb') as f:f.write(data);f.flush();os.fsync(f.fileno())
oldpath=S/'target-clear-default-build-author-r1/RUNTIME-FREEZE.json';newpath=S/'opening-turn-payoff-wording-strict-build-root-r1/final-seal-r1/RUNTIME-FREEZE.json'
assert pin(oldpath)=='739f5e87f95f2ca2ad4e60f7b90ea00aa6384d74c1ae2fc8a4e60266e705ce62';assert pin(newpath)=='d6c225d5408c8e60433aed54655e922a44af224621fc8c48cb6aca8cd3c5883a'
old=json.loads(body(oldpath));new=json.loads(body(newpath));assert len(old['inputs'])==88 and len(new['inputs'])==89 and len(old['outputs'])==len(new['outputs'])==56
delta={k:[old['inputs'].get(k),new['inputs'].get(k)] for k in sorted(set(old['inputs'])|set(new['inputs'])) if old['inputs'].get(k)!=new['inputs'].get(k)};assert list(delta)==['src/main.ts','src/opening-turn-payoff.css']
domains=[]
for label,root,m in [('canonicalInputs',R,old['inputs']),('canonicalOutputs',R/'dist',old['outputs']),('candidateInputs',T,new['inputs']),('candidateOutputs',T/'dist',new['outputs'])]:
 total=0
 for rel,h in m.items():
  data=body((root/rel).resolve(strict=True));assert sha(data)==h,(label,rel);total+=len(data)
 domains.append({'domain':label,'entries':len(m),'fullBodiesMatched':True,'bytesRead':total,'mapSHA256':sha(json.dumps(m,sort_keys=True,separators=(',',':')).encode())})
assert not (R/'src/opening-turn-payoff.css').exists() and not (R/'src/opening-turn-payoff.css').is_symlink()
before=body(R/'src/main.ts');after=body(T/'src/main.ts');a=before.splitlines(keepends=True);b=after.splitlines(keepends=True);offset=[0]
for line in a:offset.append(offset[-1]+len(line))
patch=[]
for tag,i,j,k,l in difflib.SequenceMatcher(None,a,b).get_opcodes():
 if tag!='equal':patch.append({'oldByteStart':offset[i],'oldByteEnd':offset[j],'oldBase64':base64.b64encode(b''.join(a[i:j])).decode(),'newBase64':base64.b64encode(b''.join(b[k:l])).decode()})
forward=bytearray();cursor=0;reverse=[];newcursor=0
for row in patch:
 start,end=row['oldByteStart'],row['oldByteEnd'];ob=base64.b64decode(row['oldBase64']);nb=base64.b64decode(row['newBase64']);assert before[start:end]==ob
 forward+=before[cursor:start];newcursor+=start-cursor;reverse.append((newcursor,newcursor+len(nb),ob));forward+=nb;newcursor+=len(nb);cursor=end
forward+=before[cursor:];assert bytes(forward)==after
restored=bytearray();cursor=0
for start,end,ob in reverse:restored+=after[cursor:start];restored+=ob;cursor=end
restored+=after[cursor:];assert bytes(restored)==before
put('MAIN-INVERSE.json',{'beforeSHA256':sha(before),'afterSHA256':sha(after),'beforeBytes':len(before),'afterBytes':len(after),'format':'sorted old byte ranges, preserve intervening original bytes; inverse uses cumulative offsets','patches':patch,'fullForwardAndInverseByteEquality':True,'qualification':'Selected c4 to accepted cue contains the cue implementation as well as wording; it is not a one-literal delta.'})
gates=[]
for folder,h in [('opening-turn-payoff-wording-actual-gameplay-independent-r2','cbfcbc0e082c17b663d3bb1fac3f7a415505e0aeb7ca664814ebea36e3cccc52'),('opening-turn-payoff-wording-actual-visual-independent-r1','cae95281a0aef122085edb29e68b6e88ff7571d69333ad3c8fdd7162fc9f1e17'),('opening-turn-payoff-wording-actual-technical-independent-r1','83eab5f5ed24dfe7d5bf7ae353ce44f20d716493b106175ef119aae79cc19e3e')]:
 p=S/folder/'GATE.json';assert pin(p)==h;gate=json.loads(body(p));assert gate['decision'].startswith('ACCEPT');gates.append({'path':str(p),'sha256':h,'decision':gate['decision']})
method=P/'select-development-source.py';code=body(method);tree=ast.parse(code);compile(tree,str(method),'exec')
assert not any(isinstance(n,(ast.Import,ast.ImportFrom)) and any(a.name.split('.')[0] in ['subprocess','shutil'] for a in n.names) for n in ast.walk(tree))
assert not any(isinstance(n,ast.Attribute) and n.attr in ['unlink','remove','rmtree','chmod','utime','setxattr'] for n in ast.walk(tree))
plan=S/'wording-grounded-trials-checkpoint-source-author-r1/PLAN.json';assert pin(plan)=='0998d948c57e2fb3d1e01f34e61028d5c80db299df308d3b1e83ab902d4281b7';checkpoint=json.loads(body(plan))
assert any(pathlib.Path(checkpoint['roots'][r[0]])/r[1]==R/'src/main.ts' and r[2]==sha(before) for r in checkpoint['rows'])
hold=pin(R/'AGENTS.md');assert hold=='19e35b29256309ef3fbded5d57ae4e3a582b07dfd0e18f7e8497341e0fe3378e'
assert resource.getrusage(resource.RUSAGE_SELF).ru_maxrss<=24576
put('SOURCE-PROOF.json',{'decision':'AUTHOR_SOURCE_ONLY_FULL_INVERSE_AND_PINS_VERIFIED_NOT_INDEPENDENT_ACCEPTANCE','method':{'path':str(method),'sha256':sha(code),'bytes':len(code),'astCompileOnly':True,'executedOrImported':False},'fullBodyDomains':domains,'exactInputDelta':delta,'sourceMap':{'before':old['sourceDigest'],'after':new['sourceDigest']},'builtOutputMap':{'retainedCanonical':old['outputsDigest'],'candidateReferenceOnly':new['outputsDigest']},'actualGates':gates,'checkpointPlanSHA256':pin(plan),'oldCanonicalMainExactCheckpointLogicalRow':True,'currentHoldSHA256':hold,'futureCompletePreservationGate':'NOT_YET_AVAILABLE_EXTERNAL_ROOT_GRANT_REQUIRED','candidateCSS':body(T/'src/opening-turn-payoff.css').decode(),'canonicalCSSAbsent':True,'NOATIMEFallbackPaths':fallback,'ownRSSKiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'elapsedSeconds':time.monotonic()-started,'capLogicalBytes':96*1024,'scopeLimits':['No action/selection/Git/build/runtime/archive execution','Source-only method still requires different independent reviewer','No protected ZIP body or media decode','No state or game rules acceptance from Python compile']})
print(json.dumps({'normal':True,'ownRSSKiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'elapsedSeconds':time.monotonic()-started,'logicalPacketBytes':sum(q.stat().st_size for q in P.rglob('*') if q.is_file()),'guardClosure':'outer wrapper owns closure'}))
