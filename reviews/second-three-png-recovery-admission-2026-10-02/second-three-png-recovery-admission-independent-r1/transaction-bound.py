import pathlib,os,json,hashlib,resource,math
p=pathlib.Path(__file__).parent;path=pathlib.Path('/workspace/scratch/media-loose-png-recovery-proposal-author-r2/PROPOSAL.json')
fd=os.open(path,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW)
with os.fdopen(fd,'rb') as f:b=f.read()
assert hashlib.sha256(b).hexdigest()=='45ed75b5078c84e32981ba86b43f62826b00c53278ef8ea2f9888d661b8fd8d5'
e=json.loads(b);pairs=e['pairs'];stamp=9999999999999999999
before={'utcNs':stamp,'pairs':pairs,'initialFree':9999999999999999999,'proposalSHA256':'f'*64,'gateSHA256':'f'*64,'judgmentSHA256':'f'*64,'pushSHA256':'f'*64,'commit':'f'*40}
journal=[];post=[]
for x in pairs:
 ap=x['anchor']['path'];bp=x['candidate']['path'];tmp=bp+'.root-share-second-r3.tmp'
 journal += [{'utcNs':stamp,'operation':'PRE_LINK','source':ap,'target':bp,'temp':tmp},{'utcNs':stamp,'operation':'LINK_DURABLE','target':bp,'temp':tmp},{'utcNs':stamp,'operation':'REPLACED_DURABLE','target':bp,'tempAbsent':True}]
 metadata={k:9999999999999999999 for k in x['anchor']['fstat']}
 post.append({'candidate':bp,'canonical':ap,'sha256':'f'*64,'candidateMetadata':metadata,'canonicalMetadata':metadata})
result={'normal':True,'pairs':post,'grossAllocationBytes':9999999999999999999,'windowFreeBefore':9999999999999999999,'windowFreeAfterBeforeResultWrite':9999999999999999999,'netWindowGainBytes':-9999999999999999999,'allPathsBodiesKept':True,'allTempAbsent':True,'losses':'Three private inodes/time/write isolation lost; anchors nlink5 to6 and ctime changes, one previous alias unresolved per anchor. No original-inode backup, no all-three atomicity, durable prefix only. All bytes/paths/provenance remain needed.','noOtherActionAuthorized':True}
sizes={'BEFORE.json':len((json.dumps(before,indent=2)+'\n').encode()),'JOURNAL.jsonl':sum(len((json.dumps(r)+'\n').encode()) for r in journal),'RESULT.json':len((json.dumps(result,indent=2)+'\n').encode())}
frsize=os.statvfs('/workspace/Roguelike-deckbuilder').f_frsize;assert frsize==4096
allocated=sum(math.ceil(n/frsize)*frsize for n in sizes.values())+2*frsize
assert allocated<64*1024
rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss;assert rss<24*1024
bound={'method':'Static JSON size model with fixed exactproposal3pairs/paths and conservative20digit nativeinteger representations; action notexecuted.','upperLogicalFileBytes':sizes,'sumLogicalBytes':sum(sizes.values()),'blockBytes':frsize,'modeledRoundedFilesPlusTwoDirectoryBlocks':allocated,'scopeBoundBytes':65536,'qualification':'Conservative modeled controlwrites; filesystemmetadata/journal allocator notuniversally bounded bythis model. Fresh56 admission and1MiB observedstop remainrequired, no media backup/copy. Allthreebefore inputs fixed byexactproposalpin.','ownRSSKiB':rss}
(p/'TRANSACTION-BOUND.json').write_text(json.dumps(bound,indent=2)+'\n');print(json.dumps(bound))
