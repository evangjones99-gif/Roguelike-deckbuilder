import os,json,pathlib,hashlib,resource
resource.setrlimit(resource.RLIMIT_DATA,(24*1048576,24*1048576))
P=pathlib.Path(__file__).parent;R=pathlib.Path('/workspace/Roguelike-deckbuilder');O=R/'reviews/opening-native-aftermath-and-starter-art-2026-10-02';S=pathlib.Path('/workspace/scratch')
def read(p):
 fd=os.open(p,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW)
 with os.fdopen(fd,'rb') as f:return f.read()
def pin(p):
 h=hashlib.sha256();fd=os.open(p,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW);n=0
 with os.fdopen(fd,'rb') as f:
  first=os.fstat(f.fileno())
  for b in iter(lambda:f.read(32768),b''):n+=len(b);h.update(b)
  last=os.fstat(f.fileno());assert (first.st_dev,first.st_ino,first.st_size,first.st_mtime_ns)==(last.st_dev,last.st_ino,last.st_size,last.st_mtime_ns)
 return {'path':str(p),'bytes':n,'sha256':h.hexdigest()}
def j(p):return json.loads(read(p))
def digest(m):return hashlib.sha256(json.dumps(m,sort_keys=True,separators=(',',':')).encode()).hexdigest()
pub=j(O/'PUBLICATION.json');assert pin(O/'PUBLICATION.json')['sha256']=='702aa2f5f0324c03fb05be0980cc68dae35f4eec10b9de947ccb00e21ca0ecc6'
rows=pub['copyRows'];assert len(rows)==78 and sum(r['bytes'] for r in rows)==389662
assert len({r['originalPath'] for r in rows})==len({r['canonicalPath'] for r in rows})==78
copies=[]
for row in rows:
 original=pathlib.Path(row['originalPath']);target=pathlib.Path(row['canonicalPath']);assert target.is_relative_to(O) and not target.is_symlink()
 for q in [original,target]:v=pin(q);assert v['sha256']==row['sha256'] and v['bytes']==row['bytes']
 assert read(original)==read(target);copies.append({'relativePath':str(target.relative_to(O)),'sha256':row['sha256'],'bytes':row['bytes']})
trees=[('native-checkpoint-archive-complete-independent-r1','archive-complete-independent'),('native-checkpoint-root-manifest-independent-r1','root-manifest-independent'),('native-aftermath-starter-checkpoint-source-independent-r1','archive-source-independent'),('native-checkpoint-archive-guard-root-r1','archive-resource-closure')]
for original,canonical in trees:
 expected={q.relative_to(S/original).as_posix() for q in (S/original).rglob('*') if q.is_file() and not q.is_symlink()}
 actual={q.relative_to(O/canonical).as_posix() for q in (O/canonical).rglob('*') if q.is_file()};assert expected==actual,(original,expected^actual)
archiveNames={'evidence-8cdf546a8429e949fe88611d781aca341566f473135fbcbe44b5373beabd7aa8.tar.gz','ROOT-FINAL-INPUT-MANIFEST.json','ROOT-ARCHIVE-GRANT.json','READ-OBSERVATIONS.json','README.md','INDEX.json','RESULT.json'}
assert {q.name for q in (O/'archive').iterdir()}==archiveNames
expected={r['relativePath'] for r in copies}|{'archive/'+n for n in archiveNames}|{'README.md','PUBLICATION.json'}
actual={q.relative_to(O).as_posix() for q in O.rglob('*') if q.is_file()};assert actual==expected and len(actual)==87
assert not any(q.is_symlink() for q in O.rglob('*'))
gatep=O/'archive-complete-independent/GATE.json';gate=j(gatep);assert pin(gatep)['sha256']==pub['completeGateSHA256']=='08d09c6abe9886a0c52590c4f519fb0a9c6f113aa8b9be62b4b594e517419078'
assert gate['accepted'] and gate['COMPLETE'] and gate['preservationOnly'] and not gate['gameRuntimeDefaultReleaseSelected'] and not gate['newArtApproval']
ap=pathlib.Path(gate['archivePath']);assert ap.is_relative_to(O/'archive') and pin(ap)['sha256']==gate['archiveSHA256'] and pin(ap)['bytes']==gate['archiveBytes']==5085419
for key,n in [('indexSHA256','INDEX.json'),('readObservationsSHA256','READ-OBSERVATIONS.json'),('inputManifestSHA256','ROOT-FINAL-INPUT-MANIFEST.json'),('rootGrantSHA256','ROOT-ARCHIVE-GRANT.json')]:assert pin(O/'archive'/n)['sha256']==gate[key]
index=j(O/'archive/INDEX.json');root=j(O/'archive/ROOT-FINAL-INPUT-MANIFEST.json')
assert index['rows']==root['rows'] and index['roots']==root['roots'] and len(index['rows'])==gate['logicalRows']==1278 and gate['fullNewUniqueOriginalByteEqualityCount']==1116
assert index['selfContainedRelease'] is False and index['allOriginalPathsRetained'] is True
docs=[];prefixes=[]
for row in pub['documentPrefixRows']:
 q=pathlib.Path(row['path']);b=read(q);assert pin(q)['sha256']==row['newSHA256'];suffix=b[row['prefixBytes']:];prefix=b[:row['prefixBytes']]
 assert hashlib.sha256(suffix).hexdigest()==row['previousSHA256'] and row['oldLiteralSuffixPreserved']
 matches=[]
 for r in index['rows']:
  logical=str(pathlib.Path(index['roots'][r[0]])/(r[1] if r[1]!='.' else ''))
  if logical==str(q):matches.append(r)
 assert len(matches)==1 and matches[0][2]==row['previousSHA256'] and matches[0][3]==len(suffix)
 text=prefix.decode('utf8');assert text.startswith('## Pixel aftermath and starter-art evidence preserved') and 'default pixel scene and complete payoff remain rejected' in text and 'no cleanup or release/tag occurred' in text
 assert 'Illegal-held readiness was unobserved' in text and 'no CSS acceptance or game-performance causality follows' in text and 'not human enjoyment or completed 300-second' in text
 prefixes.append(text.replace('reviews/opening-native-aftermath-and-starter-art-2026-10-02/README.md','LINK').replace('../LINK','LINK'))
 docs.append({'path':str(q),'newBody':pin(q),'previousSHA256':row['previousSHA256'],'prefixBytes':row['prefixBytes'],'completeUTF8SuffixMatchesArchivedCheckpointRow':True})
assert len(docs)==3 and prefixes[0]==prefixes[1]==prefixes[2]
readme=read(O/'README.md').decode();assert readme.startswith('# Native pixel opening: aftermath and starter-art checkpoint')
for text in ['reject default pixel-scene quality and complete combat payoff','No game source or release is selected by this archive.','requested illegal-held transition was not observed','Root tool history','saved post-closure receipt independently records 54.953892','Eight visible legs are not certified','empty manual-cleanup recipe','No new starter-family sprite has been integrated','1,278 exact logical identities','1,116 new unique bodies','explicit prior4513 inheritance','not a self-contained release','R1 omitted runtime stages','R2 stopped on a nonexistent guessed Vitest package','CSS source/control proposals are included; their later strict build and failed actual comparison are outside','held older `8bbaea72','No server was launched']:assert text in readme,text
decisions={}
for q in sorted((O/'gates').rglob('GATE.json')):decisions[q.parent.name]={'gate':pin(q),'decision':j(q)['decision']}
assert len(decisions)==10
for n in ['corpse-gameplay','corpse-visual','floor-gameplay','floor-visual']:assert 'REJECT_DEFAULT' in decisions[n]['decision']
assert decisions['starter-art-rejected']['decision'].startswith('REJECT') and decisions['ash-art-private-fit']['decision']=='ACCEPT_CORRECTED_ASH_PAIR_FOR_PRIVATE_SCENE_FIT_ONLY'
history=O/'root-manifest-history';assert {q.name for q in history.iterdir()}=={'native-checkpoint-root-manifest-r1.py','native-checkpoint-root-manifest-r2.py','native-checkpoint-root-manifest-r3.py','native-checkpoint-final-input-manifest-root-r1.json','native-checkpoint-manifest-guard-root-r1','native-checkpoint-manifest-guard-root-r2','native-checkpoint-manifest-guard-root-r3'}
hr=[j(history/('native-checkpoint-manifest-guard-root-r'+str(i))/'RESULT.json') for i in (1,2,3)];assert hr[0]['exit_code']==1 and hr[1]['exit_code']==1 and hr[2]['exit_code']==0
runtime=[]
for kind,freezePath,wanted in [('developmentSource',S/'opening-turn-payoff-wording-strict-build-root-r1/final-seal-r1/RUNTIME-FREEZE.json','64c2a14ada2b24796535f9bb71d8a6acc534685365bcf4f5665b21bf18595353'),('heldDist',S/'target-clear-default-build-author-r1/RUNTIME-FREEZE.json','8bbaea72d9cb3b9757a2b8cb10ead190495ef61e6496e1ace0f942f635e00cf7')]:
 f=j(freezePath);mapping=f['inputs'] if kind=='developmentSource' else f['outputs'];assert digest(mapping)==wanted
 if kind=='developmentSource':
  observed={q.relative_to(R).as_posix() for r in ['src','public','desktop'] for q in (R/r).rglob('*') if q.is_file()};observed.update(['index.html','THIRD-PARTY.md','package.json','package-lock.json','tsconfig.json','vite.config.ts','scripts/build.mjs']);assert observed==set(mapping) and len(mapping)==89
 else:assert {q.relative_to(R/'dist').as_posix() for q in (R/'dist').rglob('*') if q.is_file()}==set(mapping) and len(mapping)==56
 code=[];media=[]
 for rel,h in mapping.items():
  q=R/rel if kind=='developmentSource' else R/'dist'/rel
  if q.suffix.lower() in ('.png','.wav'):
   ref=pathlib.Path(f['stage'])/rel if kind=='developmentSource' else pathlib.Path(f['stage'])/'dist'/rel
   assert q.is_file() and q.stat().st_size==ref.stat().st_size;media.append({'path':rel,'sha256':h,'bytes':q.stat().st_size})
  else:assert pin(q)['sha256']==h;code.append(pin(q))
 runtime.append({'domain':kind,'fullMembershipCount':len(mapping),'digestBoundToFrozenAuthority':wanted,'freeze':pin(freezePath),'freshNonmediaBodyCount':len(code),'freshNonmediaBodyPins':code,'mediaBodyCount':len(media),'mediaSizes':sum(x['bytes'] for x in media),'mediaQualification':'Existing held PNG/WAV SHA maps and sizes/path existence bound to prior frozen complete body admissibility; no redundant media-body replay or fresh universal media identity claim. Root publisher only copies evidence and prepends docs, no game/media write route.'})
assert pub['archiveImmutableAfterCOMPLETE'] and pub['originalFailuresPreserved'] and pub['soleCanonicalWriter']=='Root'
pg=S/'native-checkpoint-publication-guard-root-r1/RESULT.json';r=j(pg);assert r['exit_code']==0 and r['failure'] is None and r['memory_events_before']==r['memory_events_after']
for x in [r['initial'],*r['samples'],r['final']]:assert x['headroom']>=512*1048576 and x['current']-r['initial']['current']<=64*1048576 and x['free']>=1048576
log=(S/'native-checkpoint-publication-guard-root-r1/EXECUTION.log').read_text();reported=json.loads(log.strip());assert reported['literalCopies']==78 and reported['copiedBytes']==389662 and reported['documentPrefixes']==3 and reported['publicationSHA256']==pin(O/'PUBLICATION.json')['sha256']
rss={s.split(':')[0]:int(s.split()[1])*1024 for s in pathlib.Path('/proc/self/status').read_text().splitlines() if s.startswith(('VmHWM:','VmRSS:'))};assert max(rss.values())<24*1048576
out={'decision':'ACCEPT_EXACT_NATIVE_CHECKPOINT_LITERAL_PUBLICATION_ONLY','postPublicationAccepted':True,'publication':pin(O/'PUBLICATION.json'),'publisherMethod':pin(S/'native-checkpoint-publish-root-r1.py'),'README':pin(O/'README.md'),'copyRowsVerified':78,'literalCopyBytes':389662,'newDirectoryRegularFiles':87,'fullNewMembershipVerified':True,'literalCopyPins':copies,'documentPrefixRowsVerified':docs,'archive':pin(ap),'archiveCOMPLETEGate':pin(gatep),'archiveIndex':pin(O/'archive/INDEX.json'),'logicalArchiveRows':1278,'uniqueNewBlobs':1116,'originalGateDecisions':decisions,'RootManifestGenerationHistoryExits':[q['exit_code'] for q in hr],'runtimeBindings':runtime,'RootPublicationGuard':pin(pg),'RootGuardRows':len(r['samples']),'ownRSSBytes':rss,'limits':['Literal publication/copy/document prefix preservation engineering only; no art/game/default/completepayoff/animation/leg count/humanfun approval.','Existing COMPLETE gate verifies full new archive roundtrip; this review renews archive fullSHA/INDEX/copy identities and3 doc suffixes versus archived SHA rows, does not redo tar decoding or prior4513 body reads.','Ten copied original gates remain byte-exact including original spider/default-scene rejections and private-fit eligibility limits. Original R1 invalid manifest/R2 guessedtool failure methods+3 guards retained.','New empty-intent strictbuild and failed896 aggregate actual are later than fixed archive and remain outside archive; docs qualify them and R2 independent allocation caller/grammar pending actual.','Selected development source89/64c2 nonmedia/currentmembership checked, held dist56/8b nonmedia/currentmembership checked separately; media freeze-map/size histories inherited, no universal fresh media hash/OSreadonly/self-contained release claim.','No old archive/protectedZIP/Gitpack body read, Node/PIL/browser/runtime/build/Git/canonical writes or retirement occurred in reviewer lane. Root sole publisher writes are doc prepends and literal evidence copies, not game promotion.','Earlier spent-command cue author, distinct from Rootpublisher/preserver/newfloor/css/art authors. This does not endorse own-cue fun/visual quality.','Root and reviewer generic guards sampled shared cgroup64+512; not exclusive global attribution/universal unseen descendant closure. Bootstrap/display/finalseal outside guard disclosed.']}
(P/'PROOF.json').write_text(json.dumps(out,separators=(',',':'))+'\n');print(json.dumps({'decision':out['decision'],'copies':78,'membership':87,'ownRSS':rss},separators=(',',':')))
