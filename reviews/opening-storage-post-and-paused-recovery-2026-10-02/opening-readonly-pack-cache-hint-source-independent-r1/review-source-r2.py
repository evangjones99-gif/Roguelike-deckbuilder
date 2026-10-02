from pathlib import Path
p=Path(__file__).with_name('review-source-r1.py');s=p.read_text()
old="if name.endswith('.json'):entry['historicalControl']=json.loads(b)"
new="if name.endswith('.json'):\n   h=json.loads(b);entry['historicalControl']={k:v for k,v in h.items()if isinstance(v,(bool,int,float,type(None)))or isinstance(v,str)and len(v)<600};entry['historicalControlKeys']=list(h)"
assert s.count(old)==1;s=s.replace(old,new)
old="else:entry['historicalReviewText']=b.decode()"
new="else:entry['historicalReviewText']='\\n'.join(line for line in b.decode().splitlines()if any(t in line.lower()for t in ['accept','metadata','source','readonly','read-only','pack','scope','cause','causal','grant','preserv','failure','risk','sha','fresh']))[:3300]"
assert s.count(old)==1;s=s.replace(old,new)
exec(compile(s,str(p),'exec'),{'__name__':'__main__','__file__':str(p)})
