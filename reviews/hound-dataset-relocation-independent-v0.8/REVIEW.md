# Independent comparison-dataset preservation assessment

**Accept the proposed relocation of only the two uncompressed working JSON files, subject to root's verified move and preserved access paths.** This reviewer performed no move and changed no production files or original study inputs.

Both gzip files were streamed through decompression to EOF, validating their complete contents and gzip trailers. The resulting sizes and SHA-256 hashes exactly match the raw files and the frozen study manifest:

| Dataset | Raw/decompressed bytes | Raw/decompressed SHA-256 |
|---|---:|---|
| renderer-comparison-r3.json | 92,205,657 | a86828b78db64ac203ecae334aafe7de32d1aeda4c3a3cf736ede2ba7afc624c |
| retaliation-comparison.json | 58,899,964 | c4fa713e0056b13359a54a962b99551f220d3d7e7df11e2879661ee0c5755959 |

The two durable gzip files total 5,330,366 bytes and independently match their original manifest hashes. All 93 study-manifest entries were streamed and verified against their original sizes and hashes; the manifest remained unchanged and is preserved here. Detailed checks are in `ASSESSMENT.json`.

The proposed move relocates 151,105,621 bytes of redundant working data. Keep the original gzip files, old art, studies, reviews and formal release archives unchanged. Root must move the two raw files to unique temporary paths, verify exact bytes/modes before and after, and retain the original paths as symlinks. Those temporary working copies preserve convenient comparison access; they are not a durable backup. Complete dataset contents remain reconstructable from the durable gzip files.

Content hash/size identity is preserved, but `lstat` type, inode and physical location of the raw paths necessarily change. This is a scoped content-preservation acceptance, not a claim that filesystem identity or every consumer's symlink behavior stays identical. Root must coordinate readers and record a post-move receipt. No gameplay, renderer-quality or art acceptance follows from this assessment.
