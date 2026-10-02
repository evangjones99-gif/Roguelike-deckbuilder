from pathlib import Path
S=Path('/workspace/scratch')
j=S/'judge-second-three-png-sharing-root-r2.py';newj=S/'judge-second-three-png-sharing-root-r3.py';assert not newj.exists()
b=j.read_text().replace('second-three-png-producer-judgment-root-r2.json','second-three-png-producer-judgment-root-r3.json')
old="out.write_text(json.dumps(j,indent=2)+'\\n');print(json.dumps({'judgment':str(out),'sha256':sha(out),'commit':p['commit'],'actionPerformed':False}))"
new="""with out.open('x') as f:json.dump(j,f,indent=2);f.write('\\n');f.flush();os.fsync(f.fileno())
fd=os.open(out.parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
try:os.fsync(fd)
finally:os.close(fd)
print(json.dumps({'judgment':str(out),'sha256':sha(out),'commit':p['commit'],'actionPerformed':False,'authorizationFileAndParentFsyncReturned':True}))"""
assert b.count(old)==1;b=b.replace(old,new);newj.write_text(b)
p=S/'publish-reviewed-recovery-admission-root-r1.py';newp=S/'publish-reviewed-recovery-admission-root-r2.py';assert not newp.exists()
b=p.read_text().replace("P=S/'recovery-admission-push-root-r1'", "P=S/'recovery-admission-push-root-r2'")
b=b.replace("'judge-second-three-png-sharing-root-r2.py']", "'judge-second-three-png-sharing-root-r2.py','judge-second-three-png-sharing-root-r3.py','publish-reviewed-recovery-admission-root-r2.py','draft-durable-recovery-controls-root-r1.py']")
old="(P/'PUSH-CONFIRMED.json').write_text(json.dumps({'commit':head,'remote':remote,'confirmed':True,'clean':True,'gateSHA256':sha(gate),'methodSHA256':sha(S/'share-second-three-retained-pngs-root-r3.py'),'holdSHA256':sha(R/'AGENTS.md'),'copiedBytes':sum(v['bytes'] for v in records.values()),'noStorageAction':True},indent=2)+'\\n')"
new="""with (P/'PUSH-CONFIRMED.json').open('x') as f:json.dump({'commit':head,'remote':remote,'confirmed':True,'clean':True,'gateSHA256':sha(gate),'methodSHA256':sha(S/'share-second-three-retained-pngs-root-r3.py'),'holdSHA256':sha(R/'AGENTS.md'),'copiedBytes':sum(v['bytes'] for v in records.values()),'noStorageAction':True,'durableReceiptFileAndParentFsync':True},f,indent=2);f.write('\\n');f.flush();os.fsync(f.fileno())
fd=os.open(P,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
try:os.fsync(fd)
finally:os.close(fd)"""
assert b.count(old)==1;b=b.replace(old,new);newp.write_text(b)
# Fresh producer must reference the fresh durable confirmed-push receipt.
c=newj.read_text();assert c.count('recovery-admission-push-root-r1')==1;newj.write_text(c.replace('recovery-admission-push-root-r1','recovery-admission-push-root-r2'))
print(str(newp));print(str(newj))
