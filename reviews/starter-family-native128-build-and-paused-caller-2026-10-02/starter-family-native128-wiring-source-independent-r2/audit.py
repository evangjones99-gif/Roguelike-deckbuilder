import os,stat,json,gzip,hashlib,difflib,ast,resource,time
from pathlib import Path
P=Path(__file__).parent;A=Path('/workspace/scratch/starter-family-native128-wiring-source-author-r2');R=A.with_name('starter-family-native128-wiring-source-author-r1');BASE=Path('/workspace/scratch/native128-empty-intent-stage-r1');beg=time.monotonic();pins={}
def read(p):
 fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME)
 with os.fdopen(fd,'rb') as f:assert stat.S_ISREG(os.fstat(fd).st_mode);return f.read()
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p,h=None):
 b=read(p);assert h is None or sha(b)==h,str(p);pins[str(p)]=sha(b);return b
def obj(p,h=None):return json.loads(pin(p,h))
plan=obj(A/'PLAN.json','7f40607b43f820e0e738b3899b0ab66c61c6acfc3ec42e6af9b6ee362e5b908f');final=obj(A/'FINAL-SEAL.json','5d8395a94db71d439ba87f9cb3c33bbf37a1d59bf7dfac95c1aa08caea5f9413')
method=pin(A/'materialize.py','37d70748744934b5b2bd2ef2a23486d5a76b118614c4f0cd27fff6c2836ffb45');ast.parse(method)
assert final['planSHA256']==pins[str(A/'PLAN.json')] and final['materializeMethodSHA256']==pins[str(A/'materialize.py')]
actual={str(q) for q in R.rglob('*') if q.is_file()};assert actual=={r['path'] for r in plan['immutableR1BodyRows']}
for x in plan['immutableR1BodyRows']:assert len(pin(x['path'],x['sha256']))==x['bytes']
assert sum(x['bytes'] for x in plan['immutableR1BodyRows'])==129374==plan['r1LogicalBytes']<=131072
assert not (R/'FINAL-SEAL.json').exists() and plan['r1FinalSealRefusedTailReserve']
failed=[]
for root in [R,A]:
 for q in root.glob('*-GUARD/RESULT.json'):
  result=obj(q)
  if result['exit_code']!=0:failed.append({'path':str(q),'exitCode':result['exit_code']})
assert len(failed)==3
for name in ['PREPARE-GUARD','FINAL-GUARD']:
 r=obj(A/name/'RESULT.json');assert r['exit_code']==0 and r['failure'] is None and r['memory_events_before']==r['memory_events_after']
bodyrows=[]
for q in sorted(A.rglob('*')):
 if q.is_file() and 'FINAL-GUARD' not in q.parts and q.name!='FINAL-SEAL.json':bodyrows.append([str(q.relative_to(A)),q.stat().st_size,sha(read(q))])
assert len(bodyrows)==final['sourceBodyCount']==8 and sha(json.dumps(bodyrows,separators=(',',':')).encode())==final['sourceBodyTupleSHA256']
f=obj(plan['baseFreeze']['path'],plan['baseFreeze']['sha256']);assert f['stage']==str(BASE) and f['sourceDigest']=='76e5ba02635900ad242b047f9aa5e11adbc67b9e99f9cb67b35884405d21bc40' and f['outputsDigest']=='2547c159b14f634a2ec17473bded94af60c38e6f4aba8ea208f32dba9875f3a8'
def digest(m):return sha(json.dumps(dict(sorted(m.items())),separators=(',',':')).encode())
assert len(f['inputs'])==98 and len(f['outputs'])==64 and digest(f['inputs'])==f['sourceDigest'] and digest(f['outputs'])==f['outputsDigest']
sources={}
for name,x in plan['candidateSources'].items():
 b=pin(x['path'],x['storedSHA256']);assert len(b)==x['storedBytes']
 if x['format']=='gzip-mtime0':
  assert b[:3]==b'\x1f\x8b\x08' and b[4:8]==b'\0'*4
  import io
  with gzip.GzipFile(fileobj=io.BytesIO(b),mode='rb') as z:d=z.read(131073);assert z.read(1)==b''
 else:assert x['format']=='plain';d=b
 assert len(d)==x['decodedBytes']<=131072 and sha(d)==x['decodedSHA256'];sources[name]=d
proof=obj(R/'candidate/PROOF.json',plan['proofSHA256']);baseSources={n:pin(BASE/'src'/n,f['inputs']['src/'+n]) for n in ['main.ts','coherent-native128.ts','art.ts']}
for n in baseSources:assert proof[n]['baseSHA256']==sha(baseSources[n]) and proof[n]['decodedSHA256']==sha(sources[n])
def swap(s,a,b):assert s.count(a)==1;return s.replace(a,b,1)
helper=baseSources['coherent-native128.ts'].decode();oldkey=helper[helper.index('const keyFor ='):helper.index('/** All-or-baseline')]
newkey="""const starterBodyKey = (cardId: string): number | null => {
  const id = cardId.endsWith('+') ? cardId.slice(0, -1) : cardId;
  return id === 'cairnhound' ? 0 : id === 'ashwidow' ? 7 : id === 'fenstalker' ? 9 : id === 'briarcolossus' ? 11 : null;
};
const starterPortraitKey = (cardId: string): number | null => {
  const body = starterBodyKey(cardId);
  return body === null ? null : body === 0 ? 4 : body + 1;
};
const keyFor = (unit: Unit, side: 'ally' | 'enemy'): number | null => side === 'ally'
  ? starterBodyKey(unit.cardId)
  : unit.cardId === 'raider' ? (unit.hp <= 0 ? 6 : 1) : unit.cardId === 'revenant' ? 2 : null;
"""
portrait="    portrait(kind: 'hound' | 'hunter') { return ready && !disposed ? images[kind === 'hound' ? 4 : 5].src : ''; },"
ops=[(oldkey,newkey),('COHERENT_NATIVE128.sprites.length !== 7','COHERENT_NATIVE128.sprites.length !== 13'),('images.length === 7','images.length === 13'),('Native seven-image contract','Native thirteen-image contract'),("state.hand.every(id => CARDS[id]?.type !== 'summon' || id === 'cairnhound' || id === 'cairnhound+')","state.hand.every(id => CARDS[id]?.type !== 'summon' || starterPortraitKey(id) !== null)"),(portrait,portrait+"\n    cardPortrait(cardId: string) { const key = starterPortraitKey(cardId); return ready && !disposed && key !== null ? images[key].src : ''; },")]
for a,b in ops:helper=swap(helper,a,b)
assert helper.encode()==sources['coherent-native128.ts'];inverse=helper
for a,b in reversed(ops):inverse=swap(inverse,b,a)
assert inverse.encode()==baseSources['coherent-native128.ts']
main=baseSources['main.ts'].decode();a="const nativeArt = card.type === 'summon' && coherentNative128.ready && (card.id === 'cairnhound' || card.id === 'cairnhound+') ? `<img src=\"${escape(coherentNative128.portrait('hound'))}\" width=\"128\" height=\"128\" alt=\"\">` : pixelToolSymbol(card.type === 'summon' ? 'binding' : card.effect || '');";b="const nativePortrait = card.type === 'summon' ? coherentNative128.cardPortrait(card.id) : '';\n  const nativeArt = nativePortrait ? `<img src=\"${escape(nativePortrait)}\" width=\"128\" height=\"128\" alt=\"\">` : pixelToolSymbol(card.type === 'summon' ? 'binding' : card.effect || '');"
assert swap(main,a,b).encode()==sources['main.ts'] and swap(sources['main.ts'].decode(),b,a).encode()==baseSources['main.ts']
mb=pin(BASE/'public/art/coherent-native128-manual-crop-view-manifest.json',f['inputs']['public/art/coherent-native128-manual-crop-view-manifest.json']);oldm=json.loads(mb);m=json.loads(sources['coherent-native128-manual-crop-view-manifest.json']);assert m['sprites'][:7]==oldm['sprites'] and len(m['sprites'])==13 and m['animation'] is None and m['palette']==oldm['palette'] and m['dimensions']==[128,128]
restored=dict(m);restored.update({'sprites':oldm['sprites'],'status':oldm['status'],'master_sha256':oldm['master_sha256']});assert (json.dumps(restored,indent=2)+'\n').encode()==mb
art=baseSources['art.ts'].decode();prefix='export const COHERENT_NATIVE128 = ';i=art.index(prefix)+len(prefix);j=art.index(' as const;',i);oldDescriptor=art[i:j];d=json.loads(oldDescriptor);assert d['sprites']==oldm['sprites'];d['sprites']=m['sprites'];d['manifestSha256']=sha(sources['coherent-native128-manual-crop-view-manifest.json']);newDescriptor=json.dumps(d,separators=(',',':'))
assert swap(art,oldDescriptor,newDescriptor).encode()==sources['art.ts'] and swap(sources['art.ts'].decode(),newDescriptor,oldDescriptor).encode()==baseSources['art.ts']
av=obj('/workspace/scratch/ash-widow-correction-native128-final-output-root-r2/VIEW-MANIFEST.json','94858fa8587480982b1d927efca73252e95e677f80b4775ef7b5bdbc66f5570f');ov=obj('/workspace/scratch/starter-family-native128-final-output-root-r3/VIEW-MANIFEST.json','e9aa184e2f39f88751759f63de02c830df0a0252bdfbffb46297bb6af776344d');assert m['sprites'][7:]==av['sprites']+ov['sprites'][2:]
for x in plan['externalSixPNGs']:assert len(pin(x['path'],x['sha256']))==x['bytes']
allImages=[]
for row in m['sprites']:
 assert row['native_dimensions']==[128,128] and row['ground_anchor']==[64,120] and row['mirror'] is False
 if row in m['sprites'][:7]:path=BASE/'public/art'/row['filename']
 else:path=next(Path(x['path']) for x in plan['externalSixPNGs'] if Path(x['path']).name==row['filename'])
 assert sha(read(path.resolve()))==row['sha256'];allImages.append({'filename':row['filename'],'sha256':row['sha256']})
assert m['sprites'][7]['sha256']=='e02e10cb6b02404b87d22053321e3b0268fa6729c09f6d4b3df3bedc6eb9d462' and m['sprites'][8]['sha256']=='21bead977286b45053242fb8b37d225838e2d78b448e22d1b2a8373a61f72a8d'
for card,body,port in [('cairnhound',0,4),('ashwidow',7,8),('fenstalker',9,10),('briarcolossus',11,12)]:assert m['sprites'][body]['category']=='body' and m['sprites'][port]['category']=='portrait'
gates={}
for key,x in plan['exactGatePins'].items():gates[key]=obj(x['path'],x['sha256']);assert Path(x['path']).stat().st_size==x['bytes']
assert gates['fenBriarPrivateFit']['fenAndBriarFourAssetsEligibleForIsolatedPrivateFitTrial'] and not gates['fenBriarPrivateFit']['allSixPrivateIntegrationEligible']
assert gates['ashPrivateFit']['decision']=='ACCEPT_CORRECTED_ASH_PAIR_FOR_PRIVATE_SCENE_FIT_ONLY'
compressed=pin(plan['full104MapPath'],plan['full104MapStoredSHA256']);assert compressed[4:8]==b'\0'*4;pred=json.loads(gzip.decompress(compressed));expected=dict(f['inputs'])
for n in ['main.ts','art.ts','coherent-native128.ts']:expected['src/'+n]=sha(sources[n])
expected['public/art/coherent-native128-manual-crop-view-manifest.json']=sha(sources['coherent-native128-manual-crop-view-manifest.json'])
for x in plan['externalSixPNGs']:expected['public/art/'+Path(x['path']).name]=x['sha256']
assert pred==expected and len(pred)==104 and digest(pred)==plan['predictedSourceDigest']==final['predictedSourceDigest']=='65b31b3f21e34a624bdac962e4919c7dc1791e502eb6cfdb1612103b8036fe9c'
changed=[k for k,v in f['inputs'].items() if pred[k]!=v];assert sorted(changed)==sorted(['src/main.ts','src/art.ts','src/coherent-native128.ts','public/art/coherent-native128-manual-crop-view-manifest.json']);assert pred['src/arena.ts']==plan['arenaUntouched']=='ce8ba9e8cd80ca5acd3e9eb6956a4879fc14abd465b66d7a4f358ca9052d2835'
# Materializer inspected as inert source, never imported or invoked: it verifies all four bodies before mkdir,
# pins stored and decoded identities, uses fresh x writes/fsync/readback and no media/module/build calls.
assert "assert not out.exists()" in method.decode() and method.decode().index("bodies[name]=d")<method.decode().index('out.mkdir')
assert plan['currentCanonicalCueCompositionPending'] and plan['privateCueFlagUnchanged'] and plan['actualBuild'] is False
assert resource.getrusage(resource.RUSAGE_SELF).ru_maxrss<=24576
result={'decision':'ACCEPT_EXACT_STARTER_WIRING_SOURCE_FOR_SEPARATE_PRIVATE_MATERIALIZATION_AND_STRICT_BUILD_ONLY','sourceEngineeringEligible':True,'candidateSourceDigest':plan['predictedSourceDigest'],'predictedInputCount':104,'outputCountPredictionOnly':70,'baseFreezeSHA256':plan['baseFreeze']['sha256'],'fourFullByteInversesVerified':True,'unchangedBaseInputEntries':94,'all13NativeImageSHA256VerifiedWithoutDecode':True,'sixAddedRowsCorrectedAshAndFenBriarOnly':True,'rolesAndUpgradeMapping':'Cairn0/4,Ash7/8,Fen9/10,Briar11/12; one+upgrade suffix same body/portrait; enemyReaver1/dead6 andGloam2 unchanged; hunter3/5 unchanged.','unsupportedFamilies':'Unmapped summon body/portrait returns null/empty; supports false for current unknown allies/enemies/hand summon, whole painted battle fallback under unchanged admission latch. Unsupported card native slot uses existing binding symbol hidden by baseline mode. No new latch/readiness/reentry fix claimed.','authorR1LogicalBytes':129374,'authorR2LogicalBytes':sum(q.stat().st_size for q in A.rglob('*') if q.is_file()),'authorFailedGuardsRetained':failed,'decodedGzipQualified':'Main117957/helper19633 bytes, exact stored+decoded SHA/length/mtime0 verified under bounded128KiB reads; full candidate compressed in unchanged R1 rather than hidden omitted source.','materializeQualification':'Future Root must choose exact new private directory and current method/PLAN pins under separate source guard. Materializer is not a stand-alone authorization gate; no actual invocation here. It writes only4 regularsource/manifest bodies, no media/build/Node.','preservedAuthority':'Only inspected presentation spans change; wholebyte inverse restores baseline. Arena/rules/save/content/pointer/buttons/UID/accessibility DOM/reduced motion/floor/corpse remain exact frozen source. Main cue flag remains baseline byte-exact; canonical current guidance composition is pending and default promotion excluded.','privateFitQualification':'Different-author art gates authorize isolated private fit only; original six-asset REJECT retained, corrected Ash pair used. No current scene/facing/eight-legs/pixel-art/default/animation/first300/fun approval.','priorRoleDisclosure':'Reviewer authored older converter utility/witness/helper-related work; Cairn authors new wiring. Engineering adaptation reviewed separately, no independent own-old-design/art approval.','futureRequired':'Fresh Root materialization/strict fullTS build, independent actual freeze/alias/source-body checks and separately granted browser fit trial required. Unbuilt70 outputs are a prediction.','pins':pins,'ownMaxRSSKiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'elapsedSeconds':time.monotonic()-beg}
(P/'AUDIT.json').open('x').write(json.dumps(result,separators=(',',':'))+'\n');print(json.dumps({k:result[k] for k in ['decision','candidateSourceDigest','fourFullByteInversesVerified','all13NativeImageSHA256VerifiedWithoutDecode','authorR2LogicalBytes','ownMaxRSSKiB','elapsedSeconds']}))
