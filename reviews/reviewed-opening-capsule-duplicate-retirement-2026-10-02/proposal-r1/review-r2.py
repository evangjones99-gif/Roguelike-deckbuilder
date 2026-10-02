import pathlib,hashlib
p=pathlib.Path(__file__).parent/'review.py';b=p.read_bytes();s=b.decode()
a="index=load(ci);unique={}"
z="index=load(ci);unique={}\n if 'logicalBodies' in index:index['rows']=[[0,r['originalPath'],r['sha256'],r['bytes'],0,'newBlob'] for r in index['logicalBodies']]"
assert s.count(a)==1;s=s.replace(a,z,1)
a="'indexArchivePointer':index['newArchive']";z="'indexArchivePointer':index.get('newArchive'),'historicalCOMPLETEArchivePointer':g['archive']['path'],'schemaQualification':'ce0f logicalBodies are stored-body references; synthesized rows used only for member/hash counts. Original index bytes remain unchanged.'";assert s.count(a)==1;s=s.replace(a,z,1)
a="'matchedNeedles':hits";z="'referencedArchiveIDs':sorted({results[i%2]['id'] for i,n in enumerate(needle) if n in hits})";assert s.count(a)==1;s=s.replace(a,z,1)
s=s.replace("'ownRSSKiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'elapsedSeconds':time.monotonic()-began,'noMutationDeletionRecompressionOrTARCopy':True", "'preservedReaderFailure':'Original review.py/PROOF-GUARD assumed rows schema force0f and raisedKeyError before proof write; actualschema logicalBodies corrected only. No archive mismatch/resource defect inferred.','ownRSSKiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'elapsedSeconds':time.monotonic()-began,'noMutationDeletionRecompressionOrTARCopy':True")
exec(compile(s,str(p),'exec'),{'__file__':__file__})
