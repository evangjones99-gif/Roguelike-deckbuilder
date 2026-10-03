import pathlib
p=pathlib.Path(__file__).parent;s=(p/'verify.py').read_text()
old="len(newArtBodies)==6"
new="len({logical[path]['sha256'] for path in newArtBodies})==6"
assert s.count(old)==1;s=s.replace(old,new)
s=s.replace("'newArtOriginalBodies':sorted(newArtBodies),","'newArtFrozenOriginalPaths':sorted(newArtBodies),'newArtUniqueBodies':6,")
exec(compile(s,str(p/'verify.py'),'exec'))
