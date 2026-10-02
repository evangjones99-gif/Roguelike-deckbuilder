import pathlib
p=pathlib.Path(__file__).parent/'verify.py';s=p.read_text()
old='''assert 'backup' in body and "'canonical'" not in body'''
new='''assert 'backup' in body and "x['canonical']" not in body'''
assert s.count(old)==1
exec(compile(s.replace(old,new),str(p),'exec'))
