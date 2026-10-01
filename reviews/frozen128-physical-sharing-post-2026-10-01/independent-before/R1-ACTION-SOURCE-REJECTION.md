# Original action-source rejection — retained r1

The original unexecuted share.py SHA256 `552668d636d65011f1faa51e7858c3e16e2eafedecd28df01085ee21526b3c60` is **REJECTED for action**. Exact physical-sharing comparison is separately acceptable, but this source can durably replace media directory entries without first making its new named provenance/journal directory entries durable.

It fsyncs BEFORE/JOURNAL file content, but does not fsync the new evidence directory’s parent after mkdir, the evidence directory after BEFORE/JOURNAL/RESULT creation, or the temporary recipient link directory before durably reporting PREPARED. A crash could therefore leave durable replacements with missing named evidence or an overclaimed prepared-link state. This is a narrow preservation blocker, not rejection of body equivalence or the freeing-only guard.

The blocker was reported to Root before any action. Root retained this source unchanged and supplied fresh share-r2.py for separate review. The r1 rejection remains historical and is not silently rewritten by the later r2 decision. No r1 action was attempted by this reviewer.
