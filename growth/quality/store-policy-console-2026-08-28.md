# Store policy console check — 2026-08-28

Status: **PASS for the current point-in-time policy gate**. This is a mutable
console observation, not a substitute for the next complete weekly export.

## App Store Connect

- Public iOS version `1.0.1` is `Ready for Distribution`.
- The two latest submitted versions, iOS `1.0.1` and iOS `1.0`, show
  `Review Complete`.
- No pending submission, rejection, unresolved App Review conversation, or
  compliance action is shown in the current review-submissions view.

## Google Play Console

- `Policy status` explicitly reports `No issues found` for Nimbo.
- The publishing overview shows no pending unpublished change and records the
  latest publication on 2026-08-27.
- Phone `1.0.2 (6)` and Wear OS `1.0.2 (1000007)` remain published.

## Non-policy quality warning

Play Console separately warns that production phone bundle `1.0.2 (6)`
contains deprecated `androidx.fragment:fragment:1.1.0`. This is tracked as a
release-quality dependency issue and does not contradict the explicit
`No issues found` policy status.

The current unreleased candidate now pins `androidx.fragment:fragment:1.9.0`
in the phone, shared Android, and Wear OS graphs. Dependency reports resolve
the transitive `1.0.0`/`1.1.0` requests to `1.9.0`, and both generated AAB
`dependencies.pb` manifests contain `fragment 1.9.0`:

- phone AAB SHA-256:
  `e476a124c33854873add9061140f68f1720ff098202b52e7758038bb50f5a77c`
- Wear OS AAB SHA-256:
  `ac19a0eab1a60554db309166f135e754c97205b79c4f5182164a8b21594e7dc6`

This closes the candidate dependency defect. The production-console warning
will remain visible until a newer accepted bundle replaces phone `1.0.2 (6)`.

## Boundary

The console state can change after this observation. The weekly KPI importer
must still receive explicit `apple_policy_issues=0` and
`google_policy_issues=0` rows from a complete seven-day console evidence
period before the evaluator's metric guardrail can become `pass`.
