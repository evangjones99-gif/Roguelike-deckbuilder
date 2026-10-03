import os,re,resource,hashlib
resource.setrlimit(resource.RLIMIT_DATA,(24*1048576,24*1048576))
P='/workspace/scratch/r3-two-raw-retirement-source-author-r1/'
fd=os.open('/workspace/scratch/retire-two-archived-json-copies-root-r1.py',os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW)
with os.fdopen(fd) as f:s=f.read()
s=s.replace('proposal,proposal_sha,gate,gate_sha,push,push_sha=sys.argv[1:]','proposal,proposal_sha,gate,gate_sha,judgment,judgment_sha,push,push_sha=sys.argv[1:]')
s=s.replace('[(proposal,proposal_sha),(gate,gate_sha),(push,push_sha)]','[(proposal,proposal_sha),(gate,gate_sha),(judgment,judgment_sha),(push,push_sha)]')
s=s.replace("assert p['confirmed'] and p['clean']", "judged=json.loads(Path(judgment).read_text());assert judged['decision']=='AUTHORIZE_EXACT_TWO_R3_RAW_RETIREMENTS_ONCE'\nassert judged['proposalSHA256']==proposal_sha and judged['gateSHA256']==gate_sha and judged['methodSHA256']==sha(Path(__file__)) and judged['pushSHA256']==push_sha\nassert p['confirmed'] and p['clean']")
s=s.replace("assert (R/'.git/refs/heads/codex/lanternbound-production').read_text().strip()==p['commit']", "assert judged['commit']==p['commit']\nassert (R/'.git/refs/heads/codex/lanternbound-production').read_text().strip()==p['commit']")
s=s.replace('two-archived-json-retirement-2026-10-02','r3-two-archived-json-retirement-2026-10-02').replace('two-archived-json-retirement-actual-root-r1','r3-two-archived-json-retirement-actual-root-r1').replace('settle-drag-comparison-actual-r1','target-clear-ghost-comparison-actual-r3')
a=s.index("selected=json.loads((S/'target-wait-default-promotion-root-r1/RESULT.json').read_text())")
b=s.index("\nselected_exact()\n",a)+1
s=s[:a]+"selected_path=S/'target-clear-ghost-promotion-root-r3/RESULT.json'\nassert sha(selected_path)==e['selectedMap']['sha256']==g['selectedMap']['sha256']\nselected=json.loads(selected_path.read_text())\ndef selected_exact():\n assert len(selected[e['selectedMap']['inputKey']])==88 and len(selected[e['selectedMap']['outputKey']])==56\n for rel,h in selected[e['selectedMap']['inputKey']].items():assert sha(R/rel)==h,rel\n for rel,h in selected[e['selectedMap']['outputKey']].items():assert sha(R/'dist'/rel)==h,rel\n"+s[b:]
s=s.replace('reviews/opening-ready-and-rapid-drop-2026-10-01/evidence.tar.gz','reviews/opening-target-clear-ghost-opt-in-2026-10-02/evidence-0f6cec73b283cffd830f57d60a37edde43d1670e814d18a33eeb54d05afc37fa.tar.gz').replace('27c7d4e2a117c5fa2625146a5ca78e7965705f8f809e44b6c2d7b9efb52817af','0f6cec73b283cffd830f57d60a37edde43d1670e814d18a33eeb54d05afc37fa')
s=s.replace("entries=[entry for entry in manifest['entries'] if entry.get('originalPath')==mapping['originalPath']]", "entries=[{'originalPath':str(Path(manifest['roots'][row[0]])/row[1]),'path':row[0]+'/'+row[1],'sha256':row[3],'bytes':row[2]} for row in manifest['rows'] if str(Path(manifest['roots'][row[0]])/row[1])==mapping['originalPath']]")
s=re.sub(r"save\(P/'PRODUCER.json',\{.*\}\)","save(P/'PRODUCER.json',judged)",s)
s=s.replace("'initialFree':initial_free}","'initialFree':initial_free,'proposalSHA256':proposal_sha,'gateSHA256':gate_sha,'judgmentSHA256':judgment_sha,'pushSHA256':push_sha,'protectedZIPStat':protected_before}")
s=s.replace("'capsuleAndCurrent87_56Exact':True", "'capsuleAndCurrent88_56Exact':True,'protectedZIPBefore':protected_before,'protectedZIPAfter':md(os.stat(protected,follow_symlinks=False))")
s=s.replace("assert capsule['sha256']=='0f6cec73b283cffd830f57d60a37edde43d1670e814d18a33eeb54d05afc37fa'", "assert capsule['sha256']=='0f6cec73b283cffd830f57d60a37edde43d1670e814d18a33eeb54d05afc37fa'\nassert e['manifestSHA256']=='38e3cd6de37f9bbc8bbc59f7b3222c0d6774eaee55bd2862c6111e53588b62ba'\nassert sha(Path(e['independentCompleteGate']['path']))==e['independentCompleteGate']['sha256']=='6ec96568886fbeede7c9abacd6365edffa9cb4a7401c9d143ca50a281fd6ac65'")
s=s.replace("assert judged['commit']==p['commit']","assert judged['commit']==p['commit']\nassert judged['callerGateSHA256']==p['callerGateSHA256']==sha(S/'target-clear-default-caller-independent-r1/GATE.json')=='36ddead7bcd9647706f33c766952732dc3ff7b42455f2c678b125569bde2c31a'")
s=s.replace("for p,h in [(proposal,proposal_sha)","assert proposal==str(S/'r3-two-raw-retirement-source-author-r1/PROPOSAL.json')\nassert gate==str(S/'r3-two-raw-retirement-independent-r1/GATE.json') and judgment==str(S/'r3-two-raw-retirement-producer-root-r1.json')\nassert push==str(S/'r3-two-raw-retirement-push-root-r1/PUSH-CONFIRMED.json')\nfor p,h in [(proposal,proposal_sha)")
assert 'settle-drag-comparison' not in s and 'manifest[\'entries\']' not in s
compile(s,'retire-r3-two-archived-json-root-r1.py','exec')
with open(P+'retire-r3-two-archived-json-root-r1.py','x') as out:out.write(s)
print('UNEXECUTED_ACTION_SOURCE',hashlib.sha256(s.encode()).hexdigest(),resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024)
