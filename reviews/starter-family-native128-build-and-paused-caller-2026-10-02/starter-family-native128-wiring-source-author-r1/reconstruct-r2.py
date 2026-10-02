"""Narrow successor for retained pre-output exact-span failure; original method immutable."""
import os,hashlib
from pathlib import Path
p=Path(__file__).with_name('reconstruct.py');fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME)
with os.fdopen(fd) as f:original=f.read()
a="s=swap(s,'ready = images.length === 7;','ready = images.length === 13;',ops['coherent-native128.ts'])"
b="s=swap(s,'images.length === 7','images.length === 13',ops['coherent-native128.ts'])\ns=swap(s,'Native seven-image contract','Native thirteen-image contract',ops['coherent-native128.ts'])"
assert original.count(a)==1
successor=original.replace(a,b);assert successor.replace(b,a)==original
exec(compile(successor,str(p)+'+r2-exact-span-successor','exec'))
