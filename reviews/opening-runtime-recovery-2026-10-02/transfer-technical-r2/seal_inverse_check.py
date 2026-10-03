import pathlib,json,gzip,hashlib,yaml,subprocess
P=pathlib.Path('/workspace/scratch/opening-runtime-transfer-source-r2')
O=pathlib.Path('/workspace/scratch/opening-runtime-transfer-technical-r2')
def sha(b):return hashlib.sha256(b).hexdigest()
seal=(P/'SOURCE-SEAL.json').read_bytes();s=json.loads(seal)
assert sha(seal)=='55ed1038ea01a94aae86c39c72599c1d35092d1e36e74f8dd9d1871afab6ddcb'
assert set(x.name for x in P.iterdir())=={'SOURCE-SEAL.json'}|{x['name'] for x in s['files']}
for x in s['files']:
 p=P/x['name'];assert p.is_file() and not p.is_symlink();b=p.read_bytes();assert len(b)==x['bytes'] and sha(b)==x['sha256']
total=sum(x.stat().st_size for x in P.iterdir());assert total==s['familyBytesIncludingSeal']==97988 and total<=s['familyCapBytes']==131072
m=json.loads((P/'MANIFEST.json').read_bytes());external=[]
for key in ['immutableR1Source','recoveryMap','priorActual8cdfTransfer']:
 d=m[key]
 for x in d['files']:
  p=pathlib.Path(d['root'])/x['name'];b=p.read_bytes();assert len(b)==x['bytes'] and sha(b)==x['sha256'];external.append({'path':str(p),'bytes':len(b),'sha256':sha(b)})
inverse=json.loads(gzip.decompress((P/'R2-INVERSE.json.gz').read_bytes()));roundtrips=[]
def apply(source,hunks,reverse=False):
 lines=source.splitlines(keepends=True);out=[];cursor=0
 for h in hunks:
  index=h['afterLineStart' if reverse else 'beforeLineStart'];old=h['after' if reverse else 'before'];new=h['before' if reverse else 'after'];expected=old.splitlines(keepends=True)
  assert index>=cursor and ''.join(lines[index:index+len(expected)])==old
  out.extend(lines[cursor:index]);out.append(new);cursor=index+len(expected)
 out.extend(lines[cursor:]);return ''.join(out)
for f in inverse['files']:
 old=(pathlib.Path(inverse['R1ExternalRoot'])/f['oldName']).read_bytes();new=(P/f['newName']).read_bytes()
 assert sha(old)==f['oldSHA256'] and sha(new)==f['newSHA256']
 assert apply(old.decode(),f['hunks']).encode()==new
 assert apply(new.decode(),f['hunks'],True).encode()==old
 roundtrips.append({'oldName':f['oldName'],'newName':f['newName'],'forwardExact':True,'reverseExact':True,'hunks':len(f['hunks'])})
w=yaml.load((P/'recover-opening-evidence.yml').read_bytes(),Loader=yaml.BaseLoader);j=w['jobs']['transfer'];steps=j['steps'];pins=json.loads((P/'PINSET.json').read_bytes())
assert w['permissions']=={} and j['permissions']=={'contents':'read'}
assert w['on']=={'push':{'branches':['codex/lanternbound-production'],'paths':['.github/workflows/recover-opening-evidence.yml']},'workflow_dispatch':{}}
assert j['runs-on']=='ubuntu-24.04' and j['timeout-minutes']=='10' and len(steps)==3
assert steps[0]['env']=={'GITHUB_TOKEN':'${{ github.token }}'} and steps[0]['timeout-minutes']=='4'
assert steps[0]['shell']=='bash --noprofile --norc -euo pipefail {0}'
subprocess.run(['bash','-n'],input=steps[0]['run'].encode(),check=True,capture_output=True,timeout=10)
prefix='${{ runner.temp }}/opening-runtime-transfer-${{ github.run_id }}-${{ github.run_attempt }}/'
for group,step in zip(['canonical','containers'],steps[1:]):
 assert step['uses']=='actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02' and step['timeout-minutes']=='4'
 params=step['with'];assert set(params)=={'name','path','if-no-files-found','compression-level','retention-days','overwrite','include-hidden-files'}
 assert {k:params[k] for k in ['if-no-files-found','compression-level','retention-days','overwrite','include-hidden-files']}=={'if-no-files-found':'error','compression-level':'0','retention-days':'30','overwrite':'false','include-hidden-files':'false'}
 expected=[prefix+group+'/'+(x['path'] if group=='canonical' else pathlib.PurePosixPath(x['gitPath']).name) for x in pins[group]]+[prefix+group+'/VERIFICATION.json']
 assert params['path'].splitlines()==expected
 assert all('8cdf' not in x for x in expected)
proof={'sourceOnly':True,'sourceSealSHA256':sha(seal),'familyBytesIncludingSeal':total,'ownSourceCapBytes':49152,'allTenSealedFilesVerified':True,'noExtraFilesOrSymlinks':True,'externalExactBodiesVerified':external,'inverseRoundtrips':roundtrips,'yamlExactTriggersPermissionsUploadPathLists':True,'syntaxOnlyBashPassed':True,'embeddedExactPythonPreviouslyVerified':True,'officialActionPin':'ea165f8d65b6e75b540449e92b4886f43607fa02','noNetworkOrProductionMainOrArchivesExecuted':True}
(O/'SEAL-INVERSE-PROOF.json').write_text(json.dumps(proof,indent=2)+'\n')
print(json.dumps({'seal':sha(seal),'familyBytes':total,'externalPins':len(external),'roundtrips':roundtrips,'exactPaths':54}))
