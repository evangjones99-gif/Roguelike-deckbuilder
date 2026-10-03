from pathlib import Path
import json,hashlib,os,time,resource
R=Path('/workspace/Roguelike-deckbuilder');S=Path('/workspace/scratch');start=time.monotonic();rows=[]
def read(p):
 if time.monotonic()-start>35:raise RuntimeError('Finite35s verification exceeded')
 fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME)
 with os.fdopen(fd,'rb') as f:return f.read()
for n in ['starter-family-native128-build-and-paused-caller-2026-10-02','opening-storage-post-and-paused-recovery-2026-10-02']:
 d=R/'reviews'/n;pub=json.loads(read(d/'PUBLICATION.json'));membership={str(x.relative_to(d)) for x in d.rglob('*') if x.is_file()};expected={str(Path(x['canonical']).relative_to(d)) for x in pub['literalCopies']}|{'PUBLICATION.json','README.md'};assert membership==expected
 for x in pub['literalCopies']:
  a=read(Path(x['original']));b=read(Path(x['canonical']));assert a==b and len(b)==x['bytes'] and hashlib.sha256(b).hexdigest()==x['sha256'];rows.append(x)
assert len(rows)==268 and sum(x['bytes'] for x in rows)==1529628
f=S/'starter-family-native128-strict-build-root-r1/final-seal-r1/RUNTIME-FREEZE.json';j=json.loads(read(f));assert hashlib.sha256(read(f)).hexdigest()=='6e61e6e42b1c160e899da7888b20daf33264f8dc2f65d5301ac72e70537590fc'
assert j['sourceDigest']=='65b31b3f21e34a624bdac962e4919c7dc1791e502eb6cfdb1612103b8036fe9c' and j['outputsDigest']=='960e723da3b98d31e99e2b4ce6ee2195dd9fea1bfce9c8254b3cb65c04b7b49d'
assert hashlib.sha256(read(Path(j['actualAliasCatalogue']['path']))).hexdigest()==j['actualAliasCatalogue']['sha256']=='dc763ace41dfbb1666a989014fea57f71d8458c9cafdd0b0b280c6fa076686b6'
expectedPins={'starter-family-native128-strict-build-independent-r1/GATE.json':'2f4f3ef63b325bcbe08a151cf7f0432831afac0d820abaa785c2457fe59f4c12','opening-capsule-duplicate-retirement-post-independent-r1/GATE.json':'a25a01805308439a34ad748358ca83eea566a6ea759847a15009c8db3d75cca7','opening-loop-additional-duplicate-storage-triage-independent-r1/GATE.json':'c4760f06d81f5c1f578bd8e0f619c52da771b01f05499f112d1c9e00238f752d','opening-readonly-pack-cache-hint-source-independent-r1/INDEPENDENT-ACCEPTANCE.json':'58e2b1b1727107e25d39c98caf045c9f78685fa8890c1444ba259bb95607f43f','starter-family-native128-opening-caller-source-author-r1/PAUSED-CLOSURE.json':'d06e84c11913e746811360b392a393dfa3f4de74f3f70b3245e1b1a7f436e0a2'}
for p,h in expectedPins.items():assert hashlib.sha256(read(S/p)).hexdigest()==h
h=read(R/'docs/FRESH-SESSION-HANDOFF-2026-10-02.md').decode()
for k,v in expectedPins.items():assert v in h
for val in [j['sourceDigest'],j['outputsDigest'],j['actualAliasCatalogue']['sha256']]:assert val in h
p=read(R/'docs/HOLLOWPACT-HOURLY-PROMPT.txt').decode();pause=json.loads(read(S/'hollowpact-hourly-pause-and-owner-steering-2026-10-02.json'));assert p.rstrip('\n')==pause['after']['prompt'].rstrip('\n');assert pause['after']['is_enabled'] is False and pause['after']['id']=='6abd587c353c8191bbdbeec3ddcfa741';assert 'lead session choosing the reasoning level necessary' in p and 'with high reasoning when agents' not in p
assert resource.getrusage(resource.RUSAGE_SELF).ru_maxrss<=24576
out={'literalCopies':len(rows),'allLiteralBodiesMatch':True,'membershipExact':True,'actualFreezeAndKeyGatePinsVerified':expectedPins,'pausedTimerAndSavedPromptMatch':True,'scope':'Root handoff verification only; not new independent review, runtime/art/default/cleanup/advice approval. Existing original findings retained.','ownRSSKiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'elapsed':time.monotonic()-start}
q=R/'reviews/opening-storage-post-and-paused-recovery-2026-10-02/HANDOFF-VERIFICATION.json'
with q.open('x') as f:json.dump(out,f,indent=2);f.write(chr(10))
print(json.dumps(out))
