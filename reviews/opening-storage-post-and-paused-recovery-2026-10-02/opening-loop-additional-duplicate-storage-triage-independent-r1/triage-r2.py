from pathlib import Path
p=Path(__file__).with_name('triage.py')
s=p.read_text().replace("json.dumps(j,indent=2)","json.dumps(j,separators=(',',':'))").replace("'matchLines':lines[:5]","'matchLines':lines[:1]")
assert s!=p.read_text()
exec(compile(s,str(p)+' [compact proof serialization successor]', 'exec'))
