# Daily public-rank snapshots

One `YYYY-MM-DD.json` is captured in `Asia/Tashkent` time. The schema contains:

- `config_fingerprint`, fixed app/store identifiers, and methodology caveats;
- `surfaces.apple.category` and `surfaces.apple.search[query_id]`;
- `surfaces.google.category[profile_id]` and `surfaces.google.search[profile_id][query_id]`;
- per-surface status, source URL, response SHA-256, exact target rank or a `>observed_count` bound, target item, and first ten unique apps;
- `capture_complete` across every configured surface and separate fail-closed `evaluation` for the daily Top-10 goal.

Do not edit a snapshot to make a day pass. Re-run with `--replace` only to correct a known same-day capture problem, and record the reason in the weekly review. A configuration change starts a new comparability series because the fingerprint changes.
