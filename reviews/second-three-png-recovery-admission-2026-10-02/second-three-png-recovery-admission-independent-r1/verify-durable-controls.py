import pathlib,os,json,hashlib,ast,resource,time
p=pathlib.Path(__file__).parent;s=pathlib.Path('/workspace/scratch')
def read(path):
 fd=os.open(path,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW)
 with os.fdopen(fd,'rb') as f:return f.read()
def rec(path):
 b=read(path);return {'path':str(path),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
publisher=s/'publish-reviewed-recovery-admission-root-r2.py';producer=s/'judge-second-three-png-sharing-root-r3.py'
pub=read(publisher).decode();prod=read(producer).decode();tree=ast.parse(pub);ast.parse(prod)
assert rec(publisher)['sha256']=='b5fcfa84d67b07e1bb3f8d06648091d140bb0b088d714c8237ab0a3ef50abad3'
assert rec(producer)['sha256']=='ee13fd19c0e38195269b5cb794fae24ff6f092cb2bdbf16cbbbf714da6d18c88'
assert "with (P/'PUSH-CONFIRMED.json').open('x')" in pub and 'os.fsync(f.fileno())' in pub and 'fd=os.open(P,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)' in pub
assert "with out.open('x')" in prod and 'os.fsync(f.fileno())' in prod and 'fd=os.open(out.parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)' in prod
assert "recovery-admission-push-root-r2/PUSH-CONFIRMED.json" in prod
lists=[]
for node in tree.body:
 if isinstance(node,ast.For) and isinstance(node.iter,ast.List):lists.append(ast.literal_eval(node.iter))
assert len(lists)==2
records=[];otherBytes=0;otherCount=0
for folder in lists[0]:
 if folder==p.name:continue
 for path in sorted((s/folder).rglob('*')):
  if path.is_file():assert not path.is_symlink();r=rec(path);records.append(r);otherBytes+=r['bytes'];otherCount+=1
for name in lists[1]:
 path=s/name;assert not path.is_symlink();r=rec(path);records.append(r);otherBytes+=r['bytes'];otherCount+=1
payloadUpper=otherBytes+192*1024;assert payloadUpper<512*1024
proof=json.loads(read(p/'PROOF.json'));oldGate=json.loads(read(proof['priorAcceptedGate']['path']))
authorProposal=oldGate['proposal'];hold=oldGate['currentHold'];selected=oldGate['selectedMap']
for r in [authorProposal,hold,selected]:assert rec(r['path'])==r
originals=[rec(s/name) for name in ['publish-reviewed-recovery-admission-root-r1.py','judge-second-three-png-sharing-root-r2.py','draft-durable-recovery-controls-root-r1.py']]
rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss;assert rss<24*1024
data={'publisher':rec(publisher),'producer':rec(producer),'authorProposal':authorProposal,'currentHold':hold,'selectedMap':selected,'supersededUnexecutedDraftsAndGenerator':originals,'publicationOtherSourceRecords':records,'otherPayloadBytes':otherBytes,'otherSourceFileCount':otherCount,'reviewPacketBoundBytes':192*1024,'publicationCopiedPayloadUpperBytes':payloadUpper,'publicationCopiedPayloadBoundBytes':512*1024,'publicationAuxiliaryQualification':'COPY-IDENTITIES/README andGitobjects/log costs notincluded in copiedpayload predicate; finitefew additional controls. Current exactsource sum plusreview192KiB cap leaves statedmargin; exact method rechecks56 disk beforeaction. No blanket512KiB bound for Gitkernel/networklogs.','durableCompositeSequence':'Publisher fsyncs exclusivePUSHreceipt file anditsPdirectory. Pnewentry inexistingScratchparent is not separatelyfsynced bypublisher. Producerthen fsyncs exclusivejudgment file andexistingScratchparent, makingboth judgmententry andpriornewPdirectoryentry durable beforeaction. Publisherreceipt alone notfullancestor durability certificate; sequence throughdurable producercompletion required.','approvedInvocations':[{'script':rec(publisher),'workMiB':256,'diskAdmissionMiB':56,'reserveMiB':512,'operation':'newowned reviewfolder/sourcecopies +selectiveGitcommit/push/lsremote/clean; no media action'},{'script':rec(producer),'workMiB':64,'diskAdmissionMiB':56,'reserveMiB':512,'operation':'GateSHA CLIargument exact; checkcurrentpublishedgate/method/push, writedurablefinite judgment only'},{'script':proof['methodR3'],'workMiB':64,'diskAdmissionMiB':56,'reserveMiB':512,'operation':'exactthreepath sharing onlyafternewpush/durablejudgment/rootgrant'}],'guardQualification':'Filename/prefix filter not exactallowlist/body/child enforcement; Gatepins andRoot coordinatedsolewriter bindonly reviewed invocations. Allother56-threshold scripts/actionspending review.','ownRSSKiB':rss,'utcNs':time.time_ns()}
(p/'DURABLE-CONTROLS-PROOF.json').write_text(json.dumps(data,indent=2)+'\n')
print(json.dumps({'publisher':data['publisher'],'producer':data['producer'],'otherPayloadBytes':otherBytes,'copyPayloadUpperBytesWith192KiBReviewerCap':payloadUpper,'ownRSSKiB':rss,'durability':'Compositepublisher+producer sequence accepted beforeaction; publisheralone parentcreation qualification retained'}))
