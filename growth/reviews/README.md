# Review inbox operations

Status date: August 29, 2026.

This directory is the non-PII operating record for store ratings and review
response work. Store consoles remain authoritative. The log records only dated
aggregate counts and actions; it is not a copy of review content and does not
prove notification delivery.

## Current checkpoint

- Google Play Console was checked read-only from `2026-08-29 23:38` through
  `23:40 +05:00` on the global default Ratings and reviews surface. It showed an
  average rating of `1.000`, one rating user, and zero text reviews all-time.
  There was therefore no reply surface and the check is `non_actionable`.
- Account-wide email notifications were changed and saved for all 1–5-star
  ratings and edited reviews. The configured destination is described only as
  the **developer account email**; its address must never be stored here.
- Current App Store review/rating state is unavailable through the present App
  Store Connect API permission. A separate logged-out public UZ lookup reported
  one rating with an average of `5.0` at `2026-09-01 00:55 +05:00`; its bounded
  response identity is recorded in
  [apple-public-store-2026-09-01.md](../quality/apple-public-store-2026-09-01.md).
  That aggregate exposes no review text or reply surface and is not current
  review-inbox evidence.
- The existing `nimbo-uz-rank-monitor` heartbeat is configured to check the
  review inbox once per day after `09:15` Asia/Tashkent and respond within 48
  hours only when a substantive text review exists. The repository log does not
  contain credentials and does not itself perform that external action.

## Response policy

1. A star-only rating is non-actionable because there is no text or reply
   surface. Record the aggregate observation with `action=none` and
   `sla_state=non_actionable`.
2. A substantive review contains product-specific feedback that can be answered
   or investigated. Respond within 48 hours in the review language when
   possible, using a concise, truthful, localized answer. Record only its oldest
   actionable timestamp and the response timestamp; never retain the review or
   reviewer identity.
3. Never offer incentives, use sentiment gating, ask for a higher rating, argue
   with the reviewer, or include unsupported product claims.
4. Do not store reviewer names, handles, account IDs, email addresses, review
   text, device identifiers, coordinates, or other PII in this repository.
5. When the same issue repeats, create a sanitized product fix, add a regression
   test, and verify the correction. Preserve only aggregate counts and the
   operational action state here; do not quote or fingerprint the reviews.

## Machine-readable log

[`review-inbox.csv`](review-inbox.csv) contains one aggregate console check per
row. `source_as_of` is an offset-aware ISO-8601 timestamp. Rating values use
three decimal places; counts are non-negative integers. Allowed action states
are `none`, `pending`, and `reply_sent`; SLA states are `non_actionable`,
`within_48h`, `overdue`, and `responded_late`. The schema deliberately has no
free-text review or reviewer field.

`oldest_substantive_review_at` is the oldest actionable review timestamp visible
for the aggregate check. `action_at` is the timestamp of the recorded developer
reply and is empty while work is pending. Both are offset-aware ISO-8601 values
and contain no reviewer identifier. For `pending`, SLA is derived from timestamps
as `source_as_of - oldest_substantive_review_at`: at most 48 hours is
`within_48h`, and more than 48 hours is `overdue`. For `reply_sent`, SLA is
derived from timestamps as `action_at - oldest_substantive_review_at`: at most 48
hours is `within_48h`, otherwise `responded_late`; `action_at` cannot precede the
review or exceed `source_as_of`. A row with zero substantive reviews requires
both timestamps empty, `action=none`, and `sla_state=non_actionable`.

Before adding a row, recheck the exact console surface, retain no reviewer-level
data, and run:

```sh
python3 scripts/check_review_inbox.py
python3 scripts/check_repository.py
```

The validator fails closed on schema drift, malformed or duplicate observations,
email-like data, impossible aggregate counts, an incorrect seed checkpoint, or
an action/SLA/timestamp combination that contradicts this policy.
