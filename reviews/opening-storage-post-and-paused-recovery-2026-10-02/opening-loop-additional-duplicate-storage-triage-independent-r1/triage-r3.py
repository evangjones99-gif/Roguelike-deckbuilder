from pathlib import Path
p=Path(__file__).with_name('triage.py')
s=p.read_text().replace("json.dumps(j,indent=2)","json.dumps(j,separators=(',',':'))").replace("'matchLines':lines[:5]","'matchLines':lines[:1]")
old="receipts.append({'pin':pinned(q),'receipt':json.loads(q.read_bytes())})"
new="j=json.loads(q.read_bytes());receipts.append({'pin':pinned(q),'receiptSelectedFields':{k:v for k,v in j.items() if k in ['confirmedPush','clean','localHEAD','remoteHEAD','head','remoteHead','priorActionHEAD','qualification']},'fullReceiptRetainedAtPinnedOriginal':True})"
assert old in s;s=s.replace(old,new)
exec(compile(s,str(p)+' [compact receipt-reference successor]', 'exec'))
