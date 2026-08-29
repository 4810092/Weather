# Daily public-rank snapshots

One `YYYY-MM-DD.json` is captured in `Asia/Tashkent` time. The schema contains:

- `config_fingerprint`, fixed app/store identifiers, and methodology caveats;
- `surfaces.apple.category` and `surfaces.apple.search[query_id]`;
- `surfaces.google.category[profile_id]` and `surfaces.google.search[profile_id][query_id]`;
- `methodology.fixed_query_ids`, preserving the configured query set even when
  a source omits an entire query surface;
- per-surface status, source URL, response SHA-256, exact target rank or a `>observed_count` bound, target item, and first ten unique apps;
- `diagnostic_capture_complete` across every configured surface, including
  auxiliary Apple searches. Schema-v1 field `capture_complete` is retained as
  a legacy alias with the same diagnostic meaning;
- `goal_evidence_complete` and a three-state fail-closed `evaluation` for the
  daily Top-10 goal. A diagnostic error does not make a provable goal pass or
  failure unknown. The monitor exits non-zero only when missing required goal
  evidence could change the day's result.

Do not edit a snapshot to make a day pass. Re-run with `--replace` only to correct a known same-day capture problem, and record the reason in the weekly review. A configuration change starts a new comparability series because the fingerprint changes.
