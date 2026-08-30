# Google Play weekly store-listing funnel — 2026-08-30

## Verdict

The first dimension-aligned weekly Google Play funnel is now recorded for the
seven complete days from `2026-08-18` through `2026-08-24`.

- All countries: `26` store-listing visitors and `11` unique users who clicked
  Install. The exact derived click-through rate is `42.31%`.
- Uzbekistan: `0` visitors and `0` unique users who clicked Install. The UZ
  rate is **UNKNOWN**, not `0%`, because the denominator is zero.
- These values do not close any retention, first-launch, rating, Android-vitals,
  release, or Top-10 gate.

## Authenticated source

The signed-in Play Console surface was:

`Nimbo > Store listings > Performance in Google Play > Installs`

Both measures used the same inclusive date window, dimension scope, device
scope, and app-version scope. The normalized, non-PII import is
[`../imports/2026-08-18_2026-08-24-google-play-console.csv`](../imports/2026-08-18_2026-08-24-google-play-console.csv).
The Console generated these private aggregate exports in the operator's local
Downloads directory; raw files are intentionally not committed:

| Scope | Measure | Private export SHA-256 |
| --- | --- | --- |
| UZ | Unique users who clicked Install | `c796172c749fca71399ef6b51ded6e304e76309fc5886b6899e35b7889c8cdea` |
| ALL | Visitors | `dd8c5fd5d956d924682e3e3191c3c7d3d3701d07ce2de6cea072709d2abc92e1` |
| ALL | Unique users who clicked Install | `1d2e87147bb430c475a26c9cfd1fe9021bbd817c10f70b5469f42c4fa2d459cc` |

The UZ visitor value was visually confirmed on the same Console surface. Its
separate visitor export was not retained in this evidence pass, so the import
does not claim a second file hash for that value.

## Definition boundary

The earlier reported `779` impressions and `40.82%` conversion came from a
different Console surface or denominator and cannot be reconciled to this
store-listing visitor/install-click pair. It remains historical reported
baseline only.

The private CSV named `Узбекистан.csv` has SHA-256
`dc07b1de33be37388023400c0b176f6dcda7604c9d9d8467c2b5a2be4e7d85f8` and
reports users with the app installed on an active device. Its daily value was
`1` for the visible `2026-08-19` through `2026-08-25` rows. That population is
not MAU, DAU, installations, first launches, or the store-listing funnel, so it
is deliberately excluded from the canonical weekly import.

## Decision boundary

The all-country `42.31%` rate is diagnostic only because the Nimbo objective and
KPI are scoped to UZ. The UZ conversion KPI remains missing until a later
seven-day UZ window has a non-zero, dimension-aligned visitor denominator.
