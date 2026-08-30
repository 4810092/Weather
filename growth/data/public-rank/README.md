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

Do not edit a snapshot to make a day pass. A configuration change starts a new
comparability series because the fingerprint changes. The unattended hosted
path never uses `--replace`; correction of a known manual capture problem is a
reviewed repository operation, not an automated rerun.

## Hosted immutable state

`.github/workflows/uz-rank-monitor.yml` is scheduled for `19:05 UTC` (`00:05`
Asia/Tashkent). It reads code and configuration only from protected `master`,
then persists the new daily snapshot, same-date evaluation, and a hash-bound
receipt on `growth-observations`. Code from that mutable branch is never
executed by the write-capable job.

Before capture, every default-branch canonical file must be present with
byte-identical content in the observation branch. Before persistence, the
remote branch head must still equal the parent recorded by the read-only job.
Installation uses exclusive links, the commit allowlist contains exactly three
new files, and the push is non-force. An existing day or changed branch parent
fails without capture or overwrite. A rerun therefore cannot replace the first
committed day.

If required rank evidence is `unknown`, the workflow still commits that exact
failure evidence and its receipt, then ends red. This prevents a later retry
from silently selecting a more favorable same-day result. Receipts live under
`hosted-receipts/`, so the streak evaluator's root-level `*.json` scan cannot
mistake them for canonical days.

The observation branch does not itself update the public dashboard or GitHub
Pages. Those surfaces change only after review promotes the exact branch bytes
to `master` and the existing validation pipeline succeeds.

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
