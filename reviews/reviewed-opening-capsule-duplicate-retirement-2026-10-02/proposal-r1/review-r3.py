import pathlib
p=pathlib.Path(__file__).parent/'review-r2.py';t=p.read_text();ns={'__file__':__file__};exec(compile(t[:t.index('exec(compile(s')],str(p),'exec'),ns);s=ns['s']
a='seen=set();decoded=0';z='seen=set();decoded=0;embeddedIndex=False';assert s.count(a)==1;s=s.replace(a,z,1)
a='   for member in tar:\n';z='''   for member in tar:
    if member.name=='INDEX.json':
     assert ident=='ce0f' and not embeddedIndex and member.isfile() and member.size==ci.stat().st_size;hh=hashlib.sha256();nn=0;body=tar.extractfile(member)
     while bb:=body.read(32768):hh.update(bb);nn+=len(bb)
     assert nn==member.size and hh.hexdigest()==sha(ci);embeddedIndex=True;continue
''';assert s.count(a)==1;s=s.replace(a,z,1)
a='assert seen==set(unique);after=meta(scratch)';z="assert seen==set(unique) and embeddedIndex==(ident=='ce0f');after=meta(scratch)";assert s.count(a)==1;s=s.replace(a,z,1)
a="'freshDecodedBytes':decoded";z="'freshDecodedBytes':decoded,'embeddedArchiveIndexExact':embeddedIndex";assert s.count(a)==1;s=s.replace(a,z,1)
s=s.replace('actualschema logicalBodies corrected only. No archive mismatch/resource defect inferred.','actualschema logicalBodies corrected. R2 wrongly assumed only blob members; preserved prior COMPLETE verifier shows ce0f also contains exact INDEX.json, now checked explicitly. No archive mismatch/resource defect inferred.')
exec(compile(s,str(p),'exec'),{'__file__':__file__})
