# App Store Connect crash refresh — 2026-09-03

Status: **authoritative aggregate refreshed; `ios_crash_gate` remains blocked**.

At `2026-09-03 15:48 Asia/Tashkent`, the authenticated App Store Connect
Analytics UI was inspected read-only for Nimbo Weather (`6799886897`). No
report request, export, app version, TestFlight group, submission, or release
state was created or changed.

## Observed crash aggregates

The metric was `Usage > Crashes`, grouped by app version, with Apple’s
`Received consent` population:

| Window shown by Apple | Public version | Reported crashes |
| --- | --- | ---: |
| `2026-08-26`–`2026-09-01` | `1.0.1 (iOS)` | 2 |
| `2026-08-03`–`2026-09-01` | `1.0.1 (iOS)` | 3 |
| `2026-06-04`–`2026-09-01` | `1.0.1 (iOS)` | 3 |

Apple states on the same surface that these days run from `00:00` through
`23:59 UTC`. The seven-day chart visibly places the two non-zero daily points
on August 29 and August 30. Earlier retained point-in-time evidence had already
recorded one event on August 25 and one on August 29; the current total and
window therefore show that an additional August 30 production event became
visible after that checkpoint.

## Fail-closed boundary

- These are consented crash counts, not affected users and not a
  source-defined crash-free-session percentage.
- The UI exposes no diagnostic, stack, incident/signature ID, crashed-process
  identity, or binary UUID for these low-volume aggregates.
- The counts belong to public `1.0.1`; they do not prove anything about
  processed-but-unreleased `1.1.0 (9)`.
- The fixed build-9 iPad Share regression remains source-current and green in
  simulator/XCUITest evidence, but it cannot substitute for a post-release
  stability window.

Accordingly, the third public crash strengthens the existing fail-closed
decision. `ios_crash_gate` remains blocked, Apple build 9 remains unattached
and unsubmitted, and no public acquisition or outreach is enabled.
