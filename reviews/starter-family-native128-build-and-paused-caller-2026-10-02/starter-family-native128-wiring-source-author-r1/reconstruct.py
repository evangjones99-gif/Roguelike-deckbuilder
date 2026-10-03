"""SOURCE-only exact frozen-base reconstruction; no modules executed, PNGs decoded or stage writes."""
import os,sys,json,gzip,hashlib,resource
from pathlib import Path
resource.setrlimit(resource.RLIMIT_DATA,(24*1048576,24*1048576))
ROOT=Path(__file__).resolve().parent;BASE=Path('/workspace/scratch/native128-empty-intent-stage-r1')
FREEZE=Path('/workspace/scratch/native128-empty-intent-strict-build-root-r1/final-seal-r1/RUNTIME-FREEZE.json')
SHA=lambda b:hashlib.sha256(b).hexdigest()
def read(p):
 fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME)
 with os.fdopen(fd,'rb') as f:return f.read()
def js(x):return (json.dumps(x,separators=(',',':'))+'\n').encode()
def digest(m):return SHA(json.dumps(dict(sorted(m.items())),separators=(',',':')).encode())
def need(c,m):
 if not c:raise ValueError(m)
def pin(p):
 b=read(p);return {'path':str(p),'bytes':len(b),'sha256':SHA(b)}
def swap(s,a,b,ops):
 need(s.count(a)==1,'Unique exact source span');ops.append((a,b));return s.replace(a,b)
def inverse(s,ops):
 for a,b in reversed(ops):need(s.count(b)==1,'Unique inverse span');s=s.replace(b,a)
 return s
GATES={
 'ashEngineering':('ash-widow-correction-native128-final-engineering-independent-r2','480eb3f2bf8f1a3e35f440f6a78a62e72d35adb1f12911ce6ef815c5c064dfbb'),
 'ashPrivateFit':('ash-widow-correction-native128-native-visual-independent-r2','3b2b0f6e6e3e06ad8fea8d10b5dc271956767da302e4f7e43d8c3d70885cb77d'),
 'fenBriarEngineering':('starter-family-native128-final-output-engineering-independent-r3','4c24290e18f58efdd9b6c56a35aaff5a10930b1738f4bbaaa629832ca892631d'),
 'fenBriarPrivateFit':('starter-family-native128-assets-visual-independent-r3','7fd5ad5fb035420ea8c2fff3724fb8dbe6d700e7c39bc32e67e4d0d867dd744c')}
f= json.loads(read(FREEZE));need(f['sourceDigest']=='76e5ba02635900ad242b047f9aa5e11adbc67b9e99f9cb67b35884405d21bc40' and f['outputsDigest']=='2547c159b14f634a2ec17473bded94af60c38e6f4aba8ea208f32dba9875f3a8','Frozen base')
need(len(f['inputs'])==98 and len(f['outputs'])==64 and digest(f['inputs'])==f['sourceDigest'] and digest(f['outputs'])==f['outputsDigest'],'Full frozen maps')
gatePins={}
for k,(n,h) in GATES.items():
 p=Path('/workspace/scratch')/n/'GATE.json';gatePins[k]=pin(p);need(gatePins[k]['sha256']==h,'Exact independent scope gate')
manifestPath='public/art/coherent-native128-manual-crop-view-manifest.json';mb=read(BASE/manifestPath);need(SHA(mb)==f['inputs'][manifestPath],'Manifest donor hash');m=json.loads(mb);need(len(m['sprites'])==7 and m['animation'] is None,'Seven unchanged initial assets')
ash=Path('/workspace/scratch/ash-widow-correction-native128-final-output-root-r2');others=Path('/workspace/scratch/starter-family-native128-final-output-root-r3')
av=json.loads(read(ash/'VIEW-MANIFEST.json'));ov=json.loads(read(others/'VIEW-MANIFEST.json'));newRows=av['sprites']+ov['sprites'][2:];need(len(newRows)==6 and all('ash-widow-correction' in x['name'] for x in newRows[:2]),'Corrected Ash only')
assetPins=[]
for i,x in enumerate(newRows):
 p=(ash if i<2 else others)/x['filename'];pp=pin(p);need(pp['sha256']==x['sha256'],'Exact native PNG external identity');need(x['native_dimensions']==[128,128] and x['ground_anchor']==[64,120] and x['mirror'] is False,'Common asset geometry');assetPins.append(pp)
m['sprites']+=newRows;m['status']='UNSELECTED_THIRTEEN_STATIC_NATIVE_ASSETS_PRIVATE_SCENE_PROPOSAL';m['master_sha256']={'existingSeven':m['master_sha256'],'correctedAsh':av['master_sha256'],'fenBriar':ov['master_sha256']};newManifest=js(m)
source={};ops={}
for n in ['coherent-native128.ts','main.ts','art.ts']:
 b=read(BASE/'src'/n);need(SHA(b)==f['inputs']['src/'+n],'Exact frozen source donor');source[n]=b;ops[n]=[]
s=source['coherent-native128.ts'].decode()
a=s[s.index('const keyFor ='):s.index('/** All-or-baseline')]
b="""const starterBodyKey = (cardId: string): number | null => {
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
s=swap(s,a,b,ops['coherent-native128.ts'])
s=swap(s,'COHERENT_NATIVE128.sprites.length !== 7','COHERENT_NATIVE128.sprites.length !== 13',ops['coherent-native128.ts'])
s=swap(s,'ready = images.length === 7;','ready = images.length === 13;',ops['coherent-native128.ts'])
s=swap(s,"state.hand.every(id => CARDS[id]?.type !== 'summon' || id === 'cairnhound' || id === 'cairnhound+')","state.hand.every(id => CARDS[id]?.type !== 'summon' || starterPortraitKey(id) !== null)",ops['coherent-native128.ts'])
a="    portrait(kind: 'hound' | 'hunter') { return ready && !disposed ? images[kind === 'hound' ? 4 : 5].src : ''; },"
s=swap(s,a,a+"\n    cardPortrait(cardId: string) { const key = starterPortraitKey(cardId); return ready && !disposed && key !== null ? images[key].src : ''; },",ops['coherent-native128.ts']);sourceNew={'coherent-native128.ts':s.encode()}
s=source['main.ts'].decode();a="const nativeArt = card.type === 'summon' && coherentNative128.ready && (card.id === 'cairnhound' || card.id === 'cairnhound+') ? `<img src=\"${escape(coherentNative128.portrait('hound'))}\" width=\"128\" height=\"128\" alt=\"\">` : pixelToolSymbol(card.type === 'summon' ? 'binding' : card.effect || '');"
b="const nativePortrait = card.type === 'summon' ? coherentNative128.cardPortrait(card.id) : '';\n  const nativeArt = nativePortrait ? `<img src=\"${escape(nativePortrait)}\" width=\"128\" height=\"128\" alt=\"\">` : pixelToolSymbol(card.type === 'summon' ? 'binding' : card.effect || '');"
s=swap(s,a,b,ops['main.ts']);sourceNew['main.ts']=s.encode();need(len(sourceNew['main.ts'])<=128*1024,'Bounded decoded main')
s=source['art.ts'].decode();start=s.index('export const COHERENT_NATIVE128 = ')+len('export const COHERENT_NATIVE128 = ');end=s.index(' as const;',start);a=s[start:end];d=json.loads(a);need(d['sprites']==json.loads(mb)['sprites'],'Exact existing descriptor');d['sprites']=m['sprites'];d['manifestSha256']=SHA(newManifest);s=swap(s,a,json.dumps(d,separators=(',',':')),ops['art.ts']);sourceNew['art.ts']=s.encode()
proof={}
for n,b in sourceNew.items():
 need(inverse(b.decode(),ops[n]).encode()==source[n],'Full byte inverse '+n);proof[n]={'baseSHA256':SHA(source[n]),'decodedSHA256':SHA(b),'decodedBytes':len(b),'replacementCount':len(ops[n]),'fullByteInverse':True}
inputs=dict(f['inputs']);inputs.update({'src/'+n:SHA(b) for n,b in sourceNew.items()});inputs[manifestPath]=SHA(newManifest)
for pp in assetPins:inputs['public/art/'+Path(pp['path']).name]=pp['sha256']
need(len(inputs)==104,'Full predicted104 map');need(inputs['src/arena.ts']==f['inputs']['src/arena.ts'],'Arena unchanged')
out=Path(sys.argv[1]);need(not out.exists(),'Fresh output directory only')
files={'coherent-native128.ts':sourceNew['coherent-native128.ts'],'art.ts':sourceNew['art.ts'],'main.ts.gz':gzip.compress(sourceNew['main.ts'],mtime=0),'coherent-native128-manual-crop-view-manifest.json':newManifest,'PREDICTED-INPUTS.json.gz':gzip.compress(js(inputs),mtime=0)}
proof.update({'mainStoredSHA256':SHA(files['main.ts.gz']),'mainStoredBytes':len(files['main.ts.gz']),'mainFormat':'gzip mtime0; decoded UTF-8 TypeScript source hash above','baselineFreeze':pin(FREEZE),'baselineInputs':98,'predictedInputs':104,'predictedSourceDigest':digest(inputs),'predictedOutputs':70,'outputPredictionOnly':True,'unchangedArenaSHA256':inputs['src/arena.ts'],'existingSevenRowsExact':m['sprites'][:7]==json.loads(mb)['sprites'],'gatePins':gatePins,'externalNativePNGs':assetPins,'viewPins':[pin(ash/'VIEW-MANIFEST.json'),pin(others/'VIEW-MANIFEST.json')],'actualBuild':False,'actualArtApproval':False,'currentCueFlagBehaviorPreserved':True,'unsupportedOtherSummonsFallback':True,'rssKiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss})
files['PROOF.json']=js(proof)
current=sum(p.stat().st_size for p in ROOT.rglob('*') if p.is_file());need(current+sum(map(len,files.values()))+6000<=128*1024,'Upfront entire family128KiB including6000B final/guard reserve')
out.mkdir(mode=0o700)
for n,b in files.items():
 with (out/n).open('xb') as w:w.write(b);w.flush();os.fsync(w.fileno())
 need(read(out/n)==b,'Saved byte readback')
need(gzip.decompress(read(out/'main.ts.gz'))==sourceNew['main.ts'],'Literal full decoded main readback')
need(json.loads(gzip.decompress(read(out/'PREDICTED-INPUTS.json.gz')))==inputs,'Literal104 map readback')
print(json.dumps({'output':str(out),'writtenBytes':sum(map(len,files.values())),'predictedSource':digest(inputs),'inputs':104,'predictedOutputs':70,'rssKiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'inverseAll':True}))
