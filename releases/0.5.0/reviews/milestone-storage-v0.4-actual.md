# Independent v0.4 actual preservation result

Decision: accept **partial development milestone storage**, with no public publication or commercial/AAA approval. The successful workflow preserves two of the six binary archives, plus three metadata assets. The original failure and source reviews remain preserved. This reviewer authored the narrowly scoped Accept-header repair; the lead independently reviewed that repair before execution. This document independently checks its actual outcome, rather than claiming independence from repair authorship.

Actual execution: PUSH run `36779379544`, job `110105312046`, repaired commit `3ece2f4`. Personally compared its workflow bytes with the repaired source: SHA256 `90d317a7207b8a6e66e52b016d4e8024a4244730719b0157863ce0b71d31f81f`. The retained job log records the passing partial-preservation notice and diagnostic artifact `11126708197` (846 bytes, SHA256 `b877883e7e288d7d76553ef7a2e79968d08633a24823f1790541c89e5ca5c0be`). Personally hashed raw report: `2945882899c102a18ebee154e9417f1ea54c01023d9eb4a9fcf3624d5382fb88`. The workflow executed five byte-for-byte readbacks before reporting success; this reviewer inspected its source and retained evidence, and personally cross-checked all five asset sizes/digests with two read-only connected GitHub API requests. I did not independently download the complete 178 MB asset a second time.

Release `400449104` currently reports `draft: true`, `prerelease: true`, `published_at: null`, and `immutable: false`; tag `v0.4.0` declares target commit `dae9758ea40f849b36d9891c859b7bf6df09d242` (annotated-tag identity verified in the source review). Both release and asset-list API responses contain exactly the same five uploaded assets:

| Asset | GitHub ID | Bytes | SHA256 |
|---|---:|---:|---|
| Actual tested native Windows ZIP | 601826618 | 178481506 | `ec5203567cf15bcae28c6b1b4e908469fd075197bba6b67cfab2185f2b9d8927` |
| Original native evidence ZIP | 601826777 | 1993027 | `55f967466653acda8fe52545892590de663629f8ed28c8e697d7b0c9f07dcd3a` |
| manifest.json | 601826795 | 2615 | `59b252300f50244d06ea0d40e6d4e2318a02806bcfa5d719a2ca7186217fbb67` |
| SHA256SUMS | 601826799 | 608 | `0b227baad42e6529cff939598903533171a24b078e792536cfcebbaadb38c0b4` |
| preservation-coverage.json | 601826812 | 885 | `aa27c5b27f92f143ea4f574dcba9a13c60f00439947a9a8027d9b1a8e9aceaab` |

The release body explicitly retains known v0.4 presentation limitations and rejects polished/AAA/commercial promotion. Four binary archives remain outside this draft: Linux, source, web, and the separately repacked native Windows archive. The fourth is repacked native output, not a crossbuilt Windows executable. Local historical archives remain their own preserved evidence.

Draft assets avoid Actions artifact expiry, but this is not permanent immutable storage: administrators can alter/delete releases, account availability matters, and current authorized connector access does not establish public or anonymous access. Plain workspace API credentials previously returned 403; connected read-only requests succeeded during this review. No release mutation, publication, replacement, deletion, or new storage action was performed by this reviewer.

Evidence: `reviews/milestone-storage-v0.4/run-36779379544-1/{report.json,job-log.txt,artifact-transfer.json}`; retained initial failure and `milestone-storage-v0.4-repair1.md`; independently queried metadata snapshot below (2026-09-30 UTC).

```json
{
  "release": {
    "id": 400449104,
    "tag_name": "v0.4.0",
    "target_commitish": "dae9758ea40f849b36d9891c859b7bf6df09d242",
    "draft": true,
    "prerelease": true,
    "immutable": false,
    "published_at": null,
    "html_url": "https://github.com/evangjones99-gif/Roguelike-deckbuilder/releases/tag/untagged-fc0f44877e9fdadfb1d9",
    "updated_at": "2026-09-30T21:26:16Z"
  },
  "assets": [
    {
      "id": 601826777,
      "name": "hollowpact-0.4.0-windows-native-evidence.zip",
      "size": 1993027,
      "digest": "sha256:55f967466653acda8fe52545892590de663629f8ed28c8e697d7b0c9f07dcd3a",
      "state": "uploaded"
    },
    {
      "id": 601826618,
      "name": "hollowpact-0.4.0-windows-native-tested-x64.zip",
      "size": 178481506,
      "digest": "sha256:ec5203567cf15bcae28c6b1b4e908469fd075197bba6b67cfab2185f2b9d8927",
      "state": "uploaded"
    },
    {
      "id": 601826795,
      "name": "manifest.json",
      "size": 2615,
      "digest": "sha256:59b252300f50244d06ea0d40e6d4e2318a02806bcfa5d719a2ca7186217fbb67",
      "state": "uploaded"
    },
    {
      "id": 601826812,
      "name": "preservation-coverage.json",
      "size": 885,
      "digest": "sha256:aa27c5b27f92f143ea4f574dcba9a13c60f00439947a9a8027d9b1a8e9aceaab",
      "state": "uploaded"
    },
    {
      "id": 601826799,
      "name": "SHA256SUMS",
      "size": 608,
      "digest": "sha256:0b227baad42e6529cff939598903533171a24b078e792536cfcebbaadb38c0b4",
      "state": "uploaded"
    }
  ]
}
```

