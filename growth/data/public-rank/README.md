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

## Live and intraday checks

Exactly one root-level `YYYY-MM-DD.json` is eligible for the daily streak. A
same-day live check must not replace that canonical observation merely because
rank changed later in the day:

```sh
# Compact machine-readable result, no file writes.
python3 scripts/growth/monitor_public_rank.py --check-current

# Full capture on stdout, no file writes.
python3 scripts/growth/monitor_public_rank.py --stdout

# Full append-only local observation under intraday/YYYY-MM-DD/HHMMSS+ZZZZ.json.
python3 scripts/growth/monitor_public_rank.py --append-intraday
```

Intraday files carry `observation.kind=intraday`, explicitly set
`streak_eligible=false`, and live under a nested ignored directory. The streak
evaluator reads only root-level `*.json`, so these probes cannot add, replace,
or reset a canonical daily result. An identical timestamp collision fails
closed; the monitor never overwrites an existing intraday observation. Use
`--intraday-dir` with `--append-intraday` only when a different local evidence
root is required.
