# Receipt clarification

The frozen REVIEW.md capacity paragraph quotes **93,634,560 bytes** from the earlier read-only workspace inspection as the initial durable free space. The actual execution preflight in `capacity-before.json` measured **86,913,024 bytes** free at 2026-10-01T01:24:15Z. Use that execution receipt for the run's initial durable value. Temporary reservation, sampled usage, object/blob/index results and cleanup remain correct. The full new evidence remains below 1 MB. Preserve the original report and first manifest unchanged; this correction is append-only.
