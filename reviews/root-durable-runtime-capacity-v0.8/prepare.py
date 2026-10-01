from pathlib import Path
import hashlib
source=Path('reviews/root-tmp-runtime-capacity-v0.8/consolidate.py').read_text()
assert hashlib.sha256(source.encode()).hexdigest()=='577d71a18f3a9b45e8c9abcf20439daf2358ad98c2c687bac4297b9a7a52c283'
replacements={
 'root-tmp-runtime-capacity-v0.8':'root-durable-runtime-capacity-v0.8',
 'tmp-runtime-capacity-independent-v08-r1':'durable-runtime-capacity-independent-v08-r1',
 '500a2b3a0582c8d67a3519632b1447f93f7a58426665ced17488a767492ea525':'baa73b3df3105de3a10b4da3a894f4ee59349eb59d3966c9af98ac3545adbc06',
 "'blocks':s.st_blocks}":"'blocks':s.st_blocks,'uid':s.st_uid,'gid':s.st_gid,'xattrs':{key:os.getxattr(p,key,follow_symlinks=False).hex() for key in os.listxattr(p,follow_symlinks=False)}}",
 "audit['regular_files_hashed']==942 and len(audit['roots'])==13":"audit['regular_files_hashed']==432 and len(audit['roots'])==6",
 "len(set(roots))==13 and all(r.is_dir() and r.resolve().is_relative_to('/tmp') for r in roots)":"len(set(roots))==6 and all(r.is_dir() and r.resolve().is_relative_to('/workspace/scratch') for r in roots)",
 "'mtime_ns','ctime_ns']":"'mtime_ns','ctime_ns','uid','gid','xattrs']",
 "p.resolve().is_relative_to('/tmp')":"p.resolve().is_relative_to('/workspace/scratch')",
 'len(rows)==981 and len(directories)==39':'len(rows)==450 and len(directories)==18',
 'len(groups)==140':'len(groups)==141',
 "assert row['sha256']==group['sha256'] and row['after_hash']['size']==group['bytes'] and row['after_hash']['mode']==group['mode']":"assert row['sha256']==group['sha256'] and row['after_hash']['size']==group['bytes'] and row['after_hash']['mode']==group['mode']\n  assert all(row['after_hash'][k]==group[k] for k in ['uid','gid','xattrs'])",
 "os.statvfs('/tmp')":"os.statvfs('/workspace')",
 '942-byte/mode and39-directory':'432-byte/mode/ownership/xattrs and18-directory',
 'Current scene tests use production browser assets, not these package trees.':'These historical comparison roots have no active native host/build writer; current scene tests and UI playtest use separate web assets.',
 "assert m['type']==before[name]['type'] and m['mode']==before[name]['mode']":"assert all(m[k]==before[name][k] for k in ['type','mode','uid','gid','xattrs'])",
 "'all942FilesExactSizeModeSHA'":"'all432FilesExactSizeModeSHA'",
 "'all39DirectoryModesAndMembershipsExact'":"'all18DirectoryModesAndMembershipsExact'",
 'All paths/bytes/modes preserved, unique resources/ASAR untouched.':'All paths/bytes/modes/ownership/xattrs preserved, unique resources/ASAR untouched.',
 'TMP is not durable backup; every original official archive remains untouched.':'These durable historical package paths remain, but shared stock bytes are one storage copy; every original official archive remains untouched.',
 'Preserve every TMP comparison path':'Preserve every durable comparison path',
 'Free delta includes unrelated concurrent TMP use.':'Free delta includes unrelated concurrent workspace use.'
}
for old,new in replacements.items():
 assert old in source,old
 source=source.replace(old,new)
with Path('reviews/root-durable-runtime-capacity-v0.8/consolidate.py').open('x') as f:f.write(source)
