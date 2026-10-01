# Audit filename correction and retained auxiliary failure

The immutable `REVIEW.md` refers to `root-snapshot-r1-error.txt`. The copied file is actually named **`root-root-snapshot-r1-error.txt`**, because the independent input-copy step prefixes every root-owned filename with `root-`. It is byte-identical to the canonical root failure file; SHA256 `73a77dc0f75dd4a6fd13160d1a4792f4a4d827cb7f52774cf5606466505a92a8`.

An auxiliary print-only command attempted the shorter filename after the verifier had already passed. It failed with `FileNotFoundError`, as retained in `auxiliary-listing-r1-failure.txt`. This was a reporting path mistake; no storage assertion, original input or verification result changed. The original 25-file `SHA256.json` and report are preserved unchanged. `SHA256-with-errata.json` freezes them and these added corrections. The raw diagnostic report is 1669 bytes; its original compressed Actions ZIP wrapper is 850 bytes.
